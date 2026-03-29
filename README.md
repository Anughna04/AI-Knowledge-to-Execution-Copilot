# AI Knowledge-to-Execution Copilot ⚡

A lightning-fast, highly optimized AI Copilot engineered entirely on the **Oxlo.ai** platform. Designed as an intelligent assistant that seamlessly transforms user queries into actionable output—code, structured explanations, images, and grounded knowledge. 

- **Developer / Registered Oxlo Email:** `[]`
- **Use Case:** An AI Copilot for developers and learners that reduces cognitive load by smartly classifying intent. Instead of needing different apps for writing code, understanding dense PDF documents, grasping new conceptual frameworks, or diagramming systems—this single unified interface intelligently routes queries to specialized Oxlo models.

## ✨ Key Features & Architecture

1. **Smart Intent Routing:** Every query undergoes a rapid, lightweight classification to route the prompt to the optimal model flow (Text, Code, Learn, Image).
2. **Semantic Caching & Token Economy:** Tracks exact and semantic matches of previous queries via a local Vector Store (`FAISS`). Identical concepts avoid hitting external APIs, dropping latency to ~0 seconds and saving countless tokens.
3. **Local Document Grounding (RAG):** Upload PDFs to chunk, index, and query via Oxlo's Embeddings model without the overhead of heavy orchestration frameworks.
4. **"Learning Queries" Mode:** Automatically fetches relevant visual diagrams from the Open Web (via DuckDuckGo) to accompany AI-generated structural plans when a user tries to learn a complex topic.
5. **Glassmorphic UI Engine:** Premium dark-mode aesthetics built on Streamlit with custom injected CSS, ensuring the UI looks sharp, minimalist, and responsive.

### 🏛️ System Architecture

```mermaid
graph TD
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef core fill:#10b981,stroke:#047857,color:#fff
    classDef external fill:#8b5cf6,stroke:#5b21b6,color:#fff
    classDef db fill:#f59e0b,stroke:#b45309,color:#fff

    User[User Input] --> UI(Streamlit Interface):::frontend
    
    subgraph Core Logic
        UI -->|Query| Router{Intent Classifier}:::core
        UI -.->|PDF Upload| RAG[Document RAG Engine]:::core
        Router -->|Store History| Mem[Memory Manager]:::core
        Router -->|Lookup| Cache[(FAISS Semantic Cache)]:::db
        RAG -->|Vector Embeddings| Cache
    end

    subgraph External APIs & OSINT
        Router -->|CODE| DeepSeek[DeepSeek Coder 33b]:::external
        Router -->|RESEARCH / LEARN| Tools[Wiki / DuckDuckGo]:::external
        Router -->|GENERAL| Llama[Llama 3.2 3B]:::external
        Tools -.->|Data Context| Llama
        RAG -->|Embedding Gen| OxloEmbed[Oxlo text-embedding-v2]:::external
    end
    
    DeepSeek --> UI
    Llama --> UI
    Cache -.->|Cache Hit| UI
```

### 🔄 Query Execution Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Streamlit UI
    participant C as Semantic Cache
    participant R as Intent Router
    participant T as OSINT Tools
    participant O as Oxlo LLMs
    
    U->>S: Submits Query
    S->>C: Check FAISS Vector Match
    
    alt Cache Hit
        C-->>S: Return Cached Response
        S-->>U: Display Instant Output (⚡ 0 API Cost)
    else Cache Miss
        S->>R: Analyze Query Semantics
        
        alt Intent == CODE
            R->>O: Stream deepseek-coder-33b
        else Intent == RESEARCH
            R->>T: Scrape Web Extracts
            T-->>O: Inject Context Data
            R->>O: Stream Llama 3B Analyst Report
        else Intent == LEARN
            R->>O: Stream Educational Breakdown
            R->>T: Query Wikipedia Native Thumbnail
            T-->>S: Return Graphic URL
        else General
            R->>O: Stream General Chat
        end
        
        O-->>S: Final Markdown
        S->>C: Store Query Vectors
        S-->>U: Display Rich Output
    end
```

## Models Used (Oxlo.ai exclusive)

* **General Intelligence / Intent Router:** `llama-3.2-3b` (Default Text Model)
* **Code Synthesis:** `deepseek-coder-33b` (Triggered upon `CODE` intent)
* **Knowledge Retrieval / RAG:** `bge-large`
* **Diagram Definition:** `stable-diffusion-1.5` (Image generation API)

## 🚀 Setup & Installation

### Requirements
- Python 3.10+
- Oxlo.ai API Key ([Get it here](https://portal.oxlo.ai/))

### Steps

1. Clone or download this directory.
2. Setup the virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set your environment variables:
   Copy `.env.example` to `.env` and insert your API key.
   ```bash
   cp .env.example .env
   ```
4. Run the Copilot!
   ```bash
   streamlit run app.py
   ```

## 🐳 Docker Deployment (Recommended)

For hackathon judges and verifiers, the application has been fully containerized to ensure zero-dependency deployment.

### 1. Build the Image
Navigate to the root directory and build the container:
```bash
docker build -t oxlo-knowledge-copilot .
```

### 2. Run the Container
Run the container, securely injecting your `.env` variables and exposing the Streamlit server on port `8501`:
```bash
docker run -p 8501:8501 --env-file .env oxlo-knowledge-copilot
```
The application will be instantly live at `http://localhost:8501`!

## 🛠️ Tech Stack
- **Backend:** Python + `openai` (Oxlo-compatible wrapper)
- **Frontend:** Streamlit 
- **Vector DB / RAG:** FAISS + PyMuPDF
- **External Web Indexing:** DuckDuckGo / Wikimedia Open API

*Note: LangChain/LangGraph were intentionally avoided to minimize overhead latency and maintain maximum architectural control.*
