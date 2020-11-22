"""Utility functions."""

def save_all_sections_sp21():
    with open("sp21/courses.json") as f1, open("sp21/allSections.json", "w") as f2:
    soc = json.load(f1)
    all_sections = []
    for course in soc:
        for section in course["sections"]:
            all_sections.append(section["index"])
    f2.write(json.dumps(sorted(all_sections)))
