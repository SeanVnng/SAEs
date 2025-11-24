<?php
require_once 'config.php';
session_start();

#Ajout des 3 blocs (nombre de client, nombre de vlan, nombre d'IP).
$nb_clients = $pdo->query("SELECT COUNT(*) FROM client WHERE admin = false")->fetchColumn();
$nb_vlan = $pdo->query("SELECT COUNT(*) FROM vlan")->fetchColumn();
$nb_ip = $pdo->query("SELECT COUNT(*) FROM sousreseau")->fetchColumn();


?>
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>SAE 2.03 - MINI-IPAM</title>
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
      height: 70px;
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

    .info {
      position: relative;
      cursor: pointer;
      font-size: 1.5rem;
    }

    .info-box {
      display: none;
      position: absolute;
      top: 30px;
      right: 0;
      background-color: #333;
      color: #fff;
      padding: 10px;
      border-radius: 5px;
      font-size: 0.85rem;
      white-space: nowrap;
    }

    body.light .info-box {
      background-color: #eee;
      color: #000;
    }

    .info:hover .info-box {
      display: block;
    }

    .hero {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 60px 40px;
      background: linear-gradient(135deg, #1f1f1f, #2c2c2c);
    }

    body.light .hero {
      background: linear-gradient(135deg, #f9f9f9, #e0e0e0);
    }

    .hero-text {
      max-width: 50%;
    }

    .hero-text h1 {
      font-size: 3rem;
      margin: 0;
      overflow: hidden;
      white-space: nowrap;
      border-right: 0.15em solid transparent;
      animation: typing 4s steps(70, end) infinite, blink-caret 0.75s step-end infinite;
    }

    @keyframes typing {
    0% { width: 0 }
    50% { width: 100% }
    80% { width: 100% }
    100% { width: 0 }
    }


    @keyframes blink-caret {
      from, to { border-color: transparent }
      50% { border-color: white; }
    }

    body.dark .hero-text h1 {
      background: linear-gradient(90deg, #d4d4d4, #ffffff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    body.light .hero-text h1 {
      background: none;
      color: #000;
    }

    .hero-text p {
      margin-top: 20px;
      font-size: 1.5rem;
      color: #aaa;
    }

    body.light .hero-text p {
      color: #444;
    }

    .hero-buttons {
      margin-top: 30px;
    }

    .hero-buttons a {
      display: inline-block;
      padding: 12px 24px;
      margin-right: 10px;
      border: none;
      border-radius: 5px;
      font-size: 1rem;
      cursor: pointer;
      text-decoration: none;
    }

    .hero-buttons .primary {
      background: linear-gradient(90deg, #d6d6ff, #cce0ff);
      color: #000;
    }

    .hero-buttons .secondary {
      background: #333;
      color: #fff;
    }

    body.light .hero-buttons .secondary {
      background: #ddd;
      color: #000;
    }

    .hero-image {
      max-width: 40%;
    }

    .hero-image img {
      width: 100%;
      border-radius: 10px;
    }

    /* Section des statistiques */
    .stats-section {
      display: flex; 
      justify-content: center; 
      gap: 25px; 
      margin: 60px 0; 
      padding: 0 20px;
    }

    .stat-card {
      background: #2c2c2c; 
      padding: 70px; 
      border-radius: 8px; 
      width: 160px; 
      text-align: center; 
      box-shadow: 0 0 6px rgba(0,0,0,0.4);
      transition: transform 0.3s ease;
    }

    .stat-card:hover {
      transform: translateY(-2px);
    }

    body.light .stat-card {
      background: #f5f5f5;
      box-shadow: 0 0 6px rgba(0,0,0,0.1);
    }

    .stat-card h2 {
      margin: 0; 
      color: #d6d6ff;
      font-size: 2rem;
    }

    body.light .stat-card h2 {
      color: #007BFF;
    }

    .stat-card p {
      margin: 8px 0 0 0; 
      color: #ccc;
      font-size: 0.9rem;
    }

    body.light .stat-card p {
      color: #666;
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
    </div>
    <div class="header-right">
      <a href="connexion.php" title="Se connecter">
        <img src="connexion.png" alt="Connexion" style="height: 24px;">
      </a>
      <button class="theme-toggle" onclick="toggleTheme()">Mode</button>
      <div class="info">ℹ️
        <div class="info-box">Pour démarrer, veuillez créer un compte pour vous connecter. Par la suite vous aurez accès a un compte client pour ajouter / supprimer les IP(s) choisis.</div>
      </div>
    </div>
  </header>

  <section class="hero">
    <div class="hero-text">
      <h1>SAE 2.03 - Mettre en place 
        une solution informatique</h1>
      <p>Bienvenue sur notre plateforme IPAM, un outil de gestion automatisée des adresses IP pour les clients de notre réseau. Configurer par MR VAN NGOC & MR LE PABIC.</p>
      <div class="hero-buttons">
        <a href="connexion.php" class="primary">Commencer</a>
        <a href="apropos.php" class="secondary">En savoir plus</a>
      </div>
    </div>
    <div class="hero-image">
      <img src="image-banner.jpg" alt="Illustration IPAM">
    </div>
  </section>

  <div class="stats-section">
    <div class="stat-card">
      <h2><?= $nb_clients ?></h2>
      <p>Clients</p>
    </div>
    <div class="stat-card">
      <h2><?= $nb_vlan ?></h2>
      <p>VLANs utilisés</p>
    </div>
    <div class="stat-card">
      <h2><?= $nb_ip ?></h2>
      <p>IP configurées</p>
    </div>
  </div>

  <footer>
    &copy; 2025 IUT de Villetaneuse - SAE 2.03 - Tous droits réservés.
  </footer>
</body>
</html>