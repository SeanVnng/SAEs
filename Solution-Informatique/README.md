# 🌐 IPAM Solution - Gestion d'Adressage IP

![PHP](https://img.shields.io/badge/PHP-8.x-purple?style=for-the-badge&logo=php)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?style=for-the-badge&logo=postgresql)
![Apache](https://img.shields.io/badge/Server-Apache-red?style=for-the-badge&logo=apache)
![HTML5](https://img.shields.io/badge/Frontend-HTML5%20%2F%20CSS3-orange?style=for-the-badge&logo=html5)

**IPAM (IP Address Management)** est une application web complète développée dans le cadre de la **SAE 2.03** à l'IUT Sorbonne Nord. Elle permet aux entreprises de centraliser, planifier et gérer l'attribution des adresses IP, des VLANs et des configurations réseaux multi-sites.

Ce projet intègre une interface client dynamique, un panel d'administration complet et une base de données relationnelle robuste.

---

## ✨ Fonctionnalités Principales

### 👤 Espace Client
* **Attribution d'IP :** Génération automatique de 1 à 50 adresses IP dans les sous-réseaux attribués.
* **Visualisation Réseau :** Consultation des détails techniques : VLAN, VRF, RD, Masque et Statut des interfaces.
* **Gestion Autonome :** Ajout et suppression d'adresses IP en temps réel.
* **Interface :** Mode Sombre (Dark Mode) / Mode Clair et design responsive.

### 🛡️ Espace Administrateur
* **Gestion des Utilisateurs :** CRUD complet (Création, Lecture, Mise à jour, Suppression) des comptes clients.
* **Supervision Globale :** Vue d'ensemble sur tous les clients, leurs sites (Paris, Lyon, etc.) et leurs ressources allouées.
* **Intervention :** Possibilité d'ajouter ou de révoquer des IP directement sur le compte d'un client en cas de problème.
* **Sécurité :** Hachage des mots de passe (`password_hash`) et protection des sessions.

---

## 🏗️ Architecture & Base de Données

Le projet repose sur une architecture **Client/Serveur** classique utilisant **Apache** et **PostgreSQL**. La base de données est structurée pour gérer la relation entre les sites géographiques et l'infrastructure réseau.

**Tables Principales :** 
* `client` : Informations utilisateurs et droits (Admin/User).
* `site` : Localisation géographique (ex: Paris).
* `vlan` : Segmentation logique associée au client.
* `sousreseau` & `plageip` : Gestion des pools d'adresses.

> **Note Technique :** Dans le cadre du projet, la base de données PostgreSQL a été rendue accessible à distance via **Ngrok** pour simuler une infrastructure distribuée.

---

## 🚀 Installation & Déploiement

### Prérequis
* Un serveur Web (Apache/Nginx).
* PHP 7.x ou 8.x.
* Serveur de base de données PostgreSQL.

### Étapes d'installation

1.  **Cloner le projet :**
    ```bash
    git clone [https://github.com/votre-username/sae203-ipam.git](https://github.com/votre-username/sae203-ipam.git)
    ```

2.  **Configuration de la Base de Données :**
    Importez le script SQL fourni dans votre serveur PostgreSQL :
    ```bash
    psql -U postgres -d ipam -f sae203.sql
    ```
    *(Le script crée les tables `site`, `client`, `vlan`, `plageip`, `sousreseau`)*.

3.  **Connexion à la BDD :**
    Modifiez le fichier `SITE/config.php` avec vos identifiants :
    ```php
    $host = "localhost"; // Ou votre tunnel Ngrok
    $dbname = "ipam";
    $username = "votre_user";
    $password = "votre_mdp";
    ```

4.  **Lancement :**
    Placez le contenu du dossier `SITE/` à la racine de votre serveur web (`/var/www/html` ou `htdocs`) et accédez à `http://localhost/index.php`.

---

## 🔑 Identifiants de Démonstration

Pour tester l'application immédiatement après l'importation de la base de données :

| Rôle | Email | Mot de passe |
| :--- | :--- | :--- |
| **Administrateur** | `admin@gmail.com` | `admin` |
| **Client Test** | `testclient1@gmail.com` | *(A créer)* |

---

## 📂 Structure du Projet

```text
SAE203/
├── sae203.sql                      # 💾 Script de création de la BDD (PostgreSQL)
├── SAE23_Rapport.pdf               # 📄 Rapport technique détaillé
└── SITE/                           # 💻 Code source de l'application
    ├── index.php                   # Page d'accueil (Landing Page)
    ├── connexion.php               # Login
    ├── inscription.php             # Register
    ├── ajout.php                   # Logique d'ajout d'IP
    ├── gerer_utilisateur.php       # Dashboard Admin
    ├── visualization.php           # Dashboard Client
    ├── config.php                  # Connexion BDD
    ├── css/                        # Feuilles de style
    └── img/                        # Assets graphiques
