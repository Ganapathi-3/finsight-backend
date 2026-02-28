from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# In-memory store
documents_store = {
    "finance": [],
    "hr": [],
    "executive": [],
    "admin": []
}

def add_documents(role: str, texts: list):
    if role not in documents_store:
        raise ValueError("Invalid role")

    documents_store[role].extend(texts)


def search_documents(role: str, query: str):
    docs = documents_store.get(role, [])

    if not docs:
        return "No documents found for this department."

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(docs + [query])

    similarity = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    )

    best_index = similarity.argmax()

    return docs[best_index]