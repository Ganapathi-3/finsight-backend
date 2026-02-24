from app.rag.vector_store import add_documents


def seed_documents():
    """
    Seeds role-based vector databases.
    Creates separate Chroma collections per department.
    """

    add_documents("finance", [
        "Finance department handles revenue and budgeting.",
        "Finance manages company investments.",
        "Finance tracks profit and loss statements."
    ])

    add_documents("hr", [
        "HR handles employee relations and payroll.",
        "HR manages hiring and benefits.",
        "HR oversees performance reviews."
    ])

    add_documents("executive", [
        "Executive team defines company strategy.",
        "Executives oversee major decisions.",
        "Executives approve high-level budgets."
    ])

    add_documents("admin", [
        "Admin manages system configurations.",
        "Admin has full system access.",
        "Admin monitors backend operations."
    ])