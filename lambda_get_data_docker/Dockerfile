# Base image
#FROM public.ecr.aws/lambda/python:3.11
FROM --platform=linux/x86_64 amazon/aws-lambda-python:3.9

# Copy requirements file to wd
COPY requirements_local_data_ingest.txt ${LAMBDA_TASK_ROOT}

# Install libraries
RUN pip install -r requirements_local_data_ingest.txt

# Copy folders & files to run pipeline: config, src, pipeline.py
COPY config ${LAMBDA_TASK_ROOT}/config
COPY get_data.py ${LAMBDA_TASK_ROOT}

# Command to run when running docker container
CMD ["get_data.lambda_handler"]