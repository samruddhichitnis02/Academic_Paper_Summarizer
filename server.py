import uvicorn
import shutil
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from typing import List
from agent import app_agent
from utils import process_paper
from dotenv import load_dotenv
from agent import app_agent, answer_question
from utils import clear_vector_store

load_dotenv()


app = FastAPI(title="Academic Paper Summarizer")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Ensure valid upload directory
UPLOAD_DIR = "data/papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

@app.post("/api/upload")
async def upload_papers(files: List[UploadFile] = File(...)):
    uploaded_files = []
    
    print(f"[UPLOAD] Received {len(files)} file(s)")
    
    for file in files:
        print(f"[UPLOAD] File: {file.filename}, content_type: {file.content_type}")
        
        if not file.filename.lower().endswith(".pdf"):
            print(f"[UPLOAD] Skipped non-PDF: {file.filename}")
            continue 
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            contents = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            print(f"[UPLOAD] Saved {file.filename} ({len(contents)} bytes)")
            
            # Process paper for RAG
            
            clear_vector_store()
            chunks_count = process_paper(file_path)
            if chunks_count > 0:
                uploaded_files.append(file.filename)
                print(f"[UPLOAD] Processed {file.filename}: {chunks_count} chunks")
            else:
                print(f"[UPLOAD] Processing returned 0 chunks for {file.filename}")
        except Exception as e:
            print(f"[UPLOAD] Error processing {file.filename}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not uploaded_files:
        return {"status": "error", "message": "No valid PDF files processed"}
        
    return {"status": "success", "message": f"Successfully processed {len(uploaded_files)} papers", "files": uploaded_files}

@app.get("/api/summary/{paper_id}")
async def get_summary(paper_id: str):
    # Trigger the agent workflow
    try:
        # Initial state
        initial_state = {
            "paper_id": paper_id,
            "query": "Summarize this paper thoroughly.",
            "summary": "",
            "critique": "",
            "revision_count": 0
        }
        
        # Invoke agent
        # Note: langgraph invoke returns the final state
        result = app_agent.invoke(initial_state)
        final_summary = result.get("summary", "No summary generated.")
        
        # Format explicitly for frontend if needed, currently just dict
        return {
            "paper_id": paper_id,
            "title": paper_id, # Using filename/id as title since we don't have separate metadata extraction yet
            "authors": "Unknown Authors", # Placeholder
            "summary": final_summary
        }
    except Exception as e:
        print(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comparison")
async def get_comparison():
    # Mock data for now - could be extended with multi-doc agent
    return {
        "papers": ["Paper A", "Paper B"],
        "comparison": [
            {"feature": "Methodology", "paper_a": "Transformer", "paper_b": "LSTM"},
            {"feature": "Accuracy", "paper_a": "89.5%", "paper_b": "84.2%"}
        ]
    }

@app.get("/api/gaps")
async def get_gaps():
    # Mock data for now
    return {
        "unsolved_problems": ["High computational cost", "Lack of interpretability"],
        "future_work": ["Efficient attention mechanisms", "Application to other domains"]
    }

@app.get("/api/trends")
async def get_trends():
    # Mock data for now
    return {
        "years": [2018, 2019, 2020, 2021, 2022],
        "citations": [50, 150, 400, 850, 1200],
        "keywords": ["Self-Attention", "BERT", "GPT-3", "Transformers", "Multimodal"]
    }

@app.post("/api/qa")
async def qa_endpoint(request: Request):
    body = await request.json()
    question = body.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    try:
        answer = answer_question(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
