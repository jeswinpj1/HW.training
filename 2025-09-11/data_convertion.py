# import pandas as pd
# from pymongo import MongoClient
# import json

# client = MongoClient("mongodb://localhost:27017/")
# db = client["johnlewis"]
# collection = db["product_details"]

# # Load data
# docs = list(collection.find({}, {"_id": 0}))

# # --- JSON EXPORTS ---
# # JSON Array
# with open("products_array.json", "w") as f:
#     json.dump(docs, f, indent=2)

# # JSON Lines
# with open("products_lines.jsonl", "w") as f:
#     for d in docs:
#         f.write(json.dumps(d) + "\n")

# # --- CSV EXPORTS ---
# df = pd.DataFrame(docs)

# # Normal CSV
# df.to_csv("products.csv", index=False)

# # Pipe-separated CSV
# df.to_csv("products_pipe.csv", index=False, sep="|")

# df.to_json("products_lines.jsonl", orient="records", lines=True)




import pandas as pd
from pymongo import MongoClient
import json
from datetime import datetime

def json_serializer(obj):
    """Custom serializer for non-serializable objects like datetime"""
    if isinstance(obj, datetime):
        return obj.isoformat()   # or str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

client = MongoClient("mongodb://localhost:27017/")
db = client["johnlewis"]
collection = db["product_details"]

# Load data from MongoDB
docs = list(collection.find({}, {"_id": 0}))

# --- JSON EXPORTS ---
# JSON Array
with open("products_array.json", "w") as f:
    json.dump(docs, f, indent=2, default=json_serializer)

# JSON Lines
with open("products_lines.jsonl", "w") as f:
    for d in docs:
        f.write(json.dumps(d, default=json_serializer) + "\n")

# --- CSV EXPORTS ---
df = pd.DataFrame(docs)

df.to_json("products_lines.jsonl", orient="records", lines=True)

# Normal CSV
df.to_csv("products.csv", index=False)

# Pipe-separated CSV
df.to_csv("products_pipe.csv", index=False, sep="|")

print("Exported to JSON (array, lines) and CSV (comma, pipe)")
