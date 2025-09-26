# all the functions to get data from the google sheets

from google.oauth2.service_account import Credentials
import gspread
import random
import logging
from flask import jsonify, request
import os
import json

import os

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive"
]

SHOP_SHEET_ID = "1R4chFy9edh8Ao6zs9WX5o03nDmwYN9xJWl0ONVOfqH8"

# scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)

# gets credentials for reading in and authorizing google sheets
def get_creds():
    raw = os.getenv("GOOGLE_CREDENTIALS_JSON")
    info = json.loads(raw)
    return Credentials.from_service_account_info(info, scopes=SCOPES)

def authorize_sheets(spreadsheet_id=None):
    scope =  ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = get_creds()
    client = gspread.authorize(creds)

    if spreadsheet_id:
        return client.open_by_key(spreadsheet_id)
    else:
        # fallback to default content sheet
        return client.open_by_key("1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4")

# function to clean titles in case i accidentally put a space in them
def clean_record_keys(data):
    return [
        {k.strip().title(): v for k, v in row.items()}
        for row in data
    ]


def get_clean_records(worksheet):
    raw = worksheet.get_all_records()
    return clean_record_keys(raw)


# === Encounter Generator ===

def get_random_encounter(biome=None):
    sheet = authorize_sheets().worksheet("Encounters")
    raw_data = sheet.get_all_values()

    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]

    records = [
        dict(zip(headers, [cell.strip() for cell in row] + [""] * (len(headers) - len(row))))
        for row in rows
    ]

    def normalize(val):
        return val.strip().lower() if isinstance(val, str) else val

    biome = normalize(biome)

    filtered = [
        row
        for row in records
        if row.get("Encounter")
        and (not biome or normalize(row.get("Biome")) == biome)
    ]

    if not filtered:
        return {
            "Encounter": "No encounters match your criteria.",
            "Details": "",
            "Biome": ""
        }

    chosen = random.choice(filtered)
    return {
        "Encounter": chosen.get("Encounter", "").strip(),
        "Details": chosen.get("Encounter Details", "").strip(),
        "Biome": chosen.get("Biome", "").strip()
    }



# === Lore ===

def get_random_lore(num_items=5):
    sheet = authorize_sheets().worksheet("Lore")
    entries = sheet.col_values(1)
    entries = [entry.strip() for entry in entries if entry.strip()]
    return random.sample(entries, min(num_items, len(entries)))

# === Characters ===

def get_random_character():
    sheet = authorize_sheets().worksheet("Characters")
    raw_data = sheet.get_all_values()

    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]

    records = [
        dict(zip(headers, [cell.strip() for cell in row]))
        for row in rows if any(cell.strip() for cell in row)
    ]

    if not records:
        return None

    chosen = random.choice(records)
    chosen["Picture File Name"] = chosen.get("Picture File Name", "").strip()
    return chosen

# === Food ===

def get_random_food(include_weird=False, include_magical=False):
    sheet = authorize_sheets().worksheet("Food")
    data = get_clean_records(sheet)

    if not data:
        return None

    food = random.choice(data)

    result = {
        "food_item": food.get("Food Item", ""),
        "description": food.get("Description", ""),
        "picture_file_name": food.get("Picture File Name", "")
    }

    if include_weird:
        result["weird"] = food.get("Weird Side Effect", "")

    if include_magical:
        result["magical"] = food.get("Magical Side Effect", "")

    return result

# === Landmarks ===

def get_random_landmark(biome=None):
    sheet = authorize_sheets().worksheet("Landmarks")
    raw_data = sheet.get_all_values()

    if not raw_data:
        return {"landmark": "No landmark data found.", "biome": None}

    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]

    biome = biome.strip() if biome else None

    if biome and biome not in headers:
        return {"landmark": f"No landmarks found for biome: {biome}", "biome": None}

    if not biome:
        # Random from all columns
        biome_index = random.randint(0, len(headers) - 1)
        biome = headers[biome_index]
        landmarks = [row[biome_index].strip() for row in rows if len(row) > biome_index and row[biome_index].strip()]
    else:
        col_index = headers.index(biome)
        landmarks = [row[col_index].strip() for row in rows if len(row) > col_index and row[col_index].strip()]

    if not landmarks:
        return {"landmark": f"No landmarks found for {biome}.", "biome": biome}

    return {
        "landmark": random.choice(landmarks),
        "biome": biome
    }

# === Rumors ===

def get_random_rumor():
    """Return one random rumor from the Rumors sheet."""
    sheet = authorize_sheets().worksheet("Rumors")
    lines = sheet.col_values(1)  # first column
    lines = [line.strip() for line in lines if line and line.strip()]
    return random.choice(lines) if lines else None


def get_random_rumors(count=3):
    """Return up to `count` random rumors from the Rumors sheet."""
    sheet = authorize_sheets().worksheet("Rumors")
    values = sheet.col_values(1)  # first column
    values = [v.strip() for v in values if v and v.strip()]
    if not values:
        return []
    count = max(1, int(count))  # ensure positive integer
    return random.sample(values, min(count, len(values)))


# === Room Dressing ===

def get_room_dress():
    include_treasure = request.args.get("treasure") == "true"
    include_trap = request.args.get("trap") == "true"
    include_special = request.args.get("special") == "true"

    sheet = authorize_sheets().worksheet("Room Dressing")
    data = get_clean_records(sheet)

    room_items = [row.get("Room Item") for row in data if row.get("Room Item")]
    room_vibes = [row.get("Room Vibe") for row in data if row.get("Room Vibe")]
    treasures = [row.get("Treasure") for row in data if row.get("Treasure")]
    traps = [row.get("Trap") for row in data if row.get("Trap")]
    specials = [row.get("Special Element") for row in data if row.get("Special Element")]

    result = {
        "room_items": random.sample(room_items, min(3, len(room_items))) if room_items else [],
        "room_vibe": random.sample(room_vibes, min(2, len(room_vibes))) if room_vibes else [],
        "treasure": random.sample(treasures, min(3, len(treasures))) if include_treasure and treasures else [],
        "trap": [random.choice(traps)] if include_trap and traps else [],
        "special": [random.choice(specials)] if include_special and specials else []
    }

    return result

# === Shop system ===

def get_random_shop_items(store_type, count):
    sheet = authorize_sheets(SHOP_SHEET_ID).worksheet(store_type)
    data = get_clean_records(sheet)
    return random.sample(data, min(count, len(data)))

def get_random_shopkeeper():
    sheet = authorize_sheets(SHOP_SHEET_ID).worksheet("Shopkeeper")
    rows = get_clean_records(sheet)  # returns list[dict] keyed by header names
    if not rows:
        return None
    sk = random.choice(rows)

    # Normalize keys coming from the sheet
    first = sk.get("First Name", sk.get("first_name", "")).strip()
    last = sk.get("Last Name", sk.get("last_name", "")).strip()
    desc = sk.get("Personality", sk.get("personality", "")).strip()

    return {
        "first_name": first,
        "last_name": last,
        "personality": desc,
        "full_name": " ".join([p for p in [first, last] if p])
    }
