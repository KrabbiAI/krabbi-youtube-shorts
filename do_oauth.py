#!/usr/bin/env python3
"""YouTube OAuth - complete flow in one script"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

CODE = "4/0Aci98E8TRt7D7NgvxsYMufbVoXGERQRvjbgzSqSGiDa4CbP7efndepcFF-m2_3w7le9Aug"

with open('/home/dobby/.openclaw/workspace/youtube-shorts/client_secret.json') as f:
    cc = json.load(f)

# Create flow and fetch token WITH THE SAME INSTANCE
flow = InstalledAppFlow.from_client_config(
    cc,
    ['https://www.googleapis.com/auth/youtube.upload'],
    redirect_uri='http://localhost:8765'
)
flow.fetch_token(code=CODE)
c = flow.credentials

creds = {
    'token': c.token,
    'refresh_token': c.refresh_token,
    'token_uri': c.token_uri,
    'client_id': c.client_id,
    'client_secret': c.client_secret,
    'scopes': list(c.scopes)
}
with open('/home/dobby/.openclaw/workspace/youtube-shorts/credentials.json', 'w') as f:
    json.dump(creds, f, indent=2)
print("DONE - token saved")
