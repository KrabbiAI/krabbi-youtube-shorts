"""
Text-to-Speech using gTTS (free, no API key needed)
"""

import os
from gtts import gTTS
from config import AUDIO_DIR


def create_tts(text: str, output_name: str, lang: str = "en") -> str:
    """Create TTS audio file from text."""
    output_path = os.path.join(AUDIO_DIR, f"{output_name}.mp3")
    
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)
    
    return output_path


# Test
if __name__ == "__main__":
    test_text = "Oh my goodness! Look at these adorable little creatures!"
    result = create_tts(test_text, "test")
    print(f"Created: {result}")
