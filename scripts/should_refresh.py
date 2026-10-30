#!/usr/bin/env python3
"""Skip expensive scheduled news builds when this local-time edition is already published.

Workflow pushes and manual dispatches always rebuild. Scheduled runs use the
hosted news.json timestamp so subsequent retry opportunities are inexpensive.
"""
import json
import os
import urllib.request
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

ZONE = ZoneInfo("America/Halifax")
URL = "https://jkav23.github.io/kavanaugh-daily/news.json"

def needs_refresh():
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    if event != "schedule":
        print("Push or manual run: always publish.")
        return True

    now = datetime.now(timezone.utc).astimezone(ZONE)
    if now.hour < 3 or now.hour >= 21:
        print("Outside the morning and afternoon publishing windows.")
        return False

    window_hour = 3 if now.hour < 12 else 12
    window_start = datetime.combine(now.date(), time(window_hour, 0), tzinfo=ZONE)
    try:
        req = urllib.request.Request(
            URL + "?check=" + str(int(datetime.now(timezone.utc).timestamp())),
            headers={"User-Agent": "The-Kavanaugh-Daily-GitHub-Actions/1.0", "Cache-Control": "no-cache"}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            edition = json.load(response)
        published = datetime.fromisoformat(edition["updated_at"].replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise ValueError("Missing timezone on feed timestamp")
        published_local = published.astimezone(ZONE)
        if published_local >= window_start and published_local <= now:
            print("Edition already published for this window:", published_local.isoformat())
            return False
        print("Published edition is older than this window:", published_local.isoformat())
    except Exception as exc:
        print("Could not verify published edition; refresh as a precaution:", exc)
    return True

def main():
    refresh = needs_refresh()
    print("Should refresh:", refresh)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("refresh=" + ("true" if refresh else "false") + "\n")

if __name__ == "__main__":
    main()
