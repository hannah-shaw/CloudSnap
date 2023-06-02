import json
import boto3

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
TABLE_NAME = 'assignment2tags'


def lambda_handler(event, context):
    # TODO implement
    print(f'Event object: {event}')
    # data = json.loads(event['body'])

    # parameters = event.get('parameters')
    # Api use the following code
    parameters = json.loads(json.dumps(event['parameters']))
    # Test use the following code
    # parameters = json.loads(event['parameters'])
    print("parameters", parameters)

    response = {"message": "error:No tags in parameters."}
    tags = parameters.get('tags')
    if tags:
        d_set = set((item['tag'], item['count']) for item in parameters['tags'])
        print(d_set)
    else:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            },
            'body': json.dumps(response)
        }

    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response.get('Items')
    urls = []
    for i in items:
        item_tags = i.get('tags').get('L')
        tuples = [(item['L'][0]['S'], int(item['L'][1]['N'])) for item in item_tags]
        s = set(tuples)

        d_tags = set(tag for tag, count in d_set)
        s_tags = set(tag for tag, count in s)
        if d_tags.issubset(s_tags):
            for tag, count in d_set:
                for s_tag, s_count in s:
                    if s_tag == tag and s_count >= count:
                        url = i.get('s3-url').get('S')
                        urls.append(url)
    response_image = {"links": urls}

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': json.dumps(response_image)
    }
# 'Access-Control-Allow-Origin': '*',
# 'Access-Control-Allow-Origin': "*",