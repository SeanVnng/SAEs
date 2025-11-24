README — Projet SAE15

🇫🇷 Présentation

Ce projet génère une page HTML récapitulant des incidents de cybersécurité à partir d’un fichier CSV.

Il se compose de :
-cyber-operations-incidents.csv : les données d’incidents
-generate_site.py : le script Python qui lit le CSV et produit la page HTML
-cyber_operations_site.html : la page HTML générée

Prérequis
Python 3.x
Bibliothèques Python standards (aucune installation supplémentaire requise si le script n’utilise que csv/html)

Utilisation
1. Placez generate_site.py et cyber-operations-incidents.csv dans le même dossier.
2. Ouvrez un terminal dans ce dossier.
3. Lancez :
python generate_site.py
4. Le fichier cyber_operations_site.html sera créé ou mis à jour.
5. Ouvrez ce fichier dans votre navigateur.

Projet_SAE15/

  ├── cyber-operations-incidents.csv   # Données source

  ├── generate_site.py                 # Script de génération

  └── cyber_operations_site.html       # Sortie HTML

