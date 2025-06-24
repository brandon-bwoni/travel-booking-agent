from langchain.tools import Tool
from search.google_search import search_fn

search_tool = Tool(
    name="search",
    func=search_fn,
    description="Fetch up-to-date web results via SerpAPI.",
)