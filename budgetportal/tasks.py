"""
Tasks for async work.

Tasks MUST be idempotent.
"""
import logging
import traceback

import django_q
from budgetportal import prov_infra_projects
from budgetportal.models import Department, IRMSnapshot
from django.conf import settings
from django.core.management import call_command

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


def import_irm_snapshot(snapshot_id):
    row_num = None
    try:
        snapshot = IRMSnapshot.objects.get(pk=snapshot_id)
        result = prov_infra_projects.import_snapshot(snapshot.file.read(), snapshot.id)
        for row_num, row in enumerate(result.rows):
            for error in row.errors:
                logger.error("Row %d: %s" % (row_num, error.error), exc_info=True)
                raise error.error
        django_q.tasks.async(index_irm_projects, snapshot_id=snapshot_id)
        return {
            "totals": result.totals,
            "validation_errors": [row.validation_error for row in result.rows],
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        raise Exception(
            "Error on row %d%s\n\nTechnical details: \n\n%s"
            % (e, row_num, traceback.format_exc())
        )


def index_irm_projects(snapshot_id):
    return call_command("update_index", "-r")
