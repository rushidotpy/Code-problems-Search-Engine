# Code Problems Search Engine

A lightweight search engine for LeetCode problems — fully offline and backed by a local SQLite database.  
I scraped **~2540 LeetCode problems**, including their titles, URLs, and full descriptions, and stored them in a structured dataset to enable fast querying and experimentation for ML/NLP projects.

---

## 🚀 Features

- Local SQLite database (`problemhunt.db`)
- 2540+ LeetCode problem statements
- Cleanly indexed titles and URLs
- Ready for NLP tasks like:
  - semantic search  
  - embeddings  
  - clustering  
  - tagging  
  - difficulty prediction
- Easy integration with Python applications or web backends

---

## 📁 Folder Structure

```text
project-root/
│
├── problemhunt.db              # Generated SQLite database
│
├── db.py                       # Python script to populate the database
│
├── Qdata/
│   ├── index.txt               # All problem titles (one per line)
│   ├── Qindex.txt              # All problem URLs (one per line)
│   │
│   ├── 1/
│   │   └── Problem_1.txt       # Full problem description
│   ├── 2/
│   │   └── Problem_2.txt
│   ├── 3/
│   │   └── Problem_3.txt
│   │
│   └── ...                     # Continues up to folder 2540
│
└── 2540/
    └── Problem_2540.txt        # Last problem description
Each folder 1/, 2/, …, 2540/ contains exactly one .txt file holding the full problem description.

Python Script (db.py)
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

index_path   = os.path.join(BASE_DIR, "Qdata", "index.txt")
q_index_path = os.path.join(BASE_DIR, "Qdata", "Qindex.txt")
qdata_dir    = os.path.join(BASE_DIR, "Qdata")

# Create / connect to DB
conn = sqlite3.connect(os.path.join(BASE_DIR, "problemhunt.db"))
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
""")

# Load titles + links
with open(index_path, encoding="utf-8") as f:
    titles = [line.strip() for line in f]

with open(q_index_path, encoding="utf-8") as f:
    links = [line.strip() for line in f]

insert_sql = "INSERT INTO problems (title, url, description) VALUES (?, ?, ?)"

# Walk through data directories (1 → 2540)
for n in range(1, 2541):
    folder = os.path.join(qdata_dir, str(n))

    # Expect exactly one text file
    files = [name for name in os.listdir(folder) if name.endswith(".txt")]
    if len(files) != 1:
        raise RuntimeError(f"Expected 1 text file in {folder}, found {files}")

    txt_path = os.path.join(folder, files[0])

    with open(txt_path, encoding="utf-8") as f:
        desc = f.read()

    idx = n - 1
    cur.execute(insert_sql, (titles[idx], links[idx], desc))

# Sanity check
cur.execute("SELECT COUNT(*) FROM problems")
print("Rows in problems:", cur.fetchone()[0])

conn.commit()
cur.close()
conn.close()
