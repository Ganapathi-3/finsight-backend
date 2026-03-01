from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_role
)
from app.database import run_sql
from app.rag.rag_chain import get_rag_response
from app.rag.vector_store import add_documents
import os

app = FastAPI(title="FinSight Backend")


# =========================================================
# ROOT & HEALTH
# =========================================================

@app.get("/")
def root():
    return {"message": "FinSight Backend Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# =========================================================
# AUTHENTICATION
# =========================================================

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


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user["username"],
        "role": current_user["role"]
    }


# =========================================================
# ROLE-BASED ROUTES
# =========================================================

@app.get("/finance/data")
def finance_data(current_user: dict = Depends(require_role("finance"))):
    return {"message": "Finance data accessed", "user": current_user["username"]}


@app.get("/hr/data")
def hr_data(current_user: dict = Depends(require_role("hr"))):
    return {"message": "HR data accessed", "user": current_user["username"]}


@app.get("/executive/data")
def executive_data(current_user: dict = Depends(require_role("executive"))):
    return {"message": "Executive data accessed", "user": current_user["username"]}


@app.get("/admin/data")
def admin_data(current_user: dict = Depends(require_role("admin"))):
    return {"message": "Admin data accessed", "user": current_user["username"]}


# =========================================================
# SECURE SQL (Role Filtered)
# =========================================================

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


# =========================================================
# AI ASK ENDPOINT (RAG)
# =========================================================

@app.post("/ask")
def ask_ai(
    request: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    role = current_user["role"]
    question = request.get("question")

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question field is required"
        )

    response = get_rag_response(role, question)

    return {
        "role": role,
        "question": question,
        "answer": response
    }


# =========================================================
# ADMIN: ADD DOCUMENTS TO VECTOR DB
# =========================================================

@app.post("/admin/add-documents")
def add_department_documents(
    request: dict = Body(...),
    current_user: dict = Depends(require_role("admin"))
):
    department = request.get("department")
    texts = request.get("texts")

    if not department or not texts:
        raise HTTPException(
            status_code=400,
            detail="Both 'department' and 'texts' fields are required"
        )

    if department not in ["finance", "hr", "executive", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid department"
        )

    if not isinstance(texts, list):
        raise HTTPException(
            status_code=400,
            detail="'texts' must be a list of strings"
        )

    add_documents(department, texts)

    return {
        "message": f"Documents added successfully to {department}",
        "count": len(texts)
    }


# =========================================================
# DEVELOPMENT ONLY
# =========================================================

@app.get("/test-sql")
def test_sql():
    result = run_sql("SELECT * FROM department_data")
    return {"data": result}


# =========================================================
# RENDER SERVER START
# =========================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )