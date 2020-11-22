"""Core functions for interacting with Rutgers SOC."""

from urllib.parse import urlencode, quote

import requests

import config

def get_open_sections():
    """Retrieve all open section index numbers from SOC.

    Returns:
        A list of all open section index numbers. list of strs.
    """
    # Construct API URL from config parameters
    PARAMS_SOC = urlencode(config.QUERY_PARAMS_SOC_API, quote_via=quote)
    API_URL = f"http://sis.rutgers.edu/soc/api/openSections.gzip?{PARAMS_SOC}"

    resp = requests.get(API_URL)
    if resp.status_code != 200:
        print("Error with SOC API request")
        print("Status Code:", resp.status_code)
        print("Text:", resp.text)
        raise Exception("SOC API failed to retrieve open sections.")

    return resp.json()


def check_section_is_open(section, open_sections):
    """Check if a section is currently open.

    Given an index number of a section, check if it is in the list of
    open section. Implemented with binary search.

    Args:
        section:
            The index number of a section. str.
        open_sections:
            The list of all open section index numbers. list of strs.

    Returns:
        A bool for whether or not the section is open.
    """
    lo = 0
    hi = len(open_sections) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if open_sections[mid] == section:
            return True
        if open_sections[mid] > section:
            hi = mid - 1
        else:
            lo = mid + 1
    return False
