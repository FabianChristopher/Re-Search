import os
from config import get_openai_api_key
os.environ["OPENAI_API_KEY"] = get_openai_api_key()

import requests
import xml.etree.ElementTree as ET
import openai
from openai import OpenAI

# Now create the client—no need to pass the key as an argument.
client = OpenAI()

def summarize_fulltext(title, fulltext):
    """
    Summarizes the fulltext of a paper to include only key points for comparison.
    """
    prompt = (
        f"Summarize the following paper, focusing only on the key information "
        f"required for comparing papers, such as research methods, experiments, "
        f"results, and limitations. Please keep the summary concise.\n\n"
        f"Title: {title}\n\nFulltext:\n{fulltext}\n\nSummary:"
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = completion.choices[0].message.content
    except Exception as e:
        summary = f"Error summarizing: {str(e)}"
    return summary

def get_fulltext_core(title):
    core_api_url = "https://api.core.ac.uk/v3/search/works"
    response = requests.get(f"{core_api_url}?query={title}")
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            if result.get("fullText"):
                return result["fullText"]
            elif result.get("sourceFulltextUrls"):
                return result["sourceFulltextUrls"][0]
    return None

def get_fulltext_europepmc(title):
    epmc_api_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    response = requests.get(f"{epmc_api_url}?query={title}&format=json")
    if response.status_code == 200:
        data = response.json()
        result_list = data.get("resultList", {}).get("result", [])
        if result_list:
            result = result_list[0]
            if result.get("fullTextUrl"):
                return result["fullTextUrl"]
    return None

def get_fulltext_arxiv(title):
    arxiv_api_url = "http://export.arxiv.org/api/query"
    response = requests.get(f"{arxiv_api_url}?search_query=ti:{title}&max_results=1")
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        if entries:
            entry = entries[0]
            for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
                if link.attrib.get("type") == "application/pdf":
                    return link.attrib.get("href")
    return None

def retrieve_fulltext(title):
    fulltext = get_fulltext_core(title)
    if fulltext:
        return fulltext
    fulltext = get_fulltext_europepmc(title)
    if fulltext:
        return fulltext
    fulltext = get_fulltext_arxiv(title)
    if fulltext:
        return fulltext
    return "Fulltext not available."

def compare_papers(paper_ids, paper_title_map):
    """
    For the first 3 papers in paper_ids, retrieve fulltexts, summarize them to extract key points,
    then construct a prompt that compares these summaries using the OpenAI API.
    """
    selected_ids = paper_ids[:3]
    summaries = []
    for pid in selected_ids:
        title = paper_title_map.get(pid, "Unknown Title")
        fulltext = retrieve_fulltext(title)
        truncated_text = fulltext  # Optionally, truncate here if needed.
        summary = summarize_fulltext(title, truncated_text)
        summaries.append((title, summary))
    
    prompt = "Compare the following three papers based on their summarized key points. " \
             "Focus on aspects like research methods, experiments, results, and limitations. " \
             "Provide a structured, bullet-pointed comparison format.\n\n"
    
    for i, (title, summary) in enumerate(summaries):
        prompt += f"Paper {i+1} ({title}):\n{summary}\n\n"
    
    prompt += "Please provide the comparison in a clear, structured format."
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        comparison = completion.choices[0].message.content
    except Exception as e:
        comparison = f"Error calling OpenAI API for comparison: {str(e)}"
    
    html = f"""
    <div style="border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;">
        <h2>Paper Comparison</h2>
        <pre>{comparison}</pre>
    </div>
    """
    return html
