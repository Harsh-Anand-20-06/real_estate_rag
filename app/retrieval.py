import os
import pickle
import faiss
from typing import List
from app.embeddings import EmbeddingModel
from app.ingestion import process_pdf

# Temporary session storage
SESSION_INDEX_PATH = "index/session_index/faiss.index"
SESSION_META_PATH = "index/session_index/metadata.pkl"
os.makedirs("index/session_index", exist_ok=True)

# Global session objects (only initialized via functions)
model = EmbeddingModel()
session_index = None
session_metadata = []

def init_session_index():
    """Initialize a fresh FAISS index"""
    global session_index, session_metadata
    session_index = None
    session_metadata = []

def add_pdfs(file_paths: List[str]):
    global session_index, session_metadata
    new_texts = []
    new_meta = []

    for path in file_paths:
        chunks = process_pdf(path)
        for chunk in chunks:
            new_texts.append(chunk["text"])
            new_meta.append({
                "pdf_name": os.path.basename(path),
                "page_number": chunk["page_number"],
                "text": chunk["text"]
            })

    if not new_texts:
        return {"added": 0, "total": 0}

    embeddings = model.encode(new_texts)
    dim = embeddings.shape[1]

    if session_index is None:
        session_index = faiss.IndexFlatIP(dim)

    session_index.add(embeddings)
    session_metadata.extend(new_meta)

    # Save temporarily
    faiss.write_index(session_index, SESSION_INDEX_PATH)
    with open(SESSION_META_PATH, "wb") as f:
        pickle.dump(session_metadata, f)

    return {"added": len(new_texts), "total": session_index.ntotal}

def search(query: str, top_k: int = 3):
    if session_index is None or session_index.ntotal == 0:
        return []

    query_embedding = model.encode([query])
    scores, indices = session_index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        item = session_metadata[idx].copy()
        item["score"] = float(score)
        results.append(item)

    return results

def clear_session():
    global session_index, session_metadata
    session_index = None
    session_metadata = []
    if os.path.exists(SESSION_INDEX_PATH):
        os.remove(SESSION_INDEX_PATH)
    if os.path.exists(SESSION_META_PATH):
        os.remove(SESSION_META_PATH)
