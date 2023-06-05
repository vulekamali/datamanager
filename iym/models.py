from django.contrib.auth.models import User
from django.db import models

class IYMFileUpload(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True)
    task_id = models.TextField()
    # Plain text listing which departments could not be matched and were not imported
    import_report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)