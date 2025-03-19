import requests

def format_bibtex_box(content):
    html = f"""
    <div style="border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;">
        <h2>BibTeX References</h2>
        {content}
    </div>
    """
    return html

def get_bibtex(paper_ids, paper_title_map):
    """
    For each paper in paper_ids, call the BibTeX endpoint to fetch the BibTeX reference,
    then format the results in HTML so that each paper's BibTeX is displayed under its title.
    """
    lookup_bibtex_url = "http://recommendpapers.xyz/api/bibtex"
    if not paper_ids:
        return "<div>No papers available.</div>"
    
    all_bibtex_html = ""
    for pid in paper_ids:
        paper_title = paper_title_map.get(pid, pid)
        # Construct the URL with the expected prefix "CorpusId:".
        url = f"{lookup_bibtex_url}?id=CorpusId:{pid}"
        try:
            resp = requests.get(url)
            data = resp.json()
            papers = data.get("papers", [])
            if papers:
                bibtex_text = papers[0].get("bibtex", "No BibTeX found.")
            else:
                bibtex_text = "No BibTeX found."
            bibtex_html = f"<h3>BibTeX for {paper_title}</h3><pre>{bibtex_text}</pre><hr>"
            all_bibtex_html += bibtex_html
        except Exception as e:
            all_bibtex_html += f"<p>Error retrieving BibTeX for paper {pid}: {str(e)}</p><hr>"
    
    return format_bibtex_box(all_bibtex_html)
