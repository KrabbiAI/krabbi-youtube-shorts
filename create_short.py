#!/usr/bin/env python3
"""
Create a 15-second YouTube Short with fast cuts + TTS narration
Uses: FFmpeg (video editing), gTTS (voiceover), yt-dlp (download)
"""

import os
import sys
import subprocess
import random
from config import (
    FFMPEG, FFPROBE, CLIPS_DIR, OUTPUT_DIR, AUDIO_DIR,
    SHORT_DURATION, TARGET_RES
)

# Narrations for cute animal shorts
NARRATIONS = [
    "Oh my goodness! Look at these adorable puppies!",
    "Warning: Extreme cuteness ahead!",
    "This is what happiness looks like!",
]


def get_video_info(path: str) -> dict:
    """Get video duration and resolution."""
    cmd = [FFPROBE, "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,duration", 
           "-of", "csv=p=0", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        w, h, d = result.stdout.strip().split(',')
        return {"width": int(w), "height": int(h), "duration": float(d)}
    except:
        return {"width": 0, "height": 0, "duration": 5}


def scale_clip_toVertical(input_path: str, output_name: str) -> str:
    """Scale and center crop a clip to 9:16 vertical."""
    output_path = os.path.join(CLIPS_DIR, f"{output_name}_vertical.mp4")
    
    cmd = [
        FFMPEG, "-y",
        "-i", input_path,
        "-vf", f"scale={TARGET_RES[0]}:-1:center_y=in_h/2,crop={TARGET_RES[0]}:{TARGET_RES[1]}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-t", "5",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path


def create_fast_cut_video(clip_paths: list, output_name: str) -> str:
    """Create fast-cut video from multiple clips using filter_complex."""
    output_path = os.path.join(OUTPUT_DIR, f"{output_name}.mp4")
    
    if not clip_paths:
        print("No clips provided!")
        return None
    
    # First, scale all clips to vertical format
    scaled_clips = []
    for i, clip in enumerate(clip_paths):
        info = get_video_info(clip)
        if info["width"] == 0:
            continue
        scaled = scale_clip_toVertical(clip, f"{output_name}_clip_{i}")
        if os.path.exists(scaled) and os.path.getsize(scaled) > 1000:
            scaled_clips.append(scaled)
    
    if len(scaled_clips) < 2:
        print("Not enough valid clips!")
        return None
    
    # Calculate how many clips we need for 15 seconds (2s each = 7-8 clips)
    cuts_needed = SHORT_DURATION // 2  # 2 second cuts
    while len(scaled_clips) < cuts_needed:
        scaled_clips.extend(scaled_clips[:min(len(scaled_clips), cuts_needed - len(scaled_clips))])
    scaled_clips = scaled_clips[:cuts_needed]
    
    # Build filter_complex for fast switching
    # Each clip gets displayed for 2 seconds
    filter_parts = []
    for i, clip in enumerate(scaled_clips):
        filter_parts.append(f"[{i}:v]")
    
    filter_str = ";".join([f"{p}trim=0:2,setpts=PTS-STARTPTS[v{i}]" for i, p in enumerate(filter_parts)])
    
    # Concatenate
    concat_filter = "".join([f"[v{i}][v{i}]" for i in range(len(scaled_clips))])
    concat_filter += f"concat=n={len(scaled_clips)}:v=1:a=0[outv]"
    
    # Use intermediate approach - just concat the scaled clips directly
    concat_file = os.path.join(OUTPUT_DIR, f"{output_name}_concat.txt")
    with open(concat_file, 'w') as f:
        for clip in scaled_clips:
            f.write(f"file '{clip}'\n")
    
    # Concatenate
    concat_output = os.path.join(OUTPUT_DIR, f"{output_name}_full.mp4")
    cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        concat_output
    ]
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0 or not os.path.exists(concat_output):
        print(f"Concat failed: {result.stderr}")
        return None
    
    # Trim to exactly 15 seconds if longer
    if os.path.getsize(concat_output) > 1000:
        actual_duration = get_duration(concat_output)
        if actual_duration > SHORT_DURATION:
            cmd = [
                FFMPEG, "-y",
                "-i", concat_output,
                "-t", str(SHORT_DURATION),
                "-c:v", "copy",
                "-c:a", "copy",
                output_path
            ]
            subprocess.run(cmd, capture_output=True)
            os.remove(concat_output)
        else:
            os.rename(concat_output, output_path)
        
        # Cleanup
        for clip in scaled_clips:
            if os.path.exists(clip):
                os.remove(clip)
        os.remove(concat_file)
        
        return output_path
    
    return None


def add_tts_to_video(video_path: str, tts_path: str, output_name: str) -> str:
    """Combine video with TTS audio."""
    output_path = os.path.join(OUTPUT_DIR, f"{output_name}_with_audio.mp4")
    
    # Get durations
    video_duration = get_duration(video_path)
    tts_duration = get_duration(tts_path)
    
    # Make TTS the full length of video (overwrite original audio)
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", tts_path,
        "-t", str(video_duration),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Replace original with audio version
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        os.replace(output_path, video_path)
    
    return video_path


def get_duration(path: str) -> float:
    """Get duration of media file in seconds."""
    cmd = [FFPROBE, "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return SHORT_DURATION


def generate_title(short_num: int) -> dict:
    """Generate title, description, tags for a short."""
    templates = [
        f"Adorable Baby Animals Compilation 🐾 #{short_num}",
        f"Cute Animals That Will Make Your Day Better ✨ #{short_num}",
        f"15 Seconds of Pure Cuteness! 💖 #{short_num}",
        f"Unbelievably Cute Animals 🐶🐱 #{short_num}",
        f"Animals So Cute You'll Melt 🫠 #{short_num}",
    ]
    
    descriptions = [
        "Watch these adorable creatures and smile today!\n\n#cuteanimals #babyanimals #animals #funny #wholesome",
        "Because you deserve a little cuteness today 💕\n\n#pets #cute #animals #viral #shorts",
        "Nature's most adorable moments captured!\n\n#wildlife #cuteanimals #babyanimals #nature",
    ]
    
    return {
        "title": random.choice(templates),
        "description": random.choice(descriptions),
        "tags": "cute animals,baby animals,puppies,kittens,adorable,happy,wholesome"
    }


def make_short(clip_paths: list, narration: str, short_num: int) -> dict:
    """Create a complete short from clips and narration."""
    short_name = f"short_{short_num:02d}"
    
    print(f"\n🎬 Creating {short_name}...")
    
    # Step 1: Create fast-cut video
    video_path = create_fast_cut_video(clip_paths, short_name)
    if not video_path or not os.path.exists(video_path) or os.path.getsize(video_path) < 1000:
        return {"error": f"Failed to create video for {short_name}"}
    
    # Step 2: Create TTS
    from tts import create_tts
    tts_path = create_tts(narration, short_name)
    
    # Step 3: Combine video + TTS
    final_path = add_tts_to_video(video_path, tts_path, short_name)
    
    # Step 4: Generate metadata
    metadata = generate_title(short_num)
    metadata["tts_path"] = tts_path
    metadata["video_path"] = final_path
    
    # Check file size
    if os.path.exists(final_path):
        size_mb = os.path.getsize(final_path) / 1024 / 1024
        metadata["size_mb"] = round(size_mb, 2)
    
    print(f"✅ Created: {final_path}")
    print(f"   Title: {metadata['title']}")
    
    return metadata


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create YouTube Short from animal clips")
    parser.add_argument("--clips", nargs="+", required=True, help="Paths to clip files")
    parser.add_argument("--narration", required=True, help="TTS narration text")
    parser.add_argument("--num", type=int, default=1, help="Short number")
    
    args = parser.parse_args()
    result = make_short(args.clips, args.narration, args.num)
    
    if "error" not in result:
        print(f"\n📹 Output: {result['video_path']}")
        print(f"   Size: {result.get('size_mb', '?')} MB")
