#!/usr/bin/env python3
"""
Import Superman & Lois TV Talk and SHoE: Krypton episodes from the
merged House of El Fireside RSS feed into Jekyll archive collection.

Filters the full feed by title prefix to separate the two shows,
then generates markdown files in all_collections/_archive/.
"""

import feedparser
import re
import html
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "all_collections" / "_archive"
SHOW_PAGES_DIR = BASE_DIR / "archive" / "podcasts"

FEED_URL = "https://feeds.fireside.fm/supermantvtalk/rss"

# Show definitions: slug, title, and title-matching patterns
SHOWS = [
    {
        "slug": "superman-and-lois-tv-talk",
        "title": "Superman & Lois TV Talk",
        "numbering": "season",
        "patterns": [
            r"^Superman and Lois\b",
            r"^Superman & Lois\b",
        ],
    },
    {
        "slug": "shoe-krypton",
        "title": "SHoE: Krypton",
        "numbering": "season",
        "patterns": [
            r"^Krypton\b",
            r"\bSHoE[:\s]+Krypton\b",
            r"^Previously on Krypton",
            r"^Return to Krypton",
            r"^Journey to .?Krypton",
            r"^Krypton is Doomed",
        ],
    },
]


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()


def detect_season_episode(title):
    patterns = [
        r'(\d+)x(\d+)',
        r'[Ss](\d+)[Ee](\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None, None


def parse_date(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6])
    return None


def get_audio_url(entry):
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'audio' in enc.get('type', '') or enc.get('href', '').endswith(('.mp3', '.m4a')):
                return enc.get('href', '')
        if entry.enclosures:
            return entry.enclosures[0].get('href', '')
    return ""


def get_description(entry):
    for attr in ('summary', 'description', 'content'):
        val = getattr(entry, attr, None)
        if val:
            if isinstance(val, list):
                val = val[0].get('value', '') if val else ''
            return clean_html(val)
    return ""


def match_show(title):
    """Return the show dict if the episode title matches, else None."""
    for show in SHOWS:
        for pattern in show["patterns"]:
            if re.search(pattern, title, re.IGNORECASE):
                return show
    return None


def make_episode_id(show, title, season, episode):
    if season is not None and episode is not None:
        return f"{season}x{episode:02d}"
    return slugify(title)[:60]


def write_episode(show, title, date, episode_id, original_url, audio_url, description,
                  season=None, episode=None):
    filename = f"{date.strftime('%Y-%m-%d')}-{show['slug']}-{episode_id}.md"
    filepath = ARCHIVE_DIR / filename

    if filepath.exists():
        return False, filename

    permalink = f"/archive/podcasts/{show['slug']}/{episode_id}/"
    yaml_title = title.replace('"', '\\"')

    lines = ['---']
    lines.append(f'title: "{yaml_title}"')
    lines.append(f'date: "{date.strftime("%Y-%m-%d")}"')
    lines.append(f'type: "podcast"')
    lines.append(f'platform: "podcast"')
    lines.append(f'podcast: "{show["slug"]}"')
    lines.append(f'podcast_title: "{show["title"]}"')
    if season is not None:
        lines.append(f'season: {season}')
    if episode is not None:
        lines.append(f'episode: {episode}')
    lines.append(f'episode_id: "{episode_id}"')
    lines.append(f'permalink: "{permalink}"')
    if original_url:
        lines.append(f'original_url: "{original_url}"')
    if audio_url:
        lines.append(f'audio_url: "{audio_url}"')
    lines.append('---')
    lines.append('')

    if description and len(description) > 2000:
        description = description[:2000] + '...'
    if description:
        lines.append(description)
        lines.append('')

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    return True, filename


def ensure_show_page(show):
    show_dir = SHOW_PAGES_DIR / show['slug']
    index_file = show_dir / "index.html"
    if index_file.exists():
        return
    show_dir.mkdir(parents=True, exist_ok=True)
    content = f"""---
layout: archive-list
title: "{show['title']}"
permalink: /archive/podcasts/{show['slug']}/
archive_type: podcast
archive_podcast: {show['slug']}
---
"""
    with open(index_file, 'w') as f:
        f.write(content)
    print(f"  Created show page: archive/podcasts/{show['slug']}/index.html")


def main():
    print("SHoE Import: Superman & Lois TV Talk + Krypton")
    print("=" * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for show in SHOWS:
        ensure_show_page(show)

    print(f"Fetching feed: {FEED_URL}")
    feed = feedparser.parse(FEED_URL)

    if feed.bozo and not feed.entries:
        print(f"  ERROR: Could not parse feed — {feed.bozo_exception}")
        return

    print(f"  Total entries in feed: {len(feed.entries)}")

    counts = {show['slug']: {'imported': 0, 'skipped': 0} for show in SHOWS}
    unmatched = 0
    errors = 0

    for entry in feed.entries:
        try:
            title = entry.get('title', '')
            show = match_show(title)
            if not show:
                unmatched += 1
                continue

            date = parse_date(entry)
            if not date:
                errors += 1
                continue

            season, episode = detect_season_episode(title)
            episode_id = make_episode_id(show, title, season, episode)
            audio_url = get_audio_url(entry)
            description = get_description(entry)
            original_url = entry.get('link', '')

            created, filename = write_episode(
                show, title, date, episode_id, original_url, audio_url, description,
                season=season, episode=episode
            )

            slug = show['slug']
            if created:
                counts[slug]['imported'] += 1
                if counts[slug]['imported'] <= 3:
                    print(f"  + {filename}")
            else:
                counts[slug]['skipped'] += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    print(f"\n{'='*60}")
    print(f"Results:")
    for show in SHOWS:
        slug = show['slug']
        print(f"  {show['title']}:")
        print(f"    Imported: {counts[slug]['imported']}")
        print(f"    Skipped:  {counts[slug]['skipped']}")
    print(f"  Unmatched (other House of El episodes): {unmatched}")
    print(f"  Errors: {errors}")


if __name__ == '__main__':
    main()
