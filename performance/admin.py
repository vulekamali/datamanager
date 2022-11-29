from django.contrib import admin

from performance import models


class EQPRSFileUploadAdmin(admin.ModelAdmin):
    pass


class IndicatorAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.EQPRSFileUpload, EQPRSFileUploadAdmin)
admin.site.register(models.Indicator, IndicatorAdmin)
