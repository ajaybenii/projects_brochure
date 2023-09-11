import os
import pytesseract
import openai
from fastapi import FastAPI, File, UploadFile, HTTPException
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PIL import Image
import logging


import io
app = FastAPI()

load_dotenv()

# Set up OpenAI API
openai.api_type = "azure"
openai.api_key = 'f379f0f5e9e042289297765f32320268'

openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

# relative_path = r'Tesseract-OCR\tesseract.exe'
# absolute_path = os.path.abspath(str(pytesseract))
# print(absolute_path)

tesseract_path = r'Tesseract-OCR\tesseract.exe'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Function to process PDF and extract text
def process_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for page_count, page in enumerate(images, start=1):

        b = io.BytesIO()
        page.save(b, "JPEG")
        img_bytes = b.getvalue()

        page_text = str(
            (
                (
                    pytesseract.image_to_string(
                        Image.open(io.BytesIO(img_bytes)), lang="eng", config="--psm 3"
                    )
                )
            )
        )
        # page_text = pytesseract.image_to_string(page)
        # print(page_text)
        text += page_text
        # # if len(text) >= 12500:
        # print("page count = ", page_count)
        if page_count == 4:
            break
    # print(text)
    return text

@app.post("/uploadpdf/")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    try:
        # Check if the uploaded file is a PDF
        if pdf_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file format")

        # Create a temporary file to save the uploaded PDF
        temp_pdf_path = f"temp_{pdf_file.filename}"
        with open(temp_pdf_path, "wb") as temp_pdf:
            temp_pdf.write(pdf_file.file.read())

        try:
            # pytesseract.pytesseract.tesseract_cmd = tesseract_path
            pdf_text = process_pdf(temp_pdf_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
        finally:
            os.remove(temp_pdf_path)

        print("text = ", pdf_text)

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
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
