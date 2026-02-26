"""
High-quality Pinecone indexing script
Optimized for medical RAG retrieval quality
"""

from dotenv import load_dotenv
import os
import re
from uuid import uuid4

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY not found in .env")

# ==========================================================
# LOAD PDF FILES
# ==========================================================

from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

def load_pdf_files(data_path):
    docs = []
    for pdf_file in Path(data_path).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        docs.extend(loader.load())
    return docs


# ==========================================================
# SMART TEXT SPLITTING (SEMANTIC FIRST)
# ==========================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(documents):
    """
    Semantic-first chunking.
    Larger chunks preserve medical section integrity.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,     # ⬆ Increased for better context continuity
        chunk_overlap=500,   # ⬆ Strong overlap to prevent info loss
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )

    chunks = splitter.split_documents(documents)

    filtered = []
    for chunk in chunks:
        content = chunk.page_content.strip()

        # Remove obvious junk
        if len(content) < 200:
            continue

        if re.search(r"GALE\s+ENCYCLOPEDIA", content, re.IGNORECASE):
            continue

        filtered.append(chunk)

    print(f"Created {len(chunks)} chunks → kept {len(filtered)}")
    return filtered


# ==========================================================
# EMBEDDINGS
# ==========================================================

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================================
# LOAD DOCUMENTS
# ==========================================================

print("📄 Loading PDFs...")
documents = load_pdf_files("data")
print(f"Loaded {len(documents)} pages")

print("✂ Splitting documents...")
chunks = split_text(documents)

if not chunks:
    raise ValueError("⚠️ No valid content chunks found")

# ==========================================================
# PINECONE SETUP
# ==========================================================

from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medical-chatbot"

if index_name not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print("🆕 Index created")
else:
    print("✅ Index exists")

index = pc.Index(index_name)

# Clear existing
print("🗑 Clearing old index...")
index.delete(delete_all=True)

# ==========================================================
# STORE IN PINECONE (Stable Batched Upload)
# ==========================================================

from langchain_pinecone import PineconeVectorStore

vectorstore = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings
)

batch_size = 40

print("📤 Uploading batches...")
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    vectorstore.add_documents(batch)
    print(f"  Uploaded batch {i//batch_size + 1}")

print("✅ Indexing complete!")
print(f"Total chunks indexed: {len(chunks)}")