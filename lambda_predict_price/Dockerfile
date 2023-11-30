# Base image
#FROM public.ecr.aws/lambda/python:3.11
FROM --platform=linux/x86_64 amazon/aws-lambda-python:3.9

# Copy requirements file to wd
COPY requirements_prediction.txt ${LAMBDA_TASK_ROOT}

# Install libraries
RUN pip install -r requirements_prediction.txt

# Copy folders & files to run pipeline: config, src, pipeline.py
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY prediction_utils.py ${LAMBDA_TASK_ROOT}

COPY config.ini ${LAMBDA_TASK_ROOT}
COPY inference_config.yaml ${LAMBDA_TASK_ROOT}

# Command to run when running docker container
CMD ["lambda_function.lambda_handler"]