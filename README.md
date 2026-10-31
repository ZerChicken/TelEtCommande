# TelEtCommande

TelEtCommande est une interface web ergonomique conçue pour contrôler à distance un PC (clavier, souris, multimédia) depuis un smartphone ou un autre appareil, de manière sécurisée à travers votre réseau Tailscale.

Ce projet est un projet uniquement web codé par Gemini.

---

## Configuration et Installation

### 1. Sur la machine cible (PC à contrôler)

Installez les dépendances Python requises :

```bash
pip install pyautogui flask
```
Lancez ensuite le serveur d'écoute sur la machine cible :
```bash
python3 main.py
```
Le serveur s'exécutera sur le port 5000 et acceptera les commandes émises depuis votre réseau Tailscale.

## Utilisation de la Télécommande Web
1. Ouvrez la page web TelEtCommande.html dans un navigateur sur votre smartphone ou votre tablette.

2. Sélectionnez le preset (1 à 4), modifiez son nom si besoin, et renseignez l'adresse IP de la machine cible.

3. Interagissez avec les boutons de l'interface pour contrôler votre PC à distance.

## Interface et Fonctionnalités

* L'interface de la télécommande est organisée de manière ergonomique :

* Gros bouton circulaire : Clic principal de la souris.

* Joystick tactile : Déplacement analogique de la souris.

* Contrôles du volume et mode silencieux.

* Raccourcis web dynamiques (YouTube, Google, etc.).

* Raccourcis de navigation et système (Plein écran avec la touche F, défilement haut/bas, entrée, fermeture d'onglet, mise en veille).

* Joystick tactile : Déplacement analogique ultra-fluide et réactif de la souris (avec accumulateur anti-perte de paquets).

## Endpoints API

## Endpoints API

Le serveur Flask écoute sur les requêtes et endpoints suivants :

* **`/press/<action_type>`** (GET, POST) : Exécute une touche ou une action clavier/système (ex: `fullscreen`, `space`, `volumeup`, `click`, etc.).
* **`/move`** (POST) : Déplace le curseur de la souris de manière relative (`dx`, `dy`).
* **`/type`** (POST) : Simule la saisie d'une chaîne de caractères (`text`).
* **`/open-url`** (POST) : Ouvre une URL spécifique dans le navigateur de la machine distante (`url`).

Exemple de structure d'appel :
```Plaintext
http://<IP_TAILSCALE>:5000/press/fullscreen
```