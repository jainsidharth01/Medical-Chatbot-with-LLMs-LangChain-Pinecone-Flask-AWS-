# 🏥 Medical RAG Chatbot (Pinecone + Groq + LangChain 0.3)

A Production-Ready Medical Chatbot built using Retrieval-Augmented Generation (RAG) architecture.

This project uses Pinecone for vector storage, Groq Llama 3.1 as the Large Language Model, and LangChain 0.3 for correct RAG flow implementation. The chatbot provides structured, professional medical responses in clean Markdown format.

---

## 🚀 Features

- ✅ RAG Architecture (LangChain 0.3 Correct Flow)
- ✅ Pinecone Vector Database Integration
- ✅ Groq Llama 3.1 (High-speed inference)
- ✅ HuggingFace Sentence-Transformers Embeddings
- ✅ Structured Markdown Medical Responses
- ✅ Clean UI with Markdown Rendering
- ✅ Flask Backend
- ✅ Error Handling & Logging
- ✅ Production-Stable Dependency Management

---

## 🏗️ Architecture Overview

User Query  
⬇  
Retriever (Pinecone Vector Search)  
⬇  
Relevant Medical Context  
⬇  
Groq LLM (Llama 3.1)  
⬇  
Structured Markdown Response  

---

## 📂 Project Structure

```
Medical-Chatbot/
│
├── app.py                 # Main Flask Application
├── requirements.txt
├── .env
│
├── src/
│   ├── helper.py          # Embeddings + Retriever logic
│   ├── langchain_groq.py  # Groq LLM Wrapper
│   └── prompt.py          # Structured System Prompt
│
├── templates/
│   └── index.html         # Frontend UI
│
├── static/
│   └── style.css          # Styling
│
└── README.md
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/medical-chatbot.git
cd medical-chatbot
```

---

### 2️⃣ Create Virtual Environment

Using Conda:

```bash
conda create -n medibot python=3.10
conda activate medibot
```

Or using venv:

```bash
python -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If needed (dependency safe versions):

```bash
pip install langchain==0.3.26
pip install langchain-pinecone==0.2.8
pip install pinecone>=6.0.0,<8.0.0
pip install langchain-groq==0.2.1
pip install groq==0.8.0
pip install httpx==0.27.0
pip install sentence-transformers
pip install langchain-community
```

---

### 4️⃣ Setup Environment Variables

Create a `.env` file in root directory:

```
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key
```

---

### 5️⃣ Run the Application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:8080
```

---

## 🧠 How RAG Works in This Project

1. User asks a medical question  
2. Query is converted into embeddings  
3. Pinecone retrieves relevant medical documents  
4. Context + Question sent to Groq Llama 3.1  
5. LLM generates structured medical response  

---

## 📝 Response Structure

Each answer follows this structured format:

- Definition  
- Causes  
- Symptoms  
- Risk Factors  
- Complications  
- Treatment  
- Prevention  
- Prognosis  

All responses are generated in Markdown and rendered properly in the UI.

---

## 🔥 Technologies Used

- Python 3.10
- Flask
- LangChain 0.3
- Pinecone Vector Database
- Groq Llama 3.1
- HuggingFace Sentence Transformers
- HTML / CSS / JavaScript
- Marked.js (Markdown Rendering)

---

## 🛡️ Error Handling

- Graceful API error management
- Dependency conflict resolution
- Logging enabled
- Structured JSON responses
- Production-ready RAG flow

---

## 📈 Future Improvements

- Conversation memory
- User authentication
- Streaming responses
- Docker containerization
- Deployment on AWS / Render / Railway
- Admin dashboard

---

## 👨‍💻 Author

**Siddharth Jain**  
B.Tech Computer Science  
MERN Stack | DevOps | Cloud Enthusiast  

---

## ⭐ Support

If you found this project helpful, consider giving it a star on GitHub!