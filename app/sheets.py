import gspread
import random
from oauth2client.service_account import ServiceAccountCredentials

# Setup Google Sheets access
def authorize_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    spreadsheet_id = "1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4"
    return client.open_by_key(spreadsheet_id)

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
