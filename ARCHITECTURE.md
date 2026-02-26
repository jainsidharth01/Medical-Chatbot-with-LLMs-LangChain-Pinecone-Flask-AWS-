# Medical Chatbot - Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Browser)                        │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Medical Chatbot UI                                      │   │
│  │  - Chat interface                                        │   │
│  │  - Message display                                       │   │
│  │  - AJAX requests to /get endpoint                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────���─────────────────────────────────────┘
                              ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION (app.py)                    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Route: /get (POST)                                      │   │
│  │  - Receives user question                                │   │
│  │  - Orchestrates RAG pipeline                             │   │
│  │  - Returns JSON response                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  RAG Pipeline                                            │   │
│  │                                                          │   │
│  │  1. Get Retriever                                        │   │
│  │  2. Get LLM                                              │   │
│  │  3. Build RAG Chain                                      │   │
│  │  4. Invoke Chain                                         │   │
│  │  5. Return Answer                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         ↓                                    ↓
    ┌────────────────┐            ┌──────────────────┐
    │   PINECONE     │            │   GROQ API       │
    │   (Retriever)  │            │   (LLM)          │
    │                │            │                  │
    │ - Vector DB    │            │ - LLaMA3-8b      │
    │ - Embeddings   │            │ - Chat API       │
    │ - Similarity   │            │ - Generation     │
    │   Search       │            │                  │
    └────────────────┘            └──────────────────┘
```

---

## Data Flow - Detailed

### Request Flow
```
User Input: "What is acne?"
    ↓
[Flask /get endpoint]
    ↓
Extract message from form data
    ↓
[Try RAG Chain Path]
    ├─ Get Retriever (lazy init)
    ├─ Get LLM (lazy init)
    ├─ Build RAG Chain (lazy init)
    └─ Invoke: rag_chain.invoke({"input": "What is acne?"})
        ↓
    [Retriever]
        ├─ Convert question to embeddings
        ├─ Search Pinecone index
        └─ Return top 3 documents
        ↓
    [Stuff Documents Chain]
        ├─ Format documents as context
        ├─ Build prompt with context
        └─ Pass to LLM
        ↓
    [ChatGroq (LLaMA3)]
        ├─ Receive prompt with context
        ├─ Generate answer
        └─ Return response
        ↓
    Extract answer from result
    ↓
[If RAG Chain fails → Fallback Path]
    ├─ Manual retriever.get_relevant_documents()
    ├─ Clean context
    ├─ Build messages
    ├─ LLM.generate(messages)
    └─ If LLM fails → Extractive QA
    ↓
Return JSON: {"response": "Acne is a common skin condition..."}
    ↓
[Frontend]
    ├─ Parse JSON
    ├─ Display response
    └─ Show in chat UI
```

---

## Component Initialization (Lazy Loading)

```
First Request
    ↓
[get_embeddings()]
    ├─ Load HuggingFace model (all-MiniLM-L6-v2)
    ├─ Cache in memory
    └─ Return embeddings
    ↓
[get_retriever()]
    ├─ Connect to Pinecone
    ├─ Load existing index (medical-chatbot)
    ├─ Create retriever
    ├─ Cache globally
    └─ Return retriever
    ↓
[get_llm()]
    ├─ Initialize ChatGroq
    ├─ Load LangChain ChatGroq
    ├─ Cache globally
    └─ Return LLM
    ↓
[get_rag_chain()]
    ├─ Create prompt template
    ├─ Create stuff documents chain
    ├─ Create retrieval chain
    ├─ Cache globally
    └─ Return RAG chain
    ↓
Subsequent Requests
    ↓
Use cached components (no re-initialization)
```

---

## Context Processing Pipeline

```
Raw Retrieved Documents
    ↓
[Split into lines]
    ├─ Split by newlines
    └─ Strip whitespace
    ↓
[Filter by alpha ratio]
    ├─ Calculate: alphabetic_chars / total_chars
    ├─ Keep if > 0.30 (30% alphabetic)
    └─ Remove if < 0.30 (likely metadata)
    ↓
[Remove metadata patterns]
    ├─ Pattern 1: ^\d+\s*$ (just numbers)
    ├─ Pattern 2: ^Page\s+\d+ (page references)
    ├─ Pattern 3: ^\d{1,2}/\d{1,2}/\d{2,4} (dates)
    └─ Pattern 4: ^[A-Z\s\-\d]+\s+\d+\s+[A-Z]+\s+\-\s+\d+ (headers)
    ↓
[Validate context]
    ├─ Check if empty
    ├─ Check if < 50 chars
    └─ Use placeholder if invalid
    ↓
[Truncate if needed]
    ├─ Max 3000 characters
    └─ Add "..." if truncated
    ↓
Clean Context Ready for LLM
```

---

## Error Handling & Fallbacks

```
User Request
    ↓
[Try RAG Chain]
    ├─ Success → Return answer
    └─ Fail → Go to Fallback 1
        ↓
[Fallback 1: Manual Retrieval + LLM]
    ├─ Retrieve documents manually
    ├─ Clean context
    ├─ Build messages
    ├─ Call LLM
    ├─ Success → Return answer
    └─ Fail → Go to Fallback 2
        ↓
[Fallback 2: Extractive QA]
    ├─ Parse context and question
    ├─ Split into sentences
    ├─ Rank by token overlap
    ├─ Return top sentences
    └─ Return answer
```

---

## ChatGroq Initialization Flow

```
ChatGroq.__init__()
    ↓
[Load API Key]
    ├─ From parameter
    ├─ Or from GROQ_API_KEY env var
    └─ Store in self.api_key
    ↓
[Check LangChain Groq Available]
    ├─ Try: from langchain_groq import ChatGroq
    ├─ Success → LANGCHAIN_GROQ_AVAILABLE = True
    └─ Fail → LANGCHAIN_GROQ_AVAILABLE = False
    ↓
[Initialize LLM]
    ├─ If not available → self._llm = None
    ├─ If no API key → self._llm = None
    └─ Else:
        ├─ Create LangChainChatGroq instance
        ├─ Set timeout=30, max_retries=2
        ├─ Store in self._llm
        └─ Log success
    ↓
[Ready for Use]
    ├─ get_llm() → Returns self._llm
    ├─ generate(messages) → Calls self._llm.invoke()
    └─ Fallback available if needed
```

---

## Response Generation Paths

### Path 1: RAG Chain (Preferred)
```
Question
    ↓
RAG Chain
    ├─ Retriever: Get documents
    ├─ Stuff Chain: Format context
    └─ LLM: Generate answer
    ↓
Answer
```

### Path 2: Manual Retrieval + LLM (Fallback 1)
```
Question
    ↓
Manual Retriever
    ↓
Clean Context
    ↓
Build Messages
    ↓
LLM.generate()
    ↓
Answer
```

### Path 3: Extractive QA (Fallback 2)
```
Question + Context
    ↓
Parse Context
    ↓
Split into Sentences
    ↓
Rank by Relevance
    ↓
Return Top Sentences
    ↓
Answer
```

---

## API Integration Points

### Pinecone Integration
```
PineconeVectorStore
    ├─ from_existing_index()
    │  ├─ Connect to Pinecone
    │  ├─ Load index: medical-chatbot
    │  └─ Use embeddings: all-MiniLM-L6-v2
    └─ as_retriever()
       ├─ search_type: similarity
       └─ search_kwargs: {"k": 3}
```

### Groq Integration
```
ChatGroq (LangChain)
    ├─ groq_api_key: from env
    ├─ model_name: llama3-8b-8192
    ├─ temperature: 0.0
    └─ Methods:
       ├─ invoke(messages) → Generate response
       └─ batch(messages) → Batch processing
```

---

## Configuration Parameters

### Retriever
```python
search_type = "similarity"      # Similarity search
k = 3                           # Top 3 documents
```

### LLM
```python
model_name = "llama3-8b-8192"   # LLaMA3 8B
temperature = 0.0              # Deterministic
timeout = 30                    # 30 seconds
max_retries = 2                 # Retry twice
```

### Context
```python
max_context_length = 3000       # Max 3000 chars
min_alpha_ratio = 0.30          # 30% alphabetic
min_line_length = 20            # Min 20 chars
```

---

## Monitoring & Debugging

### Health Check Endpoint
```
GET /health
    ↓
Check embeddings
Check retriever
Check LLM
    ↓
Return status
```

### Debug Logging
```
DEBUG_MODE=True
    ↓
Log initialization steps
Log API calls
Log response times
Log errors
```

### Test Script
```
test_setup.py
    ├─ Check env vars
    ├─ Check dependencies
    ├─ Test embeddings
    ├─ Test Pinecone
    ├─ Test retriever
    ├─ Test LLM
    ├─ Test RAG chain
    └─ Report status
```

---

## Performance Metrics

```
Component              Time        Notes
─────────────────────────────────────────────
Embeddings Load        ~2-5s       First request only
Pinecone Connect       ~1-2s       First request only
Retrieval              ~100-500ms  Per request
LLM Generation         ~1-3s       Per request
Total Response         ~2-4s       Typical
─────────────────────────────────────────────
```

---

## Summary

The Medical Chatbot uses a sophisticated RAG pipeline:

1. **Retrieval** - Pinecone finds relevant documents
2. **Augmentation** - LangChain combines documents into context
3. **Generation** - Groq LLaMA3 generates answer

With multiple fallback paths ensuring reliability and comprehensive debugging capabilities for troubleshooting.
