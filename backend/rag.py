# backend/rag.py
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vectorstore = FAISS.load_local(
    "data/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

def search(query: str, k: int = 3):
    docs = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
