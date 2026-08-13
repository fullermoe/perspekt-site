"""Post today's Perspekt drop card to Instagram via the Meta Graph API.

Runs in GitHub Actions daily. Requires two repo secrets:
  IG_USER_ID        - the Instagram professional account's IG User ID
  META_ACCESS_TOKEN - a long-lived token with instagram_content_publish

The drop is chosen with the app's exact rotation: rotation.json order,
days since 2026-07-01 in America/Chicago, modulo the library size.
"""
import json, os, sys, urllib.parse, urllib.request
from datetime import date, datetime
from zoneinfo import ZoneInfo

GRAPH = "https://graph.facebook.com/v21.0"
REFERENCE = date(2026, 7, 1)

def main():
    ig_user = os.environ["IG_USER_ID"]
    token = os.environ["META_ACCESS_TOKEN"]

    rotation = json.load(open("rotation.json"))
    today = datetime.now(ZoneInfo("America/Chicago")).date()
    drop = rotation[(today - REFERENCE).days % len(rotation)]

    caption = drop["copy"] + "\n\nSource: " + drop["sourceName"] + \
        "\n\nOne real reason a day. perspekt.app"
    image_url = f"https://perspekt.app/cards/{drop['id']}.png"

    def post(path, params):
        body = urllib.parse.urlencode({**params, "access_token": token}).encode()
        with urllib.request.urlopen(urllib.request.Request(f"{GRAPH}/{path}", data=body)) as r:
            return json.load(r)

    container = post(f"{ig_user}/media", {"image_url": image_url, "caption": caption})
    result = post(f"{ig_user}/media_publish", {"creation_id": container["id"]})
    print(f"published {drop['id']} as media {result['id']}")

if __name__ == "__main__":
    sys.exit(main())
