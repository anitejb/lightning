# Lightning
![Version](https://img.shields.io/badge/version-0.0.1-blue)

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Helpful Tips](#helpful-tips)
- [License](#license)
- [Disclaimer](#disclaimer)

## Overview
Lightning is a course sniper for real time monitoring of [Rutgers Schedule of Classes](https://sis.rutgers.edu/soc/). Get lightning fast notifications via email when a course you need opens up.

Built with [Python](https://www.python.org/), [Requests](https://requests.readthedocs.io/), [APScheduler](https://apscheduler.readthedocs.io/), [Mailgun](https://www.mailgun.com/), and <3.

## Project Structure
The project is structured as follows. Only `sniper.py` is actually required for Lightning to function, everything else is supplementary for informational purposes.

- `sniper.py`: Contains the cron function that continuously monitors Rutgers SOC for openings.
- `test_processing.py`: Contains time comparison tests between different lookup methods to determine most efficient handling of API response.
- `sample_api_responses/`
    - `courses.gzip`: Sample response from `https://sis.rutgers.edu/soc/api/courses.gzip?year=2020&term=9&campus=NB` (currently unused)
    - `courses.json`: Same content as `courses.gzip`, but formatted nicely :)
    - `openSections.gzip`: Sample response from `https://sis.rutgers.edu/soc/api/openSections.gzip?year=2020&term=9&campus=NB`

## Requirements
The following requirements are necessary in order to set up and use Lightning.

- Python (v3.8.2 and above) - get the latest version [here](https://www.python.org/downloads/).
- Mailgun - sign up for an account [here](https://mailgun.com/).

## Getting Started
Make sure you have all of the necessary [requirements](#requirements) before getting started.

0. Clone the respository.
    - Using HTTPS: `git clone https://github.com/anitejb/lightning`
    - Using SSH: `git clone git@github.com:anitejb/lightning.git`
0. Enter the working directory.
    - `cd ./lightning`
0. Create a virtual environment.
    - `python3 -m venv ./venv`
0. Activate the virtual environment.
    - For Windows users: `venv\Scripts\activate`
    - For Linux/Mac users: `source venv/bin/activate`
0. Install necessary dependencies.
    - `pip3 install -r requirements.txt`
0. Create a new file called `config.py` and copy the contents of `example.config.py` into it.
0. Follow instructions in `config.py` and fill in the specified fields.
0. Run `python3 sniper.py` to launch Lightning.

## Helpful Tips

**Mailgun Free Plan**: The free plan on Mailgun is fine for use with Lightning, but it has certain restrictions. Make sure to add any email addresses you plan on sending notifications to as "Authorized Reciepients" via your Mailgun dashboard. In addition, notification emails from Mailgun sandbox domains often end up in Spam folders. Make sure to add a filter in your email client to catch all emails from `mailgun@<your_mailgun_domain>` and prevent them from going to your Spam folder (for example, the "Never send it to Spam" option in Gmail), so that you don't miss out when a course opens up!

**Rutgers University Emails**: Using a Rutgers provided email account (scarletmail) is not recommended because emails typically take a longer time to reach your inbox. Instead, use a personal account to make sure you get notifications as fast as possible.

**Performance**: Lightning is designed to be running 24/7, which may lead to performance issues if you are using it on a personal computer. To prevent this from happening, consider deploying to a service like [Heroku](https://heroku.com/) instead of deploying Lightning locally.

## License
Copyright (c) 2020 Anitej Biradar. Released under the MIT License. See
[LICENSE](LICENSE) for details.

Questions? Reach out to [lightning@anitejb.dev](mailto:lightning@anitejb.dev), and I'll try to get back to you lightning fast!

## Disclaimer
Lightning is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Rutgers University, or any of its subsidiaries or its affiliates.
