import io
import boto3
import easyocr
import numpy as np
from PIL import Image


def lambda_handler(event, context):
    key = event.get('Key')
    bucket = event.get('Bucket')
    target_languages = event.get('TargetLanguages')

    s3_client = boto3.client('s3')

    image_obj = s3_client.get_object(Bucket=bucket, Key=key)
    image_content = image_obj['Body'].read()
    image = Image.open(io.BytesIO(image_content))
    image_np = np.array(image)

    reader = easyocr.Reader(
        target_languages,
        model_storage_directory='/tmp',
        user_network_directory='/tmp',
        download_enabled=True,
        gpu=False
    )
    results = reader.readtext(image_np)
    results = reader.readtext(image_np)

    detected_texts = []
    positions = []
    for result in results:
        text = result[1]
        detected_texts.append(text)

        position = result[0]
        top_left = [int(coord) for coord in position[0]]
        top_right = [int(coord) for coord in position[1]]
        bottom_right = [int(coord) for coord in position[2]]
        bottom_left = [int(coord) for coord in position[3]]
        positions.append({
            "Text": text,
            "TopLeft": {
                "x": top_left[0],
                "y": top_left[1]
            },
            "TopRight": {
                "x": top_right[0],
                "y": top_right[1]
            },
            "BottomRight": {
                "x": bottom_right[0],
                "y": bottom_right[1]
            },
            "BottomLeft": {
                "x": bottom_left[0],
                "y": bottom_left[1]
            }
        })

    detected_texts_join = ' '.join([result[1] for result in results])

    return {
        'DetectedText': detected_texts_join,
        'DetectedResults': positions
    }
