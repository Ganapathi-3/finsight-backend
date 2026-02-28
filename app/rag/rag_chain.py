from app.rag.vector_store import search_documents

def get_rag_response(role: str, query: str):
    result = search_documents(role, query)

    return f"Based on department documents: {result}"