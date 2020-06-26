import json
import boto3
import os

ses = boto3.client('sesv2')

SENDER_ADDRESS = os.environ["SENDER_ADDRESS"]
TO_ADDRESS = os.environ["TO_ADDRESS"]

def send_email(record):
    body = "Received a new bad translation report on curl-to-ps.sebastiancarreira.com\n"
    body+= "Mode: " + ("Curl to Powerhsell" if record["dynamodb"]["NewImage"]["mode"]["S"] == "ctp" else "Powershell to Curl") + "\n"
    body+= "Original code: " + record["dynamodb"]["NewImage"]["original"]["S"] + "\n"
    body+= "Translated code: " + record["dynamodb"]["NewImage"]["translated"]["S"] + "\n"
    body+= "Commentary: "+ record["dynamodb"]["NewImage"]["report"]["S"] + "\n"
    print(body)
    response = ses.send_email(
        FromEmailAddress=SENDER_ADDRESS,
        Destination={
            'ToAddresses': [
                TO_ADDRESS
            ]
        },
        Content={
            'Simple': {
                'Subject': {
                    'Data': 'Received a bad translation report con curl-to-ps.sebastiancarreira.com'
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                }
            }
        }
    )
    print(response)




def lambda_handler(event, context):
    for record in event["Records"]:
        send_email(record)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
