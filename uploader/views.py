from django.shortcuts import render, redirect
from uploader.forms import ImageFileForm
from uploader.models import ImageFile
import pytesseract 
from PIL import Image

# Path of working folder on Disk Replace with your working folder
src_path = "C:\\Users\\<user>\\PycharmProjects\\ImageToText\\input\\"
# If you don't have tesseract executable in your PATH, include the following:
TESSDATA_PREFIX = 'C:/Program Files (x86)/Tesseract-OCR'

pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe' 


def home(request):
    data = dict()

    image_form = ImageFileForm(request.POST or None, request.FILES or None)
    if image_form.is_valid():
        image = image_form.save()
        image.execute_and_save_ocr()
        redirect('home')

    image_list = ImageFile.objects.all().order_by('-id')
    # print("||||||||||||||||||||||||||||||||||||")
    # print(image_list)
    data['image_form'] = image_form
    data['image_list'] = image_list
    return render(request, "uploader/index.html", data)
