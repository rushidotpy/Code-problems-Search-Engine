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