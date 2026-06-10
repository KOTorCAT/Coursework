from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = '/app/data/tasks.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('/app/data', exist_ok=True)
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            datetime TEXT,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    conn = get_db()
    cur = conn.execute('SELECT id, title, description, priority, datetime, done FROM tasks ORDER BY id DESC')
    tasks = []
    for row in cur.fetchall():
        tasks.append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'] or '',
            'priority': row['priority'] or 'medium',
            'datetime': row['datetime'] or '',
            'done': bool(row['done'])
        })
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    title = data.get('title', '')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    datetime = data.get('datetime', '')
    done = 1 if data.get('done', False) else 0
    
    print(f"DEBUG: Saving task - title={title}, priority={priority}, datetime={datetime}")
    
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO tasks (title, description, priority, datetime, done) VALUES (?, ?, ?, ?, ?)',
        (title, description, priority, datetime, done)
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': new_id,
        'title': title,
        'description': description,
        'priority': priority,
        'datetime': datetime,
        'done': bool(done)
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    done = 1 if data.get('done', False) else 0
    
    conn = get_db()
    conn.execute('UPDATE tasks SET done = ? WHERE id = ?', (done, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'id': task_id, 'done': bool(done)})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)