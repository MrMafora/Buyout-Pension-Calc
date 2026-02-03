# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## TTS / Voice

- **Provider:** Edge TTS (free, no API key needed)
- **Voice:** `en-US-GuyNeural` — male, steady, slightly dramatic
- **Settings:** +10% rate (slightly faster), -5% pitch (slightly deeper)
- **Fallback:** None needed — Edge TTS is the free tier
- **Mode:** Full Thunder — voice on every reply

## Speech-to-Text / Whisper

- **Engine:** whisper.cpp (local, CPU-only)
- **Model:** base.en (74MB, good balance of speed/accuracy)
- **Location:** `/tmp/whisper.cpp/`
- **Script:** `/usr/local/bin/transcribe.sh`
- **Usage:** `transcribe.sh <audio.ogg>` → outputs text
- **Note:** Converts OGG→WAV automatically, 16kHz mono

## Email

- **Provider:** GoDaddy
- **Support Email:** support@fedbuyout.com (contact form, user inquiries)
- **Business Email:** clark@fedbuyout.com (operations, notifications)
- **Gmail Account:** fedbuyout@gmail.com (Google services, Analytics, Search Console)
- **Resend API:** For transactional emails (welcome, notifications)
- **Test Email:** mmafora@gmail.com (backup notifications)

## Web Browser

- **Browser:** Chromium (via snap)
- **Path:** `/snap/bin/chromium`
- **Mode:** Headless (no GUI)
- **Usage:** I can visit websites, take screenshots, fill forms, click elements
- **Config:** Set in `openclaw.json` under `browser` section

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
