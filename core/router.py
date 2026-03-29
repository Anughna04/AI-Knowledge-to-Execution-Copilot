from .oxlo_client import generate_text
import os
import re

def classify_intent(query):
    """
    Returns one of: 'GENERAL', 'CODE', 'LEARN', 'IMAGE_GEN', 'RESEARCH'
    """
    query_lower = query.lower()
    
    # Fast Rule-Based Routing
    if re.search(r'\b(generate|create|draw|make|show).*\b(image|picture|photo|diagram|architecture)\b', query_lower):
        return "IMAGE_GEN"
        
    if re.search(r'\b(code|function|script|def |python|javascript|bug|fix)\b', query_lower):
        return "CODE"
        
    if re.search(r'\b(research|deep dive|analyze|comprehensive|report|reasoning)\b', query_lower):
        return "RESEARCH"
        
    if re.search(r'\b(explain|how does|what is|teach me|learn|concept)\b', query_lower):
        return "LEARN"
        
    # LLM Fallback Routing
    system_prompt = """
    You are a fast intent classifier. Classify the user's query into exactly ONE of these categories:
    - CODE: The user wants code written, debugged, explained, or refactored.
    - LEARN: The user asks to understand a complex concept, system, or framework.
    - IMAGE_GEN: The user is explicitly asking to generate an image, diagram, or picture.
    - RESEARCH: The user wants an in-depth, structured research report with reasoning/analysis.
    - GENERAL: Basic conversation, general Q&A, or summarizing documents.
    
    Return ONLY the exact category string (CODE, LEARN, IMAGE_GEN, RESEARCH, or GENERAL).
    """
    
    response = generate_text(
        prompt=query,
        model=os.environ.get("OXLO_TEXT_MODEL", "llama-3.2-3b"), 
        system_prompt=system_prompt,
        history=None
    )
    
    val = response.strip().upper()
    valid_intents = ["CODE", "LEARN", "IMAGE_GEN", "RESEARCH", "GENERAL"]
    
    for intent in valid_intents:
        if intent in val:
            return intent
            
    # Default fallback
    return "GENERAL"
