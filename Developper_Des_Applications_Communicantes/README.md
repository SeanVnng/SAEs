# 📱 WhatsApp SAE - Plateforme de Communication Temps Réel

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![KivyMD](https://img.shields.io/badge/GUI-KivyMD-2980B9?style=for-the-badge&logo=kivy&logoColor=white)
![Network](https://img.shields.io/badge/Network-TCP%2FUDP-E67E22?style=for-the-badge)
![Database](https://img.shields.io/badge/Data-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production--Ready-2EA44F?style=for-the-badge)

**WhatsApp SAE** est une solution complète de messagerie instantanée et de visioconférence développée en Python. Elle repose sur une architecture **Client-Serveur hybride** innovante, utilisant simultanément le protocole TCP pour la fiabilité des échanges textuels et UDP pour la performance du streaming vidéo.

Conçu dans le cadre d'une Situation d'Apprentissage et d'Évaluation (SAE), ce projet démontre la mise en œuvre de concepts réseaux avancés couplés à une interface graphique moderne Material Design.

---

## 📑 Table des Matières

1.  [🌟 Fonctionnalités](#-fonctionnalités)
2.  [⚙️ Architecture Technique](#️-architecture-technique)
3.  [💻 Prérequis & Installation](#-prérequis--installation)
4.  [🚀 Démarrage Rapide (Local)](#-démarrage-rapide-local)
5.  [🌐 Guide de Déploiement VPS](#-guide-de-déploiement-vps)
6.  [📂 Structure du Projet](#-structure-du-projet)
7.  [🔧 Dépannage (FAQ)](#-dépannage-faq)
8.  [👥 Auteurs & Licence](#-auteurs--licence)

---

## 🌟 Fonctionnalités

### 🔐 Sécurité & Authentification
* **Système d'inscription/connexion** complet.
* **Hachage sécurisé** des mots de passe (SHA-256) avant stockage.
* **Persistance des données** via SQLite (Utilisateurs, Historique, Logs).
* **Compte Administrateur** pré-configuré (`admin` / `admin`).

### 💬 Messagerie Avancée
* **Chat temps réel** (Socket TCP) avec accusés de réception implicites.
* **Historique synchronisé :** Retrouvez vos messages même après redémarrage.
* **Groupes de discussion :** Support jusqu'à 50 participants simultanés.
* **Recherche par numéro :** Ajout de contacts via identifiant téléphonique unique.
* **Partage de Fichiers :** Envoi d'images (`.png`, `.jpg`), PDF et fichiers divers encodés en Base64.

### 🎥 Appels Vidéo & Audio (VoIP)
* **Streaming Vidéo Low-Latency :** Utilisation d'UDP pour minimiser la latence.
* **Interface "Split View" :** Affichage simultané de la caméra locale (miroir) et distante.
* **Audio Bidirectionnel :** Capture et lecture via `PyAudio`.
* **Contrôles Dynamiques :** Activation/Désactivation micro et caméra à la volée.

---

## ⚙️ Architecture Technique

Le projet utilise une architecture hybride pour optimiser les performances :

| Composant | Technologie / Protocole | Rôle |
| :--- | :--- | :--- |
| **Serveur Central** | `threading`, `socket` | Gère les connexions concurrentes, route les messages et stocke les fichiers. |
| **Canal de Contrôle** | **TCP (Port 5000)** | Assure l'intégrité des données critiques (Login, Texte, Fichiers, Création de groupes). |
| **Canal de Streaming** | **UDP (Port 9999)** | Permet un flux vidéo rapide (tolérance aux pertes de paquets) sans bloquer le chat. |
| **Interface Client** | `KivyMD` | Framework UI réactif et cross-platform (Windows, Linux, MacOS). |
| **Traitement Image** | `OpenCV`, `NumPy` | Capture webcam, compression JPEG frame-by-frame et décodage. |

---

## 💻 Prérequis & Installation

### Environnement
* **OS :** Windows 10/11, macOS ou Linux (Ubuntu 22.04 recommandé pour le serveur).
* **Python :** Version 3.8 ou supérieure.

### Installation des dépendances

1.  **Cloner le dépôt :**
    ```bash
    git clone [https://github.com/votre-username/whatsapp-sae.git](https://github.com/votre-username/whatsapp-sae.git)
    cd whatsapp-sae
    ```

2.  **Installer les bibliothèques Python :**
    ```bash
    pip install kivy kivymd opencv-python pyaudio numpy
    ```

    > **⚠️ Note pour les utilisateurs Linux :**
    > L'installation de `pyaudio` nécessite des paquets système préalables :
    > ```bash
    > sudo apt update
    > sudo apt install python3-pip portaudio19-dev python3-pyaudio
    > ```

---

## 🚀 Démarrage Rapide (Local)

Pour tester l'application sur une seule machine :

1.  **Lancer le Serveur :**
    Il doit toujours être démarré en premier. Il initialisera la base de données `whatsapp.db`.
    ```bash
    python server.py
    ```
    *Sortie attendue : `Serveur TCP démarré sur 0.0.0.0:5000`*

2.  **Configurer le Client :**
    Ouvrez `client.py` et vérifiez la variable `SERVER_IP` (ligne ~40) :
    ```python
    SERVER_IP = "127.0.0.1"
    ```

3.  **Lancer le Client :**
    Ouvrez deux terminaux séparés et lancez deux instances :
    ```bash
    python client.py
    ```
    *Connectez-vous avec deux comptes différents pour tester le chat et les appels.*

---

## 🌐 Guide de Déploiement VPS

Pour rendre l'application accessible via 4G ou depuis n'importe où, hébergez le serveur sur un VPS (IONOS, OVH, AWS).

### 1. Préparation du Serveur (Ubuntu)
Connectez-vous en SSH et mettez à jour le système :
```bash
ssh root@IP_DU_VPS
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip screen -y