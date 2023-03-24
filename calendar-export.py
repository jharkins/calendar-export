import os
import json
import csv
import datetime
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def check_credentials_file(file_path):
    """
    Check if the credentials file exists at the given file path.
    If not, print an error message and exit the script.

    :param file_path: str, path to the credentials file
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Please download your credentials file from the Google API Console and place it in the script's directory.")
        exit(1)


def get_credentials():
    """
    Obtain and return valid Google API credentials.
    If the token file exists and the credentials are valid, use them.
    If the token file exists but the credentials are expired, refresh them.
    If the token file doesn't exist or the credentials are invalid, prompt the user to authenticate.

    :return: google.oauth2.credentials.Credentials object
    """
    creds = None
    token_file = 'token.json'
    credentials_file = 'credentials.json'
    check_credentials_file(credentials_file)

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())  # Add the required Request object here
        else:
            scopes = ['https://www.googleapis.com/auth/calendar.readonly']
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return creds


def export_calendar(num_days=7, output_mode='csv', output_file=None, output_screen=False):
    """
    Export Google Calendar events for the last num_days in the specified output_mode (CSV or JSON).
    If output_file is provided, save the events to the file.
    If output_screen is True, print the events to the screen.
    If both output_file and output_screen are not provided or False, save the events to a default file.

    :param num_days: int, number of days to look back (default: 7)
    :param output_mode: str, output format ('csv' or 'json', default: 'csv')
    :param output_file: str, output file name (default: None)
    :param output_screen: bool, whether to print the output to the screen (default: False)
    """

    # Access Google Calendar API
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # Get the calendar events for the last num_days, including today
    now = datetime.datetime.utcnow()
    start_date = now - datetime.timedelta(days=num_days - 1)

    events_result = service.events().list(calendarId='primary', timeMin=start_date.isoformat(
    ) + 'Z', timeMax=now.isoformat() + 'Z', singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if output_file is None and not output_screen:
        output_file = f'calendar_events_last_{num_days}_days.{output_mode}'

    if output_file and os.path.exists(output_file):
        overwrite = input(
            f'File "{output_file}" already exists. Overwrite? (y/n): ')
        if overwrite.lower() != 'y':
            print('Operation canceled.')
            return

    # Export events to CSV
    if output_mode == 'csv':
        csv_lines = [['Start Time', 'End Time',
                      'Summary', 'Location', 'Description']]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', '')
            location = event.get('location', '')
            description = event.get('description', '')
            csv_lines.append([start, end, summary, location, description])

        if output_screen:
            for line in csv_lines:
                print(', '.join(line))
        else:
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_lines)

    # Export events to JSON
    elif output_mode == 'json':
        if output_screen:
            print(json.dumps(events, indent=2))
        else:
            with open(output_file, 'w') as f:
                json.dump(events, f, indent=2)

    if not output_screen:
        print(
            f'Calendar events for the last {num_days} days exported to {output_file}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Google Calendar events for the last N days")
    parser.add_argument("-d", "--days", type=int, default=7,
                        help="Number of days to look back (default: 7)")
    parser.add_argument("-m", "--mode", choices=['json', 'csv'],
                        default='csv', help="Output mode: json or csv (default: csv)")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-f", "--file", type=str, help="Output file name")
    output_group.add_argument(
        "-o", "--output", action="store_true", help="Print output to the screen")
    args = parser.parse_args()

    export_calendar(args.days, args.mode, args.file, args.output)
