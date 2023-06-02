#这个lambda可以实现更新db中指定id图片的tags，可以用于tags的增删改查
# This lambda can be implemented to update the tags of the specified id images in the db,
# which can be used to add, delete, alter and remove tags
import json
import boto3
from decimal import Decimal


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
#DynamoDB 使用 Decimal 类型来存储数字，但是 Python 的 json 模块无法直接序列化此类型。
#要解决此问题，您可以在序列化 JSON 之前将 Decimal 对象转换为可以序列化的类型，例如 float 或 int。
# 您可以通过定义一个自定义函数来实现这一点，该函数将 Decimal 对象转换为 float，然后在调用 json.dumps() 时将其作为 default 参数传递

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('assignment2tags')

    print('Lambda function started')
    print(f'Event object: {event}')

    data = json.loads(event['body'])
    item_id = data['id']
    tags = data['tags']
    # item_id = event['id']
    # tags = event['tags']
    print("成功开始修改", id, tags)
    response1 = table.update_item(
        Key={
            'id': item_id
        },
        UpdateExpression='SET tags = :tags',
        ExpressionAttributeValues={
            ':tags': tags
        }
    )
    # 将更新后的条目返回
    updated_item = table.get_item(Key={'id': item_id})
    print("updated_item:", updated_item)

    return {
        'statusCode': 200,
        'headers': {

            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': json.dumps(updated_item, default=decimal_default)
    }

    # ,'Access-Control-Allow-Origin': "*"