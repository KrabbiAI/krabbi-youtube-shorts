#!/usr/bin/env python3
"""YouTube Shorts Uploader"""
import json
import google.auth
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

CREDENTIALS_FILE = '/home/dobby/.openclaw/workspace/youtube-shorts/credentials.json'

def get_authenticated_service():
    with open(CREDENTIALS_FILE) as f:
        creds_data = json.load(f)
    
    credentials = google.auth.credentials.Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
        scopes=creds_data.get('scopes')
    )
    
    if not credentials.valid:
        credentials.refresh(Request())
    
    return build('youtube', 'v3', credentials=credentials)

def upload_short(video_path, title, description, tags):
    youtube = get_authenticated_service()
    
    response = youtube.channels().list(part='snippet,contentDetails', mine=True).execute()
    channel_id = response['items'][0]['id']
    
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '15',
                'channelId': channel_id,
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False,
            }
        },
        media_body=media
    )
    
    response = request.execute()
    return response['id']

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 upload.py <video_file> [title]")
        sys.exit(1)
    
    video = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Cute Animals Short"
    description = "Watch these adorable animals! #shorts #cuteanimals"
    tags = ["cute animals", "baby animals", "pets", "viral"]
    
    vid_id = upload_short(video, title, description, tags)
    print(f"SUCCESS: https://youtu.be/{vid_id}")
