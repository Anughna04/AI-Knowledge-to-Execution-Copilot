import numpy as np
import faiss
import streamlit as st
from .oxlo_client import generate_embeddings

class SemanticCache:
    def __init__(self, threshold=0.92):
        self.threshold = threshold
        self.index = None
        
        if "semantic_cache_metadata" not in st.session_state:
            st.session_state.semantic_cache_metadata = []
        if "semantic_cache_embeddings" not in st.session_state:
            st.session_state.semantic_cache_embeddings = []
            
        self._init_faiss_from_state()

    def _init_faiss_from_state(self):
        vectors = st.session_state.semantic_cache_embeddings
        if not vectors:
            return
        dim = len(vectors[0])
        self.index = faiss.IndexFlatIP(dim)
        embeddings_np = np.array(vectors).astype('float32')
        faiss.normalize_L2(embeddings_np)
        self.index.add(embeddings_np)

    def get_cached_response(self, query):
        # 1. Exact text match (0 API calls, fastest)
        for meta in st.session_state.semantic_cache_metadata:
            if meta['query'].strip().lower() == query.strip().lower():
                return meta['response'], True, meta.get('type', 'text')
        
        # 2. Semantic matching
        emb = generate_embeddings(query)
        if not emb:
            return None, False, None
            
        if self.index is None:
             return None, emb, None
            
        emb_np = np.array([emb]).astype('float32')
        faiss.normalize_L2(emb_np)
        
        distances, indices = self.index.search(emb_np, 1)
        if len(distances) > 0 and distances[0][0] >= self.threshold:
            idx = indices[0][0]
            if idx < len(st.session_state.semantic_cache_metadata):
                meta = st.session_state.semantic_cache_metadata[idx]
                return meta['response'], True, meta.get('type', 'text')
                
        return None, emb, None
        
    def add_to_cache(self, query, response, response_type="text", emb=None):
        if not emb:
            emb = generate_embeddings(query)
            if not emb: return
                
        st.session_state.semantic_cache_metadata.append({
            'query': query,
            'response': response,
            'type': response_type
        })
        st.session_state.semantic_cache_embeddings.append(emb)
        
        dim = len(emb)
        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)
            
        emb_np = np.array([emb]).astype('float32')
        faiss.normalize_L2(emb_np)
        self.index.add(emb_np)
        
class MemoryManager:
    def __init__(self, max_history=5):
        self.max_history = max_history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
    def add_message(self, role, content, meta_type="text"):
        st.session_state.chat_history.append({"role": role, "content": content, "type": meta_type})
        
    def get_conversation_for_llm(self):
        # Format for OpenAI struct
        context = []
        # Take the last N messages to avoid overflowing context
        for msg in st.session_state.chat_history[-(self.max_history*2):]:
            if msg['type'] in ['text', 'code']: # Only pass relevant text to LLM
                context.append({"role": msg['role'], "content": msg['content']})
        return context
