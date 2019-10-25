from budgetportal import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
import django_q
from budgetportal import tasks


@receiver([post_save], sender=models.IRMSnapshot)
def handle_irm_snapshot_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    django_q.tasks.async(tasks.import_irm_snapshot, snapshot_id=instance.id)
