import json
import os
import subprocess
import logging
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("plex-webhook")

SCRIPT_PATH = "/app/plex-hide-spoilers.py"
EVENTS = {"media.scrobble", "library.new"}


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.form.get("payload")
    if not payload:
        return "no payload", 400

    data = json.loads(payload)
    event = data.get("event", "")
    title = data.get("Metadata", {}).get("title", "unknown")
    log.info(f"Received event: {event} — {title}")

    if event not in EVENTS:
        log.info(f"Ignoring event: {event}")
        return "ignored", 200

    cmd = ["python3", SCRIPT_PATH, "--quiet"]

    if event == "media.scrobble":
        metadata = data.get("Metadata", {})
        rating_key = metadata.get("ratingKey")
        media_type = metadata.get("type", "")
        if rating_key and media_type in ("episode", "movie"):
            plex_uri = f"plex://{media_type}/{rating_key}"
            cmd.extend(["--also-unhide", plex_uri])

    log.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.error(f"Script failed: {result.stderr}")
        return "error", 500

    log.info(f"Script finished successfully")
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9000))
    app.run(host="0.0.0.0", port=port)
