# 📱 PyTalk - Plateforme de Communication Temps Réel

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![KivyMD](https://img.shields.io/badge/GUI-KivyMD-2980B9?style=for-the-badge&logo=kivy&logoColor=white)
![Android](https://img.shields.io/badge/Mobile-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)
![Network](https://img.shields.io/badge/Network-TCP%2FUDP-E67E22?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production--Ready-2EA44F?style=for-the-badge)

**PyTalk** est une solution complète de messagerie instantanée et de visioconférence développée en Python. Elle repose sur une architecture **Client-Serveur hybride** innovante, utilisant simultanément le protocole TCP pour la fiabilité des échanges textuels et UDP pour la performance du streaming vidéo.

Conçu dans le cadre d'une Situation d'Apprentissage et d'Évaluation (SAE), ce projet démontre la mise en œuvre de concepts réseaux avancés couplés à une interface graphique moderne Material Design, compatible **Windows et Android**.

---

## 📑 Table des Matières

1.  [🌟 Fonctionnalités](#-fonctionnalités)
2.  [⚙️ Architecture Technique](#️-architecture-technique)
3.  [💻 Prérequis & Installation](#-prérequis--installation)
4.  [🚀 Démarrage Rapide (Local)](#-démarrage-rapide-local)
5.  [🌐 Guide de Déploiement VPS](#-guide-de-déploiement-vps)
6.  [📱 Compilation Android (APK)](#-compilation-android-apk)
7.  [📂 Structure du Projet](#-structure-du-projet)
8.  [🔧 Dépannage (FAQ)](#-dépannage-faq)
9.  [👥 Auteurs & Licence](#-auteurs--licence)

---

## 🌟 Fonctionnalités

### 🔐 Sécurité & Authentification
* **Système d'inscription/connexion** complet avec vérification en base de données.
* **Hachage sécurisé** des mots de passe (SHA-256).
* **Persistance des données** via SQLite (Utilisateurs, Historique, Logs).

### 💬 Messagerie Avancée
* **Chat temps réel** (Socket TCP) avec gestion des buffers pour les gros transferts.
* **Historique synchronisé :** Retrouvez vos messages même après redémarrage.
* **Groupes de discussion :** Support jusqu'à 50 participants simultanés.
* **Gestion d'Amis :** Ajout par numéro de téléphone unique (10 chiffres).
* **Partage Multimédia :** Envoi d'images (JPG, PNG) avec prévisualisation et cache local.
* **Confidentialité :** Option pour masquer une conversation (historique conservé) ou quitter un groupe.

### 🎥 Appels Vidéo & Audio (VoIP)
* **Streaming Vidéo Low-Latency :** Utilisation d'UDP pour minimiser la latence.
* **Compatibilité Mobile :** Utilisation de l'API Caméra native sur Android.
* **Interface "Split View" :** Affichage simultané de la caméra locale et distante.

---

## ⚙️ Architecture Technique

Le projet utilise une architecture hybride pour optimiser les performances :

| Composant | Technologie / Protocole | Rôle |
| :--- | :--- | :--- |
| **Serveur Central** | `threading`, `socket` | Gère les connexions concurrentes, route les messages et stocke les fichiers. |
| **Canal de Contrôle** | **TCP (Port 5000)** | Assure l'intégrité des données critiques (Login, Texte, Fichiers, Création de groupes). |
| **Canal de Streaming** | **UDP (Port 9999)** | Permet un flux vidéo rapide (tolérance aux pertes de paquets) sans bloquer le chat. |
| **Interface Client** | `KivyMD` | Framework UI réactif et cross-platform (Windows, Linux, Android). |
| **Traitement Image** | `Pillow`, `Plyer` | Gestion des assets, compression et accès matériel (Caméra/Stockage). |

---

## 💻 Prérequis & Installation

### Environnement
* **OS :** Windows 10/11, macOS ou Linux (Ubuntu 22.04 recommandé pour le serveur).
* **Python :** Version 3.8 à 3.11.

### Installation des dépendances

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/SeanVnng/SAEs/tree/main/Developper_Des_Applications_Communicantes
    cd PyTalk
    ```

2.  **Installer les bibliothèques Python :**
    ```bash
    pip install kivy kivymd opencv-python pyaudio numpy pillow plyer
    ```

---

## 🚀 Démarrage Rapide (Local)

Pour tester l'application sur une seule machine :

1.  **Lancer le Serveur :**
    Il doit toujours être démarré en premier. Il initialisera la base de données `whatsapp.db`.
    ```bash
    python server.py
    ```
    *Sortie attendue : `[DÉMARRAGE] Serveur en écoute sur 0.0.0.0:5000`*

2.  **Configurer le Client :**
    Ouvrez `client.py` et vérifiez la variable `SERVER_IP` (ligne ~40) :
    ```python
    SERVER_IP = "127.0.0.1" # Mettre l'IP locale ou Hamachi pour tester entre deux PC
    ```

3.  **Lancer le Client :**
    Ouvrez deux terminaux séparés et lancez deux instances :
    ```bash
    python client.py
    ```

---

## 🌐 Guide de Déploiement VPS

Pour rendre l'application accessible depuis n'importe où (4G/Internet), hébergez le serveur sur un VPS (Ubuntu).

1.  **Préparation du Serveur :**
    Connectez-vous en SSH et mettez à jour le système :
    ```bash
    ssh root@IP_DU_VPS
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3 python3-pip screen -y
    ```

2.  **Installation et Lancement :**
    ```bash
    # Cloner le projet (ou copier les fichiers server.py et database.py)
    git clone [https://github.com/votre-repo/sae.git](https://github.com/votre-repo/sae.git)
    cd sae

    # Lancer le serveur en tâche de fond avec Screen
    python3 server.py
    ```
    *Pour quitter le mode screen sans couper le serveur : `CTRL + A`, puis `D`.*

3.  **Côté Client :**
    Modifiez `SERVER_IP` dans `client.py` avec l'adresse IP publique de votre VPS.

---

## 📱 Compilation Android (APK)

L'application est optimisée pour être compilée en `.apk` via **Buildozer** (recommandé via Google Colab).

1.  **Préparer les fichiers :** Renommer `client.py` en `main.py` et inclure `buildozer.spec`.
2.  **Configurer `buildozer.spec` :**
    ```spec
    requirements = python3,kivy==2.2.0,kivymd==1.1.1,pillow,plyer,android
    android.permissions = INTERNET,CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
    ```
3.  **Compiler :**
    Utiliser la commande `!buildozer -v android debug` sur un environnement Linux.

---

## 📂 Structure du Projet

```text
PyTalk/
│
├── assets/              # Ressources graphiques (Logo, Avatar par défaut)
│   ├── default_avatar.png
│   ├── heart.png
│   └── ...
│
├── server_files/        # Stockage côté serveur (Images partagées, Uploads)
│   └── ...
│
├── client.py            # Code source de l'application (Interface & Logique)
├── server.py            # Code source du Serveur (Gestion Sockets + Threads)
├── database.py          # Gestion de la base de données SQLite (Requêtes)
├── whatsapp.db          # Fichier BDD (généré automatiquement au lancement)
├── buildozer.spec       # Configuration pour la compilation Android
└── README.md            # Documentation du projet



