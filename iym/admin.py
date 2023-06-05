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


admin.site.register(models.IYMFileUpload, IYMFileUploadAdmin)
