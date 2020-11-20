import time
from urllib.parse import urlencode, quote

import pyrebase
import requests

import config

firebase = pyrebase.initialize_app(config.FIREBASE)
db = firebase.database()

# Construct API URL from config parameters
PARAMS_SOC = urlencode(config.QUERY_PARAMS_SOC_API, quote_via=quote)
API_URL = f"http://sis.rutgers.edu/soc/api/openSections.gzip?{PARAMS_SOC}"

resp = requests.get(API_URL)
if resp.status_code != 200:
    print("Error with SOC API request")
    print("Status Code:", resp.status_code)
    print("Text:", resp.text)
    raise Exception("SOC API failed to retrieve open sections.")

db.child("spring21").update({int(time.time()): resp.json()})
