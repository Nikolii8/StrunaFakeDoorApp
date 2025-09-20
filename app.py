from flask import Flask, jsonify, send_from_directory, request
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "counter.db"

# Създаваме базата и таблиците, ако не съществуват
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Таблица за брояча
    c.execute("CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, clicks INTEGER)")
    c.execute("SELECT * FROM counter WHERE id=1")
    if not c.fetchone():
        c.execute("INSERT INTO counter (id, clicks) VALUES (1, 0)")
    
    # Таблица за имейлите
    c.execute("""
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

# Вземаме текущия брой кликове
@app.route("/count", methods=["GET"])
def get_count():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT clicks FROM counter WHERE id=1")
    clicks = c.fetchone()[0]
    conn.close()
    return jsonify({"clicks": clicks})

# Натискане на бутона Buy now
@app.route("/click", methods=["POST"])
def add_click():
    # Увеличаваме брояча
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE counter SET clicks = clicks + 1 WHERE id=1")
    conn.commit()
    c.execute("SELECT clicks FROM counter WHERE id=1")
    clicks = c.fetchone()[0]
    conn.close()
    return jsonify({"clicks": clicks})

# Записване на имейл в waitlist
@app.route("/waitlist", methods=["POST"])
def add_email():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO waitlist (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# Сервиране на HTML и статични файлове
@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    return send_from_directory(os.getcwd(), path)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
