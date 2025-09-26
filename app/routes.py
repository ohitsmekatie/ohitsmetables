
from flask import Blueprint, render_template, jsonify, request
import subprocess
from datetime import datetime
import logging
from functools import wraps
import random
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from .sheets import get_creds
from zoneinfo import ZoneInfo

from .sheets import (
    authorize_sheets,
    get_random_encounter,
    get_random_lore,
    get_random_character,
    get_random_food,
    get_random_landmark,
    get_random_rumor,
    get_room_dress,
    get_random_shop_items,
    get_random_shopkeeper,
    get_random_rumors
)

# === logging to help me debug ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)

# === Helper to wrap JSON-returning routes ===
def safe_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in route '{f.__name__}': {e}")
            return jsonify({"error": str(e)}), 500
    return wrapper

# === Get Git last update date and google sheet last update ===

def get_last_updated():
    try:
        result = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=iso"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()

        dt = datetime.fromisoformat(result)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception as e:
        logger.warning("Failed to get last updated date: %s", e)
        return "Unknown"


def get_sheet_last_updated():
    try:
        creds = get_creds()
        service = build("drive", "v3", credentials=creds)

        file_id = "1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4"
        file = service.files().get(fileId=file_id, fields="modifiedTime").execute()
        updated = file["modifiedTime"]

        # Convert UTC timestamp to local timezone bc the API returns UTC
        dt_utc = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        dt_local = dt_utc.astimezone(ZoneInfo("America/New_York"))  # ← your timezone here

        return dt_local.strftime("%B %d, %Y at %I:%M %p")
    except Exception as e:
        logger.warning("Could not fetch sheet modified time: %s", e)
        return "Unknown"

# === Routes ===

@main.route("/")
def index():
    last_updated = get_last_updated()
    content_updated = get_sheet_last_updated()
    return render_template("index.html", last_updated=last_updated, content_updated=content_updated)

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/random-encounters")
def random_encounters():
    return render_template("random_encounters.html")

@main.route("/random-encounter")
def random_encounter():
    biome = request.args.get("biome") or None
    return jsonify(get_random_encounter(biome))


@main.route("/lore")
@safe_json
def lore():
    return jsonify(get_random_lore())

@main.route("/characters")
def characters():
    return render_template("characters.html")

@main.route("/character")
@safe_json
def character():
    return jsonify(get_random_character())

@main.route("/food")
def food():
    return render_template("food.html")

@main.route("/food-item")
@safe_json
def food_item():
    include_weird = request.args.get("weird") == "true"
    include_magical = request.args.get("magical") == "true"
    return jsonify(get_random_food(include_weird, include_magical))

@main.route("/landmarks")
def landmarks():
    return render_template("landmarks.html")

@main.route("/landmark")
@safe_json
def landmark():
    biome = request.args.get("biome")

    result = get_random_landmark(biome)
    response = {
        "landmark": result["landmark"],
        "biome": result["biome"]
    }

    return response

@main.route("/room-dressing")
def room_dressing():
    return render_template("room_dressing.html")

@main.route("/room-dress")
@safe_json
def room_dress():
    return jsonify(get_room_dress())

@main.route("/shops")
def shops():
    return render_template("shops.html")

@main.route("/generate-shop")
def generate_shop():
    store_type = request.args.get("type")
    count = int(request.args.get("count", 5))
    include_keeper = request.args.get("keeper") == "true"

    try:
        items = get_random_shop_items(store_type, count)
        keeper = get_random_shopkeeper() if include_keeper else None

        return jsonify({
            "items": items,
            "shopkeeper": keeper
        })
    except Exception as e:
        print("🔥 Error in generate_shop:", e)
        return jsonify({"error": str(e)}), 500

@main.route("/rumors-page")
def rumors_page():
    return render_template("rumors.html")

@main.route("/rumors")
def rumors_api():
    count = request.args.get("count", 3)
    try:
        rumors = get_random_rumors(count)
        if not rumors:
            return jsonify({"error": "No rumors found.", "rumors": []}), 200
        return jsonify({"rumors": rumors})
    except Exception as e:
        return jsonify({"error": str(e), "rumors": []}), 500



@main.route("/test-auth")
def test_auth():
    try:
        sheet = authorize_sheets().sheet1
        title = sheet.title
        return jsonify({"status": "✅ Success", "sheet_title": title})
    except Exception as e:
        return jsonify({"status": "❌ Failed", "error": str(e)}), 500
    
