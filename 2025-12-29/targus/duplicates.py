import logging
from pymongo import MongoClient
from settings import (
    MONGO_DB,
    MONGO_COLLECTION_DATA,
    MONGO_COLLECTION_DEDUP,
)


class DeduplicateProducts:
    """Deduplicate products using product name"""

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")

        # SOURCE
        self.source_db = self.client[MONGO_DB]
        self.source_col = self.source_db[MONGO_COLLECTION_DATA]

        # TARGET
        self.target_db = self.client[MONGO_DB]
        self.target_col = self.target_db[MONGO_COLLECTION_DEDUP]

        self.seen_names = set()

    # --------------------------------------------------
    # START
    # --------------------------------------------------
    def start(self):
        cursor = self.source_col.find({}, no_cursor_timeout=True)

        count_total = 0
        count_unique = 0

        for doc in cursor:
            count_total += 1

            name = doc.get("name", "").strip().lower()
            if not name:
                continue

            # DUPLICATE CHECK
            if name in self.seen_names:
                continue

            self.seen_names.add(name)

            # REMOVE _id TO AVOID CONFLICT
            doc.pop("_id", None)

            try:
                self.target_col.insert_one(doc)
                count_unique += 1
            except Exception as e:
                logging.error(e)

        cursor.close()

        logging.info(f"Total records read   : {count_total}")
        logging.info(f"Unique records saved : {count_unique}")

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------
    def close(self):
        self.client.close()


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dedupe = DeduplicateProducts()
    dedupe.start()
    dedupe.close()
