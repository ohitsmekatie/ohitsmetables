import gspread
import random
from oauth2client.service_account import ServiceAccountCredentials

# def get_random_encounter(biome=None, difficulty=None):
#     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#     creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#     client = gspread.authorize(creds)

#     spreadsheet_id = "1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4"
#     sheet = client.open_by_key(spreadsheet_id).sheet1
#     records = sheet.get_all_records()

#     filtered = [
#         row["Encounter"]
#         for row in records
#         if (not biome or row.get("Biome") == biome)
#         and (not difficulty or row.get("Difficulty") == difficulty)
#     ]

#     if not filtered:
#         return "No encounters match your criteria."
#     return random.choice(filtered)

import gspread
import random
from oauth2client.service_account import ServiceAccountCredentials

def get_random_encounter(biome=None, difficulty=None):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    spreadsheet_id = "1rYVBYbfByR-M4G-WQiDmIkHyGsgRVGUnmwFaQsaNRO4"
    sheet = client.open_by_key(spreadsheet_id).sheet1

    # Normalize headers and data
    raw_data = sheet.get_all_values()
    headers = [h.strip() for h in raw_data[0]]
    rows = raw_data[1:]

    records = [dict(zip(headers, [cell.strip() for cell in row])) for row in rows]

    def normalize(value):
        return value.strip().lower() if isinstance(value, str) else value

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


