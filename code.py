import sqlite3

DB_PATH = "users.db"

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Drop the existing table (⚠ WARNING: This will delete all users)
cursor.execute("DROP TABLE IF EXISTS users")

# Recreate the table with the correct structure
cursor.execute('''
    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("✅ Database reset successfully.")
