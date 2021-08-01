import re

def save_message_id(messages, target_list):
    for item in messages['messages']:
        target_list.append(item['id'])

def save_full_message(raw_messages, target_list):

    def get_value_from_email_header(val: str):

        headers = raw_messages['payload']['headers']

        for item in headers:
            if item['name'] == val:
                return item['value']

    target_list.append({
        'id': raw_messages['id'],
        'from': get_value_from_email_header('From'),
        'subject': get_value_from_email_header('Subject')
    })