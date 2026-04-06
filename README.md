# KrabbysAnimals — YouTube Shorts Automation

**Automated pipeline that creates 15-second vertical animal Shorts from Pexels stock footage and uploads them to YouTube.**

**Channel:** https://www.youtube.com/@KrabbysAnimals

## What It Does

Downloads Pexels videos → generates gTTS narration → cuts clips with FFmpeg → adds captions → uploads via YouTube OAuth API. Runs on cron at 07:30 and 17:30.

## Restore from Scratch

```bash
# Requires: Python 3.10+, Node.js 18+, FFmpeg
python3 --version
ffmpeg -version

cd /home/dobby/.openclaw/workspace/youtube-shorts

# Python dependencies
pip install pexels-api requests gTTS

# Node dependencies (for OAuth server)
npm install

# Set up credentials (see below)
cp credentials.json my_credentials.json
# Edit my_credentials.json with real tokens
```

## Credentials Needed

### Pexels API
1. Create account at https://www.pexels.com/api/
2. Get API key
3. Add to `credentials.json` or set env: `PEXELS_API_KEY=your_key`

### YouTube OAuth
The `credentials.json` already contains OAuth tokens. To refresh:
```bash
python oauth_flow.py
# Opens browser for OAuth consent
# Saves tokens to credentials.json
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `create_short.py` | Main pipeline: video → TTS → cut → caption → output |
| `upload.py` | YouTube OAuth upload |
| `download_clips.py` | Pexels video downloader |
| `oauth_flow.py` | Initial OAuth setup |

## FFmpeg

Static FFmpeg is included at `ffmpeg-master-latest-linux64-gpl/bin/ffmpeg`. If missing:
```bash
cd /home/dobby/.openclaw/workspace/youtube-shorts
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
# Move ffmpeg to expected path
```

## Manual Usage

```bash
# Create a short
python create_short.py --pexels-id 1234567 --query "cute puppy"

# Upload
python upload.py --file output/my_short.mp4 --title "Cute Puppy 🐕"

# Download a Pexels video
python download_clips.py --query "puppy playing" --count 3
```

## Cron Schedule

```bash
# Morning short
30 7 * * * cd /home/dobby/.openclaw/workspace/youtube-shorts && bash cron_upload.sh >> upload_log.txt 2>&1

# Evening short
30 17 * * * cd /home/dobby/.openclaw/workspace/youtube-shorts && bash cron_upload.sh >> upload_log.txt 2>&1
```

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Main pipeline |
| FFmpeg (static) | Video cutting, re-encoding |
| gTTS | Text-to-speech narration |
| Pexels API | Stock video source |
| YouTube Data API v3 | OAuth upload |

## Project Structure

```
youtube-shorts/
├── create_short.py      # Main short creation
├── upload.py           # YouTube upload
├── download_clips.py   # Pexels downloader
├── tts.py             # gTTS wrapper
├── config.py          # Paths + settings
├── oauth_flow.py      # YouTube OAuth setup
├── credentials.json   # API tokens (gitignored)
├── ffmpeg-master-*/   # Static FFmpeg binary
├── stock/             # Downloaded Pexels videos
├── output/            # Generated shorts (pre-upload)
├── uploaded/          # Track uploaded videos
├── audio/             # TTS audio files
├── thumbnails/        # Generated thumbnails
└── cron_upload.sh     # Cron entry point
```

## Verify Setup

```bash
# FFmpeg
./ffmpeg-master-latest-linux64-gpl/bin/ffmpeg -version

# Pexels API
curl -H "Authorization: YOUR_API_KEY" https://api.pexels.com/videos/search?query=puppy

# gTTS
python -c "from gtts import gTTS; tts = gTTS('hello'); tts.save('/tmp/test.mp3')"

# YouTube OAuth
python -c "import httplib2; print('httplib2 OK')"
```
