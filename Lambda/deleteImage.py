import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr


def lambda_handler(event, context):
    print(event)
    if event['httpMethod'] == 'DELETE':
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('assignment2tags')
        s3 = boto3.resource('s3')

        try:
            url = event['queryStringParameters']['s3-url']
            response = table.scan(
                FilterExpression=Attr('s3-url').eq(url)
            )
            if response['Count'] == 0:
                print('No matching image found.')
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST, DELETE',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'message': 'No matching image found.'})
                }
            else:
                id = response['Items'][0]['id']
                responseDB = table.delete_item(Key={'id': id})

            object_key = url.split('/')[-1]
            responseS3 = s3.Object('bucket-for-images-5225', object_key).delete()
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, DELETE',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Successfully deleted.'})
            }
        except ClientError as e:
            print(e)
            return "error"
    else:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, DELETE',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'No matching image found.'})
        }

