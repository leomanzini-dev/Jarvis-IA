from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import sqlite3
import bcrypt
from dotenv import load_dotenv
import json
import datetime

# Importa a classe correta do cérebro
from jarvis_brain import JarvisBrain

# --- Configurações Iniciais ---
load_dotenv()
app = Flask(__name__)
# ADICIONE ESTA LINHA para corrigir a codificação de caracteres
app.config['JSON_AS_ASCII'] = False
app.secret_key = os.urandom(24)

# --- Gestão de Sessões Cerebrais ---
user_brains = {}

# --- Configuração do Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para aceder a esta página."

class User(UserMixin):
    def __init__(self, id, username, role='user'):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_db = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_db:
        return User(id=user_db['id'], username=user_db['username'], role=user_db['role'])
    return None

def get_db_connection():
    conn = sqlite3.connect('jarvis.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user_db = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user_db and bcrypt.checkpw(password.encode('utf-8'), user_db['password']):
            user = User(id=user_db['id'], username=user_db['username'], role=user_db['role'])
            login_user(user)
            
            # Instancia a classe correta
            user_brains[current_user.id] = JarvisBrain(current_user.id)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect_url': url_for('index')})
            
            return redirect(url_for('index'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Nome de utilizador ou palavra-passe incorretos.'})

            flash('Nome de utilizador ou palavra-passe incorretos.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    if current_user.id in user_brains:
        del user_brains[current_user.id]
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    is_admin = current_user.role == 'admin'
    return render_template('index.html', username=current_user.username, is_admin=is_admin)

@app.route("/ask", methods=["POST"])
@login_required
def ask():
    user_message = request.json.get("message")
    
    brain = user_brains.get(current_user.id)
    if not brain:
        # Instancia a classe correta
        brain = JarvisBrain(current_user.id)
        user_brains[current_user.id] = brain
    
    try:
        response_text = brain.get_response(user_message)
        response_data = {
            'text': response_text,
            'timestamp': datetime.datetime.now().strftime("%H:%M")
        }
        return jsonify(response_data)
    except Exception as e:
        print(f"Erro no processamento: {e}")
        return jsonify({"text": "Desculpe, ocorreu um erro interno. Tente novamente."}), 500

@app.route("/get_shortcuts", methods=["GET"])
@login_required
def get_shortcuts():
    conn = get_db_connection()
    shortcuts_db = conn.execute('SELECT id, text FROM shortcuts WHERE user_id = ? ORDER BY id DESC', (current_user.id,)).fetchall()
    conn.close()
    shortcuts = [{"id": row["id"], "text": row["text"]} for row in shortcuts_db]
    return jsonify({"shortcuts": shortcuts})

@app.route("/add_shortcut", methods=["POST"])
@login_required
def add_shortcut():
    text = request.json.get("text")
    if not text:
        return jsonify({"success": False, "error": "Texto do atalho não pode ser vazio."}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO shortcuts (user_id, text) VALUES (?, ?)', (current_user.id, text))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Atalho adicionado!", "id": new_id, "text": text})

@app.route("/delete_shortcut", methods=["POST"])
@login_required
def delete_shortcut():
    shortcut_id = request.json.get("id")
    if not shortcut_id:
        return jsonify({"success": False, "error": "ID do atalho não fornecido."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM shortcuts WHERE id = ? AND user_id = ?', (shortcut_id, current_user.id))
    conn.commit()
    conn.close()

    if cursor.rowcount > 0:
        return jsonify({"success": True, "message": "Atalho removido."})
    else:
        return jsonify({"success": False, "error": "Atalho não encontrado."}), 404

@app.route("/feedback", methods=["POST"])
@login_required
def feedback():
    data = request.json
    user_query = data.get('user_query')
    bot_response = data.get('bot_response')
    rating = data.get('rating')
    correction = data.get('correction')
    if not user_query or not bot_response or rating is None:
        return jsonify({"success": False, "error": "Dados de feedback incompletos."}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO feedback (user_id, user_query, bot_response, rating, correction) VALUES (?, ?, ?, ?, ?)',
            (current_user.id, user_query, bot_response, rating, correction)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Obrigado pelo seu feedback!"})
    except Exception as e:
        print(f"Erro ao guardar feedback: {e}")
        return jsonify({"success": False, "error": "Erro interno ao guardar feedback."}), 500

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Acesso negado. Você precisa ser um administrador.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("admin.html")

@app.route("/api/knowledge/<key>", methods=['GET', 'POST'])
@login_required
@admin_required
def handle_knowledge(key):
    conn = get_db_connection()
    if request.method == 'GET':
        row = conn.execute('SELECT content FROM knowledge_base WHERE key = ?', (key,)).fetchone()
        conn.close()
        return jsonify(json.loads(row['content'])) if row else (jsonify({"error": "Chave não encontrada"}), 404)
    if request.method == 'POST':
        try:
            new_content = request.json
            cursor = conn.cursor()
            cursor.execute("SELECT key FROM knowledge_base WHERE key = ?", (key,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO knowledge_base (key, content) VALUES (?, ?)", (key, json.dumps(new_content, indent=4, ensure_ascii=False)))
            else:
                cursor.execute('UPDATE knowledge_base SET content = ? WHERE key = ?', (json.dumps(new_content, indent=4, ensure_ascii=False), key))
            conn.commit()
            conn.close()
            user_brains.clear()
            return jsonify({"message": f"'{key}' atualizado com sucesso!"})
        except Exception as e:
            conn.close()
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists('jarvis.db'):
        print("AVISO: Banco de dados não encontrado. Execute init_db.py primeiro.")
    app.run(host='0.0.0.0', port=5000, debug=True)