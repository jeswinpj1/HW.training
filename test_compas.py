from parsel import Selector
from random import choice
from settings import *
from datahut_tools.pipelines import RequestPipeline
request = RequestPipeline(
    handle_status_code=[200, 404, 412, 456],
    proxy=REQUEST_PROXY,
    check_interval=10,
    failure_limit=0.95,
    slack_id=MAINTAINER_SLACK_ID,
    session=True,
    runid=SITE_RUNID,
    mongo=MONGO_SERVER,
    username=TEAM_USERNAME,
    password=TEAM_PASSWORD,
    module=REQUEST_MODULE,
    retry=20,
   )
browser = choice(BROWSERS)

url = "https://coralgables.ewm.com/agents.php"

headers = {
    "authority": "api.liveby.com",
    "method": "GET",
    "path": "/v1/pages/ldp-template?clientid=ewm",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.ewm.com",
    "priority": "u=1, i",
    "referer": "https://www.ewm.com/",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

response = request.get(url, headers=headers, impersonate=browser)
sel = Selector(text=response.text)
res = sel.xpath('//div[contains(@class,"content-title-inner")]//h1/text()[1]').get(default="").strip() or "Unknown Office"
print(response.status_code)
print(res)
