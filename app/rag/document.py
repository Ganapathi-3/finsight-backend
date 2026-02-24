from app.rag.vector_store import add_documents, get_vector_store


def seed_documents():

    departments = {
        "finance": [
            "Finance department handles revenue and budgeting.",
            "Finance manages investments and profit tracking."
        ],
        "hr": [
            "HR manages employee relations and payroll.",
            "HR handles hiring and benefits."
        ],
        "executive": [
            "Executive team defines company strategy.",
            "Executives oversee major decisions."
        ],
        "admin": [
            "Admin manages system configurations.",
            "Admin oversees backend infrastructure."
        ]
    }

    for dept, texts in departments.items():
        vectorstore = get_vector_store(dept)

        # Check if documents already exist
        existing = vectorstore._collection.count()

        if existing == 0:
            add_documents(dept, texts)