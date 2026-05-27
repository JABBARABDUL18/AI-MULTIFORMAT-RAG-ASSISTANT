import warnings
warnings.filterwarnings("ignore", message=".*Tried to instantiate class.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import time
import logging

# Fix torch.classes path issue
try:
    import torch
    torch.classes.__path__ = []
except Exception:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from openai import OpenAI

logger = logging.getLogger(__name__)

OPENAI_MODEL = "gpt-3.5-turbo"


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Please paste your key at the top of app.py."
        )
    return OpenAI(api_key=api_key)


class RAGEngine:

    def __init__(self):
        logger.info("Initializing RAG Engine")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        self.documents = []
        self._chunk_count = 0   # track manually for reliable stats

    # ── Indexing ──────────────────────────────────────────────────────────────

    def add_document(self, text: str, filename: str):
        if not text or len(text.strip()) < 50:
            logger.warning(f"Text too short to index for {filename}")
            return

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_text(text)
        chunks = [c.strip() for c in chunks if len(c.strip()) > 50]

        if not chunks:
            logger.warning(f"No valid chunks produced from {filename}")
            return

        metadata = [{"filename": filename} for _ in chunks]

        try:
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_texts(
                    chunks, self.embeddings, metadatas=metadata
                )
            else:
                self.vectorstore.add_texts(chunks, metadatas=metadata)

            self.documents.append(filename)
            self._chunk_count += len(chunks)
            logger.info(f"Added {len(chunks)} chunks from {filename}. Total chunks: {self._chunk_count}")

        except Exception as e:
            logger.error(f"Failed to embed/store chunks from {filename}: {e}")
            raise

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, question: str, k: int = 6):
        if self.vectorstore is None:
            return []
        docs = self.vectorstore.similarity_search(question, k=k)
        return [
            doc.page_content.strip()
            for doc in docs
            if doc.page_content and len(doc.page_content) > 30
        ]

    # ── LLM answer (non-streaming) ────────────────────────────────────────────

    def query(self, question: str) -> str:
        contexts = self.retrieve(question, k=6)
        if not contexts:
            return "No relevant information found in the uploaded documents."

        system_prompt = (
            "You are a precise document assistant. "
            "Answer the user's question using ONLY the context provided below. "
            "Give a clear, complete, well-structured answer in proper English sentences. "
            "If the context does not contain enough information, say so honestly. "
            "Do NOT make up information."
        )
        user_prompt = (
            "Context extracted from the uploaded document(s):\n\n"
            + "\n".join(f"--- Chunk {i+1} ---\n{c}" for i, c in enumerate(contexts))
            + f"\n\nQuestion: {question}\n\nAnswer:"
        )

        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1024,
            )
            answer = response.choices[0].message.content.strip()
            logger.info(f"LLM answered ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._fallback_extract(question, contexts)

    # ── LLM answer (streaming) ────────────────────────────────────────────────

    def stream_answer(self, question: str):
        contexts = self.retrieve(question, k=6)
        if not contexts:
            yield "No relevant information found in the uploaded documents."
            return

        system_prompt = (
            "You are a precise document assistant. "
            "Answer the user's question using ONLY the context provided below. "
            "Give a clear, complete, well-structured answer in proper English sentences. "
            "If the context does not contain enough information, say so honestly. "
            "Do NOT make up information."
        )
        user_prompt = (
            "Context extracted from the uploaded document(s):\n\n"
            + "\n".join(f"--- Chunk {i+1} ---\n{c}" for i, c in enumerate(contexts))
            + f"\n\nQuestion: {question}\n\nAnswer:"
        )

        try:
            client = _get_client()
            stream = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1024,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                token = getattr(delta, "content", None)
                if token:
                    yield token

        except Exception as e:
            logger.error(f"Streaming API call failed: {e}")
            try:
                answer = self.query(question)
                for word in answer.split():
                    yield word + " "
                    time.sleep(0.012)
            except Exception as e2:
                logger.error(f"Fallback query also failed: {e2}")
                yield "Sorry, I encountered an error. Please check your API key and try again."

    # ── Fallback (no API) ─────────────────────────────────────────────────────

    def _fallback_extract(self, question: str, contexts: list) -> str:
        q_words = set(question.lower().split())
        best_ctx = contexts[0]
        best_score = 0
        for ctx in contexts:
            score = len(set(ctx.lower().split()) & q_words)
            if score > best_score:
                best_score = score
                best_ctx = ctx
        return best_ctx[:600]

    # ── Utility ───────────────────────────────────────────────────────────────

    def debug_retrieval(self, question):
        return self.retrieve_docs(question)

    def retrieve_docs(self, question: str, k: int = 5):
        if self.vectorstore is None:
            return []
        docs = self.vectorstore.similarity_search(question, k=k)
        return [doc for doc in docs if doc.page_content and len(doc.page_content) > 30]

    def get_sources(self, question, k=3):
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(question, k=k)

    def stats(self):
        return {
            "chunks": self._chunk_count,
            "docs": len(self.documents)
        }