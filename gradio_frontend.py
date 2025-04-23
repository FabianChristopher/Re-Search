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
cached_papers = [] 
selected_paper_ids = []
formatted_label_to_id = {}

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

def search_and_update(query, file) -> tuple:
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

            global cached_papers
            cached_papers = papers

            # Build global paper_ids and mapping from id to title.
            for paper in papers:
                if isinstance(paper, dict):
                    pid = str(paper.get("id", "N/A"))
                    title = paper.get("title", "Unknown Title")
                    paper_ids.append(pid)
                    paper_title_map[pid] = title
            html_results = "<div style='line-height:1.8;'>"
            
            for paper in papers:
                pid = str(paper.get("id", "N/A"))
                title = paper.get("title", "Unknown Title")
                html_results += f"""
                    <div style='margin-bottom: 10px;'>
                        <div style='padding:5px 10px; border:1px solid #999; background:#f8f8f8;'>
                            📄 {title}
                        </div>
                    </div>
                """
            html_results += "</div>"

            titles = []
            global formatted_label_to_id
            formatted_label_to_id = {}

            for paper in papers:
                title = paper.get("title", "Unknown Title")
                authors = ", ".join(paper.get("authors", []))
                citations = paper.get("citations", 0)
                pdf_link = paper.get("pdf", None)

                label = f"📄 {title}\n👥 {authors}\n📈 Citations: {citations}"
                if pdf_link:
                    label += f"\n🔗 [PDF]({pdf_link})"

                titles.append(label)
                formatted_label_to_id[label] = str(paper.get("id", "N/A"))

            pdf_links_inner = ""
            for paper in papers:
                title = paper.get("title", "Unknown Title")
                pdf = paper.get("pdf", "").strip()

                if pdf.startswith("http"):
                    pdf_links_inner += f"<li><a href='{pdf}' target='_blank' style='color: #93c5fd;'>{title}</a></li>"
                else:
                    pdf_links_inner += f"<li>{title} <span style='color: #94a3b8;'>(No PDF available)</span></li>"

            if pdf_links_inner:
                pdf_links_html = f"<ul style='padding-left: 20px; margin: 0;'>{pdf_links_inner}</ul>"
            else:
                pdf_links_html = "<p style='color: #cbd5e1;'>No PDF links available for these results.</p>"

            # Safely wrap the links inside the outer styled box directly
            wrapped_pdf_html = f"""
            <div id='pdf-box' style='border: 2px solid #334155; border-radius: 10px; padding: 16px; background-color: #1e293b; color: #e2e8f0; margin-top: 50px; max-height: 200px; overflow-y: auto;'>
                <h3 style='margin-top: 0;'>🔗 PDF Links for Papers</h3>
                {pdf_links_html}
            </div>
            """

            return (
                gr.update(choices=titles, value=[]),
                wrapped_pdf_html
            )

        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Request failed: {str(e)}"

def update_selection(selected_titles):
    global selected_paper_ids
    selected_paper_ids = [
        formatted_label_to_id[label] for label in selected_titles if label in formatted_label_to_id
    ]
    return f"✅ Selected papers: {len(selected_paper_ids)}" 

def guarded_compare():
    if len(selected_paper_ids) < 2:
        return "<div style='color:red;'>⚠️ Please select at least <b>2 papers</b> to compare.</div>"
    return compare_papers(selected_paper_ids, paper_title_map)

def guarded_summary():
    if not selected_paper_ids:
        return "<div style='color:red;'>⚠️ Please select at least <b>1 paper</b> to summarize.</div>"
    return summarize_papers(selected_paper_ids, paper_title_map)

def guarded_bibtex():
    if not selected_paper_ids:
        return "<div style='color:red;'>⚠️ Please select at least <b>1 paper</b> to generate BibTeX.</div>"
    return get_bibtex(selected_paper_ids, paper_title_map, cached_papers)

def guarded_citations():
    if not selected_paper_ids:
        return "<div style='color:red;'>⚠️ Please select at least <b>1 paper</b> to get citation contexts.</div>"
    return get_citations(selected_paper_ids, paper_title_map)

def select_paper(paper_id):
    if paper_id in selected_paper_ids:
        selected_paper_ids.remove(paper_id)
    else:
        selected_paper_ids.append(paper_id)
    return f"✅ Selected papers: {len(selected_paper_ids)}"

# For now, we leave other action functions as placeholders.
def action_placeholder():
    return "Other actions not implemented yet."

with gr.Blocks() as demo:
    with gr.Row():
        # Left Column: Search and action buttons.
        with gr.Column(scale=1):
            gr.Markdown("<h1 style='font-size: 32px; margin-bottom: 20px;'>🔍 Re:Search – AI Powered Research Assistant</h1>")
            query_input = gr.Textbox(label="Enter your research query", placeholder="e.g., Find papers on NLP")
            upload_file = gr.File(label="Upload Document - .pdf, .docx, .txt (optional)")
            search_button = gr.Button("Search")
            paper_selector = gr.CheckboxGroup(choices=[], label="Select Papers", interactive=True)

            selected_display = gr.Markdown("✅ Selected papers: 0")

            # pdf_links_display = gr.Markdown("🔗 PDF links will appear here.")
            
            # with gr.Row():
            #     btn_citations = gr.Button("Get Citations")
            #     btn_summary = gr.Button("Explain Papers")
            #     btn_bibtex = gr.Button("Get BibTeX Reference")
            #     btn_compare = gr.Button("Compare Papers")                
                
        # Right Column: Detailed results pane.
        with gr.Column(scale=1):
            pdf_links_display = gr.HTML("""
                <div id='pdf-box' style='border: 2px solid #334155; border-radius: 10px; padding: 16px; background-color: #1e293b; color: #e2e8f0; margin-top: 50px; max-height: 200px; overflow-y: auto;'>
                    <h3 style='margin-top: 0;'>🔗 PDF Links for Papers</h3>
                    <div id='pdf-content'>PDF links will appear here.</div>
                </div>
            """)
            
            with gr.Row():
                btn_citations = gr.Button("Get Citations")
                btn_summary = gr.Button("Explain Papers")
                btn_bibtex = gr.Button("Get BibTeX Reference")
                btn_compare = gr.Button("Compare Papers")
            
            details_html = gr.HTML(
                "<div style='border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;'>Detailed Results will appear here.</div>",
                label="Detailed Results"
            )

    
    # Wire up the search button.
    search_button.click(
        fn=search_and_update,
        inputs=[query_input, upload_file],
        outputs=[paper_selector, pdf_links_display]
    )

    paper_selector.change(
        fn=update_selection,
        inputs=[paper_selector],
        outputs=[selected_display]
    )
        
    # Wire up the "Get Citations" button.
    btn_citations.click(fn=guarded_citations, inputs=[], outputs=details_html)
    
    # Other buttons remain placeholders for now.
    btn_summary.click(fn=guarded_summary, inputs=[], outputs=details_html)
    btn_bibtex.click(fn=guarded_bibtex, inputs=[], outputs=details_html)
    btn_compare.click(fn=guarded_compare, inputs=[], outputs=details_html)
    
demo.launch(share=True)
