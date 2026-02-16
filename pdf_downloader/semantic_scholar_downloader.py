import os
import time
import requests
from pathlib import Path
from typing import List, Dict


class SemanticScholarDownloader:
    """Download papers from Semantic Scholar"""
    def __init__(self, output_dir: str = "data/papers"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents = True, exist_ok = True)
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.delay = 2  # Seconds between requests

    def search_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for papers on Semantic Scholar"""
        print(f"Searching Semantic Scholar for: '{query}'")
        
        search_url = f"{self.base_url}/paper/search"
        
        params = {
            'query': query,
            'limit': max_results,
            'fields': 'title,authors,year,abstract,openAccessPdf,citationCount,publicationDate'
        }
        
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            papers = data.get('data', [])
            
            # Filter papers that have open access PDFs
            papers_with_pdf = [p for p in papers if p.get('openAccessPdf')]
            
            print(f"Found {len(papers)} papers ({len(papers_with_pdf)} with free PDF)\n")
            return papers_with_pdf
        
        except Exception as e:
            print(f"Error searching Semantic Scholar: {str(e)}")
            return []
    

    def download_paper(self, paper: Dict) -> bool:
        """Download a single paper"""
        try:
            title = paper.get('title', 'Unknown')
            pdf_info = paper.get('openAccessPdf')
            
            if not pdf_info or not pdf_info.get('url'):
                print(f"No PDF available for: {title[:50]}")
                return False
            
            pdf_url = pdf_info['url']
            paper_id = paper.get('paperId', 'unknown')
            
            # Create filename
            safe_title = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title)
            safe_title = safe_title[:100]
            filename = f"S2_{paper_id}_{safe_title}.pdf"
            filepath = self.output_dir / filename
            
            # Skip if exists
            if filepath.exists():
                print(f"Already exists: {filename}")
                return True
            
            print(f"Downloading: {title[:60]}...")
            
            # Download PDF
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save PDF
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Saved: {filename}")
            return True
        
        except Exception as e:
            print(f"Failed: {str(e)}")
            return False
        

    def download_papers(self, query: str, max_results: int = 10) -> int:
        """Search and download papers"""
        print("\n" + "="*70)
        print("Semantic Scholar Paper Downloader")
        print("="*70)
        
        # Search
        papers = self.search_papers(query, max_results)
        
        if not papers:
            print("No papers with free PDFs found")
            return 0
        
        # Show papers
        print("Found papers with free PDFs:")
        print("-" * 70)
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')
            year = paper.get('year', 'N/A')
            citations = paper.get('citationCount', 0)
            print(f"{i}. {title[:70]}")
            print(f"   Year: {year} | Citations: {citations}")
            authors = paper.get('authors', [])
            if authors:
                author_names = [a.get('name', '') for a in authors[:3]]
                print(f"   Authors: {', '.join(author_names)}")
            print()
        
        # Download
        print("\n" + "="*70)
        print("Downloading papers...")
        print("="*70 + "\n")
        
        success_count = 0
        for i, paper in enumerate(papers, 1):
            print(f"[{i}/{len(papers)}]")
            if self.download_paper(paper):
                success_count += 1
            
            if i < len(papers):
                time.sleep(self.delay)
        
        print("\n" + "="*70)
        print(f"Successfully downloaded {success_count}/{len(papers)} papers")
        print(f"Saved to: {self.output_dir}")
        print("="*70 + "\n")
        
        return success_count
    

def main():
    """Example usage"""
    downloader = SemanticScholarDownloader(output_dir="data/papers")
    
    # Download papers
    downloader.download_papers(query = "Medical Imagery",
                               max_results = 10)


if __name__ == "__main__":
    main()