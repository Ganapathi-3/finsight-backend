from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from app.rag.vector_store import get_vector_store
import os

def get_rag_response(role: str, query: str):

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    vectorstore = get_vector_store(role)

    retriever = vectorstore.as_retriever()

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever
    )

    return qa.run(query)
