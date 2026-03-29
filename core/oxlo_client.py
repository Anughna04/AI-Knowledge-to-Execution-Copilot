import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_oxlo_client():
    api_key = os.environ.get("OXLO_API_KEY", "dummy_key_for_testing")
    base_url = os.environ.get("OXLO_BASE_URL", "https://api.oxlo.ai/v1")
    return OpenAI(api_key=api_key, base_url=base_url)

client = get_oxlo_client()

def generate_text(prompt, model=None, system_prompt=None, history=None):
    model = model or os.environ.get("OXLO_TEXT_MODEL", "llama-3.2-3b")
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
    model = model or os.environ.get("OXLO_EMBEDDING_MODEL", "text-embedding-v2")
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []


