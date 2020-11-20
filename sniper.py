"""Lightning - Rutgers Course Sniper

Lightning monitors Rutgers SOC (Schedule of Classes) to see if any
desired courses which were previously closed, are now open. As soon as
a course is identified as open, it sends an email with a link to
register for the class via WebReg.
"""
__author__ = "Anitej Biradar (@anitejb)"
__license__ = "MIT"

from datetime import datetime
from pytz import timezone
import time
from urllib.parse import urlencode, quote

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

import config


def check_time_in_bounds():
    """Check if current time is within WebReg operational hours.

    SOC is still active when WebReg is down, but there's no reason to
    check for open courses if you can't register for them ¯\_(ツ)_/¯

    Returns:
        A bool for whether or not the current time is acceptable.
    """
    # WebReg is down [2:00 AM, 6:00 AM)
    WEBREG_DOWN_START = datetime(1970, 1, 1, 2, 00, tzinfo=timezone("US/Eastern")).time()
    WEBREG_DOWN_END = datetime(1970, 1, 1, 6, 00, tzinfo=timezone("US/Eastern")).time()

    curr_time = datetime.now(timezone("US/Eastern")).time()

    return curr_time < WEBREG_DOWN_START or WEBREG_DOWN_END <= curr_time


def check_course_is_open(course, open_sections):
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
    hi = len(open_sections) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if open_sections[mid] == course:
            return True
        if open_sections[mid] > course:
            hi = mid - 1
        else:
            lo = mid + 1
    return False


def notify(course):
    """Send an email with a link to register for an open course.

    Given an index number of a couse, generate a link that leads to
    WebReg and has the course index prefilled. Send an email with
    the link to all addresses in config.CONTACT_EMAILS via Mailgun.

    Q > Why doesn't Lightning just add the course for you?
    A > From https://sims.rutgers.edu/webreg/, "The use of automated
        software for registration is prohibited. If detected, the
        student's online registration privileges will be suspended."
        Generating a link (just like CSP) is as close as we can get :D

    Args:
        course:
            The index number of a course. str.

    Raises:
        Exception: Mailgun failed to send an email.
    """
    # Construct WebReg easy registration link from config parameters
    config.QUERY_PARAMS_WEBREG["indexList"] = course
    params = urlencode(config.QUERY_PARAMS_WEBREG, quote_via=quote)
    webreg_link = f"http://sims.rutgers.edu/webreg/editSchedule.htm?{params}"

    # Send email via Mailgun
    resp = requests.post(
        f"http://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
        auth=("api", config.MAILGUN_API_KEY),
        data={
            "from": f"Lightning <mailgun@{config.MAILGUN_DOMAIN}>",
            "to": config.CONTACT_EMAILS,
            "subject": f"{course} opened up!",
            "text": f"Click here to register!\n\n{webreg_link}",
        },
    )

    # Mailgun email queued successfullly
    if resp.status_code == 200:
        return

    # Mailgun failed to accept email request
    print("Error with Mailgun request")
    print("Status Code:", resp.status_code)
    print("Text:", resp.text)
    raise Exception("Mailgun failed to send an email.")


def cron():
    """Cron function to check if any desired courses are open.

    Raises:
        Exception: SOC API failed to retrieve open sections.
        Exception: No desired courses remaining. Shutting down.
    """
    if not check_time_in_bounds():
        return

    # Construct API URL from config parameters
    params_soc = urlencode(config.QUERY_PARAMS_SOC_API, quote_via=quote)
    api_url = f"http://sis.rutgers.edu/soc/api/openSections.gzip?{params_soc}"

    resp = requests.get(api_url)
    if resp.status_code != 200:
        print("Error with SOC API request")
        print("Status Code:", resp.status_code)
        print("Text:", resp.text)
        raise Exception("SOC API failed to retrieve open sections.")

    open_courses = resp.json()
    desired_courses = {course for course in config.DESIRED_COURSES}
    if not desired_courses:
        raise Exception("No desired courses remaining. Shutting down.")
    for course in desired_courses:
        if check_course_is_open(course, open_courses):
            notify(course)
            # Once a notification for a course has been sent, prevent
            # duplicate emails for the same course from sending
            config.DESIRED_COURSES.remove(course)


def shutdown(event):
    """Terminate cron job."""
    if scheduler.running:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    # Initial cron trigger
    cron()
    # Set cron function to be executed in intervals of 15 seconds
    scheduler = BlockingScheduler()
    scheduler.add_listener(shutdown, EVENT_JOB_ERROR)
    scheduler.add_job(cron, "interval", seconds=15)
    scheduler.start()
