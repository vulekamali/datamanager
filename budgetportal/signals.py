from django_q.tasks import async_task
from budgetportal import models, tasks
from django.contrib import messages
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from haystack.signals import BaseSignalProcessor
from .models import InfraProject
from django.db.models import Count


@receiver([post_save], sender=models.IRMSnapshot)
def handle_irm_snapshot_post_save(
    sender, instance, created, raw, using, update_fields, **kwargs
):
    async_task(
        tasks.import_irm_snapshot,
        snapshot_id=instance.id,
        task_name="Import IRM Snappshot file of infrastructue projects",
    )


@receiver([post_delete], sender=models.IRMSnapshot)
def handle_irm_snapshot_post_delete(sender, instance, using, **kwargs):
    InfraProject.objects.annotate(num_snapshots=Count("project_snapshots")).filter(
        num_snapshots=0
    ).delete()
    async_task(
        tasks.index_irm_projects,
        snapshot_id=instance.id,
        task_name="Update infrastructure projects search index following snapshot deletion",
    )
