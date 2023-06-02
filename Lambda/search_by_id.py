#根据id查询db中的条目
#在search_by_id.html中输入图片id，即可在db中查询数据并返回
#在search_by_id.html中获取所有检测数据，显示所有db数据
import json
import boto3
from decimal import Decimal


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def getDataById(id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("assignment2tags")
    response = table.get_item(Key={'id': id})
    if 'Item' in response:
        return response['Item']
    else:
        return None


def lambda_handler(event, context):
    print('Lambda function started')
    print(f'Event object: {event}')

    data = json.loads(event['body'])
    print("czy data:", data)
    id = data['id']
    data = getDataById(id)
    if data:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            },
            'body': json.dumps(data, default=decimal_default)
        }
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            },
            'body': json.dumps({'error': f'No data found for id: {id}'})
        }