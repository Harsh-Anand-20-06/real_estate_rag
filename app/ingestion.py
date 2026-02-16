import fitz
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "]
)

def preprocess(text: str):
    text = re.sub(r'-\n', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    all_chunks = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        raw_text = page.get_text("text")
        cleaned = preprocess(raw_text)

        if not cleaned:
            continue

        chunks = splitter.split_text(cleaned)
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "page_number": page_number + 1
            })

    return all_chunks
