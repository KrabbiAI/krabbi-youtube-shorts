#!/usr/bin/env python3
"""
Dynamic Animal Facts Generator - ElevenLabs Edition
Selects random UNUSED animal facts, generates TTS narration
"""
import json
import random
import os
import sys
import hashlib
import requests

BASE = "/home/dobby/.openclaw/workspace/youtube-shorts"
FACTS_FILE = f"{BASE}/animal_facts.json"
USED_FILE = f"{BASE}/used_facts.json"
CREDS_FILE = "/home/dobby/.openclaw/workspace/credentials.json"

# ElevenLabs config
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah
MODEL_ID = "eleven_v3"

def get_api_key():
    with open(CREDS_FILE, 'r') as f:
        creds = json.load(f)
    return creds.get('elevenlabs', {}).get('api_key', '')

def load_used_ids():
    if os.path.exists(USED_FILE):
        with open(USED_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def mark_fact_used(fact_id):
    used = load_used_ids()
    used.add(fact_id)
    with open(USED_FILE, 'w') as f:
        json.dump(list(used), f)

def get_random_unused_facts(count=1):
    """Get random facts that haven't been used yet"""
    with open(FACTS_FILE, 'r') as f:
        data = json.load(f)
    
    used = load_used_ids()
    
    # Collect all unused facts
    unused = []
    for animal in data['animals']:
        for fact in animal['facts']:
            if fact['id'] not in used:
                unused.append((fact['id'], fact['text'], animal['name']))
    
    if len(unused) < count:
        print(f"WARNING: Only {len(unused)} unused facts left! Need to research more.")
        return [], unused  # Return what we have
    
    selected = random.sample(unused, count)
    return [(f[0], f[1], f[2]) for f in selected], unused

def research_new_facts(target_count=20):
    """Research new animal facts with similar wordcount (~15-20 words)"""
    # New animals to add facts for
    new_animals = [
        {"name": "Wolves", "examples": ["Wolves howl to communicate with their pack over 6 miles away!", "A wolf pack can have up to 30 members with a strict hierarchy!"]},
        {"name": "Bats", "examples": ["Bats are the only mammals that can truly fly long distances!", "A single bat can eat up to 1,000 mosquitoes in just one hour!"]},
        {"name": "Rhinoceros", "examples": ["Rhino horns are made of keratin, the same as human fingernails!", "Despite their massive size, rhinos can charge at 40 miles per hour!"]},
        {"name": "Peacocks", "examples": ["Only male peacocks have the colorful tail feathers for attracting mates!", "A peacock's tail feathers can be up to 6 feet long!"]},
        {"name": "Squirrels", "examples": ["Squirrels plant thousands of trees by forgetting where they buried their acorns!", "A squirrel's front teeth never stop growing and must be worn down by chewing!"]},
        {"name": "Bees", "examples": ["Honeybees can recognize human faces and remember them for days!", "A bee visits 50 to 100 flowers in a single collection trip!"]},
        {"name": "Goldfish", "examples": ["Goldfish can remember things for at least 3 months, not just seconds!", "A goldfish can actually see more colors than humans can perceive!"]},
        {"name": "Camels", "examples": ["A camel can drink up to 40 gallons of water in one sitting!", "Camels have three eyelids to protect their eyes from sand and sun!"]},
        {"name": "Chameleons", "examples": ["Chameleons can move their eyes independently in two directions at once!", "A chameleon's tongue can be twice the length of its entire body!"]},
        {"name": "Narwhals", "examples": ["The narwhal's spiral tusk is actually an overgrown tooth!", "Narwhals can dive over a mile deep and hold their breath for 25 minutes!"]},
        {"name": "Platypus", "examples": ["The platypus is one of the few mammals that actually lays eggs!", "A platypus can detect electric fields from prey hidden underground!"]},
        {"name": "Leopards", "examples": ["Leopards can drag prey three times their weight high into trees!", "Each leopard has a unique spot pattern like a human fingerprint!"]},
        {"name": "Snowy Owls", "examples": ["Snowy owls have feathers covering even their toes to survive Arctic cold!", "Unlike most owls, snowy owls hunt during the day because of the midnight sun!"]},
        {"name": "Eagles", "examples": ["An eagle's eyesight is 8 times more powerful than a human's!", "Bald eagles can lock their talons in place while flying to conserve energy!"]},
        {"name": "Alligators", "examples": ["Alligators can go through 3,000 teeth in their entire lifetime!", "An alligator's bite force measures over 2,000 pounds!"]},
        {"name": "Hippos", "examples": ["Hippos can run 20 miles per hour despite their massive size!", "Hippos secrete a natural red-colored mucus that acts as sunscreen!"]},
        {"name": "Crocodiles", "examples": ["Crocodiles can hold their breath for over an hour underwater!", "A crocodile's bite force is even stronger than a T-Rex dinosaur's!"]},
        {"name": "Woodpeckers", "examples": ["Woodpeckers can peck up to 20 times per second without getting headaches!", "A woodpecker's tongue wraps around the back of its brain for protection!"]},
        {"name": "Moles", "examples": ["Moles can dig tunnels up to 300 feet per day!", "A mole's nose is so sensitive it can detect tiny earthworms underground!"]},
        {"name": "Seahorses", "examples": ["Male seahorses are the ones who get pregnant and give birth!", "A seahorse can change color to blend perfectly with its surroundings!"]},
    ]
    
    with open(FACTS_FILE, 'r') as f:
        data = json.load(f)
    
    # Find existing animal names
    existing_names = {a['name'] for a in data['animals']}
    
    added = 0
    for animal_data in new_animals:
        if animal_data['name'] in existing_names:
            continue
        
        # Generate facts with similar wordcount (15-20 words)
        facts = []
        for example in animal_data['examples'][:4]:
            fid = hashlib.md5(example.encode()).hexdigest()[:12]
            facts.append({'id': fid, 'text': example})
        
        if len(facts) >= 2:
            data['animals'].append({'name': animal_data['name'], 'facts': facts})
            added += 1
            print(f"Added {len(facts)} facts for {animal_data['name']}")
        
        if len(data['animals']) >= target_count + 50:  # Stop when we have enough
            break
    
    with open(FACTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Research complete! Added {added} new animals. Total: {len(data['animals'])}")
    return added

def generate_tts(narration, output_file):
    """Generate TTS audio file using ElevenLabs"""
    api_key = get_api_key()
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": narration,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=60)
    
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file
    else:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: facts_search.py <output.mp3> [count]")
        sys.exit(1)
    
    output_file = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # Check if we're running low on facts
    unused_count = len(get_random_unused_facts(0)[1])
    print(f"Available unused facts: {unused_count}")
    
    if unused_count < 10:
        print("Running low on facts! Researching new ones...")
        research_new_facts()
    
    result, all_unused = get_random_unused_facts(count)
    
    if len(result) < count:
        print(f"Only {len(result)} unused facts available!")
        count = len(result)
        if count == 0:
            print("ERROR: No facts left!")
            sys.exit(1)
    
    # Extract fact texts and animal names
    facts = [f[1] for f in result]
    fact_ids = [f[0] for f in result]
    animal_names = [f[2] for f in result]
    animals_str = '_'.join(animal_names).upper()
    
    print(f"Selected {len(facts)} fact(s): {[f[:50]+'...' for f in facts]}")
    print(f"Animals: {', '.join(animal_names)}")
    
    # Build narration
    if len(facts) == 1:
        narration = f"Did you know? {facts[0]} Like and subscribe for more daily animal facts!"
    else:
        narration = "Did you know? " + " And did you know? ".join(facts) + " Like and subscribe for more daily animal facts!"
    
    print(f"Narration: {narration}")
    
    # Generate TTS to temp file first, then rename with animals
    import tempfile
    temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
    os.close(temp_fd)
    generate_tts(narration, temp_path)
    
    # Rename to include animals in filename
    # e.g., /path/fact_tmp.mp3 -> /path/fact_CROWS_OCTOPUSES.mp3
    base_name = os.path.basename(output_file).replace('.mp3', '')
    final_path = output_file.replace(base_name, animals_str)
    os.rename(temp_path, final_path)
    
    # Save animal names to sidecar file
    with open(f'{final_path}_animals.txt', 'w') as f:
        f.write(animals_str)
    
    print(f"TTS saved: {final_path}")
    print(f"Animals: {animals_str}")
    
    # Mark as used
    for fid in fact_ids:
        mark_fact_used(fid)
    print(f"Marked {len(fact_ids)} fact(s) as used")
