import pdfplumber
import streamlit as st
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 🔐 Set Gemini API Key (use environment variable in production)
#os.environ["GOOGLE_API_KEY"] = "RAHUL"
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
GOOGLE_API_KEY=keys.get("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)
os.environ["GOOGLE_API_KEY"] =GOOGLE_API_KEY
# UI
st.set_page_config(page_title="Gemini PDF Chatbot", layout="wide")
st.header("📄 Gemini PDF Chatbot")

# Sidebar
with st.sidebar:
    st.title("📂 Upload PDF")
    file = st.file_uploader("Upload a PDF file", type="pdf")

# Process PDF
if file is not None:

    # Extract text
    with st.spinner("📖 Reading PDF..."):
        with pdfplumber.open(file) as pdf:
            text = ""
            print("-----------------------------------------------------------------------------")
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
                print(text)
            print("-----------------------------------------------------------------------------")

    if not text.strip():
        st.error("❌ Could not extract text from PDF")
        st.stop()

    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)

    # Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )

    # Vector DB (Chroma)
    vector_store = Chroma.from_texts(chunks, embeddings)

    # User input
    user_question = st.text_input("💬 Ask a question about your PDF")

    # Format docs
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    # Retriever
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4}
    )

    # Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        max_output_tokens=1000
    )

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant answering questions about a PDF document.\n\n"
         "Guidelines:\n"
         "1. Use ONLY the provided context.\n"
         "2. Give clear, structured answers.\n"
         "3. If answer is not in context, say politely.\n\n"
         "Context:\n{context}"),
        ("human", "{question}")
    ])

    # RAG Chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Generate answer
    if user_question:
        with st.spinner("🤔 Thinking..."):
            try:
                response = chain.invoke(user_question)
                st.success("✅ Answer:")
                st.write(response)
            except Exception as e:
                st.error(f"❌ Error: {e}")