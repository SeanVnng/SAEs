# 🌐 GreenHome Network Infrastructure - SAE 21

![Cisco](https://img.shields.io/badge/Cisco-Packet%20Tracer-blue?style=for-the-badge&logo=cisco)
![Windows Server](https://img.shields.io/badge/Server-Windows%20Server-orange?style=for-the-badge&logo=windows)
![pfSense](https://img.shields.io/badge/Security-pfSense-red?style=for-the-badge&logo=pfsense)
![Status](https://img.shields.io/badge/Status-Validé-success?style=for-the-badge)

**GreenHome Solutions Network** est un projet d'infrastructure complet réalisé dans le cadre de la **SAE 21** à l'IUT Sorbonne Nord. Il simule le déploiement d'un réseau d'entreprise multisite sécurisé reliant le siège administratif (Lyon) et l'unité de production (Grenoble).

Ce projet intègre la conception logique (VLANs, adressage), le déploiement des services critiques (DNS, DHCP, AD) et la sécurisation périmétrique (Pare-feu, ACL).

---

## ✨ Fonctionnalités & Architecture

* **📡 Architecture Réseau Avancée :**
    * **Multisite :** Interconnexion simulée entre Lyon et Grenoble.
    * **Segmentation VLAN :** Cloisonnement strict des services via 5 VLANs distincts (RH, Informatique, Sécurité, Commerce, Direction).
    * **Routage Inter-VLAN :** Configuration "Router-on-a-Stick" via sous-interfaces (Encapsulation dot1Q).
* **⚙️ Services Systèmes (Windows Server) :**
    * **Active Directory (AD DS) :** Gestion centralisée des utilisateurs et des ordinateurs du domaine `sae21.local`.
    * **DNS & DHCP :** Résolution de noms interne et attribution dynamique des IP.
    * **Serveur Web (IIS) :** Hébergement d'un intranet accessible via l'alias `www.sae21.fr`.
* **🛡️ Sécurité & Filtrage :**
    * **Pare-feu pfSense :** Gestion des flux entrants/sortants et isolation via interfaces LAN/WAN.
    * **NAT/PAT :** Traduction d'adresses pour l'accès Internet sécurisé.
    * **ACLs :** Règles de filtrage strictes (ex: blocage ICMP entre zones sensibles).

---

## 🏗️ Structure des VLANs

Le réseau est segmenté pour optimiser la sécurité et la performance :

| ID VLAN | Nom du Service | Description |
| :---: | :--- | :--- |
| **10** | RH | Ressources Humaines |
| **20** | Informatique | Service IT & Administration |
| **30** | Securite | Vidéosurveillance & Contrôle d'accès |
| **40** | Commerce | Ventes & Marketing |
| **50** | Direction | Management & Stratégie |

---

## 🚀 Installation & Utilisation

### Prérequis
* **Cisco Packet Tracer** (Version 8.0 ou supérieure recommandée).
* Un environnement compatible (Windows/Linux/macOS).

### Lancement de la simulation
1.  **Cloner ou télécharger** ce dépôt.
2.  **Lancer Cisco Packet Tracer**.
3.  **Ouvrir le fichier** `Réseau.pkt`.
4.  **Explorer** : Vous pouvez naviguer entre le site de Lyon et Grenoble, ouvrir les terminaux des PC pour lancer des `ping` ou inspecter les configurations des routeurs/switchs (CLI).

---

## 🧪 Tests de Validation

Le projet a été validé par une batterie de tests unitaires et d'intégration :

* ✅ **T001** : Ping Intra-VLAN (Même switch).
* ✅ **T003** : Ping Intra-VLAN (Traversée de Trunk).
* ✅ **T005** : Ping Inter-Sites (Lyon ↔ Grenoble).
* 🔒 **T002/T004** : Validation du cloisonnement (Échec de ping entre VLANs non autorisés).

---

## 👥 Équipe Projet

Projet réalisé par l'équipe **SAE 21 - IUT Sorbonne Nord (2024-2025)** :

* 🔴 **Chef de Projet ** 
* 🟢 **Architecte Réseau ** 
* 🔵 **Admin Systèmes ** 
* 🟡 **Technicien Sécurité ** 
* 🟣 **Testeur / Qualité ** 

---
*Basé sur le rapport technique `SAE21-Reseau-Informatique.pdf` inclus dans ce dépôt.*
