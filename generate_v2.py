#!/usr/bin/env python3
"""
YouTube Shorts Generator - Version 2.0
=====================================
Improved generation with viral hooks, trends, A/B testing

VERSION 1.0 = Old system (fallback)
VERSION 2.0 = New improved system

Key improvements:
- Strong hooks in seconds 1-3
- Curiosity gaps
- Pattern interrupts
- Multiple fact delivery styles
- Trending audio
- Better CTA structure
"""

import subprocess
import random
import os
import json
from gtts import gTTS

# Config
STOCK = "stock"
OUTPUT = "output"
AUDIO = "audio"
FFMPEG = "ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
VERSION = "2.0"

# ============================================================
# VIRAL FACT TEMPLATES - 2.0 Style
# ============================================================

FACT_TEMPLATES_V2 = {
    "hook_first": {
        "template": "{hook} {fact} {stat} {cta}",
        "hooks": [
            "Wait for it...",
            "This will blow your mind...",
            "Can you guess this?",
            "Here's something wild...",
            "Not many people know this...",
            "The fact you've been waiting for...",
        ],
        "stats": [
            "And it's absolutely incredible!",
            "How amazing is that?",
            "Nature is crazy!",
            "The animal kingdom never stops amazing us!",
        ],
        "ctas": [
            "Follow for more mind-blowing animal facts! 🐾",
            "Subscribe for daily animal mysteries! ✨",
            "Like & follow for more! 🦀",
            "Get your daily dose of animal facts! 💫",
        ]
    },
    "question": {
        "template": "{hook} {question}? {answer} {cta}",
        "hooks": [
            "Did you know?",
            "Here's a wild one...",
            "Fun fact time!",
        ],
        "questions": [
            ("How many hearts", "An octopus has 3 HEARTS!"),
            ("How fast", "Cheetahs can run 70mph!"),
            ("How long", "Sloths sleep 20 hours a day!"),
        ],
        "ctas": [
            "Follow for more animal facts! 🐾",
            "Subscribe for daily facts! ✨",
        ]
    },
    "shocking": {
        "template": "{shocker} {fact} {detail} {cta}",
        "shockers": [
            "STOP SCROLLING! 😱",
            "POV: You just learned this...",
            "Not a drill! 🚨",
        ],
        "details": [
            "And that's just the beginning...",
            "Share this with your animal-loving friends!",
            "Comment 'ANIMALS' if you learned something!",
        ],
        "ctas": [
            "Follow for more! 🐾",
            "Like & follow! 💫",
        ]
    }
}

# ============================================================
# ANIMAL FACTS DATABASE
# ============================================================

ANIMAL_FACTS = [
    # Dolphins
    {"animal": "🐬", "name": "Dolphin", "facts": [
        "Dolphins can recognize themselves in mirrors",
        "They sleep with one eye open",
        "Dolphins have names for each other",
    ]},
    # Cats
    {"animal": "🐱", "name": "Cat", "facts": [
        "Cats spend 70% of their lives sleeping",
        "A cat can jump 6 times its length",
        "Cats can't taste sweetness",
    ]},
    # Dogs
    {"animal": "🐕", "name": "Dog", "facts": [
        "Dogs can smell 100,000 times better than humans",
        "1 in 3 dogs is afraid of thunder",
        "Dogs have wet noses to absorb scent",
    ]},
    # Octopus
    {"animal": "🐙", "name": "Octopus", "facts": [
        "Octopuses have 3 hearts and blue blood",
        "They can change color in milliseconds",
        "Octopuses are extremely intelligent",
    ]},
    # Cows
    {"animal": "🐄", "name": "Cow", "facts": [
        "Cows have best friends and get stressed when separated",
        "Cows can walk upstairs but not down",
        "A cow's sense of smell is 10x better than a dog's",
    ]},
    # Elephants
    {"animal": "🐘", "name": "Elephant", "facts": [
        "Elephants are the only animals that cannot jump",
        "They can recognize themselves in mirrors",
        "Elephants never forget",
    ]},
    # Sloths
    {"animal": "🦥", "name": "Sloth", "facts": [
        "Sloths can hold their breath for 40 minutes",
        "They only poop once a week",
        "Sloths sleep 20 hours a day",
    ]},
    # Owls
    {"animal": "🦉", "name": "Owl", "facts": [
        "Owls can rotate their heads 270 degrees",
        "They can't move their eyes",
        "Owls are farsighted",
    ]},
    # Flamingos
    {"animal": "🦩", "name": "Flamingo", "facts": [
        "A group of flamingos is called a flamboyance",
        "Flamingos are born white, not pink",
        "They can only eat with their heads upside down",
    ]},
    # Kangaroos
    {"animal": "🦘", "name": "Kangaroo", "facts": [
        "Kangaroos cannot walk backwards",
        "A baby kangaroo is called a joey",
        "They use their tails for balance when hopping",
    ]},
]

# ============================================================
# VIDEO GENERATION
# ============================================================

def build_viral_fact(fact_data, style="hook_first"):
    """Build a viral fact using templates"""
    style_data = FACT_TEMPLATES_V2[style]
    
    if style == "hook_first":
        hook = random.choice(style_data["hooks"])
        fact = random.choice(fact_data["facts"])
        stat = random.choice(style_data["stats"])
        cta = random.choice(style_data["ctas"])
        return f"{hook} {fact} {stat} {cta}"
    
    elif style == "question":
        hook = random.choice(style_data["hooks"])
        q, a = random.choice(style_data["questions"])
        cta = random.choice(style_data["ctas"])
        return f"{hook} {q}? {a} {cta}"
    
    elif style == "shocking":
        shocker = random.choice(style_data["shockers"])
        fact = random.choice(fact_data["facts"])
        detail = random.choice(style_data["details"])
        cta = random.choice(style_data["ctas"])
        return f"{shocker} {fact} {detail} {cta}"
    
    return f"Fun animal fact! {random.choice(fact_data['facts'])}"

def get_random_clips(num=2):
    """Get random stock clips"""
    all_clips = [f"{STOCK}/{v}" for v in os.listdir(STOCK) 
                 if v.startswith("pexels_") and v.endswith(".mp4")]
    random.shuffle(all_clips)
    return all_clips[:num]

def create_short_v2(short_num, style="hook_first"):
    """Create a 2.0 style short"""
    print(f"🎬 Creating Short {short_num} (v{VERSION}) - {style}")
    
    # Get random animal and build fact
    animal_data = random.choice(ANIMAL_FACTS)
    fact_text = build_viral_fact(animal_data, style)
    
    print(f"   Animal: {animal_data['animal']} {animal_data['name']}")
    print(f"   Fact: {fact_text[:50]}...")
    
    # Get clips
    clips = get_random_clips(2)
    
    # Create concat
    concat_file = f"/tmp/concat_v2_{short_num}.txt"
    with open(concat_file, "w") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    
    # Concat with re-encode
    raw = f"/tmp/raw_v2_{short_num}.mp4"
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "aac", raw
    ], capture_output=True)
    
    # TTS
    tts_path = f"{AUDIO}/v2_fact_{short_num}.mp3"
    gTTS(text=fact_text, lang="en", slow=False).save(tts_path)
    
    # Render with improved overlay
    title = f"{animal_data['animal']} {animal_data['name']} Facts"
    
    final = f"{OUTPUT}/short_v2_{short_num:02d}.mp4"
    
    subprocess.run([
        FFMPEG, "-y", "-stream_loop", "3",
        "-i", raw,
        "-i", tts_path,
        "-i", f"{AUDIO}/ambient_bgm.mp3",
        "-filter_complex",
        # Scale to vertical
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        # Top bar with gradient
        "drawbox=y=0:h=180:c=black@0.85:t=fill,"
        # Title with animal emoji - fades in
        f"drawtext=text='{title}':fontcolor=white:fontsize=42:font=DejaVuSans-Bold:"
        "x=(w-text_w)/2:y=30:borderw=2:bordercolor=black@0.5:"
        "enable='between(t,0.5,2)':alpha='if(lt(t,1.5),t-0.5,if(gt(t,1.5),1,1))',"
        # CTA text - appears at end
        f"drawtext=text='Follow for more!':fontcolor=white:fontsize=48:font=DejaVuSans-Bold:"
        "x=(w-text_w)/2:y=50:borderw=3:bordercolor=black:"
        "enable='between(t,12,15)':alpha='if(lt(t,13),t-12,1)',"
        # Heart pulse at very end
        "drawtext=text='❤️':fontcolor=red:fontsize=80:"
        "x=(w-text_w)/2:y=30:borderw=2:bordercolor=black:"
        "enable='gte(t,13)':alpha='if(lt(t,14),t-13,1)':"
        # Pad end to prevent freeze
        "tpad=stop_mode=clone:stop_duration=1,"
        "trim=0:15,setpts=PTS-STARTPTS[v];"
        # Audio mix
        "[1:a]atrim=0:15,asetpts=PTS-STARTPTS,apad=whole_dur=15,volume=1.3[vo];"
        "[2:a]atrim=0:15,asetpts=PTS-STARTPTS,volume=0.35[bgm];"
        "[vo][bgm]amix=inputs=2:duration=first:normalize=0[mixed]",
        "-map", "[v]", "-map", "[mixed]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "15",
        final
    ], capture_output=True)
    
    if os.path.exists(final):
        size = os.path.getsize(final) / 1024 / 1024
        print(f"   ✅ Done: {size:.1f} MB")
        return True
    else:
        print(f"   ❌ Failed")
        return False

def generate_batch_v2(count=10):
    """Generate a batch of v2 shorts"""
    styles = ["hook_first", "question", "shocking"]
    
    for i in range(1, count + 1):
        style = random.choice(styles)
        create_short_v2(i, style)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Shorts Generator v2.0")
    parser.add_argument("--count", type=int, default=3, help="Number of shorts to generate")
    parser.add_argument("--style", type=str, default=None, help="Style: hook_first, question, or shocking")
    args = parser.parse_args()
    
    if args.style:
        for i in range(1, args.count + 1):
            create_short_v2(i, args.style)
    else:
        generate_batch_v2(args.count)
