from django.db import models
from core import utils
import hashlib
from PIL import Image
import pytesseract
import re
import csv
import pandas as pd  

class ImageFileManager(models.Manager):

    def search(self, query):
        return self.get_queryset().filter(models.Q(internal_reference__icontains=query) |
                                          models.Q(name__icontains=query) |
                                          models.Q(description__icontains=query)
                                          )


class ImageFile(models.Model):

    state_choices = (
        ("Andhra Pradesh", "Andhra Pradesh"), ("Arunachal Pradesh ", "Arunachal Pradesh "), ("Assam", "Assam"),
        ("Bihar", "Bihar"), ("Chhattisgarh", "Chhattisgarh"), ("Goa", "Goa"), ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"), ("Himachal Pradesh", "Himachal Pradesh"), ("Jammu and Kashmir ", "Jammu and Kashmir "),
        ("Jharkhand", "Jharkhand"), ("Karnataka", "Karnataka"), ("Kerala", "Kerala"), ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"), ("Manipur", "Manipur"), ("Meghalaya", "Meghalaya"), ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"), ("Odisha", "Odisha"), ("Punjab", "Punjab"), ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"), ("Tamil Nadu", "Tamil Nadu"), ("Telangana", "Telangana"), ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"), ("Uttarakhand", "Uttarakhand"), ("West Bengal", "West Bengal"),
        ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"), ("Chandigarh", "Chandigarh"),
        ("Dadra and Nagar Haveli", "Dadra and Nagar Haveli"), ("Daman and Diu", "Daman and Diu"),
        ("Lakshadweep", "Lakshadweep"), ("National Capital Territory of Delhi", "National Capital Territory of Delhi"),
        ("Puducherry", "Puducherry"))
        
    name = models.CharField("Name", max_length=100)
    city = models.CharField("City", max_length=100)
    state= models.CharField(choices=state_choices,max_length=36, null=True, blank=True)
    internal_reference = models.CharField("Internal Reference", max_length=100, editable=False)
    description = models.TextField("Description", blank=True, null=True)
    image = models.ImageField(upload_to="OCR_image/input/", verbose_name="Input Image")
    create_at = models.DateTimeField("Create at", auto_now_add=True)
    updated_at = models.DateTimeField("Update at", auto_now=True)

    def __str__(self):
        return "{0:03d} - {1}".format(self.id, self.image)

    def execute_and_save_ocr(self):
        import time
        start_time = time.time()

        img = Image.open(self.image)

        txt = pytesseract.image_to_string(img, lang='eng')
        city = self.city + "["+self.state+"]"
        # phone number Regex 
        
        #regex = '(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
        txt = [ str(s) for s in re.findall('\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}', txt)]
        execution_time = time.time() - start_time
        
        ocr_txt = OCRText(image = self, text = txt, lang = city, execution_time = execution_time)
        ocr_txt.save()

        print("The image {0} was opened.".format(self.image))
        print('OCR: \n{0}\n'.format(txt))
        print('Execution Time: {0}'.format(ocr_txt.execution_time))

        return ocr_txt

    """
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('course_details', args=[], kwargs={'slug': self.slug})
    """

    def save(self, *args, **kwargs):

        if not self.internal_reference:
            random_value = utils.random_value_generator(size=20)
            while ImageFile.objects.filter(internal_reference=random_value).exists():
                random_value = utils.random_value_generator(size=20)
            hash_value = hashlib.md5(bytes(str(self.id) + str(random_value), 'utf-8'))
            self.internal_reference = hash_value.hexdigest()
        super(ImageFile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "ImageFile"
        verbose_name_plural = "ImageFiles"
        ordering = ['id']

    objects = ImageFileManager()


class OCRText(models.Model):
    text = models.TextField("OCR text", blank=True)
    lang = models.TextField("Language", default="EN")
    execution_time = models.IntegerField("Execution Time", editable=False, null=True);
    image = models.ForeignKey('ImageFile', on_delete=models.CASCADE)
    create_at = models.DateTimeField("Create at", auto_now_add=True)
    updated_at = models.DateTimeField("Update at", auto_now=True)

    def __str__(self):
        return "{0:03d} - {1}".format(self.id, self.image.internal_reference)

    class Meta:
        verbose_name = "OCRText"
        verbose_name_plural = "OCRTexts"
        ordering = ['id']
