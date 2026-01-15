import json

# File paths
input_file = "/home/user/HW.training/zara_categories.json"
output_file = "/home/user/HW.training/zara_category_urls.txt"

# Configuration
base_url = "https://www.zara.com/in/en/s-{section}-{category}-l{seo_id}.html"
region_group = 232
max_pages = 1  # number of pages per category

# Function to clean category key into URL-friendly format
def clean_category(key):
    return key.split('-')[-1].lower().replace('_', '-')

# Recursive function to collect all categories and subcategories
def extract_categories(categories_list, collected=None):
    if collected is None:
        collected = []
    for cat in categories_list:
        collected.append(cat)
        if "subcategories" in cat and cat["subcategories"]:
            extract_categories(cat["subcategories"], collected)
    return collected

# Read JSON data
with open(input_file, "r") as f:
    data = json.load(f)

# Since the JSON is a list at the top level, pass it directly
all_categories = extract_categories(data)

# Generate URLs
all_urls = []

for cat in all_categories:
    if cat.get("hasSubcategories") is False:  # only generate URLs for actual categories
        section = cat.get("sectionName", "unknown").lower()
        category = clean_category(cat.get("key", "category"))
        seo_id = cat.get("categorySeoId", 0)
        v1 = cat.get("id", 0)

        for page in range(1, max_pages + 1):
            url = f"{base_url.format(section=section, category=category, seo_id=seo_id)}?v1={v1}&regionGroupId={region_group}&page={page}"
            all_urls.append(url)

# Save URLs to file
with open(output_file, "w") as f:
    for u in all_urls:
        f.write(u + "\n")

print(f"Generated {len(all_urls)} URLs. Saved to {output_file}")
