# 📻 Radio Shazam Downloader

Script Python qui :

1. **joue une webradio** via VLC ;
2. **enregistre quelques secondes du son de ton PC** avec FFmpeg ;
3. **identifie le morceau** avec Shazam (`shazamio`) ;
4. **télécharge le titre en MP3** avec `yt-dlp`, rangé par genre dans `musiques/<genre>/` ;
5. mémorise les titres déjà vus dans `musique_db.json` pour **éviter les doublons**.

> ⚠️ **Windows uniquement** : la capture audio utilise DirectShow (`dshow`).

> ⚖️ **Avis légal** : ce projet est fourni à titre éducatif. Télécharger de la musique protégée par le droit d'auteur peut être illégal dans ton pays et enfreindre les conditions d'utilisation de YouTube. Utilise-le uniquement pour du contenu dont tu as le droit de faire une copie. L'auteur décline toute responsabilité quant à l'usage qui en est fait.

---

## 📋 Sommaire

- [Ce qu'il te faut](#-ce-quil-te-faut)
- [Installation pas à pas (PC sans Python)](#-installation-pas-à-pas-pc-sans-python)
- [Configurer la capture audio (Mixage stéréo)](#-configurer-la-capture-audio-mixage-stéréo)
- [Lancer le script](#-lancer-le-script)
- [Ajouter une radio](#-ajouter-une-radio)
- [Résultats générés](#-résultats-générés)
- [Dépannage](#-dépannage)

---

## 🧰 Ce qu'il te faut

| Outil | Rôle | Version conseillée |
|---|---|---|
| **Python** | Exécute le script | **3.12** (3.13 possible) |
| **VLC media player** | Lit la webradio | 64 bits (comme Python) |
| **FFmpeg** | Enregistre le son du PC et convertit en MP3 | dernière version |
| **Git** | Récupère le projet | dernière version |
| Paquets Python | `python-vlc`, `shazamio`, `yt-dlp` | via `requirements.txt` |

> ❗ **Évite Python 3.14 pour l'instant** : `shazamio` dépend de paquets (`pydantic`, `aiohttp`…) qui n'ont pas toujours de version précompilée pour les toutes dernières versions de Python, ce qui provoque des erreurs d'installation.

---

## 🚀 Installation pas à pas (PC sans Python)

Toutes les commandes se tapent dans **PowerShell** (menu Démarrer → tape `PowerShell`).

### Étape 1 : Installer Python 3.12

1. Va sur <https://www.python.org/downloads/windows/> et télécharge **Python 3.12.x** (Windows installer 64-bit).
2. Lance l'installeur et **coche absolument** la case **« Add python.exe to PATH »** en bas de la première fenêtre.
3. Clique sur **Install Now**.
4. **Ferme et rouvre PowerShell**, puis vérifie :

```powershell
python --version
```

Tu dois voir `Python 3.12.x`. Si Windows ouvre le Microsoft Store ou dit que la commande est introuvable, l'option PATH n'a pas été cochée : relance l'installeur, choisis *Modify* puis coche l'option, ou réinstalle.

### Étape 2 : Installer VLC (64 bits)

1. Télécharge VLC sur <https://www.videolan.org/vlc/> (la version proposée est en 64 bits par défaut).
2. Installe-le avec les options par défaut (dans `C:\Program Files\VideoLAN\VLC`).

> `python-vlc` n'est qu'un « pont » : l'application VLC doit **obligatoirement** être installée, avec la **même architecture** que Python (64 bits avec 64 bits).

### Étape 3 : Installer FFmpeg

Le plus simple est d'utiliser `winget` (inclus dans Windows 10/11) :

```powershell
winget install Gyan.FFmpeg
```

**Ferme et rouvre PowerShell**, puis vérifie :

```powershell
ffmpeg -version
```

Si la commande n'est pas reconnue, FFmpeg n'est pas dans le PATH. Installation manuelle : télécharge un build Windows sur <https://www.gyan.dev/ffmpeg/builds/>, dézippe-le (par ex. dans `C:\ffmpeg`) et ajoute `C:\ffmpeg\bin` à la variable d'environnement `Path` (Paramètres → Système → À propos → Paramètres système avancés → Variables d'environnement).

### Étape 4 : Installer Git

```powershell
winget install Git.Git
```

Ferme et rouvre PowerShell, puis vérifie avec `git --version`.

### Étape 5 : Récupérer le projet

Place-toi dans le dossier où tu ranges tes projets, puis clone le dépôt (remplace l'URL par celle de ton dépôt) :

```powershell
cd $HOME\Documents
git clone https://github.com/TON_PSEUDO/radio-shazam-downloader.git
cd radio-shazam-downloader
```

### Étape 6 : Créer un environnement virtuel

Un environnement virtuel isole les paquets du projet du reste du PC.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Tu dois voir `(.venv)` au début de la ligne du terminal.

> Si PowerShell refuse avec une erreur du type *« l'exécution de scripts est désactivée sur ce système »*, autorise-la pour ton utilisateur puis recommence l'activation :
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### Étape 7 : Installer les dépendances Python

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Étape 8 : (VS Code) Sélectionner le bon interpréteur

Si tu utilises VS Code : `Ctrl + Shift + P` → **Python: Select Interpreter** → choisis celui qui contient `.venv`.

---

## 🎙️ Configurer la capture audio (Mixage stéréo)

Le script enregistre **ce que ton PC joue** (la radio lue par VLC) grâce au périphérique « Mixage stéréo » (*Stereo Mix*).

### 1. Activer le Mixage stéréo

1. `Win + R`, tape `mmsys.cpl`, Entrée.
2. Onglet **Enregistrement**.
3. Clic droit dans la liste → coche **Afficher les périphériques désactivés**.
4. Clic droit sur **Mixage stéréo** → **Activer**.

> Certains PC n'ont pas ce périphérique (selon la carte son et les pilotes). Dans ce cas, installe un câble audio virtuel comme [VB-Cable](https://vb-audio.com/Cable/) et définis-le comme périphérique d'enregistrement (voir ci-dessous).

### 2. Trouver le nom exact du périphérique

```powershell
ffmpeg -list_devices true -f dshow -i dummy
```

Repère dans la liste la ligne « (audio) » correspondante, par exemple :

```
"Mixage stéréo (Realtek(R) Audio)" (audio)
```

### 3. Indiquer ce nom au script

Deux options :

**Option A : variable d'environnement** (sans toucher au code), à refaire à chaque nouvelle session PowerShell :

```powershell
$env:AUDIO_DEVICE = "Mixage stéréo (Realtek(R) Audio)"
```

**Option B : modifier la constante** `AUDIO_DEVICE` en haut de `connect_radio_choix.py`.

---

## ▶️ Lancer le script

Avec l'environnement virtuel activé (`(.venv)` visible) :

```powershell
python connect_radio_choix.py
```

Le script te demande quelle radio jouer. Tape par exemple `europe2` puis Entrée.

Il enregistre ensuite 4 secondes, identifie le morceau, le télécharge s'il est nouveau, puis attend 60 secondes avant de recommencer.

**Arrêter le script** : clique dans le terminal et appuie sur `Ctrl + C`.

> Le son de la radio doit être **audible sur le PC** (volume non coupé, bon périphérique de sortie) pour que le Mixage stéréo le capte.

---

## 📻 Ajouter une radio

Dans `connect_radio_choix.py`, ajoute une ligne au dictionnaire `radios` :

```python
radios = {
    ...
    "ma_radio": "https://exemple.com/flux.mp3",
}
```

Le nom (`ma_radio`) est ce que tu taperas au lancement. L'URL doit être un flux audio lisible par VLC (MP3, AAC, `.pls`, `.m3u`…).

---

## 📦 Résultats générés

| Fichier / dossier | Contenu |
|---|---|
| `musiques/<genre>/` | MP3 téléchargés, triés par genre |
| `musique_db.json` | Liste des morceaux déjà identifiés (anti-doublons) |
| `sample.wav` | Extrait audio temporaire envoyé à Shazam |

Ces éléments sont ignorés par Git (voir `.gitignore`).

---

## 🛠️ Dépannage

| Symptôme | Cause / solution |
|---|---|
| `ModuleNotFoundError: No module named 'vlc'` (ou `shazamio`) | Dépendances non installées, ou mauvais interpréteur. Active `.venv` puis `python -m pip install -r requirements.txt`. |
| `Failed to load libvlc` / `NoneType ... vlc` | VLC absent ou d'architecture différente de Python (32 vs 64 bits). Installe VLC 64 bits. |
| `main libvlc error: stale plugins cache: modified ...` | Message **inoffensif** : le cache de plugins VLC est obsolète. Pour le régénérer, dans PowerShell **administrateur** : `& 'C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe' 'C:\Program Files\VideoLAN\VLC\plugins'`. |
| `ffmpeg est introuvable` | FFmpeg non installé ou pas dans le PATH. Refais l'étape 3 et rouvre le terminal. |
| `Could not find audio only device with name ...` | Mauvais nom de périphérique : refais la section « Trouver le nom exact ». |
| `ERREUR : fichier non créé` | Mixage stéréo désactivé ou nom incorrect. Vérifie la section « Configurer la capture audio ». |
| Échec d'installation de `shazamio` (erreur de compilation, `failed building wheel`) | Tu es probablement sur Python 3.14. Installe Python 3.12 et recrée l'environnement : `py -3.12 -m venv .venv`. |
| Shazam renvoie toujours « Rien trouvé » | Radio trop silencieuse/parlée pendant l'extrait, volume trop bas, ou 4 secondes trop courtes (augmente la durée dans `main()`). |
| Le MP3 n'est pas créé après le téléchargement | FFmpeg manquant (nécessaire à la conversion) ou `yt-dlp` à mettre à jour : `python -m pip install -U yt-dlp`. |
| Le son continue après `Ctrl + C` | Ferme le terminal (icône poubelle dans VS Code). |

---

## 📁 Structure du projet

```
radio-shazam-downloader/
├── connect_radio_choix.py   # Script principal
├── requirements.txt         # Dépendances Python
├── .gitignore               # Fichiers exclus de Git
├── README.md                # Ce fichier
└── PUBLIER_SUR_GITHUB.md    # Guide pour publier le dépôt
```
