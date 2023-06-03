import json
import boto3
import base64
import time

def lambda_handler(event, context):
    # 从event中提取Base64编码的图片数据
    image_data = json.loads(event['body'])['image']
    
    # 将Base64编码的图片数据解码为二进制数据
    image_data = base64.b64decode(image_data)
    
    # 创建S3客户端
    s3 = boto3.client('s3')
    
    # 定义S3桶和对象的键
    bucket = 'bucket-for-images-5225'
    key = str(time.time())
    
    try:
        # 将图片数据上传到S3
        s3.put_object(Bucket=bucket, Key=key, Body=image_data)
        return {
            'statusCode': 200,
            'body': json.dumps('Image uploaded to S3 successfully!')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps('An error occurred: ' + str(e))
        }
