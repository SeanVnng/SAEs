<?php
session_start();
require_once 'config.php';

# Vérifie que l'utilisateur est connecté ET est admin
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

# Récupération des données pour les statistiques
$totalClients = $pdo->query("SELECT COUNT(*) FROM client WHERE admin = false")->fetchColumn();
$totalVLANs = $pdo->query("SELECT COUNT(*) FROM vlan")->fetchColumn();
$totalIPs = $pdo->query("SELECT COUNT(*) FROM sousreseau")->fetchColumn();
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Menu Administrateur</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background-color: #1e1e1e;
      padding: 20px;
      border-bottom: 1px solid #333;
      width: 100%;
    }

    .header-left img {
      height: 40px;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .info {
      position: relative;
      font-size: 1.5rem;
      cursor: pointer;
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

    .info:hover .info-box {
      display: block;
    }

    .welcome {
      margin-top: 40px;
      font-size: 1.2rem;
      text-align: center;
    }

    .stats-grid {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin-top: 20px;
    }

    .stat-box {
      background: #1e1e1e;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      min-width: 150px;
      box-shadow: 0 0 5px rgba(255, 255, 255, 0.1);
    }

    .stat-box h3 {
      color: #88ccff;
    }
    .menu-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 40px;
      width: 100%;
    }

    .menu-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 20px;
      width: 100%;
      max-width: 800px;
      margin: 20px;
    }

    .menu-item {
      background-color: #1e1e1e;
      border: 1px solid #333;
      border-radius: 8px;
      text-align: center;
      padding: 30px 20px;
      text-decoration: none;
      font-weight: bold;
      color: #ccc;
      transition: background-color 0.3s, color 0.3s;
    }

    .menu-item:hover {
      background-color: #333;
      color: #fff;
    }
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <img src="logo.png" alt="Logo IUT">
    </div>
    <div class="header-right">
      <div class="info">ℹ️
        <div class="info-box">Vous êtes connecté en tant qu'administrateur.</div>
      </div>
    </div>
  </header>

  <div class="welcome">
    Bienvenue <?php echo htmlspecialchars($_SESSION['email']); ?> !👋👋
  </div>

  <div class="stats-grid">
    <div class="stat-box">
      <h3><?php echo $totalClients; ?></h3>
      <p>Clients</p>
    </div>
    <div class="stat-box">
      <h3><?php echo $totalVLANs; ?></h3>
      <p>VLANs</p>
    </div>
    <div class="stat-box">
      <h3><?php echo $totalIPs; ?></h3>
      <p>IP configurées</p>
    </div>
  </div>

  <div class="menu-wrapper">
    <div class="menu-grid">
      <a href="ajouter_client.php" class="menu-item">Ajouter un utilisateur</a>
      <a href="supprimer_client.php" class="menu-item">Supprimer un utilisateur</a>
      <a href="visualisation.php" class="menu-item">Visualisation</a>
      <a href="liste_utilisateur.php" class="menu-item">Editer un utilisateur</a>
      <a href="last_util.php" class="menu-item">10 derniers utilisateurs</a>
      <a href="utilisateur.php" class="menu-item">Ajouter / Supprimer IP</a>
      <a href="deconnexion.php" class="menu-item">Déconnexion</a>
    </div>
  </div>
</body>
</html>
