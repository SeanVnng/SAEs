<?php
require_once 'config.php';
session_start();

if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

$stmt = $pdo->query("SELECT idclient, nomclient, prenomclient, email, admin FROM client ORDER BY idclient");
$users = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Liste des utilisateurs</title>
  <style>
    body { background-color: #121212; color: #f5f5f5; font-family: sans-serif; padding: 40px; }
    table { width: 100%; background: #1e1e1e; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 12px; border: 1px solid #444; }
    a.edit-link { color: #66caff; text-decoration: none; font-weight: bold; }
    .admin { color: #ffcc00; }
    h1 { text-align: center; }
    .back { margin-top: 20px; text-align: center; }
    .back a { color: #aaa; text-decoration: underline; }
  </style>
</head>
<body>
  <h1>Liste des utilisateurs</h1>
  <table>
    <thead>
      <tr>
        <th>Nom</th><th>Prénom</th><th>Email</th><th>Rôle</th><th>Action</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($users as $u): ?>
        <tr>
          <td><?= htmlspecialchars($u['nomclient']) ?></td>
          <td><?= htmlspecialchars($u['prenomclient']) ?></td>
          <td><?= htmlspecialchars($u['email']) ?></td>
          <td class="<?= $u['admin'] ? 'admin' : '' ?>"><?= $u['admin'] ? 'Admin' : 'Client' ?></td>
          <td><a class="edit-link" href="edit_utilisateur.php?id=<?= $u['idclient'] ?>">Modifier</a></td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>

  <div class="back">
    <a href="menu.php"> Retour au menu</a>
  </div>
</body>
</html>
