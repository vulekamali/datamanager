from django.contrib import admin
from io import BytesIO
from performance import models

import json


def get_key_value_or_default(fields, key):
    if key in fields:
        return fields[key]
    else:
        return ""


class EQPRSFileUploadAdmin(admin.ModelAdmin): 
    exclude = ('num_imported', 'import_report', 'num_not_imported')
    readonly_fields = ('num_imported', 'import_report', 'num_not_imported')
    list_display = (
        "created_at",
        "user",
        "num_imported",
        "num_not_imported",
        "success",
        "updated_at",
    )
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        data = obj.file.read()
        parsed_data = json.loads(data)
        report_departments = set([x['fields']['department'][3] for x in parsed_data])

        for department in report_departments:
            department_obj = models.Department.objects.filter(name=department).first()
            models.Indicator.objects.filter(department=department_obj).delete()

        for indicator_data in parsed_data:
            fields = indicator_data['fields']
            department_name = fields['department'][3]
            department_obj = models.Department.objects.filter(name=department_name).first()

            models.Indicator.objects.create(
                indicator_name=fields['indicator_name'],
                department=department_obj,
                source_id=obj.id,

                q1_target=get_key_value_or_default(fields, 'q1_target'),
                q1_actual_output=get_key_value_or_default(fields, 'q1_actual_output'),
                q1_deviation_reason=get_key_value_or_default(fields, 'q1_deviation_reason'),
                q1_corrective_action=get_key_value_or_default(fields, 'q1_corrective_action'),
                q1_national_comments=get_key_value_or_default(fields, 'q1_national_comments'),
                q1_otp_comments=get_key_value_or_default(fields, 'q1_otp_comments'),
                q1_dpme_coordinator_comments=get_key_value_or_default(fields, 'q1_dpme_coordinator_comments'),
                q1_treasury_comments=get_key_value_or_default(fields, 'q1_treasury_comments'),

                q2_target=get_key_value_or_default(fields, 'q2_target'),
                q2_actual_output=get_key_value_or_default(fields, 'q2_actual_output'),
                q2_deviation_reason=get_key_value_or_default(fields, 'q2_deviation_reason'),
                q2_corrective_action=get_key_value_or_default(fields, 'q2_corrective_action'),
                q2_national_comments=get_key_value_or_default(fields, 'q2_national_comments'),
                q2_otp_comments=get_key_value_or_default(fields, 'q2_otp_comments'),
                q2_dpme_coordinator_comments=get_key_value_or_default(fields, 'q2_dpme_coordinator_comments'),
                q2_treasury_comments=get_key_value_or_default(fields, 'q2_treasury_comments'),

                q3_target=get_key_value_or_default(fields, 'q3_target'),
                q3_actual_output=get_key_value_or_default(fields, 'q3_actual_output'),
                q3_deviation_reason=get_key_value_or_default(fields, 'q3_deviation_reason'),
                q3_corrective_action=get_key_value_or_default(fields, 'q3_corrective_action'),
                q3_national_comments=get_key_value_or_default(fields, 'q3_national_comments'),
                q3_otp_comments=get_key_value_or_default(fields, 'q3_otp_comments'),
                q3_dpme_coordinator_comments=get_key_value_or_default(fields, 'q3_dpme_coordinator_comments'),
                q3_treasury_comments=get_key_value_or_default(fields, 'q3_treasury_comments'),

                q4_target=get_key_value_or_default(fields, 'q4_target'),
                q4_actual_output=get_key_value_or_default(fields, 'q4_actual_output'),
                q4_deviation_reason=get_key_value_or_default(fields, 'q4_deviation_reason'),
                q4_corrective_action=get_key_value_or_default(fields, 'q4_corrective_action'),
                q4_national_comments=get_key_value_or_default(fields, 'q4_national_comments'),
                q4_otp_comments=get_key_value_or_default(fields, 'q4_otp_comments'),
                q4_dpme_coordinator_comments=get_key_value_or_default(fields, 'q4_dpme_coordinator_comments'),
                q4_treasury_comments=get_key_value_or_default(fields, 'q4_treasury_comments'),

                annual_target=get_key_value_or_default(fields, 'annual_target'),
                annual_aggregate_output=get_key_value_or_default(fields, 'annual_aggregate_output'),
                annual_pre_audit_output=get_key_value_or_default(fields, 'annual_pre_audit_output'),
                annual_deviation_reason=get_key_value_or_default(fields, 'annual_deviation_reason'),
                annual_corrective_action=get_key_value_or_default(fields, 'annual_corrective_action'),
                annual_otp_comments=get_key_value_or_default(fields, 'annual_otp_comments'),
                annual_national_comments=get_key_value_or_default(fields, 'annual_national_comments'),
                annual_dpme_coordincator_comments=get_key_value_or_default(fields,
                                                                           'annual_dpme_coordincator_comments'),
                annual_treasury_comments=get_key_value_or_default(fields, 'annual_treasury_comments'),
                annual_audited_output=get_key_value_or_default(fields, 'annual_audited_output'),

                sector=get_key_value_or_default(fields, 'sector'),
                programme_name=get_key_value_or_default(fields, 'programme_name'),
                subprogramme_name=get_key_value_or_default(fields, 'subprogramme_name'),
                frequency=[item for item in models.FREQUENCIES if fields['frequency'] in item][0][0],
                type=get_key_value_or_default(fields, 'type'),
                subtype=get_key_value_or_default(fields, 'subtype'),
                mtsf_outcome=get_key_value_or_default(fields, 'mtsf_outcome'),
                cluster=get_key_value_or_default(fields, 'cluster'),
                uid=get_key_value_or_default(fields, 'uid'),
            ) 

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
