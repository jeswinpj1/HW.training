
# import csv
# import json
# import re
# from html import unescape

# INPUT_FILE = "/home/user/HW.training/mueller_products.json"
# OUTPUT_CSV = "/home/user/HW.training/mueller_2026_01_08_sample.csv"
# limit = 100
# csv_headers = [
#     "product_url",
#     "brand_name",
#     "product_name",
#     "article_number",
#     "price",
#     "price_was",
#     "price_per_unit",
#     "discount_text",
#     "size",
#     "article_information",
#     "articles_details",
#     "hazard_signal",
#     "hazard_text",
#     "safety_notice"
# ]

# class mullerExport:
#     def __init__(self, writer):
#         self.writer = writer
    
#     def start(self):
#         # write header
#         self.writer.writerow(csv_headers)

#         with open(INPUT_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)  # <-- JSON ARRAY
#             def clean_value(val):
#                 if val is None:
#                     return ""
#                 val = str(val)
#                 val = unescape(val)           # remove HTML entities
#                 val = re.sub(r"<.*?>", "", val)  # remove HTML tags
#                 val = re.sub(r"\s+", " ", val)   # replace multiple spaces/newlines with single space
#                 return val.strip()
            
#             for idx, item in enumerate(data):
#                 if idx >= limit:
#                     break
#                 details = item.get("artikel_details", {})
#                 article_details = ", ".join(
#                 f"{k}: {v}" for k, v in details.items()
#                 )
#                 hazard = item.get("gefahrenhinweis", {})
#                 row = {
#                     "product_url": clean_value(item.get("product_url")),
#                     "brand_name": clean_value(item.get("brand_name")),
#                     "product_name": clean_value(item.get("product_name")),
#                     "article_number": clean_value(item.get("article_number")),
#                     "price": clean_value(item.get("price")),
#                     "price_was": clean_value(item.get("strike_price")),
#                     "price_per_unit": clean_value(item.get("base_price")),
#                     "discount_text": clean_value(item.get("discount_text")),
#                     "size": clean_value(item.get("content_ml")),
#                     "article_information": clean_value(item.get("description")),
#                     "articles_details": article_details,
#                     "hazard_signal": clean_value(hazard.get("signal")),
#                     "hazard_text": clean_value(hazard.get("text")),
#                     "safety_notice": clean_value(item.get("sicherheitshinweis")),
#                 }

#                 self.writer.writerow([row.get(h, "") for h in csv_headers])

# if __name__ == "__main__":
#     with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         exporter = mullerExport(writer)
#         exporter.start()



import csv
import re

INPUT_CSV = "/home/user/HW.training/mueller_2026_01_08_sample.csv"
OUTPUT_CSV = "/home/user/HW.training/mueller_2026_01_08_sample_CLEAN.csv"

PRICE_FIELDS = {"price", "price_per_unit"}

def clean_price(value):
    if not value:
        return ""
    value = value.replace("€", "")
    value = value.replace(",", ".")
    value = value.strip()
    return value

def clean_base_price(value):
    if not value:
        return ""

    # remove inkl. MwSt. or inkl. MwSt.,
    value = re.sub(r"inkl\.?\s*MwSt\.?,?", "", value, flags=re.I)

    # remove €
    value = value.replace("€", "")

    # comma to dot
    value = value.replace(",", ".")

    # remove spaces around slash /
    value = re.sub(r"\s*/\s*", "/", value)

    # normalize spaces
    value = re.sub(r"\s+", " ", value).strip()

    return value

with open(INPUT_CSV, newline="", encoding="utf-8") as infile, \
     open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(
        outfile,
        fieldnames=reader.fieldnames,
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()

    for row in reader:
        for field in PRICE_FIELDS:
            if field in row:
                row[field] = clean_price(row[field])

        if "base_price" in row:
            row["base_price"] = clean_base_price(row["base_price"])

        writer.writerow(row)





