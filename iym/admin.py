from django.contrib import admin
from iym import models


class IYMFileUploadAdmin(admin.ModelAdmin):
    readonly_fields = (
        "import_report",
        "user",
        "process_completed"
    )
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "user",
                    "financial_year",
                    "latest_quarter",
                    "file",
                    "import_report",
                    "process_completed",
                )
            },
        ),
    )
    list_display = (
        "created_at",
        "user",
        "financial_year",
        "latest_quarter",
        "process_completed",
        "updated_at",
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(models.IYMFileUpload, IYMFileUploadAdmin)
