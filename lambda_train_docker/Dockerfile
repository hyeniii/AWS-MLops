# Base image
FROM public.ecr.aws/lambda/python:3.11

# Create working directory in container
#WORKDIR /app

# Copy requirements file to wd
COPY requirements_train.txt ${LAMBDA_TASK_ROOT}

# Install libraries
#RUN pip install --upgrade pip
RUN pip install -r requirements_train.txt

# Copy folders & files to run pipeline: config, src, pipeline.py
COPY config ${LAMBDA_TASK_ROOT}/config
COPY src ${LAMBDA_TASK_ROOT}/src
COPY main.py ${LAMBDA_TASK_ROOT}

# Command to run when running docker container
CMD ["main.lambda_handler"]