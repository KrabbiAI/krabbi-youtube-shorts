#!/bin/bash
# YouTube Shorts Upload - runs at 7:30 and 17:30
# 1. Generate TTS with ElevenLabs
# 2. Download fresh stock clip (>= TTS+2s, not used before)
# 3. Render short
# 4. Send preview to Telegram
# 5. Upload to YouTube
# 6. Delete all local files (clip + video)

BASE="/home/dobby/.openclaw/workspace/youtube-shorts"
LOG="$BASE/upload_log.txt"
PEXELS_API="YFU5OwjisNiAyjBj7GCJGM7WOzHSR1wLp2IVBwAddYkZWl463OexLXmV"
TELEGRAM_BOT="8798400513:AAHVGh4T2dtsEXZML6zmtXLNLVPM4lpAcZE"
CHAT_ID="631196199"
FFMPEG="$BASE/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
FFPROBE="$BASE/ffmpeg-master-latest-linux64-gpl/bin/ffprobe"

cd $BASE

log() {
    echo "[$(date)] $1" >> $LOG
}

download_clip() {
    # Downloads ONE clip that's at least $1 seconds long
    # $2 = comma-separated animal names to use as search terms
    local needed_dur=$1
    local animal_terms=$2
    local clip_file=""
    
    python3 << PYEOF 2>> $LOG
import requests, os, random, time

API = "$PEXELS_API"
STOCK = "$BASE/stock"
USED_FILE = "$BASE/used_videos.txt"
os.makedirs(STOCK, exist_ok=True)

used_ids = set()
if os.path.exists(USED_FILE):
    with open(USED_FILE, 'r') as f:
        used_ids = {line.strip().split(',')[0] for line in f if line.strip()}
print(f"Already used: {len(used_ids)} clips")

# Use animal names from TTS as primary search terms
animal_terms = "$animal_terms"
if animal_terms and animal_terms != "ANIMALS":
    # Convert KANGAROO|CAMEL to ["cute baby kangaroos", "cute kangaroos playing"]
    searches = []
    for a in animal_terms.split('_'):
        a = a.strip().lower()
        if a:
            searches.append(f"cute baby {a}s")
            searches.append(f"cute {a}s playing")
            searches.append(f"cute {a}s sleeping")
            searches.append(f"cute {a}s")
    # Add high-watchtime fallback searches
    searches += [
        "cute baby puppies playing", "cute puppies sleeping",
        "cute baby kittens", "cute kittens playing", "cute kittens sleeping",
        "cute baby bunnies", "cute baby ducks", "cute baby elephants",
        "cute otters holding hands", "cute quokkas", "cute red pandas",
        "cute fennec foxes", "cute sugar gliders", "cute ferrets playing"
    ]
else:
    searches = [
        # Baby + Playing (highest watchtime)
        "cute baby puppies playing", "cute puppies sleeping",
        "cute baby kittens", "cute kittens playing", "cute kittens sleeping",
        "cute baby bunnies", "cute baby ducks", "cute baby elephants",
        "cute baby foxes", "cute baby pandas",
        # Emotional/Behavior
        "cute otters holding hands", "cute puppies playing",
        "cute kittens playing", "cute baby penguins",
        "cute baby seals", "cute baby koalas",
        # Popular Animals
        "cute puppies", "cute kittens", "cute bunnies", "cute pandas",
        "cute elephants", "cute foxes", "cute seals",
        "cute penguins", "cute koalas", "cute sloths",
        # Unique/Interesting
        "cute quokkas", "cute red pandas", "cute fennec foxes",
        "cute sugar gliders", "cute ferrets", "cute hedgehogs",
        "cute alpacas", "cute meerkats", "cute capybaras"
    ]

# Track last searched animal to avoid the same animal twice in a row
skip_animals_pl = {'puppies': 'puppy', 'kittens': 'kitten', 'bunnies': 'bunny',
                'ducks': 'duck', 'elephants': 'elephant', 'foxes': 'fox',
                'penguins': 'penguin', 'seals': 'seal', 'koalas': 'koala',
                'pandas': 'panda', 'sloths': 'sloth', 'quokkas': 'quokka',
                'gliders': 'glider', 'ferrets': 'ferret'}
last_animal = None

def dl(vid, fn):
    r = requests.get(f"https://api.pexels.com/videos/videos/{vid}", headers={"Authorization": API})
    if r.status_code != 200: return False
    for vf in r.json().get("video_files", []):
        h = vf.get("height", 0)
        if 720 <= h <= 1080:
            url = vf.get("link")
            if url:
                x = requests.get(url, stream=True)
                if x.status_code == 200:
                    with open(fn, 'wb') as f:
                        for c in x.iter_content(8192): f.write(c)
                    return True
    return False

random.shuffle(searches)
needed = $needed_dur
last_animal = None

for q in searches:
    # Skip if same animal as last search
    words = q.lower().split()
    animal = words[-1] if words else ''
    normalized = skip_animals_pl.get(animal, animal)
    if normalized == last_animal:
        continue  # skip duplicate animal
    last_animal = normalized
    
    r = requests.get("https://api.pexels.com/videos/search", params={"query": q, "per_page": 15, "page": random.randint(1,5)}, headers={"Authorization": API}).json()
    for v in r.get("videos", []):
        vid = str(v["id"])
        dur = v.get("duration", 0)
        fn = f"{STOCK}/pexels_{vid}.mp4"
        if vid in used_ids or os.path.exists(fn):
            continue
        if dur >= needed:
            print(f"Downloading {vid} ({dur}s >= {needed}s needed) [{q}]...", end=" ", flush=True)
            if dl(vid, fn):
                print("OK")
                # Save to used_videos.txt with timestamp (vid,timestamp)
                with open(USED_FILE, 'a') as f:
                    f.write(f"{vid},{time.time()}\n")
                print(fn)
                exit(0)
            else:
                print("FAILED")
        time.sleep(0.3)
    time.sleep(0.5)

# No clip found - retry with cleared used_videos
print("No clip found. Retrying with fresh clip pool...")
with open(USED_FILE, 'r') as f:
    lines = f.readlines()
# Keep last 30 most recent
if len(lines) > 30:
    with open(USED_FILE, 'w') as f:
        f.writelines(lines[-30:])
    print(f"Cleared old entries from used_videos.txt, keeping last 30")

# Retry with cleared used_videos
used_ids = set()
with open(USED_FILE, 'r') as f:
    used_ids = {line.strip().split(',')[0] for line in f if line.strip()}
print(f"Retry with {len(used_ids)} used clips")

for q in searches:
    words = q.lower().split()
    animal = words[-1] if words else ''
    normalized = skip_animals_pl.get(animal, animal)
    if normalized == last_animal:
        continue
    last_animal = normalized

    r = requests.get("https://api.pexels.com/videos/search", params={"query": q, "per_page": 15, "page": random.randint(1,5)}, headers={"Authorization": API}).json()
    for v in r.get("videos", []):
        vid = str(v["id"])
        dur = v.get("duration", 0)
        fn = f"{STOCK}/pexels_{vid}.mp4"
        if vid in used_ids or os.path.exists(fn):
            continue
        if dur >= needed:
            print(f"RETRY Downloading {vid} ({dur}s) [{q}]...", end=" ", flush=True)
            if dl(vid, fn):
                print("OK")
                with open(USED_FILE, 'a') as f:
                    f.write(f"{vid},{time.time()}\n")
                print(fn)
                exit(0)
            else:
                print("FAILED")
        time.sleep(0.3)
    time.sleep(0.5)

print("ERROR: No suitable clip found after retry")
exit(1)
PYEOF

    return $?
}

cleanup_old_used_videos() {
    # Remove used_videos.txt entries older than 30 days
    local used_file="$BASE/used_videos.txt"
    if [ ! -f "$used_file" ]; then return 0; fi
    
    python3 << PYEOF 2>> $LOG
import time, os

used_file = "$used_file"
max_age_days = 30
max_age_sec = max_age_days * 24 * 3600
now = time.time()

if not os.path.exists(used_file):
    print("No used_videos.txt found")
    exit(0)

kept = []
removed = 0
with open(used_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        vid = parts[0]
        # No timestamp = old entry from before this feature
        # Treat as newly added so it expires in 30 days from now
        if len(parts) < 2 or not parts[1].strip():
            ts = now - (29 * 86400)  # 29 days ago — expires tomorrow
        age_days = (now - ts) / 86400
        if age_days < max_age_days:
            kept.append(line)
        else:
            removed += 1
            print(f"Removing old video {vid} ({age_days:.1f} days old)")

with open(used_file, 'w') as f:
    for line in kept:
        f.write(line + '\n')

print(f"Cleanup done: {removed} old entries removed, {len(kept)} kept")
PYEOF
}

generate_and_upload() {
    num=$(date +%s)
    
    # Clean up used videos older than 30 days
    cleanup_old_used_videos
    
    # 1. Generate TTS FIRST
    log "Generating TTS..."
    count=$(python3 -c "
import json, random
with open('$BASE/animal_facts.json') as f:
    data = json.load(f)
a = random.choice(data['animals'])
fact = random.choice(a['facts'])
words = len(fact['text'].split())
print(2 if words < 43 else 1)
")
    # Generate TTS with temp filename, will be renamed with animals
    python3 $BASE/facts_search.py $BASE/audio/fact_tmp.mp3 $count
    
    # Find the renamed TTS file (most recent .mp3, not ambient)
    TTS_FILE=$(ls -t $BASE/audio/*.mp3 2>/dev/null | grep -v fact_tmp | grep -v ambient | head -1)
    ANIMALS_FILE="${TTS_FILE%.*}_animals.txt"
    
    if [ -z "$TTS_FILE" ] || [ ! -f "$TTS_FILE" ]; then
        log "ERROR: TTS file not found after generation!"
        return 1
    fi
    
    ANIMALS=$(cat "$ANIMALS_FILE" 2>/dev/null || echo "ANIMALS")
    log "Animals in this short: $ANIMALS"
    
    # 2. Measure TTS duration
    dur=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$TTS_FILE" 2>/dev/null | cut -d. -f1)
    dur=${dur:-20}
    [ "$dur" -lt 10 ] && dur=20
    vid_dur=$((dur + 2))
    log "TTS: ${dur}s → Video: ${vid_dur}s"
    
    # 3. Download fresh clip using animal names as search terms
    log "Downloading fresh stock clip for $ANIMALS (need >= ${vid_dur}s)..."
    clip_path=$(download_clip $vid_dur "$ANIMALS")
    if [ $? -ne 0 ] || [ -z "$clip_path" ]; then
        log "Failed to download clip!"
        rm -f "$TTS_FILE" "${TTS_FILE}_animals.txt" 2>/dev/null
        return 1
    fi
    clip_path=$(echo "$clip_path" | tail -1)
    log "Using clip: $(basename $clip_path)"
    
    SHORT_FILE="$BASE/output/short_${num}.mp4"
    
    # 4. Render
    log "Rendering ${vid_dur}s video..."
    $FFMPEG -y -i "$clip_path" -i "$TTS_FILE" -i $BASE/audio/ambient_bgm.mp3 \
        -filter_complex "[0:v]trim=0:${vid_dur},setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,drawbox=y=120:h=220:c=black@0.7:t=fill,drawtext=text='Subscribe for daily animal facts!':fontcolor=yellow:fontsize=60:font=/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf:x=(w-text_w)/2:y=215:borderw=5:bordercolor=black@0.9[vid];[1:a]atrim=0:${vid_dur},asetpts=PTS-STARTPTS,volume=1.2[a];[2:a]atrim=0:${vid_dur},asetpts=PTS-STARTPTS,volume=0.35,afade=t=in:st=0:d=1[a2];[a][a2]amix=inputs=2:duration=first:normalize=0[m]" \
        -map "[vid]" -map "[m]" -c:v libx264 -preset ultrafast -crf 23 -c:a aac -b:a 128k -t ${vid_dur} -movflags +faststart $SHORT_FILE 2>/dev/null
    
    # 5. Delete stock clip and TTS immediately after render
    rm -f "$clip_path" "$TTS_FILE" "${TTS_FILE}_animals.txt"
    log "Deleted stock clip and TTS"
    
    if [ ! -f "$SHORT_FILE" ]; then
        log "Render failed!"
        return 1
    fi
    
    # 6. Send to Telegram and save message_id for later deletion
    log "Sending to Telegram..."
    resp=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT}/sendVideo" \
        -F "chat_id=${CHAT_ID}" \
        -F "video=@${SHORT_FILE}" \
        -F "caption=🦀 Dein neuer Short!")
    echo "$resp" >> $LOG
    msg_id=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['message_id'])" 2>/dev/null)
    log "Telegram message_id: $msg_id"
    
    # Save for later cleanup
    if [ -n "$msg_id" ]; then
        echo '{"msg_id": '$msg_id', "timestamp": '$(date +%s)'}' >> $BASE/telegram_messages.json
    fi
    
    # 7. Upload to YouTube
    log "Uploading to YouTube..."
    python3 << PYEOF >> $LOG 2>&1
import json, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Read animal names from sidecar file
try:
    with open("$ANIMALS_FILE", "r") as f:
        animals = f.read().strip().replace('|', ' #').lower()
        animal_hashtags = f"#{animals}" if animals else ""
except:
    animal_hashtags = ""

with open('credentials.json') as f:
    creds = Credentials.from_authorized_user_info(json.load(f))
if not creds.valid:
    creds.refresh(Request())

yt = build('youtube', 'v3', credentials=creds)
media = MediaFileUpload("$SHORT_FILE", chunksize=-1, resumable=True)
resp = yt.videos().insert(
    part='snippet,status',
    body={
        'snippet': {
            'title': 'Daily Animal Facts! 🐾 #shorts',
            'description': f'🐱 Like & Subscribe for daily animal facts!\n\n{animal_hashtags} #cuteanimals #animalfacts #dailyfacts',
            'tags': ['cute animals', 'animal facts', 'fun facts', 'wildlife', 'pets', 'baby animals', 'nature', 'educational', 'amazing facts', 'weird animals', 'animal kingdom', 'daily facts', 'shorts'],
            'categoryId': '15',
        },
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    },
    media_body=media
).execute()

print(f"Uploaded: https://youtu.be/{resp['id']}")
os.remove("$SHORT_FILE")
print("Deleted local short file")
PYEOF

    # 8. Cleanup
    find $BASE -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
    find $BASE -name "*.pyc" -delete 2>/dev/null
    log "Cleanup done"
}

log "Starting daily upload..."
generate_and_upload
log "Done"
