from django.contrib import admin

from performance import models


class EQPRSFileUploadAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "num_imported",
        "num_not_imported",
        "success",
        "updated_at",
    )
    readonly_fields = (
        "user",
        "num_imported",
        "num_not_imported",
        "success",
        "import_report",
    )
    exclude = ("task",)

    def success(self, obj):
        return obj.task.success

    success.boolean = True
    success.short_description = "Success"


class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "indicator_name",
        "financial_year",
        "sphere",
        "government",
        "get_department",
        "created_at",
    )
    list_filter = (
        "department__government__sphere__financial_year__slug",
        "department__government__sphere__name",
        "department__government__name",
        "department__name",
    )
    search_fields = (
        "department__government__sphere__financial_year__slug",
        "department__government__sphere__name",
        "department__government__name",
        "department__name",
        "indicator_name",
    )

    readonly_fields = (
        "source",
        "indicator_name",
        "department",
        "q1_target",
        "q1_actual_output",
        "q1_deviation_reason",
        "q1_corrective_action",
        "q1_national_comments",
        "q1_otp_comments",
        "q1_dpme_coordinator_comments",
        "q1_treasury_comments",
        "q2_target",
        "q2_actual_output",
        "q2_deviation_reason",
        "q2_corrective_action",
        "q2_national_comments",
        "q2_otp_comments",
        "q2_dpme_coordinator_comments",
        "q2_treasury_comments",
        "q3_target",
        "q3_actual_output",
        "q3_deviation_reason",
        "q3_corrective_action",
        "q3_national_comments",
        "q3_otp_comments",
        "q3_dpme_coordinator_comments",
        "q3_treasury_comments",
        "q4_target",
        "q4_actual_output",
        "q4_deviation_reason",
        "q4_corrective_action",
        "q4_national_comments",
        "q4_otp_comments",
        "q4_dpme_coordinator_comments",
        "q4_treasury_comments",
        "annual_target",
        "annual_aggregate_output",
        "annual_pre_audit_output",
        "annual_deviation_reason",
        "annual_corrective_action",
        "annual_otp_comments",
        "annual_national_comments",
        "annual_dpme_coordincator_comments",
        "annual_treasury_comments",
        "annual_audited_output",
        "sector",
        "programme_name",
        "subprogramme_name",
        "frequency",
        "type",
        "subtype",
        "mtsf_outcome",
        "cluster",
        "uid",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "source",
                    "indicator_name",
                    "department",
                    "sector",
                    "programme_name",
                    "subprogramme_name",
                    "frequency",
                    "type",
                    "subtype",
                    "mtsf_outcome",
                    "cluster",
                ),
            },
        ),
        (
            "Quarter 1",
            {
                "fields": (
                    "q1_target",
                    "q1_actual_output",
                    "q1_deviation_reason",
                    "q1_corrective_action",
                    "q1_national_comments",
                    "q1_otp_comments",
                    "q1_dpme_coordinator_comments",
                    "q1_treasury_comments",
                ),
            },
        ),
        (
            "Quarter 2",
            {
                "fields": (
                    "q2_target",
                    "q2_actual_output",
                    "q2_deviation_reason",
                    "q2_corrective_action",
                    "q2_national_comments",
                    "q2_otp_comments",
                    "q2_dpme_coordinator_comments",
                    "q2_treasury_comments",
                ),
            },
        ),
        (
            "Quarter 3",
            {
                "fields": (
                    "q3_target",
                    "q3_actual_output",
                    "q3_deviation_reason",
                    "q3_corrective_action",
                    "q3_national_comments",
                    "q3_otp_comments",
                    "q3_dpme_coordinator_comments",
                    "q3_treasury_comments",
                ),
            },
        ),
        (
            "Quarter 4",
            {
                "fields": (
                    "q4_target",
                    "q4_actual_output",
                    "q4_deviation_reason",
                    "q4_corrective_action",
                    "q4_national_comments",
                    "q4_otp_comments",
                    "q4_dpme_coordinator_comments",
                    "q4_treasury_comments",
                ),
            },
        ),
        (
            "Full year",
            {
                "fields": (
                    "annual_target",
                    "annual_aggregate_output",
                    "annual_pre_audit_output",
                    "annual_deviation_reason",
                    "annual_corrective_action",
                    "annual_otp_comments",
                    "annual_national_comments",
                    "annual_dpme_coordincator_comments",
                    "annual_treasury_comments",
                    "annual_audited_output",
                ),
            },
        ),
    )

    def get_department(self, obj):
        return obj.department.name

    get_department.short_description = "Department"

    def government(self, obj):
        return obj.department.government.name

    def sphere(self, obj):
        return obj.department.government.sphere.name

    def financial_year(self, obj):
        return obj.department.government.sphere.financial_year.slug


admin.site.register(models.EQPRSFileUpload, EQPRSFileUploadAdmin)
admin.site.register(models.Indicator, IndicatorAdmin)
