import gradio as gr
import requests
import os
import fitz  # PyMuPDF for PDFs
import docx

from api.citations import get_citations  # Import our get_citations function
from api.bibtex import get_bibtex  # Import the get_bibtex function
from api.compare import compare_papers
from api.summarizer import summarize_papers
from api.literature_review import generate_literature_review
from api.keyword_extraction import extract_main_keyword

# Global variables to store search result data.
paper_ids = []             # List of paper IDs.
paper_title_map = {}       # Mapping: paper_id -> paper title.

def extract_text_from_file(file_path):
    """
    Extracts text from a given file (.txt, .docx, .pdf).
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        elif file_extension == ".docx":
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif file_extension == ".pdf":
            pdf_document = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in pdf_document])
            return text if text else "No extractable text found in the PDF."
        
        else:
            return "Unsupported file format."
    
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def search_and_update(query, file):
    """
    Extracts the main topic keyword from the query (or uploaded file content),
    then passes the extracted keyword to the paper search API.
    """
    global paper_ids, paper_title_map
    paper_ids = []
    paper_title_map = {}

    # If a file is uploaded, extract its content and append it to the query
    if file is not None:
        file_text = extract_text_from_file(file.name)
        if "Error" in file_text:
            return file_text  # Display error message if file extraction fails
        query += " " + file_text  # Append extracted content to query

    # Extract the main topic keyword from the query
    keyword = extract_main_keyword(query)
    print(f"Extracted Keyword: {keyword}")  # Debugging log

    url = "http://127.0.0.1:5000/chatbot"
    headers = {"Content-Type": "application/json"}
    data = {"message": keyword}  # Send extracted keyword instead of full query

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
            gr.Markdown("## Re:Search - AI Powered Research Assistant")
            query_input = gr.Textbox(label="Enter your research query", placeholder="e.g., Find papers on NLP")
            upload_file = gr.File(label="Upload Document - .pdf, .docx, .txt (optional)")
            search_button = gr.Button("Search")
            results_md = gr.Markdown(label="Search Results")
            
            with gr.Row():
                btn_citations = gr.Button("Get Citations")
                btn_summary = gr.Button("Explain Papers")
                btn_bibtex = gr.Button("Get BibTeX Reference")
                btn_compare = gr.Button("Compare Papers")                
                
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
    btn_summary.click(fn=lambda: summarize_papers(paper_ids, paper_title_map), inputs=[], outputs=details_html)
    btn_bibtex.click(fn=lambda: get_bibtex(paper_ids, paper_title_map), inputs=[], outputs=details_html)
    btn_compare.click(fn=lambda: compare_papers(paper_ids, paper_title_map), inputs=[], outputs=details_html)
    
demo.launch(share=True)
