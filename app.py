from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Initialize databases
def init_db():
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    
    # Drop existing tables (for development purposes)
    cursor.execute('DROP TABLE IF EXISTS replies')
    cursor.execute('DROP TABLE IF EXISTS comments')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    # Comments table (with user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Replies table (with user_name)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            comment_id INTEGER,
            user_name TEXT NOT NULL,
            FOREIGN KEY (comment_id) REFERENCES comments (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/discuss')
def discuss():
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    
    # Fetch comments with associated user names
    cursor.execute('SELECT comments.id, comments.content, users.name FROM comments JOIN users ON comments.user_id = users.id')
    comments = cursor.fetchall()
    
    # Fetch replies and organize as before
    cursor.execute('SELECT * FROM replies')
    replies = cursor.fetchall()
    conn.close()

    reply_dict = {}
    for reply in replies:
        if reply[2] not in reply_dict:
            reply_dict[reply[2]] = []
        reply_dict[reply[2]].append(reply)

    return render_template('index.html', comments=comments, reply_dict=reply_dict)

@app.route('/comment', methods=['POST'])
def comment():
    name = request.form['name']
    content = request.form['content']
    
    # Insert user and comment
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
    user_id = cursor.lastrowid  # Get the newly created user ID
    cursor.execute('INSERT INTO comments (content, user_id) VALUES (?, ?)', (content, user_id))
    
    conn.commit()
    conn.close()
    return redirect('/discuss')

@app.route('/reply/<int:comment_id>', methods=['POST'])
def reply(comment_id):
    content = request.form['content']
    user_name = request.form['user_name']  # Get the user's name from the form
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO replies (content, comment_id, user_name) VALUES (?, ?, ?)', (content, comment_id, user_name))
    conn.commit()
    conn.close()
    return redirect('/discuss')

if __name__ == '__main__':
    app.run(debug=True)