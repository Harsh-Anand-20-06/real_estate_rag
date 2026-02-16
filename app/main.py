from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import os
import time
from app.retrieval import search, add_pdfs, init_session_index, clear_session

app = FastAPI(title="Real Estate Document Intelligence API")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.on_event("startup")
def startup_event():
    init_session_index()

@app.get("/")
def root():
    return {"message": "Real Estate Document Intelligence API is running!"}

@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        return {"error": "No files uploaded."}

    os.makedirs("data/pdfs", exist_ok=True)
    saved_paths = []

    for upload in files:
        contents = await upload.read()
        safe_name = f"{int(time.time() * 1000)}_{upload.filename.replace(' ', '_')}"
        path = os.path.join("data/pdfs", safe_name)
        with open(path, "wb") as f:
            f.write(contents)
        saved_paths.append(path)

    result = add_pdfs(saved_paths)

    # Delete PDFs after ingestion
    for path in saved_paths:
        try:
            os.remove(path)
        except:
            pass

    return {"uploaded_files": [os.path.basename(p) for p in saved_paths], **result}

@app.post("/query")
def query_documents(request: QueryRequest):
    results = search(request.query, request.top_k)
    return {"query": request.query, "results": results}

@app.on_event("shutdown")
def shutdown_event():
    clear_session()
