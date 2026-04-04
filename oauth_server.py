#!/usr/bin/env python3
"""
YouTube OAuth with HTTP server to capture redirect
"""
import json
import http.server
import socketserver
import urllib.parse
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

PORT = 8765

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    auth_code = None
    
    def do_GET(self):
        # Parse the redirect URL
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in query:
            OAuthHandler.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Auth Complete!</h1><p>You can close this window.</p></body></html>')
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def main():
    # Load client secrets
    with open('/home/dobby/.openclaw/workspace/youtube-shorts/client_secret.json', 'r') as f:
        client_config = json.load(f)
    
    # Create flow with callback to our server
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=f'http://localhost:{PORT}'
    )
    
    # Generate auth URL
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print(f"\nOpen this URL in your browser:\n")
    print(auth_url)
    print(f"\n⏳ Waiting for authorization...")
    
    # Start HTTP server in background
    with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
        # Handle request in a way that lets us get the code
        httpd.handle_request()  # Just one request
    
    if OAuthHandler.auth_code:
        print(f"\n📝 Got auth code: {OAuthHandler.auth_code[:30]}...")
        
        # Exchange for tokens
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=f'http://localhost:{PORT}'
        )
        flow.fetch_token(code=OAuthHandler.auth_code)
        credentials = flow.credentials
        
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
        
        print("\n✅ OAuth complete! Credentials saved.")
        print(f"\nYouTube Channel: {credentials.client_id}")
    else:
        print("\n❌ No auth code received")

if __name__ == '__main__':
    main()
