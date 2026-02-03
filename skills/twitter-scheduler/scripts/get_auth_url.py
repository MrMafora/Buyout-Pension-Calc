#!/usr/bin/env python3
import os
import sys
from requests_oauthlib import OAuth1Session

# New keys he provided
CONSUMER_KEY = "yElqGTVlW0jRtnPPR1yyrWi2B"
CONSUMER_SECRET = "xSZ1V8hi7WsN41EkqlAKyzmmSRVJ2bI3GRk56cFJdflJp1qJWi"

# Step 1: Get request token
request_token_url = "https://api.twitter.com/oauth/request_token"
oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='oob')

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    
    # Step 2: Get authorization URL
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    
    print(f"URL: {authorization_url}")
    # Save the temp tokens to a file so we can resume step 2 later
    with open("/tmp/twitter_oauth_temp", "w") as f:
        f.write(f"{resource_owner_key}\n{resource_owner_secret}")
        
except Exception as e:
    print(f"Error: {e}")
