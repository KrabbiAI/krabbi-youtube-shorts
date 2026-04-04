#!/usr/bin/env python3
"""
YouTube OAuth Authentication Flow
Generates auth URL for user to visit, then captures the code
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'
]

def main():
    # Load client secrets
    with open('/home/dobby/.openclaw/workspace/youtube-shorts/client_secret.json', 'r') as f:
        client_config = json.load(f)
    
    # Create flow
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='http://localhost'
    )
    
    # Generate authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print("\n" + "="*60)
    print("🔗 AUTHORIZATION URL:")
    print("="*60)
    print(auth_url)
    print("="*60)
    print("\n1. Copy the URL above")
    print("2. Open it in your browser")
    print("3. Authorize the app")
    print("4. You'll be redirected to localhost (which won't load)")
    print("5. Copy the FULL URL from your browser address bar")
    print("6. Paste it here")
    print("="*60 + "\n")
    
    # Get the authorization code from user
    redirect_response = input("Paste the redirected URL here: ").strip()
    
    # Exchange code for tokens
    flow.fetch_token(authorization_response=redirect_response)
    credentials = flow.credentials
    
    print("\n✅ Authentication successful!")
    
    # Save credentials
    creds_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    with open('/home/dobby/.openclaw/workspace/youtube-shorts/credentials.json', 'w') as f:
        json.dump(creds_data, f, indent=2)
    
    print("\nCredentials saved to credentials.json")

if __name__ == '__main__':
    main()
