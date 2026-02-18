from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import authenticate_user, create_access_token, get_current_user
import os

app = FastAPI(title="FinSight Backend")

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "FinSight Backend Running"}


# -----------------------------
# Health Check Endpoint
# -----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}


# -----------------------------
# Login Endpoint (JWT)
# -----------------------------
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


# -----------------------------
# Protected Endpoint
# -----------------------------
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user["username"],
        "role": current_user["role"]
    }


# -----------------------------
# Run Server (Render Compatible)
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
