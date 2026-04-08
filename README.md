# KrabbysAnimals — YouTube Shorts Automation

**Automated pipeline that creates 15-second vertical animal Shorts from Pexels stock footage and uploads them to YouTube.**

**Channel:** https://www.youtube.com/@KrabbysAnimals

## Was Es Macht

Downloads Pexels videos → generates gTTS narration → cuts clips with FFmpeg → renders captions + thumbnails with Remotion → uploads via YouTube OAuth API. Runs on cron at 07:30 and 17:30.

## Tech Stack

| Tool | Purpose | Version |
|------|---------|---------|
| Python | Main pipeline + OAuth | 3.8+ |
| FFmpeg (static) | Video cutting, audio mixing | latest |
| gTTS | Text-to-speech narration | latest |
| yt-dlp | Video downloading | latest |
| Pexels API | Stock video library | v1 |
| Remotion | Video composition | latest |
| YouTube Data API v3 | OAuth upload | v3 |

## Restore from Scratch

### 1. System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3-pip python3-venv curl wget git
```

### 2. FFmpeg (Static Build)

```bash
cd /home/dobby/.openclaw/workspace/youtube-shorts
wget https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
tar xf ffmpeg-master-latest-linux64-gpl.tar.xz
# Binary ends up at: ffmpeg-master-latest-linux64-gpl/bin/ffmpeg
```

### 3. Python Dependencies

```bash
pip install pexels-api requests gTTS yt-dlp httplib2 google-auth google-auth-oauthlib google-auth-httplib2
```

### 4. Node Dependencies (for Remotion)

```bash
cd /home/dobby/.openclaw/workspace/youtube-shorts
npm install
```

### 5. Credentials Setup

**Pexels API:**
1. Account auf https://www.pexels.com/api/ erstellen
2. API Key holen
3. In `credentials.json` speichern (nicht in Git!):
```json
{
  "pexels_api_key": "YOUR_PEXELS_KEY"
}
```

**YouTube OAuth (Browser Required Once):**
```bash
# OAuth flow — öffnet Browser für Google login
python oauth_flow.py

# Erstellt credentials.json mit tokens
# Tokens verfallen; refresh mit oauth_flow.py erneut
```

### 6. Directory Setup

```bash
mkdir -p stock output audio clips thumbnails uploaded
```

### 7. Environment Variables

```bash
# Optional: Pexels API key als env var statt in credentials.json
export PEXELS_API_KEY="your_pexels_key"
```

## API Endpoints

### Pexels API

**Base URL:** `https://api.pexels.com/v1/`

**Search Videos:**
```
GET /search?query=<query>&per_page=<num>&orientation=<portrait|landscape>
Headers: Authorization: <API_KEY>
```

**Get Video:**
```
GET /videos/<id>
Headers: Authorization: <API_KEY>
```

### YouTube Data API v3

**Base URL:** `https://www.googleapis.com/youtube/v3/`

**Upload Video:**
```
POST /videos
Headers: Authorization: Bearer <ACCESS_TOKEN>
Body: {snippet: {...}, status: {...}}
```

**OAuth Token Refresh:**
```
POST /token
Body: client_id=...&client_secret=...&refresh_token=...&grant_type=refresh_token
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `create_short.py` | Download Pexels video → cut → add TTS → produce final MP4 |
| `produce_short.sh` | Full pipeline with BGM + TTS + Remotion captions |
| `upload.py` | YouTube OAuth upload |
| `download_clips.py` | Batch download from Pexels |
| `oauth_flow.py` | Initial YouTube OAuth setup (opens browser) |
| `cron_upload.sh` | Cron wrapper für automatischen upload |

## Production Pipeline

```bash
# Full pipeline:
./produce_short.sh <num> "<narration>" "<animal_name>" <clips...>

# Example:
./produce_short.sh 1 "Look at these adorable puppies!" "Golden Retriever" clip1.mp4 clip2.mp4
```

**Cron:**
```bash
# Morning short — 07:30
30 7 * * * cd /home/dobby/.openclaw/workspace/youtube-shorts && bash cron_upload.sh >> upload_log.txt 2>&1

# Evening short — 17:30
30 17 * * * cd /home/dobby/.openclaw/workspace/youtube-shorts && bash cron_upload.sh >> upload_log.txt 2>&1
```

## YouTube OAuth Refresh

Access tokens verfallen nach ~1 Stunde. Für Refresh:

```bash
python oauth_flow.py
# Öffnet Browser → login → tokens zu credentials.json
```

**Für Headless Server**, Tunnel einrichten:
```bash
# Auf Server:
python oauth_flow.py --port 8080

# Lokal (mit ngrok):
ngrok http 8080
# ngrok URL als redirect URI in Google Console nutzen
```

## 30-Tage Video Cleanup

`used_videos.txt` trackt verwendete Videos mit Timestamps. Einträge >30 Tage werden automatisch gelöscht.

```
# Format:
<pexels_video_id>|<timestamp>
```

## Projekt Struktur

```
youtube-shorts/
├── create_short.py      # FFmpeg-based clip cutter + TTS
├── produce_short.sh     # Full pipeline with BGM + Remotion
├── upload.py           # YouTube OAuth upload
├── download_clips.py   # Pexels batch downloader
├── tts.py             # gTTS wrapper
├── config.py          # Paths + constants
├── oauth_flow.py      # YouTube OAuth setup (browser)
├── cron_upload.sh     # Cron wrapper
├── credentials.json   # API tokens (gitignored!)
├── remotion/          # Video renderer (captions, effects)
│   ├── Entry.tsx
│   └── MyVideo.tsx
├── ffmpeg-master-*/   # Static FFmpeg (gitignored)
├── stock/             # Downloaded Pexels videos
├── output/            # Rendered shorts
├── audio/             # TTS + BGM files
├── thumbnails/        # Generated thumbnails
├── uploaded/          # Track uploaded videos
└── used_videos.txt   # Video usage log (30-day cleanup)
```

## Troubleshooting

**Pexels API Error 401/403:**
- API Key prüfen, in credentials.json korrekt?
- API Key hat noch credits?

**YouTube Upload schlägt fehl:**
- OAuth Token abgelaufen? → `python oauth_flow.py` erneut
- Video zu groß? YouTube limit ist 256GB
- Copyright Content? YouTube kann Content ID strikes geben

**FFmpeg Fehler:**
- Static FFmpeg binary in PATH?
- `chmod +x ffmpeg-master-*/bin/ffmpeg`

**Remotion rendering langsam:**
- Node.js memory limit erhöhen
- `NODE_OPTIONS="--max-old-space-size=4096"`

## Credentials Storage

**WICHTIG:** `credentials.json` enthält:
- Pexels API Key
- YouTube OAuth tokens (refresh token, access token)

Diese Datei ist in `.gitignore` — NIE in Git pushen!

## Verify Installation

```bash
# FFmpeg
./ffmpeg-master-*/bin/ffmpeg -version

# Python packages
python -c "import pexels; import gtts; import yt_dlp; print('All OK')"

# OAuth status
python -c "import json; c=json.load(open('credentials.json')); print('Has tokens' if 'access_token' in c else 'No tokens')"
```
