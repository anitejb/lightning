# YEAR = 4 digit year
# Sample: 2020
# YEAR = 2020
YEAR = 0

# TERM = 1 digit term (0 for Winter, 1 for Spring, 7 for Summer, 9 for Winter)
# Sample: Fall
# TERM = 9
TERM = 0

# CAMPUS = 2 letter campus ("NB" for New Brunswick, "NK" for Newark, "CM" for Camden)
# Sample: New Brunswick
# CAMPUS = "NB"
CAMPUS = ""

# DESIRED_COURSES = Set of 5 digit index numbers of the courses you want to watch, as strings
# Sample: Index numbers 42205, 08854
# DESIRED_COURSES = {"42205", "08854"}
DESIRED_COURSES = {"00000"}

# Retrieve credentials from your Mailgun account
# Mailgun domain can be found at https://app.mailgun.com/app/sending/domains
MAILGUN_DOMAIN = ""
# Mailgun Private API Key can be found at https://app.mailgun.com/app/account/security/api_keys
MAILGUN_API_KEY = ""

# CONTACT_EMAILS = List of email addresses to notify of a course opening, as strings
# Sample: Email dinesh@piedpiper.com and gilfoyle@piedpiper.com when courses open
# CONTACT_EMAILS = ["dinesh@piedpiper.com", "gilfoyle@piedpiper.com"]
CONTACT_EMAILS = []

##### DO NOT EDIT PAST THIS LINE #####
QUERY_PARAMS_SOC_API = {"year": YEAR, "term": TERM, "campus": CAMPUS}

QUERY_PARAMS_WEBREG = {
    "login": "cas",
    "semesterSelection": f"{TERM}{YEAR}",
    "indexList": None,
}
