from django.db import models

from budgetportal.models.government import Department
from django_q.tasks import Task


class EQPRSFileUpload(models.Model):
    task = models.ForeignKey(Task)
    file = models.FileField(upload_to=irm_snapshot_file_path)
    file_validation_report = models.JsonField()


class IndicatorPeriod(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name=indicator_values)
    indicator_name

    phase (Target, ActualOutput, ResonForDeviation, CorrectiveAction, Preliminary, PreliminaryAudited, ValidatedAudited)
    period (Q1, Q2, Q3, Q4, Annual)

    # or

    q1_target
    q1_actual_output
    q1_reason_for_deviation
    q1_corrective_action
    q2_target
    q2_actual_output
    q2_reason_for_deviation
    q2_corrective_action
    q3_...


    value
    sector
    programme_name
    subprogramme_name
    frequency (Annually, Quarterly)
    type
    subtype
    mtsf_outcome
    uid
    source = models.ForeignKey(EQPRSFileUpload, on_delete=models.CASCADE, related_name=IndicatorValues)
