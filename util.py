"""Utility functions."""

import json
import pyrebase

import config


def save_all_sections_sp21():
    with open("sp21/courses.json") as f1, open("sp21/allSections.json", "w") as f2:
        soc = json.load(f1)
        all_sections = []
        for course in soc:
            for section in course["sections"]:
                all_sections.append(section["index"])
        f2.write(json.dumps(sorted(all_sections)))


def clear_db():
    db = pyrebase.initialize_app(config.FIREBASE).database()
    db.remove()


def get_section(section):
    db = pyrebase.initialize_app(config.FIREBASE).database()
    return db.child(section).get().val()


if __name__ == "__main__":
    pass
    # save_all_sections_sp21()
    # clear_db()
    # print(get_section("07303"))
    # print(get_section("20724"))
