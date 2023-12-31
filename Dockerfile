
# FROM python:3.9

# RUN apt-get update

# RUN apt-get -y install tesseract-ocr
# RUN apt-get install poppler-utils -y

# # Set the working directory inside the container
# WORKDIR /app

# # Copy the requirements file into the container
# COPY requirements.txt .

# # Install any dependencies needed for your application
# RUN pip install -r requirements.txt


# # Copy your application code into the container
# COPY . .

# # Expose the port that your FastAPI application will run on (change it if needed)
# EXPOSE 80

# CMD gunicorn --bind 0.0.0.0:$PORT main:app -k uvicorn.workers.UvicornWorker

# Use an official Python runtime as a parent image
# Use an official Python runtime as a parent image
FROM python:3.9

# Install Tesseract OCR and Poppler utilities
RUN apt-get update \
    && apt-get -y install tesseract-ocr \
    && apt-get install poppler-utils -y

# Set the working directory inside the container
WORKDIR /projects_brochure

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies needed for your application
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose the port that your FastAPI application will run on (change it if needed)
EXPOSE 80

# Define environment variables for logging
ENV LOG_FILE /projects_brochure/app.log
ENV LOG_LEVEL INFO

# Install Gunicorn and Create a Log Directory
RUN pip install gunicorn
RUN mkdir /projects_brochure/logs

# Define the command to run your FastAPI application with Gunicorn
CMD ["gunicorn", "main:app", "--log-file", "$LOG_FILE", "--log-level", "$LOG_LEVEL"]
