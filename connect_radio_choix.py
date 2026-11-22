import vlc
import time
import subprocess
import asyncio
import json
import os
import sys
from shazamio import Shazam

# 🎛️ Nom du périphérique d'enregistrement DirectShow (Mixage stéréo).
# Pour trouver le nom exact sur ton PC :
#   ffmpeg -list_devices true -f dshow -i dummy
# Tu peux aussi le définir sans modifier le script :
#   $env:AUDIO_DEVICE = "Stereo Mix (Realtek(R) Audio)"
AUDIO_DEVICE = os.environ.get("AUDIO_DEVICE", "Mixage stéréo (Realtek(R) Audio)")

# 📻 Radios
radios = {
    "europe2": "http://europe2.lmn.fm/europe2.mp3",
    "nostalgie": "https://master.net-radio.fr/nostalgie-tuner37.mp3",
    "techno_lover": "https://stream.technolovers.fm/ibiza-house",
    "house": "https://listen.di.fm/public3/house.pls",
    "ibiza_global": "http://ibizaglobalradio.streaming-pro.com:8024/stream",
    "fg": "https://n15a-eu.rcs.revma.com/7081n2b6p98uv?rj-ttl=5&rj-tok=AAABne3vWzsAginXDSNJ6QQO4Q",
    "Ato": "https://streaming.radio.co/s0c41ec4af/low",
    "ace": "https://ice41.securenetsystems.net/KHAM",
    "fun": "https://icecast.funradio.fr/fun-1-44-64",
}

DB_FILE = "musique_db.json"


# 📂 Charger base de données
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# 💾 Sauvegarder
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


# 🔎 Vérifier doublon
def is_duplicate(db, title, artist):
    for track in db:
        if track["title"] == title and track["artist"] == artist:
            return True
    return False


# 🎧 Capture audio (son système)
def record_audio(filename="sample.wav", duration=8):
    print("🎙️ Capture audio ambiance PC...")

    if os.path.exists(filename):
        os.remove(filename)

    try:
        subprocess.run([
            "ffmpeg",
            "-y",
            "-f", "dshow",
            "-i", f"audio={AUDIO_DEVICE}",
            "-t", str(duration),
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            filename
        ])
    except FileNotFoundError:
        print("❌ ffmpeg est introuvable : installe-le et ajoute-le au PATH (voir README).")
        return False

    if not os.path.exists(filename):
        print("❌ ERREUR : fichier non créé (vérifie le nom du périphérique audio)")
        return False

    print("✅ Fichier audio capturé")
    return True


# 🔍 Shazam
async def recognize_music(file):
    shazam = Shazam()
    out = await shazam.recognize(file)

    if "track" in out:
        track = out["track"]

        return {
            "title": track.get("title"),
            "artist": track.get("subtitle"),
            "genre": track.get("genres", {}).get("primary"),
            "downloaded": False
        }
    return None


# Nettoyage du nom (évite erreurs Windows)
def clean_genre(genre):
    if not genre:
        return "Unknown"

    for c in '/\\:*?"<>|':
        genre = genre.replace(c, "-")

    return genre


# ⬇️ Téléchargement avec yt-dlp (installé via pip)
def download_music(title, artist, genre):
    query = f"{artist} - {title}"

    genre = clean_genre(genre)

    # 📁 Créer dossier si pas existant
    folder = os.path.join("musiques", genre)
    os.makedirs(folder, exist_ok=True)

    print(f"⬇️ Téléchargement : {query} → {folder}")

    subprocess.run([
        sys.executable, "-m", "yt_dlp",
        f"ytsearch1:{query}",
        "-x",
        "--audio-format", "mp3",
        "-o", os.path.join(folder, "%(title)s.%(ext)s")
    ])


# 🚀 Programme principal
def main():
    choix = input(f"Quelle radio ? ({', '.join(radios)}) ")

    if choix not in radios:
        print("❌ Radio inconnue")
        return

    url = radios[choix]

    # ▶️ Lancer radio
    player = vlc.MediaPlayer(url)
    player.play()
    print("📻 Lecture en cours... (Ctrl + C pour arrêter)")

    db = load_db()

    try:
        while True:

            # 🎧 Enregistrer 4 sec
            success = record_audio("sample.wav", 4)

            if not success:
                time.sleep(5)
                continue  # ⛔ on saute cette boucle si pas d'audio

            # 🔍 Reconnaissance
            result = asyncio.run(recognize_music("sample.wav"))

            if result:
                title = result["title"]
                artist = result["artist"]
                genre = result["genre"]

                print(f"\n🎵 {artist} - {title}")

                if not is_duplicate(db, title, artist):
                    print("✅ Nouveau morceau !")

                    # ⬇️ Télécharger automatiquement
                    download_music(title, artist, genre)
                    result["downloaded"] = True

                    db.append(result)
                    save_db(db)

                else:
                    print("⚠️ Déjà enregistré")

            else:
                print("❌ Rien trouvé")

            # ⏱️ Attendre 1 minute (dans la boucle)
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n🛑 Arrêt du programme")

    finally:
        player.stop()


# ▶️ Lancer
if __name__ == "__main__":
    main()
