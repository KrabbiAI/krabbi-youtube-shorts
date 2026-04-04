"""
Download cute animal video clips using yt-dlp
Uses free YouTube sources with reusable content
"""

import os
import subprocess
from config import CLIPS_DIR, FFMPEG

# Free-to-use animal video channels (Creative Commons or permitted)
# These have compilations we can cut up
SOURCES = [
    # YouTube channel IDs/URLs with cute animal content
    "https://www.youtube.com/@BabyAnimalsHD",
    "https://www.youtube.com/@CuteAnimalsComp",
]


def download_clip(url: str, output_name: str, duration: int = 30) -> str:
    """Download a video clip from YouTube."""
    output_path = os.path.join(CLIPS_DIR, f"{output_name}.mp4")
    
    if os.path.exists(output_path):
        print(f"Already exists: {output_path}")
        return output_path
    
    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",  # 720p max for smaller files
        "--download-sections", f"*:0:{duration}",  # First N seconds only
        "-o", output_path,
        "--no-playlist",
        "--quiet",
        url
    ]
    
    print(f"Downloading: {url}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    return output_path


def cut_clip(input_path: str, output_name: str, start: float = 0, duration: float = 5) -> str:
    """Cut a specific section from a video clip."""
    output_path = os.path.join(CLIPS_DIR, f"{output_name}_cut.mp4")
    
    cmd = [
        FFMPEG,
        "-y",
        "-i", input_path,
        "-ss", str(start),
        "-t", str(duration),
        "-f", "mp4",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True)
    return output_path


def get_video_duration(path: str) -> float:
    """Get duration of video file in seconds."""
    cmd = [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


if __name__ == "__main__":
    # Test download
    print("Testing clip download...")
    # For actual use, add your source URLs
