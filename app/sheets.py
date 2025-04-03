# all the functions to get data from the google sheets 

from google.oauth2.service_account import Credentials
import gspread
import random
import logging
from flask import jsonify, request 

import os

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive"
]

SHOP_SHEET_ID = "1R4chFy9edh8Ao6zs9WX5o03nDmwYN9xJWl0ONVOfqH8"

# scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
client = gspread.authorize(creds)

def get_creds():
    return Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

def authorize_sheets(spreadsheet_id=None):
    scope =  ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = get_creds() 
    client = gspread.authorize(creds)

    if spreadsheet_id:
        return client.open_by_key(spreadsheet_id)
    else:
        # fallback to your default content sheet
        return client.open_by_key("1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4") 


def clean_record_keys(data):
    return [
        {k.strip().title(): v for k, v in row.items()}
        for row in data
    ]

def get_clean_records(worksheet):
    raw = worksheet.get_all_records()
    return clean_record_keys(raw)

# === Encounter Generator ===
def get_random_encounter(biome=None, difficulty=None):
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
    difficulty = normalize(difficulty)

    filtered = [
        row.get("Encounter", "").strip()
        for row in records
        if row.get("Encounter")
        and (not biome or normalize(row.get("Biome")) == biome)
        and (not difficulty or normalize(row.get("Difficulty")) == difficulty)
    ]

    if not filtered:
        return "No encounters match your criteria."
    return random.choice(filtered)

# === Lore ===
def get_random_lore(num_items=5):
    sheet = authorize_sheets().worksheet("Lore")
    entries = sheet.col_values(1)
    entries = [entry.strip() for entry in entries if entry.strip()]
    return random.sample(entries, min(num_items, len(entries)))

def get_flavor_text():
    sheet = authorize_sheets().worksheet("Flavor")
    lines = sheet.col_values(1)
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines) if lines else ""

# === Characters ===
def get_random_character():
    sheet = authorize_sheets().worksheet("Characters")
    raw_data = sheet.get_all_values()

    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]

    records = [dict(zip(headers, [cell.strip() for cell in row])) for row in rows if any(cell.strip() for cell in row)]

    if not records:
        return None

    return random.choice(records)

# === Food ===
def get_random_food(include_weird=False, include_magical=False):
    sheet = authorize_sheets().worksheet("Food")
    data = get_clean_records(sheet)

    if not data:
        return None

    food = random.choice(data)

    result = {
        "Food Item": food.get("Food Item", ""),
        "Description": food.get("Description", "")
    }

    if include_weird:
        result["Weird Side Effect"] = food.get("Weird Side Effect", "")

    if include_magical:
        result["Magical Side Effect"] = food.get("Magical Side Effect", "")

    return result

# === Landmarks ===
def get_random_landmark(biome=None):
    sheet = authorize_sheets().worksheet("Landmarks")
    raw_data = sheet.get_all_values()

    if not raw_data or not biome:
        return "Please select a biome to generate a landmark."

    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]

    if biome not in headers:
        return f"No landmarks found for biome: {biome}"

    col_index = headers.index(biome)
    landmarks = [row[col_index].strip() for row in rows if len(row) > col_index and row[col_index].strip()]

    if not landmarks:
        return f"No landmarks found for {biome}."

    return random.choice(landmarks)

# === Rumors ===
def get_random_rumor():
    sheet = authorize_sheets().worksheet("Rumors")
    lines = sheet.col_values(1)
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines) if lines else None

def get_random_rumors(count=3):
    sheet = authorize_sheets().worksheet("Rumors")
    values = sheet.col_values(1)
    values = [v.strip() for v in values if v.strip()]
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
        "room_vibe": random.choice(room_vibes) if room_vibes else None,
    }

    if include_treasure and treasures:
        result["treasure"] = random.choice(treasures)
    if include_trap and traps:
        result["trap"] = random.choice(traps)
    if include_special and specials:
        result["special"] = random.choice(specials)

    return result

# === Shop System ===
def get_random_shop_items(store_type, count):
    sheet = authorize_sheets(SHOP_SHEET_ID).worksheet(store_type)
    data = get_clean_records(sheet)
    return random.sample(data, min(count, len(data)))

def get_random_shopkeeper():
    sheet = authorize_sheets(SHOP_SHEET_ID).worksheet("Shopkeeper")
    data = get_clean_records(sheet)
    return random.choice(data) if data else None
