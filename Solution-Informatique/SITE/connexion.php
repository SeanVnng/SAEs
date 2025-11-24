<?php
# Inclusion du fichier de configuration (connexion DB, constantes, etc.)
require_once 'config.php';

# Démarrage de la session pour pouvoir stocker les infos utilisateur
session_start();

# Initialisation de la variable d'erreur car sinon "variable undefinied"
$error = '';

# Vérification que le formulaire de connexion a été soumis
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $email    = $_POST['email'];
    $password = $_POST['password'];

    # Recherche de l'utilisateur en base par son email
    $stmt = $pdo->prepare("SELECT * FROM client WHERE email = :email");
    $stmt->execute(['email' => $email]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    # Vérification que l'utilisateur existe ET que le mot de passe est correct
    if ($user && password_verify($password, $user['mot_de_passe'])) {
        # Stockage des informations utilisateur en session
        $_SESSION['idclient']  = $user['idclient'];
        $_SESSION['email']     = $user['email'];
        $_SESSION['nomclient'] = $user['nomclient'];
        $_SESSION['admin']     = $user['admin'];

        # Redirection selon le niveau d'accès : admin vers menu.php, client vers menu_client.php
        header("Location: " . ($user['admin'] ? 'menu.php' : 'menu_client.php'));
        exit; # Important : arrêter l'exécution après la redirection
    } else {
        # Message d'erreur générique pour ne pas donner d'infos aux attaquants (hack)
        $error = "Identifiants invalides.";
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Connexion - SAE 2.03</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    /* plein écran noir / texte clair */
    body{
      margin:0;
      height:100vh;
      display:flex;
      flex-direction:column;
      background:#121212;
      color:#f5f5f5;
      font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
    }

    /* barre de navigation moderne */
    .navbar{
      background:linear-gradient(135deg, #2c2c2c, #1a1a1a);
      padding:12px 25px;
      box-shadow:0 2px 8px rgba(0,0,0,.4);
      display:flex;
      justify-content:space-between;
      align-items:center;
      border-bottom:1px solid #333;
    }

    .logo{
      display:flex;
      align-items:center;
      text-decoration:none;
      transition:opacity 0.3s ease;
    }

    .logo:hover{
      opacity:0.8;
    }

    .logo img{
      height:70px;
      width:auto;
    }

    .nav-right{
      display:flex;
      align-items:center;
      gap:15px;
    }

    .nav-link{
      color:#000000;
      text-decoration:none;
      font-size:1rem;
      padding:8px 16px;
      border-radius:6px;
      background:linear-gradient(90deg,#d6d6ff,#cce0ff);
      border:1px solid rgba(74, 158, 255, 0.3);
      transition:all 0.3s ease;
    }

    .nav-link:hover{
      background:rgba(74, 158, 255, 0.2);
      border-color:rgba(74, 158, 255, 0.5);
      color:#fff;
    }

    /* contenu principal centré */
    .main-content{
      flex:1;
      display:flex;
      justify-content:center;
      align-items:center;
    }

    /* bloc gris foncé centré */
    .login-box{
      background:#1e1e1e;
      padding:40px 50px;        /* padding identique gauche/droite → texte parfaitement centré */
      border-radius:12px;
      box-shadow:0 0 12px rgba(0,0,0,.6);
      width:100%;
      max-width:400px;
      display:flex;
      flex-direction:column;
      align-items:center;       /* centre tout le contenu dans le bloc */
      box-sizing:border-box;
    }

    h2{margin:0 0 25px;font-size:1.9rem;text-align:center;}

    input[type="email"],
    input[type="password"]{
      width:100%;
      padding:12px;
      margin-bottom:20px;
      border:none;
      border-radius:6px;
      background:#2c2c2c;
      color:#fff;
      box-sizing:border-box;
      text-align:center;        /* centrage du placeholder & du texte */
    }

    input[type="submit"]{
      width:100%;
      padding:12px;
      border:none;
      border-radius:6px;
      background:linear-gradient(90deg,#d6d6ff,#cce0ff);
      color:#000;
      font-size:1rem;
      font-weight:bold;
      cursor:pointer;
    }

    .error{color:#ff5252;margin-bottom:15px;text-align:center;}

    .footer-link{
      margin-top:18px;
      text-align:center;
      font-size:.9rem;
    }
    .footer-link a{
      color:#ccc;
      text-decoration:none;
    }
  </style>
</head>
<body>
  <nav class="navbar">
    <a href="index.php" class="logo">
      <img src="logo.png" alt="Logo SAE 2.03">
    </a>
    <div class="nav-right">
      <a href="index.php" class="nav-link">Accueil</a>
    </div>
  </nav>

  <div class="main-content">
    <form class="login-box" method="post">
      <h2>Connexion</h2>

      <?php if($error): ?>
        <div class="error"><?= htmlspecialchars($error) ?></div>
      <?php endif; ?>

      <input type="email"    name="email"    placeholder="Email"        required>
      <input type="password" name="password" placeholder="Mot de passe" required>
      <input type="submit"   value="Se connecter">

      <div class="footer-link">
        <a href="inscription.php">Pas encore de compte ? S'inscrire</a>
      </div>
    </form>
  </div>
</body>
</html>