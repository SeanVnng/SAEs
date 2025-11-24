<?php
require_once 'config.php';
session_start();

# Accès uniquement admin
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

try {
    $stmt = $pdo->query("SELECT nomclient, prenomclient, email, admin, idsite FROM client ORDER BY idclient DESC LIMIT 10");
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Erreur : " . $e->getMessage());
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Derniers utilisateurs</title>
  <style>
    body {
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', Tahoma, sans-serif;
      padding: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    h1 {
      text-align: center;
      margin-bottom: 30px;
    }

    table {
      width: 100%;
      max-width: 800px;
      border-collapse: collapse;
      background-color: #1e1e1e;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
    }

    th, td {
      padding: 12px 15px;
      border: 1px solid #333;
      text-align: left;
    }

    th {
      background-color: #2c2c2c;
      color: #ccc;
    }

    tr:hover {
      background-color: #2a2a2a;
    }

    a.back {
      margin-top: 20px;
      text-decoration: underline;
      color: #ccc;
    }
  </style>
</head>
<body>
  <h1>Derniers utilisateurs ajoutés</h1>

  <table>
    <thead>
      <tr>
        <th>Nom</th>
        <th>Prénom</th>
        <th>Email</th>
        <th>Rôle</th>
        <th>Site</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($users as $user): ?>
        <tr>
          <td><?= htmlspecialchars($user['nomclient']) ?></td>
          <td><?= htmlspecialchars($user['prenomclient']) ?></td>
          <td><?= htmlspecialchars($user['email']) ?></td>
          <td><?= $user['admin'] ? 'Administrateur' : 'Client' ?></td>
          <td><?= htmlspecialchars($user['idsite']) ?></td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>

  <a href="menu.php" class="back">Retour au menu</a>
</body>
</html>
