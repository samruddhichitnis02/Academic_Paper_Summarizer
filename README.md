# Academic Paper Summarizer & Research Assistant 🎓

An AI-powered research assistant that enhances how users interact with academic papers. The platform combines **Retrieval-Augmented Generation (RAG)** and **Agentic AI (in progress)** to move beyond simple summarization into comparative analysis, research gap discovery, literature trend mapping, and intelligent Q&A.

---

## 🚀 Project Status

**Frontend:** ✅ Complete  
**Backend:** 🔄 In Progress  

### Current Backend Capabilities
- Academic paper **summarization using RAG**
- PDF ingestion and text chunking pipeline
- Embedding-based retrieval

### Planned Backend Capabilities
- Agentic multi‑paper comparison
- Automated research gap extraction
- Intelligent Q&A reasoning agents
- Knowledge graph auto‑generation
- Citation and reference linking

This repository currently demonstrates a **fully functional research UI** with partial AI backend integration.

---

## 🛠 Technology Stack

### Frontend
- **Templating:** Jinja2  
- **Styling:** Vanilla CSS3 (Custom Design System)  
- **Interactivity:** Vanilla JavaScript  
- **Visualizations:**  
  - Chart.js – Literature Trend Mapping  
  - Vis.js – Knowledge Graph Networks  

### Backend (Ongoing)
- **Framework:** FastAPI (Python)  
- **AI Architecture:** Retrieval‑Augmented Generation (RAG) + Agentic AI (Planned Expansion)

---

## 📂 Application Structure

```bash
Academic_Paper_Summarizer/
├── server.py                # FastAPI app entry point
├── templates/               # HTML Templates
│   ├── base.html
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── main.js
        ├── api.js
        └── visuals.js
```

---

## ✨ Features

### Implemented 
- **Smart PDF Upload Dashboard** – Drag & Drop interface with recent paper previews  
- **Paper Summarization View** – Clean, distraction‑free reading panel  
- **Comparative Split‑Screen Analysis** – Dual‑panel synchronized scrolling  
- **Research Gap Detection Cards** – Unsolved problems, contradictions, and future work  
- **Literature Trend Visualization** – Interactive citation and keyword timelines  
- **Interactive Knowledge Graph** – Concept, author, and paper relationships  
- **Chat‑Style Q&A Interface** – Natural language interaction UI with “Thinking…” states  

### Backend Implementation
- **RAG‑Based Academic Paper Summarization**

### Planned Backend Features
- Multi‑paper comparative reasoning  
- Automated research gap detection  
- Agent‑driven conversational Q&A  
- Auto‑generated knowledge graphs  
- Citation intelligence and reference tracing  

---

## 🏃 How to Run

### 1. Activate Environment
```bash
.\agents\Scripts\activate
```

### 2. Start the Server
```bash
uvicorn server:app --reload
```

### 3. Open in Browser
```
http://localhost:8000
```

---


