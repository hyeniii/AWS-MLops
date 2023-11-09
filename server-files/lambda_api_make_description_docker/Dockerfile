# Base image
#FROM public.ecr.aws/lambda/python:3.11
FROM --platform=linux/x86_64 amazon/aws-lambda-python:3.9

# Copy requirements file to wd
COPY requirements_api_make_description.txt ${LAMBDA_TASK_ROOT}

# Install libraries
RUN pip install -r requirements_api_make_description.txt

# Copy folders & files to run pipeline: config, src, pipeline.py
COPY config ${LAMBDA_TASK_ROOT}/config
COPY make_description.py ${LAMBDA_TASK_ROOT}

# Command to run when running docker container
CMD ["make_description.lambda_handler"]