<?php
require_once 'config.php';
session_start();

if (!isset($_SESSION['idclient'])) {
    header("Location: connexion.php");
    exit();
}

$isAdmin = $_SESSION['admin'];
$idclient = $_SESSION['idclient'];

$nomRecherche = $_GET['recherche'] ?? '';
$siteFiltre = $_GET['site'] ?? '';
$statutFiltre = $_GET['statut'] ?? '';

try {
    $query = "
        SELECT 
            c.nomclient, c.prenomclient, c.email,
            s.nomsite,
            sr.ipreseau, sr.masque, sr.ipinterface, sr.statut,
            v.numvlan, v.nomvrf, v.rd
        FROM client c
        LEFT JOIN site s ON c.idsite = s.idsite
        LEFT JOIN sousreseau sr ON c.idclient = sr.idclient
        LEFT JOIN vlan v ON c.idclient = v.idclient
    ";

    $conditions = [];
    $params = [];

    if (!$isAdmin) {
        $conditions[] = "c.idclient = ?";
        $params[] = $idclient;
    } else {
        if (!empty($nomRecherche)) {
            $conditions[] = "(LOWER(c.nomclient) LIKE LOWER(?) OR c.idclient = ?)";
            $params[] = "%$nomRecherche%";
            $params[] = (int)$nomRecherche;
        }

        if (!empty($siteFiltre)) {
            $conditions[] = "s.nomsite = ?";
            $params[] = $siteFiltre;
        }

        if (!empty($statutFiltre)) {
            $conditions[] = "sr.statut = ?";
            $params[] = $statutFiltre;
        }
    }

    if ($conditions) {
        $query .= " WHERE " . implode(" AND ", $conditions);
    }

    $query .= " ORDER BY c.idclient";
    $stmt = $pdo->prepare($query);
    $stmt->execute($params);

    $clients = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Erreur : " . $e->getMessage());
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Visualisation des Clients</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      background-color: #121212;
      color: #f5f5f5;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      padding: 40px;
    }

    h1 {
      text-align: center;
      margin-bottom: 20px;
    }

    form {
      text-align: center;
      margin-bottom: 20px;
    }

    input, select {
      padding: 8px;
      margin: 0 10px;
      border-radius: 5px;
      border: none;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      background-color: #1e1e1e;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
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

    .back {
      display: block;
      margin: 30px auto;
      text-align: center;
      padding: 10px 20px;
      background-color: #444;
      border-radius: 6px;
      color: white;
      text-decoration: none;
      width: fit-content;
    }

    .back:hover {
      background-color: #555;
    }
  </style>
</head>
<body>
  <h1>Liste des Clients</h1>

  <?php if ($isAdmin): ?>
    <form method="get">
      <input type="text" name="recherche" placeholder="Recherche par nom ou ID..." value="<?= htmlspecialchars($nomRecherche) ?>">
      <select name="site">
        <option value="">-- Tous les sites --</option>
        <option value="Paris" <?= $siteFiltre === 'Paris' ? 'selected' : '' ?>>Paris</option>
      </select>
      <select name="statut">
        <option value="">-- Tous les statuts --</option>
        <option value="attribué" <?= $statutFiltre === 'attribué' ? 'selected' : '' ?>>Attribué</option>
        <option value="réservé" <?= $statutFiltre === 'réservé' ? 'selected' : '' ?>>Réservé</option>
        <option value="libre" <?= $statutFiltre === 'libre' ? 'selected' : '' ?>>Libre</option>
      </select>
      <input type="submit" value="Filtrer">
    </form>
  <?php endif; ?>

  <table>
    <thead>
      <tr>
        <th>Nom</th>
        <th>Prénom</th>
        <th>Email</th>
        <th>Site</th>
        <th>VLAN</th>
        <th>VRF</th>
        <th>RD</th>
        <th>IP Réseau</th>
        <th>Masque</th>
        <th>IP Interface</th>
        <th>Statut</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($clients as $client): ?>
        <tr>
          <td><?= htmlspecialchars($client['nomclient']) ?></td>
          <td><?= htmlspecialchars($client['prenomclient']) ?></td>
          <td><?= htmlspecialchars($client['email']) ?></td>
          <td><?= htmlspecialchars($client['nomsite']) ?></td>
          <td><?= htmlspecialchars($client['numvlan']) ?></td>
          <td><?= htmlspecialchars($client['nomvrf']) ?></td>
          <td><?= htmlspecialchars($client['rd']) ?></td>
          <td><?= htmlspecialchars($client['ipreseau']) ?></td>
          <td>/<?= htmlspecialchars($client['masque']) ?></td>
          <td><?= htmlspecialchars($client['ipinterface']) ?></td>
          <td><?= htmlspecialchars($client['statut']) ?></td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>

  <a href="<?= $isAdmin ? 'menu.php' : 'menu_client.php' ?>" class="back"> Retour au menu</a>
</body>
</html>
