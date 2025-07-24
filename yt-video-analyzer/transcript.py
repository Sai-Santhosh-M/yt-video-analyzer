import sys
import json
import re
from youtube_transcript_api import YouTubeTranscriptApi
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript])
        return text
    except Exception as e:
        print("[X] Could not fetch transcript:", str(e))
        return None

def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentences_count=2)
    summary_text = " ".join(str(sentence) for sentence in summary)
    # Truncate to ~40 words
    words = summary_text.split()
    if len(words) > 40:
        summary_text = " ".join(words[:40]) + "..."
    return summary_text

def main():
    if len(sys.argv) < 2:
        print("[!] Usage: python transcript.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)
    if not video_id:
        print("[X] Could not extract video ID.")
        sys.exit(1)

    text = get_transcript_text(video_id)
    if text:
        summary = summarize_text(text)
        data = {"summary": summary}
        with open("summary.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[OK] Saved short summary to summary.json")
    else:
        data = {"summary": "Transcript not available for this video."}
        with open("summary.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[X] Transcript not available, saved fallback message.")

if __name__ == "__main__":
    main()
