# 🛡️ CYBER OPS ANALYZER - SAE 15 Project

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![HTML5](https://img.shields.io/badge/Report-HTML5-orange?style=for-the-badge&logo=html5)
![Data](https://img.shields.io/badge/Data-CSV-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

**CYBER OPS ANALYZER** est un outil de traitement de données développé dans le cadre de la **SAE 15**. Il ne se contente pas de lire des données brutes : **il les transforme en intelligence visuelle**. Le script analyse un jeu de données complexe d'incidents de cybersécurité et génère automatiquement un rapport web interactif et lisible.

---

## ✨ Fonctionnalités Principales

* **📊 Analyse de Données Brutes :**
    * **Parsing CSV :** Lecture optimisée du fichier source `cyber-operations-incidents.csv`.
    * **Nettoyage :** Traitement des entrées, gestion des dates et catégorisation des types d'attaques.
* **🌐 Génération de Rapport Web :**
    * **Moteur de Template :** Création automatique du fichier `cyber_operations_site.html` sans framework lourd.
    * **Design Intégré :** Le CSS est généré dynamiquement par le script Python pour un rendu immédiat.
* **⚡ Performance & Légèreté :**
    * **Zéro Dépendance :** Utilisation exclusive des librairies standards Python (`csv`, `datetime`, etc.).
    * **Portabilité :** Fonctionne sur n'importe quelle machine disposant de Python, sans installation complexe.
* **📈 Visualisation :**
    * Restitution des statistiques clés sur les cyber-opérations.
    * Classement et filtrage des incidents majeurs.

---

## ⚙️ Prérequis

Avant de commencer, assurez-vous d'avoir :

* **Python 3.x** installé sur votre machine.
* Un **Navigateur Web** moderne (Chrome, Firefox, Edge) pour visualiser le rapport.
* Le fichier de données `cyber-operations-incidents.csv` présent dans le dossier.

---

## 🚀 Installation

1.  **Télécharger le projet :**
    Assurez-vous d'avoir les trois fichiers essentiels dans le même dossier :
    * `generate_site.py`
    * `cyber-operations-incidents.csv`
    * `cyber_operations_site.html` (sera regénéré)

2.  **Créer un environnement virtuel (Optionnel) :**
    Comme le projet n'utilise pas de bibliothèques externes lourdes, cette étape est facultative mais recommandée pour la propreté.
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Dépendances :**
    Ce projet est conçu pour être **"Plug & Play"**. Aucune installation via `pip` n'est nécessaire si vous utilisez une installation Python standard. Les modules utilisés (`csv`, `os`, `datetime`) sont natifs.

---

## 🎮 Utilisation

### Lancer la génération du rapport
C'est la commande principale qui va lire les données et construire le site web.

```bash
python generate_site.py

Projet SAE15/
├── generate_site.py               # 🧠 Le Cerveau : Script de traitement et génération
├── cyber-operations-incidents.csv # 💾 La Source : Données brutes de cybersécurité
└── cyber_operations_site.html     # 🖥️ Le Rendu : Interface web finale générée

Réalisé par Seann
