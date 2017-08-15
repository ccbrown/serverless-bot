import boto3
import intents
import json
import re
import requests
import sys
import time
import traceback

from botocore.exceptions import ClientError


def put_cloudformation_response(event, status, data={}):
    response = {
        'Status': status,
        'PhysicalResourceId': event['ResourceProperties']['StackName'] + '-' + event['LogicalResourceId'] + ('-FAILED' if status == 'FAILED' else ''),
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': data,
    }
    body = json.dumps(response)
    print(body)
    requests.put(event['ResponseURL'], data=body)


def delete_intents(lex, name_prefix=''):
    for name in intents.all().keys():
        for i in range(0, 30):
            try:
                lex.delete_intent(name=name_prefix+name)
                break
            except ClientError as e:
                if e.response['Error']['Code'] != 'ConflictException':
                    raise e
            time.sleep(1)


def put_intents(lex, name_prefix=''):
    did_put = False
    for name, intent in intents.all().items():
        params = intent.definition()
        params['name'] = name_prefix+name
        params['fulfillmentActivity'] = {
            'type': 'ReturnIntent',
        }
        try:
            latest = lex.get_intent(
                name=params['name'],
                version='$LATEST',
            )
            if all([latest.get(k) == v for k, v in params.items()]):
                print('skipping {} intent (up-to-date)'.format(params['name']))
                continue
            params['checksum'] = latest['checksum']
        except ClientError as e:
            if e.response['Error']['Code'] != 'NotFoundException':
                raise e
        print('putting {} intent'.format(params['name']))
        lex.put_intent(**params)
        did_put = True
    return did_put


def delete_bot(lex, name):
    lex.delete_bot(name=name)
    delete_intents(lex, name_prefix=name+'_')


def put_bot(lex, name):
    did_put_intents = put_intents(lex, name_prefix=name+'_')

    params = {
        'name': name,
        'intents': [],
        'locale': 'en-US',
        'childDirected': False,
        'clarificationPrompt': {
            'messages': [{
                'contentType': 'PlainText',
                'content': 'Uh... what?',
            }],
            'maxAttempts': 3,
        },
        'abortStatement': {
            'messages': [{
                'contentType': 'PlainText',
                'content': 'Maybe you should ask Siri or Cortana.',
            }],
        },
    }

    for intent_name, intent in intents.all().items():
        params['intents'].append({
            'intentName': name+'_'+intent_name,
            'intentVersion': '$LATEST',
        })

    try:
        latest = lex.get_bot(
            name=params['name'],
            versionOrAlias='$LATEST',
        )
        if not did_put_intents and all([latest.get(k) == v for k, v in params.items()]):
            print('skipping {} bot (up-to-date)'.format(params['name']))
            return
        params['checksum'] = latest['checksum']
    except ClientError as e:
        if e.response['Error']['Code'] != 'NotFoundException':
            raise e
    print('putting {} bot'.format(params['name']))
    lex.put_bot(**params)


def lambda_handler(event, context):
    try:
        print(json.dumps(event))
        lex = boto3.client('lex-models')
        stack_name = event['ResourceProperties']['StackName']
        bot_name = ''.join([x[0].capitalize()+x[1:] for x in re.split('[^a-zA-Z]', stack_name)])
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            put_bot(lex, bot_name)
        elif event['RequestType'] == 'Delete':
            delete_bot(lex, bot_name)
        put_cloudformation_response(event, 'SUCCESS', {
            'Name': bot_name,
        })
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        put_cloudformation_response(event, 'FAILED')
