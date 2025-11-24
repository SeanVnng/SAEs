<?php
require_once 'config.php';
session_start();

# Sécurité : utilisateur connecté requis
if (!isset($_SESSION['idclient'])) {
    header("Location: connexion.php");
    exit();
}

# Étape d'affichage (1=demande nb IP, 2=confirmation)
$succes = $erreur = "";
$etape = 1;

if ($_SERVER["REQUEST_METHOD"] === "POST") {

    /* Génération des adresses libres */
    if (isset($_POST['generer'])) {
      $nb_ip = (int)$_POST['nb_ip'];
      
      # Validation : entre 1 et 50 adresses maximum
      if ($nb_ip < 1 || $nb_ip > 50) {
          $erreur = "Le nombre d'adresses doit être entre 1 et 50.";
      } else {
          $base_prefix = "164.166.1.";
          
          # Récupération de toutes les IP déjà utilisées en base
          $used = $pdo->query("SELECT ipreseau FROM sousreseau")
                        ->fetchAll(PDO::FETCH_COLUMN);
          
          $dispo = [];
          
          # Parcours de 164.166.1.1 à 164.166.1.255 pour trouver les IP libres
          for ($i = 1; $i <= 255 && count($dispo) < $nb_ip; $i++) {
              $ip = $base_prefix . $i;
              if (!in_array($ip, $used, true)) {
                  $dispo[] = $ip;
              }
          }
          
          # Vérification qu'on a assez d'IP disponibles
          if (count($dispo) < $nb_ip) {
              $erreur = "Pas assez d'adresses IP disponibles.";
          } else {
              # Stockage des IP disponibles en session pour l'étape suivante
              $_SESSION['dispo_ip'] = $dispo;
              $etape = 2;
          }
      }
    }

    if (isset($_POST['confirmer'])) {
        $id_client = $_SESSION['idclient'];
        $nom_vrf   = strtoupper($_SESSION['nomclient']);
        $rd_base   = "65556:";
        $dispo     = $_SESSION['dispo_ip'];
        $statuts   = $_POST['statuts'];

        try {
            $verif = $pdo->prepare("SELECT COUNT(*) FROM vlan WHERE idclient = ?");
            $verif->execute([$id_client]);
            if ($verif->fetchColumn() == 0) {
                $numvlan = $id_client;
                $rd      = $rd_base . $numvlan;
                $pdo->prepare(
                    "INSERT INTO vlan (numvlan, nomvrf, rd, idclient) VALUES (?,?,?,?)"
                )->execute([$numvlan, $nom_vrf, $rd, $id_client]);
            }

            $ins_sr = $pdo->prepare(
                "INSERT INTO sousreseau (ipreseau, masque, ipinterface, statut, idclient) VALUES (?, 24, ?, ?, ?)"
            );
            foreach ($dispo as $idx => $ip) {
                $ip_interface = preg_replace('/\.0$/', '.1', $ip);
                $statut = $statuts[$idx] ?? 'attribué';
                $ins_sr->execute([$ip, $ip_interface, $statut, $id_client]);
            }

            $requete = $pdo->prepare("SELECT c.nomclient, c.prenomclient, c.email, s.nomsite FROM client c JOIN site s ON c.idsite = s.idsite WHERE c.idclient = ?");
            $requete->execute([$id_client]);
            $infos = $requete->fetch(PDO::FETCH_ASSOC);

            if (!is_dir('exports')) mkdir('exports', 0777, true);
            $chemin_fichier = "exports/config_client_{$id_client}.txt";
            $fichier = fopen($chemin_fichier, 'w');
            fwrite($fichier, "Client n°{$id_client}\nNom : {$infos['nomclient']}\nPrénom : {$infos['prenomclient']}\nEmail : {$infos['email']}\nSite : {$infos['nomsite']}\nNombre d'IP : ".count($dispo)."\n\n");

// Remplacez tout le bloc d'écriture du fichier par :
$contenu_fichier = "Client n°{$id_client}\nNom : {$infos['nomclient']}\nPrénom : {$infos['prenomclient']}\nEmail 
: {$infos['email']}\nSite : {$infos['nomsite']}\nNombre d'IP : ".count($dispo)."\n\n";

foreach ($dispo as $idx => $ip) {
    $ip_interface = preg_replace('/\.0$/', '.1', $ip);
    $statut = $statuts[$idx] ?? 'attribué';
    $contenu_fichier .= "--- IP ".($idx+1)." ---\n";
    $contenu_fichier .= "IP réseau   : $ip/24\n";
    $contenu_fichier .= "IP interface: $ip_interface\n";
    $contenu_fichier .= "Statut      : $statut\n\n";
}

file_put_contents($chemin_fichier, $contenu_fichier);

            $succes = "Configuration enregistrée avec succès. Fichier créé : $chemin_fichier";
            unset($_SESSION['dispo_ip']);
            $etape = 1;
        } catch (PDOException $e) {
            $erreur = "Erreur : ".$e->getMessage();
        }

        if (!is_dir("logs")) mkdir("logs", 0755, true);
        $nb_ip = count($dispo);
        $message_log = "[" . date('Y-m-d H:i:s') . "] AJOUT - {$_SESSION['nomclient']} ({$_SESSION['email']}) a ajouté $nb_ip IP(s).\n";
        file_put_contents("logs/historique_ip.txt", $message_log, FILE_APPEND);
    }
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Ajout d'Adresses IP</title>
  <style>
    body { font-family: sans-serif; background:#121212; color:#f5f5f5; padding:40px; text-align:center; }
    form { background:#1e1e1e; padding:30px; border-radius:8px; max-width:500px; margin:20px auto; }
    input, select, button { width:100%; padding:10px; margin:10px 0; border:none; border-radius:5px; }
    button { background:#33aaff; color:white; font-weight:bold; cursor:pointer; }
    .error { color:red; }
    .success { color:limegreen; }
  </style>
</head>
<body>
  <h1>Ajout d'Adresses IP</h1>
  <?php if ($erreur)   echo "<p class='error'>$erreur</p>"; ?>
  <?php if ($succes) echo "<p class='success'>$succes</p>"; ?>

  <?php if ($etape === 1): ?>
    <form method="post">
      <label>Combien d'adresses IP souhaitez-vous ? (1-50)</label>
      <input type="number" name="nb_ip" min="1" max="50" required>
      <button type="submit" name="generer">Générer</button>
      <a href="menu_client.php" style="display:block;margin-top:15px;color:#aaa;text-decoration:underline;"> Retour au menu</a>
    </form>
  <?php elseif ($etape === 2): ?>
    <form method="post">
      <h3>Récapitulatif</h3>
      <ul style="list-style:none;padding:0;text-align:left;max-width:400px;margin:auto;">
        <?php foreach ($_SESSION['dispo_ip'] as $idx => $ip): ?>
          <li>
            → <?= htmlspecialchars($ip) ?>/24
            <select name="statuts[]">
              <option value="libre">Libre</option>
              <option value="réservé">Réservé</option>
              <option value="attribué" selected>Alloué</option>
            </select>
          </li>
        <?php endforeach; ?>
      </ul>
      <button type="submit" name="confirmer">Confirmer l'ajout ?</button>
      <a href="ajout.php" style="display:inline-block;margin-top:10px;color:#aaa;text-decoration:underline;">Annuler</a>
    </form>
  <?php endif; ?>
</body>
</html>