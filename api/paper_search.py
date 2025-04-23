import requests

PAPER_SEARCH_URL = "http://recommendpapers.xyz/api/paper_search"

def search_papers(query):
    """Fetches and parses research papers from the API."""
    params = {
        "query": query,
        "limit": 10,  # Fetch 3 results
        "fields": "title,authors,citationCount,externalIds,paperId",
        "get_pdfs": "True"
    }

    try:
        # Fetch data from API
        response = requests.get(PAPER_SEARCH_URL, params=params)
        response.raise_for_status()  # Raise error if request fails
        api_response = response.json()

        # Ensure 'papers' key exists and is a list
        if not isinstance(api_response.get("papers"), list):
            return {"error": "'papers' should be a list but got something else."}

        # Parse the papers
        papers = []
        for paper in api_response["papers"]:
            external_ids = paper.get("externalIds", {})
            corpus_id = external_ids.get("CorpusId", "Unknown")

            # Safe handling for missing PDF links
            pdf_links = paper.get("pdfs", [])
            pdf_url = pdf_links[0] if pdf_links else "No PDF available"

            papers.append({
                "id": paper.get("paperId", corpus_id),  # Use paperId if available, else CorpusId
                "title": paper.get("title", "Unknown Title"),
                "authors": [author.get("name", "Unknown") for author in paper.get("authors", [])],
                "citations": paper.get("citationCount", 0),
                "pdf": pdf_url,  # Safe PDF handling
                "external_ids": external_ids  # Include all external IDs (ArXiv, DOI, etc.)
            })

        return papers

    except requests.RequestException as e:
        return {"error": str(e)}
