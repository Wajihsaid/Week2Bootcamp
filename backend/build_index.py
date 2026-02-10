import pandas as pd
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

# ---------- CONFIG ----------
CSV_PATH = "../history-of-tunisia.csv"  # adjust if needed
INDEX_PATH = "data/faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------- LOAD DATA ----------
df = pd.read_csv(CSV_PATH)

documents = []
for _, row in df.iterrows():
    content = f"""
Event: {row['name_of_incident']}
Date: {row['year']}
Place: {row['place_name']}
Type: {row['type_of_event']}
Character: {row['historical_character']}
Description: {row['description']}
"""
    documents.append(Document(page_content=content))

print(f"Loaded {len(documents)} documents")

# ---------- EMBEDDINGS ----------
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# ---------- BUILD FAISS ----------
vectorstore = FAISS.from_documents(documents, embeddings)

# ---------- SAVE ----------
os.makedirs(INDEX_PATH, exist_ok=True)
vectorstore.save_local(INDEX_PATH)

print("FAISS index successfully created!")
