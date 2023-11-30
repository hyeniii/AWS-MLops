FROM --platform=linux/x86_64 amazon/aws-lambda-python:3.9

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY aws_utils.py ${LAMBDA_TASK_ROOT}
COPY geolocate.py ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

COPY config.ini ${LAMBDA_TASK_ROOT}
COPY data_clean_config.yaml ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.lambda_handler" ]
