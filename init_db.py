import sqlite3

conn = sqlite3.connect("aquafix.db")
cursor = conn.cursor()

# 1. CREATE TABLES
cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    lat REAL,
    lng REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    issue TEXT,
    description TEXT,
    lat REAL,
    lng REAL,
    assigned_team TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER,
    rating INTEGER,
    comment TEXT
)
""")

# 2. ADD SAMPLE TEAMS (👉 PUT YOUR CODE HERE)
cursor.execute("INSERT INTO teams (name, lat, lng) VALUES (?, ?, ?)",
               ("Team A", 17.3850, 78.4867))

cursor.execute("INSERT INTO teams (name, lat, lng) VALUES (?, ?, ?)",
               ("Team B", 17.4500, 78.3800))

cursor.execute("INSERT INTO teams (name, lat, lng) VALUES (?, ?, ?)",
               ("Team C", 17.5200, 78.3000))

# 3. SAVE & CLOSE
conn.commit()
conn.close()

print("Database initialized successfully")