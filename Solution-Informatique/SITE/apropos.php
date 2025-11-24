<?php
require_once 'config.php';
session_start();
?>
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>À propos - SAE 2.03 - IPAM</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      transition: background-color 0.3s, color 0.3s;
    }

    body.dark {
      background-color: #121212;
      color: #f5f5f5;
    }

    body.light {
      background-color: #ffffff;
      color: #121212;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px;
      background-color: #1e1e1e;
      border-bottom: 1px solid #333;
    }

    body.light header {
      background-color: #f0f0f0;
      border-bottom: 1px solid #ccc;
    }

    .header-left, .header-right {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .logo {
      height: 40px;
    }

    nav {
      display: flex;
      gap: 20px;
    }

    nav a {
      color: #ccc;
      text-decoration: none;
      font-weight: bold;
      font-size: 1rem;
    }

    body.light nav a {
      color: #222;
    }

    nav a:hover {
      color: #fff;
    }

    .theme-toggle {
      padding: 8px 12px;
      border: none;
      border-radius: 5px;
      background-color: #007BFF;
      color: white;
      cursor: pointer;
    }

    .back-link {
      color: #ffffff;
      text-decoration: none;
      font-weight: bold;
    }

    .back-link:hover {
      text-decoration: underline;
    }

    .content {
      flex: 1;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
      line-height: 1.6;
    }

    .content h1 {
      font-size: 2.5rem;
      margin-bottom: 30px;
      text-align: center;
      background: linear-gradient(90deg, #d4d4d4, #ffffff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    body.light .content h1 {
      background: none;
      color: #000;
    }

    .content h2 {
      font-size: 1.8rem;
      margin-top: 30px;
      margin-bottom: 15px;
      color: #f0f0f0;
    }

    .content p {
      margin-bottom: 20px;
      font-size: 1.1rem;
    }

    body.light .content p {
      color: #333;
    }

    .highlight {
      background-color: #2a2a2a;
      padding: 20px;
      border-radius: 8px;
      margin: 20px 0;
      border-left: 4px solid #007BFF;
    }

    body.light .highlight {
      background-color: #f5f5f5;
      color: #333;
    }

    footer {
      background-color: #1e1e1e;
      color: #aaa;
      text-align: center;
      padding: 20px;
      margin-top: auto;
      font-size: 0.85rem;
    }

    body.light footer {
      background-color: #f0f0f0;
      color: #444;
    }
  </style>
  <script>
    function toggleTheme() {
      const body = document.body;
      body.classList.toggle('light');
      body.classList.toggle('dark');
    }
    window.onload = () => {
      document.body.classList.add('dark');
    };
  </script>
</head>
<body>
  <header>
    <div class="header-left">
      <img src="logo.png" alt="Logo IUT" class="logo">
      <a href="index.php" class="back-link">Retour à l'accueil</a>
    </div>
    <div class="header-right">
      <a href="connexion.php" title="Se connecter">
        <img src="connexion.png" alt="Connexion" style="height: 24px;">
      </a>
      <button class="theme-toggle" onclick="toggleTheme()">Mode</button>
    </div>
  </header>

  <div class="content">
    <h1>À propos du projet SAE 2.03</h1>
    
    <p>Bienvenue dans le projet SAE 2.03 - "Mettre en place une solution informatique". Ce projet a pour objectif de développer et déployer une solution complète de gestion d'adresses IP (IPAM - IP Address Management).</p>

    <h2>Qu'est-ce que l'IPAM ?</h2>
    <p>L'IPAM (IP Address Management) est une solution qui permet de planifier, suivre et gérer les informations d'adressage IP utilisées dans un réseau. Notre système permet aux entreprises de gérer efficacement leurs ressources réseau en évitant les conflits d'adresses IP et en optimisant l'utilisation de l'espace d'adressage.</p>

    <div class="highlight">
      <p><strong>Fonctionnalités principales :</strong></p>
      <p>- Gestion automatique des adresses IP disponibles<br>
      - Attribution et suivi des sous-réseaux<br>
      - Interface intuitive pour les administrateurs<br>
      - Génération de rapports de configuration<br>
      - Journalisation des opérations</p>
    </div>

    <h2>Objectifs pédagogiques</h2>
    <p>Ce projet s'inscrit dans le cadre de la formation BUT Réseaux et Télécommunucations et vise à développer les compétences suivantes :</p>
    <p>- Conception et développement d'applications web<br>
    - Gestion de bases de données<br>
    - Sécurité des applications<br>
    - Travail en équipe et gestion de projet<br>
    - Documentation technique</p>

    <h2>Technologies utilisées</h2>
    <p>Notre solution IPAM est développée avec les technologies suivantes :</p>
    <p>- <strong>Backend :</strong> PHP pour la logique métier<br>
    - <strong>Base de données :</strong> POSTGRESQL pour le stockage des données<br>
    - <strong>Frontend :</strong> HTML5, CSS3 et JavaScript<br>
    - <strong>Sécurité :</strong> Sessions PHP et validation des données</p>

    <div class="highlight">
      <p><strong>Note importante :</strong> Cette application est développée dans un cadre pédagogique à l'IUT de Villetaneuse. Elle respecte les bonnes pratiques de développement web et de sécurité informatique.</p>
    </div>

    <h2>Comment utiliser l'application ?</h2>
    <p>Pour accéder aux fonctionnalités de l'IPAM, vous devez créer un compte client et vous connecter. Une fois connecté, vous pourrez :</p>
    <p>- Demander l'attribution d'adresses IP<br>
    - Consulter vos configurations réseau<br>
    - Télécharger les fichiers de configuration<br>
    - Suivre l'historique de vos opérations</p>

    <p style="text-align: center; margin-top: 40px;">
      <a href="connexion.php" style="background: linear-gradient(90deg, #d6d6ff, #cce0ff); color: #000; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold;">Commencer maintenant</a>
    </p>
  </div>

  <footer>
    &copy; 2025 IUT de Villetaneuse - SAE 2.03 - Tous droits réservés.
  </footer>
</body>
</html>