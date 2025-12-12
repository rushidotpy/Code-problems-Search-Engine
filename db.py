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




