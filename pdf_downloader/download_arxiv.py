import os
import time
import requests
from pathlib import Path
from typing import List, Dict
import xml.etree.ElementTree as ET
from urllib.parse import quote


class ArXivDownloader:
    """Download papers from ArXiv.org"""

    def __init__(self, output_dir: str = "data/papers"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents = True, exist_ok = True)
        self.base_url = "http://export.arxiv.org/api/query"
        self.delay = 3  # Seconds between requests (be nice to ArXiv)


    def search_papers(self, query: str, max_results: int = 10, sort_by: str = "relevance") -> List[Dict]:
        """
        Search for papers on ArXiv
        
        Args:
            query: Search query (e.g., "deep learning")
            max_results: Number of papers to find
            sort_by: 'relevance', 'lastUpdatedDate', or 'submittedDate'
        
        Returns:
            List of paper metadata dictionaries
        """
        print(f"Searching ArXiv for: '{query}'")
        print(f"Max results: {max_results}")
        
        # Build query URL
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(self.base_url, params = params)
            response.raise_for_status()
            
            # Parse XML response
            papers = self._parse_arxiv_response(response.text)
            
            print(f"Found {len(papers)} papers")
            return papers
        
        except Exception as e:
            print(f"Error searching ArXiv: {str(e)}")
            return []
        

    def _parse_arxiv_response(self, xml_text: str) -> List[Dict]:
        """Parse ArXiv API XML response"""
        papers = []
        
        # Parse XML
        root = ET.fromstring(xml_text)
        
        # Define namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Extract paper information
        for entry in root.findall('atom:entry', ns):
            paper = {}
            
            # Title
            title_elem = entry.find('atom:title', ns)
            paper['title'] = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Unknown"
            
            # ArXiv ID
            id_elem = entry.find('atom:id', ns)
            if id_elem is not None:
                arxiv_id = id_elem.text.split('/abs/')[-1]
                paper['arxiv_id'] = arxiv_id
                paper['pdf_url'] = f"http://arxiv.org/pdf/{arxiv_id}.pdf"
            
            # Authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            paper['authors'] = authors
            
            # Published date
            published_elem = entry.find('atom:published', ns)
            paper['published'] = published_elem.text[:10] if published_elem is not None else "Unknown"
            
            # Summary
            summary_elem = entry.find('atom:summary', ns)
            paper['summary'] = summary_elem.text.strip()[:200] if summary_elem is not None else ""
            
            papers.append(paper)
        
        return papers
    
    def download_paper(self, paper: Dict) -> bool:
        """Download a single paper"""
        try:
            arxiv_id = paper['arxiv_id']
            title = paper['title']
            pdf_url = paper['pdf_url']
            
            # Create safe filename
            safe_title = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title)
            safe_title = safe_title[:100]  # Limit length
            filename = f"{arxiv_id}_{safe_title}.pdf"
            filepath = self.output_dir / filename
            
            # Skip if already exists
            if filepath.exists():
                print(f"Already exists: {filename}")
                return True
            
            print(f"Downloading: {title[:60]}...")
            
            # Download PDF
            response = requests.get(pdf_url, stream=True)
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
        

    def download_papers(self, query: str, max_results: int = 10, sort_by: str = "relevance") -> int:
        """
        Search and download papers from ArXiv
        
        Returns:
            Number of successfully downloaded papers
        """
        print("\n" + "="*70)
        print("ArXiv Paper Downloader")
        print("="*70)
        
        # Search for papers
        papers = self.search_papers(query, max_results, sort_by)
        
        if not papers:
            print("No papers found")
            return 0
        
        # Show papers found
        print("Found papers:")
        print("-" * 70)
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper['title'][:70]}")
            print(f"   Authors: {', '.join(paper['authors'][:3])}")
            print(f"   Published: {paper['published']}")
            print()
        
        # Confirm download
        response = input(f"\nDownload all {len(papers)} papers? (y/n): ").lower()
        if response != 'y':
            print("Download cancelled")
            return 0
        
        # Download papers
        print("\n" + "="*70)
        print("Downloading papers...")
        print("="*70 + "\n")
        
        success_count = 0
        for i, paper in enumerate(papers, 1):
            print(f"[{i}/{len(papers)}]")
            if self.download_paper(paper):
                success_count += 1
            
            # Be nice to ArXiv servers
            if i < len(papers):
                time.sleep(self.delay)
        
        print("\n" + "="*70)
        print(f"Successfully downloaded {success_count}/{len(papers)} papers")
        print(f"Saved to: {self.output_dir}")
        print("="*70 + "\n")
        
        return success_count
    
    def download_by_ids(self, arxiv_ids: List[str]) -> int:
        """Download papers by ArXiv IDs"""
        print("\n" + "="*70)
        print("Downloading papers by ArXiv IDs")
        print("="*70 + "\n")
        
        success_count = 0
        for i, arxiv_id in enumerate(arxiv_ids, 1):
            paper = {
                'arxiv_id': arxiv_id,
                'title': arxiv_id,
                'pdf_url': f"http://arxiv.org/pdf/{arxiv_id}.pdf"
            }
            
            print(f"[{i}/{len(arxiv_ids)}]")
            if self.download_paper(paper):
                success_count += 1
            
            if i < len(arxiv_ids):
                time.sleep(self.delay)
        
        print("\n" + "="*70)
        print(f"Downloaded {success_count}/{len(arxiv_ids)} papers")
        print("="*70 + "\n")
        
        return success_count
    
def main():
    """Example usage"""
    downloader = ArXivDownloader(output_dir="data/papers")
    
    # Example 1: Search and download
    print("EXAMPLE 1: Search and Download")
    downloader.download_papers(
        # query = "transformer architecture",
        query = "Forgery Detection",
        max_results = 1,
        sort_by = "relevance"
    )
    
    # Example 2: Download specific papers by ID
    # print("EXAMPLE 2: Download by ArXiv IDs")
    # famous_papers = [
    #     "1706.03762",  # Attention Is All You Need
    #     "1810.04805",  # BERT
    #     "1512.03385",  # ResNet
    # ]
    # downloader.download_by_ids(famous_papers)



if __name__ == "__main__":
    main()