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
<SYSTEM INFORMATION>
Your name is {assistant_name}. If you are asked, you should say that this is your name, even if you think it's something else.
</SYSTEM INFORMATION>

<IMPORTANT FORMATTING>
Your response will be sent via SMS and it is very important that you keep answers as concise as possible.

Short answers are extremely important. Please keep this in mind no matter what.

Bullet points are encouraged when there are possible solutions but sometimes you might need to respond in multiple short sentences.

It is helpful to include newline breaks regularly to make the response easier to read on a small screen.
</IMPORTANT FORMATTING>
"""


def create_chat_thread(phone_number: str, web_search_timeframe_days: int = None, assistant_name: str = 'Alfred') -> str:
    # create the chat thread with some defaults and set supp_id to the phone number
    # this will allow us to get the chat thread by phone number
    payload = {
        'supp_id': phone_number,
        'title': assistant_name,
        'default_options': {
            'model': 'claude-3-haiku',
            'system_message': CHAT_SYSTEM_MESSAGE.format(assistant_name=assistant_name),
            'use_web_search': True,
            'response_length': 'short',
        }
    }
    if web_search_timeframe_days:
        payload['default_options']['web_search_config'] = {
            'timeframe_days': web_search_timeframe_days
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


def send_twilio_response(to: str, from_: str, body: str):
    return TWILIO_CLIENT.messages.create(
        to=to,
        from_=from_,
        body=body
    )


def get_help_message():
    return u"""\
Available commands:

/help | \U00002753 | \U00002754: get this help message

/clear | \U0000274C: reset the conversation settings (besides the assistant name)

/settings | \U00002699: display conversation settings

/timeframe N | \U0001F4C5 N: set the web search timeframe to the last N days

/name NAME: set the name of the assistant to NAME

/model MODEL: set the model of the assistant to MODEL. Must be one of `gpt-3.5-turbo`, `claude-3-haiku`, `mixtral`.

/temperature N | \U0001F525 N: set the temperature of the assistant to N. Must be a number between 0 and 1.
"""


def delete_chat_thread(thread_id: str):
    # reset the chat thread
    resp = requests.delete(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}',
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error resetting superpowered chat thread: {resp.text}')
    

def get_chat_thread(thread_id: str):
    resp = requests.get(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}',
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error getting superpowered chat thread settings: {resp.text}')

    return resp.json()


def update_chat_thread_web_search_timeframe(thread_id: str, timeframe_days: int):
    resp = requests.patch(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}',
        json={'default_options': {'web_search_config': {'timeframe_days': timeframe_days}}},
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error updating superpowered chat thread web search timeframe: {resp.text}')


def update_assistant_name(thread_id: str, name: str):
    resp = requests.patch(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}',
        json={'title': name, 'default_options': {'system_message': CHAT_SYSTEM_MESSAGE.format(assistant_name=name)}},
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error updating superpowered chat thread assistant name: {resp.text}')


def update_assistant_model(thread_id: str, model: str):
    resp = requests.patch(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}',
        json={'default_options': {'model': model}},
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error updating superpowered chat thread assistant name: {resp.text}')


def update_assistant_temperature(thread_id: str, temperature: float):
    resp = requests.patch(
        url=f'{SP_BASE_URL}/chat/threads/{thread_id}',
        json={'default_options': {'temperature': temperature}},
        auth=SP_AUTH
    )
    if not resp.ok:
        raise Exception(f'Error updating superpowered chat thread assistant name: {resp.text}')


def print_unicode_representation(text):
    for char in text:
        code_point = ord(char)
        # Using '\\U{:08X}' to ensure it works for all characters, including those outside BMP.
        unicode_string = '\\U{:08X}'.format(code_point)
        print(unicode_string)


def lambda_handler(event, context):
    ############################
    # WEBHOOK VALIDATION
    ############################
    validator = RequestValidator(TWILIO_AUTH_TOKEN)

    # parse the event body but make sure to keep empty values for webhook validation
    body = base64.b64decode(event['body']).decode('utf-8')
    twilio_webhook = parse_qs(body, keep_blank_values=True)
    twilio_webhook = {k: v[0] for k, v in twilio_webhook.items()}

    # validation url is the url that twilio will send the webhook to (i.e. the url of this lambda function)
    url = f"https://{event['headers']['host']}{event['rawPath']}"

    if not validator.validate(uri=url, params=twilio_webhook, signature=event['headers'].get('x-twilio-signature')):
        raise Exception('Not authorized to access this endpoint.')
    
    ############################⚙️
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
        # send an initial message to the user
        sms_response = f'Hello! You can view/adjust settings via keywords and emojis.\n\n'
        sms_response += get_help_message()
        send_twilio_response(
            to=user_phone_number,
            from_=twilio_phone_number,
            body=sms_response
        )

    ############################
    # DEPENDING ON POSSIBLE FIRST WORD,
    # DECIDE WHAT ACTION TO TAKE
    ############################
    sms_response = ''
    words = twilio_webhook['Body'].split(' ')
    first_word = u'{}'.format(words[0]).lower()
    # sometimes emojis are broken up into multiple characters
    # in the case of the gearbox / settings emoji, it's broken up into 2 characters
    first_char = first_word[0]

    # print(first_word)
    # print_unicode_representation(first_word)

    ### HELP
    if first_word in [u'/help', u'\U00002753', u'\U00002754']:
        # send help message
        sms_response = get_help_message()
    ### CLEAR
    elif first_word in [u'/clear', u'\U0000274C']:
        # reset the chat thread
        thread = get_chat_thread(thread_id)
        assistant_name = thread['title']
        if len(assistant_name) > 1:
            assistant_name = assistant_name[1]
        else:
            assistant_name = 'Alfred'
        delete_chat_thread(thread_id)
        thread_id = create_chat_thread(user_phone_number, assistant_name=assistant_name)
        sms_response = 'Conversation settings have been reset to defaults.'
    ### VIEW SETTINGS
    elif first_word == u'/settings' or first_char == u'\U00002699':
        thread = get_chat_thread(thread_id)
        chat_thread_defaults = thread['default_options']
        assistant_name = thread.get('title', 'Alfred')
        sms_response = f"**name**: {assistant_name}\n**model**: {chat_thread_defaults['model']}\n**web search timeframe**: {chat_thread_defaults['web_search_config']['timeframe_days'] if chat_thread_defaults['web_search_config'] else 'all time'}\n**temperature**: {round(chat_thread_defaults['temperature'], 2)}"
    ### SET TIMEFRAME DAYS
    elif first_word in [u'/timeframe', u'\U0001F4C5']:
        try:
            timeframe_days = int(words[1])
            update_chat_thread_web_search_timeframe(thread_id, timeframe_days)
            sms_response = f'Web search timeframe set to {timeframe_days} days.'
        except:
            sms_response = 'Invalid timeframe. Please use a number.'
    ### SET ASSISTANT NAME
    elif first_word in [u'/name']:
        try:
            assistant_name = words[1]
            update_assistant_name(thread_id, assistant_name)
            sms_response = f'Assistant name set to {assistant_name}.'
        except Exception as e:
            print(e)
            sms_response = 'Invalid input. Please specify the new name like "/name Alfred".'
    ### SET MODEL
    elif first_word in [u'/model']:
        try:
            model = words[1].lower()
            if model not in ['gpt-3.5-turbo', 'claude-3-haiku', 'mixtral']:
                sms_response = 'Invalid model. Must be one of "gpt-3.5-turbo", "claude-3-haiku", "mixtral".'
            else:
                update_assistant_model(thread_id, model)
                sms_response = f'Assistant model set to {model}.'
        except Exception as e:
            print(e)
            sms_response = 'Invalid model. Must be one of "gpt-3.5-turbo", "claude-3-haiku", "mixtral".'
    ### SET TEMPERATURE
    elif first_word in [u'/temperature', u'\U0001F525']:
        try:
            temperature = float(words[1])
            update_assistant_temperature(thread_id, temperature)
            sms_response = f'Assistant temperature set to {temperature}.'
        except Exception as e:
            print(e)
            sms_response = 'Invalid input. Please specify the new temperature like "/temperature 0.5".'
    ### SEND NORMAL SP RESPONSE
    else:
        ############################
        # GET API RESPONSE FROM SUPERPOWERED API
        ############################
        # get the response from the model
        model_response = get_chat_response(
            thread_id=thread_id, 
            user_input=twilio_webhook['Body']
        )
        sms_response = model_response['interaction']['model_response']['content']

    ############################
    # SEND RESPONSE BACK TO USER VIA TWILIO
    ############################
    send_twilio_response(
        to=user_phone_number,
        from_=twilio_phone_number,
        body=sms_response
    )

    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
