from flask import Flask, request, jsonify
from flask_cors import CORS
from api.paper_search import search_papers

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

def handle_intents(user_message):
    print("Received query:", user_message)
    papers = search_papers(user_message)
    print("Papers returned:", papers)
    if not papers or ("error" in papers):
        response_text = "❌ Sorry, I couldn't find any papers on that topic."
    else:
        response_text = "**Here are some relevant research papers:**\n\n"
        for i, paper in enumerate(papers, 1):
            response_text += (
                f"**{i}. {paper['title']}**\n"
                f"🔗 {'[PDF Available]('+paper['pdf']+')' if paper['pdf'] != 'No PDF available' else 'No PDF available'}\n"
                f"👥 Authors: {', '.join(paper['authors'])}\n"
                f"📊 Citations: {paper['citations']}\n\n"
            )
    return {"response": response_text, "papers": papers}

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """Handles user queries and executes the search function."""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"]
    response = handle_intents(user_message)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
