# Code-problems-Search-Engine

Link: https://code-problems-search-engine-lssgm2c4mtvhz2syyjaptd.streamlit.app/

db.py
```
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

index_path   = os.path.join(BASE_DIR, "Qdata", "index.txt")
q_index_path = os.path.join(BASE_DIR, "Qdata", "Qindex.txt")
qdata_dir    = os.path.join(BASE_DIR, "Qdata")

# 1. Connect to SQLite
conn = sqlite3.connect(os.path.join(BASE_DIR, "problemhunt.db"))
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    url         TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Read titles and links
with open(index_path, encoding="utf-8") as f:
    titles = [line.strip() for line in f]

with open(q_index_path, encoding="utf-8") as f:
    links = [line.strip() for line in f]

# 3. Walk Qdata folders 1..2540
insert_sql = """
INSERT INTO problems (title, url, description)
VALUES (?, ?, ?)
"""

for i in range(1, 2541):  # 1 to 2540 inclusive
    folder = os.path.join(qdata_dir, str(i))
    # assume exactly one .txt file per folder
    txt_files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    if not txt_files:
        raise RuntimeError(f"No .txt file found in {folder}")
    if len(txt_files) > 1:
        raise RuntimeError(f"Multiple .txt files in {folder}: {txt_files}")

    file_path = os.path.join(folder, txt_files[0])
    with open(file_path, encoding="utf-8") as f:
        desc = f.read()

    idx = i - 1  # 0-based index for lists
    cur.execute(insert_sql, (titles[idx], links[idx], desc))
    
cur.execute("SELECT COUNT(*) FROM problems;")
print("Rows in problems:", cur.fetchone()[0])
conn.commit()
cur.close()
conn.close()




```

Build_index.py
```
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
```

app.py
```
import pickle

import numpy as np
import pandas as pd
import streamlit as st
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity  # [web:203][web:208]

@st.cache_resource
def load_index():
    with open("tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    tfidf_matrix = sparse.load_npz("tfidf_matrix.npz")
    meta = pd.read_csv("metadata.csv")
    return vectorizer, tfidf_matrix, meta

vectorizer, tfidf_matrix, meta = load_index()

st.title("Search for the problem")
query = st.text_input("Search coding problems")

top_k = 20

if query:
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, tfidf_matrix)[0]
    top_idx = np.argsort(sims)[::-1][:top_k]

    results = meta.iloc[top_idx].copy()
    results["score"] = sims[top_idx]

    for _, row in results.iterrows():
        st.link_button(row["title"], row["url"])
```
