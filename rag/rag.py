from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

faq_entries = [
    "What is your refund policy? You can cancel up to 48 hours before check-in for a full refund.",
    "How does the loyalty program work? Members earn 1 point per €1 spent.",
    "Check-in: 3 PM, Check-out: 11 AM.",
    "Pets allowed under 25kg for a €20 fee.",
    "Continental breakfast included with all room rates.",
]

emb = OpenAIEmbeddings(model_name="BAAI/bge-m3")
vectorstore = FAISS.from_texts(faq_entries, emb)