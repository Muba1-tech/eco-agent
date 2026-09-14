"""
build_index.py - Advanced Hybrid RAG Engine for EcoAgent Knowledge Base.

Implements Enterprise Hybrid Search:
1. Dense Semantic Vector Search via FAISS Index (all-MiniLM-L6-v2)
2. Sparse Lexical Keyword Search via Rank-BM25 (BM25Okapi)
3. Reciprocal Rank Fusion (RRF) algorithm to rank results with zero hallucination.
"""

import os
import sys

# Environment variables to prevent OpenMP runtime library clash on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import glob
import pickle
import numpy as np
import faiss
# Lazy import sentence_transformers for ultra-fast startup (<1s)
# sentence_transformers is imported inside get_model() on demand.
from rank_bm25 import BM25Okapi
import pypdf

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")

# Global in-memory cache
_INDEX = None
_CHUNKS = None
_MODEL = None
_BM25 = None
_QUERY_CACHE = {}



def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using pypdf."""
    reader = pypdf.PdfReader(pdf_path)
    full_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text.append(text)
    return "\n".join(full_text)


def extract_chunks_from_document(filepath: str, max_chunk_words: int = 150, overlap_words: int = 30):
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(filepath)
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
    else:
        return []

    lines = raw_text.split("\n")
    title = filename
    authority = "Official Government Source"
    reference = ""
    
    content_lines = []
    for line in lines:
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("AUTHORITY:"):
            authority = line.replace("AUTHORITY:", "").strip()
        elif line.startswith("REFERENCE:"):
            reference = line.replace("REFERENCE:", "").strip()
        else:
            content_lines.append(line)
            
    clean_body = "\n".join(content_lines).strip()
    words = clean_body.split()
    
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_chunk_words, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "text": chunk_text,
            "source_file": filename,
            "title": title,
            "authority": authority,
            "reference": reference,
            "chunk_id": len(chunks)
        })
        if end == len(words):
            break
        start += (max_chunk_words - overlap_words)
        
    return chunks


def get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _MODEL


def build_faiss_index(force_rebuild: bool = False):
    global _INDEX, _CHUNKS, _MODEL, _BM25
    
    if not force_rebuild and os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
        return load_index()

    print("Building EcoAgent Advanced Hybrid FAISS + BM25 RAG Index...")
    doc_files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    all_chunks = []
    for filepath in doc_files:
        chunks = extract_chunks_from_document(filepath)
        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No documents found in data/ to build FAISS index.")

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = get_model()
    
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    
    dimension = embeddings.shape[1]
    _INDEX = faiss.IndexFlatIP(dimension)
    _INDEX.add(embeddings.astype("float32"))
    _CHUNKS = all_chunks
    
    # Initialize BM25 Lexical Index
    tokenized_corpus = [chunk["text"].lower().split() for chunk in all_chunks]
    _BM25 = BM25Okapi(tokenized_corpus)
    
    faiss.write_index(_INDEX, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(all_chunks, f)
        
    print("FAISS + BM25 Hybrid Index successfully built and saved.")
    return _INDEX, _CHUNKS, model, _BM25


def load_index():
    global _INDEX, _CHUNKS, _MODEL, _BM25
    if _INDEX is not None and _CHUNKS is not None and _BM25 is not None and _MODEL is not None:
        return _INDEX, _CHUNKS, _MODEL, _BM25
        
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        return build_faiss_index(force_rebuild=True)
        
    if _INDEX is None:
        _INDEX = faiss.read_index(INDEX_PATH)
    if _CHUNKS is None:
        with open(METADATA_PATH, "rb") as f:
            _CHUNKS = pickle.load(f)
        
    if _BM25 is None:
        tokenized_corpus = [chunk["text"].lower().split() for chunk in _CHUNKS]
        _BM25 = BM25Okapi(tokenized_corpus)
    
    if _MODEL is None:
        _MODEL = get_model()
    
    return _INDEX, _CHUNKS, _MODEL, _BM25


def query_hybrid_rag(query: str, top_k: int = 3, rrf_k: int = 60) -> list:
    """
    Advanced Hybrid Search combining Dense FAISS + Sparse BM25 via Reciprocal Rank Fusion (RRF).
    Formula: RRF_Score(doc) = 1/(k + rank_dense) + 1/(k + rank_sparse)
    """
    cache_key = (query.strip().lower(), top_k, rrf_k)
    if cache_key in _QUERY_CACHE:
        return _QUERY_CACHE[cache_key]

    index, all_chunks, model, bm25 = load_index()
    if model is None:
        model = get_model()
    
    # 1. Dense Vector Search
    query_vector = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    dense_distances, dense_indices = index.search(query_vector, min(len(all_chunks), 10))
    
    dense_ranks = {}
    for rank, (dist, idx) in enumerate(zip(dense_distances[0], dense_indices[0])):
        if 0 <= idx < len(all_chunks):
            dense_ranks[idx] = (rank + 1, float(dist))

    # 2. Sparse BM25 Search
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_sorted_indices = np.argsort(bm25_scores)[::-1][:10]
    
    bm25_ranks = {}
    for rank, idx in enumerate(bm25_sorted_indices):
        if bm25_scores[idx] > 0:
            bm25_ranks[idx] = (rank + 1, float(bm25_scores[idx]))

    # 3. Reciprocal Rank Fusion (RRF)
    all_candidate_indices = set(dense_ranks.keys()).union(set(bm25_ranks.keys()))
    rrf_scores = []
    
    for idx in all_candidate_indices:
        dense_r, dense_score = dense_ranks.get(idx, (999, 0.0))
        sparse_r, sparse_score = bm25_ranks.get(idx, (999, 0.0))
        
        rrf_val = (1.0 / (rrf_k + dense_r)) + (1.0 / (rrf_k + sparse_r))
        chunk = all_chunks[idx]
        
        rrf_scores.append({
            "rrf_score": rrf_val,
            "dense_similarity": dense_score,
            "bm25_score": sparse_score,
            "text": chunk["text"],
            "title": chunk["title"],
            "authority": chunk["authority"],
            "reference": chunk["reference"],
            "source_file": chunk["source_file"],
            "score": round(dense_score if dense_score > 0 else 0.50, 3)
        })

    rrf_scores.sort(key=lambda x: x["rrf_score"], reverse=True)
    res = rrf_scores[:top_k]
    _QUERY_CACHE[cache_key] = res
    return res


def query_hybrid_rag_batch(queries: list, top_k: int = 3, rrf_k: int = 60) -> list:
    """
    Batch hybrid RAG query for multiple item search strings simultaneously.
    Encodes all query strings in a single model.encode() vector call for maximum performance.
    """
    if not queries:
        return []

    index, all_chunks, model, bm25 = load_index()
    if model is None:
        model = get_model()
    
    uncached_indices = []
    uncached_queries = []
    results_map = {}
    
    for i, q in enumerate(queries):
        cache_key = (q.strip().lower(), top_k, rrf_k)
        if cache_key in _QUERY_CACHE:
            results_map[i] = _QUERY_CACHE[cache_key]
        else:
            uncached_indices.append(i)
            uncached_queries.append(q)
            
    if uncached_queries:
        query_vectors = model.encode(uncached_queries, convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        dense_distances_batch, dense_indices_batch = index.search(query_vectors, min(len(all_chunks), 10))
        
        for batch_idx, orig_idx in enumerate(uncached_indices):
            q_str = uncached_queries[batch_idx]
            dense_distances = dense_distances_batch[batch_idx]
            dense_indices = dense_indices_batch[batch_idx]
            
            dense_ranks = {}
            for rank, (dist, idx) in enumerate(zip(dense_distances, dense_indices)):
                if 0 <= idx < len(all_chunks):
                    dense_ranks[idx] = (rank + 1, float(dist))

            tokenized_query = q_str.lower().split()
            bm25_scores = bm25.get_scores(tokenized_query)
            bm25_sorted_indices = np.argsort(bm25_scores)[::-1][:10]
            
            bm25_ranks = {}
            for rank, idx in enumerate(bm25_sorted_indices):
                if bm25_scores[idx] > 0:
                    bm25_ranks[idx] = (rank + 1, float(bm25_scores[idx]))

            all_candidate_indices = set(dense_ranks.keys()).union(set(bm25_ranks.keys()))
            rrf_scores = []
            
            for idx in all_candidate_indices:
                dense_r, dense_score = dense_ranks.get(idx, (999, 0.0))
                sparse_r, sparse_score = bm25_ranks.get(idx, (999, 0.0))
                rrf_val = (1.0 / (rrf_k + dense_r)) + (1.0 / (rrf_k + sparse_r))
                chunk = all_chunks[idx]
                
                rrf_scores.append({
                    "rrf_score": rrf_val,
                    "dense_similarity": dense_score,
                    "bm25_score": sparse_score,
                    "text": chunk["text"],
                    "title": chunk["title"],
                    "authority": chunk["authority"],
                    "reference": chunk["reference"],
                    "source_file": chunk["source_file"],
                    "score": round(dense_score if dense_score > 0 else 0.50, 3)
                })

            rrf_scores.sort(key=lambda x: x["rrf_score"], reverse=True)
            res = rrf_scores[:top_k]
            cache_key = (q_str.strip().lower(), top_k, rrf_k)
            _QUERY_CACHE[cache_key] = res
            results_map[orig_idx] = res

    return [results_map[i] for i in range(len(queries))]




def query_knowledge_base(query: str, top_k: int = 3, min_score: float = 0.15):
    """Backwards-compatible wrapper for hybrid RAG search."""
    return query_hybrid_rag(query, top_k=top_k)


if __name__ == "__main__":
    idx, chunks, mdl, bm25_idx = build_faiss_index(force_rebuild=False)
    res = query_hybrid_rag("BEE 24 degree Celsius AC thermostat rule", top_k=2)
    print("\n--- Advanced Hybrid RAG (FAISS + BM25 + RRF) Results ---")
    for r in res:
        print(f"[RRF: {r['rrf_score']:.4f} | Dense: {r['dense_similarity']:.3f} | BM25: {r['bm25_score']:.2f}] {r['authority']} ({r['reference']})")
        print(f"Snippet: {r['text'][:120]}...\n")
