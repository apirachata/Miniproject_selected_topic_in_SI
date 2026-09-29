import os
import glob
import re
import ollama
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
try:
    import pypdf
except ImportError:
    pypdf = None

EMBEDDING_MODEL = "nomic-embed-text:latest"
CHROMA_PERSIST_DIR = ".chroma_db"
COLLECTION_NAME = "knowledge_base"

class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            try:
                # Try ollama.embed first
                res = ollama.embed(model=self.model_name, input=text)
                if "embeddings" in res and res["embeddings"]:
                    emb = res["embeddings"][0]
                else:
                    emb = res.get("embedding", [])
            except Exception:
                # Fallback to ollama.embeddings
                res = ollama.embeddings(model=self.model_name, prompt=text)
                emb = res.get("embedding", [])
            embeddings.append(emb)
        return embeddings

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Splits text into overlapping chunks by character count, respecting paragraph boundaries where possible."""
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        if len(current_chunk) + len(p) + 2 <= chunk_size:
            current_chunk = (current_chunk + "\n\n" + p).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If paragraph itself is longer than chunk_size, split by sliding window
            if len(p) > chunk_size:
                start = 0
                while start < len(p):
                    sub = p[start:start + chunk_size]
                    chunks.append(sub)
                    start += (chunk_size - overlap)
                current_chunk = ""
            else:
                current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def load_document(file_path: str) -> str:
    """Reads content from .md, .txt, or .pdf files."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.md', '.txt']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == '.pdf':
        if not pypdf:
            return ""
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    return ""

class RAGEngine:
    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = knowledge_dir
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.embedding_fn = OllamaEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def index_knowledge_base(self, force_reindex: bool = False) -> dict:
        """Reads files from knowledge directory, chunks them, and stores embeddings in ChromaDB."""
        if force_reindex:
            try:
                self.chroma_client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )

        supported_extensions = ['*.md', '*.txt', '*.pdf']
        files = []
        for ext in supported_extensions:
            files.extend(glob.glob(os.path.join(self.knowledge_dir, ext)))
            files.extend(glob.glob(os.path.join(self.knowledge_dir, "**", ext), recursive=True))
        
        # Also check root directory for PDFs or MDs if any exist (e.g. casestudy_session_exam.pdf)
        files.extend(glob.glob("*.pdf"))

        files = sorted(list(set(files)))
        
        indexed_files_count = 0
        total_chunks = 0

        for file_path in files:
            file_name = os.path.basename(file_path)
            content = load_document(file_path)
            if not content.strip():
                continue

            chunks = chunk_text(content)
            if not chunks:
                continue

            ids = [f"{file_name}_chunk_{idx}" for idx in range(len(chunks))]
            metadatas = [{"source": file_name, "file_path": file_path, "chunk_index": idx} for idx in range(len(chunks))]

            # Upsert into ChromaDB
            self.collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )

            indexed_files_count += 1
            total_chunks += len(chunks)

        return {
            "status": "success",
            "files_indexed": indexed_files_count,
            "total_chunks": total_chunks
        }

    def retrieve(self, query: str, top_k: int = 4) -> list[dict]:
        """Retrieves top_k relevant text chunks for a query."""
        if self.collection.count() == 0:
            # Auto index if empty
            self.index_knowledge_base()

        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count())
        )

        retrieved = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                retrieved.append({
                    "content": doc,
                    "source": meta.get("source", "Unknown"),
                    "score": round(1.0 - dist, 4) if dist is not None else 1.0
                })

        return retrieved

    def build_rag_system_prompt(self, base_system_prompt: str, retrieved_chunks: list[dict]) -> str:
        """Appends retrieved context chunks to the system prompt."""
        if not retrieved_chunks:
            return base_system_prompt

        context_str = "\n\n".join([
            f"--- Document Source: {chunk['source']} ---\n{chunk['content']}"
            for chunk in retrieved_chunks
        ])

        augmented_prompt = f"""{base_system_prompt}

You are provided with relevant knowledge documents below to accurately answer the user's request.
Base your answer strictly on the provided context where applicable. If the information is found in the context, cite the source filename.

=== RETRIEVED KNOWLEDGE CONTEXT ===
{context_str}
===================================
"""
        return augmented_prompt
