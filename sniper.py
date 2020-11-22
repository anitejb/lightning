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
from urllib.parse import urlencode, quote

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
import requests

import config
from soc import get_open_sections, check_section_is_open


def check_time_in_bounds():
    """Check if current time is within WebReg operational hours.

    SOC is still active when WebReg is down, but there's no reason to
    check for open courses if you can't register for them ¯\_(ツ)_/¯

    Returns:
        A bool for whether or not the current time is within bounds.
    """
    # WebReg is down [2:00 AM, 6:00 AM)
    WEBREG_DOWN = datetime(1970, 1, 1, 2, 00, tzinfo=timezone("US/Eastern")).time()
    WEBREG_UP = datetime(1970, 1, 1, 6, 00, tzinfo=timezone("US/Eastern")).time()

    curr_time = datetime.now(timezone("US/Eastern")).time()

    return curr_time < WEBREG_DOWN or WEBREG_UP <= curr_time


def notify(section):
    """Send an email with a link to register for an open section.

    Given an index number of a section, generate a link that leads to
    WebReg and has the section index prefilled. Send an email with
    the link to all addresses in config.CONTACT_EMAILS via Mailgun.

    Q > Why doesn't Lightning just add the course section for you?
    A > From https://sims.rutgers.edu/webreg/, "The use of automated
        software for registration is prohibited. If detected, the
        student's online registration privileges will be suspended."
        Generating a link (just like CSP) is as close as we can get :D

    Args:
        section:
            The index number of a section. str.

    Raises:
        Exception: Mailgun failed to send an email.
    """
    # Construct WebReg easy registration link from config parameters
    config.QUERY_PARAMS_WEBREG["indexList"] = section
    params = urlencode(config.QUERY_PARAMS_WEBREG, quote_via=quote)
    webreg_link = f"http://sims.rutgers.edu/webreg/editSchedule.htm?{params}"

    # Send email via Mailgun
    resp = requests.post(
        f"http://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
        auth=("api", config.MAILGUN_API_KEY),
        data={
            "from": f"Lightning <mailgun@{config.MAILGUN_DOMAIN}>",
            "to": config.CONTACT_EMAILS,
            "subject": f"{section} opened up!",
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


def main():
    """Cron function to check if any desired courses are open.

    Raises:
        Exception: SOC API failed to retrieve open sections.
        Exception: No desired courses remaining. Shutting down.
    """
    if not check_time_in_bounds():
        return

    open_sections = get_open_sections()

    if not config.DESIRED_SECTIONS:
        raise Exception("No desired courses remaining. Shutting down.")

    for section in set(config.DESIRED_SECTIONS):
        if check_section_is_open(section, open_sections):
            notify(section)
            # Once a notification for a section has been sent, prevent
            # duplicate emails for the same section from sending
            config.DESIRED_SECTIONS.remove(section)


def shutdown(event):
    """Terminate cron job."""
    if scheduler.running:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    print("Lightning is listening...")
    # Initial cron trigger
    main()
    # Set cron function to be executed in intervals of 15 seconds
    scheduler = BlockingScheduler()
    scheduler.add_listener(shutdown, EVENT_JOB_ERROR)
    scheduler.add_job(main, "interval", seconds=15)
    scheduler.start()
