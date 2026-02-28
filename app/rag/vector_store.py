from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import os

persist_directory = "chroma_db"

# ✅ Load embedding model ONLY ONCE
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def get_vector_store(role: str):
    return Chroma(
        persist_directory=f"{persist_directory}/{role}",
        embedding_function=embedding_model
    )

def add_documents(role: str, texts: list):
    vectorstore = get_vector_store(role)

    docs = [Document(page_content=text) for text in texts]
    vectorstore.add_documents(docs)
    vectorstore.persist()