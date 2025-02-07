import sqlite3

# Connect to SQLite database (creates if not exists)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

# Commit & close
conn.commit()
conn.close()

print("Database setup completed.")

