# Real Estate Document Intelligence System

A semantic search system for PDF documents using FAISS and SentenceTransformers.
Users can upload one or more PDFs and query them using natural language to retrieve the most relevant document sections.

------------------------------------------------------------
 OVERVIEW
------------------------------------------------------------

This project implements a session-based semantic document search system that:

- Extracts text from uploaded PDF files
- Splits text into context-preserving chunks
- Generates dense semantic embeddings
- Stores embeddings in a FAISS similarity index
- Retrieves the most relevant chunks using cosine similarity
- Serves search functionality via a FastAPI backend

The system is optimized for correctness, low latency, and efficient retrieval for small-to-medium sized document collections.

Uploaded PDFs are processed temporarily and removed after ingestion to ensure clean session isolation.

------------------------------------------------------------
 SYSTEM ARCHITECTURE
------------------------------------------------------------

User  
  ↓  
FastAPI Backend (main.py)  
  ↓  
PDF Processing (ingestion.py)  
  ↓  
Text Chunking (350 char, 100 overlap)  
  ↓  
Embedding Generation (all-MiniLM-L6-v2)  
  ↓  
FAISS Session Index (IndexFlatIP)  
  ↓  
Top-K Similarity Search  
  ↓  
Returned Relevant Chunks with Metadata


##  Project Structure

```
project/
│
├── app/
│   ├── main.py
│   ├── retrieval.py
│   ├── ingestion.py
│   └── embeddings.py
│
├── data/
│   └── pdfs/
│
├── index/
│   └── session_index/
│
├── requirements.txt
└── README.md
```



------------------------------------------------------------
⚙️ INSTALLATION
------------------------------------------------------------

1) Clone Repository

git clone <your-repo-url>
cd project

2) Create Virtual Environment

python -m venv venv

Mac/Linux:
source venv/bin/activate

Windows:
venv\Scripts\activate

3) Install Dependencies

pip install -r requirements.txt

------------------------------------------------------------
▶️ RUNNING THE APPLICATION
------------------------------------------------------------

uvicorn app.main:app --reload --port 8000

Open in browser:

http://127.0.0.1:8000/docs

Swagger UI allows:
- Uploading PDFs
- Searching documents

------------------------------------------------------------
 API ENDPOINTS
------------------------------------------------------------

1) Root Endpoint

GET /

Response:
{
  "message": "Real Estate Document Intelligence API is running!"
}

Used to verify that the API server is active.

------------------------------------------------------------

2) Upload PDFs

POST /upload

<img width="1818" height="830" alt="Screenshot 2026-02-19 061651" src="https://github.com/user-attachments/assets/6a69ee5c-1540-4332-83f5-cc79e7dc4e81" />


Description:
- Accepts multiple PDF files in a single request.
- Saves files temporarily to data/pdfs/.
- Extracts text and splits into chunks.
- Generates embeddings for all chunks.
- Adds embeddings to the session-based FAISS index.
- Deletes uploaded PDFs immediately after ingestion.
- Updates in-memory metadata and FAISS index.

Request Type:
multipart/form-data

Parameter:
files → List of PDF files

Example:
Upload one or more PDF files via Swagger UI or Postman.

Response Example:
{
  "uploaded_files": [
    "1771462014392_test_pdf_2.pdf",
    "1771462014413_test_pdf_1.pdf",
    "1771462014430_test_pdf_4.pdf"
  ],
  "added": 266,
  "total": 266
}

Where:
- added = number of chunks added from current upload
- total = total number of chunks currently stored in session index

------------------------------------------------------------

3) Search Query

POST /query

<img width="1820" height="817" alt="Screenshot 2026-02-19 061839" src="https://github.com/user-attachments/assets/b3673457-b41a-4dfc-becf-ffa448a5a52d" />


Description:
- Performs semantic similarity search using FAISS.
- Uses cosine similarity via Inner Product.
- Returns top-k most relevant chunks.
- Default top_k = 3.

Request Body Example:
{
  "query": "Give certification of Max Towers.",
  "top_k": 3
}

Response Example:

<img width="1764" height="882" alt="Screenshot 2026-02-19 061859" src="https://github.com/user-attachments/assets/b9c53df5-b963-42be-bc9e-b450939bdb6b" />


Each result includes:
- pdf_name
- page_number
- text
- similarity score

------------------------------------------------------------

4) Session Management

Startup:
- A fresh FAISS session index is initialized automatically when the server starts.

Shutdown:
- The session index and metadata are cleared.
- Temporary index files are removed.

This ensures clean session isolation and prevents mixing results across runs.


------------------------------------------------------------
 HOW IT WORKS
------------------------------------------------------------

1) PDF Processing

- Uses PyMuPDF (fitz) to extract text page by page.
- Each page is processed and converted into structured chunks.
- Metadata stored for each chunk:
  - PDF name
  - Page number
  - Text content

The processing is handled inside the `process_pdf()` function.

------------------------------------------------------------

2) Chunking Strategy

- Chunk size: 350 characters
- Overlap: 100 characters
- Overlapping chunks preserve context across boundaries.
- Balanced for retrieval accuracy and computational efficiency.

Each chunk is stored along with its page reference for traceability.

------------------------------------------------------------

3) Embeddings

- Model: sentence-transformers/all-MiniLM-L6-v2
- Encoded using a custom `EmbeddingModel` wrapper.
- Embeddings are normalized to enable cosine similarity using Inner Product (IP).
- Batched encoding improves performance.

------------------------------------------------------------

4) FAISS Index (Session-Based)

- Index type: IndexFlatIP (Inner Product for cosine similarity)
- Created dynamically during the session.
- Stored temporarily at:

  index/session_index/faiss.index  
  index/session_index/metadata.pkl  

- Metadata (text + page + pdf name) is stored separately using pickle.
- The index is session-based and can be cleared using `clear_session()`.

This ensures:
- Fast semantic similarity search
- Clean isolation between sessions
- Temporary storage without long-term persistence


------------------------------------------------------------
 SUCCESS METRICS
------------------------------------------------------------

The system was evaluated using 20 manually curated test queries based on the uploaded real estate PDFs.

===== FINAL METRICS =====

Total Questions: 20  
Top-1 Accuracy: 0.80  
Top-3 Accuracy: 0.85  
Average Latency (s): 0.0102  
P95 Latency (s): 0.0207 

<img width="371" height="174" alt="image" src="https://github.com/user-attachments/assets/2a90718b-38ca-4e03-9482-c3df82fb73a8" />


Performance Interpretation:

1) Retrieval Accuracy
- Top-1 Accuracy (80%): The correct document chunk was ranked first in 80% of the queries.
- Top-3 Accuracy (85%): The correct chunk appeared within the top 3 results in 85% of the queries.
- This demonstrates strong semantic understanding and effective chunk retrieval.

2) Query Latency
- Average latency of ~10 milliseconds per query.
- 95% of queries completed within ~20 milliseconds.
- Low latency achieved due to efficient FAISS vector similarity search and normalized embeddings.

3) System Efficiency
- Embedding computation is the primary computational cost.
- Once indexed, semantic search remains highly efficient even with multiple queries.

These results demonstrate that the system achieves both high retrieval relevance and low-latency performance for small-to-medium document collections.


------------------------------------------------------------
 DESIGN DECISIONS
------------------------------------------------------------

- In-memory FAISS for fast similarity search
- Persistent index stored to disk
- Batched embedding generation for efficiency
- Modular code structure for maintainability
- Balanced chunk size for retrieval quality vs speed
- Designed with scalability awareness (can extend to persistent vector DB and background processing)

------------------------------------------------------------
 CHALLENGES
------------------------------------------------------------

1) Handling Large PDFs

Large PDFs increase:
- Processing time
- Memory usage
- Embedding latency

Recommendation:
- Limit documents to < 50 pages
- Pre-split very large files before upload

2) Chunk Size Tradeoff

Small chunks:
+ Better precision
- May lose context

Large chunks:
+ More context
- Slower search and reduced specificity

Balanced at ~300–350 characters with overlap.

3) Fine-Tuning Embedding Model (Stretch Goal)

Potential improvement:
- Fine-tune embedding model on real estate domain documents
- Improve domain-specific retrieval accuracy

##  System Behavior

###  What Happens as PDFs Grow Larger?

As the size and number of PDFs increase:

- Processing time increases proportionally (more pages → more chunks → more embeddings).
- Memory usage increases during embedding generation.
- The FAISS index becomes larger.
- Query latency may increase slightly due to a larger search space.

For very large PDFs (e.g., 500+ pages):
- Ingestion time becomes noticeable.
- Embedding generation becomes the slowest step in the pipeline.

---

###  What Would Break First in Production?

The most likely failure points are:

1. **Memory Exhaustion**
   - Large numbers of chunks can consume significant RAM.
   - FAISS index stored in memory may become too large.

2. **Slow Response Times**
   - Larger indexes increase retrieval latency.
   - Concurrent users multiply embedding and search load.

3. **CPU Bottleneck**
   - SentenceTransformer runs on CPU (if GPU not enabled).
   - Multiple simultaneous uploads may overload the server.

4. **Disk I/O Pressure**
   - Temporary PDF storage and index writing can slow down under heavy traffic.

---

###  Where Are the Bottlenecks?

####  Embedding Generation (Primary Bottleneck)
- Transformer inference is computationally expensive.
- Becomes slower as chunk count increases.

####  FAISS Index Construction
- Index build time increases with number of vectors.

####  Chunk Explosion
- Large PDFs produce thousands of chunks.
- More chunks → more embeddings → larger index → slower queries.

####  Single Backend Instance
- Currently runs as a single FastAPI service.
- No horizontal scaling or distributed indexing.

---

##  Production Scaling Improvements

To make this system production-ready:

- Batch embedding generation.
- Add GPU acceleration.
- Replace local FAISS with a managed vector database (e.g., Pinecone, Weaviate).
- Implement asynchronous task queues (Celery + Redis).
- Add rate limiting.
- Use cloud storage (e.g., S3) for PDF storage.
- Add horizontal scaling with load balancing.


------------------------------------------------------------
 FUTURE IMPROVEMENTS
------------------------------------------------------------

- Background task processing for large PDFs
- Multi-user indexing
- GPU acceleration
- Advanced FAISS indexing (IVF, HNSW)
- Cloud deployment



------------------------------------------------------------
 AUTHOR
------------------------------------------------------------

Harsh
IIT Indore


