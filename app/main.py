from app.rag.rag_chain import get_rag_response
from app.database import run_sql
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_role
)
import os

app = FastAPI(title="FinSight Backend")

# Root Endpoint
@app.get("/")
def root():
    return {"message": "FinSight Backend Running"}

# Health Check
@app.get("/health")
def health():
    return {"status": "healthy"}

# Login Endpoint
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

# Basic Protected Route
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user["username"],
        "role": current_user["role"]
    }

# Role-Based Routes
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
@app.get("/secure-sql")
def secure_sql(current_user: dict = Depends(get_current_user)):

    role = current_user["role"]

    if role == "admin":
        query = "SELECT * FROM department_data"
    else:
        query = f"""
            SELECT * FROM department_data
            WHERE department = '{role}'
        """

    result = run_sql(query)

    return {
        "user": current_user["username"],
        "role": role,
        "data": result
    }
@app.post("/ask")
def ask_ai(query: str, current_user: dict = Depends(get_current_user)):

    role = current_user["role"]

    response = get_rag_response(role, query)

    return {
        "role": role,
        "answer": response
    }




# Render Compatible Server Start
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
from app.database import run_sql

@app.get("/test-sql")
def test_sql():
    result = run_sql("SELECT * FROM department_data")
    return {"data": result}

