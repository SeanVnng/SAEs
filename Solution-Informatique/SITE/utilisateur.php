<?php
require_once 'config.php';
session_start();

# Sécurité : uniquement admin
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

# Récupération de tous les utilisateurs
try {
    $stmt = $pdo->query("SELECT idclient, nomclient, prenomclient FROM client ORDER BY nomclient ASC");
    $clients = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Erreur : " . $e->getMessage());
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Gestion des IPs utilisateurs</title>
  <style>
    body {
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', sans-serif;
      padding: 40px;
      text-align: center;
    }

    h1 {
      margin-bottom: 30px;
    }

    .user-list {
      max-width: 600px;
      margin: 0 auto;
      background-color: #1e1e1e;
      padding: 20px;
      border-radius: 10px;
    }

    .user-item {
      margin: 10px 0;
      padding: 10px;
      background-color: #2c2c2c;
      border-radius: 5px;
    }

    .user-item a {
      color: #aaddff;
      text-decoration: none;
      font-weight: bold;
    }

    .user-item a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <h1>Liste des utilisateurs</h1>

  <div class="user-list">
    <?php foreach ($clients as $client): ?>
      <div class="user-item">
        <a href="gerer_utilisateur.php?id=<?= $client['idclient'] ?>">
          <?= htmlspecialchars($client['nomclient']) . " " . htmlspecialchars($client['prenomclient']) ?>
        </a>
      </div>
    <?php endforeach; ?>
  </div>

  <br>
  <a href="menu.php" style="color:#ccc;text-decoration:underline;"> Retour au menu</a>
</body>
</html>
