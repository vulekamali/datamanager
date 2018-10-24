"""
Tasks for async work.

Tasks MUST be idempotent.
"""
import logging


logger = logging.getLogger(__name__)


def create_dataset(department_id, name, title, group_name):
    return (department_id, name, title, group_name)
