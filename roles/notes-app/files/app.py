from flask import Flask, request, render_template_string, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Connect to sqlite
def get_db_connection():
    conn = sqlite3.connect('/opt/notes-app/notes.db')
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn

# Create table if not exists
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Notes App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        form {
            text-align: center;
        }
        textarea {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border-radius: 6px;
            border: 1px solid #ccc;
            resize: vertical;
        }
        input[type="submit"], .delete-btn {
            margin-top: 10px;
            padding: 8px 15px;
            font-size: 14px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
        }
        input[type="submit"] {
            background-color: #007bff;
            color: white;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .delete-btn {
            background-color: #dc3545;
            color: white;
        }
        .delete-btn:hover {
            background-color: #a71d2a;
        }
        .note {
            border-bottom: 1px solid #ddd;
            padding: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .note-content {
            flex-grow: 1;
        }
        .note time {
            color: #888;
            font-size: 14px;
        }
        .delete-form {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h2>📝 Write your note</h2>
    <form method="POST">
        <textarea name="note" rows="4" placeholder="Write your note here..."></textarea><br>
        <input type="submit" value="Save Note">
    </form>

    <hr>

    <h3>📚 Previous Notes</h3>
    {% for note in notes %}
        <div class="note">
            <div class="note-content">
                <time>🕒 {{note['timestamp']}}</time><br>
                📌 {{note['content']}}
            </div>
            <form method="POST" action="/delete/{{note['id']}}" style="display:inline;">
                <button type="submit" class="delete-btn">Delete</button>
            </form>
        </div>
    {% endfor %}
</body>
</html>
'''


@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        note = request.form["note"]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (note, timestamp))
        conn.commit()

    cursor.execute("SELECT * FROM notes ORDER BY timestamp DESC")
    notes = cursor.fetchall()
    conn.close()
    
    return render_template_string(HTML, notes=notes)


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


