import os
import time
import re
import requests
from pathlib import Path
from typing import List, Dict, Optional


class OpenAlexDownloader:
    """Download open-access papers using OpenAlex (and optionally Unpaywall)."""
    
    def __init__(self, output_dir: str = "data/papers"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.openalex.org/works"
        self.delay = 1.0
        self.timeout = 30

    def search_papers(self, query: str, max_results: int = 10, open_access_only: bool = True, sort_by: str = "relevance") -> List[Dict]:
        """
        Search OpenAlex.

        sort_by:
          - relevance (default)
          - publication_date (most recent first)
          - cited_by_count (most cited first)
        """
        print(f"Searching OpenAlex for: '{query}'")
        print(f"Max results: {max_results}")

        params = {
            "search": query,
            "per_page": min(max_results, 200),
        }

        # OA filter
        if open_access_only:
            params["filter"] = "is_oa:true"

        # Sorting
        sort_map = {"relevance": None,
                    "publication_date": "publication_date:desc",
                    "cited_by_count": "cited_by_count:desc"}
        
        sort_value = sort_map.get(sort_by)
        if sort_value:
            params["sort"] = sort_value

        try:
            r = requests.get(self.base_url, params=params, timeout = self.timeout)
            r.raise_for_status()
            data = r.json()

            results = (data.get("results") or [])[:max_results]
            print(f"Found {len(results)} papers\n")
            return results

        except Exception as e:
            print(f"Error searching OpenAlex: {e}")
            return []
        
    
    def get_paper_info(self, work: Dict) -> Dict:
        """Extract useful fields from OpenAlex work record."""

        title = work.get("title") or "Unknown"
        doi = (work.get("doi") or "").replace("https://doi.org/", "")
        pub_date = work.get("publication_date") or ""
        pub_year = work.get("publication_year") or ""
        cited_by = work.get("cited_by_count", 0)

        # Authors
        authors = []
        for a in (work.get("authorships") or []):
            name = (a.get("author") or {}).get("display_name")
            if name:
                authors.append(name)

        # OA and PDF URLs
        oa = work.get("open_access") or {}
        is_oa = bool(oa.get("is_oa"))
        oa_status = oa.get("oa_status") or ""

        best_oa = work.get("best_oa_location") or {}
        pdf_url = best_oa.get("pdf_url") or ""
        landing_oa = best_oa.get("landing_page_url") or ""

        # Fallback landing page (OpenAlex ID URL)
        landing = (work.get("primary_location") or {}).get("landing_page_url") or work.get("id") or ""

        return {
            "title": title,
            "doi": doi,
            "publication_date": pub_date,
            "publication_year": pub_year,
            "cited_by_count": cited_by,
            "authors": authors,
            "is_oa": is_oa,
            "oa_status": oa_status,
            "pdf_url": pdf_url,
            "oa_landing_url": landing_oa,
            "landing_url": landing,
        }
    
    def download_paper(self, work: Dict) -> bool:
        """Download one paper PDF if a direct OpenAlex pdf_url exists."""
        try:
            info = self.get_paper_info(work)
            title = info["title"]

            if not info["is_oa"]:
                print(f"Not open access - skipping: {title[:60]}...")
                return False

            pdf_url = info["pdf_url"]
            if not pdf_url:
                print(f"No direct PDF link from OpenAlex: {title[:60]}...")
                print(f"OA Landing: {info['oa_landing_url'] or info['landing_url']}")
                return False

            # Safe filename
            safe_title = re.sub(r"[^A-Za-z0-9 _-]+", "_", title).strip()
            safe_title = re.sub(r"\s+", " ", safe_title)[:100]
            name_part = info["doi"].replace("/", "_") if info["doi"] else "NO_DOI"
            filename = f"{name_part}_{safe_title}.pdf"
            filepath = self.output_dir / filename

            if filepath.exists():
                print(f"Already exists: {filename}")
                return True

            print(f"Downloading: {title[:60]}...")
            headers = {"User-Agent": "Mozilla/5.0"}

            time.sleep(self.delay)
            r = requests.get(pdf_url, headers=headers, stream=True, timeout=self.timeout)

            if r.status_code != 200:
                print(f"Download failed (status {r.status_code})")
                print(f"PDF: {pdf_url}")
                return False

            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Sanity check: avoid saving HTML
            if filepath.stat().st_size < 5000:
                with open(filepath, "rb") as f:
                    head = f.read(5)
                if head != b"%PDF-":
                    filepath.unlink(missing_ok=True)
                    print("Not a valid PDF (likely an HTML page).")
                    print(f"OA Landing: {info['oa_landing_url'] or info['landing_url']}")
                    return False

            print(f"Saved: {filename}")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False


    def download_papers(self, query: str, max_results: int = 10, open_access_only: bool = True, sort_by: str = "relevance") -> int:
        """Search and download papers."""
        print("\n" + "=" * 70)
        print("OpenAlex Paper Downloader (No Email)")
        print("=" * 70)

        works = self.search_papers(query, max_results, open_access_only, sort_by)

        if not works:
            print("No papers found")
            return 0

        infos = [self.get_paper_info(w) for w in works]

        print("Found papers:")
        print("-" * 70)
        for i, info in enumerate(infos, 1):
            print(f"{i}. {info['title'][:70]}")
            if info["authors"]:
                print(f"   Authors: {', '.join(info['authors'][:3])}")
            print(f"Date: {info['publication_date']} | Cited by: {info['cited_by_count']}")
            print(f"OA: {'✓' if info['is_oa'] else '✗'} ({info['oa_status']})")
            if info["doi"]:
                print(f"DOI: {info['doi']}")
            if info["pdf_url"]:
                print(f"PDF: {info['pdf_url']}")
            else:
                print(f"Link: {info['oa_landing_url'] or info['landing_url']}")
            print()

        # Write info file
        info_file = self.output_dir / "papers_info.txt"
        with open(info_file, "w", encoding="utf-8") as f:
            f.write("OpenAlex Papers Information (No Email)\n")
            f.write("=" * 70 + "\n\n")
            for i, info in enumerate(infos, 1):
                f.write(f"{i}. {info['title']}\n")
                f.write(f"   Authors: {', '.join(info['authors'][:10])}\n")
                f.write(f"   Date: {info['publication_date']}\n")
                f.write(f"   DOI: {info['doi']}\n")
                f.write(f"   OA: {info['is_oa']} ({info['oa_status']})\n")
                f.write(f"   PDF: {info['pdf_url']}\n")
                f.write(f"   OA Landing: {info['oa_landing_url']}\n")
                f.write(f"   Landing: {info['landing_url']}\n")
                f.write("\n")

        print(f"Paper info saved to: {info_file}")

        resp = input(f"\nDownload PDFs for up to {len(works)} papers? (y/n): ").strip().lower()
        if resp != "y":
            print("Download cancelled")
            return 0

        print("\n" + "=" * 70)
        print("Downloading papers...")
        print("=" * 70 + "\n")

        success = 0
        for i, w in enumerate(works, 1):
            print(f"[{i}/{len(works)}]")
            if self.download_paper(w):
                success += 1

        print("\n" + "=" * 70)
        print(f"Successfully downloaded {success}/{len(works)} papers")
        print(f"Saved to: {self.output_dir}")
        print("=" * 70 + "\n")

        return success
    
def main():
    downloader = OpenAlexDownloader(output_dir="data/papers")

    query = "Object Detection"
    num = 5

    sort_by = "relevance"

    downloader.download_papers(query = query, max_results = num, open_access_only = True, sort_by = sort_by)


if __name__ == "__main__":
    main()