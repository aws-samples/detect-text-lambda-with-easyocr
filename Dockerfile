FROM public.ecr.aws/lambda/python:3.8

RUN yum -y install gcc python3-devel zlib-devel libjpeg-devel

RUN pip install easyocr Pillow numpy

COPY index.py ./

CMD ["index.lambda_handler"]
