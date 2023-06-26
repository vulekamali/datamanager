from django.contrib import admin
from iym import models
from django_q.tasks import async_task

import iym
from iym.tasks import process_uploaded_file


class IYMFileUploadAdmin(admin.ModelAdmin):
    readonly_fields = (
        "import_report",
        "user",
        "process_completed",
        "status",
        "task_id",
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
                    "task_id",
                    "import_report",
                    "status",
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
        "status",
        "process_completed",
        "updated_at",
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

        obj.task_id = async_task(func=process_uploaded_file, obj_id=obj.id)
        obj.save()

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return (
                       "financial_year",
                       "latest_quarter",
                       "file",
                   ) + self.readonly_fields
        return self.readonly_fields

    def has_change_permission(self, request, obj=None):
        super(IYMFileUploadAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        super(IYMFileUploadAdmin, self).has_delete_permission(request, obj)


admin.site.register(models.IYMFileUpload, IYMFileUploadAdmin)
