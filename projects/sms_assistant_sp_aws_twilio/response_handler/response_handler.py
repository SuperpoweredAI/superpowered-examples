# twilio documentation about webhooks: https://www.twilio.com/docs/messaging/guides/webhook-request
import base64
import boto3
import json
import os
import requests
from urllib.parse import parse_qs

from twilio.rest import Client
from twilio.request_validator import RequestValidator


# GET CREDENTIALS FROM SSM
# THIS STEP ASSUMES THAT YOU HAVE STORED YOUR CREDENTIALS IN SSM
# twilio
ssm = boto3.client('ssm')
TWILIO_ACCOUNT_SID = ssm.get_parameter(
    Name=os.environ['TWILIO_ACCOUNT_SID_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']
TWILIO_AUTH_TOKEN = ssm.get_parameter(
    Name=os.environ['TWILIO_AUTH_TOKEN_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# superpowered
SP_API_KEY_ID = ssm.get_parameter(
    Name=os.environ['SP_API_KEY_ID_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']
SP_API_KEY_SECRET = ssm.get_parameter(
    Name=os.environ['SP_API_KEY_SECRET_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']


SP_BASE_URL = 'https://api.superpowered.ai/v1'
SP_AUTH = (SP_API_KEY_ID, SP_API_KEY_SECRET)


CHAT_SYSTEM_MESSAGE = """\
You are are responding in an SMS message so please keep your responses short and to the point.

If you do not have the information you need to respond to a user, please ask for follow up questions."""


def create_chat_thread(phone_number: str) -> str:
    # create the chat thread with some defaults and set supp_id to the phone number
    # this will allow us to get the chat thread by phone number
    payload = {
        'supp_id': phone_number,
        'model': 'gpt-3.5-turbo',
        'system_message': CHAT_SYSTEM_MESSAGE,
        'use_web_search': True,
        'response_length': 'short',
    }
    resp = requests.post(
        url=f'{SP_BASE_URL}/chat/threads',
        json=payload,
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error creating superpowered chat thread: {resp.text}')

    return resp.json()['id']


def get_chat_thread_by_phone_number(phone_number: str) -> str:
    # NOTE: THIS ASSUMES THERE IS ONLY ONE THREAD PER PHONE NUMBER
    resp = requests.get(
        url=f'{SP_BASE_URL}/chat/threads',
        params={'supp_id': phone_number},
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error getting superpowered chat thread by phone number: {resp.text}')

    return resp.json()['chat_threads'][0]['id'] if resp.json()['chat_threads'] else None


def get_chat_response(thread_id: str, user_input: str) -> str:
    # get the response from the chat thread
    # this will first create a chat job and then wait for it to complete
    payload = {
        'input': user_input,
        'async': True
    }
    resp = requests.post(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}/get_response',
        json=payload,
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error getting superpowered chat response: {resp.text}')

    while resp.json()['status'] not in ['COMPLETE', 'FAILED']:
        resp = requests.get(
            url=resp.json()['status_url'],
            auth=SP_AUTH
        )
        if not resp.ok:
            raise Exception(f'Error getting superpowered chat response: {resp.text}')

    return resp.json()['response']


def organize_chat_response(response: str) -> str:
    web_search_references = ('REFERENCES\n' + '\n'.join(response['interaction']['web_search_results'][i] for i in response['interaction']['web_search_references'])) if response['interaction']['web_search_references'] else ''
    return response['interaction']['model_response']['content'] + '\n\n' + web_search_references


def send_twilio_response(to: str, from_: str, body: str):
    return TWILIO_CLIENT.messages.create(
        to=to,
        from_=from_,
        body=body
    )


def lambda_handler(event, context):
    ############################
    # WEBHOOK VALIDATION
    ############################
    validator = RequestValidator(TWILIO_AUTH_TOKEN)

    # parse the event body but make sure to keep empty values for webhook validation
    body = base64.b64decode(event['body']).decode('utf-8')
    twilio_webhook = parse_qs(body, keep_blank_values=True)
    twilio_webhook = {k: v[0] for k, v in twilio_webhook.items()}

    # webhook url is the url that twilio will send the webhook to (i.e. the url of this lambda function)
    url = f"https://{event['headers']['host']}{event['rawPath']}"

    if not validator.validate(uri=url, params=twilio_webhook, signature=event['headers'].get('x-twilio-signature')):
        raise Exception('Not authorized to access this endpoint.')
    
    ############################
    # WEBHOOK HANDLING
    ############################
    # get the phone number from the webhook
    user_phone_number = twilio_webhook['From']
    twilio_phone_number = twilio_webhook['To']

    ############################
    # GET OR CREATE CHAT THREAD
    ############################
    thread_id = get_chat_thread_by_phone_number(user_phone_number)
    if not thread_id:
        # create a chat thread for this user
        thread_id = create_chat_thread(user_phone_number)
    
    ############################
    # GET API RESPONSE FROM SUPERPOWERED API
    ############################
    # get the response from the model
    model_response = get_chat_response(
        thread_id=thread_id, 
        user_input=twilio_webhook['Body']
    )

    user_response = organize_chat_response(model_response)

    # send the response back to the user phone number
    resp = send_twilio_response(
        to=user_phone_number,
        from_=twilio_phone_number,
        body=user_response
    )

    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
