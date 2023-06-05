from django.contrib import admin
from iym import models

class IYMFileUploadAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.IYMFileUpload, IYMFileUploadAdmin)