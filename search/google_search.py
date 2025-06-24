import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

# Search function using SerpAPI
def search_fn(query):
    data = GoogleSearch(
        {"q": query, "api_key": os.getenv("SERPAPI_API_KEY", "")}
    ).get_dict()
    results = data.get("organic_results", [])[:5]
    return (
        "\n".join(
            f"{i+1}. {r.get('title')} — {r.get('link')}" for i, r in enumerate(results)
        )
        or "No results found."
    )