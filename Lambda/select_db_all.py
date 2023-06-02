#获取显示所有db条目
#在template中的search_by_id.html中点击获取所有检测数据，显示所有db数据
import json
import boto3

from decimal import Decimal


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def getAllData(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("assignment2tags")
    response = table.scan()
    result = []
    items = response['Items']
    for i in items:
        result.append(i)
    return {"data": result}


def lambda_handler(event, context):
    # TODO implement
    res_dict = {}
    res_dict["info"] = "the jie"

    return {
        'statusCode': 200,
        'headers': {

            'Access-Control-Allow-Origin': "*",
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': json.dumps(getAllData(), default=decimal_default)
    }
