import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_oxlo_client():
    # 1. Grab from local environments OR the Sidebar Override
    api_key = os.environ.get("OXLO_API_KEY")
    base_url = os.environ.get("OXLO_BASE_URL", "https://api.oxlo.ai/v1")
    
    # 2. If it's empty, grab from Streamlit Cloud Native Secrets (TOML)
    if not api_key:
        try:
            api_key = st.secrets.get("OXLO_API_KEY")
            base_url = st.secrets.get("OXLO_BASE_URL", base_url)
            # Rehydrate the OS environment so other components work
            if api_key: os.environ["OXLO_API_KEY"] = api_key
            if base_url: os.environ["OXLO_BASE_URL"] = base_url
        except Exception:
            pass
            
    if not api_key:
        api_key = "dummy_key_for_missing_env_vars"

    return OpenAI(api_key=api_key, base_url=base_url)

def generate_text(prompt, model=None, system_prompt=None, history=None):
    client = get_oxlo_client() # Dynamically initialize to capture latest Override key
    
    # Same logic to fallback to Streamlit secrets for model name
    if not model:
        model = os.environ.get("OXLO_TEXT_MODEL")
        if not model:
            try: model = st.secrets.get("OXLO_TEXT_MODEL", "llama-3.2-3b")
            except: model = "llama-3.2-3b"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {e}"

def generate_embeddings(text, model=None):
    client = get_oxlo_client()
    
    if not model:
        model = os.environ.get("OXLO_EMBEDDING_MODEL")
        if not model:
            try: model = st.secrets.get("OXLO_EMBEDDING_MODEL", "bge-large")
            except: model = "bge-large"
            
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []


