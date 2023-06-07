from django.contrib import admin
from iym import models


def process_uploaded_file(obj_id):
    # read file
    obj_to_update = models.IYMFileUpload.objects.get(id=obj_id)
    full_text = obj_to_update.file.read().decode("utf-8")

    print('============ aaa ============')
    print(obj_to_update.file.__dict__)
    print('============ bbb ============')


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

        process_uploaded_file(obj.id)


admin.site.register(models.IYMFileUpload, IYMFileUploadAdmin)
