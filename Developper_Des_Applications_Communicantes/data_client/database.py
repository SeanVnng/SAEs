import sqlite3
import hashlib
import json

DB_NAME = "Pytalk.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. TABLE UTILISATEURS (Avec les nouveaux champs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            phone_number TEXT DEFAULT '',
            infos TEXT DEFAULT 'Salut, j''utilise PyTalk !',
            profile_pic_path TEXT DEFAULT 'default_avatar'
        )
    ''')

    # 2. TABLE AMIS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER,
            friend_id INTEGER,
            PRIMARY KEY (user_id, friend_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id)
        )
    ''')

    # 3. TABLE MESSAGES (Avec Polls, Reply et Réactions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER, 
            group_id INTEGER,
            content TEXT,
            msg_type TEXT DEFAULT 'text', 
            file_path TEXT,
            reply_to_id INTEGER,
            poll_data TEXT,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id),
            FOREIGN KEY(reply_to_id) REFERENCES messages(id)
        )
    ''')

    # 4. TABLE GROUPES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            members TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

    # CRÉATION DE L'ADMIN APRÈS LA CRÉATION DES TABLES
    if not get_user_id("admin"):
        # On utilise la nouvelle signature avec 6 arguments
        create_user("admin", "admin", "Admin", "System", "admin@pytalk.com", "0000000000")
        update_user_profile("admin", "Administrateur Système", "0000000000", "admin@pytalk.com")

# --- UTILISATEURS ---
def create_user(username, password, first_name, last_name, email, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, first_name, last_name, email, phone_number) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hash_password(password), first_name, last_name, email, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally: conn.close()

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
    try:
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        res = cursor.fetchone()
        return res['id'] if res else None
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()

def get_username_by_phone(phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE phone_number = ?', (phone,))
    res = cursor.fetchone()
    conn.close()
    return res['username'] if res else None

def get_user_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, infos, phone_number, email, profile_pic_path FROM users WHERE username = ?', (username,))
    res = cursor.fetchone()
    conn.close()
    return dict(res) if res else None

def update_user_profile(username, new_infos, new_phone, new_email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if new_phone and len(new_phone) > 0:
        cursor.execute('SELECT username FROM users WHERE phone_number = ? AND username != ?', (new_phone, username))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            return False, "Ce numéro est déjà associé à un autre compte."

    try:
        cursor.execute('''
            UPDATE users SET infos = ?, phone_number = ?, email = ? 
            WHERE username = ?
        ''', (new_infos, new_phone, new_email, username))
        conn.commit()
        conn.close()
        return True, "Profil mis à jour avec succès."
    except Exception as e:
        conn.close()
        return False, f"Erreur base de données: {e}"

def update_profile_pic(username, filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET profile_pic_path = ? WHERE username = ?', (filename, username))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- AMIS ---
def add_friend_by_phone(my_username, target_phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE phone_number = ?', (target_phone,))
    friend = cursor.fetchone()
    
    if not friend:
        conn.close()
        return False, "Numéro introuvable"
        
    if friend['username'] == my_username:
        conn.close()
        return False, "Impossible de s'ajouter soi-même"

    my_id = get_user_id(my_username)
    friend_id = friend['id']
    
    try:
        cursor.execute('INSERT INTO friends (user_id, friend_id) VALUES (?, ?)', (my_id, friend_id))
        conn.commit()
        conn.close()
        return True, friend['username']
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Déjà dans vos amis"

def add_friend_by_username(my_username, target_username):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    my_id = get_user_id(my_username)
    friend_id = get_user_id(target_username)
    
    if not friend_id:
        conn.close()
        return False, "Utilisateur introuvable"

    try:
        cursor.execute('INSERT INTO friends (user_id, friend_id) VALUES (?, ?)', (my_id, friend_id))
        conn.commit()
        conn.close()
        return True, target_username
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Déjà ami"

def get_my_friends(username):
    user_id = get_user_id(username)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT u.username FROM friends f JOIN users u ON f.friend_id = u.id WHERE f.user_id = ?'
    cursor.execute(query, (user_id,))
    res = cursor.fetchall()
    conn.close()
    return [r['username'] for r in res]

# --- MESSAGES & GROUPES & RÉACTIONS ---
def create_group(name, admin_name, members_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    admin_id = get_user_id(admin_name)
    members_json = json.dumps(members_list)
    cursor.execute('INSERT INTO groups (name, admin_id, members) VALUES (?, ?, ?)', (name, admin_id, members_json))
    conn.commit()
    conn.close()

def get_group_members(group_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT members FROM groups WHERE name = ?', (group_name,))
    res = cursor.fetchone()
    conn.close()
    return json.loads(res['members']) if res else []

def save_message(sender_user, receiver_user, content, msg_type='text', file_path=None, group_name=None, reply_to_id=None, poll_data=None):
    sender_id = get_user_id(sender_user)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if group_name:
        cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
        grp = cursor.fetchone()
        if grp:
            cursor.execute('''
                INSERT INTO messages (sender_id, group_id, content, msg_type, file_path, reply_to_id, poll_data) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sender_id, grp['id'], content, msg_type, file_path, reply_to_id, poll_data))
    else:
        receiver_id = get_user_id(receiver_user)
        if sender_id and receiver_id:
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, content, msg_type, file_path, reply_to_id, poll_data) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sender_id, receiver_id, content, msg_type, file_path, reply_to_id, poll_data))
            
    conn.commit()
    conn.close()
    return True

def update_message_reaction(message_id, reaction_type, action="add"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # On détermine si on fait +1 ou -1
    value = 1 if action == "add" else -1
    
    if reaction_type == "like":
        cursor.execute('UPDATE messages SET likes = likes + ? WHERE id = ?', (value, message_id))
    elif reaction_type == "dislike":
        cursor.execute('UPDATE messages SET dislikes = dislikes + ? WHERE id = ?', (value, message_id))
        
    conn.commit()
    conn.close()

def get_conversation_history(user1, target):
    id1 = get_user_id(user1)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérification si c'est un groupe
    cursor.execute('SELECT id FROM groups WHERE name = ?', (target,))
    grp = cursor.fetchone()
    
    # Requête de base pour récupérer les messages ET les infos de réponse (jointure)
    base_query = '''
        SELECT 
            m.id, 
            u.username AS sender, 
            m.content, 
            m.msg_type, 
            m.file_path, 
            m.timestamp,
            m.likes,
            m.dislikes,
            m.poll_data,
            m_reply.content AS reply_content
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        LEFT JOIN messages m_reply ON m.reply_to_id = m_reply.id
    '''

    if grp:
        query = base_query + ' WHERE m.group_id = ? ORDER BY m.timestamp ASC'
        cursor.execute(query, (grp['id'],))
    else:
        id2 = get_user_id(target)
        if not id2: conn.close(); return []
        query = base_query + ''' 
            WHERE (m.sender_id = ? AND m.receiver_id = ?) 
               OR (m.sender_id = ? AND m.receiver_id = ?) 
            ORDER BY m.timestamp ASC
        '''
        cursor.execute(query, (id1, id2, id2, id1))
        
    messages = cursor.fetchall()
    conn.close()
    
    history = []
    for msg in messages:
        # On tente de charger les options de sondage si c'est un POLL
        poll_opts = []
        if msg['msg_type'] == 'poll' and msg['poll_data']:
            try:
                p_data = json.loads(msg['poll_data'])
                poll_opts = p_data.get("options", [])
            except: pass

        history.append({
            "id": msg['id'],
            "sender": msg['sender'], 
            "content": msg['content'], 
            "msg_type": msg['msg_type'],
            "file_path": msg['file_path'],
            "timestamp": msg['timestamp'],
            "likes": msg['likes'],
            "dislikes": msg['dislikes'],
            "reply_content": msg['reply_content'] if msg['reply_content'] else "",
            "poll_options": poll_opts
        })
    return history

def get_user_conversations_rich(username):
    user_id = get_user_id(username)
    if not user_id: return []
    conn = get_db_connection()
    cursor = conn.cursor()
    
    partners = set()
    
    # 1. On récupère les personnes avec qui on a parlé (envoyé ou reçu)
    cursor.execute('''
        SELECT DISTINCT u.username FROM messages m
        JOIN users u ON (m.sender_id = u.id OR m.receiver_id = u.id)
        WHERE (m.sender_id = ? OR m.receiver_id = ?) AND u.id != ?
    ''', (user_id, user_id, user_id))
    for row in cursor.fetchall(): partners.add(row['username'])
    
    # 2. On ajoute les groupes où l'on est membre
    cursor.execute('SELECT name, members, id FROM groups')
    groups = cursor.fetchall()
    for grp in groups:
        try:
            members = json.loads(grp['members'])
            if username in members: partners.add(grp['name'])
        except: pass
            
    data = []
    for p in partners:
        is_group = False
        grp_id = None
        # On vérifie si c'est un groupe
        for g in groups:
            if g['name'] == p: is_group = True; grp_id = g['id']; break
        
        last_msg = "Nouvelle discussion"
        unread = 0
        ts = "1970-01-01 00:00:00" # Date par défaut pour éviter les bugs de tri
        
        if is_group:
            cursor.execute('SELECT content, timestamp, msg_type FROM messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT 1', (grp_id,))
            lm = cursor.fetchone()
            if lm: 
                # Si c'est une image/fichier, on affiche le type au lieu du contenu vide
                last_msg = lm['content'] if lm['msg_type'] == 'text' else f"[{lm['msg_type']}]"
                ts = lm['timestamp'] if lm['timestamp'] else ts
        else:
            p_id = get_user_id(p)
            # Récupère le dernier message échangé avec cette personne
            cursor.execute('''
                SELECT content, timestamp, msg_type FROM messages 
                WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) 
                ORDER BY timestamp DESC LIMIT 1
            ''', (user_id, p_id, p_id, user_id))
            lm = cursor.fetchone()
            if lm: 
                last_msg = lm['content'] if lm['msg_type'] == 'text' else f"[{lm['msg_type']}]"
                ts = lm['timestamp'] if lm['timestamp'] else ts
            
            # Compte les messages non lus
            cursor.execute('''SELECT COUNT(*) FROM messages WHERE sender_id = ? AND receiver_id = ? AND is_read = 0''', (p_id, user_id))
            unread = cursor.fetchone()[0]

        data.append({"username": p, "last_msg": last_msg, "unread_count": unread, "timestamp": ts})
    
    conn.close()
    # Tri par date décroissante (le plus récent en haut)
    try:
        data.sort(key=lambda x: x['timestamp'], reverse=True)
    except: pass # Si jamais une date bug, on ne plante pas l'app
    
    return data

def mark_as_read(user, partner):
    user_id = get_user_id(user)
    p_id = get_user_id(partner)
    if not user_id or not p_id: return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE messages SET is_read = 1 WHERE sender_id = ? AND receiver_id = ?', (p_id, user_id))
    conn.commit()
    conn.close()

def remove_user_from_group(group_name, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, members FROM groups WHERE name = ?', (group_name,))
    grp = cursor.fetchone()
    if not grp: conn.close(); return False
    members = json.loads(grp['members'])
    if username in members:
        members.remove(username)
        cursor.execute('UPDATE groups SET members = ? WHERE id = ?', (json.dumps(members), grp['id']))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def delete_conversation_history(username, target):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = get_user_id(username)
    cursor.execute('SELECT id FROM groups WHERE name = ?', (target,))
    grp = cursor.fetchone()
    if grp:
        conn.close()
        return False
    target_id = get_user_id(target)
    if not user_id or not target_id:
        conn.close()
        return False
    cursor.execute('DELETE FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)', (user_id, target_id, target_id, user_id))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    create_tables()

