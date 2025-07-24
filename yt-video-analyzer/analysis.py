import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def load_comments(filename):
    """Load comments from JSON file"""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_sentiments(comments):
    """Analyze sentiment for each comment"""
    analyzer = SentimentIntensityAnalyzer()
    results = {
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "details": []
    }
    for comment in comments:
        sentiment = analyzer.polarity_scores(comment)
        compound = sentiment["compound"]
        if compound >= 0.05:
            label = "Positive"
            results["positive"] += 1
        elif compound <= -0.05:
            label = "Negative"
            results["negative"] += 1
        else:
            label = "Neutral"
            results["neutral"] += 1
        results["details"].append({
            "comment": comment,
            "sentiment": label
        })
    return results

def main():
    comments = load_comments("comments.json")
    print(f"[+] Loaded {len(comments)} comments.")  # Changed ✓ to [+]
    sentiment_data = analyze_sentiments(comments)
    total = len(comments)
    if total > 0:
        positive_percent = (sentiment_data['positive'] / total) * 100
        sentiment_data["positive_percent"] = round(positive_percent, 2)
        sentiment_data["total"] = total
        # Save results
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(sentiment_data, f, ensure_ascii=False, indent=2)
        print("[+] Sentiment analysis completed and saved to results.json.")
    else:
        print("[!] No comments to analyze.")

if __name__ == "__main__":
    main()
