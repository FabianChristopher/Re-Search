import gradio as gr
import requests

from api.citations import get_citations  # Import our get_citations function
from api.bibtex import get_bibtex  # Import the get_bibtex function
from api.compare import compare_papers

# Global variables to store search result data.
paper_ids = []             # List of paper IDs.
paper_title_map = {}       # Mapping: paper_id -> paper title.

def search_and_update(query, file):
    """
    Combines the query with file text (if provided), calls the backend API,
    and updates the global paper_ids and paper_title_map with returned papers.
    Returns a Markdown summary of the search.
    """
    global paper_ids, paper_title_map
    paper_ids = []
    paper_title_map = {}
    
    if file is not None:
        try:
            with open(file.name, "r", encoding="utf-8") as f:
                file_text = f.read()
            query = query + " " + file_text
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    url = "http://127.0.0.1:5000/chatbot"
    headers = {"Content-Type": "application/json"}
    data = {"message": query}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            markdown_text = response_data.get("response", "No response received")
            papers = response_data.get("papers", [])
            # Build global paper_ids and mapping from id to title.
            for paper in papers:
                if isinstance(paper, dict):
                    pid = str(paper.get("id", "N/A"))
                    title = paper.get("title", "Unknown Title")
                    paper_ids.append(pid)
                    paper_title_map[pid] = title
            return markdown_text
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Request failed: {str(e)}"

# For now, we leave other action functions as placeholders.
def action_placeholder():
    return "Other actions not implemented yet."

with gr.Blocks() as demo:
    with gr.Row():
        # Left Column: Search and action buttons.
        with gr.Column(scale=1):
            gr.Markdown("## Research Assistant")
            query_input = gr.Textbox(label="Enter your research query", placeholder="e.g., Find papers on NLP")
            upload_file = gr.File(label="Upload Document (optional)")
            search_button = gr.Button("Search")
            results_md = gr.Markdown(label="Search Results")
            
            with gr.Row():
                btn_citations = gr.Button("Get Citations")
                btn_summary = gr.Button("Get Literature Review")
                btn_bibtex = gr.Button("Get BibTeX Reference")
                btn_compare = gr.Button("Compare Papers")
                btn_pdf = gr.Button("Get PDF/Fulltext")
                
        # Right Column: Detailed results pane.
        with gr.Column(scale=1):
            details_html = gr.HTML(
                "<div style='border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;'>Detailed Results will appear here.</div>", 
                label="Detailed Results"
            )
    
    # Wire up the search button.
    search_button.click(
        fn=search_and_update,
        inputs=[query_input, upload_file],
        outputs=results_md
    )
    
    # Wire up the "Get Citations" button.
    btn_citations.click(fn=lambda: get_citations(paper_ids, paper_title_map), inputs=[], outputs=details_html)
    
    # Other buttons remain placeholders for now.
    btn_summary.click(fn=action_placeholder, inputs=[], outputs=details_html)
    btn_bibtex.click(fn=lambda: get_bibtex(paper_ids, paper_title_map), inputs=[], outputs=details_html)
    btn_compare.click(fn=lambda: compare_papers(paper_ids, paper_title_map), inputs=[], outputs=details_html)
    btn_pdf.click(fn=action_placeholder, inputs=[], outputs=details_html)

demo.launch(share=True)
