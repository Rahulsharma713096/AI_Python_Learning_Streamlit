import pdfplumber
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

def load_keys(filepath="key.txt"):
    keys = {}
    with open(filepath, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                keys[key.strip()] = value.strip().strip('"')
    return keys
# Configuration
keys = load_keys()
OPENROUTER_API_KEY = keys.get("OpenRouter")
print(OPENROUTER_API_KEY)
#OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"

st.header("💬 Jald Chatbot (OpenRouter Only)")

# Sidebar
with st.sidebar:
    st.title("⚙️ Input Settings")

    input_type = st.radio(
        "Choose Input Type:",
        ["📄 PDF Upload", "📝 Enter Text"]
    )

# Input handling
source_text = ""

if input_type == "📄 PDF Upload":
    file = st.file_uploader("Upload your PDF", type="pdf")

    if file is not None:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    source_text += text + "\n"

elif input_type == "📝 Enter Text":
    source_text = st.text_area("Paste your text here:", height=300)

# Process only if text exists
if source_text.strip():

    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(source_text)

    # ✅ FREE embeddings (no OpenAI)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Vector DB
    vector_store = FAISS.from_texts(chunks, embeddings)

    # Question
    user_question = st.text_input("Ask your question:")

    # ✅ OpenRouter LLM
    llm = ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct",
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,
        max_tokens=1000
    )

    # Helper
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are Jald Chatbot.\n\n"
         "Answer ONLY using the given context.\n"
         "Give clear and structured answers.\n\n"
         "Context:\n{context}"),
        ("human", "{question}")
    ])

    # Chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Run
    if user_question:
        response = chain.invoke(user_question)
        st.write("### 🤖 Answer")
        st.write(response)

else:
    st.info("Please upload a PDF or enter text to continue.")