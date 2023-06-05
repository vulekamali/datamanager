from django.contrib.auth.models import User
from django.db import models
from budgetportal.models import FinancialYear
import uuid

QUARTERS = (
    ("Q1", "Q1"),
    ("Q2", "Q2"),
    ("Q3", "Q3"),
    ("Q4", "Q4"),
)


def eqprs_file_path(instance, filename):
    return f"iym_uploads/{uuid.uuid4()}/{filename}"


class IYMFileUpload(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True)
    financial_year = models.ForeignKey(
        FinancialYear, on_delete=models.CASCADE
    )
    latest_quarter = models.CharField(max_length=2, choices=QUARTERS)
    process_completed = models.BooleanField(default=False)
    import_report = models.TextField()
    file = models.FileField(upload_to=eqprs_file_path)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
