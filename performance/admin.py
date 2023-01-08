from django.contrib import admin
from io import StringIO
from performance import models
from django_q.tasks import async_task

from frictionless import validate

import os
import csv


def get_key_value_or_default(fields, key):
    if key in fields:
        return fields[key]
    else:
        return ""


VALID_REPORT_TYPES = ['Provincial Institutions Oversight Performance  Report',
                      'National Institutions Oversight Performance  Report']


def generate_import_report(report_type_validated, frictionless_report, not_matching_departments):
    report = ""
    if not report_type_validated:
        report += "Report preamble must be for one of " + os.linesep
        for report_type in VALID_REPORT_TYPES:
            report += f"* {report_type} {os.linesep}"

    if frictionless_report:
        if not frictionless_report.valid:
            for error in frictionless_report.tasks[0].errors:
                report += f"* {error.message} {os.linesep}"

    if len(not_matching_departments) > 0:
        report += "Department names that could not be matched on import : " + os.linesep
        for department in not_matching_departments:
            report += f"* {department} {os.linesep}"

    return report


def save_imported_indicators(parsed_data, obj_id):
    report_departments = set([x[1] for x in parsed_data])
    num_imported = 0
    total_record_count = len(parsed_data)
    not_matching_departments = []

    for department in report_departments:
        department_obj = models.Department.objects.filter(name=department).first()
        models.Indicator.objects.filter(department=department_obj).delete()

    for indicator_data in parsed_data:
        department_name = indicator_data[1]
        department_obj = models.Department.objects.filter(name=department_name).first()

        if department_obj:
            models.Indicator.objects.create(
                indicator_name=indicator_data[6],
                department=department_obj,
                source_id=obj_id,

                q1_target=indicator_data[11],
                q1_actual_output=indicator_data[12],
                q1_deviation_reason=indicator_data[13],
                q1_corrective_action=indicator_data[14],
                q1_national_comments=indicator_data[16],
                q1_otp_comments=indicator_data[15],
                q1_dpme_coordinator_comments='',
                q1_treasury_comments='',

                q2_target=indicator_data[17],
                q2_actual_output=indicator_data[18],
                q2_deviation_reason=indicator_data[19],
                q2_corrective_action=indicator_data[20],
                q2_national_comments=indicator_data[22],
                q2_otp_comments=indicator_data[21],
                q2_dpme_coordinator_comments='',
                q2_treasury_comments='',

                q3_target=indicator_data[23],
                q3_actual_output=indicator_data[24],
                q3_deviation_reason=indicator_data[25],
                q3_corrective_action=indicator_data[26],
                q3_national_comments=indicator_data[28],
                q3_otp_comments=indicator_data[27],
                q3_dpme_coordinator_comments='',
                q3_treasury_comments='',

                q4_target=indicator_data[29],
                q4_actual_output=indicator_data[30],
                q4_deviation_reason=indicator_data[31],
                q4_corrective_action=indicator_data[32],
                q4_national_comments=indicator_data[34],
                q4_otp_comments=indicator_data[33],
                q4_dpme_coordinator_comments='',
                q4_treasury_comments='',

                annual_target=indicator_data[35],
                annual_aggregate_output='',
                annual_pre_audit_output=indicator_data[37],
                annual_deviation_reason=indicator_data[38],
                annual_corrective_action=indicator_data[39],
                annual_otp_comments=indicator_data[40],
                annual_national_comments=indicator_data[41],
                annual_dpme_coordincator_comments='',
                annual_treasury_comments='',
                annual_audited_output=indicator_data[42],

                sector=indicator_data[0],
                programme_name=indicator_data[2],
                subprogramme_name=indicator_data[3],
                frequency=indicator_data[5],
                type=indicator_data[7],
                subtype=indicator_data[8],
                mtsf_outcome=indicator_data[9],
                cluster=indicator_data[10],
                uid=indicator_data[43],
            )
            num_imported = num_imported + 1
        elif department_name not in not_matching_departments:
            not_matching_departments.append(department_name)

    obj_to_update = models.EQPRSFileUpload.objects.get(id=obj_id)

    obj_to_update.num_imported = num_imported
    obj_to_update.num_not_imported = total_record_count - num_imported
    obj_to_update.import_report = generate_import_report(True, None, not_matching_departments)
    obj_to_update.save()


def validate_report_type(full_text, obj_id):
    validated = False
    for report_type in VALID_REPORT_TYPES:
        validated = validated or (report_type in full_text)

    if not validated:
        obj_to_update = models.EQPRSFileUpload.objects.get(id=obj_id)
        obj_to_update.num_imported = None
        obj_to_update.num_not_imported = None
        obj_to_update.import_report = generate_import_report(False, None, [])
        obj_to_update.save()

    return validated


def validate_frictionless(data, obj_id):
    report = validate(data)
    validated = report.valid
    if not validated:
        obj_to_update = models.EQPRSFileUpload.objects.get(id=obj_id)
        obj_to_update.num_imported = None
        obj_to_update.num_not_imported = None
        obj_to_update.import_report = generate_import_report(True, report, [])
        obj_to_update.save()

    return validated


class EQPRSFileUploadAdmin(admin.ModelAdmin):
    exclude = ('num_imported', 'import_report', 'num_not_imported')
    readonly_fields = ('num_imported', 'import_report', 'num_not_imported', 'user')
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
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)
        full_text = obj.file.read().decode('utf-8')
        report_type_validated = validate_report_type(full_text, obj.id)
        if report_type_validated:
            f = StringIO(full_text)
            reader = csv.reader(f, delimiter=',')
            print('============ aaa ============')
            test = csv.DictReader(f)
            for item in test:
                # print(dict(item))
                print(item['ReportTitle'])
            print('============ bbb ============')
            parsed_data = [tuple(row) for row in reader]
            parsed_data = [x for x in parsed_data if x]
            del parsed_data[0:2]  # delete first 3 rows

            frictionless_validated = validate_frictionless(parsed_data, obj.id)
            return
            if frictionless_validated:
                del parsed_data[0]  # delete header row
                task = async_task(func=save_imported_indicators, parsed_data=parsed_data, obj_id=obj.id)

    def success(self, obj):
        if obj.task:
            return obj.task.success
        else:
            return True  # change this

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
