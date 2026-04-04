#!/bin/bash
# Deletes Telegram messages older than 10 hours
TELEGRAM_BOT="8798400513:AAHVGh4T2dtsEXZML6zmtXLNLVPM4lpAcZE"
CHAT_ID="631196199"
MSG_FILE="/home/dobby/.openclaw/workspace/youtube-shorts/telegram_messages.json"
MAX_AGE_HOURS=10

if [ ! -f "$MSG_FILE" ]; then
    exit 0
fi

# Read messages and delete old ones
python3 << PYEOF
import json, time, os, subprocess

msg_file = "$MSG_FILE"
max_age_seconds = $MAX_AGE_HOURS * 3600
current_time = time.time()

try:
    with open(msg_file, 'r') as f:
        messages = json.load(f)
except:
    messages = []

if not messages:
    exit(0)

remaining = []
for msg in messages:
    age = current_time - msg.get('timestamp', 0)
    if age < max_age_seconds:
        remaining.append(msg)
        print(f"Keeping message {msg['msg_id']} (age: {age/3600:.1f}h)")
    else:
        print(f"Deleting message {msg['msg_id']} (age: {age/3600:.1f}h)")
        # Delete via Telegram API
        subprocess.run([
            'curl', '-s', 
            'https://api.telegram.org/bot${TELEGRAM_BOT}/deleteMessage',
            '-F', f'chat_id=${CHAT_ID}',
            '-F', f'message_id={msg["msg_id"]}'
        ])

# Save remaining messages
with open(msg_file, 'w') as f:
    json.dump(remaining, f)

print(f"Cleanup done. {len(remaining)} messages remaining.")
PYEOF
