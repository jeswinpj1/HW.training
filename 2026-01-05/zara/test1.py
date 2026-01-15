# import requests
# from parsel import Selector

# url = "https://www.zara.com/in"

# headers = {
#     "accept": "text/plain",
#     "accept-encoding": "gzip, deflate, br, zstd",
#     "accept-language": "en-US,en;q=0.9",
#     "authorization": "Bearer 3f0f084d-afe7-45d1-b738-0c39136991a0",
#     "cache-control": "no-cache",
#     "content-type": "text/plain",
#     "lib-o11y-name": "COBSERVJS",
#     "lib-o11y-version": "2.4.0",
#     "o11y-tracker": "browser",
#     "origin": "https://www.zara.com",
#     "pragma": "no-cache",
#     "project-key": "ZFRONTST",
#     "referer": "https://www.zara.com/",
#     "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Linux"',
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "cross-site",
#     "tracker-id": "itx-observability-js",
#     "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
# }

# response = requests.get(url, headers=headers, timeout=30)
# print(response.status_code)

# sel = Selector(text=response.text)
# print(sel)
# cat_url = sel.xpath("//a[contains(@class,'layout-categories')]/@href").getall()
# print(cat_url)






import requests
import json
cookies = {
    'MicrosoftApplicationsTelemetryDeviceId': '2ca64f76-3655-41e8-b16a-6651900bfbf5',
    'MicrosoftApplicationsTelemetryFirstLaunchTime': '2026-01-05T05:29:34.355Z',
    'MicrosoftApplicationsTelemetryDeviceId': '2ca64f76-3655-41e8-b16a-6651900bfbf5',
    'MicrosoftApplicationsTelemetryFirstLaunchTime': '2026-01-05T05:29:34.355Z',
    'rid': '47d07f5a-6ee8-49b7-ac05-a646b6343cf9',
    'cart-was-updated-in-standard': 'true',
    'rskxRunCookie': '0',
    'rCookie': 'dxsp57ipdcaefmdj0562tdmk0ptohe',
    '__attentive_id': '9dbc6ef633ee4773a081ccf8bde354e4',
    '_attn_': 'eyJ1Ijoie1wiY29cIjoxNzY3NTkwNjMzNDgyLFwidW9cIjoxNzY3NTkwNjMzNDgyLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjlkYmM2ZWY2MzNlZTQ3NzNhMDgxY2NmOGJkZTM1NGU0XCJ9In0=',
    '__attentive_cco': '1767590633494',
    '__attentive_dv': '1',
    '_gcl_au': '1.1.1721951815.1767590717',
    '_ga': 'GA1.1.2062557525.1767590717',
    'CookiesConsent': 'C0001%3BC0002%3BC0003%3BC0004',
    'FPID': 'FPID2.2.V7K%2FIRIfoz21rFUeLpGheRg3j9jAGCMyaS7TcdsYAAc%3D.1767590717',
    '_fbp': 'fb.1.1767590717795.1117567373',
    '_gtmeec': 'e30%3D',
    'ITXDEVICEID': 'be025c9be8762f7df3b8570c4f969e6f',
    'UAITXID': '44560ca049a024d90fb9527f56835804a8cb3d30b0c9d2cc421ef3d53bf96306',
    'lantern': 'a363a550-8055-4c30-8533-3ff2c5631d35',
    '_tt_enable_cookie': '1',
    '_ttp': '01KE69VTTC131JRB0ZDMH257SM_.tt.1',
    '_clck': 't3340q%5E2%5Eg2g%5E1%5E2196',
    '_pin_unauth': 'dWlkPU1HSmxabVkxWXpjdFlXTmlPQzAwTXpZMExUZzJNRFF0TVRjMk9UVmpaR1UxWWpJeA',
    'FPLC': 'mgG4F42Y0YDZrpzXpJxvBiHo%2FBlISUHjAmiFCETOD%2BoX8lMVeUWKMLQpEgVCW7ALOptuv7EkpHT32wti0cspzpm78A0K18QHzVELjodayAXkDRVMO8LYaEjkzIOzcw%3D%3D',
    '_clsk': 'j6t2at%5E1767590966443%5E9%5E0%5Eb.clarity.ms%2Fcollect',
    'ttcsid': '1767590718288::BLkv9yfX110AcQdl4LnF.1.1767590970836.0',
    'ttcsid_CPC49C3C77UFPV6QTC60': '1767590718287::MuqapAeRpJVgxj8MXeBM.1.1767590970836.1',
    'ITXSESSIONID': '7836593a6cd06ea4f352f0ab77f9fee9',
    'lastRskxRun': '1767601854524',
    '_ga_HCEXQGE0MW': 'GS2.1.s1767601608$o2$g1$t1767601905$j60$l0$h0',
    'bm_mi': 'C547057AE35760E1D7CB44FB4AE0C80D~YAAQRAosF/+lDS2bAQAA56NIjR5rYdtrpTFlkDJQI6f9IotKeZHlGlr/AutxICnZ6JG3wLh1OEuPEOxC4nnXnc0Vr+pv16yjgclJkACGlAaCIon1M5oJBnx6jOq1eLh2MbSvWpTs0QGioBEi0q7IAVYvrTrolP3GDw1roz3IsCp1/Oq7IkEV5aKiQhKeF/OvEPZNQXOxDF4+XGcxsRRE7e/ze2Icg6jY53MNVaAUfwGIvbp1hddyuFvGDYohPes7pnKtUrIJkvpDtvJWYCAHt9A13z1wqM9v3tR+fuWbUD8287gei5x5KtdPwZx/ERTvzmiD4biLbPbEcRVqTE46vMXHNLSEw5vXQ1E=~1',
    'bm_sz': '3A0F30683AE600E9960FCBDC9AB175F2~YAAQRAosFwGmDS2bAQAA56NIjR4mcA3+xN0JWSL262BvuTiaUJZp2eaYqZYOzC7ELbGAXMXlKQTdnuP9UDBmcQLbb9CHD6JbpmpBYkfdUAYTR203/kwTF1U53tHm8Iv0x+307FLganVfuZ+dTcKVgKInPM3sBkWiYiH80Ms2WGkL9WAOW9YNPoZlu/XkmJw6IIO1G+t3hEj1LOvYgh51iQbfdYnlemWljwA6j4Uc/aKg4DZ/IjJ0oAcXUtE45rGF24xgwRk+pFLwa3n55bJmeiD4xWqziBlefGZm7bfcy6y1n64d9SFunINUt2ElsqBs2y9ZU+rQZjGKjxjYSF0G2yA5FRB2janLLHrNHyrzwH7fOTQ7G7Q8/QjXaSxajY0mslp9BoMnCSHPJTJcD0B64CsKQ+ixatT1w65FqusQlI/wq9q22Uc1rrmSm5Zyyqwz5PWTGyHfAtYPlE2rG+rvY+0fL0rvowS3hhpuKSFK+34=~3749942~3683650',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Mon+Jan+05+2026+14%3A01%3A47+GMT%2B0530+(India+Standard+Time)&version=202510.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2a6af79d-5077-46d0-ba39-11a6de9c5abe&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=IN%3BKL&AwaitingReconsent=false',
    'OptanonAlertBoxClosed': '2026-01-05T08:31:47.436Z',
    '_abck': '24D65C179177664E57E3143B0DF095B0~0~YAAQRAosFwimDS2bAQAAoqtIjQ8R9wirObptBYCyQQU/CHyQoJSuyzBJ5fVjGf4WhYlRVaiIYDAktsPXy9E9Et6jLSC+p4YYqwDCrZwT66IValu5wWdxEdxq1YJmq102hNRTrQfJmHNsSDUncOw1KJS6NQ1w7S0hOX5STNS/5r5/3h8r6ffplZSrIHv6gBt9fpVLXsGpGFCA6mj9CUavWj7XN3MzEDlDfpy0X5x6QWeYWJ5AK48beVWEJCtNAJThP8E9gScB3vFasQfa98OGqBDec4BPVXKDtvxWGPg63TgwQzg7PYmdz9R7hE1sRutiMCVLWy1iWmToeIIKlW7wjMx/YrnkKlQUpz99DI+NRsStY4s3PVbrzxem4zvHZH7n42Yfpxe3fPFkL9uUrqqJjlLE8fJ0KPC/Aoj/UqoiJjBi12NiXUBbSxTVkGfLptlJJkvXHVBJ4sxKdLw3wd0lhgWGlxHdtoE/WcRhy5QFYTXUHEN1+B5gKE/c1kwmOx1aW4D+4A17QBTnhHxL/X+JRqYc4sC23RvuF++7d9IH/UoWgeaU02K8tQgrJtfDbfNBy/heQIJD+w2qAywNPGQc5m731oYJHzqHwIpXnKbZt05eEj7bHAHBYaM1wYDdr4iOvHBNoqBlWikJtYJ+XA/WiM6pkWZHPOSD6xkAEcpUFrodHJT8ho2RgwjYsYxKdUMypj4S~-1~-1~1767605031~AAQAAAAE%2f%2f%2f%2f%2fyaEJZsKS0nAJbCYBgeeE84LwvO0CzHJqHYnzOLB+ZC%2fMEW5sa6pYwN60dU1TOwJUPAzZDKKc5y5alR1XzB8%2fjK64DN4IX7ldr6EiIhymt1D+HiKNL3TGMLWoLBJcCpy%2fuU7cKE4fnHgZUsZmMl+18AKCMqrhUEPYLsL3VHUnA%3d%3d~-1',
    '_ga_NOTFORGA4TRACKING': 'GS2.1.s1767601691$o3$g1$t1767601908$j4$l0$h219752909',
    'vwr_global': '1.5.1767601909.65650196-ed64-41be-a1cb-2f75da0b67b2.1767601909..tybLcLKI8FkF5S31muoXqZkUTe7lJggV6y2FdJMDoqA',
    'TS0122c9b6': '01d57b118cb5de501213182ce2fb736981ba1afda61219aa4cf246bc09f836dd5b619c1a1af3652884f4737c1ff3da46854e191df7',
    'ak_bmsc': 'DAB05B1A1873E06EE5FD0D8CCEA34C36~000000000000000000000000000000~YAAQRAosFwumDS2bAQAAQq5IjR4QMDt3RvwSnWwvIa9U8xjILFtqWz4+GOo7fJhW48ryTgOq/EzWRfLbVnbYk1rGQRNsFamYFIDt4Ho3SUtr3XD3MHYRD216AR5EsxYjh/iukDbMJSMCjo+DY42ZqG+S2xjK9HXN6r6FrtHrECiuFyHWKaCeHUWvaw7p9dELftiTP1+vdSjm1LLdIbTWPbUOYVXgkgBlbNHjS7hQk1+wIE/CE6XaEMgSxQCxvp13nqhfUOkT/XtKMbWGmAcyKbuivUJWbDtDpksxLnSKgBqmKr2XyIQyC3/K5EljgHRXN+xtWFNtm5nBktkymlAje5eHYAoyPsbXc0cfmCdxfCSWyUZ3lBCY2CpXz2cCX3ESfb5fe3a6j/WBs+XVg1mURMS596eu0aqpi+VLAxEtaXHgx30e8ZoQ8E5uru33X7g2lnVgTvyEmqvAvdXWHW3SlnU8TfvI76LlumXQNiALifYPagBPfLjSjPvj/7pWDs38OVzgmwEWxwrnj7Ex6keodzsFJtXpuCFWD0cD9Tj4M1r6QpD7UXMsD1I44Jk7jX8in0TK17Kw/zuftRGu6BVg3wuphQ8zKq1TahOHr0yzgu1UFrrfBMJCmrFUzsg7/aU=',
    'bm_sv': '155DF57A7AFDDAE0C930AE77F3B2BCCD~YAAQRAosFwymDS2bAQAAQq5IjR4PiWE9KxO37uO4z/8tXvBxz9bqGY9SlD3o5BKkFmMGZFopFSnsTKQrJMPPXOJY5QcXeLmjrouTUuKVaaOSKjRH7zPyZtbeDibfk0s6Ccvv3BLoC5f9taNiaU0ndEqyxUBCYSR4Y9oS/e+HwEjsUWqoZevKdn+w4kRR7Q4cXcog5C7VlhV3I3IdrGZ1s8vATPTn1tNsUsN50dYht7RpOW/qDR8Ck1U88PTImw==~1',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.zara.com/in/en/s-man-shirts-l11058.html?v1=2636268&regionGroupId=232&page=12',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    # 'cookie': 'MicrosoftApplicationsTelemetryDeviceId=2ca64f76-3655-41e8-b16a-6651900bfbf5; MicrosoftApplicationsTelemetryFirstLaunchTime=2026-01-05T05:29:34.355Z; MicrosoftApplicationsTelemetryDeviceId=2ca64f76-3655-41e8-b16a-6651900bfbf5; MicrosoftApplicationsTelemetryFirstLaunchTime=2026-01-05T05:29:34.355Z; rid=47d07f5a-6ee8-49b7-ac05-a646b6343cf9; cart-was-updated-in-standard=true; rskxRunCookie=0; rCookie=dxsp57ipdcaefmdj0562tdmk0ptohe; __attentive_id=9dbc6ef633ee4773a081ccf8bde354e4; _attn_=eyJ1Ijoie1wiY29cIjoxNzY3NTkwNjMzNDgyLFwidW9cIjoxNzY3NTkwNjMzNDgyLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjlkYmM2ZWY2MzNlZTQ3NzNhMDgxY2NmOGJkZTM1NGU0XCJ9In0=; __attentive_cco=1767590633494; __attentive_dv=1; _gcl_au=1.1.1721951815.1767590717; _ga=GA1.1.2062557525.1767590717; CookiesConsent=C0001%3BC0002%3BC0003%3BC0004; FPID=FPID2.2.V7K%2FIRIfoz21rFUeLpGheRg3j9jAGCMyaS7TcdsYAAc%3D.1767590717; _fbp=fb.1.1767590717795.1117567373; _gtmeec=e30%3D; ITXDEVICEID=be025c9be8762f7df3b8570c4f969e6f; UAITXID=44560ca049a024d90fb9527f56835804a8cb3d30b0c9d2cc421ef3d53bf96306; lantern=a363a550-8055-4c30-8533-3ff2c5631d35; _tt_enable_cookie=1; _ttp=01KE69VTTC131JRB0ZDMH257SM_.tt.1; _clck=t3340q%5E2%5Eg2g%5E1%5E2196; _pin_unauth=dWlkPU1HSmxabVkxWXpjdFlXTmlPQzAwTXpZMExUZzJNRFF0TVRjMk9UVmpaR1UxWWpJeA; FPLC=mgG4F42Y0YDZrpzXpJxvBiHo%2FBlISUHjAmiFCETOD%2BoX8lMVeUWKMLQpEgVCW7ALOptuv7EkpHT32wti0cspzpm78A0K18QHzVELjodayAXkDRVMO8LYaEjkzIOzcw%3D%3D; _clsk=j6t2at%5E1767590966443%5E9%5E0%5Eb.clarity.ms%2Fcollect; ttcsid=1767590718288::BLkv9yfX110AcQdl4LnF.1.1767590970836.0; ttcsid_CPC49C3C77UFPV6QTC60=1767590718287::MuqapAeRpJVgxj8MXeBM.1.1767590970836.1; ITXSESSIONID=7836593a6cd06ea4f352f0ab77f9fee9; lastRskxRun=1767601854524; _ga_HCEXQGE0MW=GS2.1.s1767601608$o2$g1$t1767601905$j60$l0$h0; bm_mi=C547057AE35760E1D7CB44FB4AE0C80D~YAAQRAosF/+lDS2bAQAA56NIjR5rYdtrpTFlkDJQI6f9IotKeZHlGlr/AutxICnZ6JG3wLh1OEuPEOxC4nnXnc0Vr+pv16yjgclJkACGlAaCIon1M5oJBnx6jOq1eLh2MbSvWpTs0QGioBEi0q7IAVYvrTrolP3GDw1roz3IsCp1/Oq7IkEV5aKiQhKeF/OvEPZNQXOxDF4+XGcxsRRE7e/ze2Icg6jY53MNVaAUfwGIvbp1hddyuFvGDYohPes7pnKtUrIJkvpDtvJWYCAHt9A13z1wqM9v3tR+fuWbUD8287gei5x5KtdPwZx/ERTvzmiD4biLbPbEcRVqTE46vMXHNLSEw5vXQ1E=~1; bm_sz=3A0F30683AE600E9960FCBDC9AB175F2~YAAQRAosFwGmDS2bAQAA56NIjR4mcA3+xN0JWSL262BvuTiaUJZp2eaYqZYOzC7ELbGAXMXlKQTdnuP9UDBmcQLbb9CHD6JbpmpBYkfdUAYTR203/kwTF1U53tHm8Iv0x+307FLganVfuZ+dTcKVgKInPM3sBkWiYiH80Ms2WGkL9WAOW9YNPoZlu/XkmJw6IIO1G+t3hEj1LOvYgh51iQbfdYnlemWljwA6j4Uc/aKg4DZ/IjJ0oAcXUtE45rGF24xgwRk+pFLwa3n55bJmeiD4xWqziBlefGZm7bfcy6y1n64d9SFunINUt2ElsqBs2y9ZU+rQZjGKjxjYSF0G2yA5FRB2janLLHrNHyrzwH7fOTQ7G7Q8/QjXaSxajY0mslp9BoMnCSHPJTJcD0B64CsKQ+ixatT1w65FqusQlI/wq9q22Uc1rrmSm5Zyyqwz5PWTGyHfAtYPlE2rG+rvY+0fL0rvowS3hhpuKSFK+34=~3749942~3683650; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Jan+05+2026+14%3A01%3A47+GMT%2B0530+(India+Standard+Time)&version=202510.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2a6af79d-5077-46d0-ba39-11a6de9c5abe&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=IN%3BKL&AwaitingReconsent=false; OptanonAlertBoxClosed=2026-01-05T08:31:47.436Z; _abck=24D65C179177664E57E3143B0DF095B0~0~YAAQRAosFwimDS2bAQAAoqtIjQ8R9wirObptBYCyQQU/CHyQoJSuyzBJ5fVjGf4WhYlRVaiIYDAktsPXy9E9Et6jLSC+p4YYqwDCrZwT66IValu5wWdxEdxq1YJmq102hNRTrQfJmHNsSDUncOw1KJS6NQ1w7S0hOX5STNS/5r5/3h8r6ffplZSrIHv6gBt9fpVLXsGpGFCA6mj9CUavWj7XN3MzEDlDfpy0X5x6QWeYWJ5AK48beVWEJCtNAJThP8E9gScB3vFasQfa98OGqBDec4BPVXKDtvxWGPg63TgwQzg7PYmdz9R7hE1sRutiMCVLWy1iWmToeIIKlW7wjMx/YrnkKlQUpz99DI+NRsStY4s3PVbrzxem4zvHZH7n42Yfpxe3fPFkL9uUrqqJjlLE8fJ0KPC/Aoj/UqoiJjBi12NiXUBbSxTVkGfLptlJJkvXHVBJ4sxKdLw3wd0lhgWGlxHdtoE/WcRhy5QFYTXUHEN1+B5gKE/c1kwmOx1aW4D+4A17QBTnhHxL/X+JRqYc4sC23RvuF++7d9IH/UoWgeaU02K8tQgrJtfDbfNBy/heQIJD+w2qAywNPGQc5m731oYJHzqHwIpXnKbZt05eEj7bHAHBYaM1wYDdr4iOvHBNoqBlWikJtYJ+XA/WiM6pkWZHPOSD6xkAEcpUFrodHJT8ho2RgwjYsYxKdUMypj4S~-1~-1~1767605031~AAQAAAAE%2f%2f%2f%2f%2fyaEJZsKS0nAJbCYBgeeE84LwvO0CzHJqHYnzOLB+ZC%2fMEW5sa6pYwN60dU1TOwJUPAzZDKKc5y5alR1XzB8%2fjK64DN4IX7ldr6EiIhymt1D+HiKNL3TGMLWoLBJcCpy%2fuU7cKE4fnHgZUsZmMl+18AKCMqrhUEPYLsL3VHUnA%3d%3d~-1; _ga_NOTFORGA4TRACKING=GS2.1.s1767601691$o3$g1$t1767601908$j4$l0$h219752909; vwr_global=1.5.1767601909.65650196-ed64-41be-a1cb-2f75da0b67b2.1767601909..tybLcLKI8FkF5S31muoXqZkUTe7lJggV6y2FdJMDoqA; TS0122c9b6=01d57b118cb5de501213182ce2fb736981ba1afda61219aa4cf246bc09f836dd5b619c1a1af3652884f4737c1ff3da46854e191df7; ak_bmsc=DAB05B1A1873E06EE5FD0D8CCEA34C36~000000000000000000000000000000~YAAQRAosFwumDS2bAQAAQq5IjR4QMDt3RvwSnWwvIa9U8xjILFtqWz4+GOo7fJhW48ryTgOq/EzWRfLbVnbYk1rGQRNsFamYFIDt4Ho3SUtr3XD3MHYRD216AR5EsxYjh/iukDbMJSMCjo+DY42ZqG+S2xjK9HXN6r6FrtHrECiuFyHWKaCeHUWvaw7p9dELftiTP1+vdSjm1LLdIbTWPbUOYVXgkgBlbNHjS7hQk1+wIE/CE6XaEMgSxQCxvp13nqhfUOkT/XtKMbWGmAcyKbuivUJWbDtDpksxLnSKgBqmKr2XyIQyC3/K5EljgHRXN+xtWFNtm5nBktkymlAje5eHYAoyPsbXc0cfmCdxfCSWyUZ3lBCY2CpXz2cCX3ESfb5fe3a6j/WBs+XVg1mURMS596eu0aqpi+VLAxEtaXHgx30e8ZoQ8E5uru33X7g2lnVgTvyEmqvAvdXWHW3SlnU8TfvI76LlumXQNiALifYPagBPfLjSjPvj/7pWDs38OVzgmwEWxwrnj7Ex6keodzsFJtXpuCFWD0cD9Tj4M1r6QpD7UXMsD1I44Jk7jX8in0TK17Kw/zuftRGu6BVg3wuphQ8zKq1TahOHr0yzgu1UFrrfBMJCmrFUzsg7/aU=; bm_sv=155DF57A7AFDDAE0C930AE77F3B2BCCD~YAAQRAosFwymDS2bAQAAQq5IjR4PiWE9KxO37uO4z/8tXvBxz9bqGY9SlD3o5BKkFmMGZFopFSnsTKQrJMPPXOJY5QcXeLmjrouTUuKVaaOSKjRH7zPyZtbeDibfk0s6Ccvv3BLoC5f9taNiaU0ndEqyxUBCYSR4Y9oS/e+HwEjsUWqoZevKdn+w4kRR7Q4cXcog5C7VlhV3I3IdrGZ1s8vATPTn1tNsUsN50dYht7RpOW/qDR8Ck1U88PTImw==~1',
}

params = {
    'categoryId': '2636268',
    'categorySeoId': '11058',
    'ajax': 'true',
}

response = requests.get('https://www.zara.com/in/en/categories', params=params, cookies=cookies, headers=headers)

print(response.status_code)

data = response.json()

all_categories = []

def extract_categories(categories_list, parent_id=None, level=1):
    for cat in categories_list:
        category_info = {
            'id': cat.get('id'),
            'key': cat.get('key'),
            'name': cat.get('name'),
            'sectionName': cat.get('sectionName'),
            'menuLevel': cat.get('menuLevel', level),
            'parent_id': parent_id,
            'hasSubcategories': cat.get('hasSubcategories', False),
            'image_url': None
        }

        # Try to get the first image if available
        try:
            data_sources = cat.get('sdui', {}).get('dataSources', {})
            carousel_data = data_sources.get('carousel', {}).get('data', [])
            if carousel_data:
                category_info['image_url'] = carousel_data[0].get('storeFrontMedia', {}).get('asset', {}).get('url')
        except:
            pass

        all_categories.append(category_info)

        # Recursively extract subcategories
        if cat.get('subcategories'):
            extract_categories(cat['subcategories'], parent_id=cat.get('id'), level=level+1)

# Start extraction
extract_categories(data.get('categories', []))

# Save to JSON
with open('zara_categories.json', 'w', encoding='utf-8') as f:
    json.dump(all_categories, f, ensure_ascii=False, indent=4)

print(f"Total categories extracted: {len(all_categories)}")
