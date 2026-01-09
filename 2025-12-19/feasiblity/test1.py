import requests
import time
import random
import logging
import json
from datetime import datetime

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------------------------------------
# BASE URL
# -------------------------------------------------
BASE_URL = (
    "https://www.autozone.com/external/product-discovery/"
    "browse-search/v1/product-shelves"
)

# -------------------------------------------------
# OUTPUT FILE
# -------------------------------------------------
OUTPUT_FILE = f"autozone_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# -------------------------------------------------
# GLOBAL STORAGE
# -------------------------------------------------
ALL_PRODUCTS = []

cookies = {
    'REQUEST_ID': 'Ir_trn2uCdivKWUCaDv0S',
    'mt.v': '5.2113638288.1766136073163',
    'preferedstore': '6997',
    'eCookieId': 'af497e4d-4e96-4c0f-80c6-f0026f79ec9a',
    'akacd_default': '2147483647~rv=53~id=e4aadede6bde93169b6f7a8f0bd850fd',
    '_pxhd': '1c375643dd0e2ce960ab6a095ac7bd8d94d14076be84d22f5d56cb62a4d40a53:0ff531a6-dcbc-11f0-bbce-393e09930bbe',
    'eCookieId': 'af497e4d-4e96-4c0f-80c6-f0026f79ec9a',
    'RES_TRACKINGID': '648008875727071',
    '_pxvid': '0ff531a6-dcbc-11f0-bbce-393e09930bbe',
    's_ecid': 'MCMID%7C69847302916069607832568946155882566522',
    '_scid': 'pmCI_61vc4w3OUkE7F3H7oR1RHLvhqpa',
    '_gcl_au': '1.1.674812607.1766136080',
    '_ga': 'GA1.1.2107962357.1766136080',
    'QuantumMetricUserID': '06d8831bdc3e9e9d361800599997d7aa',
    'seerid': 'af352cf9-deda-42af-af2c-a880787a44e3',
    '_fbp': 'fb.1.1766136080096.626553772490140020',
    '_ScCbts': '%5B%22272%3Bchrome.2%3A2%3A5%22%2C%22289%3Bchrome.2%3A2%3A5%22%5D',
    'thrive_fp_uuid': 'AAAAAZs16ehU2Bk4plVJjjEtLMp33PmYCV6FTUXsxW_ELEnyttOq4L0u',
    '_sctr': '1%7C1766082600000',
    'cs-personalize-user-uid': '1c9aa302-5989-5725-9fbf-91b08c8ce3eb',
    'cs-lytics-audiences': '|all|anonymous_profiles|smt_new|',
    'cs-lytics-flows': '||',
    'level1Category': 'Auto Parts',
    'QSI_SI_9ud5OjHx5m8Lxki_intercept': 'true',
    'BVBRANDID': 'f1325390-13ec-486e-bedf-d6e54f53c38b',
    'QSI_SI_enaOc3sA6n8rkVg_intercept': 'true',
    'level2Category': 'Batteries, Starting and Charging',
    'level3Category': 'Batteries',
    'AZ_APP_BANNER_SHOWN': 'true',
    'JSESSIONID': 'oetEILXhspkHa7Ghk_IwB51lAGbpdHkcFHFTiLwoxy209Pn61BR4!1457265935',
    'WWW-WS-ROUTE': 'ffffffff09e9782945525d5f4f58455e445a4a4216ce',
    'preferredStoreId': '6997',
    'GCVE': 'false',
    'bm_ss': 'ab8e18ef4e',
    'profileId': '322451245073',
    'loginInteractionMethod': '',
    'userVehicleCount': '0',
    'cartProductPartIds': '',
    'cartProductSkus': '',
    'cartProductTitles': '',
    'cartProductVendors': '',
    'cartUnitPrice': '',
    'cartCorePrice': '',
    'cartDiscountPriceList': '',
    'rxVisitor': '1766374557602UIF7KUQL02R42AL8J8CV33IUHM4JP8CM',
    'AMCVS_0E3334FA53DA8C980A490D44%40AdobeOrg': '1',
    'AMCV_0E3334FA53DA8C980A490D44%40AdobeOrg': '1406116232%7CMCIDTS%7C20445%7CMCMID%7C69847302916069607832568946155882566522%7CMCAAMLH-1766979357%7C12%7CMCAAMB-1766979357%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1766381757s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.5.0',
    'sc_lv_s': 'Less%20than%207%20days',
    's_vnum': '1767205800408%26vn%3D3',
    's_invisit': 'true',
    's_p24': 'https%3A%2F%2Fwww.autozone.com%2F',
    's_cc': 'true',
    'pxcts': '5425e512-dee7-11f0-910b-ac8103b8426c',
    'QuantumMetricSessionID': 'cb43f5296003f166fb5d987f0b8cdc82',
    '_y2': '1%3AeyJjIjp7fX0%3D%3AMTc0OTg2MjMwNA%3D%3D%3A99',
    'seerses': 'e',
    'thrive_lp_msec': '1766374559472',
    'thrive_lp': 'https%3A%2F%2Fwww.autozone.com%2F',
    'thrive_60m_msec': '1766374559472',
    'dtPC': '-4142$574553859_761h-vURGDFREMUCQCOMFBLGCLFLNLMQHUFBBM-0e0',
    'rxvt': '1766376363937|1766374563937',
    'botStatus': 'Not a Bot',
    'dtSa': '-',
    '_pxdc': 'Human',
    'OptanonAlertBoxClosed': '2025-12-22T03:49:20.963Z',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Mon+Dec+22+2025+09%3A19%3A21+GMT%2B0530+(India+Standard+Time)&version=202510.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=e9db8750-32d6-439c-b5c3-57a7fbf913df&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=IN%3BKL',
    '_scid_r': 'sOCI_61vc4w3OUkE7F3H7oR1RHLvhqpap0XUPQ',
    'RT': '"z=1&dm=www.autozone.com&si=ca6398b1-550c-427f-99bf-b5d2253cdf97&ss=mjglsvd3&sl=2&tt=363&obo=1&rl=1&nu=43mj4fvq&cl=itud"',
    'QSI_HistorySession': 'https%3A%2F%2Fwww.autozone.com%2F~1766374559583%7Chttps%3A%2F%2Fwww.autozone.com%2Fbatteries-starting-and-charging%2Fbattery~1766375431475',
    'prevUrlRouteValue': '%2Fbatteries-starting-and-charging%2Fbattery',
    'redirect_url': '%2Fbatteries-starting-and-charging%2Fbattery',
    'userType': '3',
    'nddMarket': 'N%2FA',
    'nddHub': 'N%2FA',
    'nddStore': 'N%2FA',
    'availableRewardBalance': '0',
    'prevPageType': 'ProductShelf',
    'dtCookie': 'v_4_srv_6_sn_8R247DTB4BAU6OSVIL5HNKPNP6VPTFR9_perc_100000_ol_0_mul_1_app-3A533fc11017a2a54e_0_rcs-3Acss_1',
    's_pn': 'az%3Acatalog%3Abatteries%2C-starting-and-charging%3Abatteries%3Ashelf',
    's_tbe': '1766375437871',
    '_ga_GEFNYC68GY': 'GS2.1.s1766374558$o4$g1$t1766375437$j60$l1$h136216349',
    'utag_main': 'v_id:019b35e9dac70003b8a038aa188b05065001905d00bd0$_sn:4$_se:4$_ss:0$_st:1766377237803$vapi_domain:autozone.com$dc_visit:4$ses_id:1766374556607%3Bexp-session$_pn:3%3Bexp-session$dc_event:4%3Bexp-session$dc_region:me-central-1%3Bexp-session',
    's_ppvl': 'az%253Ahome%2C34%2C5%2C1761%2C1682%2C531%2C1920%2C1080%2C1.1%2CP',
    'mt.aa': 'CB2C12956-Remove-nearby-store_2068845:Experiment%7CDXM4976-DIY-Tonneau-Covers_2063848:Control%7CDXM4976-DIY-Tonneau-Covers_2063848:Control%7CDXM5035-Rate-Review-Addition:Experiment%7CDXM5041-Product-recs-moved:Control',
    'az_bt_cl': 'hPp0YAbH2l1Jzlm4TTBcIb2FTD+B7tTCyDf9kId3WS7mA6o1ZMyfIimqCeDn//dS',
    'az_bt_al': '9bc892cfaa0dfcfb4cff01089b1bf37a',
    's_ppv': 'az%253Acatalog%253Abatteries%252C-starting-and-charging%253Abatteries%253Ashelf%2C74%2C5%2C8376%2C1682%2C304%2C1920%2C1080%2C1.1%2CP',
    'sc_nrv': '1766375720147-Repeat',
    'sc_lv': '1766375720148',
    's_sq': 'autozmobilefirstprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Daz%25253Acatalog%25253Abatteries%25252C-starting-and-charging%25253Abatteries%25253Ashelf%2526link%253DLOAD%252520MORE%2526region%253Dshelf-results-container%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Daz%25253Acatalog%25253Abatteries%25252C-starting-and-charging%25253Abatteries%25253Ashelf%2526pidt%253D1%2526oid%253Dfunctionse%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DBUTTON',
    'bm_s': 'YAAQxUvSF+reUTKbAQAA6IUyRARNkjif1ZUFewwPiQnK3qGWwJ1fpNE8JBVeVt+hWLDxsoxxo81En1xKqD/hLdn2pxNZvEtLE5oDVKCCf9O+KCcrWP5XmqJnCxBeES/xWYLTCzbBGLaofbqX4XR7U3wLRTpefm46ZdUwBJl/brwS8WZvjaiL/3fyH3ZRtVwbCoGVA8WAac+XRNx5tb/3tYLlVHasP7NJRc25sP1BulPxM1AzLds3Un735397KJaEQ5e3nmjomm3FvfxteArzmBXdrepefMKrYHMSkOHU2S1rVDP+TwC53M6VWhJnYyx2i6I0Vx4F/uh9+TzNGPoqm56dhcHEjt6gAHild9zi4x4TexjWGZCOrXvg3GhhnRi94KwubbiLBXnw1O0JtOWvXE9T5IH3cBPl52AG5/QSGTVNALGi1BGIstm0CrW4BoL34VhiKlZHIjEGnZ3kn6HQ9bmoij6ytKjMMZ8stUP8nfrgp392IRGHV1M5X8bo4q88T6EaBtqpLyf6IfLNzmRb/V9bEudbdIjWsF8rPZHqc6PR2POwwkbEqdquuqBcV/w37XEKTLMS6bNf',
    'bm_so': '240075052663D0E0B8FB678731BAB07467E2B3F651609320A4F623D246CB26D1~YAAQxUvSF+veUTKbAQAA6IUyRAbqdbUhrEaJ4p/p8XEJLyBksPgnM+szlgbuhFeTS6/2bGrgPg2KJxBw/NQHmaLs/bOGlccp3tx1IZxqAWngQVMcLXokZguhptZliCXNAXg/M8csJOZilvpv7aIVM+DfeTh/Vnnqj7MdUgjgBv75Nq6+vSJuGHi08sSFfNHqTDIcGA6vkK5a2Bpjz2vov4GWLwnCDAXXHU4EH7Tle6aF6+2OarKIThuj6T7mukDFMYF/PpsT49pjBkXpEzfIEG4Ms1i434ddsn2M4DtGoYgcpwOE3eVArzg4mGxS4qPH8vNmKkB+lsHFQIj7YV6sGTDwlJRAJOCKMXzfx8+u2Fad26XARpB+PS+qLaqUPl00VaquH8e3LyNsHpiflfNEQWR/T09S3RsyBPJvWgnHyrWd+Ca8GJwunY7ksbi4LDgNeTxWmPVGOSUlTMF6ORJ7lQ==',
    'bm_lso': '240075052663D0E0B8FB678731BAB07467E2B3F651609320A4F623D246CB26D1~YAAQxUvSF+veUTKbAQAA6IUyRAbqdbUhrEaJ4p/p8XEJLyBksPgnM+szlgbuhFeTS6/2bGrgPg2KJxBw/NQHmaLs/bOGlccp3tx1IZxqAWngQVMcLXokZguhptZliCXNAXg/M8csJOZilvpv7aIVM+DfeTh/Vnnqj7MdUgjgBv75Nq6+vSJuGHi08sSFfNHqTDIcGA6vkK5a2Bpjz2vov4GWLwnCDAXXHU4EH7Tle6aF6+2OarKIThuj6T7mukDFMYF/PpsT49pjBkXpEzfIEG4Ms1i434ddsn2M4DtGoYgcpwOE3eVArzg4mGxS4qPH8vNmKkB+lsHFQIj7YV6sGTDwlJRAJOCKMXzfx8+u2Fad26XARpB+PS+qLaqUPl00VaquH8e3LyNsHpiflfNEQWR/T09S3RsyBPJvWgnHyrWd+Ca8GJwunY7ksbi4LDgNeTxWmPVGOSUlTMF6ORJ7lQ==~1766375720941',
    '_yi': '1%3AeyJsaSI6eyJjIjowLCJjb2wiOjIyNjg4NzcwMTAsImNwZyI6Mjc2NTc3LCJjcGkiOjcwMzM1MTg3MzExLCJzYyI6MiwidHMiOjE3NjYxNDU1NDgyNzd9LCJzZSI6eyJjIjozLCJlYyI6MTEsImxhIjoxNzY2Mzc1NzIwOTc2LCJwIjo0LCJzYyI6MTE1NH0sInUiOnsiaWQiOiI0NzU0YzE5ZC05ODAxLTRhZjMtYjlkYi1iZGU0OTI1OTY5YzAiLCJmbCI6IjAifX0%3D%3ALTE4MDY5MDc0ODg%3D%3A99',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'ecookieid': 'af497e4d-4e96-4c0f-80c6-f0026f79ec9a',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.autozone.com/batteries-starting-and-charging/battery',
    'sales-channel': 'AZRMFWEB',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'x-requested-by': 'MF',
    # 'cookie': 'REQUEST_ID=Ir_trn2uCdivKWUCaDv0S; mt.v=5.2113638288.1766136073163; preferedstore=6997; eCookieId=af497e4d-4e96-4c0f-80c6-f0026f79ec9a; akacd_default=2147483647~rv=53~id=e4aadede6bde93169b6f7a8f0bd850fd; _pxhd=1c375643dd0e2ce960ab6a095ac7bd8d94d14076be84d22f5d56cb62a4d40a53:0ff531a6-dcbc-11f0-bbce-393e09930bbe; eCookieId=af497e4d-4e96-4c0f-80c6-f0026f79ec9a; RES_TRACKINGID=648008875727071; _pxvid=0ff531a6-dcbc-11f0-bbce-393e09930bbe; s_ecid=MCMID%7C69847302916069607832568946155882566522; _scid=pmCI_61vc4w3OUkE7F3H7oR1RHLvhqpa; _gcl_au=1.1.674812607.1766136080; _ga=GA1.1.2107962357.1766136080; QuantumMetricUserID=06d8831bdc3e9e9d361800599997d7aa; seerid=af352cf9-deda-42af-af2c-a880787a44e3; _fbp=fb.1.1766136080096.626553772490140020; _ScCbts=%5B%22272%3Bchrome.2%3A2%3A5%22%2C%22289%3Bchrome.2%3A2%3A5%22%5D; thrive_fp_uuid=AAAAAZs16ehU2Bk4plVJjjEtLMp33PmYCV6FTUXsxW_ELEnyttOq4L0u; _sctr=1%7C1766082600000; cs-personalize-user-uid=1c9aa302-5989-5725-9fbf-91b08c8ce3eb; cs-lytics-audiences=|all|anonymous_profiles|smt_new|; cs-lytics-flows=||; level1Category=Auto Parts; QSI_SI_9ud5OjHx5m8Lxki_intercept=true; BVBRANDID=f1325390-13ec-486e-bedf-d6e54f53c38b; QSI_SI_enaOc3sA6n8rkVg_intercept=true; level2Category=Batteries, Starting and Charging; level3Category=Batteries; AZ_APP_BANNER_SHOWN=true; JSESSIONID=oetEILXhspkHa7Ghk_IwB51lAGbpdHkcFHFTiLwoxy209Pn61BR4!1457265935; WWW-WS-ROUTE=ffffffff09e9782945525d5f4f58455e445a4a4216ce; preferredStoreId=6997; GCVE=false; bm_ss=ab8e18ef4e; profileId=322451245073; loginInteractionMethod=; userVehicleCount=0; cartProductPartIds=; cartProductSkus=; cartProductTitles=; cartProductVendors=; cartUnitPrice=; cartCorePrice=; cartDiscountPriceList=; rxVisitor=1766374557602UIF7KUQL02R42AL8J8CV33IUHM4JP8CM; AMCVS_0E3334FA53DA8C980A490D44%40AdobeOrg=1; AMCV_0E3334FA53DA8C980A490D44%40AdobeOrg=1406116232%7CMCIDTS%7C20445%7CMCMID%7C69847302916069607832568946155882566522%7CMCAAMLH-1766979357%7C12%7CMCAAMB-1766979357%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1766381757s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.5.0; sc_lv_s=Less%20than%207%20days; s_vnum=1767205800408%26vn%3D3; s_invisit=true; s_p24=https%3A%2F%2Fwww.autozone.com%2F; s_cc=true; pxcts=5425e512-dee7-11f0-910b-ac8103b8426c; QuantumMetricSessionID=cb43f5296003f166fb5d987f0b8cdc82; _y2=1%3AeyJjIjp7fX0%3D%3AMTc0OTg2MjMwNA%3D%3D%3A99; seerses=e; thrive_lp_msec=1766374559472; thrive_lp=https%3A%2F%2Fwww.autozone.com%2F; thrive_60m_msec=1766374559472; dtPC=-4142$574553859_761h-vURGDFREMUCQCOMFBLGCLFLNLMQHUFBBM-0e0; rxvt=1766376363937|1766374563937; botStatus=Not a Bot; dtSa=-; _pxdc=Human; OptanonAlertBoxClosed=2025-12-22T03:49:20.963Z; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Dec+22+2025+09%3A19%3A21+GMT%2B0530+(India+Standard+Time)&version=202510.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=e9db8750-32d6-439c-b5c3-57a7fbf913df&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=IN%3BKL; _scid_r=sOCI_61vc4w3OUkE7F3H7oR1RHLvhqpap0XUPQ; RT="z=1&dm=www.autozone.com&si=ca6398b1-550c-427f-99bf-b5d2253cdf97&ss=mjglsvd3&sl=2&tt=363&obo=1&rl=1&nu=43mj4fvq&cl=itud"; QSI_HistorySession=https%3A%2F%2Fwww.autozone.com%2F~1766374559583%7Chttps%3A%2F%2Fwww.autozone.com%2Fbatteries-starting-and-charging%2Fbattery~1766375431475; prevUrlRouteValue=%2Fbatteries-starting-and-charging%2Fbattery; redirect_url=%2Fbatteries-starting-and-charging%2Fbattery; userType=3; nddMarket=N%2FA; nddHub=N%2FA; nddStore=N%2FA; availableRewardBalance=0; prevPageType=ProductShelf; dtCookie=v_4_srv_6_sn_8R247DTB4BAU6OSVIL5HNKPNP6VPTFR9_perc_100000_ol_0_mul_1_app-3A533fc11017a2a54e_0_rcs-3Acss_1; s_pn=az%3Acatalog%3Abatteries%2C-starting-and-charging%3Abatteries%3Ashelf; s_tbe=1766375437871; _ga_GEFNYC68GY=GS2.1.s1766374558$o4$g1$t1766375437$j60$l1$h136216349; utag_main=v_id:019b35e9dac70003b8a038aa188b05065001905d00bd0$_sn:4$_se:4$_ss:0$_st:1766377237803$vapi_domain:autozone.com$dc_visit:4$ses_id:1766374556607%3Bexp-session$_pn:3%3Bexp-session$dc_event:4%3Bexp-session$dc_region:me-central-1%3Bexp-session; s_ppvl=az%253Ahome%2C34%2C5%2C1761%2C1682%2C531%2C1920%2C1080%2C1.1%2CP; mt.aa=CB2C12956-Remove-nearby-store_2068845:Experiment%7CDXM4976-DIY-Tonneau-Covers_2063848:Control%7CDXM4976-DIY-Tonneau-Covers_2063848:Control%7CDXM5035-Rate-Review-Addition:Experiment%7CDXM5041-Product-recs-moved:Control; az_bt_cl=hPp0YAbH2l1Jzlm4TTBcIb2FTD+B7tTCyDf9kId3WS7mA6o1ZMyfIimqCeDn//dS; az_bt_al=9bc892cfaa0dfcfb4cff01089b1bf37a; s_ppv=az%253Acatalog%253Abatteries%252C-starting-and-charging%253Abatteries%253Ashelf%2C74%2C5%2C8376%2C1682%2C304%2C1920%2C1080%2C1.1%2CP; sc_nrv=1766375720147-Repeat; sc_lv=1766375720148; s_sq=autozmobilefirstprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Daz%25253Acatalog%25253Abatteries%25252C-starting-and-charging%25253Abatteries%25253Ashelf%2526link%253DLOAD%252520MORE%2526region%253Dshelf-results-container%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Daz%25253Acatalog%25253Abatteries%25252C-starting-and-charging%25253Abatteries%25253Ashelf%2526pidt%253D1%2526oid%253Dfunctionse%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DBUTTON; bm_s=YAAQxUvSF+reUTKbAQAA6IUyRARNkjif1ZUFewwPiQnK3qGWwJ1fpNE8JBVeVt+hWLDxsoxxo81En1xKqD/hLdn2pxNZvEtLE5oDVKCCf9O+KCcrWP5XmqJnCxBeES/xWYLTCzbBGLaofbqX4XR7U3wLRTpefm46ZdUwBJl/brwS8WZvjaiL/3fyH3ZRtVwbCoGVA8WAac+XRNx5tb/3tYLlVHasP7NJRc25sP1BulPxM1AzLds3Un735397KJaEQ5e3nmjomm3FvfxteArzmBXdrepefMKrYHMSkOHU2S1rVDP+TwC53M6VWhJnYyx2i6I0Vx4F/uh9+TzNGPoqm56dhcHEjt6gAHild9zi4x4TexjWGZCOrXvg3GhhnRi94KwubbiLBXnw1O0JtOWvXE9T5IH3cBPl52AG5/QSGTVNALGi1BGIstm0CrW4BoL34VhiKlZHIjEGnZ3kn6HQ9bmoij6ytKjMMZ8stUP8nfrgp392IRGHV1M5X8bo4q88T6EaBtqpLyf6IfLNzmRb/V9bEudbdIjWsF8rPZHqc6PR2POwwkbEqdquuqBcV/w37XEKTLMS6bNf; bm_so=240075052663D0E0B8FB678731BAB07467E2B3F651609320A4F623D246CB26D1~YAAQxUvSF+veUTKbAQAA6IUyRAbqdbUhrEaJ4p/p8XEJLyBksPgnM+szlgbuhFeTS6/2bGrgPg2KJxBw/NQHmaLs/bOGlccp3tx1IZxqAWngQVMcLXokZguhptZliCXNAXg/M8csJOZilvpv7aIVM+DfeTh/Vnnqj7MdUgjgBv75Nq6+vSJuGHi08sSFfNHqTDIcGA6vkK5a2Bpjz2vov4GWLwnCDAXXHU4EH7Tle6aF6+2OarKIThuj6T7mukDFMYF/PpsT49pjBkXpEzfIEG4Ms1i434ddsn2M4DtGoYgcpwOE3eVArzg4mGxS4qPH8vNmKkB+lsHFQIj7YV6sGTDwlJRAJOCKMXzfx8+u2Fad26XARpB+PS+qLaqUPl00VaquH8e3LyNsHpiflfNEQWR/T09S3RsyBPJvWgnHyrWd+Ca8GJwunY7ksbi4LDgNeTxWmPVGOSUlTMF6ORJ7lQ==; bm_lso=240075052663D0E0B8FB678731BAB07467E2B3F651609320A4F623D246CB26D1~YAAQxUvSF+veUTKbAQAA6IUyRAbqdbUhrEaJ4p/p8XEJLyBksPgnM+szlgbuhFeTS6/2bGrgPg2KJxBw/NQHmaLs/bOGlccp3tx1IZxqAWngQVMcLXokZguhptZliCXNAXg/M8csJOZilvpv7aIVM+DfeTh/Vnnqj7MdUgjgBv75Nq6+vSJuGHi08sSFfNHqTDIcGA6vkK5a2Bpjz2vov4GWLwnCDAXXHU4EH7Tle6aF6+2OarKIThuj6T7mukDFMYF/PpsT49pjBkXpEzfIEG4Ms1i434ddsn2M4DtGoYgcpwOE3eVArzg4mGxS4qPH8vNmKkB+lsHFQIj7YV6sGTDwlJRAJOCKMXzfx8+u2Fad26XARpB+PS+qLaqUPl00VaquH8e3LyNsHpiflfNEQWR/T09S3RsyBPJvWgnHyrWd+Ca8GJwunY7ksbi4LDgNeTxWmPVGOSUlTMF6ORJ7lQ==~1766375720941; _yi=1%3AeyJsaSI6eyJjIjowLCJjb2wiOjIyNjg4NzcwMTAsImNwZyI6Mjc2NTc3LCJjcGkiOjcwMzM1MTg3MzExLCJzYyI6MiwidHMiOjE3NjYxNDU1NDgyNzd9LCJzZSI6eyJjIjozLCJlYyI6MTEsImxhIjoxNzY2Mzc1NzIwOTc2LCJwIjo0LCJzYyI6MTE1NH0sInUiOnsiaWQiOiI0NzU0YzE5ZC05ODAxLTRhZjMtYjlkYi1iZGU0OTI1OTY5YzAiLCJmbCI6IjAifX0%3D%3ALTE4MDY5MDc0ODg%3D%3A99',
}
# -------------------------------------------------
# CATEGORIES TO CRAWL (CHAINED)
# -------------------------------------------------
CATEGORIES = [
    {
        "name": "battery",
        "canonicalPath": "/batteries-starting-and-charging/battery",
        "taxonomyPath": "/parts/batteries-starting-and-charging/batteries/battery",
        "referer": "https://www.autozone.com/batteries-starting-and-charging/battery",
    },
    {
        "name": "spark_plug",
        "canonicalPath": "/external-engine/spark-plug",
        "taxonomyPath": "/parts/external-engine/ignition/spark-plug",
        "referer": "https://www.autozone.com/external-engine/spark-plug",
    },
]

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
# -------------------------------------------------
def extract_price(price_raw):
    if isinstance(price_raw, dict):
        current = price_raw.get("currentPrice")
        if isinstance(current, dict):
            return current.get("value", 0)
        return 0
    if isinstance(price_raw, (int, float)):
        return price_raw
    return 0


def parse_items(data, category_name):
    sku_records = data.get("productShelfResults", {}).get("skuRecords", [])
    items = []

    for sku in sku_records:
        items.append({
            "category": category_name,
            "name": sku.get("itemDescription", ""),
            "sku": sku.get("itemId", ""),
            "part_number": sku.get("partNumber", ""),
            "brand": sku.get("brandName", ""),
            "price": extract_price(sku.get("price")),
            "instock": sku.get("activeFlag", False),
            "manufacturer": sku.get("lineCode", ""),
            "mpn": sku.get("partNumber", ""),
            "warranty_months": sku.get("warrantyMonths") or 0,
        })

    return items

# -------------------------------------------------
# CATEGORY CRAWLER
# -------------------------------------------------
def crawl_category(category):
    page = 1
    records_per_page = 24

    logging.info(f"Starting category: {category['name']}")

    while True:
        params = {
            "country": "USA",
            "customerType": "B2C",
            "salesChannel": "ECOMM",
            "preview": "false",
            "canonicalPath": category["canonicalPath"],
            "pageNumber": page,
            "recordsPerPage": records_per_page,
            "storeId": "6997",
            "ignoreVehicleSpecificProductsCheck": "false",
            "taxonomyPath": category["taxonomyPath"],
            "partNumberSearch": "false",
        }

        headers["referer"] = category["referer"]

        response = requests.get(
            BASE_URL,
            headers=headers,
            cookies=cookies,
            params=params,
            timeout=30
        )

        logging.info(f"[{category['name']}] Page {page} → {response.status_code}")

        if response.status_code != 200:
            logging.error("Non-200 response. Stopping category.")
            break

        data = response.json()
        items = parse_items(data, category["name"])

        if not items:
            logging.info("No more products in category.")
            break

        ALL_PRODUCTS.extend(items)

        if len(items) < records_per_page:
            logging.info("Last page reached.")
            break

        page += 1
        time.sleep(random.uniform(1.5, 3.5))

    logging.info(f"Finished category: {category['name']}")

# -------------------------------------------------
# SAVE JSON
# -------------------------------------------------
def save_to_json():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(ALL_PRODUCTS, f, indent=2, ensure_ascii=False)

    logging.info(f"Saved {len(ALL_PRODUCTS)} products → {OUTPUT_FILE}")

# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
def start():
    for category in CATEGORIES:
        crawl_category(category)

    save_to_json()

if __name__ == "__main__":
    start()