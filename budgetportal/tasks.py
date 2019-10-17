"""
Tasks for async work.

Tasks MUST be idempotent.
"""
import logging
from budgetportal.models import Department
from django.conf import settings


ckan = settings.CKAN
logger = logging.getLogger(__name__)


def create_dataset(department_id, name, title, group_name):
    department = Department.objects.get(pk=department_id)
    dataset = department.get_dataset(group_name, name)
    if dataset:
        logger.info("Not recreating existing dataset %s", name)
        return {"status": "Already exists", "package": dataset.package}
    else:
        dataset = department.create_dataset(name, title, group_name)
        return {"status": "Created", "package": dataset.package}


def create_resource(department_id, group_name, dataset_name, name, format, url):
    department = Department.objects.get(pk=department_id)
    dataset = department.get_dataset(group_name, dataset_name)
    resource = dataset.get_resource(format, name)
    if resource:
        logger.info(
            "Not recreating existing resource %s %s on dataset %s",
            name,
            format,
            dataset_name,
        )
        return {"status": "Already exists", "resource": resource}
    else:
        resource = dataset.create_resource(name, format, url)
        return {"status": "Created", "package": resource}
