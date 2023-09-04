import pytesseract
import uvicorn
import os
import openai
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path

app = FastAPI()

load_dotenv()

# OPENAI_DEPLOYMENT_NAME = 'sqy-gpt-35-turbo'
openai.api_type = "azure"
openai.api_key = os.getenv('openai.api_key')
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

@app.post("/uploadpdf/")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    # Check if the uploaded file is a PDF
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file format")

    # Create a temporary file to save the uploaded PDF
    temp_pdf_path = f"temp_{pdf_file.filename}"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.file.read())

    # Process the PDF file
    pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
    images = convert_from_path(temp_pdf_path, dpi=300, poppler_path=r'poppler-23.05.0\Library\bin')
    text = ""
    
    # Extract text from the first 4 pages
    for page_count, page in enumerate(images, start=1):
        page_text = pytesseract.image_to_string(page)
        text += page_text
        if page_count == 4:
            break

    text = text.replace('\n', '')

    # Use OpenAI API to generate a description
    completion = openai.ChatCompletion.create(
        deployment_id="sqy-gpt-35-turbo",
        model="gpt-3.5-turbo",
        temperature=1.3,
        messages=[
            {"role": "system", "content": "i will give you dataset, the dataset belongs to real estate projects, Given the dataset containing valuable information on various real estate projects, your task is to craft a comprehensive and engaging 500-word project description that intricately illustrates the key features, benefits, and potential of these projects. Your description should captivate potential investors and buyers, providing them with a vivid picture of the exceptional opportunities and unique qualities each project presents. Ensure that your narrative not only highlights the project's physical attributes but also its location, market potential, and any other relevant details that can make these real estate ventures stand out in the competitive market."},
            {"role": "user", "content": str(text)}
        ]
    )

    get_content = completion.choices[0].message
    result = get_content['content']

    # Clean up the temporary PDF file
    os.remove(temp_pdf_path)
    # print(result)
    return {"Description": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
