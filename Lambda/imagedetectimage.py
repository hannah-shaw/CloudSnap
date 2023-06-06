import json
import urllib.parse
import numpy as np
import sys
import time
import cv2
import os
import boto3
import uuid
import base64

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
TABLE_NAME = 'assignment2tags'
image_bucket = 'bucket-for-images-5225'
yolo_bucket = 'yolo-configs-5225'

# construct the argument parse and parse the arguments
confthres = 0.1
nmsthres = 0.1

def get_labels(labels_path):
    # load the COCO class labels our YOLO model was trained on
    response = s3.get_object(
        Bucket=yolo_bucket,
        Key=labels_path
    )
    LABELS = response.get('Body').read().decode('utf8').strip().split("\n")
    return LABELS


def get_weights(weights_path):
    # derive the paths to the YOLO weights and model configuration
    response = s3.get_object(
        Bucket=yolo_bucket,
        Key=weights_path
    )
    WEIGHTS = response.get('Body').read()
    return WEIGHTS


def get_config(config_path):
    response = s3.get_object(
        Bucket=yolo_bucket,
        Key=config_path
    )
    CONFIG = response.get('Body').read()
    return CONFIG


def load_model(configpath, weightspath):
    # load our YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configpath, weightspath)
    print("[INFO] net over")
    return net


def do_prediction(image, net, LABELS):
    (H, W) = image.shape[:2]
    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[int(i) - 1] for i in net.getUnconnectedOutLayers()]

    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    # print(layerOutputs)
    end = time.time()

    # show timing information on YOLO
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            # print(scores)
            classID = np.argmax(scores)
            # print(classID)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > confthres:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])

                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping bounding boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres,
                            nmsthres)

    # TODO Prepare the output as required to the assignment specification
    # ensure at least one detection exists
    tags = []
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            tags.append(LABELS[classIDs[i]])
            print("detected item:{}, accuracy:{}, X:{}, Y:{}, width:{}, height:{}".format(LABELS[classIDs[i]],
                                                                                          confidences[i],
                                                                                          boxes[i][0],
                                                                                          boxes[i][1],
                                                                                          boxes[i][2],
                                                                                          boxes[i][3]))
    return list(tags)


## Yolov3-tiny versrion
labelsPath = "coco.names"
cfgpath = "yolov3-tiny.cfg"
wpath = "yolov3-tiny.weights"

Lables = get_labels(labelsPath)
CFG = get_config(cfgpath)
Weights = get_weights(wpath)


def detect_image(imagefile):
    nparr = np.frombuffer(imagefile, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
    image = img_np.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    nets = load_model(CFG, Weights)
    tags = do_prediction(image, nets, Lables)
    print("[INFO] prediction over")
    return tags


def lambda_handler(event, context):
    # TODO implement
    body = json.loads(event['body'])
    image_data = body['imageData']
    filename = body['filename']

    # 解码图片数据
    image_data = base64.b64decode(image_data)
    tags = detect_image(image_data)
    print("[INFO] detect over and detected" + str(tags))
    errorResponse = {"message": "We couldn't find images in our Database."}
    if tags is None:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
                'Access-Control-Allow-Origin': '*'  # 允许所有源
                },
        'body': json.dumps(errorResponse)
        }

    # count the occurrences of each tag
    counts = {}
    for tag in tags:
        if tag in counts:
            counts[tag] += 1
        else:
            counts[tag] = 1

    # create a list of dictionaries with tag and count
    tags_list = []
    for tag, count in counts.items():
        tag_dict = {}
        tag_dict['S'] = tag
        count_dict = {}
        count_dict['N'] = str(count)
        # Add label dictionaries and counting dictionaries to the list
        tag_list = []
        tag_list.append(tag_dict)
        tag_list.append(count_dict)
        # Convert the list of tags into nested dictionaries
        tags_dict = {}
        tags_dict['L']= tag_list
        # Add nested dictionaries to the list of tag dictionaries
        tags_list.append(tags_dict)

    errorResponse1 = {"message": "error: No labels detected."}
    tags = {'L': tags_list}
    if tags_list:
        d_set = set()
        for tag_dict in tags['L']:
            tag = tag_dict['L'][0]['S']
            count = tag_dict['L'][1]['N']
            d_set.add((tag, count))
        print(d_set)
    else:
        return {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': json.dumps(errorResponse1)
    }
    
    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response.get('Items')
    urls = []
    #print(items)
    for i in items:
        item_tags = i.get('tags').get('L')
        #Convert labels to tuple lists
        #print(i)
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
                    if s_tag == tag and s_count >= int(count):
                        d_num = d_num-1
            if(d_num==0):
                url = i.get('s3-url').get('S')
                urls.append(url)
    response_image_links = {"links": urls}
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
            'Access-Control-Allow-Origin': '*'  # 允许所有源
        },
        'body': json.dumps(response_image_links)
    }
        