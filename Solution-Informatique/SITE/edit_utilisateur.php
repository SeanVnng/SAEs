<?php
require_once 'config.php';
session_start();

# Sécurité : uniquement pour admin
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

# Récupération de l'utilisateur à éditer
$id = $_GET['id'] ?? null;
if (!$id) {
    header("Location: menu.php");
    exit;
}

$error = $success = "";

try {
   # Récupération des données actuelles de l'utilisateur
   $stmt = $pdo->prepare("SELECT * FROM client WHERE idclient = ?");
   $stmt->execute([$id]);
   $utilisateur = $stmt->fetch(PDO::FETCH_ASSOC);

   if (!$utilisateur) {
       throw new Exception("Utilisateur non trouvé.");
   }

   if ($_SERVER["REQUEST_METHOD"] === "POST") {
       # Récupération des nouvelles données du formulaire
       $nom = $_POST['nom'];
       $prenom = $_POST['prenom'];
       $email = $_POST['email'];
       $site = $_POST['site'];
       $role = $_POST['role'] ?? 'client';
       $password = $_POST['password'];

       # Conversion du rôle pour PostgreSQL
       $admin = ($role === 'admin') ? 'true' : 'false';

       # UPDATE avec ou sans changement de mot de passe
       if (!empty($password)) {
           # Nouveau mot de passe : on le hash et on l'inclut dans l'update
           $hash = password_hash($password, PASSWORD_DEFAULT);
           $stmt = $pdo->prepare("UPDATE client SET nomclient=?, prenomclient=?, email=?, mot_de_passe=?, idsite=?, admin=? WHERE idclient=?");
           $stmt->execute([$nom, $prenom, $email, $hash, $site, $admin, $id]);
       } else {
           # Pas de nouveau mot de passe : on garde l'ancien
           $stmt = $pdo->prepare("UPDATE client SET nomclient=?, prenomclient=?, email=?, idsite=?, admin=? WHERE idclient=?");
           $stmt->execute([$nom, $prenom, $email, $site, $admin, $id]);
       }

       # Création d'un fichier de sauvegarde des modifications
       $file = fopen("exports/conf_client_$id.txt", "w");
       fwrite($file, "Nom : $nom\nPrénom : $prenom\nEmail : $email\nSite : $site\nRôle : " . ($admin ? "Administrateur" : "Client") . "\n");
       fclose($file);

       $success = "Utilisateur modifié avec succès.";
   }

} catch (Exception $e) {
   $error = "Erreur : " . $e->getMessage();
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Modifier l'utilisateur</title>
  <style>
    body {
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px;
    }

    form {
      background-color: #1e1e1e;
      padding: 30px;
      border-radius: 10px;
      width: 100%;
      max-width: 500px;
      box-shadow: 0 0 10px rgba(0,0,0,0.4);
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    form h2 {
      text-align: center;
      margin-bottom: 20px;
    }

    label {
      width: 100%;
      text-align: left;
      margin-top: 10px;
    }

    input, select {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border-radius: 5px;
      border: none;
      background-color: #2c2c2c;
      color: white;
    }

    input[type="submit"] {
      margin-top: 20px;
      background-color: #33aaff;
      font-weight: bold;
      cursor: pointer;
    }

    .error { color: red; text-align: center; margin-top: 10px; }
    .success { color: limegreen; text-align: center; margin-top: 10px; }

    .back {
      margin-top: 20px;
      color: #ccc;
      text-decoration: underline;
      text-align: center;
    }
  </style>
</head>
<body>
  <form method="post">
    <h2>✏️ Modifier l'utilisateur</h2>

    <?php if (!empty($error)) echo "<p class='error'>$error</p>"; ?>
    <?php if (!empty($success)) echo "<p class='success'>$success</p>"; ?>

    <label>Nom :</label>
    <input type="text" name="nom" value="<?= htmlspecialchars($utilisateur['nomclient']) ?>" required>

    <label>Prénom :</label>
    <input type="text" name="prenom" value="<?= htmlspecialchars($utilisateur['prenomclient']) ?>" required>

    <label>Email :</label>
    <input type="email" name="email" value="<?= htmlspecialchars($utilisateur['email']) ?>" required>

    <label>Mot de passe (laisser vide pour ne pas changer) :</label>
    <input type="password" name="password" placeholder="Nouveau mot de passe">

    <label>Site :</label>
    <select name="site" required>
      <option value="1" <?= $utilisateur['idsite'] == 1 ? 'selected' : '' ?>>Paris</option>
    </select>

    <label>Rôle :</label>
    <select name="role" required>
      <option value="client" <?= !$utilisateur['admin'] ? 'selected' : '' ?>>Client</option>
      <option value="admin" <?= $utilisateur['admin'] ? 'selected' : '' ?>>Administrateur</option>
    </select>

    <input type="submit" value="Enregistrer les modifications">
    <a href="menu.php" class="back"> Retour à la liste</a>
  </form>
</body>
</html>
