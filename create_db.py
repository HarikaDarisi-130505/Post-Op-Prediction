import sqlite3

conn = sqlite3.connect('patients.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    L_CORE INTEGER,
    L_SURF INTEGER,
    L_O2 INTEGER,
    L_BP INTEGER,
    SURF_STBL INTEGER,
    CORE_STBL INTEGER,
    BP_STBL INTEGER,
    COMFORT INTEGER,
    prediction TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("✅ Database and table created successfully!")
