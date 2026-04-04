"""
YouTube Shorts - Cute Animals Automation
Free tools only: yt-dlp, FFmpeg, gTTS
"""

import os

# Paths
BASE_DIR = "/home/dobby/.openclaw/workspace/youtube-shorts"
FFMPEG = f"{BASE_DIR}/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
FFPROBE = f"{BASE_DIR}/ffmpeg-master-latest-linux64-gpl/bin/ffprobe"
CLIPS_DIR = f"{BASE_DIR}/clips"
OUTPUT_DIR = f"{BASE_DIR}/output"
AUDIO_DIR = f"{BASE_DIR}/audio"
THUMBNAILS_DIR = f"{BASE_DIR}/thumbnails"

# Video settings
SHORT_DURATION = 15  # seconds
TARGET_RES = (1080, 1920)  # 9:16 vertical
TARGET_FPS = 30

# Fast cut settings - switch clip every N seconds
CUT_EVERY = 2  # seconds between cuts

# Free animal video sources (YouTube channels with reusable content)
ANIMAL_SOURCES = [
    # Pexels Animals collection - free to use
    "https://www.pexels.com/search/videos/cute%20puppies/",
    "https://www.pexels.com/search/videos/kittens/",
    "https://www.pexels.com/search/videos/cute%20bunnies/",
]

# Alternative: Direct YouTube search for animal shorts
YOUTUBE_SEARCH_TERMS = [
    "cute puppies compilation",
    "kittens playing",
    "baby animals funny",
    "cute bunnies",
]

# TTS settings
TTS_LANG = "en"
TTS_SPEED = 1.1  # slightly faster for short pace
