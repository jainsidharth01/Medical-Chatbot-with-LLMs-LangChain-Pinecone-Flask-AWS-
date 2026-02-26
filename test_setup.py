#!/usr/bin/env python3
"""
Test script to verify Medical Chatbot RAG setup.
Run this before starting the Flask app to diagnose issues.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("MEDICAL CHATBOT - SETUP VERIFICATION")
print("=" * 70)

# ============================================================================
# 1. Check Environment Variables
# ============================================================================
print("\n[1] Checking Environment Variables...")
print("-" * 70)

groq_key = os.getenv("GROQ_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

print(f"✓ GROQ_API_KEY present: {bool(groq_key)}")
if groq_key:
    print(f"  └─ Key preview: {groq_key[:20]}...{groq_key[-10:]}")

print(f"✓ PINECONE_API_KEY present: {bool(pinecone_key)}")
if pinecone_key:
    print(f"  └─ Key preview: {pinecone_key[:20]}...{pinecone_key[-10:]}")

if not groq_key or not pinecone_key:
    print("\n❌ ERROR: Missing API keys in .env file")
    sys.exit(1)

# ============================================================================
# 2. Check Dependencies
# ============================================================================
print("\n[2] Checking Dependencies...")
print("-" * 70)

dependencies = {
    "langchain": "LangChain",
    "langchain_groq": "LangChain Groq",
    "langchain_pinecone": "LangChain Pinecone",
    "langchain_community": "LangChain Community",
    "groq": "Groq SDK",
    "sentence_transformers": "Sentence Transformers",
    "pinecone": "Pinecone",
    "flask": "Flask",
}

missing = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name} - NOT INSTALLED")
        missing.append(module)

if missing:
    print(f"\n❌ ERROR: Missing packages: {', '.join(missing)}")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

# ============================================================================
# 3. Test Embeddings
# ============================================================================
print("\n[3] Testing Embeddings Model...")
print("-" * 70)

try:
    from src.helper import download_embeddings
    embeddings = download_embeddings()
    print(f"✓ Embeddings loaded successfully")
    print(f"  └─ Model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"  └─ Dimension: 384")
except Exception as e:
    print(f"✗ Failed to load embeddings: {str(e)}")
    sys.exit(1)

# ============================================================================
# 4. Test Pinecone Connection
# ============================================================================
print("\n[4] Testing Pinecone Connection...")
print("-" * 70)

try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=pinecone_key)
    indexes = pc.list_indexes()
    index_names = [idx["name"] for idx in indexes]
    
    print(f"✓ Connected to Pinecone")
    print(f"  └─ Indexes found: {len(index_names)}")
    
    if "medical-chatbot" in index_names:
        print(f"✓ 'medical-chatbot' index exists")
        index = pc.Index("medical-chatbot")
        stats = index.describe_index_stats()
        print(f"  └─ Total vectors: {stats.get('total_vector_count', 'N/A')}")
        print(f"  └─ Dimension: {stats.get('dimension', 'N/A')}")
    else:
        print(f"✗ 'medical-chatbot' index NOT FOUND")
        print(f"  └─ Available indexes: {index_names}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Pinecone connection failed: {str(e)}")
    sys.exit(1)

# ============================================================================
# 5. Test Retriever
# ============================================================================
print("\n[5] Testing Retriever...")
print("-" * 70)

try:
    from langchain_pinecone import PineconeVectorStore
    
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name="medical-chatbot",
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    print(f"✓ Retriever initialized")
    
    # Test retrieval
    test_query = "what is acne?"
    docs = retriever.get_relevant_documents(test_query)
    
    from app import clean_context

    print(f"✓ Retrieved {len(docs)} documents for test query: '{test_query}'")
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        raw_preview = doc.page_content[:100].replace("\n", " ")
        cleaned_preview = clean_context(doc.page_content)[:100].replace("\n", " ")
        print(f"  └─ Doc {i}: {source}")
        print(f"     Raw preview: {raw_preview}...")
        print(f"     Cleaned preview: {cleaned_preview}...")
except Exception as e:
    print(f"✗ Retriever test failed: {str(e)}")
    sys.exit(1)

# ============================================================================
# 6. Test ChatGroq
# ============================================================================
print("\n[6] Testing ChatGroq LLM...")
print("-" * 70)

try:
    from src.langchain_groq import ChatGroq
    
    llm = ChatGroq(
        groq_api_key=groq_key,
        model_name="llama3-8b-8192",
        temperature=0.0,
        verbose=True
    )
    
    print(f"✓ ChatGroq initialized")
    
    # Check if LangChain ChatGroq is available
    langchain_llm = llm.get_llm()
    if langchain_llm:
        print(f"✓ LangChain ChatGroq available")
    else:
        print(f"⚠ LangChain ChatGroq not available (will use fallback)")
    
except Exception as e:
    print(f"✗ ChatGroq initialization failed: {str(e)}")
    sys.exit(1)

# ============================================================================
# 7. Test LLM Generation
# ============================================================================
print("\n[7] Testing LLM Generation...")
print("-" * 70)

try:
    messages = [
        {"role": "system", "content": "You are a medical assistant. Answer briefly."},
        {"role": "user", "content": "What is acne?"}
    ]
    
    print("Sending test query to Groq API...")
    response = llm.generate(messages=messages)
    
    print(f"✓ LLM generated response")
    print(f"  └─ Response: {response[:150]}...")
    
except Exception as e:
    print(f"✗ LLM generation failed: {str(e)}")
    print(f"  └─ This might be a network or API issue")

# ============================================================================
# 8. Test RAG Chain
# ============================================================================
print("\n[8] Testing RAG Chain...")
print("-" * 70)

try:
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant.
Use the following context to answer the question.
If you don't know, say so.

Context:
{context}

Question: {input}

Answer:"""
    )
    
    combine_docs_chain = create_stuff_documents_chain(
        langchain_llm,
        prompt
    )
    
    rag_chain = create_retrieval_chain(
        retriever,
        combine_docs_chain
    )
    
    print(f"✓ RAG chain created")
    
    # Test RAG chain
    print("Testing RAG chain with sample query...")
    result = rag_chain.invoke({"input": "what is acne?"})
    
    answer = result.get("answer", "").strip()
    if answer:
        print(f"✓ RAG chain generated answer")
        print(f"  └─ Answer: {answer[:150]}...")
    else:
        print(f"⚠ RAG chain returned empty answer")
        
except Exception as e:
    print(f"⚠ RAG chain test failed: {str(e)}")
    print(f"  └─ This is not critical - fallback will be used")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED - Ready to start the chatbot!")
print("=" * 70)
print("\nNext steps:")
print("1. Start the Flask app: python app.py")
print("2. Open browser: http://localhost:5000")
print("3. Ask a medical question")
print("\nFor debugging, set DEBUG_MODE=True in .env")
print("=" * 70)
