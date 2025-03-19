import requests

def get_bibtex_reference(paper_id, paper_metadata):
    """
    Fetches the BibTeX reference for a given paper ID. If BibTeX is not found,
    constructs a reference using available metadata.
    """
    lookup_bibtex_url = "http://recommendpapers.xyz/api/bibtex"
    response = requests.get(f"{lookup_bibtex_url}?id=CorpusId:{paper_id}")

    if response.status_code == 200:
        data = response.json()
        papers = data.get("papers", [])

        # Check if "papers" exists and is not empty before accessing index 0
        if papers and isinstance(papers, list) and len(papers) > 0:
            if "bibtex" in papers[0]:  # Ensure BibTeX key exists
                return papers[0]["bibtex"]

    # If BibTeX is not found, construct a citation from metadata
    metadata = paper_metadata.get(paper_id, {})
    title = metadata.get("title", "Unknown Title")
    authors = metadata.get("authors", "Unknown Authors")
    journal = metadata.get("journal", "Unknown Journal")
    year = metadata.get("year", "Unknown Year")

    return f"{authors} ({year}). {title}. {journal}."

def generate_literature_review(paper_ids, paper_metadata):
    """
    Generates a structured Literature Review using BibTeX references.
    If BibTeX is unavailable, metadata is used instead.
    """
    if not paper_ids:
        return "<div>No papers available for Literature Review.</div>"
    
    review_content = "<h2>Literature Review</h2><p>Below is the list of references for the papers found in your search results:</p>"
    for pid in paper_ids:
        bibtex_or_metadata = get_bibtex_reference(pid, paper_metadata)
        review_content += f"<h3>{paper_metadata.get(pid, {}).get('title', 'Unknown Title')}</h3><pre>{bibtex_or_metadata}</pre><hr>"

    # Wrap everything in a scrollable HTML box
    html = f"""
    <div style="border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;">
        {review_content}
    </div>
    """
    return html