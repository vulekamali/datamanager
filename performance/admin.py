from django.contrib import admin

from performance import models


class EQPRSFileUploadAdmin(admin.ModelAdmin):
    exclude = ('num_imported', 'import_report', 'num_not_imported')
    readonly_fields = ('num_imported', 'import_report', 'num_not_imported')
    fieldsets = (
        ("", {
            "fields": (
                'user', 'file', 'import_report', 'num_imported', 'num_not_imported'
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user', 'file',) + self.readonly_fields
        return self.readonly_fields


class IndicatorAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.EQPRSFileUpload, EQPRSFileUploadAdmin)
admin.site.register(models.Indicator, IndicatorAdmin)
