import json

import boto3

# Function for finding images URL by tags

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
TABLE_NAME = 'assignment2tags'

def lambda_handler(event, context):
    # TODO implement
    httpMethod = event.get('httpMethod')
    print(httpMethod)
    parameters = event.get('queryStringParameters')
    print(parameters)
    d_set = set((item['tag'], item['count']) for item in parameters['tags'])
    print(d_set)
    
    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response.get('Items')
    urls = []
    for i in items:
        item_tags = i.get('tags').get('L')
        tuples = [(item['L'][0]['S'], int(item['L'][1]['N'])) for item in item_tags]
        s = set(tuples)
        if d_set.issubset(s):
            url = i.get('s3-url').get('S')
            urls.append(url)
    response_image = {"links": urls}

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*"
        },
        'body': json.dumps(response_image)
    }
