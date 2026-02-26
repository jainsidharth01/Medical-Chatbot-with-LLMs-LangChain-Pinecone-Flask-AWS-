"""
Stable ChatGroq wrapper for LangChain + Groq.
Fixes incomplete responses, token truncation, and fallback issues.
"""

import os
from typing import Optional, List, Dict, Union
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_groq import ChatGroq as LangChainChatGroq
    LANGCHAIN_GROQ_AVAILABLE = True
except ImportError:
    LANGCHAIN_GROQ_AVAILABLE = False
    print("⚠️ Install: pip install langchain-groq>=0.2.1")


class ChatGroq:
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        top_p: float = 0.9,
        verbose: bool = False,
    ):
        self.verbose = verbose
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model_name or "llama-3.3-70b-versatile"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

        self._llm = None
        self._init_llm()

    # ------------------------------------------------------------------

    def _init_llm(self):
        if not LANGCHAIN_GROQ_AVAILABLE:
            raise RuntimeError("langchain-groq not installed.")

        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY not found.")

        # ✅ CRITICAL FIX: Pass max_tokens + top_p
        self._llm = LangChainChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            timeout=60,
            max_retries=3,
        )

        if self.verbose:
            print("✅ ChatGroq initialized correctly")

    # ------------------------------------------------------------------

    def get_llm(self):
        return self._llm

    # ------------------------------------------------------------------

    def generate(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
    ) -> str:

        if not self._llm:
            raise RuntimeError("LLM not initialized.")

        try:
            if messages:
                response = self._llm.invoke(messages)
            elif prompt:
                response = self._llm.invoke(prompt)
            else:
                return "No input provided."

            content = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )

            return content.strip()

        except Exception as e:
            raise RuntimeError(f"Groq API failed: {str(e)}")