from functools import wraps
from pathlib import Path
import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from core.chatbot import Chatbot

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'chatbot.db'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-me')
chatbot = Chatbot()


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.executescript(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT 'Nova conversa',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );
            '''
        )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Faça login para continuar.'}), 401
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped


def owned_conversation(db, conversation_id, user_id):
    return db.execute(
        'SELECT * FROM conversations WHERE id = ? AND user_id = ?',
        (conversation_id, user_id),
    ).fetchone()


@app.route('/')
@login_required
def home():
    return render_template('chat.html', user_name=session.get('user_name', 'Usuário'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect(url_for('home'))
        return render_template('login.html', mode='login')

    data = request.form
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    with get_db() as db:
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if not user or not check_password_hash(user['password_hash'], password):
        return render_template('login.html', mode='login', error='E-mail ou senha inválidos.'), 401

    session.clear()
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect(url_for('home'))
        return render_template('login.html', mode='register')

    data = request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if len(name) < 2 or '@' not in email or len(password) < 6:
        return render_template(
            'login.html',
            mode='register',
            error='Preencha os dados corretamente. A senha deve ter pelo menos 6 caracteres.',
        ), 400

    try:
        with get_db() as db:
            cursor = db.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password)),
            )
            db.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return render_template('login.html', mode='register', error='Este e-mail já está cadastrado.'), 409

    session.clear()
    session['user_id'] = user_id
    session['user_name'] = name
    return redirect(url_for('home'))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
        'database': str(DATABASE.name),
    })


@app.route('/api/conversations', methods=['GET', 'POST'])
@login_required
def conversations():
    user_id = session['user_id']

    with get_db() as db:
        if request.method == 'POST':
            cursor = db.execute(
                'INSERT INTO conversations (user_id, title) VALUES (?, ?)',
                (user_id, 'Nova conversa'),
            )
            db.commit()
            return jsonify({'id': cursor.lastrowid, 'title': 'Nova conversa'}), 201

        rows = db.execute(
            '''
            SELECT id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY updated_at DESC, id DESC
            ''',
            (user_id,),
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.route('/api/conversations/<int:conversation_id>', methods=['GET', 'DELETE'])
@login_required
def conversation_detail(conversation_id):
    user_id = session['user_id']

    with get_db() as db:
        conversation = owned_conversation(db, conversation_id, user_id)
        if not conversation:
            return jsonify({'error': 'Conversa não encontrada.'}), 404

        if request.method == 'DELETE':
            db.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
            db.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            db.commit()
            return jsonify({'status': 'deleted'})

        rows = db.execute(
            '''
            SELECT id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            ''',
            (conversation_id,),
        ).fetchall()

    return jsonify({
        'id': conversation['id'],
        'title': conversation['title'],
        'messages': [dict(row) for row in rows],
    })


@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    conversation_id = data.get('conversation_id')
    message = str(data.get('message') or '').strip()
    user_id = session['user_id']

    if not message:
        return jsonify({'error': 'Digite uma mensagem antes de enviar.'}), 400

    with get_db() as db:
        if not conversation_id:
            cursor = db.execute(
                'INSERT INTO conversations (user_id, title) VALUES (?, ?)',
                (user_id, message[:48]),
            )
            conversation_id = cursor.lastrowid
            db.commit()

        conversation = owned_conversation(db, conversation_id, user_id)
        if not conversation:
            return jsonify({'error': 'Conversa não encontrada.'}), 404

        history_rows = db.execute(
            '''
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT 16
            ''',
            (conversation_id,),
        ).fetchall()
        history = [dict(row) for row in reversed(history_rows)]

        response = chatbot.process_message(str(user_id), message, history)

        db.execute(
            'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
            (conversation_id, 'user', message),
        )
        db.execute(
            'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
            (conversation_id, 'assistant', response),
        )

        count = db.execute(
            'SELECT COUNT(*) AS total FROM messages WHERE conversation_id = ?',
            (conversation_id,),
        ).fetchone()['total']
        if count <= 2:
            db.execute(
                'UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (message[:48], conversation_id),
            )
        else:
            db.execute(
                'UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (conversation_id,),
            )
        db.commit()

    return jsonify({
        'conversation_id': conversation_id,
        'response': response,
    })


init_db()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
