from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from pydantic import BaseModel
import os

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_role
)

from app.database import run_sql
from app.rag.rag_chain import get_rag_response
from app.rag.vector_store import add_documents


# ==========================================================
# APP INITIALIZATION
# ==========================================================

app = FastAPI(title="FinSight Backend")


# ==========================================================
# CORS (Allow Frontend Access)
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():
    return {"message": "FinSight Backend Running"}


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():
    return {"status": "healthy"}


# ==========================================================
# LOGIN
# ==========================================================

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================================
# PROTECTED ROUTE
# ==========================================================

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user["username"],
        "role": current_user["role"]
    }


# ==========================================================
# ROLE BASED ROUTES
# ==========================================================

@app.get("/finance/data")
def finance_data(current_user: dict = Depends(require_role("finance"))):
    return {"message": "Finance data accessed"}


@app.get("/hr/data")
def hr_data(current_user: dict = Depends(require_role("hr"))):
    return {"message": "HR data accessed"}


@app.get("/executive/data")
def executive_data(current_user: dict = Depends(require_role("executive"))):
    return {"message": "Executive data accessed"}


@app.get("/admin/data")
def admin_data(current_user: dict = Depends(require_role("admin"))):
    return {"message": "Admin data accessed"}


# ==========================================================
# SECURE SQL (ROLE FILTERED)
# ==========================================================

@app.get("/secure-sql")
def secure_sql(current_user: dict = Depends(get_current_user)):

    role = current_user["role"]

    if role == "admin":
        result = run_sql("SELECT * FROM department_data")
    else:
        result = run_sql(
            "SELECT * FROM department_data WHERE department = ?",
            (role,)
        )

    return {
        "user": current_user["username"],
        "role": role,
        "data": result
    }


# ==========================================================
# AI ASK ENDPOINT (RAG + ROLE SECURITY)
# ==========================================================

@app.post("/ask")
def ask_ai(
    request: dict,
    current_user: dict = Depends(get_current_user)
):

    question = request.get("question")

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question field is required"
        )

    role = current_user["role"]

    question_lower = question.lower()

    # Detect department mentioned in question
    departments = ["finance", "hr", "executive", "admin"]

    detected_department = None

    for dept in departments:
        if dept in question_lower:
            detected_department = dept
            break

    # Block cross-department access
    if detected_department and role != "admin" and detected_department != role:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: {role} users cannot query {detected_department} data."
        )

    # Run RAG retrieval for user's department
    response = get_rag_response(role, question)

    return {
        "role": role,
        "question": question,
        "answer": response
    }


# ==========================================================
# MULTI-DEPARTMENT DOCUMENT UPLOAD
# ==========================================================

class DepartmentDocuments(BaseModel):
    department: str
    texts: List[str]


@app.post("/admin/add-documents")
def add_multiple_department_documents(
    request: List[DepartmentDocuments],
    current_user: dict = Depends(require_role("admin"))
):

    allowed_departments = ["finance", "hr", "executive", "admin"]

    total_added = 0

    for item in request:

        if item.department not in allowed_departments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department: {item.department}"
            )

        if not item.texts or not isinstance(item.texts, list):
            raise HTTPException(
                status_code=400,
                detail=f"'texts' must be a list for department {item.department}"
            )

        add_documents(item.department, item.texts)

        total_added += len(item.texts)

    return {
        "message": "Documents added successfully",
        "departments_processed": len(request),
        "total_documents_added": total_added
    }


# ==========================================================
# DEVELOPMENT TEST SQL
# ==========================================================

@app.get("/test-sql")
def test_sql():
    result = run_sql("SELECT * FROM department_data")
    return {"data": result}


# ==========================================================
# RUN SERVER
# ==========================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True
    )