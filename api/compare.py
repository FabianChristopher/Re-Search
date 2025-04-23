from config import get_openai_api_key
from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"] = get_openai_api_key()
client = OpenAI()

def compare_papers(paper_ids, paper_title_map):
    selected_ids = paper_ids  # Only compare first 3 papers

    paper_infos = []
    for pid in selected_ids:
        title = paper_title_map.get(pid, "Unknown Title")
        paper_infos.append(f"- {title}")

    prompt = (
        "You are a senior academic researcher. Your task is to compare the following research papers given their titles. "
        "Use your expert-level understanding of research to infer what each paper is about.\n\n"
        "For each paper, analyse and compare the **methodologies**, **experiments**, **results**, and **contributions**, and then write a **structured comparison** "
        "highlighting similarities and differences.\n\n"
        "**Instructions:**\n"
        "1. **Do not fabricate data** or pretend to know specific content — base your response purely on knowledge of the paper.\n"
        "2. Use markdown formatting for readability.\n"
        "3. Present your output in the following structure:\n\n"
        "### Comparison of Research Papers\n"
        "- **Paper 1: _Title_**\n"
        "  - Methodologies:\n"
        "  - Key Focus:\n"
        "  - Expected Findings:\n"
        "  - Possible Limitations:\n\n"
        "... repeat for all papers ...\n\n"
        "**🧠 Comparative Insights:**\n"
        "- Point out overlaps in methods or aims\n"
        "- Note any differences in scope, domain, or novelty\n"
        "- Comment on how the papers may complement or contrast each other\n\n"
        f"### Papers to Compare:\n" + "\n".join(paper_infos) +
        "\n\nNow provide the structured markdown comparison below."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        comparison = completion.choices[0].message.content
    except Exception as e:
        comparison = f"❌ Error generating comparison: {str(e)}"

    html = f"""
    <div style="border: 2px solid #333; padding: 10px; height: 90vh; overflow-y: auto;">
        <h2>Paper Comparison</h2>
        <pre>{comparison}</pre>
    </div>
    """
    return html
