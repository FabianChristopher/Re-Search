from config import get_openai_api_key
from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"] = get_openai_api_key()
client = OpenAI()

def summarize_papers(paper_ids, paper_title_map):
    selected_ids = paper_ids

    paper_infos = []
    for pid in selected_ids:
        title = paper_title_map.get(pid, "Unknown Title")
        paper_infos.append(f"- {title}")

    prompt = (
        "You are an academic research assistant. Your goal is to generate structured summaries for each of the following papers given their titles. "
        "Do not invent specific data or hallucinate, but you can analyse their **general methods, contributions, and challenges** based on research.\n\n"
        "**Instructions:**\n"
        "1. Write each summary under the paper title.\n"
        "2. Use clear, readable markdown formatting with bullet points.\n"
        "3. Structure each summary with these sections:\n"
        "   - **Research Focus**\n"
        "   - **Methodologies or Approaches**\n"
        "   - **Expected Results or Applications**\n"
        "   - **Challenges or Limitations**\n\n"
        f"### Papers:\n" + "\n".join(paper_infos) +
        "\n\nGenerate the markdown-formatted summaries below."
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = completion.choices[0].message.content
    except Exception as e:
        summary = f"❌ Error generating summary: {str(e)}"

    html = f"""
    <div style="border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;">
        <h2>Paper Key Points</h2>
        <pre>{summary}</pre>
    </div>
    """
    return html
