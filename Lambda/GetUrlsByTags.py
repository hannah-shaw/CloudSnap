import json
import boto3

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
TABLE_NAME = 'assignment2tags'


def lambda_handler(event, context):
    # TODO implement
    print(f'Event object: {event}')

    # Api use the following code
    parameters = json.loads(json.dumps(event['parameters']))
    # Event json test use the following code
    # parameters = json.loads(event['parameters'])
    print("parameters", parameters)

    # If tags exist, convert them to set type
    errorResponse = {"message": "error:No tags in parameters."}
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
            'body': json.dumps(errorResponse)
        }

    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response.get('Items')
    urls = []
    # print(items)
    for i in items:
        item_tags = i.get('tags').get('L')
        # Convert labels to tuple lists
        # print(i)
        tuples = [(item['L'][0]['S'], int(item['L'][1]['N'])) for item in item_tags]
        s = set(tuples)
        d_tags = set(tag for tag, count in d_set)
        s_tags = set(tag for tag, count in s)
        d_num = len(d_tags)
        # If the label in d_set exists in s, check whether the number of each label meets the requirements.
        if d_tags.issubset(s_tags):
            for tag, count in d_set:
                for s_tag, s_count in s:
                    # If the quantity meets the requirements, add the URL of this item to the urls list
                    if s_tag == tag and s_count >= count:
                        d_num = d_num - 1
            if (d_num == 0):
                url = i.get('s3-url').get('S')
                urls.append(url)
    response_image = {"links": urls}

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': response_image
    }
# 'Access-Control-Allow-Origin': '*',
# 'Access-Control-Allow-Origin': "*",