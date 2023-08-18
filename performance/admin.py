from django.contrib import admin
from io import StringIO
from performance import models
from django_q.tasks import async_task, fetch

from frictionless import validate

import os
import csv
import budgetportal

VALID_REPORT_TYPES = [
    "Provincial Institutions Oversight Performance  Report",
    "National Institutions Oversight Performance  Report",
]


def generate_import_report(
    report_type_validated, frictionless_report, not_matching_departments
):
    report = ""
    if not report_type_validated:
        report += "Report type must be for one of " + os.linesep
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


def save_imported_indicators(obj_id):
    # read file
    obj_to_update = models.EQPRSFileUpload.objects.get(id=obj_id)
    full_text = obj_to_update.file.read().decode("utf-8")

    # validate report type
    report_type_validated = validate_report_type(full_text, obj_id)
    if not report_type_validated:
        return

    # clean the csv & extract data
    financial_year = get_financial_year(full_text)
    sphere = get_sphere(full_text)
    clean_text = full_text.split("\n", 3)[3]
    f = StringIO(clean_text)
    reader = csv.DictReader(f)
    parsed_data = list(reader)

    # find the objects
    department_government_pairs = set(
        [(x["Institution"], x["Programme"]) for x in parsed_data]
    )  # Programme column in CSV is mislabeled
    num_imported = 0
    total_record_count = len(parsed_data)
    not_matching_departments = set()

    for department, government_name in department_government_pairs:
        if government_name == "National":
            government_name = "South Africa"

        if department.startswith(f"{government_name}: "):
            department = department.replace(f"{government_name}: ", "")

        # clear by department
        models.Indicator.objects.filter(
            department__name=department,
            department__government__name=government_name,
            department__government__sphere__name=sphere,
            department__government__sphere__financial_year__slug=financial_year,
        ).delete()

        # clear by alias
        alias_obj = models.EQPRSDepartmentAlias.objects.filter(
            alias=department,
            department__government__name=government_name,
            department__government__sphere__name=sphere,
            department__government__sphere__financial_year__slug=financial_year,
        ).first()
        if alias_obj:
            models.Indicator.objects.filter(department=alias_obj.department).delete()

    # create new indicators
    for indicator_data in parsed_data:
        frequency = indicator_data["Frequency"]
        government_name = indicator_data["Programme"]
        if government_name == "National":
            government_name = "South Africa"
        department_name = indicator_data["Institution"]
        if department_name.startswith(f"{government_name}: "):
            department_name = department_name.replace(f"{government_name}: ", "")

        department_matches = models.Department.objects.filter(
            name=department_name,
            government__name=government_name,
            government__sphere__name=sphere,
            government__sphere__financial_year__slug=financial_year,
        )

        assert department_matches.count() <= 1
        department_obj = department_matches.first()

        if not department_obj:
            alias_matches = models.EQPRSDepartmentAlias.objects.filter(
                alias=department_name,
                department__government__name=government_name,
                department__government__sphere__name=sphere,
                department__government__sphere__financial_year__slug=financial_year,
            )
            assert alias_matches.count() <= 1
            if len(alias_matches) > 0:
                department_obj = alias_matches.first().department

        if department_obj:
            models.Indicator.objects.create(
                indicator_name=indicator_data["Indicator"],
                department=department_obj,
                source_id=obj_id,
                q1_target=indicator_data["Target_Q1"],
                q1_actual_output=indicator_data["ActualOutput_Q1"],
                q1_deviation_reason=indicator_data["ReasonforDeviation_Q1"],
                q1_corrective_action=indicator_data["CorrectiveAction_Q1"],
                q1_national_comments=indicator_data.get("National_Q1", ""),
                q1_otp_comments=indicator_data.get("OTP_Q1", ""),
                q1_dpme_coordinator_comments=indicator_data.get("OTP_Q1", ""),
                q1_treasury_comments=indicator_data.get("National_Q1", ""),
                q2_target=indicator_data["Target_Q2"],
                q2_actual_output=indicator_data["ActualOutput_Q2"],
                q2_deviation_reason=indicator_data["ReasonforDeviation_Q2"],
                q2_corrective_action=indicator_data["CorrectiveAction_Q2"],
                q2_national_comments=indicator_data.get("National_Q2", ""),
                q2_otp_comments=indicator_data.get("OTP_Q2", ""),
                q2_dpme_coordinator_comments=indicator_data.get("OTP_Q2", ""),
                q2_treasury_comments=indicator_data.get("National_Q2", ""),
                q3_target=indicator_data["Target_Q3"],
                q3_actual_output=indicator_data["ActualOutput_Q3"],
                q3_deviation_reason=indicator_data["ReasonforDeviation_Q3"],
                q3_corrective_action=indicator_data["CorrectiveAction_Q3"],
                q3_national_comments=indicator_data.get("National_Q3", ""),
                q3_otp_comments=indicator_data.get("OTP_Q3", ""),
                q3_dpme_coordinator_comments=indicator_data.get("OTP_Q3", ""),
                q3_treasury_comments=indicator_data.get("National_Q3", ""),
                q4_target=indicator_data["Target_Q4"],
                q4_actual_output=indicator_data["ActualOutput_Q4"],
                q4_deviation_reason=indicator_data["ReasonforDeviation_Q4"],
                q4_corrective_action=indicator_data["CorrectiveAction_Q4"],
                q4_national_comments=indicator_data.get("National_Q4", ""),
                q4_otp_comments=indicator_data.get("OTP_Q4", ""),
                q4_dpme_coordinator_comments=indicator_data.get("OTP_Q4", ""),
                q4_treasury_comments=indicator_data.get("National_Q4", ""),
                annual_target=indicator_data["AnnualTarget_Summary2"],
                annual_aggregate_output="",
                annual_pre_audit_output=indicator_data["PrelimaryAudited_Summary2"],
                annual_deviation_reason=indicator_data["ReasonforDeviation_Summary"],
                annual_corrective_action=indicator_data["CorrectiveAction_Summary"],
                annual_otp_comments=indicator_data.get("OTP_Summary", ""),
                annual_national_comments=indicator_data.get("National_Summary", ""),
                annual_dpme_coordinator_comments=indicator_data.get("OTP_Summary", ""),
                annual_treasury_comments=indicator_data.get("National_Summary", ""),
                annual_audited_output=indicator_data["ValidatedAudited_Summary2"],
                sector=indicator_data["Sector"],
                programme_name=indicator_data[
                    "SubProgramme"
                ],  # SubProgramme column in CSV is mislabeled
                subprogramme_name=indicator_data[
                    "Location"
                ],  # Location column in CSV is mislabeled
                frequency=[i[0] for i in models.FREQUENCIES if i[1] == frequency][0],
                type=indicator_data["Type"],
                subtype=indicator_data["SubType"],
                mtsf_outcome=indicator_data["Outcome"],
                cluster=indicator_data["Cluster"],
                uid=indicator_data["UID"],
            )
            num_imported = num_imported + 1
        else:
            not_matching_departments.add(department_name)

    # update object
    obj_to_update.num_imported = num_imported
    obj_to_update.num_not_imported = total_record_count - num_imported
    obj_to_update.import_report = generate_import_report(
        True, None, not_matching_departments
    )
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


def get_financial_year(full_text):
    financial_year = full_text.split("\n", 1)[1]
    financial_year = financial_year.replace("QPR for FY ", "")
    financial_year = financial_year[: financial_year.index(" ")]
    financial_year = financial_year.strip()

    return financial_year


def get_sphere(full_text):
    line = full_text.split("\n", 2)[1]
    if "Provincial" in line:
        sphere = "Provincial"
    else:
        sphere = "National"

    return sphere


class EQPRSFileUploadAdmin(admin.ModelAdmin):
    exclude = ("num_imported", "import_report", "num_not_imported")
    readonly_fields = (
        "num_imported",
        "import_report",
        "num_not_imported",
        "user",
    )
    list_display = (
        "created_at",
        "user",
        "num_imported",
        "num_not_imported",
        "processing_completed",
        "updated_at",
    )
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "user",
                    "file",
                    "import_report",
                    "num_imported",
                    "num_not_imported",
                )
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return (
                "user",
                "file",
            ) + self.readonly_fields
        return self.readonly_fields

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        response = super(EQPRSFileUploadAdmin, self).render_change_form(
            request, context, add, change, form_url, obj
        )
        response.context_data["title"] = (
            "EQPRS file upload"
            if response.context_data["object_id"]
            else "Upload EQPRS file"
        )
        return response

    def has_change_permission(self, request, obj=None):
        super(EQPRSFileUploadAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        super(EQPRSFileUploadAdmin, self).has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)
        # It looks like the task isn't saved synchronously, so we can't set the
        # task as a related object synchronously. We have to fetch it by its ID
        # when we want to see if it's available yet.

        obj.task_id = async_task(func=save_imported_indicators, obj_id=obj.id)
        obj.save()

    def processing_completed(self, obj):
        task = fetch(obj.task_id)
        if task:
            return task.success

    processing_completed.boolean = True
    processing_completed.short_description = "Processing completed"


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
        "annual_dpme_coordinator_comments",
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
                    "annual_dpme_coordinator_comments",
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


class EQPRSDepartmentAliasAdmin(admin.ModelAdmin):
    list_display = ("alias", "department")
    list_filter = (
        "department__government__sphere__financial_year__slug",
        "department__government__sphere__name",
        "department__government__name",
    )
    search_fields = (
        "department__name",
        "alias",
    )

    autocomplete_fields = ("department",)


admin.site.register(models.EQPRSFileUpload, EQPRSFileUploadAdmin)
admin.site.register(models.Indicator, IndicatorAdmin)
admin.site.register(models.EQPRSDepartmentAlias, EQPRSDepartmentAliasAdmin)
