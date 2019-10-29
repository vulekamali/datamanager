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


class ProvInfraProjectSnapshotSignalProcessor(BaseSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        mysuper = super(ProvInfraProjectSnapshotSignalProcessor, self)
        mysuper.handle_save(sender=models.ProvInfraProject, instance=instance.project, **kwargs)

    def handle_delete(self, sender, instance, **kwargs):
        mysuper = super(ProvInfraProjectSnapshotSignalProcessor, self)
        if instance.project.project_snapshots.count():
            mysuper.handle_save(sender=models.ProvInfraProject, instance=instance.project, **kwargs)
        else:
            mysuper.handle_delete(sender=models.ProvInfraProject, instance=instance.project, **kwargs)

    def setup(self):
        post_save.connect(self.handle_save, sender=models.ProvInfraProjectSnapshot)
        post_delete.connect(self.handle_delete, sender=models.ProvInfraProjectSnapshot)

    def teardown(self):
        post_save.disconnect(self.handle_save, sender=models.ProvInfraProjectSnapshot)
        post_delete.disconnect(self.handle_delete, sender=models.ProvInfraProjectSnapshot)
