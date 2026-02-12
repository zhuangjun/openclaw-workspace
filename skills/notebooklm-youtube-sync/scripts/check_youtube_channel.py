#!/usr/bin/env python3
"""
YouTube Channel Monitor - 监控 YouTube 频道最新视频
Usage: python3 check_youtube_channel.py <channel_url_or_id> [--last-check <timestamp_file>]
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

def run_ytdlp(url, options):
    """Run yt-dlp with given options"""
    # Try to find yt-dlp in common locations
    ytdlp_paths = [
        "/Users/daniel/Library/Python/3.14/bin/yt-dlp",
        "/Users/daniel/Library/Python/3.13/bin/yt-dlp",
        "/Users/daniel/Library/Python/3.12/bin/yt-dlp",
        "/usr/local/bin/yt-dlp",
        "yt-dlp",
    ]
    
    ytdlp_cmd = None
    for path in ytdlp_paths:
        if path.startswith("/") and os.path.exists(path):
            ytdlp_cmd = path
            break
        elif path == "yt-dlp":
            # Check if yt-dlp is in PATH
            try:
                subprocess.run(["which", "yt-dlp"], capture_output=True, check=True)
                ytdlp_cmd = path
                break
            except:
                continue
    
    if not ytdlp_cmd:
        print("yt-dlp not found. Please install: pip3 install --user yt-dlp", file=sys.stderr)
        return None
    
    cmd = [ytdlp_cmd] + options + [url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"yt-dlp error: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Error running yt-dlp: {e}", file=sys.stderr)
        return None

def get_channel_videos(channel_input, limit=10):
    """Get recent videos from a YouTube channel"""
    
    # Determine if it's a channel URL, handle, or ID
    if channel_input.startswith("http"):
        url = channel_input
    elif channel_input.startswith("@"):
        # Handle like @MrBeast
        url = f"https://www.youtube.com/{channel_input}"
    elif channel_input.startswith("UC"):
        # Channel ID
        url = f"https://www.youtube.com/channel/{channel_input}"
    else:
        # Try as handle first
        url = f"https://www.youtube.com/@{channel_input}"
    
    # Get video list with metadata
    options = [
        "--flat-playlist",
        "--playlist-end", str(limit),
        "--print", "%(id)s|%(title)s|%(upload_date)s|%(webpage_url)s",
        "--dateafter", "now-7days",  # Only videos from last 7 days
    ]
    
    output = run_ytdlp(url, options)
    if not output:
        return []
    
    videos = []
    for line in output.strip().split("\n"):
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 4:
                videos.append({
                    "id": parts[0],
                    "title": parts[1],
                    "upload_date": parts[2],
                    "url": parts[3]
                })
    
    return videos

def get_last_check_time(state_file):
    """Get the last check timestamp from state file"""
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
                return data.get("last_check")
        except:
            pass
    return None

def save_state(state_file, last_check, seen_videos):
    """Save the state to file"""
    data = {
        "last_check": last_check,
        "seen_videos": seen_videos
    }
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(data, f, indent=2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_youtube_channel.py <channel_url_or_id> [--state-file <path>]")
        sys.exit(1)
    
    channel_input = sys.argv[1]
    state_file = "/Users/daniel/.openclaw/workspace/skills/notebooklm-youtube-sync/data/state.json"
    
    # Parse arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--state-file" and i + 1 < len(sys.argv):
            state_file = sys.argv[i + 1]
    
    # Get last check time
    last_check = get_last_check_time(state_file)
    
    # Fetch recent videos
    videos = get_channel_videos(channel_input, limit=20)
    
    if not videos:
        print(json.dumps({"new_videos": [], "error": "No videos found or error occurred"}))
        return
    
    # Load seen videos
    seen_videos = set()
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
                seen_videos = set(data.get("seen_videos", []))
        except:
            pass
    
    # Find new videos
    new_videos = []
    for video in videos:
        if video["id"] not in seen_videos:
            new_videos.append(video)
            seen_videos.add(video["id"])
    
    # Save state
    current_time = datetime.now().isoformat()
    save_state(state_file, current_time, list(seen_videos))
    
    # Output results
    result = {
        "channel": channel_input,
        "checked_at": current_time,
        "new_videos": new_videos,
        "total_seen": len(seen_videos)
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
