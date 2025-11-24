<?php
require_once 'config.php';
session_start();

# Vérifie que l'utilisateur est connecté et n'est pas admin
if (!isset($_SESSION['idclient']) || $_SESSION['admin']) {
    header("Location: connexion.php");
    exit();
}

$idclient = $_SESSION['idclient']; #  
$success = $error = "";

# Si l'utilisateur a soumis des cases cochées
if ($_SERVER["REQUEST_METHOD"] === "POST" && !empty($_POST['ips'])) {
    $ips_to_delete = $_POST['ips'];

    try {
        $stmt = $pdo->prepare("DELETE FROM sousreseau WHERE idclient = ? AND ipreseau = ?");
        foreach ($ips_to_delete as $ip) {
            $stmt->execute([$idclient, $ip]);
        }
        $success = "IP supprimées avec succès.";
    } catch (PDOException $e) {
        $error = "Erreur : " . $e->getMessage();
    }
}

# Récupération des IP actuelles de l'utilisateur
$stmt = $pdo->prepare("SELECT ipreseau FROM sousreseau WHERE idclient = ?");
$stmt->execute([$idclient]);
$ips = $stmt->fetchAll(PDO::FETCH_COLUMN);
$stmt = $pdo->prepare("
    SELECT c.nomclient, c.prenomclient, c.email, s.nomsite,
           sr.ipreseau, sr.masque, sr.ipinterface,
           v.numvlan, v.nomvrf, v.rd
    FROM client c
    LEFT JOIN site s ON c.idsite = s.idsite
    LEFT JOIN sousreseau sr ON c.idclient = sr.idclient
    LEFT JOIN vlan v ON c.idclient = v.idclient
    WHERE c.idclient = ?
");
$stmt->execute([$idclient]);
$data = $stmt->fetchAll(PDO::FETCH_ASSOC);

# 2. Créer ou écraser le fichier
$dir = __DIR__ . '/exports';
if (!is_dir($dir)) {
    mkdir($dir, 0777, true);
}
$filepath = $dir . "/config_client_$idclient.txt";
$f = fopen($filepath, 'w');

if ($f) {
    foreach ($data as $row) {
        fwrite($f, "Nom : {$row['nomclient']}\n");
        fwrite($f, "Prénom : {$row['prenomclient']}\n");
        fwrite($f, "Email : {$row['email']}\n");
        fwrite($f, "Site : {$row['nomsite']}\n");
        fwrite($f, "IP Réseau : {$row['ipreseau']}\n");
        fwrite($f, "Masque : {$row['masque']}\n");
        fwrite($f, "IP Interface : {$row['ipinterface']}\n");
        fwrite($f, "VLAN : {$row['numvlan']}\n");
        fwrite($f, "VRF : {$row['nomvrf']}\n");
        fwrite($f, "RD : {$row['rd']}\n");
        fwrite($f, str_repeat("-", 20) . "\n");
    }
    fclose($f);
}
?>


<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Supprimer des IP</title>
  <style>
    body {
      background: #121212;
      color: #f5f5f5;
      font-family: sans-serif;
      padding: 40px;
      text-align: center;
    }

    form {
      background: #1e1e1e;
      padding: 30px;
      border-radius: 10px;
      display: inline-block;
      max-width: 500px;
      margin-top: 20px;
    }

    h2 {
      margin-bottom: 20px;
    }

    label {
      display: block;
      text-align: left;
      margin: 8px 0;
    }

    input[type="submit"] {
      margin-top: 20px;
      padding: 10px 20px;
      background: #aa3333;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-weight: bold;
    }

    .success {
      color: limegreen;
      margin-top: 10px;
    }

    .error {
      color: red;
      margin-top: 10px;
    }

    a {
      display: inline-block;
      margin-top: 20px;
      color: #ccc;
      text-decoration: underline;
    }
    .menu-link {
        margin-top: 20px;
        text-align: center;
    }

    .menu-link a {
        color: #ccc;
        text-decoration: underline;
        font-size: 0.95rem;
    }

  </style>
</head>
<body>
  <h1>Gestion des IP attribuées</h1>

  <?php if (!empty($success)) echo "<p class='success'>$success</p>"; ?>
  <?php if (!empty($error)) echo "<p class='error'>$error</p>"; ?>

  <?php if (empty($ips)): ?>
    <p>Vous n'avez aucune IP attribuée.</p>
  <?php else: ?>
    <form method="post">
      <h2>Choisissez les IP à supprimer</h2>
      <?php foreach ($ips as $ip): ?>
        <label>
          <input type="checkbox" name="ips[]" value="<?= htmlspecialchars($ip) ?>">
          <?= htmlspecialchars($ip) ?>/24
        </label>
      <?php endforeach; ?>
        <input type="submit" value="Supprimer les IP sélectionnées">
        <div class="menu-link">
        <a href="menu_client.php">Retour au menu</a>
        </div>
    </form>
  <?php endif; ?>

</body>
</html>
