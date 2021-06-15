import pyinputplus as pip

# notion imports
import requests
import csv
from datetime import datetime
import pytz

# gcal imports
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

MARKER = "Created by NotionGCalScript"


def notion_request(data, tasks, classes, token):

    notion_data = {
        "parent": {
            "database_id": f"{tasks}"
        },
        "properties": {
            "Name": {
                "title": [{
                    "text": {
                        "content": f"{data[1]}"
                    }
                }]
            },
            "Category": {
                "select": {
                    "name": "School"
                }
            },
            "Type": {
                "select": {
                    "name": f"{data[2]}"
                }
            },
            "Notes": {
                "rich_text": [{
                    "text": {
                        "content": f"{MARKER}"
                    }
                }]
            }
        }
    }
    notion_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-05-13"
    }

    if data[3] != '':
        date = datetime.strptime(data[3], '%m/%d/%y %H:%M')
        date_converted = pytz.timezone("US/Eastern").localize(date).isoformat()
        notion_data["properties"]["Date Available"] = {
                "date": {
                    "start": f"{date_converted}"
                }
            }
    if data[4] != '':
        date = datetime.strptime(data[4], '%m/%d/%y %H:%M')
        date_converted = pytz.timezone("US/Eastern").localize(date).isoformat()
        notion_data["properties"]["Due Date"] = {
                "date": {
                    "start": f"{date_converted}"
                }
            }
    if data[5] != '' and data[6] != '':
        date_start = datetime.strptime(data[5], '%m/%d/%y %H:%M')
        date_start_converted = pytz.timezone("US/Eastern").localize(date_start).isoformat()
        date_end = datetime.strptime(data[6], '%m/%d/%y %H:%M')
        date_end_converted = pytz.timezone("US/Eastern").localize(date_end).isoformat()
        notion_data["properties"]["Due Date"] = {
            "date": {
                "start": f"{date_start_converted}",
                "end": f"{date_end_converted}"
            }
        }
    class_name = data[0]

    class_filter = {
        "filter": {
            "property": "Name",
            "title": {
                "contains": f"{class_name}"
            }
        }
    }

    get_class_page_endpoint = f"https://api.notion.com/v1/databases/{classes}/query"
    get_class_page_response = requests.post(get_class_page_endpoint, json=class_filter, headers=notion_headers)
    class_id = get_class_page_response.json()['results'][0]['id']

    notion_data["properties"]["Class"] = {
        "relation": [{
            "id": f"{class_id}"
        }]
    }

    submit_task_endpoint = "https://api.notion.com/v1/pages"
    submit_task_response = requests.post(submit_task_endpoint, json=notion_data, headers=notion_headers)
    print(submit_task_response.text)


def gcal_request(data):
    scopes = ['https://www.googleapis.com/auth/calendar']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': f'{data[0]} {data[1]}',
        'description': f'{MARKER}'
    }

    if data[4] != '':
        date = datetime.strptime(data[4], '%m/%d/%y %H:%M')
        date_converted = date.isoformat()
        event['start'] = {
            'dateTime': f'{date_converted}',
            'timeZone': 'America/New_York'
        }
        event['end'] = {
            'dateTime': f'{date_converted}',
            'timeZone': 'America/New_York'
        }
    if data[5] != '' and data[6] != '':
        date_start = datetime.strptime(data[5], '%m/%d/%y %H:%M')
        date_start_converted = date_start.isoformat()
        date_end = datetime.strptime(data[6], '%m/%d/%y %H:%M')
        date_end_converted = date_end.isoformat()
        event['start'] = {
            'dateTime': f'{date_start_converted}',
            'timeZone': 'America/New_York'
        }
        event['end'] = {
            'dateTime': f'{date_end_converted}',
            'timeZone': 'America/New_York'
        }

    calendar_id = 'ei26d4fpvfjhkdiok2cvgqrfcs@group.calendar.google.com'

    event = service.events().insert(calendarId=calendar_id, body=event).execute()


def main():
    with open("database_id.txt") as f:
        tasks_id = f.readline().strip()
        classes_id = f.readline().strip()
    with open("notion_token.txt") as f:
        notion_token = f.readline()

    input_file = pip.inputFilename(prompt="Enter input csvfile name: ")

    with open(input_file) as f:
        reader = csv.reader(f)
        print(next(reader))
        for row in reader:
            print(row)
            notion_request(row, tasks_id, classes_id, notion_token)
            gcal_request(row)


if __name__ == '__main__':
    main()
