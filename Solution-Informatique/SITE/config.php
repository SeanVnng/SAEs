<?php

$dsn = "pgsql:host=localhost;port=5432;dbname=ipam";
$user = 'sean'; #N'oubliez pas de changer avec votre propre USER
$password = 'sean'; #N'oubliez pas de changer avec votre propre MDP

try {
    $pdo = new PDO($dsn, $user, $password);
} catch (PDOException $e) {
    echo "Erreur de conneixon à la base de données : ". $e->getMessage();
}
?>


