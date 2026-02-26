# Medical Chatbot - RAG Configuration & Debugging Guide

## Overview
This document explains the RAG (Retrieval-Augmented Generation) setup and provides debugging steps for the Medical Chatbot.

---

## Architecture

```
User Question
    ↓
[Flask Route: /get]
    ↓
[Pinecone Retriever] → Fetch top 3 relevant documents
    ↓
[Context Cleaning] → Remove metadata/noise
    ↓
[LangChain RAG Chain] → Combine documents + LLM
    ↓
[ChatGroq (LLaMA3)] → Generate answer
    ↓
[JSON Response] → Return to frontend
```

---

## Configuration

### 1. Environment Variables (.env)

Required variables:
```
PINECONE_API_KEY=your_pinecone_key
GROQ_API_KEY=your_groq_key
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
DEBUG_MODE=False  # Set to True for verbose logging
```

### 2. Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Key packages:
- `langchain==0.3.26` - RAG framework
- `langchain-groq==0.2.1` - Groq integration
- `langchain-pinecone==0.2.8` - Pinecone integration
- `groq>=0.9.0` - Groq SDK

### 3. Pinecone Index

Index name: `medical-chatbot`
- Dimension: 384 (from all-MiniLM-L6-v2)
- Metric: cosine
- Cloud: AWS (us-east-1)

---

## ChatGroq Initialization

### Correct Initialization

```python
from src.langchain_groq import ChatGroq

llm = ChatGroq(
    groq_api_key="your_api_key",  # or from env
    model_name="llama3-8b-8192",
    temperature=0.0,
    verbose=True  # Enable debug logging
)

# Get the underlying LangChain ChatGroq instance
langchain_llm = llm.get_llm()
```

### What Gets Checked

1. **API Key Validation**
   - Reads from `groq_api_key` parameter or `GROQ_API_KEY` env var
   - Logs if key is missing

2. **LangChain Groq Availability**
   - Checks if `langchain-groq` package is installed
   - Falls back to extractive QA if not available

3. **Client Initialization**
   - Creates Groq client with proper timeout/retry settings
   - Logs success/failure

---

## Debugging Steps

### Step 1: Enable Debug Mode

Set in `.env`:
```
DEBUG_MODE=True
```

Or run with debug logging:
```bash
export DEBUG_MODE=True
python app.py
```

### Step 2: Check Component Initialization

Use the health check endpoint:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "embeddings": "✅",
    "retriever": "✅",
    "llm": "✅"
  }
}
```

### Step 3: Verify API Keys

Check if keys are loaded:
```python
import os
from dotenv import load_dotenv

load_dotenv()
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))
```

### Step 4: Test Retriever

```python
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore

embeddings = download_embeddings()
vectorstore = PineconeVectorStore.from_existing_index(
    index_name="medical-chatbot",
    embedding=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Test retrieval
docs = retriever.get_relevant_documents("what is acne?")
for doc in docs:
    print(f"Source: {doc.metadata.get('source')}")
    print(f"Content: {doc.page_content[:200]}...")
    print("---")
```

### Step 5: Test LLM Directly

```python
from src.langchain_groq import ChatGroq

llm = ChatGroq(verbose=True)

# Test with messages
messages = [
    {"role": "system", "content": "You are a medical assistant."},
    {"role": "user", "content": "What is acne?"}
]

response = llm.generate(messages=messages)
print("Response:", response)
```

### Step 6: Test RAG Chain

```python
from app import get_rag_chain

rag_chain = get_rag_chain()
result = rag_chain.invoke({"input": "what is acne?"})
print("Answer:", result["answer"])
```

---

## Common Issues & Solutions

### Issue 1: "[Groq not configured]" Warning

**Cause**: `langchain-groq` package not installed or API key missing

**Solution**:
```bash
pip install langchain-groq>=0.2.1
# Verify GROQ_API_KEY in .env
```

### Issue 2: Raw Metadata in Response

**Cause**: Context not properly cleaned before passing to LLM

**Solution**: The new `clean_context()` function in `app.py` handles this:
- Filters lines with <30% alphabetic characters
- Removes metadata patterns (page numbers, dates, etc.)
- Validates context length

### Issue 3: Empty or "No relevant documents" Response

**Cause**: 
- Pinecone index not populated
- Retriever not finding relevant documents
- Context too short after cleaning

**Solution**:
1. Verify Pinecone index has documents:
   ```python
   from pinecone import Pinecone
   pc = Pinecone(api_key="your_key")
   index = pc.Index("medical-chatbot")
   print(index.describe_index_stats())
   ```

2. Check retrieval quality:
   ```python
   docs = retriever.get_relevant_documents("your question")
   print(f"Retrieved {len(docs)} documents")
   for doc in docs:
       print(f"Score: {doc.metadata.get('score', 'N/A')}")
   ```

### Issue 4: Timeout or Connection Errors

**Cause**: Network issues or API rate limiting

**Solution**:
- Check internet connection
- Verify API keys are valid
- Check Groq API status: https://status.groq.com
- Increase timeout in `ChatGroq.__init__()`:
  ```python
  timeout=60  # Increase from 30
  ```

### Issue 5: LLM Returns Fallback Extraction

**Cause**: Groq API call failed, using extractive QA fallback

**Solution**:
1. Check logs for error details
2. Verify API key is correct
3. Check Groq API rate limits
4. Test with simpler question

---

## Response Flow

### Successful RAG Chain Path
```
User Question
    ↓
RAG Chain Invoked
    ↓
Retriever fetches documents
    ↓
Stuff Documents Chain combines them
    ↓
LLM generates answer
    ↓
Return answer
```

### Fallback Path (if RAG chain fails)
```
User Question
    ↓
Manual Retriever.get_relevant_documents()
    ↓
Clean context
    ↓
Build messages with system prompt
    ↓
LLM.generate(messages)
    ↓
If LLM fails → Extractive QA fallback
    ↓
Return answer
```

---

## Performance Optimization

### 1. Lazy Loading
Components are initialized on first use:
- Embeddings model
- Pinecone retriever
- RAG chain
- LLM

### 2. Caching
Global variables cache initialized components:
```python
_retriever = None
_rag_chain = None
_llm = None
```

### 3. Context Truncation
- Max context length: 3000 characters
- Prevents huge prompts to LLM

### 4. Document Retrieval
- Retrieve top 3 documents (configurable)
- Use similarity search

---

## Testing Checklist

- [ ] `.env` file has valid API keys
- [ ] `pip install -r requirements.txt` completed
- [ ] Pinecone index exists and has documents
- [ ] Health check endpoint returns all ✅
- [ ] Retriever returns relevant documents
- [ ] LLM generates responses (not fallback)
- [ ] Frontend displays responses correctly
- [ ] No "[Groq not configured]" warnings

---

## Logging

Logs are printed to console with format:
```
[Component] Message
```

Examples:
```
[ChatGroq] Initializing with model: llama3-8b-8192
[ChatGroq] API Key present: True
✅ [ChatGroq] Successfully initialized LangChain ChatGroq
[Fallback] Extracting from context (len=1500)
✅ RAG chain response: Acne is a common skin condition...
```

---

## Additional Resources

- LangChain Docs: https://python.langchain.com/
- Groq API Docs: https://console.groq.com/docs
- Pinecone Docs: https://docs.pinecone.io/
- LLaMA3 Model Card: https://huggingface.co/meta-llama/Llama-2-7b-chat

---

## Support

For issues:
1. Enable `DEBUG_MODE=True`
2. Check logs for error messages
3. Run health check endpoint
4. Test individual components
5. Verify API keys and network connectivity
