from app.rag.vector_store import add_documents

def seed_documents():

    add_documents("finance", [
        "Finance department handles revenue and budgeting.",
        "Finance manages investments and profit tracking."
    ])

    add_documents("hr", [
        "HR manages employee relations and payroll.",
        "HR handles hiring and benefits."
    ])

    add_documents("executive", [
        "Executive team defines company strategy.",
        "Executives oversee major decisions."
    ])

    add_documents("admin", [
        "Admin manages system configurations.",
        "Admin oversees backend infrastructure."
    ])