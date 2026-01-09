import sqlite3
import hashlib
import json

DB_NAME = "whatsapp.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            infos TEXT DEFAULT 'Salut, j''utilise WhatsApp SAE',
            phone_number TEXT DEFAULT '',
            profile_pic_path TEXT DEFAULT 'default_avatar'
        )
    ''')

    # Table Messages (Ajout de msg_type et file_path)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER, 
            group_id INTEGER,
            content TEXT,
            msg_type TEXT DEFAULT 'text', 
            file_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')

    # Table Groupes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            members TEXT NOT NULL -- Stocké en JSON
        )
    ''')
    
    # MIGRATION : Vérifier si la colonne msg_type existe, sinon l'ajouter (pour ne pas supprimer ta bdd actuelle)
    try:
        cursor.execute("SELECT msg_type FROM messages LIMIT 1")
    except sqlite3.OperationalError:
        print("Migration : Ajout des colonnes msg_type et file_path...")
        cursor.execute("ALTER TABLE messages ADD COLUMN msg_type TEXT DEFAULT 'text'")
        cursor.execute("ALTER TABLE messages ADD COLUMN file_path TEXT")
        cursor.execute("ALTER TABLE messages ADD COLUMN group_id INTEGER")
    
    conn.commit()
    conn.close()

    # --- CRÉATION AUTOMATIQUE ADMIN ---
    if not get_user_id("admin"):
        print("Création du compte admin par défaut...")
        create_user("admin", "admin") # <--- MOT DE PASSE ADMIN ICI
        update_user_profile("admin", "Administrateur Système", "0000000000")

# --- GESTION UTILISATEURS ---
def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pwd_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user['password_hash'] == hash_password(password):
        return True
    return False

def get_user_id(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def get_username_by_phone(phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE phone_number = ?', (phone,))
    result = cursor.fetchone()
    conn.close()
    return result['username'] if result else None

def get_all_usernames():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users')
    users = cursor.fetchall()
    conn.close()
    return [u['username'] for u in users]

# --- PROFIL ---
def get_user_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, infos, phone_number, profile_pic_path FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def update_user_profile(username, new_infos, new_phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET infos = ?, phone_number = ? WHERE username = ?', (new_infos, new_phone, username))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def update_profile_pic(username, filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET profile_pic_path = ? WHERE username = ?', (filename, username))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- MESSAGES & GROUPES ---
def create_group(name, admin_name, members_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    admin_id = get_user_id(admin_name)
    members_json = json.dumps(members_list)
    cursor.execute('INSERT INTO groups (name, admin_id, members) VALUES (?, ?, ?)', (name, admin_id, members_json))
    conn.commit()
    group_id = cursor.lastrowid
    conn.close()
    return group_id

def get_group_members(group_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT members FROM groups WHERE name = ?', (group_name,))
    res = cursor.fetchone()
    conn.close()
    return json.loads(res['members']) if res else []

def save_message(sender_user, receiver_user, content, msg_type='text', file_path=None, group_name=None):
    sender_id = get_user_id(sender_user)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if group_name:
        cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
        grp = cursor.fetchone()
        if grp:
            cursor.execute('''
                INSERT INTO messages (sender_id, group_id, content, msg_type, file_path) 
                VALUES (?, ?, ?, ?, ?)''', (sender_id, grp['id'], content, msg_type, file_path))
    else:
        receiver_id = get_user_id(receiver_user)
        if sender_id and receiver_id:
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, content, msg_type, file_path) 
                VALUES (?, ?, ?, ?, ?)''', (sender_id, receiver_id, content, msg_type, file_path))
            
    conn.commit()
    conn.close()
    return True

def get_conversation_history(user1, target):
    # Target peut être un user ou un groupe
    id1 = get_user_id(user1)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier si target est un groupe
    cursor.execute('SELECT id FROM groups WHERE name = ?', (target,))
    grp = cursor.fetchone()
    
    history = []
    
    if grp:
        # Historique Groupe
        query = '''
            SELECT u.username AS sender, m.content, m.msg_type, m.file_path, m.timestamp
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.group_id = ?
            ORDER BY m.timestamp ASC
        '''
        cursor.execute(query, (grp['id'],))
    else:
        # Historique Privé
        id2 = get_user_id(target)
        if not id2: 
            conn.close()
            return []
            
        query = '''
            SELECT u.username AS sender, m.content, m.msg_type, m.file_path, m.timestamp
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?)
               OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.timestamp ASC
        '''
        cursor.execute(query, (id1, id2, id2, id1))
        
    messages = cursor.fetchall()
    conn.close()
    
    for msg in messages:
        history.append({
            "sender": msg['sender'], 
            "content": msg['content'], 
            "type": msg['msg_type'],
            "file_path": msg['file_path'],
            "timestamp": msg['timestamp']
        })
    return history

def get_user_conversations(username):
    user_id = get_user_id(username)
    if not user_id: return []

    conn = get_db_connection()
    cursor = conn.cursor()
    
    conversations = set()
    
    # 1. Conversations privées
    query_private = '''
        SELECT DISTINCT u.username
        FROM messages m
        JOIN users u ON (m.sender_id = u.id OR m.receiver_id = u.id)
        WHERE (m.sender_id = ? OR m.receiver_id = ?) AND u.id != ?
    '''
    cursor.execute(query_private, (user_id, user_id, user_id))
    for row in cursor.fetchall():
        conversations.add(row['username'])
        
    # 2. Groupes dont je suis membre (simple check texte json pour l'instant)
    cursor.execute('SELECT name, members FROM groups')
    groups = cursor.fetchall()
    for grp in groups:
        members = json.loads(grp['members'])
        if username in members:
            conversations.add(grp['name'])
            
    conn.close()
    return list(conversations)

if __name__ == "__main__":
    create_tables()