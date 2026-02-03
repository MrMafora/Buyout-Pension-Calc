#!/usr/bin/env python3
import os
import sys
from requests_oauthlib import OAuth1Session

CONSUMER_KEY = "yElqGTVlW0jRtnPPR1yyrWi2B"
CONSUMER_SECRET = "xSZ1V8hi7WsN41EkqlAKyzmmSRVJ2bI3GRk56cFJdflJp1qJWi"
PIN = sys.argv[1]

# Load temp tokens
with open("/tmp/twitter_oauth_temp", "r") as f:
    lines = f.readlines()
    resource_owner_key = lines[0].strip()
    resource_owner_secret = lines[1].strip()

oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
                      resource_owner_key=resource_owner_key,
                      resource_owner_secret=resource_owner_secret,
                      verifier=PIN)

try:
    oauth_tokens = oauth.fetch_access_token("https://api.twitter.com/oauth/access_token")
    access_token = oauth_tokens.get("oauth_token")
    access_token_secret = oauth_tokens.get("oauth_token_secret")
    
    print(f"ACCESS_TOKEN={access_token}")
    print(f"ACCESS_TOKEN_SECRET={access_token_secret}")
    
except Exception as e:
    print(f"Error: {e}")
