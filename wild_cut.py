#!/usr/bin/env python3
"""
Wild Cut Short Generator
Takes 12min stock video and creates 15s shorts with RANDOM fast cuts
"""
import subprocess
import random
import os
import json

BASE = "/home/dobby/.openclaw/workspace/youtube-shorts"
FFMPEG = f"{BASE}/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
STOCK = f"{BASE}/stock/full_stock.mp4"
OUTPUT = f"{BASE}/output"
AUDIO = f"{BASE}/audio"

def get_duration(path):
    cmd = [FFMPEG, "-i", path, "2>&1"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration:" in line:
            dur = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur.split(":")
            return int(h)*3600 + int(m)*60 + float(s)
    return 0

def create_random_segments(num_segments=10, min_dur=1.0, max_dur=1.8):
    """Create random segment cuts from stock video."""
    total_dur = get_duration(STOCK)
    segments = []
    
    for i in range(num_segments):
        start = random.uniform(0, total_dur - max_dur)
        dur = random.uniform(min_dur, max_dur)
        segments.append((start, dur))
    
    return segments

def extract_segments(segments, output_prefix):
    """Extract random segments from stock."""
    clip_paths = []
    
    for i, (start, dur) in enumerate(segments):
        clip_path = f"/tmp/wild_clip_{output_prefix}_{i}.mp4"
        cmd = [
            FFMPEG, "-y",
            "-ss", str(start),
            "-i", STOCK,
            "-t", str(dur),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            clip_path
        ]
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1000:
            clip_paths.append(clip_path)
    
    return clip_paths

def concat_clips(clip_paths, output_name):
    """Concatenate clips into single video."""
    concat_file = f"/tmp/concat_{output_name}.txt"
    with open(concat_file, "w") as f:
        for clip in clip_paths:
            f.write(f"file '{clip}'\n")
    
    output = f"/tmp/raw_{output_name}.mp4"
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Cleanup
    for clip in clip_paths:
        if os.path.exists(clip):
            os.remove(clip)
    os.remove(concat_file)
    
    return output

def make_wild_short(short_num, breed, fact_text, tts_path):
    """Create a wild-cut 15s short."""
    print(f"\n🎬 Creating short_{short_num} (wild cuts)...")
    print(f"   Breed: {breed}")
    
    # Create random segments (10-12 cuts for wild pacing)
    num_cuts = random.randint(10, 14)  # 1-1.5s per cut
    segments = create_random_segments(num_cuts=num_cuts, min_dur=0.8, max_dur=1.5)
    
    print(f"   Cutting {len(segments)} random segments...")
    
    # Extract segments
    clip_paths = extract_segments(segments, f"short_{short_num}")
    
    if not clip_paths:
        print(f"   ERROR: No clips extracted!")
        return None
    
    # Shuffle clips for maximum randomness
    random.shuffle(clip_paths)
    
    print(f"   Shuffled {len(clip_paths)} clips")
    
    # Concatenate
    raw_path = concat_clips(clip_paths, f"short_{short_num}")
    
    if not os.path.exists(raw_path):
        print(f"   ERROR: Concat failed!")
        return None
    
    # Final render with text + TTS + BGM
    final_path = f"{OUTPUT}/wild_{short_num}.mp4"
    bgm = f"{AUDIO}/ambient_bgm.mp3"
    
    cmd = [
        FFMPEG, "-y",
        "-i", raw_path,
        "-i", tts_path,
        "-i", bgm,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "drawbox=y=1600:h=200:c=black@0.6:t=fill,"
        "drawtext=text='{breed}':fontcolor=white:fontsize=56:font=DejaVuSans-Bold:"
        "x=(w-text_w)/2:y=1640:borderw=3:bordercolor=black,"
        "trim=0:15,setpts=PTS-STARTPTS[v];"
        "[1:a]atrim=0:15,asetpts=PTS-STARTPTS,apad=whole_dur=15,volume=1.2[vo];"
        "[2:a]atrim=0:15,asetpts=PTS-STARTPTS,volume=0.5[bgm];"
        "[vo][bgm]amix=inputs=2:duration=first:normalize=0[mixed]",
        "-map", "[v]", "-map", "[mixed]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "15",
        final_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    # Cleanup
    if os.path.exists(raw_path):
        os.remove(raw_path)
    
    if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
        dur = get_duration(final_path)
        size = os.path.getsize(final_path) / 1024 / 1024
        print(f"   ✅ Done: {dur:.1f}s | {size:.1f}MB")
        return {"path": final_path, "duration": dur, "size": size}
    
    print(f"   ERROR: {result.stderr[-200:]}")
    return None

if __name__ == "__main__":
    import sys
    
    # Short definitions
    shorts = [
        {"num": 14, "breed": "Border Collie", "fact": 1},
        {"num": 15, "breed": "French Bulldog", "fact": 2},
        {"num": 16, "breed": "British Shorthair", "fact": 3},
        {"num": 17, "breed": "Angora Rabbit", "fact": 4},
        {"num": 18, "breed": "Corgi", "fact": 5},
        {"num": 19, "breed": "Ragdoll Cat", "fact": 6},
        {"num": 20, "breed": "Lop Bunny", "fact": 7},
        {"num": 21, "breed": "Pomeranian", "fact": 8},
        {"num": 22, "breed": "Munchkin Cat", "fact": 9},
        {"num": 23, "breed": "Holland Lop", "fact": 10},
    ]
    
    # Generate new TTS for shorts 14-23
    facts = {
        1: "A group of hedgehogs is called an array! Cows can walk upstairs but not down. Penguins propose to their partners with pebbles!",
        2: "Butterflies taste with their feet! A flea can jump 150 times its body length. An ostrich's eye is bigger than its brain!",
        3: "Sharks existed before trees! The great white shark has been around for 16 million years. Honey never spoils!",
        4: "Owls can rotate their heads 270 degrees! Cats cannot taste sweetness. Starfish do not have blood!",
        5: "Elephants are the only animals that cannot jump! A group of porcupines is called a prickle! Sloths can hold their breath for 40 minutes!",
        6: "Dolphins sleep with one eye open! A group of crows is called a murder. Octopuses have three hearts!",
        7: "Kangaroos cannot walk backwards! A group of jellyfish is called a smack! Koalas have fingerprints like humans!",
        8: "Crocodiles cannot stick their tongues out! Hummingbirds are the only birds that can fly backwards!",
        9: "Otters hold hands while sleeping! A group of owls is called a parliament. Cows produce more milk when listening to music!",
        10: "An ant can lift 50 times its body weight! A group of ferrets is called a business. Dragonflies have 360 degree vision!"
    }
    
    from gtts import gTTS
    
    for s in shorts:
        num = s["num"]
        tts_path = f"{AUDIO}/short_{num}_fact.mp3"
        if not os.path.exists(tts_path):
            print(f"Generating TTS {num}...")
            tts = gTTS(text=facts[s["fact"]], lang="en", slow=False)
            tts.save(tts_path)
    
    # Create shorts
    for s in shorts:
        tts_path = f"{AUDIO}/short_{s['num']}_fact.mp3"
        result = make_wild_short(s["num"], s["breed"], None, tts_path)
        
    print("\n✅ All wild shorts created!")
