<?php
require_once 'config.php';

$stmt = $pdo->query("
    SELECT c.idclient, c.nomclient, sr.ipinterface
    FROM client c
    LEFT JOIN sousreseau sr ON c.idclient = sr.idclient
");

while ($client = $stmt->fetch(PDO::FETCH_ASSOC)) {
    $id      = $client['idclient'];
    $nom     = strtoupper($client['nomclient']);
    $iface   = "eth0.$id";
    $ip      = $client['ipinterface'];
    $mask    = "24"; # Toujours /24 !!!
    $vlan_id = $id;
    $vrf     = $nom;
    $table   = 10000 + $id;

    $contenu = <<<BASH
#!/bin/bash

echo "Configuration du client $nom"

# Création de la sous-interface
ip link add link eth0 name $iface type vlan id $vlan_id

# Attribution IP
ip addr add $ip/$mask dev $iface

# Activation de l’interface
ip link set dev $iface up

# VRF (facultatif)
ip link add $vrf type vrf table $table
ip link set dev $iface master $vrf
ip link set $vrf up

echo "Client $nom configuré avec $iface (IP $ip/$mask)✅"
BASH;

    $filename = "config_client_{$nom}.sh";
    file_put_contents($filename, $contenu);
    chmod($filename, 0755);
}

echo "Tous les fichiers de configuration ont été générés.";
?>
