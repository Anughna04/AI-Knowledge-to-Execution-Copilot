import io
import fitz
import faiss
import numpy as np
import streamlit as st
import os
from .oxlo_client import generate_embeddings, client

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start+chunk_size])
        start += (chunk_size - overlap)
    return chunks

class DocumentRAG:
    def __init__(self):
        if "rag_docs" not in st.session_state:
            st.session_state.rag_docs = [] # List of dicts {chunk: str, embed: list}
        if "rag_index" not in st.session_state:
            st.session_state.rag_index = None

    def process_document(self, file_bytes, file_name):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            
        chunks = chunk_text(text)
        if not chunks:
             return False
        
        model = os.environ.get("OXLO_EMBEDDING_MODEL", "text-embedding-v2")
        
        try:
           # Batch generate embeddings to save API calls / latency
           response = client.embeddings.create(input=chunks, model=model)
           embeddings = [d.embedding for d in response.data]
        except Exception as e:
           st.error(f"Batch embedding failed: {e}")
           return False

        dim = len(embeddings[0])
        if st.session_state.rag_index is None:
             st.session_state.rag_index = faiss.IndexFlatIP(dim)
        
        emb_np = np.array(embeddings).astype('float32')
        faiss.normalize_L2(emb_np)
        st.session_state.rag_index.add(emb_np)
        
        for c, e in zip(chunks, embeddings):
            st.session_state.rag_docs.append({'chunk': c, 'embed': e, 'file': file_name})
            
        return True

    def retrieve(self, query, top_k=3):
        if st.session_state.rag_index is None or st.session_state.rag_index.ntotal == 0:
            return ""
            
        q_emb = generate_embeddings(query)
        if not q_emb: return ""
        
        q_emb_np = np.array([q_emb]).astype('float32')
        faiss.normalize_L2(q_emb_np)
        
        distances, indices = st.session_state.rag_index.search(q_emb_np, top_k)
        
        results = []
        for d, i in zip(distances[0], indices[0]):
            if i < len(st.session_state.rag_docs) and d > 0.4: # Arbitrary similarity threshold
                results.append(st.session_state.rag_docs[i]['chunk'])
                
        return "\n\n---\n\n".join(results)
