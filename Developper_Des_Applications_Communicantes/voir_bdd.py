import sqlite3

# Nom du fichier de base de données
DB_NAME = "Pytalk.db"

def view_database():
    try:
        # Connexion à la base de données en lecture seule
        conn = sqlite3.connect(f"file:{DB_NAME}?mode=ro", uri=True)
        cursor = conn.cursor()

        print(f"--- CONTENU DE {DB_NAME} ---\n")

        # 1. Afficher la table USERS
        print("TABLE: users")
        # On sélectionne les nouvelles colonnes aussi
        cursor.execute("SELECT id, username, password_hash, infos, phone_number FROM users")
        users = cursor.fetchall()
        if users:
            print(f"{'ID':<5} | {'USERNAME':<15} | {'INFOS':<30} | {'PHONE':<15} | {'PASSWORD_HASH (Hashé)'}")
            print("-" * 90)
            for user in users:
                # On tronque le hash pour l'affichage si besoin, et les infos si trop longues
                id_u, name, pwd_hash, infos, phone = user
                infos_display = (infos[:27] + '...') if infos and len(infos) > 27 else infos
                print(f"{id_u:<5} | {name:<15} | {str(infos_display):<30} | {str(phone):<15} | {pwd_hash}")
        else:
            print("(Aucun utilisateur)")
        print("\n" + "="*90 + "\n")

        # 2. Afficher la table MESSAGES (Inchangé)
        print("TABLE: messages")
        query_messages = """
            SELECT 
                m.id, 
                u_sender.username AS sender, 
                u_receiver.username AS receiver, 
                m.content, 
                m.timestamp
            FROM messages m
            JOIN users u_sender ON m.sender_id = u_sender.id
            JOIN users u_receiver ON m.receiver_id = u_receiver.id
            ORDER BY m.timestamp DESC
        """
        cursor.execute(query_messages)
        messages = cursor.fetchall()
        if messages:
            print(f"{'ID':<5} | {'EXPÉDITEUR':<15} | {'DESTINATAIRE':<15} | {'DATE':<20} | {'CONTENU'}")
            print("-" * 90)
            for msg in messages:
                id_m, sender, receiver, timestamp, content = msg
                print(f"{id_m:<5} | {sender:<15} | {receiver:<15} | {timestamp:<20} | {content}")
        else:
            print("(Aucun message)")
        print("\n" + "-"*90 + "\n")

    except sqlite3.OperationalError:
        print(f"Erreur : Le fichier '{DB_NAME}' n'existe pas encore.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    view_database()
    input("Appuyez sur Entrée pour quitter...")

