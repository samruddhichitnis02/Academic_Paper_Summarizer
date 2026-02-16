from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

load_dotenv()

# Global state for the vector store
_vector_store = None

def process_paper(pdf_path: str) -> int:
    """
    Process a PDF paper and create vector embeddings.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Number of chunks created (0 if failed)
    """
    global _vector_store
    
    try:
        # 1. Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        if not documents:
            print(f"No content extracted from {pdf_path}")
            return 0
        
        # 2. Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            print(f"No chunks created from {pdf_path}")
            return 0
        
        # 3. Embed & Store
        # Use a lightweight local model
        print("Creating embeddings using HuggingFace (sentence-transformers/all-MiniLM-L6-v2)...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # 4. Create or update vector store
        if _vector_store is None:
            _vector_store = FAISS.from_documents(chunks, embeddings)
        else:
            # Add new documents to existing store
            new_store = FAISS.from_documents(chunks, embeddings)
            _vector_store.merge_from(new_store)
        
        print(f"Successfully processed {pdf_path}: {len(chunks)} chunks created")
        return len(chunks)
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        import traceback
        traceback.print_exc()
        return 0

def get_retriever():
    """
    Get the retriever for RAG queries.
    
    Returns:
        Retriever object or None if no documents processed
    """
    global _vector_store
    
    if _vector_store is None:
        print("Warning: No vector store available. Please upload a paper first.")
        return None
    
    # Return retriever with k=4 (retrieve top 4 most relevant chunks)
    return _vector_store.as_retriever(search_kwargs={"k": 4})

def clear_vector_store():
    """
    Clear the global vector store (useful for starting fresh).
    """
    global _vector_store
    _vector_store = None
    print("Vector store cleared")