import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools import tool


load_dotenv()

# Global vectorstore variable
_vectorstore = None

def _initialize_vectorstore():
    """Initialize the vectorstore if not already done."""
    global _vectorstore
    if _vectorstore is None:
        file_path = "./document/hotel_faq_document.pdf"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")
        
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents for FAQ tool.")
        
        emb = OpenAIEmbeddings(model="text-embedding-3-large", chunk_size=1000)
        _vectorstore = FAISS.from_documents(docs, emb)
        print(f"Vectorstore initialized with {_vectorstore.index.ntotal} vectors")
    
    return _vectorstore

@tool
def search_hotel_faq(query: str) -> str:
    """
    Search hotel FAQ documents for relevant information.
    
    Args:
        query: The question or topic to search for in the FAQ documents
        
    Returns:
        str: Relevant FAQ content that answers the query
    """
    try:
        vectorstore = _initialize_vectorstore()
        
        # Search for relevant documents
        relevant_docs = vectorstore.similarity_search(query, k=3)
        
        if not relevant_docs:
            return "No relevant FAQ information found for your query."
        
        # Combine the content from relevant documents
        result = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return result
        
    except Exception as e:
        return f"Error searching FAQ: {str(e)}"

# Export the tool for use in LangGraph
faq_tool = search_hotel_faq