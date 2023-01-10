from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django_q.tasks import Task

from budgetportal.models.government import Department

import uuid


def eqprs_file_path(instance, filename):
    return (
        f"eqprs_uploads/{uuid.uuid4()}/{filename}"
    )


class EQPRSFileUpload(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to=eqprs_file_path)
    # Plain text listing which departments could not be matched and were not imported
    import_report = models.TextField()
    num_imported = models.IntegerField(null=True, default=0,
                                       verbose_name='Number of rows we could import')  # number of rows we could import
    num_not_imported = models.IntegerField(null=True, default=0,
                                           verbose_name='Number of rows we could not import')  # number of rows we could not import
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class Frequency:
    ANNUALLY = "annually"
    QUARTERLY = "quarterly"


FREQUENCIES = (
    (Frequency.ANNUALLY, "Annually"),
    (Frequency.QUARTERLY, "Quarterly"),
)


class Indicator(models.Model):
    """The indicator values available for a indicator in a department in a financial year"""

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="indicator_values")
    indicator_name = models.TextField()

    # OTP stands for Office of the Premier
    # national_comments is provincial only, headed "National Oversight Comments"
    # dpme_comments is national only, headed "DPME Coordinator Comments"
    # treasury_comments is national only, headed "National Treasury Coordinator comments

    q1_target = models.TextField(blank=True)
    q1_actual_output = models.TextField(blank=True)
    q1_deviation_reason = models.TextField(blank=True)
    q1_corrective_action = models.TextField(blank=True)
    q1_national_comments = models.TextField(blank=True)
    q1_otp_comments = models.TextField(blank=True)
    q1_dpme_coordinator_comments = models.TextField(blank=True)
    q1_treasury_comments = models.TextField(blank=True)

    q2_target = models.TextField(blank=True)
    q2_actual_output = models.TextField(blank=True)
    q2_deviation_reason = models.TextField(blank=True)
    q2_corrective_action = models.TextField(blank=True)
    q2_national_comments = models.TextField(blank=True)
    q2_otp_comments = models.TextField(blank=True)
    q2_dpme_coordinator_comments = models.TextField(blank=True)
    q2_treasury_comments = models.TextField(blank=True)

    q3_target = models.TextField(blank=True)
    q3_actual_output = models.TextField(blank=True)
    q3_deviation_reason = models.TextField(blank=True)
    q3_corrective_action = models.TextField(blank=True)
    q3_national_comments = models.TextField(blank=True)
    q3_otp_comments = models.TextField(blank=True)
    q3_dpme_coordinator_comments = models.TextField(blank=True)
    q3_treasury_comments = models.TextField(blank=True)

    q4_target = models.TextField(blank=True)
    q4_actual_output = models.TextField(blank=True)
    q4_deviation_reason = models.TextField(blank=True)
    q4_corrective_action = models.TextField(blank=True)
    q4_national_comments = models.TextField(blank=True)
    q4_otp_comments = models.TextField(blank=True)
    q4_dpme_coordinator_comments = models.TextField(blank=True)
    q4_treasury_comments = models.TextField(blank=True)

    annual_target = models.TextField(blank=True)  # AnnualTarget_Summary2
    annual_aggregate_output = models.TextField(blank=True)  # Preliminary_Summary2
    annual_pre_audit_output = models.TextField(blank=True)  # PrelimaryAudited_Summary2
    annual_deviation_reason = models.TextField(blank=True)
    annual_corrective_action = models.TextField(blank=True)
    annual_otp_comments = models.TextField(blank=True)
    annual_national_comments = models.TextField(blank=True)
    annual_dpme_coordincator_comments = models.TextField(blank=True)
    annual_treasury_comments = models.TextField(blank=True)
    annual_audited_output = models.TextField(blank=True)  # ValidatedAuditedSummary2

    sector = models.TextField(blank=True)
    programme_name = models.TextField(blank=True)
    subprogramme_name = models.TextField(blank=True)
    frequency = models.CharField(max_length=9, choices=FREQUENCIES)
    type = models.TextField(blank=True)
    subtype = models.TextField(blank=True)
    mtsf_outcome = models.TextField(blank=True)
    cluster = models.TextField(blank=True)
    uid = models.TextField(blank=True)

    source = models.ForeignKey(EQPRSFileUpload, on_delete=models.CASCADE, related_name="indicator_values")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
