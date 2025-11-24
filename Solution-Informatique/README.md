Projet SAE203 — Application Web de Gestion
Objectif du projet
Ce projet a pour but de développer une application web permettant la gestion d’utilisateurs, de clients et de configurations via une interface PHP connectée à une base de données MySQL.
Il inclut un système d’authentification, la gestion des rôles et un tableau de bord d’administration.

Prérequis
Avant d’installer et d’utiliser ce projet, vous devez disposer de :
-Serveur web (Apache recommandé)
-PHP 7.x ou 8.x
-MySQL / MariaDB
-Navigateur web récent (Chrome, Firefox, etc.)

Installation
1. Cloner ou télécharger le projet
git clone <url-du-projet>
ou extraire l’archive .zip.

2. Déployer les fichiers
-Placer le contenu du dossier SITE/ dans le répertoire racine de votre serveur web (ex. htdocs pour XAMPP ou var/www/html pour Apache sous Linux).

3. Configurer la base de données
-Importer le fichier sae203.sql dans votre base MySQL :
mysql -u root -p < sae203.sql

-Modifier le fichier config.php pour adapter les identifiants de connexion à votre base :
$host = "localhost";
$dbname = "nom_base";
$username = "utilisateur";
$password = "motdepasse";

4. Lancer l’application
-Démarrer Apache et MySQL.

-Ouvrir votre navigateur et accéder à :
http://localhost/index.php --> IMPOORTANT, login admin : admin@gmail.com mdp admin : admin

Structure du projet

SAE203/
├── README.md                      # Documentation du projet
├── SAE23_VAN-NGOC_SEAN_LE-PABIC_RONAN.pdf # Rapport du projet
├── sae203.sql                      # Script SQL pour la base de données
└── SITE/
    ├── index.php                   # Page d'accueil
    ├── connexion.php               # Page de connexion
    ├── inscription.php             # Page d'inscription
    ├── ajout.php                   # Formulaire d'ajout
    ├── ajouter_client.php          # Ajout d'un client
    ├── gerer_utilisateur.php       # Gestion des utilisateurs
    ├── edit_utilisateur.php        # Édition d'un utilisateur
    ├── deconnexion.php             # Déconnexion
    ├── config.php                  # Configuration BDD
    ├── ...                         # Autres scripts PHP
    ├── image-banner.jpg            # Image de bannière
    └── logo.png                    # Logo du site

Fonctionnalités principales
-Authentification sécurisée (connexion / inscription / déconnexion)
-Gestion des utilisateurs (ajout, modification, suppression)
-Gestion des clients et données associées
-Configuration dynamique via l’interface
-Interface d’administration claire

Auteurs
Sean Van-Ngoc
Ronan Le Pabic
