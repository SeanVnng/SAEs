<?php
require_once 'config.php';
session_start();

#Sécurité : accès réservé aux administrateurs
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

$success = $error = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $nom      = trim($_POST["nom"]);
    $prenom   = trim($_POST["prenom"]);
    $email    = trim($_POST["email"]);
    $mdp      = $_POST["mot_de_passe"];
    $site     = $_POST["idsite"];
    $is_admin = ($_POST["role"] === "admin") ? 'true' : 'false';

    if (empty($nom) || empty($prenom) || empty($email) || empty($mdp) || empty($site)) {
        $error = "Tous les champs sont obligatoires.";
    } else {
        $hash = password_hash($mdp, PASSWORD_DEFAULT);
        try {
            $stmt = $pdo->prepare("INSERT INTO client (nomclient, prenomclient, email, mot_de_passe, idsite, admin) VALUES (?, ?, ?, ?, ?, CAST(? AS BOOLEAN))");
            $stmt->execute([$nom, $prenom, $email, $hash, $site, $is_admin]);
            $success = "✅ Utilisateur ajouté avec succès.";
        } catch (PDOException $e) {
            $error = "Erreur : " . $e->getMessage();
        }
    }
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Ajouter un utilisateur</title>
  <style>
    body {
      background: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }

    .form-box {
      background: #1e1e1e;
      padding: 40px 50px;
      border-radius: 12px;
      box-shadow: 0 0 12px rgba(0,0,0,0.6);
      width: 100%;
      max-width: 500px;
      box-sizing: border-box;
      text-align: center;
    }

    h2 {
      margin-bottom: 20px;
    }

    form {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    form label {
      align-self: flex-start;
      margin-top: 15px;
      font-size: 0.95rem;
    }

    input, select {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border-radius: 6px;
      border: none;
      background-color: #2c2c2c;
      color: white;
      font-size: 1rem;
      box-sizing: border-box;
      text-align: center;
    }

    input[type="submit"] {
      margin-top: 25px;
      background: linear-gradient(90deg, #d6d6ff, #cce0ff);
      color: #000;
      font-weight: bold;
      cursor: pointer;
    }

    .message {
      margin-top: 15px;
      font-weight: bold;
    }

    .success {
      color: limegreen;
    }

    .error {
      color: red;
    }

    a {
      display: inline-block;
      margin-top: 20px;
      color: #ccc;
      text-decoration: underline;
      font-size: 0.95rem;
    }
  </style>
</head>
<body>
  <div class="form-box">
    <h2>Ajouter un utilisateur</h2>

    <?php if ($success): ?>
      <p class="message success"><?= $success ?></p>
    <?php elseif ($error): ?>
      <p class="message error"><?= $error ?></p>
    <?php endif; ?>

    <form method="post">
      <label for="nom">Nom</label>
      <input type="text" name="nom" required>

      <label for="prenom">Prénom</label>
      <input type="text" name="prenom" required>

      <label for="email">Email</label>
      <input type="email" name="email" required>

      <label for="mot_de_passe">Mot de passe</label>
      <input type="password" name="mot_de_passe" required>

      <label for="idsite">Site</label>
      <select name="idsite" required>
        <option value="">-- Choisir un site --</option>
        <option value="1">Paris</option>
      </select>

      <label for="role">Rôle</label>
      <select name="role" required>
        <option value="client">Client</option>
        <option value="admin">Administrateur</option>
      </select>

      <input type="submit" value="Créer le compte">
    </form>

    <a href="menu.php">Retour au menu </
