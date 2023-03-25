import os
import json
import csv
import argparse
import openai
import sys
import aiohttp
from tqdm import tqdm
import asyncio
from dotenv import load_dotenv
from pprint import pprint
from typing import List

# Load the OpenAI API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class SummarizationError(Exception):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Summarize Google Calendar events for the last N days"
    )
    parser.add_argument(
        "input_file",
        help="Input file containing calendar events",
    )
    parser.add_argument(
        "-i", "--input_mode",
        help="Input file format (csv or json)",
        choices=["csv", "json"],
        default="csv",
    )
    parser.add_argument(
        "output_file",
        help="Output file to write summarized events",
    )
    parser.add_argument(
        "-o", "--output_mode",
        help="Output file format (csv or json)",
        choices=["csv", "json"],
        default="json",
    )
    parser.add_argument(
        "-n", "--num-days",
        help="Number of days to summarize (default: 7)",
        type=int,
        default=7,
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Print additional information",
        action="store_true",
    )
    parser.add_argument(
        "--summarize_all",
        help="Generate an executive summary of all events",
        action="store_true",
    )
    return parser.parse_args()


def read_calendar_events(input_file, input_mode):
    events = []

    if input_mode == "csv":
        with open(input_file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                events.append(row)
    elif input_mode == "json":
        with open(input_file) as jsonfile:
            events = json.load(jsonfile)
            if not isinstance(events, list):
                raise ValueError("Input file must be a list of JSON objects")
    else:
        raise ValueError("Invalid input mode")

    return events


async def generate_summary(event):
    input_messages = [
        {
            "role": "assistant",
            "content": "Please summarize the following event description and if possible include dates/times:",
        },
        {"role": "user", "content": json.dumps(event)},
    ]

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": input_messages,
            },
            headers={"Authorization": f"Bearer {openai.api_key}"},
        ) as response:
            completion = await response.json()
            if "choices" not in completion:
                print("Error with API response:", completion)
                raise SummarizationError("Failed to generate summary")
            summary = completion["choices"][0]["message"]["content"].strip()
    return summary


def generate_summary_for_all_events(summarized_events: List[str]) -> str:
    se = [{"role": "user", "content": json.dumps(
        s)} for i, s in enumerate(summarized_events)]

    messages = [
        {"role": "assistant",
         "content": "Please provide an executive summary of the following summarized events - make sure to keep it fairly high level:"},
    ]+se

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        if "choices" in completion:
            summary = completion["choices"][0]['message']['content'].strip()
            return summary
    except openai.error.InvalidRequestError:
        if len(summarized_events) == 1:
            raise ValueError("Failed to summarize event.")
        else:
            midpoint = len(summarized_events) // 2
            first_half = summarized_events[:midpoint]
            second_half = summarized_events[midpoint:]
            return generate_summary_for_all_events(first_half) + generate_summary_for_all_events(second_half)


async def summarize_events(events, verbose=False):
    summarized_events = []

    async def process_event(event):
        try:
            summary = await generate_summary(event)
            summarized_events.append(summary)
        except Exception as e:
            log_event(
                f"Error generating summary for event '{event['Summary']}': {e}"
            )
            pprint(e)
            sys.exit(1)

    # Process events with tqdm progress bar
    with tqdm(
        total=len(events),
        desc="Summarizing events",
        unit="event",
    ) as pbar:
        for coro in asyncio.as_completed([process_event(event) for event in events]):
            await coro
            pbar.update(1)

    return summarized_events


def log_event(message, verbose=False):
    if verbose:
        print(message)


if __name__ == "__main__":
    args = parse_arguments()

    verbose = args.verbose

    try:
        if not os.path.isfile(args.input_file):
            log_event(
                f"Error: Input file {args.input_file} not found.", verbose)
            sys.exit(1)

        if args.input_mode == "csv" and not args.input_file.endswith(".csv"):
            log_event("Error: Input file must be a CSV file.", verbose)
            sys.exit(1)

        if args.input_mode == "json" and not args.input_file.endswith(".json"):
            log_event("Error: Input file must be a JSON file.", verbose)
            sys.exit(1)

        if args.output_mode == "csv" and not args.output_file.endswith(".csv"):
            log_event("Error: Output file must be a CSV file.", verbose)
            sys.exit(1)

        if args.output_mode == "json" and not args.output_file.endswith(".json"):
            log_event("Error: Output file must be a JSON file.", verbose)
            sys.exit(1)

        events = read_calendar_events(args.input_file, args.input_mode)

        # summarized_events = summarize_events(events)
        summarized_events = asyncio.run(summarize_events(events))

        with open(args.output_file, "w") as jsonfile:
            json.dump(summarized_events, jsonfile, indent=2)

        log_event(f"Summarized events saved to {args.output_file}")

        if args.summarize_all:
            summarized_all = generate_summary_for_all_events(summarized_events)
            print("\nSummary of all events:")
            print(summarized_all)
            print("\n")

    except SummarizationError as e:
        log_event(f"Error: {e}", verbose)
        sys.exit(1)
