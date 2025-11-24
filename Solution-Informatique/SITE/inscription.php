<?php
# Inclusion du fichier de configuration (connexion DB, constantes, etc...)
require_once 'config.php';

# Vérification que la requête est bien en POST (formulaire d'inscription soumis)
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    # Récupération des données du formulaire
    $email = $_POST["email"];
    $password = $_POST["password"];
    $confirm = $_POST["confirm_password"];
    $prenom = $_POST["prenom"];
    $nom = $_POST["nom"];
    $id_site = $_POST["idsite"];

    # Vérification que les deux mots de passe saisis sont identiques
    if ($password !== $confirm) {
        $error = "Les mots de passe ne correspondent pas.";
    } else {
        try {
            # Vérification si l'email existe déjà en base de données
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM client WHERE email = ?");
            $stmt->execute([$email]);

            # Si l'email existe déjà (count > 0), on refuse l'inscription
            if ($stmt->fetchColumn() > 0) {
                $error = "Cet email est déjà utilisé.";
            } else {
                # Hash sécurisé du mot de passe avant stockage en BDD
                $hash = password_hash($password, PASSWORD_DEFAULT);
                
                # Insertion du nouveau client en base de données
                $stmt = $pdo->prepare("INSERT INTO client (nomclient, prenomclient, email, mot_de_passe, idsite) VALUES (?, ?, ?, ?, ?)");
                $stmt->execute([$nom, $prenom, $email, $hash, $id_site]);
                
                # Message de succès si tout s'est bien passé
                $success = "Inscription réussie.";
            }
        } catch (PDOException $e) {
            # Gestion des erreurs de base de données
            $error = "Erreur : " . $e->getMessage();
        }
    }
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Inscription - SAE 2.03</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      margin: 0;
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }

    .signup-box {
      background-color: #1e1e1e;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 0 12px rgba(0,0,0,0.6);
      width: 100%;
      max-width: 450px;
      text-align: center;
    }

    h2 {
      margin-bottom: 20px;
      font-size: 1.8rem;
    }

    input[type="email"],
    input[type="password"],
    input[type="text"],
    select {
      width: 100%;
      padding: 12px;
      margin-bottom: 20px;
      border: none;
      border-radius: 6px;
      background-color: #2c2c2c;
      color: #fff;
      font-size: 1rem;
      box-sizing: border-box;
    }

    input[type="submit"] {
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 6px;
      background: linear-gradient(90deg, #d6d6ff, #cce0ff);
      color: #000;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
    }

    .footer-link {
      margin-top: 15px;
      font-size: 0.9rem;
      color: #aaa;
    }

    .footer-link a {
      color: #ccc;
      text-decoration: none;
      display: block;
      margin-top: 5px;
    }
  </style>
</head>
<body>
  <form class="signup-box" method="post" action="">
    <h2>Inscription</h2>
    <?php if (!empty($success)) echo "<p style='color:limegreen;'>$success</p>"; ?>
    <?php if (!empty($error)) echo "<p style='color:red;'>$error</p>"; ?>
    <input type="email" name="email" placeholder="Email" required>
    <input type="text" name="nom" placeholder="Nom" required>
    <input type="text" name="prenom" placeholder="Prénom" required>
    <select name="idsite" required>
        <option value=""> -- Choisir un site --</option>
        <option value="1"> Paris </option>
    </select>
    <input type="password" name="password" placeholder="Mot de passe" required>
    <input type="password" name="confirm_password" placeholder="Confirmer le mot de passe" required>
    <input type="submit" value="S'inscrire">
    <div class="footer-link">
      <a href="connexion.php">Déjà inscrit ? Se connecter</a>
    </div>
  </form>
</body>
</html>
