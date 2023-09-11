# import os
# import pytesseract
# import openai

# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse
# from pdf2image import convert_from_path

# from dotenv import load_dotenv

# app = FastAPI()

# load_dotenv()

# # OPENAI_DEPLOYMENT_NAME = 'sqy-gpt-35-turbo'
# openai.api_type = "azure"
# openai.api_key = 'f379f0f5e9e042289297765f32320268'

# openai.api_base = 'https://sqy-openai.openai.azure.com/'
# openai.api_version = "2023-05-15"

# # poppler_path = os.environ("poppler-23.05.0/Library/bin")
# # Set the path to the Poppler binaries directory
# # relative_path = r'poppler-23.08.0\Library\bin'
# # absolute_path = os.path.abspath(relative_path)
# # print(absolute_path)

# # poppler_path = os.environ.get("poppler_path")

# @app.post("/uploadpdf/")
# async def upload_pdf(pdf_file: UploadFile = File(...)):
#     # Check if the uploaded file is a PDF
#     if pdf_file.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Invalid file format")

#     # Create a temporary file to save the uploaded PDF
#     temp_pdf_path = f"temp_{pdf_file.filename}"
#     with open(temp_pdf_path, "wb") as temp_pdf:
#         temp_pdf.write(pdf_file.file.read())

#     # Process the PDF file
#     # pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
#     images = convert_from_path(temp_pdf_path)
#     text = ""

#     # Extract text from the all pages
#     for page_count, page in enumerate(images, start=1):
#         page_text = pytesseract.image_to_string(page)
#         text += page_text

#         if len(text) >= 12500:
#             break

#     text = text.replace('\n', '')
    

#     # if len(text) == 
#     # Use OpenAI API to generate a description
#     completion = openai.ChatCompletion.create(
#         deployment_id="sqy-gpt-35-turbo",
#         model="gpt-3.5-turbo",
#         temperature=1.3,
#         messages=[
#             {"role": "system", "content": "i will give you dataset, the dataset belongs to real estate projects, dataset containing valuable information on various real estate projects, your task is to craft a comprehensive and engaging 500-word project description that intricately illustrates the key features, property price, amenities,property size, benefits, and potential of these projects. Your description should captivate potential investors and buyers, providing them with a vivid picture of the exceptional opportunities and unique qualities each project presents. Ensure that your narrative not only highlights the project's physical attributes but also its location, market potential, and any other relevant details that can make these real estate ventures stand out in the competitive market.The output response should be without any grammtical or syntax error."},
#             {"role": "user", "content": str(text)}
#         ]
#     )

#     get_content = completion.choices[0].message
#     result = get_content['content']
#     result = result.replace('\n', '')

#     # Clean up the temporary PDF file
#     os.remove(temp_pdf_path)

#     return {"Description": result}

import os
import pytesseract
import openai
from fastapi import FastAPI, File, UploadFile, HTTPException
from dotenv import load_dotenv
from pdf2image import convert_from_path

app = FastAPI()

load_dotenv()

# Set up OpenAI API
openai.api_type = "azure"
openai.api_key = os.getenv("openai.api_key")
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

relative_path = r'Tesseract-OCR\tesseract.exe'
absolute_path = os.path.abspath(relative_path)
print(absolute_path)

tesseract_path = r'Tesseract-OCR\tesseract.exe'

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

@app.post("/uploadpdf/")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    # Check if the uploaded file is a PDF
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file format")

    # Create a temporary file to save the uploaded PDF
    temp_pdf_path = f"temp_{pdf_file.filename}"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.file.read())

    try:
        pytesseract.pytesseract.tesseract_cmd = absolute_path
        pdf_text = process_pdf(temp_pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
    finally:
        os.remove(temp_pdf_path)

    # Use OpenAI API to generate a description
    completion = openai.ChatCompletion.create(
        deployment_id="sqy-gpt-35-turbo",
        model="gpt-3.5-turbo",
        temperature=1.3,
        messages=[
            {"role": "system", "content": "i will give you content, the content belongs to real estate projects, content containing valuable information on various real estate projects, your task is to craft a comprehensive and engaging 500-word project description that intricately illustrates the key features, property price, amenities,property size, benefits, and potential of these projects. Your description should captivate potential investors and buyers, providing them with a vivid picture of the exceptional opportunities and unique qualities each project presents. Ensure that your narrative not only highlights the project's physical attributes but also its location, market potential, and any other relevant details that can make these real estate ventures stand out in the competitive market.The output response should be without any grammtical or syntax error."},
            {"role": "user", "content": str(pdf_text)}
        ]
    )

    result = completion.choices[0].message['content']

    return {"Description": result}
