# FROM python:3.8

# # RUN useradd -m SQRYRDS

# ENV PYTHONUNBUFFERED 0

# ENV ERROR_LOGFILE /home/app/logs/gunicorn-error.log

# ENV ACCESS_LOGFILE /home/app/logs/gunicorn-access.log

# WORKDIR /home/app

# ADD requirements.txt /home/app

# RUN apt-get update && apt-get install -y tesseract-ocr && apt-get clean

# RUN pip install --upgrade pip && \
#     pip install --trusted-host pypi.python.org -r requirements.txt

# RUN apt-get clean && apt-get update && apt-get install -y locales locales-all

# ADD . /home/app
# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies needed for your application
RUN pip install -r requirements.txt

# Install Tesseract OCR and clean up APT package cache
RUN apt-get update && apt-get install -y tesseract-ocr && apt-get clean

# Copy your application code into the container
COPY . .

# Expose the port that your FastAPI application will run on (change it if needed)
EXPOSE 80

# # Command to run your FastAPI application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]


# EXPOSE 8080

# ENV PORT="${PORT:-8080}"

CMD gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --workers=4 \
    --timeout 60 \
    -k uvicorn.workers.UvicornWorker \
    --log-level=info \
    --error-logfile=$ERROR_LOGFILE \
    --access-logfile=$ACCESS_LOGFILE \
    --capture-output

