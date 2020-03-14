"""
Tasks for async work.

Tasks MUST be idempotent.
"""
import logging
import traceback

from django_q.tasks import async_task
from budgetportal import infra_projects
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


class RowError(Exception):
    def __init__(self, message, row_result, row_num):
        super(Exception, self).__init__(message)
        self.row_result = row_result
        self.row_num = row_num


def format_error(error):
    return ("Error:\n%r\n\nTraceback:\n%s\n\nRow:\n%s\n") % (
        error.error,
        error.traceback,
        format_row(error.row),
    )


def format_row(ordered_dict):
    return "\n".join(["%s: %r" % (k, v) for (k, v) in ordered_dict.items()])


def import_irm_snapshot(snapshot_id):
    try:
        snapshot = IRMSnapshot.objects.get(pk=snapshot_id)
        result = infra_projects.import_snapshot(snapshot.file.read(), snapshot.id)
        for row_num, row_result in enumerate(result.rows):
            if row_result.errors:
                raise RowError("Error with row %d" % row_num, row_result, row_num)
        async_task(index_irm_projects, snapshot_id=snapshot_id)
        return {
            "totals": result.totals,
            "validation_errors": [row.validation_error for row in result.rows],
        }
    except RowError as e:
        raise Exception(
            ("Error on row %d: %s\n\n" "Technical details: \n\n" "%s")
            % (e.row_num, e, "\n".join([format_error(e) for e in e.row_result.errors]),)
        )
    except Exception as e:
        raise Exception("Error: %s\n\n%s" % (e, traceback.format_exc()))


def index_irm_projects(snapshot_id):
    return call_command("haystack_update_index", "-r")
