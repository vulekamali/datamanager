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

    class Media:
        js = ("js/eqprs-file-upload.js",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user', 'file',) + self.readonly_fields
        return self.readonly_fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super(EQPRSFileUploadAdmin, self).render_change_form(request, context, add, change, form_url, obj)
        response.context_data['title'] = 'EQPRS file upload' if response.context_data[
            'object_id'] else 'Add EQPRS file upload'
        return response


class IndicatorAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.EQPRSFileUpload, EQPRSFileUploadAdmin)
admin.site.register(models.Indicator, IndicatorAdmin)
