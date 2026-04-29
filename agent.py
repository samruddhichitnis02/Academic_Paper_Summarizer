from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
from utils import get_retriever

load_dotenv()

# 1. Define State
class AgentState(TypedDict):
    paper_id: str
    query: str
    summary: str
    critique: str
    revision_count: int

# 2. Initialize Model
# Using HuggingFace Inference API (free tier)
# Requires HUGGINGFACEHUB_API_TOKEN in .env
repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"
_llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.3,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    task="text-generation"
)
llm = ChatHuggingFace(llm=_llm)

# 3. Define Nodes
def summarize_node(state: AgentState):
    """
    Generates initial summary using RAG.
    """
    retriever = get_retriever()
    if not retriever:
        return {"summary": "Error: Please upload a paper first regarding summarization."}
    
    # Retrieve relevant context
    # We ask for extensive context
    try:
        docs = retriever.invoke("Summarize the paper's core contributions, methodology, results, and conclusion.")
        if not docs:
             return {"summary": "Error: Could not retrieve relevant information from the paper."}
        context_text = "\n\n".join([d.page_content for d in docs])
    except Exception as e:
        return {"summary": f"Error during retrieval: {str(e)}"}
    
    prompt = f"""
    You are an expert academic researcher. 
    Analyze the following text sections from a research paper and provide a comprehensive summary.
    
    Structure your summary cleanly with Markdown:
    ## Abstract
    (Brief overview, 2-3 sentences)

    ## Key Contributions
    - (Bullet point 1)
    - (Bullet point 2)
    
    ## Methodology
    (How they did it)

    ## Results
    (Key quantitative or qualitative findings)
    
    ## Conclusion
    (Implications)

    Context:
    {context_text}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"summary": response.content, "revision_count": 0}

def critique_node(state: AgentState):
    """
    Critiques the summary for missing information.
    """
    summary = state.get("summary", "")
    prompt = f"""
    Review the following research paper summary.
    Does it clearly cover:
    - Methodology?
    - Results?
    - Core Contribution?
    
    If it covers these well enough for a quick summary, respond with EXACTLY "APPROVED".
    If it is missing critical information, list what is missing.
    
    Summary:
    {summary}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"critique": response.content}

def revise_node(state: AgentState):
    """
    Refines the summary based on critique.
    """
    summary = state.get("summary", "")
    critique = state.get("critique", "")
    retriever = get_retriever()
    
    if not retriever:
        return {"summary": summary} # Fallback if retriever lost
        
    # Get more context based on critique
    docs = retriever.invoke(f"Find details about: {critique}")
    context_text = "\n\n".join([d.page_content for d in docs])
    
    prompt = f"""
    Update the summary to address the following critique: {critique}
    
    Use this additional context if helpful:
    {context_text}
    
    Original Summary:
    {summary}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"summary": response.content, "revision_count": state["revision_count"] + 1}

def should_continue(state: AgentState):
    critique = state.get("critique", "")
    revision_count = state.get("revision_count", 0)
    
    if "APPROVED" in critique or revision_count >= 1: # Limit revisions to 1 for speed and cost
        return END
    return "revise"

# 4. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("summarize", summarize_node)
workflow.add_node("critique", critique_node)
workflow.add_node("revise", revise_node)

workflow.set_entry_point("summarize")
workflow.add_edge("summarize", "critique")
workflow.add_conditional_edges(
    "critique",
    should_continue,
    {
        "revise": "revise",
        END: END
    }
)
workflow.add_edge("revise", "critique")

app_agent = workflow.compile()
