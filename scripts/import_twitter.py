#!/usr/bin/env python3
"""
Import tweets from a Twitter archive dump into Jekyll archive collection.
Parses tweets.js and tweets-part1.js from the Twitter data export.
"""

import json
import re
import html
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "all_collections" / "_archive"
MEDIA_SRC_DIR = Path(
    "/Users/frankemanuele/Downloads/_Social_Archives/Twitter Archive Demo/"
    "twitter-2023-07-05-96c7f4d59736364e17260edc6654ed27c001ed5f587db431b5b105e712c7da6b/data/tweets_media"
)
MEDIA_DEST_DIR = BASE_DIR / "assets" / "images" / "archive" / "twitter"

TWITTER_DATA_DIR = Path(
    "/Users/frankemanuele/Downloads/_Social_Archives/Twitter Archive Demo/"
    "twitter-2023-07-05-96c7f4d59736364e17260edc6654ed27c001ed5f587db431b5b105e712c7da6b/data"
)

USERNAME = "FrankRamblings"

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:80]

def make_title(text, max_len=60):
    clean = text.replace('\n', ' ').strip()
    if len(clean) <= max_len:
        return clean
    truncated = clean[:max_len].rsplit(' ', 1)[0]
    return truncated + '...'

def parse_twitter_date(date_str):
    """Parse Twitter's date format: 'Tue Jan 24 18:40:22 +0000 2023'"""
    return datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')

def expand_urls(text, entities):
    """Replace t.co URLs with their expanded versions."""
    if not entities or 'urls' not in entities:
        return text
    # Sort by start index descending to avoid offset issues
    urls = sorted(entities['urls'], key=lambda u: u.get('indices', [0])[0], reverse=True)
    for url_entity in urls:
        short = url_entity.get('url', '')
        expanded = url_entity.get('expanded_url', short)
        if short and expanded:
            text = text.replace(short, expanded)
    return text

def expand_mentions(text, entities):
    """Convert @mentions to markdown links."""
    if not entities or 'user_mentions' not in entities:
        return text
    for mention in entities['user_mentions']:
        screen_name = mention.get('screen_name', '')
        if screen_name:
            text = re.sub(
                rf'@{re.escape(screen_name)}\b',
                f'[@{screen_name}](https://twitter.com/{screen_name})',
                text,
                flags=re.IGNORECASE
            )
    return text

def is_retweet(tweet):
    """Check if this is a retweet."""
    text = tweet.get('full_text', '')
    if text.startswith('RT @'):
        return True
    if tweet.get('retweeted_status') or tweet.get('retweeted_status_result'):
        return True
    return False

def is_reply_to_others(tweet):
    """Check if this is a reply to someone else (not a self-reply/thread)."""
    reply_to = tweet.get('in_reply_to_screen_name', '')
    if reply_to and reply_to.lower() != USERNAME.lower():
        return True
    return False

def get_media(tweet):
    """Extract media from tweet, copying local files from the archive dump.
    Returns list of local asset paths (relative to site baseurl)."""
    local_paths = []
    tweet_id = tweet.get('id_str', '')
    entities = tweet.get('extended_entities', tweet.get('entities', {}))

    for media in entities.get('media', []):
        media_url = media.get('media_url_https', media.get('media_url', ''))
        if not media_url:
            continue

        # Find matching file in tweets_media/ directory
        # Filenames are like: {tweet_id}-{hash}.{ext}
        matching = list(MEDIA_SRC_DIR.glob(f"{tweet_id}-*"))
        if not matching:
            # Try the media URL filename
            url_filename = media_url.split('/')[-1]
            matching = list(MEDIA_SRC_DIR.glob(f"*{url_filename}*"))

        for src_file in matching:
            if src_file.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                dest_file = MEDIA_DEST_DIR / src_file.name
                if not dest_file.exists():
                    shutil.copy2(src_file, dest_file)
                local_paths.append(f"/assets/images/archive/twitter/{src_file.name}")

    return local_paths

def load_tweets():
    """Load tweets from all tweet files in the archive."""
    all_tweets = []
    for fname in ['tweets.js', 'tweets-part1.js']:
        path = TWITTER_DATA_DIR / fname
        if not path.exists():
            continue
        with open(path) as f:
            raw = f.read()
            # Strip the JS variable assignment
            json_str = raw.split(' = ', 1)[1]
            tweets = json.loads(json_str)
            all_tweets.extend(tweets)
            print(f"  Loaded {len(tweets)} tweets from {fname}")
    return all_tweets

def write_tweet(tweet_id, date, text, original_url, media_paths=None):
    """Write a single tweet as a markdown file."""
    title = make_title(text)
    filename = f"{date.strftime('%Y-%m-%d')}-twitter-{tweet_id}.md"
    filepath = ARCHIVE_DIR / filename

    if filepath.exists():
        return False, filename

    permalink = f"/archive/social/twitter/{tweet_id}/"
    # Sanitize title for YAML: remove backslashes and control chars, escape quotes
    yaml_title = title.replace('\\', '')
    yaml_title = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', yaml_title)
    yaml_title = yaml_title.replace('"', '\\"')

    lines = [
        '---',
        f'title: "{yaml_title}"',
        f'date: "{date.strftime("%Y-%m-%d")}"',
        f'type: "social"',
        f'platform: "twitter"',
        f'permalink: "{permalink}"',
        f'original_url: "{original_url}"',
        '---',
        '',
        text,
        '',
    ]

    if media_paths:
        for path in media_paths:
            lines.append(f'![image]({{{{site.baseurl}}}}{path})')
            lines.append('')

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    return True, filename

def main():
    print("Twitter Archive Importer")
    print("=" * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DEST_DIR.mkdir(parents=True, exist_ok=True)

    raw_tweets = load_tweets()
    print(f"  Total raw tweets: {len(raw_tweets)}")

    imported = 0
    skipped_rt = 0
    skipped_reply = 0
    skipped_empty = 0
    skipped_exists = 0
    errors = 0

    for item in raw_tweets:
        try:
            tweet = item.get('tweet', item)

            # Skip retweets
            if is_retweet(tweet):
                skipped_rt += 1
                continue

            # Skip replies to others (keep self-replies/threads)
            if is_reply_to_others(tweet):
                skipped_reply += 1
                continue

            tweet_id = tweet.get('id_str', '')
            text = tweet.get('full_text', '')

            if not text.strip() or not tweet_id:
                skipped_empty += 1
                continue

            date = parse_twitter_date(tweet['created_at'])
            entities = tweet.get('entities', {})

            # Expand t.co URLs and @mentions
            text = expand_urls(text, entities)
            text = expand_mentions(text, entities)
            text = html.unescape(text)

            # Remove trailing media URLs (they show as images instead)
            text = re.sub(r'\s*https://t\.co/\w+\s*$', '', text)

            original_url = f"https://twitter.com/{USERNAME}/status/{tweet_id}"
            media_paths = get_media(tweet)

            created, filename = write_tweet(tweet_id, date, text, original_url, media_paths)

            if created:
                imported += 1
                if imported <= 3 or imported % 5000 == 0:
                    print(f"  + {filename}")
            else:
                skipped_exists += 1

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Imported:        {imported}")
    print(f"  Skipped (RT):    {skipped_rt}")
    print(f"  Skipped (reply): {skipped_reply}")
    print(f"  Skipped (empty): {skipped_empty}")
    print(f"  Skipped (exist): {skipped_exists}")
    print(f"  Errors:          {errors}")

if __name__ == '__main__':
    main()
