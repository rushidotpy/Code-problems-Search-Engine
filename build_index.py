import sqlite3

import numpy as np
import pandas as pd
import pickle
from scipy import sparse 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity  # optional, for quick tests [web:203][web:206][web:211]

conn = sqlite3.connect("problemhunt.db")
df = pd.read_sql_query("SELECT id, title, url, description FROM problems", conn)
conn.close()

texts = df["description"].fillna("").tolist()

vectorizer = TfidfVectorizer(
    max_features=50000,
    stop_words="english",
)
tfidf_matrix = vectorizer.fit_transform(texts)  # shape: (2540, V) [web:214][web:211]

# Save artifacts for the Streamlit app
with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

sparse.save_npz("tfidf_matrix.npz", tfidf_matrix)
df[["id", "title", "url"]].to_csv("metadata.csv", index=False)