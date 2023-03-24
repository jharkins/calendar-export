# Google Calendar Export

A Python script to export Google Calendar events for the last N days in CSV or JSON format. The script can output the events to a file or print them to the screen.

Created by Joe Harkins ([jharkins](https://github.com/jharkins)) and [OpenAI's ChatGPT](https://www.openai.com/).

## Features

- Export Google Calendar events for the last N days (default: 7)
- Output format: CSV or JSON
- Save the events to a file or print them to the screen
- Token-based authentication to avoid re-authenticating every time the script is run

## Prerequisites

- Python 3.6 or higher
- A Google Account with access to Google Calendar
- Google API credentials file (`credentials.json`)

## Setup

1. Clone this repository:

```
git clone https://github.com/jharkins/google-calendar-export.git
cd google-calendar-export
```

2. Create a virtual environment and install the required packages:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Enable the Google Calendar API and obtain the `credentials.json` file:

- Go to the [Google API Console](https://console.developers.google.com/)
- Click "Create Project" and set up a new project
- Search for "Google Calendar API" in the search bar
- Click "Enable" to enable the Google Calendar API for your project
- Click "Create credentials" and follow the prompts
- Download the `credentials.json` file and place it in the `google-calendar-export` directory

## Usage

`python calendar-export.py [-d DAYS] [-m {json,csv}] [-f FILE | -o]`

- `-d, --days`: Number of days to look back (default: 7)
- `-m, --mode`: Output mode: json or csv (default: csv)
- `-f, --file`: Output file name (mutually exclusive with `-o`)
- `-o, --output`: Print output to the screen (mutually exclusive with `-f`)

## Examples

Export the last 7 days of events in CSV format (default) to a file:

`python calendar-export.py`

Export the last 14 days of events in JSON format to a file:

`python calendar-export.py -d 14 -m json`

Print the last 7 days of events in CSV format to the screen:

`python calendar-export.py -o`

Print the last 14 days of events in JSON format to the screen:

`python calendar-export.py -d 14 -m json -o`
