import csv
import json
import os

INPUT_CSV = "/home/user/HW.training/robertsbrothers-com-2025-12-31-3.csv"
OUTPUT_JSON = os.path.splitext(INPUT_CSV)[0] + "_sample.ndjson"
LIMIT = 50


def clean_text(value):
    if not value:
        return " "
    value = value.strip()
    return value if value else " "


def normalize_row(row):
    name = row.get("name_0", "")
    if name.lower().startswith("about "):
        name = name.replace("About ", "", 1)

    return {
        "title": clean_text(row.get("data_0")),
        "office_name": "Roberts Brothers, Inc.",
        "address": clean_text(row.get("streetAddress_0")),
        "profile_url": clean_text(row.get("data-page-selector")),
        "description": clean_text(row.get("About_Section_Content_0")),
        "name": clean_text(name),
        "website": " ",
        "email": " ",
        "agent_phone_numbers": clean_text(row.get("telephone_0")),
        "office_phone_numbers": " ",
        "country": " ",
    }


def csv_to_json_lines(csv_file, json_file):
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f_in, \
         open(json_file, "w", encoding="utf-8") as f_out:
        
        reader = csv.DictReader(f_in)
        count = 0
        for i, row in enumerate(reader):
            if i >= LIMIT:
                break
            json_line = normalize_row(row)
            f_out.write(json.dumps(json_line, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ Created {count} records in JSON Lines format")
    print(f"📁 Output file: {json_file}")


if __name__ == "__main__":
    csv_to_json_lines(INPUT_CSV, OUTPUT_JSON)
