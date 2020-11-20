import time
from urllib.parse import urlencode, quote

import json
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

with open("sp21/allSections.json", "r") as f:
    all_courses = json.load(f)

def check_course_is_open(course):
    """Check if a course is currently open.

    Given an index number of a course, check if it is in the list of
    open courses. Implemented with binary search.

    Args:
        course:
            The index number of a course. str.
        open_sections:
            The list of all open course index numbers. list of strs.

    Returns:
        A bool for whether or not the course is open.
    """
    lo = 0
    hi = len(all_courses) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if all_courses[mid] == course:
            return True
        if all_courses[mid] > course:
            hi = mid - 1
        else:
            lo = mid + 1
    return False

update_db = dict.fromkeys(all_courses, {})
try:
    current_db = dict(db.get().val())
except:
    current_db = dict()

for course in all_courses:
    if check_course_is_open(course):
        update_db[course]["status"] = 1
        update_db[course]["flip"] = current_db[course]["flip"] if course in current_db else []
        if course not in current_db or current_db[course]["status"] == 0:
            update_db[course]["flip"].append(int(time.time()))
    else:
        update_db[course]["status"] = 0
        update_db[course]["flip"] = current_db[course]["flip"] if course in current_db else []
        if course not in current_db or current_db[course]["status"] == 1:
            update_db[course]["flip"].append(int(time.time()))

db.update(update_db)

# # Save all courses
# import json
# with open("sp21/courses.json") as f1, open("sp21/allSections.json", "w") as f2:
#     soc = json.load(f1)
#     all_sections = []
#     for course in soc:
#         for section in course["sections"]:
#             all_sections.append(section["index"])
#     f2.write(json.dumps(sorted(all_sections)))
