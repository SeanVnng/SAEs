import socket
import threading
import json
import os
import base64
import database as db

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000
UDP_PORT = 9999
IMAGE_FOLDER = "server_images"
FILE_FOLDER = "server_files" # Nouveau dossier pour les PDFs, etc.

for folder in [IMAGE_FOLDER, FILE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

clients = {} 
udp_clients = {}
username_to_udp = {}

def send_to_user(target_username, data):
    if target_username in clients:
        try:
            clients[target_username].send(json.dumps(data).encode('utf-8'))
        except:
             print(f"Impossible d'envoyer à {target_username}")

def broadcast_to_group(group_name, sender, data):
    members = db.get_group_members(group_name)
    for member in members:
        if member != sender and member in clients:
            send_to_user(member, data)

def udp_server_loop():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", UDP_PORT))
    print(f"Serveur UDP démarré sur {UDP_PORT}")

    while True:
        try:
            data, addr = udp_sock.recvfrom(60000)
            try:
                msg = json.loads(data.decode('utf-8'))
                if msg.get("type") == "REGISTER_UDP":
                    user = msg.get("username")
                    udp_clients[addr] = user
                    username_to_udp[user] = addr
                    continue
            except: pass

            try:
                separator = b"|||"
                parts = data.split(separator, 1)
                if len(parts) == 2:
                    target_user_bytes, content = parts
                    target_user = target_user_bytes.decode('utf-8')
                    if target_user in username_to_udp:
                        udp_sock.sendto(content, username_to_udp[target_user])
            except: pass
        except: pass

def handle_client(client_socket, addr):
    print(f"Connexion TCP : {addr}")
    current_username = None

    while True:
        try:
            data = client_socket.recv(1024 * 1024 * 5) # Augmenter buffer pour les images
            if not data: break
            
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "LOGIN":
                    user = msg.get("username")
                    pwd = msg.get("password")
                    if db.verify_user(user, pwd):
                        current_username = user
                        clients[current_username] = client_socket
                        send_to_user(current_username, {"type": "LOGIN_REPLY", "success": True})
                    else:
                         send_to_user(current_username, {"type": "LOGIN_REPLY", "success": False})

                elif msg_type == "REGISTER":
                    user = msg.get("username")
                    pwd = msg.get("password")
                    success = db.create_user(user, pwd)
                    send_to_user(current_username, {"type": "REGISTER_REPLY", "success": success})

                elif not current_username: continue

                # --- FONCTIONNALITÉS AVANCÉES ---

                elif msg_type == "FIND_BY_PHONE":
                    target_user = db.get_username_by_phone(msg.get("phone"))
                    send_to_user(current_username, {"type": "FIND_PHONE_REPLY", "username": target_user})

                elif msg_type == "GET_TARGET_INFO":
                    target = msg.get("target")
                    info = db.get_user_profile(target)
                    send_to_user(current_username, {"type": "TARGET_INFO_REPLY", "data": info})

                elif msg_type == "CREATE_GROUP":
                    grp_name = msg.get("name")
                    members = msg.get("members")
                    if len(members) > 50:
                        send_to_user(current_username, {"type": "ERROR", "msg": "Trop de membres"})
                    else:
                        members.append(current_username) # Admin is member
                        db.create_group(grp_name, current_username, members)
                        send_to_user(current_username, {"type": "GROUP_CREATED", "name": grp_name})

                elif msg_type == "MESSAGE":
                    receiver = msg.get("receiver")
                    content = msg.get("content")
                    m_type = msg.get("msg_type", "text")
                    file_data = msg.get("file_data")
                    file_ext = msg.get("file_ext")
                    
                    file_path = None
                    if m_type in ["image", "file"] and file_data:
                        # Sauvegarder le fichier
                        filename = f"{datetime.now().timestamp()}_{current_username}.{file_ext}"
                        save_path = os.path.join(FILE_FOLDER, filename)
                        try:
                            with open(save_path, "wb") as f:
                                f.write(base64.b64decode(file_data))
                            file_path = filename
                        except: pass

                    # Sauvegarde DB
                    is_group = False
                    if db.get_group_members(receiver): # C'est un groupe
                        is_group = True
                        db.save_message(current_username, None, content, m_type, file_path, group_name=receiver)
                        # Broadcast
                        broadcast_data = {
                            "type": "NEW_MESSAGE", 
                            "sender": current_username, 
                            "content": content,
                            "msg_type": m_type,
                            "file_path": file_path,
                            "is_group": True,
                            "group_name": receiver
                        }
                        broadcast_to_group(receiver, current_username, broadcast_data)
                    else:
                        # Privé
                        db.save_message(current_username, receiver, content, m_type, file_path)
                        if receiver in clients:
                            send_to_user(receiver, {
                                "type": "NEW_MESSAGE", 
                                "sender": current_username, 
                                "content": content,
                                "msg_type": m_type,
                                "file_path": file_path
                            })

                # --- APPELS & LOGS ---
                elif msg_type == "CALL_REQUEST":
                    target = msg.get("target")
                    if target in clients:
                        send_to_user(target, {"type": "INCOMING_CALL", "sender": current_username, "media": msg.get("media")})

                elif msg_type == "CALL_RESPONSE":
                    send_to_user(msg.get("target"), {"type": "CALL_RESPONSE_REPLY", "responder": current_username, "response": msg.get("response")})

                elif msg_type == "END_CALL":
                    target = msg.get("target")
                    if target in clients:
                        send_to_user(target, {"type": "CALL_ENDED", "sender": current_username})

                # --- STANDARD ---
                elif msg_type == "GET_PROFILE":
                    send_to_user(current_username, {"type": "PROFILE_DATA", "data": db.get_user_profile(current_username)})
                elif msg_type == "UPDATE_PROFILE":
                    db.update_user_profile(current_username, msg.get("infos"), msg.get("phone"))
                elif msg_type == "HISTORY":
                    send_to_user(current_username, {"type": "HISTORY_REPLY", "target": msg.get("target"), "data": db.get_conversation_history(current_username, msg.get("target"))})
                elif msg_type == "GET_CONVERSATIONS":
                    send_to_user(current_username, {"type": "CONVERSATIONS_LIST", "data": db.get_user_conversations(current_username)})

            except json.JSONDecodeError: pass
        except: break

    if current_username and current_username in clients:
        del clients[current_username]
    client_socket.close()

from datetime import datetime
def start_server():
    db.create_tables()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f"Serveur TCP démarré sur {SERVER_IP}:{SERVER_PORT}")
    threading.Thread(target=udp_server_loop, daemon=True).start()
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    start_server()