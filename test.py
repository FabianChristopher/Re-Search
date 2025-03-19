from api.paper_search import search_papers

query = "Natural Language Processing"
papers = search_papers(query)
print("✅ Final Processed Papers:", papers)
