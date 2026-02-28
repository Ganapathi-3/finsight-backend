from app.rag.vector_store import get_vector_store

DEPARTMENTS = ["finance", "hr", "executive", "admin"]

def get_rag_response(role: str, query: str):

    all_docs = []

    # 🔐 Admin can access all departments
    if role == "admin":
        for dept in DEPARTMENTS:
            store = get_vector_store(dept)
            docs = store.similarity_search(query, k=3)
            all_docs.extend(docs)
    else:
        store = get_vector_store(role)
        all_docs = store.similarity_search(query, k=3)

    if not all_docs:
        return "No documents found for this department."

    # Combine context
    context = " ".join([doc.page_content for doc in all_docs])

    return f"Based on department documents: {context}"