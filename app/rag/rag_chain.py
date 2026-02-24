from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from app.rag.vector_store import get_vector_store
from fastapi import HTTPException
import os


def get_rag_response(role: str, query: str):
    """
    Role-isolated RAG response generator.
    Retrieves documents only from the user's department vector DB.
    """

    # 🔐 Ensure OpenAI key exists
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured."
        )

    # 🤖 Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=api_key
    )

    # 📚 Load role-specific vector DB
    vectorstore = get_vector_store(role)

    # If no documents exist
    if vectorstore._collection.count() == 0:
        return f"No documents found for role: {role}"

    # 🔎 Create retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    # 🧠 Build QA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )

    try:
        response = qa.run(query)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing error: {str(e)}"
        )