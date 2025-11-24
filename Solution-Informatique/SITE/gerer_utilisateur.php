<?php
require_once 'config.php';
session_start();

# Accès admin uniquement
if (!isset($_SESSION['admin']) || $_SESSION['admin'] !== true) {
    header("Location: connexion.php");
    exit;
}

function mettreAJourFichierConf($pdo, $id) {
    $stmt = $pdo->prepare("SELECT * FROM client WHERE idclient = ?");
    $stmt->execute([$id]);
    $client = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$client) return;

    $nom = $client['nomclient'];
    $prenom = $client['prenomclient'];
    $email = $client['email'];
    $site = $client['idsite'];
    $role = $client['admin'] ? 'Administrateur' : 'Client';

    $stmt = $pdo->prepare("SELECT ipreseau, masque, ipinterface, statut FROM sousreseau WHERE idclient = ?");
    $stmt->execute([$id]);
    $ips = $stmt->fetchAll(PDO::FETCH_ASSOC);

    $stmt = $pdo->prepare("SELECT numvlan, nomvrf, rd FROM vlan WHERE idclient = ?");
    $stmt->execute([$id]);
    $vlan = $stmt->fetch(PDO::FETCH_ASSOC);

    $contenu = "Nom : $nom\nPrénom : $prenom\nEmail : $email\nSite : $site\nRôle : $role\n";
    $contenu .= "Nombre d'IP : " . count($ips) . "\n\n";

    foreach ($ips as $ip) {
        $contenu .= "IP : {$ip['ipreseau']}/{$ip['masque']} → Interface : {$ip['ipinterface']} → Statut : {$ip['statut']}\n";
    }

    if ($vlan) {
        $contenu .= "\nVLAN : {$vlan['numvlan']}\nVRF : {$vlan['nomvrf']}\nRD : {$vlan['rd']}\n";
    }

    file_put_contents("exports/config_client_$id.txt", $contenu);
}

$id = $_GET['id'] ?? null;
if (!$id) {
    header("Location: utilisateurs.php");
    exit;
}

$success = $error = "";
$etape = 1; // 1 = demande nb IP, 2 = confirmation avec choix statuts

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    # Génération des IP disponibles
    if (isset($_POST['generer_ip'])) {
        $nb_ip = (int)$_POST['nb_ip'];
        if ($nb_ip < 1 || $nb_ip > 50) {
            $error = "Le nombre d'adresses doit être entre 1 et 50.";
        } else {
            $base_prefix = "164.166.1.";
            $used = $pdo->query("SELECT ipreseau FROM sousreseau")->fetchAll(PDO::FETCH_COLUMN);

            $dispo = [];
            for ($i = 1; $i <= 255 && count($dispo) < $nb_ip; $i++) {
                $ip = $base_prefix . $i;
                if (!in_array($ip, $used)) {
                    $dispo[] = $ip;
                }
            }

            if (count($dispo) < $nb_ip) {
                $error = "Pas assez d'adresses IP disponibles.";
            } else {
                $_SESSION['dispo_ip_admin'] = $dispo;
                $_SESSION['id_client_admin'] = $id;
                $etape = 2;
            }
        }
    }

    # Confirmation et ajout des IP avec statuts
    if (isset($_POST['confirmer_ajout'])) {
        $dispo = $_SESSION['dispo_ip_admin'] ?? [];
        $statuts = $_POST['statuts'] ?? [];
        $id = $_SESSION['id_client_admin'];

        if (empty($dispo)) {
            $error = "Aucune IP à ajouter.";
        } else {
            try {
                $client = $pdo->prepare("SELECT * FROM client WHERE idclient = ?");
                $client->execute([$id]);
                $c = $client->fetch();

                $nom = strtoupper($c['nomclient']);
                $rd_base = "65556:";

                # Vérifie si un VLAN a déjà été attribué
                $stmt = $pdo->prepare("SELECT COUNT(*) FROM vlan WHERE idclient = ?");
                $stmt->execute([$id]);
                $hasVlan = $stmt->fetchColumn();

                if ($hasVlan == 0) {
                    $vlan = $id;
                    $rd = $rd_base . $id;
                    $pdo->prepare("INSERT INTO vlan (numvlan, nomvrf, rd, idclient) VALUES (?, ?, ?, ?)")
                        ->execute([$vlan, $nom, $rd, $id]);
                }

                foreach ($dispo as $idx => $ip) {
                    $ip_interface = preg_replace("/\.0$/", ".1", $ip);
                    $statut = $statuts[$idx] ?? 'attribué';
                    $pdo->prepare("INSERT INTO sousreseau (ipreseau, masque, ipinterface, statut, idclient) VALUES (?, 24, ?, ?, ?)")
                        ->execute([$ip, $ip_interface, $statut, $id]);
                }

                mettreAJourFichierConf($pdo, $id);
                unset($_SESSION['dispo_ip_admin'], $_SESSION['id_client_admin']);
                header("Location: gerer_utilisateur.php?id=$id&ajout=ok");
                exit;

            } catch (PDOException $e) {
                $error = "Erreur : " . $e->getMessage();
            }
        }
    }

    # Suppression IP
    if (!empty($_POST['ips_a_supprimer'])) {
        try {
            $stmt = $pdo->prepare("DELETE FROM sousreseau WHERE idclient = ? AND ipreseau = ?");
            foreach ($_POST['ips_a_supprimer'] as $ip) {
                $stmt->execute([$id, $ip]);
            }

            mettreAJourFichierConf($pdo, $id);
            header("Location: gerer_utilisateur.php?id=$id&suppression=ok");
            exit;
        } catch (PDOException $e) {
            $error = "Erreur : " . $e->getMessage();
        }
    }
}

# Vérification des sessions pour l'étape 2
if (isset($_SESSION['dispo_ip_admin']) && isset($_SESSION['id_client_admin'])) {
    $etape = 2;
}

if (isset($_GET['ajout']) && $_GET['ajout'] === 'ok') {
    $success = "IP(s) ajoutée(s) avec succès.";
}
if (isset($_GET['suppression']) && $_GET['suppression'] === 'ok') {
    $success = "IP(s) supprimée(s) avec succès.";
}

$stmt = $pdo->prepare("SELECT * FROM sousreseau WHERE idclient = ?");
$stmt->execute([$id]);
$ips = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Gérer les IP</title>
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

    .container {
      background: #1e1e1e;
      padding: 30px;
      border-radius: 12px;
      max-width: 600px;
      width: 100%;
      text-align: center;
    }

    h2 {
      margin-bottom: 20px;
    }

    form {
      text-align: left;
      margin-top: 20px;
    }

    label {
      display: block;
      margin: 10px 0;
    }

    input[type="number"], input[type="submit"], select {
      width: 100%;
      padding: 10px;
      margin: 10px 0;
      border-radius: 5px;
      border: none;
      font-weight: bold;
    }

    input[type="submit"] {
      background-color: #33aaff;
      color: white;
      cursor: pointer;
    }

    .success {
      color: limegreen;
      margin-bottom: 15px;
    }

    .error {
      color: red;
      margin-bottom: 15px;
    }

    a {
      color: #ccc;
      text-decoration: underline;
      display: block;
      margin-top: 20px;
    }

    .ip-list {
      list-style: none;
      padding: 0;
      text-align: left;
      max-width: 500px;
      margin: auto;
    }

    .ip-list li {
      margin: 15px 0;
      padding: 10px;
      background: #2a2a2a;
      border-radius: 5px;
    }

    .ip-list select {
      margin-top: 5px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Gérer les IP de l'utilisateur #<?= htmlspecialchars($id) ?></h2>

    <?php if ($success) echo "<p class='success'>$success</p>"; ?>
    <?php if ($error) echo "<p class='error'>$error</p>"; ?>

    <?php if ($etape === 1): ?>
      <form method="post">
        <label for="nb_ip">Nombre d'adresses IP à ajouter :</label>
        <input type="number" name="nb_ip" min="1" max="50" required>
        <input type="submit" name="generer_ip" value="➕ Générer les IP">
      </form>
    <?php elseif ($etape === 2): ?>
      <form method="post">
        <h3>Récapitulatif - Choisissez le statut pour chaque IP :</h3>
        <ul class="ip-list">
          <?php foreach ($_SESSION['dispo_ip_admin'] as $idx => $ip): ?>
            <li>
              <strong>→ <?= htmlspecialchars($ip) ?>/24</strong>
              <select name="statuts[]">
                <option value="libre">Libre</option>
                <option value="réservé">Réservé</option>
                <option value="attribué" selected>Attribué</option>
              </select>
            </li>
          <?php endforeach; ?>
        </ul>
        <input type="submit" name="confirmer_ajout" value="Confirmer l'ajout">
        <a href="gerer_utilisateur.php?id=<?= $id ?>" style="color: #aaa; text-decoration: underline; display: inline-block; margin-top: 10px;">❌ Annuler</a>
      </form>
    <?php endif; ?>

    <form method="post">
      <h3>Adresses IP existantes :</h3>
      <?php if (empty($ips)): ?>
        <p>Aucune IP attribuée.</p>
      <?php else: ?>
        <?php foreach ($ips as $row): ?>
          <label>
            <input type="checkbox" name="ips_a_supprimer[]" value="<?= htmlspecialchars($row['ipreseau']) ?>">
            <?= htmlspecialchars($row['ipreseau']) ?>/<?= $row['masque'] ?> 
            <span style="color: <?= $row['statut'] === 'libre' ? '#90EE90' : ($row['statut'] === 'réservé' ? '#FFD700' : '#FF6B6B') ?>;">
              (<?= htmlspecialchars($row['statut']) ?>)
            </span>
          </label>
        <?php endforeach; ?>
        <input type="submit" value="Supprimer les IP sélectionnées">
      <?php endif; ?>
    </form>

    <a href="utilisateur.php">Retour à la liste des utilisateurs</a>
  </div>
</body>
</html>