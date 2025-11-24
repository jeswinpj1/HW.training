https://www.jarir.com/

import requests

# Replace with your desired URL
url = "https://www.homecentre.com/ae"

try:
    response = requests.get(url)
    response.raise_for_status
    print("\nResponse Text:\n")
    print(response.text)
    print("\nStatus Code:", response.status_code)
except requests.exceptions.RequestException as e:
    print("Error occurred:", e)


