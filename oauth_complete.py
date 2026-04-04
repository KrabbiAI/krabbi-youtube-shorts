#!/usr/bin/env python3
"""YouTube OAuth - complete in one session"""
import json, http.server, socketserver, urllib.parse
from google_auth_oauthlib.flow import InstalledAppFlow

PORT = 8765
CODE = None

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global CODE
        p = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(p.query)
        if 'code' in q:
            CODE = q['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'OK - close this window')
        else:
            self.send_response(400)
            self.end_headers()
    def log_message(self, s, *a): pass

with open('/home/dobby/.openclaw/workspace/youtube-shorts/client_secret.json') as f:
    cc = json.load(f)

# Create ONE flow instance
flow = InstalledAppFlow.from_client_config(
    cc,
    ['https://www.googleapis.com/auth/youtube.upload'],
    redirect_uri=f'http://localhost:{PORT}'
)

# Generate URL (this stores code_verifier in flow)
url, _ = flow.authorization_url(prompt='consent', access_type='offline')
print('OPEN_THIS_URL_IN_BROWSER:' + url)

# Start server to catch the code
with socketserver.TCPServer(('', PORT), H) as httpd:
    httpd.handle_request()  # This blocks until user visits URL

# User visited and authorized - now fetch token WITH SAME FLOW
if CODE:
    flow.fetch_token(code=CODE)  # Uses stored code_verifier
    c = flow.credentials
    with open('/home/dobby/.openclaw/workspace/youtube-shorts/credentials.json', 'w') as f:
        json.dump({
            'token': c.token,
            'refresh_token': c.refresh_token,
            'token_uri': c.token_uri,
            'client_id': c.client_id,
            'client_secret': c.client_secret,
            'scopes': list(c.scopes)
        }, f, indent=2)
    print('SUCCESS')
else:
    print('FAILED_NO_CODE')
