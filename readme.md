# Google Calendar Export

A Python script to export Google Calendar events for the last N days in CSV or JSON format, and optionally summarize the events using OpenAI's GPT-3.5 Turbo. The script can output the events to a file or print them to the screen.

Created by Joe Harkins ([jharkins](https://github.com/jharkins)) and [OpenAI's ChatGPT](https://www.openai.com/).

## Features

- Export Google Calendar events for the last N days (default: 7)
- Output format: CSV or JSON
- Save the events to a file or print them to the screen
- Token-based authentication to avoid re-authenticating every time the script is run
- Summarize events using OpenAI's GPT-3.5 Turbo (optional)

## Prerequisites

- Python 3.6 or higher
- A Google Account with access to Google Calendar
- Google API credentials file (credentials.json)
- OpenAI API key (optional, for event summarization)

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

3. Enable the Google Calendar API and obtain the credentials.json file:

- Go to the [Google API Console](https://console.developers.google.com/)
- Click "Create Project" and set up a new project
- Search for "Google Calendar API" in the search bar
- Click "Enable" to enable the Google Calendar API for your project
- Click "Create credentials" and follow the prompts
- Download the credentials.json file and place it in the google-calendar-export directory

4. If you want to use event summarization, create an .env file in the google-calendar-export directory containing your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Export Calendar Events

python calendar-export.py [-d DAYS] [-m {json,csv}] [-f FILE | -o]

- -d, --days: Number of days to look back (default: 7)
- -m, --mode: Output mode: json or csv (default: csv)
- -f, --file: Output file name (mutually exclusive with -o)
- -o, --output: Print output to the screen (mutually exclusive with -f)

### Summarize Events

`python summarize_events.py INPUT_FILE [-i {json,csv}] [-o OUTPUT_FILE] [-m {json}] [-v] [--summarize_all]`

- INPUT_FILE: Input file name with exported calendar events
- -i, --input_mode: Input file mode: json or csv (default: csv)
- -o, --output_file: Output file name for summarized calendar events (default: summarized_events.json)
- -m, --output_mode: Output mode: json (default: json)
- -v, --verbose: Enable verbose output
- --summarize_all: Summarize all events and print the result

## Examples

### Export Calendar Events

Export the last 7 days of events in CSV format (default) to a file:

`python calendar-export.py`

Export the last 14 days of events in JSON format to a file:

`python calendar-export.py -d 14 -m json`

Print the last 7 days of events in CSV format to the screen:

`python calendar-export.py -o`

Print the last 14 days of events in JSON format to the screen:

`python calendar-export.py -d 14 -m json -o`

### Summarize Events

Summarize events from a CSV file and output the results to a JSON file:

`python summarize_events.py calendar_events_last_5_days.csv -i csv -o summarized_events.json`

Summarize events from a JSON file, output the results to a JSON file, and enable verbose output:

`python summarize_events.py calendar_events_last_5_days.json -i json -o summarized_events.json -v`

Summarize all events from a CSV file and print the results:

`python summarize_events.py calendar_events_last_5_days.csv -i csv --summarize_all`
