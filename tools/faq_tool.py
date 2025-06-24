from langchain.tools import Tool
from rag.rag import vectorstore

faq_tool = Tool(
    name="faq",
    func=lambda q: "\n".join(
        [d.page_content for d in vectorstore.similarity_search(q, k=3)]
    ),
    description="Answer FAQs using vectorstore.",
)