import json
import time

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
import pyrebase

import config
from soc import get_open_sections, check_section_is_open


class Registration:
    def __init__(self):
        self.db = pyrebase.initialize_app(config.FIREBASE).database()
        try:
            self.current_db = dict(self.db.get().val())
        except:
            self.current_db = dict()

        with open("sp21/allSections.json", "r") as f:
            self.all_sections = json.load(f)

    def update_db(self, open_sections):
        timestamp = int(time.time())
        latest_db = {section: dict() for section in self.all_sections}
        flipped_open = []
        flipped_closed = []

        for section in self.all_sections:
            if check_section_is_open(section, open_sections):
                latest_db[section]["status"] = 1
                latest_db[section]["flip"] = (
                    self.current_db[section]["flip"]
                    if section in self.current_db
                    else []
                )
                if (
                    section not in self.current_db
                    or self.current_db[section]["status"] == 0
                ):
                    latest_db[section]["flip"].append(timestamp)
                    flipped_open.append(section)
            else:
                latest_db[section]["status"] = 0
                latest_db[section]["flip"] = (
                    self.current_db[section]["flip"]
                    if section in self.current_db
                    else []
                )
                if (
                    section not in self.current_db
                    or self.current_db[section]["status"] == 1
                ):
                    latest_db[section]["flip"].append(timestamp)
                    flipped_closed.append(section)

        latest_db["timestamps"] = self.current_db.get("timestamps", []) + [timestamp]
        self.db.update(latest_db)
        self.current_db = latest_db

        print(
            f"Updated @ {int(time.time())} || Flipped Open: {flipped_open} || Flip Closed: {flipped_closed}"
        )

    def main(self):
        open_sections = get_open_sections()
        self.update_db(open_sections)


def shutdown(event):
    """Terminate cron job."""
    if scheduler.running:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    print(f"Started @ {int(time.time())}")
    registration = Registration()
    # Initial cron trigger
    registration.main()
    # Set cron function to be executed in intervals of 10 minutes
    scheduler = BlockingScheduler()
    scheduler.add_listener(shutdown, EVENT_JOB_ERROR)
    scheduler.add_job(registration.main, "interval", minutes=10)
    scheduler.start()
