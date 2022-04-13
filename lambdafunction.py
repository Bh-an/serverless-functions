from __future__ import print_function
from botocore.exceptions import ClientError
import json
import boto3
print('Loading function')

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + message)

    name, email, token = get_email_details(message)

    print (name, email, token)

    if checktable(email):
        print("Email already sent")
    else:
        send_email(name, email, token)
        update_email(email)


def get_email_details(csvmessage):

    valuelist = csvmessage.split(",")
    name = valuelist[0]
    emailadd = valuelist[1]
    token = valuelist[2]


    return name, emailadd, token

def checktable(emailadd):

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    email_table = dynamodb.Table('sent-emails')
    # table = dynamodb.Table('')

    response = email_table.get_item(
        Key={'emailadd': emailadd})
    if 'Item' in response:
        return True
    else:
        return False

def update_email(emailadd):

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    email_table = dynamodb.Table('sent-emails')
    response = email_table.put_item(
        Item={'emailadd': emailadd})

    # try:
    #     response = table.get_item(Key={'emailadd': str(emailadd)})
    # except boto.dynamodb.exceptions.DynamoDBKeyNotFoundError:
    #     response = None
    # return response

def send_email(recipientname, recipientemailid, authtoken):

    SENDER = "no-reply@prod.applicationbhan.me"

    RECIPIENT = recipientemailid

    authlink = "http://prod.applicationbhan.me/verifyemail?email=" + recipientemailid + "&token=" + authtoken

    print(authlink)


    DESTINATION = {
        'ToAddresses': [
            RECIPIENT,
        ]
    }

    AWS_REGION = "us-east-1"

    SUBJECT = "Verification Email"

    BODY_TEXT = ("Email verification for new user\r\n"
                 "Details:\r\n"
                 "\n"
                 "Name: " + recipientname + "\n"
                 "\n"
                 "Verifying email id: " + recipientemailid + "\r\n"
                 "\r\n"
                 "Use the link provided below to verify yourself:\r\n"
                 "Verify: " + authlink
                 )

    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination=DESTINATION,
            Message={
                'Body': {
                    # 'Html': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_,
                    # },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
         )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:")
        print(response['MessageId'])
        print(RECIPIENT)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }