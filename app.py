"""
Production-Stable Medical Chatbot
Pinecone + Groq Llama 3.1 + Proper LangChain 0.3 RAG
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import logging
from src.prompt import prompt

from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
#from langchain_core.prompts import ChatPromptTemplate

from src.helper import download_embeddings
from src.langchain_groq import ChatGroq

# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
INDEX_NAME = "medical-chatbot"

_retriever = None
_llm = None
_rag_chain = None


# -----------------------------------------------------------------------------
# EMBEDDINGS
# -----------------------------------------------------------------------------

def get_embeddings():
    return download_embeddings()


# -----------------------------------------------------------------------------
# RETRIEVER (NO WRAPPERS — PURE LC RUNNABLE)
# -----------------------------------------------------------------------------

def get_retriever():
    global _retriever

    if _retriever:
        return _retriever

    embeddings = get_embeddings()

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embeddings
    )

    # KEEP k SMALL (avoid context overflow)
    _retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    return _retriever


# -----------------------------------------------------------------------------
# LLM
# -----------------------------------------------------------------------------

def get_llm():
    global _llm

    if _llm:
        return _llm

    _llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=2048  # safe limit for Groq
    )

    return _llm


# -----------------------------------------------------------------------------
# RAG CHAIN (LANGCHAIN 0.3 CORRECT FLOW)
# -----------------------------------------------------------------------------

def get_rag_chain():
    global _rag_chain

    if _rag_chain:
        return _rag_chain

    llm = get_llm()
    retriever = get_retriever()

    combine_docs_chain = create_stuff_documents_chain(
        llm.get_llm(),
        prompt
    )

    _rag_chain = create_retrieval_chain(
        retriever,
        combine_docs_chain
    )

    return _rag_chain


# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chat():
    user_message = request.form.get("msg", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a question."})

    greetings = ["hi", "hello", "hey", "good morning", "good evening"]

    if user_message.lower() in greetings:
        return jsonify({
            "response": "Hello! 👋 I'm your medical assistant. How can I help you today?"
        })

    try:
        rag_chain = get_rag_chain()

        result = rag_chain.invoke({"input": user_message})

        answer = result["answer"].strip()

        return jsonify({"response": answer})

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({"response": "Internal server error."}), 500


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting Medical Chatbot...")
    app.run(host="0.0.0.0", port=5000, debug=False)