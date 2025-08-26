# music_spotify.py
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

_sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    )
)

# Map emotions to Spotify seed genres (valid seeds)
'''EMOTION_TO_GENRE = {
    "happy": "pop",
    "sad": "acoustic",
    "angry": "metal",
    "surprise": "dance",
    "neutral": "chill",
    "fear": "ambient",
    "disgust": "rock",
}'''
emotion_to_genres = {
    "happy": ["pop", "dance", "party"],
    "sad": ["acoustic", "piano", "singer-songwriter"],
    "angry": ["metal", "rock", "hardcore"],
    "surprise": ["electronic", "indie", "alternative"],
    "neutral": ["chill", "ambient", "classical"]
}

def _best_image(images):
    """Pick a reasonable album image URL."""
    if not images:
        return None
    # Prefer mid-sized if available, else first
    images_sorted = sorted(images, key=lambda im: im.get("width", 0))
    return images_sorted[min(1, len(images_sorted)-1)]["url"]

def get_tracks_by_emotion(emotion: str, limit: int = 5):
    """Return up to `limit` tracks (dicts) for the given emotion."""
    emotion = (emotion or "neutral").lower()
    genre = emotion_to_genres.get(emotion, "pop")

    tracks = []
    try:
        # Try Spotify recommendations first
        rec = _sp.recommendations(seed_genres=[genre], limit=limit)
        for t in rec.get("tracks", []):
            tracks.append({
                "name": t["name"],
                "artist": t["artists"][0]["name"] if t["artists"] else "Unknown",
                "spotify_url": t["external_urls"]["spotify"],
                "image_url": _best_image(t["album"].get("images", [])),
            })
    except Exception:
        tracks = []

    # Fallback to a simple search if recommendations fail/empty
    if not tracks:
        q = f"{emotion} mood"
        res = _sp.search(q=q, type="track", limit=limit)
        for t in res["tracks"]["items"]:
            tracks.append({
                "name": t["name"],
                "artist": t["artists"][0]["name"] if t["artists"] else "Unknown",
                "spotify_url": t["external_urls"]["spotify"],
                "image_url": _best_image(t["album"].get("images", [])),
            })

    return tracks[:limit]
