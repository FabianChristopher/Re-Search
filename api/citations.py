import requests

def format_citations_box(content):
    html = f"""
    <div style="border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;">
        <h2>Citations</h2>
        {content}
    </div>
    """
    return html

def get_citations(paper_ids, paper_title_map):
    """
    For each paper in paper_ids, call the lookup_citations endpoint
    to fetch 3 citations, and then format the results in HTML.
    
    :param paper_ids: List of paper IDs (strings).
    :param paper_title_map: Dict mapping paper_id to paper title.
    :return: A formatted HTML string with citations.
    """
    if not paper_ids:
        return "<div>No papers available.</div>"
    
    all_citations_html = ""
    for pid in paper_ids:
        paper_title = paper_title_map.get(pid, pid)
        citations_html = f"<h3>Citations for {paper_title}</h3>"
        url = f"http://recommendpapers.xyz/api/lookup_citations?id={pid}&offset=0&limit=3&fields=contexts,intents,citationCount,referenceCount,title,authors"
        try:
            resp = requests.get(url)
            data = resp.json()
            citations = data.get("citations", [])
            if citations:
                for citation in citations:
                    citing = citation.get("citingPaper", {})
                    citing_title = citing.get("title", "No Title")
                    citing_authors = ", ".join([author.get("name", "Unknown") for author in citing.get("authors", [])])
                    contexts = citation.get("contexts", [])
                    context_text = "<br>".join([f"&nbsp;&nbsp;- {ctx}" for ctx in contexts]) if contexts else "&nbsp;&nbsp;- No context provided."
                    citations_html += f"<p>* <strong>{citing_title}</strong><br>&nbsp;&nbsp;Authors: {citing_authors}<br>&nbsp;&nbsp;Contexts:<br>{context_text}</p>"
            else:
                citations_html += "<p>No citations found.</p>"
            all_citations_html += citations_html + "<hr>"
        except Exception as e:
            all_citations_html += f"<p>Error retrieving citations for paper {pid}: {str(e)}</p><hr>"
    
    return format_citations_box(all_citations_html)
