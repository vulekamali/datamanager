from budgetportal import models, tasks
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_q.tasks import async_task


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
    async_task(
        tasks.index_irm_projects,
        snapshot_id=instance.id,
        task_name="Update infrastructure projects search index following snapshot deletion",
    )
