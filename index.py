import io
import boto3
import easyocr
import numpy as np
from PIL import Image
from typing import List, Dict
from botocore.exceptions import ClientError

def extract_position(coords: List[float]) -> Dict[str, int]:
    return {"x": int(coords[0]), "y": int(coords[1])}

def lambda_handler(event, context):
    try:
        # Input validation
        key = event.get('Key')
        bucket = event.get('Bucket')
        target_languages = event.get('TargetLanguages')
        
        if not all([key, bucket, target_languages]):
            raise ValueError("Missing required parameters: Key, Bucket, or TargetLanguages")

        # Initialize S3 client once
        s3_client = boto3.client('s3')

        # Get image from S3
        try:
            image_obj = s3_client.get_object(Bucket=bucket, Key=key)
            image_content = image_obj['Body'].read()
        except ClientError as e:
            return {
                'error': f"Error retrieving image from S3: {str(e)}"
            }

        # Process image
        image = Image.open(io.BytesIO(image_content))
        image_np = np.array(image)

        # Initialize EasyOCR reader
        reader = easyocr.Reader(
            target_languages,
            model_storage_directory='/tmp',
            user_network_directory='/tmp',
            download_enabled=True,
            gpu=False
        )

        # Perform text detection
        results = reader.readtext(image_np)

        # Process results
        positions = [{
            "Text": result[1],
            "TopLeft": extract_position(result[0][0]),
            "TopRight": extract_position(result[0][1]),
            "BottomRight": extract_position(result[0][2]),
            "BottomLeft": extract_position(result[0][3])
        } for result in results]

        # Join detected texts efficiently
        detected_texts_join = ' '.join(result[1] for result in results)

        return {
            'DetectedText': detected_texts_join,
            'DetectedResults': positions
        }

    except Exception as e:
        return {
            'error': f"Error processing image: {str(e)}"
        }
