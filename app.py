import streamlit as st
import os
import time

# --- Setup & Config ---
st.set_page_config(page_title="Knowledge-to-Execution Copilot", page_icon="⚡", layout="wide")

from ui.style import apply_custom_css
apply_custom_css()

from core.oxlo_client import generate_text
from core.cache_memory import SemanticCache, MemoryManager
from core.rag import DocumentRAG
from core.tools import fetch_web_image, fetch_web_research
from core.router import classify_intent
import re

# --- Initialize Session State ---
if 'api_calls' not in st.session_state:
    st.session_state.api_calls = 0
if 'cache_hits' not in st.session_state:
    st.session_state.cache_hits = 0
if 'tokens_saved' not in st.session_state:
    st.session_state.tokens_saved = 0

cache_mgr = SemanticCache()
mem_mgr = MemoryManager(max_history=6)
rag_mgr = DocumentRAG()

# --- Sidebar UI ---
with st.sidebar:
    st.image("https://portal.oxlo.ai/assets/logo.png", width=150) # Assuming an Oxlo logo exists or placeholder
    st.title("⚡ AI Copilot")
    st.markdown("Powered exclusively by **Oxlo.ai** APIs.")
    
    st.subheader("📊 Efficiency Metrics")
    col1, col2 = st.columns(2)
    col1.metric("API Calls", st.session_state.api_calls)
    col2.metric("Cache Hits", f"{st.session_state.cache_hits}")
    st.metric("Estimated Tokens Saved", f"~{st.session_state.cache_hits * 1500}")
    
    st.divider()
    
    st.subheader("📄 Upload Grounding Doc (RAG)")
    uploaded_file = st.file_uploader("Upload PDF context", type=["pdf"])
    if uploaded_file:
        with st.spinner("Processing embeddings via Oxlo.ai..."):
            if rag_mgr.process_document(uploaded_file.read(), uploaded_file.name):
                st.success("Document Embedded & Indexed!")
                st.session_state.api_calls += 1 # 1 batch embedding call
    
    st.divider()
    
    st.subheader("🔑 Demo Settings")
    override_key = st.text_input("Oxlo API Key (Optional)", type="password", help="If the public hackathon API limit is reached, Judges can securely enter their own key here to continue testing.")
    if override_key:
        os.environ["OXLO_API_KEY"] = override_key
        st.success("API Key injected for this session!")

    st.divider()
    st.subheader("🧠 System Memory (Cache)")
    with st.expander("View Stored Queries"):
        if "semantic_cache_metadata" in st.session_state and st.session_state.semantic_cache_metadata:
            for idx, item in enumerate(st.session_state.semantic_cache_metadata):
                st.markdown(f"**Q:** {item['query']}")
                st.caption(f"Type: {item.get('type', 'text')}")
        else:
            st.caption("No queries cached yet.")

# --- Main UI ---
st.title("Knowledge-to-Execution Copilot")
st.markdown("Ask general questions, request code snippets, upload PDFs for context, or explore new educational concepts.")

if not st.session_state.chat_history:
    st.markdown("### 💡 Try asking:")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**💻 Write Code**\n\n*Copy below:*\n`Write a Python API using FastAPI and explain the code.`")
        st.info("**🎓 Learn a Concept**\n\n*Copy below:*\n`Explain how Quantum Computing works and its core principles.`")
    with col2:
        st.info("**🔬 Deep Research**\n\n*Copy below:*\n`Research the latest developments in Quantum Entanglement algorithms.`")
        st.info("**📄 Document Q&A** *(Upload a PDF on the left first!)*\n\n*Copy below:*\n`Summarize the key findings from the uploaded document.`")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["type"] == "image_url":
            st.image(msg["content"], use_container_width=True)
        elif msg["type"] == "text" or msg["type"] == "code":
            st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("How can I help you today?"):
    # Add user message
    st.chat_message("user").markdown(prompt)
    mem_mgr.add_message("user", prompt)
    
    # 1. Check Sematic Cache
    st.toast("Checking cache...", icon="🔍")
    t0 = time.time()
    cached_resp, is_exact, c_type = cache_mgr.get_cached_response(prompt)
    
    if cached_resp:
        st.session_state.cache_hits += 1
        t_elapsed = time.time() - t0
        with st.chat_message("assistant"):
            st.caption(f"⚡ Returned from Cache in {t_elapsed:.2f}s (0 Oxlo API calls)")
            if c_type == "image_url":
                st.image(cached_resp, use_container_width=True)
            else:
                st.markdown(cached_resp)
        mem_mgr.add_message("assistant", cached_resp, meta_type=c_type)
        st.rerun()
    
    # Not in cache, proceed to Execution
    st.toast("Executing pipeline...", icon="⚙️")
    
    # Intent tracking
    intent = classify_intent(prompt)
    st.session_state.api_calls += 1 # Classification call
    
    # RAG Check
    doc_context = rag_mgr.retrieve(prompt)
    if doc_context:
         st.session_state.api_calls += 1 # RAG query embedding call
    
    # Select Model based on Intent
    model = os.environ.get("OXLO_TEXT_MODEL", "llama-3.2-3b")
    
    # Base/General System Prompt
    sys_prompt = """You are Oxlo Copilot, an elite AI assistant engineered for high-performance cognitive tasks.
Your primary objective is to deliver precise, highly legible, and actionable responses.
- Use markdown formatting extensively (bolding, lists, blockquotes).
- Be direct, avoiding unnecessary fluff while maintaining a professional and encouraging tone.
- If a query is ambiguous, state your assumptions clearly before answering.
- ALWAYS conclude your response with an encouraging remark and an explicit invitation for follow-up questions."""
    
    if intent == "CODE":
         model = os.environ.get("OXLO_CODE_MODEL", "deepseek-coder-33b-instruct")
         sys_prompt = """You are a Principal Software Architect AI. You output production-grade, secure, and highly optimized code.
- Prioritize best practices, clear naming conventions, and robust error handling.
- Briefly explain the core logic *before* providing the code block.
- Write modular, readable code inside markdown blocks with correct syntax highlighting.
- Provide inline comments explaining complex operations or time-complexities.
- ALWAYS conclude with an encouraging remark and ask if the user needs help extending the implementation."""
         
    elif intent == "RESEARCH":
         sys_prompt = """You are a Senior Strategic Research Analyst AI. You execute comprehensive, data-driven web analyses.
A live web scraping agent has retrieved relevant, up-to-date context from the internet and appended it below.
Your task:
- Synthesize the retrieved web data into a highly professional Research Report.
- Use Markdown headers exactly in this structure: 
  ### 📊 Executive Summary
  ### 🔬 Detailed Analysis
  ### 💡 Key Findings
  ### 🏁 Conclusion
- Maintain an objective, academic tone. Explicitly ground your reasoning in the provided live context.
- ALWAYS conclude with an encouraging remark inviting follow-up inquiries."""
    
    if doc_context:
         sys_prompt += f"\n\nContext to ground your answer on from user's document:\n{doc_context}"

    # Build history context
    history = mem_mgr.get_conversation_for_llm()

    with st.chat_message("assistant"):
        with st.spinner(f"Generating ({intent}) with `{model}`..."):
             if intent == "RESEARCH":
                  st.markdown(f"**Intent Recognized:** 🔬 `Web-Augmented Research`")
                  st.toast("Scraping live web data...", icon="🌐")
                  
                  # Pipeline Step 1: Web Fetch
                  web_context = fetch_web_research(prompt)
                  if web_context:
                       sys_prompt += f"\n\n{web_context}"
                       st.caption("*(Integrating live web data into report...)*")
                  else:
                       st.warning("Web scrape rate-limited. Falling back to internal model knowledge.")
                       
                  # Pipeline Step 2: Synthesis
                  response = generate_text(prompt, model=model, system_prompt=sys_prompt, history=history)
                  st.session_state.api_calls += 1
                  
                  if "API Error" in response:
                      st.error(response)
                      mem_mgr.add_message("assistant", f"⚠️ {response}", meta_type="text")
                  else:
                      st.markdown(response)
                      mem_mgr.add_message("assistant", response, meta_type="text")
                      cache_mgr.add_to_cache(prompt, response)
             elif intent == "LEARN":
                  # Fetch a learning concept diagram from the web via DDG (0 API Calls logic)
                  sys_prompt = """You are an Elite Technical Educator. Your goal is to break down complex concepts into intuitive, brilliant mental models.
Format your response strictly using these Markdown sections:
### 🧠 Core Understanding
(A simple, brilliant elevator pitch of the concept)
### 📖 Deep Dive Explanation
(A structured, detailed breakdown of the mechanics or context)
### 🛠️ Step-by-Step Mechanics
(Numbered list detailing how the concept functions logically)

Use analogies where deeply helpful. ALWAYS conclude with an encouraging remark and an explicit invitation for follow-up questions.
CRITICAL INSTRUCTION: On the very last line of your response, you MUST output the exact title of the most relevant Wikipedia article for this specific concept to help us ground the diagram visual, formatted exactly like this:
WIKI_TITLE: [Exact Wikipedia Article Title Here]"""
                  
                  response = generate_text(prompt, model=model, system_prompt=sys_prompt, history=history)
                  st.session_state.api_calls += 1
                  
                  if "API Error" in response:
                      st.error(response)
                      mem_mgr.add_message("assistant", f"⚠️ {response}", meta_type="text")
                  else:
                      # Parse WIKI_TITLE natively
                      extracted_wiki_title = None
                      match = re.search(r'WIKI_TITLE:\s*(.*)', response)
                      if match:
                          extracted_wiki_title = match.group(1).strip()
                          # Hide the instruction from the final UI
                          response = response.replace(match.group(0), "").strip()

                      # Display layout
                      st.markdown(f"**Intent Recognized:** 📘 `Learning Concept`")
                      st.markdown(response)
                      
                      # Web Image using exact Wikipedia title
                      img_url = fetch_web_image(prompt, exact_wiki_title=extracted_wiki_title)
                      if img_url and img_url.startswith("http"):
                          st.image(img_url, caption=f"Visual Reference: {extracted_wiki_title}")
                          response += f"\n\n![Visual Reference from the Web]({img_url})"
                          
                      mem_mgr.add_message("assistant", response, meta_type="text")
                      cache_mgr.add_to_cache(prompt, response)
                  
             else:
                  # CODE or GENERAL
                  st.markdown(f"**Intent:** `{intent}` | **Model:** `{model}`")
                  response = generate_text(prompt, model=model, system_prompt=sys_prompt, history=history)
                  st.session_state.api_calls += 1
                  
                  if "API Error" in response:
                      st.error(response)
                      mem_mgr.add_message("assistant", f"⚠️ {response}", meta_type="text")
                  else:
                      st.markdown(response)
                      mem_mgr.add_message("assistant", response, meta_type="text")
                      cache_mgr.add_to_cache(prompt, response)
                  
    st.rerun()
