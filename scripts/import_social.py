#!/usr/bin/env python3
"""
Import social media posts from Mastodon and Bluesky into Jekyll archive collection.
Mastodon: Public API (no auth needed)
Bluesky: AT Protocol public API (no auth needed for public feeds)
"""

import requests
import re
import html
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "all_collections" / "_archive"
SOCIAL_PAGES_DIR = BASE_DIR / "archive" / "social"

# --- Utilities ---

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:80]

def clean_html(text):
    if not text:
        return ""
    # Convert <br> and <p> to newlines
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>\s*<p>', '\n\n', text)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()

def make_title(text, max_len=60):
    """Generate a title from the first ~60 chars of post text."""
    clean = text.replace('\n', ' ').strip()
    if len(clean) <= max_len:
        return clean
    # Cut at word boundary
    truncated = clean[:max_len].rsplit(' ', 1)[0]
    return truncated + '...'

def ensure_platform_page(platform):
    """Create archive/social/<platform>/index.html if it doesn't exist."""
    platform_dir = SOCIAL_PAGES_DIR / platform
    index_file = platform_dir / "index.html"
    if index_file.exists():
        return
    platform_dir.mkdir(parents=True, exist_ok=True)
    content = f"""---
layout: archive-list
title: "{platform.capitalize()}"
permalink: /archive/social/{platform}/
archive_type: social
archive_platform: {platform}
---
"""
    with open(index_file, 'w') as f:
        f.write(content)
    print(f"  Created platform page: archive/social/{platform}/index.html")

def write_social_post(platform, post_id, date, text, original_url, media_urls=None):
    """Write a single social media post as a markdown file."""
    title = make_title(text)
    safe_id = str(post_id)
    filename = f"{date.strftime('%Y-%m-%d')}-{platform}-{safe_id}.md"
    filepath = ARCHIVE_DIR / filename

    if filepath.exists():
        return False, filename

    permalink = f"/archive/social/{platform}/{post_id}/"

    # Escape quotes in title for YAML
    yaml_title = title.replace('"', '\\"')

    lines = [
        '---',
        f'title: "{yaml_title}"',
        f'date: "{date.strftime("%Y-%m-%d")}"',
        f'type: "social"',
        f'platform: "{platform}"',
        f'permalink: "{permalink}"',
        f'original_url: "{original_url}"',
        '---',
        '',
        text,
        '',
    ]

    # Append media as markdown images
    if media_urls:
        for url in media_urls:
            lines.append(f'![image]({url})')
            lines.append('')

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    return True, filename


# --- Mastodon ---

def get_mastodon_account_id(instance, username):
    """Look up account ID from username."""
    url = f"https://{instance}/api/v1/accounts/lookup?acct={username}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()['id']

def fetch_mastodon_statuses(instance, account_id, max_pages=None):
    """Fetch all public statuses for an account, paginating through."""
    all_statuses = []
    url = f"https://{instance}/api/v1/accounts/{account_id}/statuses"
    params = {
        'limit': 40,
        'exclude_replies': 'false',
        'exclude_reblogs': 'true',
    }
    page = 0

    while url:
        page += 1
        if max_pages and page > max_pages:
            break

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        statuses = resp.json()

        if not statuses:
            break

        all_statuses.extend(statuses)

        if page % 5 == 0:
            print(f"  Fetched {len(all_statuses)} statuses so far...")

        # Pagination via Link header
        link_header = resp.headers.get('Link', '')
        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        if next_match:
            url = next_match.group(1)
            params = {}  # URL already has params
        else:
            break

        time.sleep(0.5)  # Be polite

    return all_statuses

def import_mastodon(instance, username):
    """Import all Mastodon posts."""
    print(f"\n{'='*60}")
    print(f"Importing Mastodon: @{username}@{instance}")

    ensure_platform_page('mastodon')

    account_id = get_mastodon_account_id(instance, username)
    print(f"  Account ID: {account_id}")

    statuses = fetch_mastodon_statuses(instance, account_id)
    print(f"  Total statuses fetched: {len(statuses)}")

    imported = 0
    skipped = 0
    errors = 0

    for status in statuses:
        try:
            # Skip boosts (reblogs)
            if status.get('reblog'):
                skipped += 1
                continue

            post_id = status['id']
            date = datetime.fromisoformat(status['created_at'].replace('Z', '+00:00'))
            text = clean_html(status.get('content', ''))
            original_url = status.get('url', f"https://{instance}/@{username}/{post_id}")

            if not text.strip():
                skipped += 1
                continue

            # Extract media URLs
            media_urls = []
            for media in status.get('media_attachments', []):
                if media.get('url'):
                    media_urls.append(media['url'])

            created, filename = write_social_post(
                'mastodon', post_id, date, text, original_url, media_urls
            )

            if created:
                imported += 1
                if imported <= 3 or imported % 100 == 0:
                    print(f"  + {filename}")
            else:
                skipped += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    print(f"  Done: {imported} imported, {skipped} skipped, {errors} errors")
    return imported


# --- Bluesky ---

def fetch_bluesky_feed(handle, max_pages=None):
    """Fetch all posts from a Bluesky account using the public API."""
    all_posts = []
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
    params = {
        'actor': handle,
        'limit': 100,
        'filter': 'posts_no_replies',
    }
    page = 0

    while True:
        page += 1
        if max_pages and page > max_pages:
            break

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        feed = data.get('feed', [])
        if not feed:
            break

        all_posts.extend(feed)

        if page % 5 == 0:
            print(f"  Fetched {len(all_posts)} posts so far...")

        cursor = data.get('cursor')
        if cursor:
            params['cursor'] = cursor
        else:
            break

        time.sleep(0.5)

    return all_posts

def import_bluesky(handle):
    """Import all Bluesky posts."""
    print(f"\n{'='*60}")
    print(f"Importing Bluesky: {handle}")

    ensure_platform_page('bluesky')

    feed = fetch_bluesky_feed(handle)
    print(f"  Total posts fetched: {len(feed)}")

    imported = 0
    skipped = 0
    errors = 0

    for item in feed:
        try:
            post = item.get('post', {})
            record = post.get('record', {})

            # Skip reposts
            if item.get('reason', {}).get('$type') == 'app.bsky.feed.defs#reasonRepost':
                skipped += 1
                continue

            text = record.get('text', '')
            if not text.strip():
                skipped += 1
                continue

            # Extract post ID from URI: at://did:plc:xxx/app.bsky.feed.post/xxx
            uri = post.get('uri', '')
            post_id = uri.split('/')[-1] if '/' in uri else ''
            if not post_id:
                skipped += 1
                continue

            created_at = record.get('createdAt', '')
            date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

            # Construct web URL
            did = post.get('author', {}).get('handle', handle)
            original_url = f"https://bsky.app/profile/{did}/post/{post_id}"

            # Extract image URLs
            media_urls = []
            embed = post.get('embed', {})
            if embed.get('$type') == 'app.bsky.embed.images#view':
                for img in embed.get('images', []):
                    if img.get('fullsize'):
                        media_urls.append(img['fullsize'])
            elif embed.get('$type') == 'app.bsky.embed.recordWithMedia#view':
                media = embed.get('media', {})
                if media.get('$type') == 'app.bsky.embed.images#view':
                    for img in media.get('images', []):
                        if img.get('fullsize'):
                            media_urls.append(img['fullsize'])

            created, filename = write_social_post(
                'bluesky', post_id, date, text, original_url, media_urls
            )

            if created:
                imported += 1
                if imported <= 3 or imported % 100 == 0:
                    print(f"  + {filename}")
            else:
                skipped += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    print(f"  Done: {imported} imported, {skipped} skipped, {errors} errors")
    return imported


# --- Main ---

def main():
    print("Social Media Importer")
    print("=" * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    total = 0

    # Mastodon
    total += import_mastodon('ramblings.social', 'frank')

    # Bluesky
    total += import_bluesky('frankramblings.com')

    print(f"\n{'='*60}")
    print(f"TOTAL: {total} social posts imported")

if __name__ == '__main__':
    main()
