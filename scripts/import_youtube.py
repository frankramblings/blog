#!/usr/bin/env python3
"""
Import This Month In Superman episodes from a YouTube playlist
into Jekyll archive collection.

Uses youtube-dl/yt-dlp to extract video metadata (title, upload date, URL).
Falls back to hardcoded data if yt-dlp is not available.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "all_collections" / "_archive"
SHOW_PAGES_DIR = BASE_DIR / "archive" / "podcasts"

SHOW = {
    "slug": "this-month-in-superman",
    "title": "This Month In Superman",
    "numbering": "sequential",
}

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLUkbAYtVoF2QdY5qf8cCLKda6Rl38Hs8n"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:60]


def ensure_show_page():
    show_dir = SHOW_PAGES_DIR / SHOW['slug']
    index_file = show_dir / "index.html"
    if index_file.exists():
        return
    show_dir.mkdir(parents=True, exist_ok=True)
    content = f"""---
layout: archive-list
title: "{SHOW['title']}"
permalink: /archive/podcasts/{SHOW['slug']}/
archive_type: podcast
archive_podcast: {SHOW['slug']}
---
"""
    with open(index_file, 'w') as f:
        f.write(content)
    print(f"  Created show page: archive/podcasts/{SHOW['slug']}/index.html")


def fetch_playlist_via_ytdlp():
    """Use yt-dlp to get playlist metadata as JSON."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--dump-json",
                "--no-download",
                PLAYLIST_URL,
            ],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"  yt-dlp error: {result.stderr[:200]}")
            return None

        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                videos.append(json.loads(line))
        return videos
    except FileNotFoundError:
        print("  yt-dlp not found, trying youtube-dl...")
        return None
    except Exception as e:
        print(f"  yt-dlp failed: {e}")
        return None


def fetch_video_details(video_id):
    """Fetch full metadata for a single video to get upload_date."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                f"https://www.youtube.com/watch?v={video_id}",
            ],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return None


def write_episode(seq_num, title, date, video_id, description=""):
    episode_id = str(seq_num)
    filename = f"{date.strftime('%Y-%m-%d')}-{SHOW['slug']}-{episode_id}.md"
    filepath = ARCHIVE_DIR / filename

    if filepath.exists():
        return False, filename

    permalink = f"/archive/podcasts/{SHOW['slug']}/{episode_id}/"
    original_url = f"https://www.youtube.com/watch?v={video_id}"
    yaml_title = title.replace('"', '\\"')

    lines = ['---']
    lines.append(f'title: "{yaml_title}"')
    lines.append(f'date: "{date.strftime("%Y-%m-%d")}"')
    lines.append('type: "podcast"')
    lines.append('platform: "youtube"')
    lines.append(f'podcast: "{SHOW["slug"]}"')
    lines.append(f'podcast_title: "{SHOW["title"]}"')
    lines.append(f'episode: {seq_num}')
    lines.append(f'episode_id: "{episode_id}"')
    lines.append(f'permalink: "{permalink}"')
    lines.append(f'original_url: "{original_url}"')
    lines.append(f'video_id: "{video_id}"')
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


def main():
    print("YouTube Playlist Importer: This Month In Superman")
    print("=" * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    ensure_show_page()

    print(f"Fetching playlist: {PLAYLIST_URL}")

    # Try yt-dlp for flat playlist listing
    videos = fetch_playlist_via_ytdlp()

    if not videos:
        print("  ERROR: Could not fetch playlist. Install yt-dlp: pip install yt-dlp")
        return

    print(f"  Found {len(videos)} videos in playlist")

    # Flat playlist doesn't include upload_date, so fetch each video's details
    imported = 0
    skipped = 0
    errors = 0

    # Reverse to process oldest first for sequential numbering
    videos_reversed = list(reversed(videos))

    for i, video in enumerate(videos_reversed):
        try:
            video_id = video.get('id', video.get('url', ''))
            title = video.get('title', 'Untitled')
            upload_date = video.get('upload_date', '')

            # If no upload_date from flat listing, fetch full details
            if not upload_date:
                print(f"  Fetching details for: {title[:50]}...")
                details = fetch_video_details(video_id)
                if details:
                    upload_date = details.get('upload_date', '')
                    if not title or title == 'Untitled':
                        title = details.get('title', title)

            if not upload_date:
                print(f"  SKIP (no date): {title}")
                errors += 1
                continue

            date = datetime.strptime(upload_date, '%Y%m%d')
            seq_num = i + 1

            created, filename = write_episode(seq_num, title, date, video_id)

            if created:
                imported += 1
                print(f"  + {filename}")
            else:
                skipped += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Imported: {imported}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")


if __name__ == '__main__':
    main()
