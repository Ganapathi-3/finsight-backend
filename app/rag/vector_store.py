from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
import os

persist_directory = "chroma_db"

def get_vector_store(role: str):
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    return Chroma(
        persist_directory=f"{persist_directory}/{role}",
        embedding_function=embeddings
    )

def add_documents(role: str, texts: list):
    vectorstore = get_vector_store(role)

    docs = [Document(page_content=text) for text in texts]
    vectorstore.add_documents(docs)
    vectorstore.persist()
