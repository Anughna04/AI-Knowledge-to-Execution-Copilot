import time
from duckduckgo_search import DDGS

import json
import urllib.request
import urllib.parse

def fetch_web_image(concept, exact_wiki_title=None):
    """Fetches a relevant educational diagram or picture from Wikipedia Open API."""
    
    # Layer 1: Wikipedia Exact Title Match
    # If the LLM successfully extracted the exact semantic Wikipedia title, skip ambiguous searching entirely!
    try:
        if exact_wiki_title and "WIKI_TITLE" not in exact_wiki_title:
            # 1. Try exact match with redirects resolved
            img_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={urllib.parse.quote(exact_wiki_title)}&pithumbsize=800&redirects=1"
            req2 = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (AI-Copilot)'})
            with urllib.request.urlopen(req2) as resp2:
                img_res = json.loads(resp2.read().decode())
                
            for _, page_data in img_res.get('query', {}).get('pages', {}).items():
                if 'thumbnail' in page_data: return page_data['thumbnail']['source']
                    
            # 2. If no thumbnail, use the LLM's title to search wikipedia natively
            search_query = urllib.parse.quote(exact_wiki_title)
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={search_query}&utf8=1&srlimit=3"
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (AI-Copilot)'})
            with urllib.request.urlopen(req) as response:
                search_res = json.loads(response.read().decode())
                
            for hit in search_res.get('query', {}).get('search', []):
                title = hit['title']
                img_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={urllib.parse.quote(title)}&pithumbsize=800&redirects=1"
                req2 = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (AI-Copilot)'})
                with urllib.request.urlopen(req2) as resp2:
                    img_res = json.loads(resp2.read().decode())
                for _, page_data in img_res.get('query', {}).get('pages', {}).items():
                    if 'thumbnail' in page_data: return page_data['thumbnail']['source']
    except Exception as e:
        pass
                    
    # Layer 2: Otherwise, fall back to stripping conversational stop words and attempting a manual search
    try:
        query = concept.lower()
        stops = ["explain", "how", "do", "does", "what", "is", "teach", "me", "tell", "about", "concept", "of", "the", "working", "work", "works", "principles", "core", "why", "are", "in", "detail", "?", "."]
        for stop in stops:
            query = query.replace(f" {stop} ", " ")
            if query.startswith(f"{stop} "): query = query[len(stop)+1:]
            if query.endswith(f" {stop}"): query = query[:-len(stop)-1]
        
        query = query.strip()
        if not query: return None
        
        search_query = urllib.parse.quote(query)
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={search_query}&utf8=1&srlimit=3"
        
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (AI-Copilot)'})
        with urllib.request.urlopen(req) as response:
            search_res = json.loads(response.read().decode())
            
        for hit in search_res.get('query', {}).get('search', []):
            title = hit['title']
            img_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={urllib.parse.quote(title)}&pithumbsize=800&redirects=1"
            
            req2 = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (AI-Copilot)'})
            with urllib.request.urlopen(req2) as resp2:
                img_res = json.loads(resp2.read().decode())
                
            for _, page_data in img_res.get('query', {}).get('pages', {}).items():
                if 'thumbnail' in page_data: return page_data['thumbnail']['source']
                    
        return None
    except Exception as e:
        print(f"Image Fetch completely failed: {e}")
        return None

def fetch_web_research(query):
    """Fetches recent text snippets from the open web for detailed research, falling back to Wikipedia."""
    # Attempt Primary DuckDuckGo Text Search
    try:
        results = DDGS().text(
            keywords=query,
            region="wt-wt",
            safesearch="moderate",
            max_results=3,
        )
        if results:
            context = "RECENT WEB DATA CONTEXT:\n"
            for i, res in enumerate(results):
                context += f"--- Source {i+1} ---\nTitle: {res.get('title')}\nSnippet: {res.get('body')}\n\n"
            return context
    except Exception:
        pass # Ignore DuckDuckGo 403 Rate Limits
        
    # Attempt Wikipedia Text Search Fallback
    try:
        search_query = urllib.parse.quote(query)
        # Hits Wikipedia API for the top 3 contextual extracts based on the search query
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&generator=search&gsrsearch={search_query}&gsrlimit=3"
        
        req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0 (AI-Copilot)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        pages = data.get('query', {}).get('pages', {})
        if pages:
            context = "WIKIPEDIA RESEARCH CONTEXT:\n"
            for idx, (page_id, page_data) in enumerate(pages.items()):
                title = page_data.get('title', 'Unknown')
                snippet = page_data.get('extract', '')[:800] # Limit paragraph size to avoid massive token costs
                if snippet:
                    context += f"--- Source {idx+1}: {title} ---\n{snippet}...\n\n"
            return context
            
        return ""
    except Exception as e:
        print(f"Web & Wiki Research Search completely failed: {e}")
        return ""
