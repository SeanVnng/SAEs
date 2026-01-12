import sqlite3

# Nom du fichier de base de données
DB_NAME = "Pytalk.db"

def view_database():
    try:
        # Connexion à la base de données en lecture seule (pour éviter les erreurs de manip)
        conn = sqlite3.connect(f"file:{DB_NAME}?mode=ro", uri=True)
        cursor = conn.cursor()

        print(f"\n{'='*30} CONTENU DE {DB_NAME} {'='*30}\n")

        # ---------------------------------------------------------
        # 1. Afficher la table USERS (Mise à jour avec les nouveaux champs)
        # ---------------------------------------------------------
        print(f"📂 TABLE: users")
        
        cursor.execute("SELECT id, username, first_name, last_name, email, phone_number, infos FROM users")
        users = cursor.fetchall()
        
        if users:
            # En-tête du tableau
            header = f"{'ID':<4} | {'PSEUDO':<12} | {'PRÉNOM':<10} | {'NOM':<10} | {'EMAIL':<25} | {'TÉL':<12} | {'BIO'}"
            print("-" * len(header))
            print(header)
            print("-" * len(header))

            for user in users:
                uid, uname, fname, lname, mail, phone, infos = user
                
                # Gestion des valeurs None (au cas où)
                fname = fname if fname else ""
                lname = lname if lname else ""
                mail = mail if mail else ""
                phone = phone if phone else ""
                
                # On coupe la bio si elle est trop longue pour l'affichage
                infos_display = (infos[:15] + '..') if infos and len(infos) > 15 else (infos if infos else "")

                print(f"{uid:<4} | {uname:<12} | {fname:<10} | {lname:<10} | {mail:<25} | {phone:<12} | {infos_display}")
        else:
            print("(Aucun utilisateur trouvé)")
        
        print("\n")

        # ---------------------------------------------------------
        # 2. Afficher la table MESSAGES (Avec les vrais pseudos)
        # ---------------------------------------------------------
        print(f"📨 TABLE: messages")
        
        query_messages = """
            SELECT 
                m.id, 
                u_sender.username AS sender, 
                u_receiver.username AS receiver, 
                m.group_id,
                m.content, 
                m.timestamp
            FROM messages m
            LEFT JOIN users u_sender ON m.sender_id = u_sender.id
            LEFT JOIN users u_receiver ON m.receiver_id = u_receiver.id
            ORDER BY m.timestamp DESC
        """
        cursor.execute(query_messages)
        messages = cursor.fetchall()
        
        if messages:
            header_msg = f"{'ID':<4} | {'DE':<12} | {'VERS':<12} | {'DATE':<19} | {'CONTENU'}"
            print("-" * len(header_msg))
            print(header_msg)
            print("-" * len(header_msg))

            for msg in messages:
                mid, sender, receiver, grp_id, content, timestamp = msg
                
                # Si receiver est None, c'est peut-être un message de groupe
                destinataire = receiver if receiver else (f"Groupe {grp_id}" if grp_id else "Inconnu")
                sender = sender if sender else "Système"
                
                print(f"{mid:<4} | {sender:<12} | {destinataire:<12} | {timestamp[:19]:<19} | {content}")
        else:
            print("(Aucun message)")

        print("\n" + "="*80 + "\n")

    except sqlite3.OperationalError:
        print(f"❌ Erreur : Le fichier '{DB_NAME}' n'existe pas ou est verrouillé.")
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    view_database()
    input("Appuyez sur Entrée pour quitter...")

