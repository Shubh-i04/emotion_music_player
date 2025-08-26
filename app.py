# app.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # hide TF info logs

import tkinter as tk
from tkinter import ttk
from io import BytesIO
import requests
from PIL import Image, ImageTk
import webbrowser

from face_emotion import detect_emotion
from music_spotify import get_tracks_by_emotion
from music_youtube import open_on_youtube

APP_TITLE = "Emotion-based Music Player (GUI)"


class EmotionMusicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x680")

        self.photo_cache = []  # keep references to PhotoImage to prevent GC
        self._build_ui()

    def _build_ui(self):
        # Top bar
        header = ttk.Frame(self.root, padding=16)
        header.pack(fill="x")

        ttk.Label(header, text=APP_TITLE, font=("Segoe UI", 16, "bold")).pack(side="left")

        self.emotion_var = tk.StringVar(value="Emotion: —")
        ttk.Label(header, textvariable=self.emotion_var, font=("Segoe UI", 12)).pack(side="left", padx=16)

        self.detect_btn = ttk.Button(header, text="Detect Emotion", command=self.on_detect_click)
        self.detect_btn.pack(side="right")

        # Instruction
        info = ttk.Label(
            self.root,
            text="Click 'Detect Emotion'. After webcam opens, press 'q' to confirm your emotion.",
            padding=(16, 4)
        )
        info.pack(fill="x")

        # Results area
        self.cards_frame = ttk.Frame(self.root, padding=16)
        self.cards_frame.pack(fill="both", expand=True)

        # Status
        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self.root, textvariable=self.status_var, relief="groove", anchor="w", padding=8)
        status.pack(fill="x", side="bottom")

    def on_detect_click(self):
        self.detect_btn.config(state="disabled")
        self.status_var.set("Opening webcam… Press 'q' to confirm.")
        self.root.update_idletasks()

        # Blocking call while the webcam window is open:
        emotion = detect_emotion()
        self.emotion_var.set(f"Emotion: {emotion}")
        self.status_var.set("Fetching songs from Spotify…")

        # Fetch 5 tracks
        tracks = get_tracks_by_emotion(emotion, limit=5)
        if not tracks:
            self.status_var.set("No tracks found. Check internet/credentials.")
        else:
            self._render_cards(tracks)
            self.status_var.set("Suggestions ready. Pick a song to play!")

        self.detect_btn.config(state="normal")

    def _render_cards(self, tracks):
        # Clear previous
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self.photo_cache.clear()

        # Create a grid of 5 cards
        for idx, t in enumerate(tracks):
            card = ttk.Frame(self.cards_frame, padding=10)
            card.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=8, pady=8)
            self.cards_frame.grid_columnconfigure(idx % 2, weight=1)

            # Cover image
            img_label = ttk.Label(card)
            img_label.pack(anchor="w")
            photo = self._fetch_image_photo(t.get("image_url"))
            if photo:
                img_label.config(image=photo)
                self.photo_cache.append(photo)  # keep ref

            # Title & artist
            title = t.get("name", "Unknown")
            artist = t.get("artist", "Unknown")
            ttk.Label(card, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6, 0))
            ttk.Label(card, text=artist, font=("Segoe UI", 11)).pack(anchor="w")

            # Buttons: Spotify / YouTube
            btns = ttk.Frame(card)
            btns.pack(anchor="w", pady=6)

            ttk.Button(
                btns, text="Open on Spotify",
                command=lambda url=t.get("spotify_url"): webbrowser.open(url) if url else None
            ).pack(side="left", padx=(0, 8))

            # ✅ FIXED: each button calls open_on_youtube() properly
            ttk.Button(
                btns, text="Play on YouTube",
                command=lambda title=title, artist=artist: open_on_youtube(f"{title} {artist} audio")
            ).pack(side="left")

    def _fetch_image_photo(self, url, size=(220, 220)):
        if not url:
            return None
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None


def main():
    root = tk.Tk()
    app = EmotionMusicGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
