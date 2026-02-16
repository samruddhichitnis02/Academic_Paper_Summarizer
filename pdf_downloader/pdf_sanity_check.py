from pathlib import Path
from pypdf import PdfReader
from pypdf.errors import PdfStreamError

def find_corrupted_pdfs(pdf_dir: str):
    pdf_dir = Path(pdf_dir)
    corrupted = []

    for pdf_path in pdf_dir.glob("*.pdf"):
        try:
            reader = PdfReader(pdf_path, strict=False)
            
            # Force reading pages (important!)
            for _ in reader.pages:
                pass

            print(f"OK: {pdf_path.name}")

        except PdfStreamError:
            print(f"CORRUPTED: {pdf_path.name}")
            corrupted.append(pdf_path.name)

        except Exception as e:
            print(f"ERROR: {pdf_path.name} -> {e}")
            corrupted.append(pdf_path.name)

    return corrupted


# Usage
bad_pdfs = find_corrupted_pdfs(r"C:\Users\samru\Study\Projects_and_learnings\RAG\Academic_Paper_Summarizer\data\papers")

print("\nCorrupted files:")
for pdf in bad_pdfs:
    print(pdf)