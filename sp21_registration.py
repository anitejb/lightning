import json
import time

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
import pyrebase

import config
from soc import get_open_sections, check_section_is_open


def update_db(db, all_sections, open_sections):
    timestamp = int(time.time())

    try:
        current_db = dict(db.get().val())
    except:
        current_db = dict()
    latest_db = {section: dict() for section in all_sections}

    flipped_open = []
    flipped_closed = []

    for section in all_sections:
        if check_section_is_open(section, open_sections):
            latest_db[section]["status"] = 1
            latest_db[section]["flip"] = (
                current_db[section]["flip"] if section in current_db else []
            )
            if section not in current_db or current_db[section]["status"] == 0:
                latest_db[section]["flip"].append(timestamp)
                flipped_open.append(section)
        else:
            latest_db[section]["status"] = 0
            latest_db[section]["flip"] = (
                current_db[section]["flip"] if section in current_db else []
            )
            if section not in current_db or current_db[section]["status"] == 1:
                latest_db[section]["flip"].append(timestamp)
                flipped_closed.append(section)

    latest_db["timestamps"] = current_db.get("timestamps", []) + [timestamp]
    db.update(latest_db)

    print(
        f"Updated @ {int(time.time())} || Flipped Open: {flipped_open} || Flip Closed: {flipped_closed}"
    )


def main():
    db = pyrebase.initialize_app(config.FIREBASE).database()
    with open("sp21/allSections.json", "r") as f:
        all_sections = json.load(f)
    open_sections = get_open_sections()

    update_db(db, all_sections, open_sections)


def shutdown(event):
    """Terminate cron job."""
    if scheduler.running:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    print(f"Started @ {int(time.time())}")
    # Initial cron trigger
    main()
    # Set cron function to be executed in intervals of 10 minutes
    scheduler = BlockingScheduler()
    scheduler.add_listener(shutdown, EVENT_JOB_ERROR)
    scheduler.add_job(main, "interval", minutes=10)
    scheduler.start()
