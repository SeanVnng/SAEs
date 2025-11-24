<?php
require_once 'config.php';
session_start();

# Sécurité : accès réservé aux administrateurs 
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

$success = $error = "";

# Suppression des clients sélectionnés
if ($_SERVER["REQUEST_METHOD"] === "POST" && !empty($_POST['clients'])) {
    $ids = $_POST['clients'];

    try {
        $pdo->beginTransaction();

        foreach ($ids as $id) {
            # 1. Nettoyer les ressources réseau 
            $pdo->prepare("DELETE FROM sousreseau WHERE idclient = ?")->execute([$id]);
            $pdo->prepare("DELETE FROM vlan       WHERE idclient = ?")->execute([$id]);

            # 2. Supprimer le client 
            $pdo->prepare("DELETE FROM client     WHERE idclient = ?")->execute([$id]);

            # 3. Supprimer le fichier de configuration s’il existe 
            $file = __DIR__ . "/exports/conf_client_$id.txt";   # <-- chemin corrigé
            if (file_exists($file)) {
                unlink($file);
            }
        }

        $pdo->commit();
        $success = "✅ Clients supprimés avec succès.";
    } catch (PDOException $e) {
        $pdo->rollBack();
        $error = "Erreur : " . $e->getMessage();
    }
}

#Récupération des clients non-admin 
$stmt    = $pdo->query("SELECT idclient, nomclient, prenomclient, email
                        FROM client
                        WHERE admin = false
                        ORDER BY nomclient");
$clients = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Supprimer des clients</title>
  <style>
    body{
      background:#121212;color:#f5f5f5;font-family:sans-serif;
      display:flex;justify-content:center;align-items:center;min-height:100vh;
      flex-direction:column;margin:0;
    }
    .box{
      background:#1e1e1e;padding:30px;border-radius:10px;
      max-width:600px;width:100%;box-shadow:0 0 12px rgba(0,0,0,.5);
    }
    h1{margin:0 0 25px;text-align:center}
    h2{margin:0 0 15px;text-align:center}
    form label{display:block;text-align:left;margin:6px 0}
    input[type=submit]{
      margin-top:20px;padding:10px;border:0;border-radius:5px;
      background:#aa3333;color:#fff;font-weight:bold;cursor:pointer;width:100%;
    }
    .success{color:limegreen;margin-bottom:15px;text-align:center}
    .error{color:red;margin-bottom:15px;text-align:center}
    a{margin-top:25px;color:#ccc;text-decoration:underline}
  </style>
</head>
<body>
  <h1>Supprimer des clients</h1>

  <?php if ($success): ?><p class="success"><?= $success ?></p><?php endif; ?>
  <?php if ($error):   ?><p class="error"><?= $error   ?></p><?php endif; ?>

  <?php if (empty($clients)): ?>
      <p>Aucun client à supprimer.</p>
  <?php else: ?>
    <div class="box">
      <form method="post">
        <h2>Sélectionnez les clients</h2>
        <?php foreach ($clients as $c): ?>
          <label>
            <input type="checkbox" name="clients[]" value="<?= $c['idclient'] ?>">
            <?= htmlspecialchars("{$c['prenomclient']} {$c['nomclient']} — {$c['email']}") ?>
          </label>
        <?php endforeach; ?>
        <input type="submit" value="Supprimer les clients sélectionnés">
      </form>
    </div>
  <?php endif; ?>

  <a href="menu.php">Retour au menu admin</a>
</body>
</html>
