#!/bin/bash
# produce_short.sh - Complete YouTube Short Production
# Usage: ./produce_short.sh <short_num> <narration_text> <breed_name> <clips...>

FFMPEG="/home/dobby/.openclaw/workspace/youtube-shorts/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
BASE="/home/dobby/.openclaw/workspace/youtube-shorts"
OUTPUT="$BASE/output"
AUDIO="$BASE/audio"

SHORT_NUM=$1
NARRATION=$2
BREED_NAME=$3
shift 3
CLIPS=("$@")

SHORT_NAME="short_${SHORT_NUM}"
FINAL="$OUTPUT/${SHORT_NAME}_final.mp4"
BGM="$AUDIO/happy_bgm_final.mp3"
TTS="$AUDIO/${SHORT_NAME}_fact.mp3"

echo "🎬 Producing $SHORT_NAME..."
echo "   Breed: $BREED_NAME"
echo "   Fact: $NARRATION"

# Step 1: Generate TTS voiceover
python3 -c "from gtts import gTTS; gTTS(text='$NARRATION', lang='en', slow=False).save('$TTS')"
if [ ! -f "$TTS" ]; then
    echo "ERROR: TTS failed"
    exit 1
fi
echo "   ✅ TTS created"

# Step 2: Create concat file for clips
CONCAT_FILE="/tmp/concat_${SHORT_NAME}.txt"
> "$CONCAT_FILE"
for clip in "${CLIPS[@]}"; do
    echo "file '$clip'" >> "$CONCAT_FILE"
done

# Step 3: Concatenate clips into raw video (no encoding for speed)
DRAFT="$OUTPUT/${SHORT_NAME}_raw.mp4"
$FFMPEG -y -f concat -safe 0 -i "$CONCAT_FILE" -c copy "$DRAFT" 2>/dev/null
if [ ! -f "$DRAFT" ]; then
    echo "ERROR: Concat failed"
    exit 1
fi
echo "   ✅ Clips concatenated ($(du -h "$DRAFT" | cut -f1))"

# Step 4: Get durations
VIDEO_DUR=$($FFMPEG -i "$DRAFT" 2>&1 | grep Duration | awk '{print $2}' | tr -d ',')
TTS_DUR=$($FFMPEG -i "$TTS" 2>&1 | grep Duration | awk '{print $2}' | tr -d ',')
echo "   Video: $VIDEO_DUR, TTS: $TTS_DUR"

# Step 5: Build complete video with text overlay + voiceover + music
# Text overlay: breed name at bottom center
# Voiceover: TTS narration  
# BGM: background music (reduced volume)
$FFMPEG -y \
    -i "$DRAFT" \
    -i "$TTS" \
    -i "$BGM" \
    -filter_complex "
        [0:v]scale=1080:1920:force_original_aspect_ratio=increase,
             crop=1080:1920,
             drawbox=y=1600:h=200:c=black@0.6:t=fill,
             drawtext=text='$BREED_NAME':fontcolor=white:fontsize=64:font=DejaVuSans-Bold:x=(w-text_w)/2:y=1640:borderw=3:bordercolor=black,
             trim=0:15,setpts=PTS-STARTPTS[v];
        [1:a]atrim=0:15,asetpts=PTS-STARTPTS[vo];
        [2:a]atrim=0:15,asetpts=PTS-STARTPTS,volume=0.25[bgm];
        [vo][bgm]amix=inputs=2:duration=first:normalize=0[mixed]
    " \
    -map "[v]" -map "[mixed]" \
    -c:v libx264 -preset fast -crf 22 \
    -c:a aac -b:a 128k \
    -t 15 \
    -shortest \
    "$FINAL" 2>&1 | tail -5

if [ ! -f "$FINAL" ] || [ $(stat -c%s "$FINAL") -lt 10000 ]; then
    echo "ERROR: Final video failed"
    exit 1
fi

echo ""
echo "🎉 $SHORT_NAME complete!"
echo "   📹 $FINAL"
echo "   📊 $(du -h "$FINAL" | cut -f1)"
echo ""
echo "📝 YOUTUBE METADATA:"
echo "   Title: $BREED_NAME Facts That Will Blow Your Mind! 🐾 #$SHORT_NUM"
echo "   Description: Did you know? $NARRATION Watch till the end! #animals #facts #$BREED_NAME"
