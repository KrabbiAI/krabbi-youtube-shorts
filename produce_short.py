#!/usr/bin/env python3
"""
YouTube Short Producer - Fixed version with tpad to prevent freeze
"""
import subprocess
import random
import os
from gtts import gTTS

STOCK = "stock"
OUTPUT = "output"
AUDIO = "audio"
FFMPEG = "ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
SHORT_DURATION = 15

def get_dur(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    for l in r.stderr.split("\n"):
        if "Duration:" in l:
            t = l.split("Duration:")[1].split(",")[0].strip()
            h,m,s = t.split(":")
            return int(h)*3600 + int(m)*60 + float(s)
    return 0

def create_short(short_num, clips, title_text, fact_text):
    print(f"Creating Short {short_num}: {title_text}")
    
    concat_file = f"/tmp/concat_{short_num}.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")
    
    raw = f"/tmp/raw_{short_num}.mp4"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", raw], capture_output=True)
    
    tts_path = f"{AUDIO}/fact_{short_num}.mp3"
    gTTS(text=fact_text, lang="en", slow=False).save(tts_path)
    
    final = f"{OUTPUT}/short_{short_num:02d}.mp4"
    
    subprocess.run([
        FFMPEG, "-y",
        "-stream_loop", "3",
        "-i", raw,
        "-i", tts_path,
        "-i", f"{AUDIO}/ambient_bgm.mp3",
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawbox=y=1600:h=200:c=black@0.6:t=fill,"
        f"drawtext=text='{title_text}':fontcolor=white:fontsize=48:font=DejaVuSans-Bold:"
        f"x=(w-text_w)/2:y=1640:borderw=3:bordercolor=black,"
        f"tpad=stop_mode=clone:stop_duration=1,"  # FIX: prevent freeze at end
        f"trim=0:{SHORT_DURATION},setpts=PTS-STARTPTS[v];"
        f"[1:a]atrim=0:{SHORT_DURATION},asetpts=PTS-STARTPTS,apad=whole_dur={SHORT_DURATION},volume=1.2[vo];"
        f"[2:a]atrim=0:{SHORT_DURATION},asetpts=PTS-STARTPTS,volume=0.4[bgm];"
        f"[vo][bgm]amix=inputs=2:duration=first:normalize=0[mixed]",
        "-map", "[v]", "-map", "[mixed]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(SHORT_DURATION),
        final
    ], capture_output=True)
    
    if os.path.exists(final):
        print(f"  ✅ {os.path.getsize(final)/1024/1024:.1f} MB")
    else:
        print(f"  ❌ Failed")

if __name__ == "__main__":
    stock = [f"{STOCK}/{v}" for v in os.listdir(STOCK) if v.startswith("pexels_") and v.endswith(".mp4")]
    random.shuffle(stock)
    
    facts = {
        1: "Did you know? Dolphins can recognize themselves in mirrors! They also sleep with one eye open! Dogs have a sense of smell 10,000 times better than humans! Subscribe for more animal facts!",
        2: "Here's an amazing fact! Cats spend 70% of their lives sleeping! That's 13 years out of 18! A cat can jump six times its length! Subscribe for more animal facts!",
        3: "Fun animal fact! Cows have best friends and get stressed when separated! An octopus has three hearts and blue blood! Subscribe for more animal facts!"
    }
    
    for i in range(1, 4):
        clips = stock[(i-1)*2 : (i-1)*2 + 2]
        create_short(i, clips, "Subscribe for daily animal facts", facts[i])
