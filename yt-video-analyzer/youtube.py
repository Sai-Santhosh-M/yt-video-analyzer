import re
import sys
import json
from googleapiclient.discovery import build

# Optional: keep stdout in utf-8 (useful on Windows)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

API_KEY = "AIzaSyDbhkSs-OmVqTHdDDpeR5MQf0SNIVoJw3c"  # replace with your actual key if needed

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_comments(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=100,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"[✓] Fetched {len(comments)} comments.")
    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[!] Usage: python youtube.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)

    if not video_id:
        print("[X] Could not extract video ID from URL.")
        sys.exit(1)

    try:
        fetch_comments(video_id, API_KEY)
    except Exception as e:
        print("[X] Failed to fetch comments:", str(e))
