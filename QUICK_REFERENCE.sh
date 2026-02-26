#!/bin/bash
# Quick Reference Commands for Medical Chatbot

echo "=========================================="
echo "Medical Chatbot - Quick Reference"
echo "=========================================="
echo ""

# Installation
echo "1. INSTALLATION"
echo "   pip install -r requirements.txt"
echo ""

# Verification
echo "2. VERIFY SETUP"
echo "   python test_setup.py"
echo ""

# Health Check
echo "3. HEALTH CHECK"
echo "   curl http://localhost:5000/health"
echo ""

# Start App
echo "4. START APP"
echo "   python app.py"
echo ""

# Debug Mode
echo "5. DEBUG MODE"
echo "   export DEBUG_MODE=True"
echo "   python app.py"
echo ""

# Test Retriever
echo "6. TEST RETRIEVER"
echo "   python -c \""
echo "   from src.helper import download_embeddings"
echo "   from langchain_pinecone import PineconeVectorStore"
echo "   embeddings = download_embeddings()"
echo "   vs = PineconeVectorStore.from_existing_index('medical-chatbot', embeddings)"
echo "   retriever = vs.as_retriever(search_kwargs={'k': 3})"
echo "   docs = retriever.get_relevant_documents('what is acne?')"
echo "   print(f'Retrieved {len(docs)} documents')"
echo "   \""
echo ""

# Test LLM
echo "7. TEST LLM"
echo "   python -c \""
echo "   from src.langchain_groq import ChatGroq"
echo "   llm = ChatGroq(verbose=True)"
echo "   response = llm.generate(messages=[{'role': 'user', 'content': 'What is acne?'}])"
echo "   print(response)"
echo "   \""
echo ""

# View Logs
echo "8. VIEW LOGS (with DEBUG_MODE=True)"
echo "   tail -f app.log"
echo ""

# Check Pinecone
echo "9. CHECK PINECONE INDEX"
echo "   python -c \""
echo "   from pinecone import Pinecone"
echo "   import os"
echo "   from dotenv import load_dotenv"
echo "   load_dotenv()"
echo "   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))"
echo "   index = pc.Index('medical-chatbot')"
echo "   stats = index.describe_index_stats()"
echo "   print(f'Total vectors: {stats.get(\\\"total_vector_count\\\")}')"
echo "   \""
echo ""

# Common Issues
echo "=========================================="
echo "COMMON ISSUES & SOLUTIONS"
echo "=========================================="
echo ""

echo "Issue: '[Groq not configured]' warning"
echo "Solution: pip install langchain-groq>=0.2.1"
echo ""

echo "Issue: Raw metadata in response"
echo "Solution: Already fixed - context cleaning improved"
echo ""

echo "Issue: Empty response"
echo "Solution: Check Pinecone index has documents"
echo ""

echo "Issue: Timeout errors"
echo "Solution: Increase timeout in ChatGroq.__init__()"
echo ""

echo "=========================================="
echo "DOCUMENTATION"
echo "=========================================="
echo ""
echo "- RAG_CONFIGURATION_FIXES.md - Detailed explanation of all fixes"
echo "- DEBUGGING_GUIDE.md - Comprehensive debugging guide"
echo "- test_setup.py - Automated setup verification"
echo ""
