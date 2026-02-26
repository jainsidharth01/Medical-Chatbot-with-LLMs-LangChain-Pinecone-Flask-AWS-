# -----------------------------
# UPDATED CLEAN helper.py FILE
# -----------------------------

from __future__ import annotations

from typing import List

# Move heavy / optional imports into functions to avoid importing
# large ML libraries at module import time (improves startup).


# -----------------------------
# 1️⃣ Extract text from PDF files
# -----------------------------
def load_pdf_files(data: str) -> List[Document]:
    from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
    from langchain.schema import Document

    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    return documents


# -----------------------------
# 2️⃣ Filter to minimal docs
# -----------------------------
def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    minimal_docs: List[Document] = []

    for doc in docs:
        from langchain.schema import Document

        src = doc.metadata.get("source")
        minimal_doc = Document(
            page_content=doc.page_content,
            metadata={"source": src}
        )
        minimal_docs.append(minimal_doc)

    return minimal_docs


# -----------------------------
# 3️⃣ Split documents into chunks
# -----------------------------
def text_split(minimal_docs: List[Document]) -> List[Document]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120
    )

    texts_chunk = text_splitter.split_documents(minimal_docs)
    return texts_chunk


# ==============================
# 4️⃣ DOWNLOAD EMBEDDINGS
# ==============================
def download_embeddings():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )

    return embeddings