import os
import pytesseract
import openai

from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, File, UploadFile, HTTPException
from dotenv import load_dotenv
from typing import Optional
from pdf2image import convert_from_path
from google.cloud import storage




app = FastAPI()

# Define your GCP credentials path
credentials_path = "sqy-prod-e00ffd95e2ce.json"

# Initialize a GCS client
client = storage.Client.from_service_account_json(credentials_path)

load_dotenv()

# Set up OpenAI API
openai.api_type = "azure"
openai.api_key = os.getenv("openai.api_key")
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"


# Function to process PDF and extract text
def process_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for page_count, page in enumerate(images, start=1):
        page_text = pytesseract.image_to_string(page)
        text += page_text

        if len(text) >= 12500:
            break
    
    return text


@app.get("/")
async def root():
    return "API is working."


@app.post("/")
async def upload_pdf_path(project_details: str, pdf_file_path: str):
    
    bucket_name = "sqydocs"
    # Convert the URL to the GCS path (remove the protocol and domain)
    gcs_path = pdf_file_path.replace("https://img.squareyards.com/", "")
    
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_path)

    # Download the file to a local destination
    blob.download_to_filename("gcp_pdf.pdf")

    pdf_file_path = "gcp_pdf.pdf"
    temp_pdf_path = pdf_file_path

    try:

        pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
        pdf_text = process_pdf(temp_pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
    finally:
        os.remove(temp_pdf_path)
    
    req_body = jsonable_encoder(project_details)
    pdf_text = req_body+pdf_text
    
    try:
        # Use OpenAI API to generate a description
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature=1.3,
            messages=[
                {"role": "system", "content": "i will give you content, the content belongs to real estate projects, content containing valuable information of real estate project, your task is to genrate a description, which is easy to readable and it should be in normal english langauge and engaging only 500-word project description that intricately illustrates the key features, property price, amenities,property size, benefits, and potential of these projects. Your description should captivate potential investors and buyers. Ensure that your narrative not only highlights the project's physical attributes but also its location, market potential, and please does not mention any mobile number or personal details in description. The output response should be without any grammatical or syntax error and remove this (\n\n) from response."},
                {"role": "user", "content": str(pdf_text)}
            ]
        )

        result = completion.choices[0].message['content']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Openai API error: {str(e)}")
    
    result = str(result).replace("\n\n", "")
    result = str(result).replace(".\n\n", ". ")
    result = str(result).replace(".\n", ". ")

    os.remove(pdf_file_path)
    return {"Description": result}


@app.post("/uploadpdf/")
async def upload_pdf(project_details: str, pdf_file: UploadFile = File(...)):

    # Check if the uploaded file is a PDF
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file format")

    # Create a temporary file to save the uploaded PDF
    temp_pdf_path = f"temp_{pdf_file.filename}"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.file.read())

    try:

        pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
        pdf_text = process_pdf(temp_pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
    finally:
        os.remove(temp_pdf_path)
    
    req_body = jsonable_encoder(project_details)
    pdf_text = req_body+pdf_text
    
    try:
        # Use OpenAI API to generate a description
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature=1.3,
            messages=[
                {"role": "system", "content": "i will give you content, the content belongs to real estate projects, content containing valuable information of real estate project, your task is to genrate a description, which is easy to readable and it should be in normal english langauge and engaging only 500-word project description that intricately illustrates the key features, property price, amenities,property size, benefits, and potential of these projects. Your description should captivate potential investors and buyers. Ensure that your narrative not only highlights the project's physical attributes but also its location, market potential, and please does not mention any mobile number or personal details in description. The output response should be without any grammatical or syntax error and remove this (\n\n) from response."},
                {"role": "user", "content": str(pdf_text)}
            ]
        )

        result = completion.choices[0].message['content']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Openai API error: {str(e)}")
    
    result = str(result).replace("\n\n", "")
    result = str(result).replace(".\n\n", ". ")
    result = str(result).replace(".\n", ". ")

    return {"Description": result}