import boto3
import intents
import json
import os
import re
import urlparse


NO_RESPONSE = {
    'statusCode': '200',
    'headers': {
        'Content-Type': 'plain/text',
    },
    'body': '',
}


def lambda_handler(event, context):
    print(json.dumps(event))
    data = urlparse.parse_qs(event['body'])

    if data.get('bot_id', [''])[0] != '':
        return NO_RESPONSE

    lex = boto3.client('lex-runtime')
    stack_name = os.environ['STACK_NAME']
    bot_name = ''.join([x[0].capitalize()+x[1:] for x in re.split('[^a-zA-Z]', stack_name)])

    response = lex.post_text(
        botName=bot_name,
        botAlias='$LATEST',
        userId=data['user_id'][0] + ':' + data['channel_id'][0],
        inputText=data['text'][0],
    )
    print(json.dumps(response))

    if response['dialogState'] in ['ElicitIntent', 'Failed'] and data.get('trigger_word', [''])[0] == '':
        return NO_RESPONSE

    message = {
        'text': response['message'],
    } if 'message' in response else None

    if response['dialogState'] == 'ReadyForFulfillment':
        intent = None
        if response['intentName'].startswith(bot_name+'_'):
            intent = intents.all().get(response['intentName'][len(bot_name)+1:])
        if intent is None:
            message = {
                'text': 'Something went wrong. Unknown intent: '+response['intentName'],
            }
        else:
            message = intent.fulfill(response['slots'])

    if message is not None:
        return {
            'statusCode': '200',
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps(message),
        }
    else:
        return NO_RESPONSE
