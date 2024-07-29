import telebot
import os
import string
import random
from reportlab.pdfgen import canvas
from PIL import Image
import pytesseract 
import google.generativeai as genai

# Path to the Tesseract executable
# Download tool: https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

Token = ""
bot = telebot.TeleBot(Token)

gemini_api=''
genai.configure(api_key=gemini_api)
model = genai.GenerativeModel('gemini-1.5-flash')

save_path="NULL"


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello, I am Student Bot. How may I help you today? 🤖")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Get the file ID of the document
    file_id = message.document.file_id
    # Download the document
    file = bot.get_file(file_id)
    downloaded_file = bot.download_file(file.file_path)
    # Save the document to disk
    global res
    res = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
    global save_path
    save_path = res + '.jpeg'
    with open(save_path, 'wb') as f:
        f.write(downloaded_file)
    bot.send_message(message.chat.id, 'Document received. Choose operation to perform')


@bot.message_handler(commands=['convert_to_pdf'])
# Send a message to the user confirming that the document was received
def convert_to_pdf(message):
    global save_path
    if save_path=='NULL':
        bot.send_message(message.chat.id, 'Please send an image document to proceed')
        return
    # Convert image to PDF
    image_to_pdf(save_path, res + '.pdf')
    # Send the PDF file
    with open(res + '.pdf', 'rb') as file:
        bot.send_document(message.chat.id, file)
    os.remove(save_path)
    os.remove(res+'.pdf')
    save_path='NULL'
    # bot.send_message(message.chat.id, 'Thanks for using me 😊')


@bot.message_handler(commands=['scan'])
def scan(message):
    global save_path
    if save_path=='NULL':
        bot.send_message(message.chat.id, 'Please send an image document to proceed')
        return
    # Extract text from the image
    extracted_text = extract_text_from_image(save_path)
    # Send the extracted text
    bot.send_message(message.chat.id, f'{extracted_text}')
    os.remove(save_path)    
    save_path='NULL'


@bot.message_handler(content_types=['text'])
def generate_content(message):
    user_text=message.text
    # generating response
    response = model.generate_content(user_text+'in short')
    bot.send_message(message.chat.id, f'{response.text}')


def image_to_pdf(input_image, output_pdf):
    img = Image.open(input_image)
    pdf = canvas.Canvas(output_pdf, pagesize=img.size)
    pdf.drawInlineImage(input_image, 0, 0)
    pdf.save()


def extract_text_from_image(image_path):
    try:
        # Open the image file
        img = Image.open(image_path)
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"Error: {e}"


bot.polling()