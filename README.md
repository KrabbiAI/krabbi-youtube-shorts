# 🦀 Krabbi's YouTube Shorts Automation

Automated YouTube Shorts pipeline that generates daily animal fact videos using:
- **Pexels** — Stock footage (free, no watermark)
- **ElevenLabs** — Sarah voice TTS narration
- **FFmpeg** — Video rendering with text overlay

## 📁 Project Structure

```
youtube-shorts/
├── animal_facts.json      # 208 animal facts (52 animals × 4 facts each)
├── used_facts.json        # Tracks which fact IDs have been used
├── used_videos.txt        # Tracks which Pexels video IDs have been used
├── credentials.json       # Google OAuth credentials (NOT in repo!)
├── client_secret.json     # Google OAuth client secrets (NOT in repo!)
├── cron_upload.sh         # Main entry point — runs twice daily
├── facts_search.py        # Picks random unused facts, generates TTS
├── download_clips.py      # Pexels API clip downloader
├── upload.py              # YouTube Data API upload
├── tts.py                 # ElevenLabs TTS wrapper
├── cleanup_telegram.sh    # Deletes Telegram messages after 10h
├── audio/
│   └── ambient_bgm.mp3    # Background music loop
├── stock/                  # Temporary stock clips (deleted after render)
└── output/                 # Temporary rendered shorts (deleted after upload)
```

## 🔑 Credentials Required

1. **Google OAuth** (for YouTube upload):
   - Create at https://console.cloud.google.com
   - Enable YouTube Data API v3
   - Download `client_secret.json` → place in project root
   - Run `python3 do_oauth.py` to get credentials

2. **Pexels API** (for stock footage):
   - Get free key at https://www.pexels.com/api/
   - Place in `credentials.json`:
     ```json
     { "pexels": "YOUR_API_KEY" }
     ```

3. **ElevenLabs** (for TTS):
   - Get key at https://elevenlabs.io
   - Place in `credentials.json`:
     ```json
     { "elevenlabs": { "api_key": "YOUR_API_KEY" } }
     ```

4. **Telegram Bot** (for preview notifications):
   - Create via @BotFather
   - Add to `credentials.json`:
     ```json
     { "telegram": { "bot_token": "BOT:TOKEN", "chat_id": "YOUR_CHAT_ID" } }
     ```

## 🚀 Setup

```bash
# 1. Clone repo
git clone https://github.com/KrabbiAI/krabbi-youtube-shorts.git
cd krabbi-youtube-shorts

# 2. Install dependencies
pip install google-api-python-client google-auth-requests elevenlabs requests

# 3. Download FFmpeg (if not system-installed)
# Download from https://johnvansickle.com/ffmpeg/
# Extract to ffmpeg-master-latest-linux64-gpl/bin/

# 4. Add credentials (see above)

# 5. Run OAuth flow
python3 do_oauth.py

# 6. Test run
./cron_upload.sh
```

## ⏰ Automation (Cron)

```cron
# Daily at 7:30 and 17:30
30 7,17 * * * /path/to/cron_upload.sh >> /path/to/upload_log.txt 2>&1

# Hourly Telegram cleanup (delete messages after 10h)
0 * * * * /path/to/cleanup_telegram.sh >> /path/to/upload_log.txt 2>&1

# Daily cleanup (old TTS, shorts, temp files)
0 6 * * * find /path/to -name '*.mp3' -mtime +1 -delete
```

## 🎬 How It Works

1. **Fact Selection** — Picks random UNUSED fact from `animal_facts.json`
2. **TTS Generation** — ElevenLabs Sarah voice, ~15-20s narration
3. **Stock Download** — Pexels clip ≥ (TTS duration + 2s), never used before
4. **Video Render** — FFmpeg: 1080×1920, yellow text banner at top, ambient BGM
5. **Telegram Preview** — Sends to bot chat, saves message_id
6. **YouTube Upload** — Public, title "Daily Animal Facts! 🐾", auto-deletes local file
7. **Telegram Cleanup** — Hourly cron deletes messages older than 10h

## 🎨 Text Banner

- Yellow bold text, LiberationSans-Bold 60px
- Centered at y=215
- Black box background at y=120 (height 220)
- Text: "Subscribe for daily animal facts!"

## 🔄 Replenishing Facts

When `< 10` unused facts remain, `facts_search.py` auto-adds 20 more animals with 4 facts each via `research_new_facts()`.

## ⚠️ Notes

- Stock clips are DELETED immediately after render
- Shorts are DELETED immediately after successful upload
- `used_facts.json` and `used_videos.txt` track what's been used
- No duplicates: fact IDs and video IDs are never reused

## 📺 YouTube Channel

**Channel:** https://www.youtube.com/@KrabbysAnimals
**Schedule:** 7:30 AM & 5:30 PM (Mon-Fri) + 12:30 PM (Fri-Sun)

---

*Built by Krabbi 🦀 — Automated with ElevenLabs, Pexels & FFmpeg*
