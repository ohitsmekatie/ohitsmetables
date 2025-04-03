
from google.oauth2.service_account import Credentials
import gspread
import random

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
    spreadsheet_id = "1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4"
    return client.open_by_key(spreadsheet_id)


# Setup Google Sheets access
# def authorize_sheets():
#     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#     creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#     client = gspread.authorize(creds)
#     spreadsheet_id = "1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4"
#     return client.open_by_key(spreadsheet_id)

# === Encounter Generator ===
def get_random_encounter(biome=None, difficulty=None):
    sheet = authorize_sheets().sheet1  # Uses the first sheet (Encounters)
    raw_data = sheet.get_all_values()
    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]
    records = [dict(zip(headers, [cell.strip() for cell in row])) for row in rows]

    def normalize(val):
        return val.strip().lower() if isinstance(val, str) else val

    biome = normalize(biome)
    difficulty = normalize(difficulty)

    filtered = [
        row["Encounter"]
        for row in records
        if (not biome or normalize(row.get("Biome")) == biome)
        and (not difficulty or normalize(row.get("Difficulty")) == difficulty)
    ]

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
