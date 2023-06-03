import json
import boto3
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('assignment2tags')
    print("测试2247")
    print('Lambda function started')
    print(f'Event object: {event}')
    
    #data = json.loads(event['body'])#aws上测试的时候用这行
    data = json.loads(json.loads(event['body'])['body'])  #使用浏览器html时候用这行
    print("data数据",data)
    print(data)
    url = data['url']
    type = data['type']
    tags = data['tags']
    
    # 根据给定的 url 值查找对应的 id 值
    response = table.scan(
        FilterExpression='#u = :url',
        ExpressionAttributeNames={
            '#u': 's3-url'
        },
        ExpressionAttributeValues={
            ':url': url
        }
    )
    items = response.get('Items', [])
    if not items:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            },
            'body': json.dumps({'error': 'Item not found'})
        }
    
    item_id = items[0]['id']
    
    # 获取当前图片的标签列表
    current_item = table.get_item(Key={'id': item_id})
    current_tags = current_item.get('Item', {}).get('tags', [])
    
    # 处理添加或删除标签的请求
    if type == 1:
        # 更新标签数量
        for tag in tags:
            tag_name = tag['tag']
            tag_count = tag.get('count', 1)
            
            # 查找当前标签是否已存在
            tag_exists = False
            for current_tag in current_tags:
                if current_tag[0] == tag_name:
                    current_tag[1] = tag_count
                    tag_exists = True
                    break
            
            # 如果当前标签不存在，则添加新标签
            if not tag_exists:
                current_tags.append([tag_name, tag_count])
    else:
        # 删除标签
        for tag in tags:
            tag_name = tag['tag']
            tag_count = tag.get('count', 1)
            
            # 查找并删除当前标签
            for current_tag in current_tags:
                if current_tag[0] == tag_name:
                    current_tag[1] -= tag_count
                    if current_tag[1] <= 0:
                        current_tags.remove(current_tag)
                    break
    
    # 更新 DynamoDB 表中的项目
    response1 = table.update_item(
        Key={
            'id': item_id
        },
        UpdateExpression='SET tags = :tags',
        ExpressionAttributeValues={
            ':tags': current_tags
        }
    )
    
    # 返回更新后的项目
    updated_item = table.get_item(Key={'id': item_id})
    print("updated_item:", updated_item)
     
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': json.dumps(updated_item, default=decimal_default)
    }
