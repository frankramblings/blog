#!/usr/bin/env python3
"""
Import podcast episodes from RSS feeds into Jekyll archive collection.
Reads _data/podcasts.yml for show metadata and feed URLs,
then generates markdown files in all_collections/_archive/.
"""

import feedparser
import yaml
import os
import re
import html
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PODCASTS_YML = BASE_DIR / "_data" / "podcasts.yml"
ARCHIVE_DIR = BASE_DIR / "all_collections" / "_archive"
SHOW_PAGES_DIR = BASE_DIR / "archive" / "podcasts"

def load_podcasts():
    with open(PODCASTS_YML) as f:
        return yaml.safe_load(f)

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def clean_html(text):
    """Decode HTML entities and normalize block element spacing for Kramdown.

    Kramdown only passes block-level HTML through untouched when each element
    starts at the beginning of a line with a blank line before it. Without this,
    tags like <ul> that immediately follow </p> on the same line get escaped as
    raw text instead of being rendered as HTML.
    """
    if not text:
        return ""
    text = html.unescape(text)
    # Ensure each closing block tag is followed by a blank line so the next
    # opening block tag starts on its own line (Kramdown requirement).
    block = r'(?:p|ul|ol|li|div|h[1-6]|blockquote|section|article|header|footer)'
    text = re.sub(rf'(</({block})>)\s*', r'\1\n\n', text, flags=re.IGNORECASE)
    # Also ensure opening block tags start on their own line.
    text = re.sub(rf'\s*(<({block})[\s>])', r'\n\n\1', text, flags=re.IGNORECASE)
    return text.strip()

def detect_season_episode(title):
    """Try to extract season and episode numbers from episode title."""
    # Patterns: "6x18:", "S01E09", "1x09", "s6e18"
    patterns = [
        r'(\d+)x(\d+)',           # 6x18
        r'[Ss](\d+)[Ee](\d+)',    # S01E09
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return season, episode
    return None, None

def detect_sequential_episode(title):
    """Try to extract sequential episode number from title."""
    patterns = [
        r'^(?:Episode\s+)?(\d+)[\s:.-]',    # "123: Title" or "Episode 123 -"
        r'[Ee]pisode\s+(\d+)',                # "Episode 39"
        r'^(\d{3})[\s:.-]',                   # "001: Title"
        r'#(\d+)',                             # "#123"
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return int(match.group(1))
    return None

def parse_date(entry):
    """Extract and parse the publication date from a feed entry."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6])
    return None

def get_audio_url(entry):
    """Extract audio URL from enclosures or links."""
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'audio' in enc.get('type', '') or enc.get('href', '').endswith(('.mp3', '.m4a', '.ogg')):
                return enc.get('href', '')
        # Fall back to first enclosure
        if entry.enclosures:
            return entry.enclosures[0].get('href', '')
    # Check links
    if hasattr(entry, 'links'):
        for link in entry.links:
            if link.get('type', '').startswith('audio/') or link.get('href', '').endswith(('.mp3', '.m4a')):
                return link.get('href', '')
    return ""

def get_episode_description(entry):
    """Get episode description/summary, preserving HTML formatting."""
    # Prefer content:encoded (rich HTML) over summary (often plain text)
    content = getattr(entry, 'content', None)
    if content:
        if isinstance(content, list) and content:
            val = content[0].get('value', '')
            if val:
                return clean_html(val)
    for attr in ('summary', 'description'):
        val = getattr(entry, attr, None)
        if val:
            if isinstance(val, list):
                val = val[0].get('value', '') if val else ''
            return clean_html(val)
    return ""

def make_episode_id(show, title, season, episode, seq_num):
    """Generate the episode_id used in URLs."""
    if show['numbering'] == 'season' and season is not None and episode is not None:
        return f"{season}x{episode:02d}"
    elif show['numbering'] == 'sequential' and seq_num is not None:
        return str(seq_num)
    else:
        # Fallback: use slugified title
        return slugify(title)[:60]

def make_permalink(show_slug, episode_id):
    return f"/archive/podcasts/{show_slug}/{episode_id}/"

def make_filename(date, show_slug, episode_id):
    """Generate the markdown filename."""
    date_str = date.strftime('%Y-%m-%d')
    safe_id = slugify(episode_id) if not episode_id.replace('x', '').replace('X', '').isdigit() else episode_id
    return f"{date_str}-{show_slug}-{safe_id}.md"

def episode_exists(filename, force=False):
    """Check if an episode file already exists."""
    if force:
        return False
    return (ARCHIVE_DIR / filename).exists()

def write_episode(show, entry, date, season, episode, seq_num, episode_id, audio_url, description, force=False):
    """Write a single episode markdown file."""
    filename = make_filename(date, show['slug'], episode_id)

    if episode_exists(filename, force):
        return False, filename

    permalink = make_permalink(show['slug'], episode_id)
    title = entry.title.replace('"', '\\"')
    original_url = entry.get('link', '')

    frontmatter = {
        'title': title,
        'date': date.strftime('%Y-%m-%d'),
        'type': 'podcast',
        'platform': 'podcast',
        'podcast': show['slug'],
        'podcast_title': show['title'],
        'episode_id': str(episode_id),
        'permalink': permalink,
    }

    if season is not None:
        frontmatter['season'] = season
    if episode is not None:
        frontmatter['episode'] = episode
    if seq_num is not None and show['numbering'] == 'sequential':
        frontmatter['episode'] = seq_num
    if original_url:
        frontmatter['original_url'] = original_url
    if audio_url:
        frontmatter['audio_url'] = audio_url

    # Build YAML front matter manually for clean output
    lines = ['---']
    for key in ['title', 'date', 'type', 'platform', 'podcast', 'podcast_title',
                'season', 'episode', 'episode_id', 'permalink', 'original_url', 'audio_url']:
        if key in frontmatter:
            val = frontmatter[key]
            if isinstance(val, str) and ('"' in val or ':' in val or "'" in val or val != val.strip()):
                lines.append(f'{key}: "{val}"')
            elif isinstance(val, str):
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f'{key}: {val}')
    lines.append('---')
    lines.append('')

    # Truncate very long descriptions
    if description and len(description) > 10000:
        description = description[:10000] + '...'

    if description:
        lines.append(description)
        lines.append('')

    filepath = ARCHIVE_DIR / filename
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    return True, filename

def import_show(show, force=False):
    """Import all episodes from a single podcast show."""
    feed_url = show.get('feed_url', '')
    if not feed_url:
        print(f"  Skipping {show['title']} — no feed URL")
        return 0

    print(f"\n{'='*60}")
    print(f"Importing: {show['title']}")
    print(f"Feed: {feed_url}")
    print(f"Numbering: {show['numbering']}")

    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        print(f"  ERROR: Could not parse feed — {feed.bozo_exception}")
        return 0

    print(f"  Found {len(feed.entries)} entries in feed")

    imported = 0
    skipped = 0
    errors = 0
    seen_ids = set()

    for entry in feed.entries:
        try:
            title = entry.get('title', 'Untitled')

            # Skip duplicate AAC/MP3 versions — prefer MP3
            # Many old feeds have both [AAC] and [MP3] versions
            base_title = re.sub(r'\s*\[(AAC|MP3|M4A)\]\s*', '', title).strip()
            title_key = slugify(base_title)

            date = parse_date(entry)
            if not date:
                print(f"  SKIP (no date): {title}")
                errors += 1
                continue

            # Detect episode numbering
            season, episode = detect_season_episode(title)
            seq_num = detect_sequential_episode(title)

            # For season-numbered shows, try to detect from title
            if show['numbering'] == 'season' and season is None:
                # Some season shows have episodes without season markers (bonuses, etc.)
                seq_num = detect_sequential_episode(title)

            episode_id = make_episode_id(show, title, season, episode, seq_num)

            # Deduplicate — skip if we've seen this episode_id already
            dedup_key = f"{show['slug']}-{episode_id}"
            if dedup_key in seen_ids:
                skipped += 1
                continue
            seen_ids.add(dedup_key)

            audio_url = get_audio_url(entry)
            description = get_episode_description(entry)

            created, filename = write_episode(
                show, entry, date, season, episode, seq_num,
                episode_id, audio_url, description, force=force
            )

            if created:
                imported += 1
                if imported <= 3 or imported % 50 == 0:
                    print(f"  + {filename}")
            else:
                skipped += 1

        except Exception as e:
            print(f"  ERROR processing '{entry.get('title', '?')}': {e}")
            errors += 1

    print(f"  Done: {imported} imported, {skipped} skipped, {errors} errors")
    return imported

def ensure_show_page(show):
    """Create the archive/podcasts/<slug>/index.html page if it doesn't exist."""
    show_dir = SHOW_PAGES_DIR / show['slug']
    index_file = show_dir / "index.html"
    if index_file.exists():
        return

    show_dir.mkdir(parents=True, exist_ok=True)

    content = f"""---
layout: archive-list
title: "{show['title']}"
description: "{show.get('description', '')}"
permalink: /archive/podcasts/{show['slug']}/
archive_type: podcast
archive_podcast: {show['slug']}
---
"""
    with open(index_file, 'w') as f:
        f.write(content)
    print(f"  Created show page: archive/podcasts/{show['slug']}/index.html")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Overwrite existing episode files')
    args = parser.parse_args()

    print("Podcast RSS Importer")
    print("=" * 60)
    if args.force:
        print("Force mode: overwriting existing files")

    podcasts = load_podcasts()
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for show in podcasts:
        if show.get('feed_url'):
            ensure_show_page(show)
            count = import_show(show, force=args.force)
            total += count

    print(f"\n{'='*60}")
    print(f"TOTAL: {total} episodes imported")
    print(f"Archive directory: {ARCHIVE_DIR}")

if __name__ == '__main__':
    main()
