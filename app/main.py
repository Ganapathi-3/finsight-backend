from fastapi import FastAPI
import os

app = FastAPI(title="FinSight Backend")

@app.get("/")
def root():
    return {"message": "FinSight Backend Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
