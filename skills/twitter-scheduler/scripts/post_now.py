#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
from requests_oauthlib import OAuth1

# Load environment variables
def load_env():
    env_path = "/root/.openclaw/workspace/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

load_env()

# Credentials
CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    print("❌ Error: Missing Twitter API credentials in .env")
    sys.exit(1)

def post_tweet(text):
    url = "https://api.twitter.com/2/tweets"
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    payload = {"text": text}
    
    print(f"🚀 Posting to Twitter: {text[:50]}...")
    
    try:
        response = requests.post(url, auth=auth, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            tweet_id = data['data']['id']
            print(f"✅ Success! Tweet ID: {tweet_id}")
            print(f"🔗 URL: https://twitter.com/user/status/{tweet_id}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: post_now.py \"Tweet text here\"")
        sys.exit(1)
        
    text = sys.argv[1]
    post_tweet(text)
