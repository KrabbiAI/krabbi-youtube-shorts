# YouTube Shorts - Cute Animals 🐾

**Project:** Automated YouTube Shorts Generator
**Tools:** yt-dlp, FFmpeg (static build), gTTS (all free)
**Location:** `/home/dobby/.openclaw/workspace/youtube-shorts/`

---

## 3 Shorts sind fertig! 🎬

### Short 1: Puppies 🐶
- **File:** `output/short_01.mp4`
- **Duration:** 15s
- **Size:** 1.5 MB
- **Clips:** Puppies compilation (3 clips fast-cut)
- **Narration:** "Oh my goodness! Look at these adorable puppies!"

**YouTube Metadata:**
- **Title:** `Adorable Baby Animals Compilation 🐾 #1`
- **Description:** `Watch these adorable puppies and smile today! #cuteanimals #babyanimals #puppies #funny #wholesome`
- **Tags:** cute animals, baby animals, puppies, adorable, happy, dogs

---

### Short 2: Kittens 🐱
- **File:** `output/short_02.mp4`
- **Duration:** 15s
- **Size:** 956 KB
- **Clips:** Kittens compilation (3 clips fast-cut)
- **Narration:** "Warning: Extreme cuteness ahead with these little kittens!"

**YouTube Metadata:**
- **Title:** `Cute Kittens That Will Make Your Day Better ✨ #2`
- **Description:** `Because you deserve a little cuteness today 💕 #kittens #cuteanimals #cats #viral #shorts`
- **Tags:** cute animals, kittens, baby cats, adorable, happy, pets

---

### Short 3: Mixed Animals 🐰🐶🐱
- **File:** `output/short_03.mp4`
- **Duration:** 15s
- **Size:** 836 KB
- **Clips:** Bunnies + Puppies + Kittens (6 clips fast-cut)
- **Narration:** "This is what happiness looks like! Sweet little bunnies and more cute animals!"

**YouTube Metadata:**
- **Title:** `15 Seconds of Pure Cuteness! 💖 #3`
- **Description:** `Nature's most adorable moments captured! #wildlife #cuteanimals #bunnies #babyanimals #viral`
- **Tags:** cute animals, baby animals, bunnies, puppies, kittens, wholesome, happy

---

## Workflow für neue Shorts

```bash
cd /home/dobby/.openclaw/workspace/youtube-shorts

# 1. Clips downloaden (YouTube)
yt-dlp --extractor-args "youtube:player_client=android" \
  -f "best[height<=720]" \
  --download-sections "*0-15" \
  --ffmpeg-location ./ffmpeg-master-latest-linux64-gpl/bin \
  -o "clips/newclip.mp4" "https://youtube.com/watch?v=..."

# 2. Clips zusammenfügen (concat)
cat > /tmp/concat.txt << 'EOF'
file 'clips/clip1.mp4'
file 'clips/clip2.mp4'
file 'clips/clip3.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt \
  -c copy output/draft.mp4

# 3. TTS erstellen
python3 -c "from gtts import gTTS; gTTS(text='Your narration here', lang='en').save('audio/tts.mp3')"

# 4. Video + TTS kombinieren (15s trim)
ffmpeg -y -i output/draft.mp4 -i audio/tts.mp3 -t 15 \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k -shortest \
  output/final_short.mp4
```

---

## Projekt-Struktur

```
youtube-shorts/
├── clips/           # Rohmaterial (Tiervideos)
├── output/          # Fertige Shorts
├── audio/           # TTS Audio Files
├── thumbnails/      # Thumbnails (optional)
├── ffmpeg-*/        # FFmpeg static build
├── config.py        # Einstellungen
├── tts.py           # Text-to-Speech
├── download_clips.py
├── create_short.py  # Short Creator (verbessert)
└── README.md
```

---

## Automatisierungsideen

- **Cron Job:** Täglich 3 neue Shorts generieren
- **RSS/Twitter:** Neue Tiervideos automatisch erkennen
- **Thumbnail Generator:** Mit Python PIL
- **Upload Script:** YouTube API Integration (mit OAuth)
- **SEO:** Hashtags automatisch aus Trends generieren

---

*Erstellt: 2. April 2026, 02:00 Uhr*
