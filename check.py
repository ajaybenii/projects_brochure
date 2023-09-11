import pytesseract
from PIL import Image  # Make sure you have the PIL/Pillow library installed

# Open an image using PIL
image = Image.open('your_image.png')

# Use pytesseract to perform OCR on the image
text = pytesseract.image_to_string(image)

# Print the extracted text
print(text)