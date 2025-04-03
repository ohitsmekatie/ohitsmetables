
from google.oauth2.service_account import Credentials
import gspread
import random
import logging
from flask import jsonify, request 


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive"
]

# scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

def get_creds():
    return Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

def authorize_sheets():
    creds = get_creds()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key("1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4")
    return spreadsheet

# === Encounter Generator ===
def get_random_encounter(biome=None, difficulty=None):
    sheet = authorize_sheets().worksheet("Encounters")
    raw_data = sheet.get_all_values()

    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]
    print("Headers:", headers)

    records = [
        dict(zip(headers, [cell.strip() for cell in row] + [""] * (len(headers) - len(row))))
        for row in rows
    ]

    def normalize(val):
        return val.strip().lower() if isinstance(val, str) else val

    biome = normalize(biome)
    difficulty = normalize(difficulty)

    # print("Biome filter:", biome)
    # print("Difficulty filter:", difficulty)

    filtered = [
        row.get("Encounter", "").strip()
        for row in records
        if row.get("Encounter")
        and (not biome or normalize(row.get("Biome")) == biome)
        and (not difficulty or normalize(row.get("Difficulty")) == difficulty)
    ]

    # print("Filtered encounters:", filtered)

    if not filtered:
        return "No encounters match your criteria."
    return random.choice(filtered)


# === Lore Fetcher ===
def get_random_lore(num_items=4):
    lore_sheet = authorize_sheets().worksheet("Lore")
    entries = lore_sheet.col_values(1)  # Assumes single-column
    entries = [entry.strip() for entry in entries if entry.strip()]
    return random.sample(entries, min(num_items, len(entries)))
    
def get_flavor_text():
    sheet = authorize_sheets().worksheet("Flavor")
    lines = sheet.col_values(1)  # Read column A
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines) if lines else ""

def get_random_character():
    sheet = authorize_sheets().worksheet("Characters")
    raw_data = sheet.get_all_values()

    headers = [h.strip() for h in raw_data[0]]  # Strip column names
    rows = raw_data[1:]

    # strips white lines or spaces
    records = [dict(zip(headers, [cell.strip() for cell in row])) for row in rows if any(cell.strip() for cell in row)]

    if not records:
        return None

    return random.choice(records)

def get_random_food(include_weird=False, include_magical=False):
    sheet = authorize_sheets().worksheet("Food")
    data = sheet.get_all_records()

    if not data:
        return None

    food = random.choice(data)
    print("Random food row:", food)  # ✅ Add this

    result = {
        "Food Item": food.get("Food Item", ""),
        "Description": food.get("Description", "")
    }

    if include_weird:
        result["Weird Side Effect"] = food.get("Weird Side Effect", "")

    if include_magical:
        result["Magical Side Effect"] = food.get("Magical Side Effect", "")

    return result

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

def get_random_rumor():
    sheet = authorize_sheets().worksheet("Rumors")
    lines = sheet.col_values(1)
    lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines) if lines else None


def get_room_dress():
    include_treasure = request.args.get("treasure") == "true"
    include_trap = request.args.get("trap") == "true"
    include_special = request.args.get("special") == "true"

    sheet = authorize_sheets().worksheet("Room Dressing")
    data = sheet.get_all_records()

    # if not data:
    #     logger.warning("No data found in Room Dressing sheet.")
    #     return jsonify({"error": "No data in sheet"}), 500

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

    # logger.info("Room dressing result: %s", result)
    return result
