# TelEtCommande

**TelEtCommande** est une interface web ergonomique conçue pour contrôler à distance un PC (clavier, souris, multimédia) depuis un smartphone ou un autre appareil, de manière sécurisée à travers votre réseau Tailscale.

---

## 🚀 Configuration & Installation

### 1. Sur la machine cible (PC à contrôler)

Installez les dépendances Python requises :

```bash
pip install pyautogui flask
```

Lancez ensuite le serveur d'écoute sur la machine cible :

```bash
python3 main.py
```

*Le serveur s'exécutera sur le port **5000** et acceptera les commandes émises depuis votre réseau Tailscale.*

---

## 📱 Utilisation de la Télécommande Web

1. Ouvrez la page web `TelEtCommande.html` dans un navigateur sur votre smartphone ou votre tablette.
2. Saisissez l'adresse **IP Tailscale** de la machine cible dans le champ prévu à cet effet (ex: `100.x.x.x`).
3. Interagissez avec les boutons de l'interface pour contrôler votre PC à distance.

---

## 🎮 Interface & Fonctionnalités

L'interface de la télécommande est organisée de manière ergonomique pour une utilisation facile à une main :

* **Gros bouton circulaire (Haut)** : Clic principal de la souris (`click`).
* **Pavé directionnel central (T inversé)** : Flèches de navigation (`▲`, `▼`, `◀`, `▶`).
* **Contrôles du son (Flanquant le haut du pavé)** : Boutons de volume rapide (`🔊 V -` et `🔊 V +`).
* **Barre d'actions rapides (Bas)** : 4 boutons dédiés (`ÉCHAP`, `TAB ➔`, `⬅ TAB`, `ENTRÉE`).

---

## 🔒 Endpoints API

Le serveur Flask écoute sur les requêtes `GET` ou `POST` sous la structure suivante :

```text
http://<IP_TAILSCALE>:5000/press/<action_type>
```

**Actions supportées :**
`click`, `up`, `down`, `left`, `right`, `volumedown`, `volumeup`, `escape`, `tab`, `shift-tab`, `enter`.