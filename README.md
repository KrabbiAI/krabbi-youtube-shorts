# KrabbysAnimals — YouTube Shorts Automation

**Automated pipeline that creates 15-second vertical animal Shorts from Pexels stock footage and uploads them to YouTube.**

**Channel:** https://www.youtube.com/@KrabbysAnimals

## What It Does

Downloads Pexels videos → generates gTTS narration → cuts clips with FFmpeg → renders captions + thumbnails with Remotion → uploads via YouTube OAuth API. Runs on cron at 07:30 and 17:30.

## Restore from Scratch

### 1. System Dependencies

```bash
# Ubuntu/Debian
sudo apt install python3-pip python3-venv curl wget git

# FFmpeg (static build — no install needed)
cd /home/dobby/.openclaw/workspace/youtube-shorts
wget https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
tar xf ffmpeg-master-latest-linux64-gpl.tar.xz
# Binary ends up at: ffmpeg-master-latest-linux64-gpl/bin/ffmpeg
```

### 2. Python Dependencies

```bash
pip install pexels-api requests gTTS yt-dlp httplib2 google-auth google-auth-oauthlib google-auth-httplib2
```

### 3. Node Dependencies (for Remotion video rendering)

```bash
cd /home/dobby/.openclaw/workspace/youtube-shorts
npm install
```

### 4. Credentials

#### Pexels API
1. Create account at https://www.pexels.com/api/
2. Get API key
3. Create `credentials.json`:
```json
{
  "pexels_api_key": "YOUR_PEXELS_KEY"
}
```

#### YouTube OAuth (Browser Required Once)
```bash
# Run the OAuth flow — opens browser for Google sign-in
python oauth_flow.py

# This creates credentials.json with tokens
# Tokens expire; refresh by running oauth_flow.py again
```

### 5. Directory Setup

```bash
mkdir -p stock output audio clips thumbnails uploaded
```

### 6. Verify Setup

```bash
# FFmpeg
./ffmpeg-master-*/bin/ffmpeg -version

# Python packages
python -c "import pexels; import gtts; import yt_dlp; print('All OK')"

# Remotion
cd remotion && npx remotion preview Entry.tsx --port 3000
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `create_short.py` | Download Pexels video → cut → add TTS → produce final MP4 |
| `produce_short.sh` | Full pipeline with BGM + TTS + Remotion captions |
| `upload.py` | YouTube OAuth upload |
| `download_clips.py` | Batch download from Pexels |
| `oauth_flow.py` | Initial YouTube OAuth setup (opens browser) |

## Production Pipeline

```bash
# One-liner for a complete short:
./produce_short.sh <num> "<narration>" "<animal_name>" <clips...>

# Example:
./produce_short.sh 1 "Look at these adorable puppies!" "Golden Retriever" clip1.mp4 clip2.mp4
```

## YouTube OAuth Refresh

Access tokens expire after ~1 hour. To refresh:
```bash
python oauth_flow.py
# Opens browser → sign in → tokens saved to credentials.json
```

For **headless servers**, set up a redirect tunnel:
```bash
# On server:
python oauth_flow.py --port 8080

# Locally (with ngrok or similar):
ngrok http 8080
# Use the ngrok URL as redirect URI in Google Console
```

## Project Structure

```
youtube-shorts/
├── create_short.py      # FFmpeg-based clip cutter + TTS
├── produce_short.sh     # Full pipeline with BGM + Remotion
├── upload.py           # YouTube OAuth upload
├── download_clips.py   # Pexels batch downloader
├── tts.py             # gTTS wrapper
├── config.py          # Paths + constants
├── oauth_flow.py      # YouTube OAuth setup (browser)
├── credentials.json   # API tokens (gitignored)
├── remotion/          # Video renderer (captions, thumbnails)
│   ├── Entry.tsx
│   ├── MyVideo.tsx
│   └── ...
├── ffmpeg-master-*/   # Static FFmpeg (gitignored)
├── stock/             # Downloaded Pexels videos
├── output/            # Rendered shorts
├── audio/             # TTS + BGM files
├── thumbnails/        # Generated thumbnails
└── uploaded/          # Track uploaded videos
```

## Cron Schedule

```bash
# Morning short — 07:30
30 7 * * * cd /home/dobby/.openclaw/workspace/youtube-shorts && bash cron_upload.sh >> upload_log.txt 2>&1

# Evening short — 17:30
30 17 * * * cd /home/dobby/.openclaw/workspace/youtube-shorts && bash cron_upload.sh >> upload_log.txt 2>&1
```

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Main pipeline + OAuth |
| FFmpeg (static) | Video cutting, audio mixing, re-encoding |
| gTTS | Text-to-speech narration |
| yt-dlp | Video downloading |
| Pexels API | Stock video library |
| Remotion | Video composition (captions, effects) |
| YouTube Data API v3 | OAuth upload |
