from django.contrib import admin
from uploader.models import *
from import_export.admin import ImportExportModelAdmin

@admin.register(OCRText,ImageFile)
class ViewAdmin(ImportExportModelAdmin):
    pass
