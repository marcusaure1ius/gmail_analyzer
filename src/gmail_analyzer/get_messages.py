import os.path
import csv

from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from help_functions import save_message_id
from help_functions import save_full_message

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../config/token.json'):
        creds = Credentials.from_authorized_user_file('../config/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../config/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    # results = service.users().labels().list(userId='me').execute()
    # labels = results.get('labels', [])

    get_profile = service.users().getProfile(userId='me').execute()

    total_messages = get_profile['messagesTotal']
    total_pages = total_messages // 100 + 1

    first_query_flag = True

    messages_id_list = []
    messages_full_list = []

    get_messages_by_page2 = service.users().messages().list(userId='me', maxResults=100,
                                                            pageToken='08702727377293148769').execute()
    print(get_messages_by_page2)

    for i in range(total_pages):

        if first_query_flag:
            get_messages = service.users().messages().list(userId='me', maxResults=100).execute()
            next_page_token = get_messages['nextPageToken']
            save_message_id(get_messages, messages_id_list)
        else:
            get_messages_by_page = service.users().messages().list(userId='me', maxResults=100,
                                                                   pageToken=next_page_token).execute()
            try:
                next_page_token = get_messages_by_page['nextPageToken']
            except:
                pass
            save_message_id(get_messages_by_page, messages_id_list)

        first_query_flag = False

    start = datetime.now()
    counter = 0

    for item in messages_id_list:
        print(item)
        get_message_by_id = service.users().messages().get(userId='me', id=item, format='full').execute()
        save_full_message(get_message_by_id, messages_full_list)

        counter += 1

        end = datetime.now()
        total = end - start
        avg_time = total / (counter + 1)
        print(f'Текущий номер письма - {counter} Текущее время обработки - {total} Среднее время обработки 1 запроса - {avg_time}', get_message_by_id)
        print('---------------------------------------------------------------------------------')

    keys = messages_full_list[0].keys()

    a_file = open('../data/gmail_stats.csv', 'w', encoding='utf-8')
    dict_writer = csv.DictWriter(a_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(messages_full_list)
    a_file.close()


main()
