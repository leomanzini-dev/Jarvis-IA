import sqlite3
import bcrypt
import json

print("Iniciando a criação/atualização do banco de dados do Jarvis...")

conn = sqlite3.connect('jarvis.db')
cursor = conn.cursor()

# --- Tabela de Utilizadores ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    )
''')
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
if cursor.fetchone() is None:
    hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('admin', hashed_password, 'admin'))
print("Tabela 'users' verificada.")

# --- Tabela da Base de Conhecimento ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        key TEXT PRIMARY KEY,
        content TEXT NOT NULL
    )
''')
print("Tabela 'knowledge_base' verificada.")

# --- Tabela de Atalhos ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS shortcuts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print("Tabela 'shortcuts' verificada.")

# --- Tabela de Histórico de Conversas ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print("Tabela 'conversation_history' verificada.")

# --- Tabela de Feedback ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_query TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        rating INTEGER NOT NULL,
        correction TEXT,
        embedding BLOB,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
print("Tabela 'feedback' verificada.")

# --- Migração de Dados do JSON (se necessário) ---
try:
    with open('knowledge_base.json', 'r', encoding='utf-8') as f:
        knowledge_data = json.load(f)
    for key, value in knowledge_data.items():
        cursor.execute("SELECT key FROM knowledge_base WHERE key = ?", (key,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO knowledge_base (key, content) VALUES (?, ?)", (key, json.dumps(value, indent=4, ensure_ascii=False)))
            print(f"Dados para '{key}' migrados do JSON.")
except FileNotFoundError:
    pass

conn.commit()
conn.close()

print("\nBanco de dados do Jarvis está pronto.")