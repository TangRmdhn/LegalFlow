# app/rag_tools.py
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv
load_dotenv(override=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

DB_PATH = "./db"

if not os.path.exists(DB_PATH):
    print(f"⚠️ WARNING: Folder DB tidak ditemukan di {DB_PATH}. Pastikan path benar.")

vector_store = Chroma(
    collection_name="legal_docs", # Pastikan nama collection sama kayak pas lu ingest
    embedding_function=embeddings,
    persist_directory=DB_PATH 
)

@tool
def search_specific_clause(article_number: int):
    """
    Use this tool ONLY when user asks about specific Article number (Pasal).
    Args:
        article_number: integer (e.g. 5, 27)
    """
    print(f"🕵️ [TOOL] Filtering Pasal {article_number}...")
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3, "filter": {"pasal_num": article_number}}
    )
    docs = retriever.invoke(f"Isi pasal {article_number}")
    return "\n\n".join([d.page_content for d in docs]) if docs else "Pasal tidak ditemukan."

@tool
def search_legal_concept(query: str):
    """
    Use this tool for general concepts, sanctions, or procedures
    when NO specific article number is mentioned.
    """
    print(f"📚 [TOOL] Semantic Search: '{query}'")
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(query)
    return "\n\n".join([d.page_content for d in docs])

# Export list tools
LEGAL_TOOLS = [search_specific_clause, search_legal_concept]