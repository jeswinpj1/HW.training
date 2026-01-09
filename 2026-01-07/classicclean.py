# import csv
# import re
# from html import unescape

# INPUT_CSV = "/home/user/HW.training/classiccars_clean.csv"
# OUTPUT_CSV = "/home/user/HW.training/classiccars_2026-01-08.csv"

# csv_headers = [
#     "make",
#     "model",
#     "year",
#     "vin",
#     "price",
#     "mileage",
#     "transmission",
#     "engine",
#     "color",
#     "fuel_type",
#     "body_style",
#     "description",
#     "image_urls",
#     "source_link"
# ]


# class GatewayExport:
#     def __init__(self, writer):
#         self.writer = writer

#     def clean_value(self, val):
#         if val is None:
#             return ""
#         val = str(val)
#         val = unescape(val)
#         val = re.sub(r"<.*?>", "", val)
#         val = re.sub(r"\s+", " ", val)
#         return val.strip()

#     def start(self):
#         # write header
#         self.writer.writerow(csv_headers)

#         with open(INPUT_CSV, encoding="utf-8") as infile:
#             reader = csv.DictReader(infile)

#             for idx, row in enumerate(reader):
#                 if idx >= 50:  # <-- limit set to 50
#                     break

#                 images = row.get("image_0", "")
#                 # remove newlines and join multiple URLs with comma
#                 images = ",".join([i.strip() for i in images.splitlines() if i.strip()])

#                 urls = [
#                     url for url in images.split(" ")
#                     if url.startswith("http")
#                 ]

#                 image_urls = ",".join(urls[:3])
#                 row = {
#                     "make": self.clean_value(row.get("Make_0") or row.get("make") or ""),
#                     "model": self.clean_value(row.get("Model_0") or row.get("model") or ""),
#                     "year": self.clean_value(row.get("Year_0") or row.get("year") or ""),
#                     "VIN": self.clean_value(row.get("text_32") or ""),
#                     "price": self.clean_value(row.get("data_0") or row.get("Price:") or ""),
#                     "mileage": self.clean_value(row.get("Odometer_0") or ""),
#                     "transmission": self.clean_value(row.get("Transmission_0") or ""),
#                     "engine": self.clean_value(row.get("Engine_Size_0") or ""),
#                     "color": self.clean_value(row.get("Exterior_Color_0") or ""),
#                     "fuel type": self.clean_value(""),  # not in source CSV
#                     "body style": self.clean_value(""), # not in source CSV
#                     "description": self.clean_value(row.get("Vehicle_Description_0") or row.get("description") or ""),
#                     "image URLs": image_urls,
#                     "source link": self.clean_value(row.get("data-page-selector") or row.get("Listing_Title_0") or "")
#                 }

#                 self.writer.writerow([row.get(h, "") for h in csv_headers])



# if __name__ == "__main__":
#     with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         exporter = GatewayExport(writer)
#         exporter.start()



# import csv
# import re
# from html import unescape

# INPUT_CSV = "/home/user/HW.training/classiccars-com-2026-01-08-3.csv"
# OUTPUT_CSV = "/home/user/HW.training/classiccars_2026-01-08.csv"

# csv_headers = [
#     "make",
#     "model",
#     "year",
#     "vin",
#     "price",
#     "mileage",
#     "transmission",
#     "engine",
#     "color",
#     "fuel_type",
#     "body_style",
#     "description",
#     "image_urls",
#     "source_link"
# ]


# class GatewayExport:
#     def __init__(self, writer):
#         self.writer = writer

#     def clean_value(self, val):
#         if val is None:
#             return ""
#         val = str(val)
#         val = unescape(val)
#         val = re.sub(r"<.*?>", "", val)
#         val = re.sub(r"\s+", " ", val)
#         return val.strip()

#     def start(self):
#     # write header
#         self.writer.writerow(csv_headers)

#         with open(INPUT_CSV, encoding="utf-8") as infile:
#             reader = csv.DictReader(infile)

#             for idx, row in enumerate(reader):
#                 if idx >= 52:  # <-- limit set to 50
#                     break

#                 # Get the year field
#                 year_str = self.clean_value(row.get("Year_0") or row.get("year") or "")
#                 try:
#                     year = int(year_str)
#                 except:
#                     year = 9999  # if invalid, exclude

#                 # FILTER CONDITIONS
#                 # include if year < 1990, OR year >= 1990 but is retro collectible (optional)
#                 # simple rule: allow years < 1990
#                 if year >= 1990:
#                     # exclude modern vehicles
#                     continue

#                 # Process images
#                 images = row.get("image_0", "")
#                 images = ",".join([i.strip() for i in images.splitlines() if i.strip()])
#                 urls = [url for url in images.split(" ") if url.startswith("http")]
#                 image_urls = ",".join(urls[:3])

#                 # Prepare output row
#                 row_out ={
#                     "make": self.clean_value(row.get("Make_0")),
#                     "model": self.clean_value(row.get("Model_0")),
#                     "year": self.clean_value(row.get("Year_0")),
#                     "vin": self.clean_value(row.get("text_25")),  
#                     "price": self.clean_value(row.get("data_0")),
#                     "mileage": self.clean_value(row.get("Odometer_0")),
#                     "transmission": self.clean_value(row.get("Transmission_0")),
#                     "engine": self.clean_value(row.get("Engine_Size_0")),
#                     "color": self.clean_value(row.get("Exterior_Color_0")),
#                     "fuel_type": "",
#                     "body_style": "",
#                     "description": self.clean_value(row.get("Vehicle_Description_0")),
#                     "image_urls": ",".join(
#                         [u.strip() for u in (row.get("image_26") or "").splitlines() if u.startswith("http")]
#                     ),
#                     "source_link": self.clean_value(row.get("data-page-selector"))
#                 }


#                 self.writer.writerow([row_out.get(h, "") for h in csv_headers])




# if __name__ == "__main__":
#     with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         exporter = GatewayExport(writer)
#         exporter.start()




import csv
import re

INPUT_CSV = "/home/user/HW.training/classiccars_2026_01_08_sample.csv"
OUTPUT_CSV = "/home/user/HW.training/classiccars_2026_01_08_CLEAN.csv"

def clean_price(value):
    if not value:
        return ""
    return re.sub(r"[^\d]", "", value)

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
        if "price" in row:
            row["price"] = clean_price(row["price"])

        writer.writerow(row)

