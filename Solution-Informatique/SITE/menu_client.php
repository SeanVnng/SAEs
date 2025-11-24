<?php
require_once 'config.php';
session_start();

// Redirige si l'utilisateur n'est pas connecté ou est admin
if (!isset($_SESSION['email']) || $_SESSION['admin']) {
    header("Location: connexion.php");
    exit();
}

$success = $error = "";
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Menu Client</title>
  <style>
    body {
      margin: 0;
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      padding: 60px;
      text-align: center;
    }
    h1 {
      margin-bottom: 100px;
    }
    a.button, button {
      display: inline-block;
      margin: 75px;
      padding: 12px 20px;
      font-size: 2rem;
      font-weight: bold;
      color: white;
      background: #2c2c2c;
      border: none;
      border-radius: 6px;
      text-decoration: none;
      cursor: pointer;
    }
    a.button:hover, button:hover {
      background: #444;
    }
    .danger {
      background-color: #aa3333;
    }
    .success {
      color: limegreen;
      margin-bottom: 15px;
    }
    .error {
      color: red;
      margin-bottom: 15px;
    }
  </style>
</head>
<body>
  <h1>Bienvenue sur votre espace client</h1>

  <?php if (!empty($success)) echo "<p class='success'>$success</p>"; ?>
  <?php if (!empty($error)) echo "<p class='error'>$error</p>"; ?>

  <a href="visualisation.php" class="button">Visualisation🔍</a>
  <a href="ajout.php" class="button">Ajouter IP➕</a>
  <a href="deconnexion.php" class="button">Déconnexion🚪</a>

  <a href="supprimer.php" class="button">Gérer mes IP❌</a>

</body>
</html>
