from budgetportal import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib import messages
import django_q
from budgetportal import tasks
from haystack.signals import BaseSignalProcessor


@receiver([post_save], sender=models.IRMSnapshot)
def handle_irm_snapshot_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    django_q.tasks.async(tasks.import_irm_snapshot, snapshot_id=instance.id)


@receiver([post_delete], sender=models.IRMSnapshot)
def handle_irm_snapshot_post_delete(sender, instance, using, **kwargs):
    django_q.tasks.async(tasks.index_irm_projects, snapshot_id=instance.id)
