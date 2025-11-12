import requests

# URL to check
url = "https://www.classiccars.com/"

# Example headers (simulate a real browser)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.classiccars.com/",
    "Connection": "keep-alive"
}

# Example cookies (use the cookies from your browser if needed)
cookies = {
    "IDE": "AHWqTUkOeRTNh07YhdhUD176dl3is_181CUVbLfHUzDhrBJt7Oj6pRD_hha5KKGkPu4",
    "DSID": "AEhM4MfwkxlssRFoHWRFN-HIBBA0Wkv21MqEMJpvO5mjya5kQgqh-mwVXswfNp_mDP-PPAxaeXf2Cz6VCB9lYuu63G8n82egqk3KiKNHSUF3P50Ru_PyoJfjlqKvOrKy8MHrxOHxkDrxnMRMtGTTdgc0NwGGigl0mceTqcbl47u8FfIsyI1zCjQ9Tt_sB6JVilPfJ1xyXgJygkl7eNamD8IaJthw2YZj4l_T-0NMLJdWedMDsqcCkvrXzJY4K7rQn9Y5N1MKRjjJJkeRDCoh6m7uKLGAa4FyzzTANStQDnJ7i_1y8TbR4TY"
}

# Make the request
response = requests.get(url, headers=headers, cookies=cookies)

# Check results
print("Status Code:", response.status_code)
print("Headers:", response.headers)
print("Content Preview:", response.text[:500])
