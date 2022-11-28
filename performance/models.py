from django.db import models
from django.contrib.postgres.fields import JSONField
from budgetportal.models.government import Department
from django_q.tasks import Task
from django.contrib.auth.models import User


def eqprs_file_path(instance, filename):
    return (
        f"eqprs_uploads/{uuid.uuid4()}/{filename}"
    )


class EQPRSFileUpload(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField(upload_to=eqprs_file_path)
    file_validation_report = JSONField()
    # Plain text listing which departments could not be matched and were not imported
    import_report = models.TextField()
    num_imported = models.IntegerField(null=True) # number of rows we could import
    num_not_imported = models.IntegerField(null=True) # number of rows we could not import


class Frequency:
    ANNUALLY = "annually"
    QUARTERLY = "quarterly"


FREQUENCIES = (
    (Frequency.ANNUALLY, "Annually"),
    (Frequency.QUARTERLY, "Quarterly"),
)


class Indicator(models.Model):
    """The indicator values available for a indicator in a department in a financial year"""

    class Meta:
        unique_together = [('department', 'indicator_name')]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="indicator_values")
    indicator_name = models.TextField()

    # OTP stands for Office of the Premier
    # national_comments is provincial only, headed "National Oversight Comments"
    # dpme_comments is national only, headed "DPME Coordinator Comments"
    # treasury_comments is national only, headed "National Treasury Coordinator comments

    q1_target = models.TextField(blank=True)
    q1_actual_outcome = models.TextField(blank=True)
    q1_deviation_reason = models.TextField(blank=True)
    q1_corrective_action = models.TextField(blank=True)
    q1_national_comments = models.TextField(blank=True)
    q1_otp_comments = models.TextField(blank=True)
    q1_dpme_coordinator_comments = models.TextField(blank=True)
    q1_treasury_comments = models.TextField(blank=True)

    q2_target = models.TextField(blank=True)
    q2_actual_outcome = models.TextField(blank=True)
    q2_deviation_reason = models.TextField(blank=True)
    q2_corrective_action = models.TextField(blank=True)
    q2_national_comments = models.TextField(blank=True)
    q2_otp_comments = models.TextField(blank=True)
    q2_dpme_coordinator_comments = models.TextField(blank=True)
    q2_treasury_comments = models.TextField(blank=True)

    q3_target = models.TextField(blank=True)
    q3_actual_outcome = models.TextField(blank=True)
    q3_deviation_reason = models.TextField(blank=True)
    q3_corrective_action = models.TextField(blank=True)
    q3_national_comments = models.TextField(blank=True)
    q3_otp_comments = models.TextField(blank=True)
    q3_dpme_coordinator_comments = models.TextField(blank=True)
    q3_treasury_comments = models.TextField(blank=True)

    q4_target = models.TextField(blank=True)
    q4_actual_outcome = models.TextField(blank=True)
    q4_deviation_reason = models.TextField(blank=True)
    q4_corrective_action = models.TextField(blank=True)
    q4_national_comments = models.TextField(blank=True)
    q4_otp_comments = models.TextField(blank=True)
    q4_dpme_coordinator_comments = models.TextField(blank=True)
    q4_treasury_comments = models.TextField(blank=True)

    sector = models.TextField(blank=True)
    programme_name = models.TextField(blank=True)
    subprogramme_name = models.TextField(blank=True)
    frequency = models.CharField(max_length=9, choices=FREQUENCIES)
    type = models.TextField(blank=True)
    subtype = models.TextField(blank=True)
    mtsf_outcome = models.TextField(blank=True)
    uid = models.TextField(blank=True)

    source = models.ForeignKey(EQPRSFileUpload, on_delete=models.CASCADE, related_name="indicator_values")
