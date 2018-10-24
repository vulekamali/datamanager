"""
Admin View for bulk uploading
"""

from django import forms
from django.shortcuts import render
from io import BytesIO
from openpyxl import load_workbook
from budgetportal.models import (
    Sphere,
    Government,
    Department,
    Dataset,
    Category,
)
import logging
from slugify import slugify

logger = logging.getLogger(__name__)


class FileForm(forms.Form):
    sphere_queryset = Sphere.objects.all()
    sphere = forms.ModelChoiceField(queryset=sphere_queryset, empty_label=None)
    file = forms.FileField()


def bulk_upload_view(request):
    form = None
    file = None
    valid = None
    preview = None

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            valid = True
            sphere = form.cleaned_data['sphere']
            metadata_file = request.FILES['file']
            preview = Preview(sphere, metadata_file)
            form = FileForm(initial = {'sphere': sphere.pk })
        else:
            valid = False
    else:
        valid = True
        form = FileForm()

    return render(request, "admin/bulk_upload.html", {
        'valid': valid,
        'file': file,
        'form': form,
        'preview': preview,
    })


class Preview:

    def __init__(self, sphere, metadata_file):
        self.rows = []

        with BytesIO(metadata_file.read()) as bytes_io:
            wb = load_workbook(filename=bytes_io, read_only=True)
            ws = wb['Resources']

            for row_idx, ws_row in enumerate(ws.rows):
                government = None
                department = None
                dataset = None

                if not ws_row[0].value:
                    continue

                if row_idx == 0:
                    heading_index = {}
                    for i, cell in enumerate(ws_row):
                        if cell.value:
                            heading_index[cell.value] = i

                    resource_name_idx = heading_index['resource_name']
                    resource_format_idx = heading_index['resource_format']
                    resource_url_idx = heading_index['resource_url']

                else:
                    government_name = ws_row[heading_index['government']].value
                    department_name = ws_row[heading_index[u'department_name']].value
                    group_name = max_length_slugify(ws_row[heading_index['group_id']].value)
                    dataset_name = max_length_slugify(ws_row[heading_index['dataset_name']].value)
                    dataset_title = ws_row[heading_index['dataset_title']].value
                    row = {}

                    government, government_preview = self.get_government_preview(
                        government_name,
                        sphere
                    )
                    row['government'] = government_preview
                    department, department_preview = self.get_department_preview(
                        department_name,
                        government
                    )
                    row['department'] = department_preview
                    dataset, dataset_preview = self.get_dataset_preview(
                        dataset_name,
                        dataset_title,
                        group_name,
                        department
                    )
                    row['dataset'] = dataset_preview
                    group, group_preview = self.get_group_preview(group_name)
                    row['group'] = group_preview
                    row.update({
                        'resource': {
                            'name': ws_row[resource_name_idx].value,
                            'format': ws_row[resource_format_idx].value,
                            'url': ws_row[resource_url_idx].value,
                            'valid': True,
                        },
                    })
                    self.rows.append(row)

    @classmethod
    def get_government_preview(cls, government_name, sphere):
        government = None
        government_preview = None

        government = Government.objects.filter(
            sphere=sphere,
            name=government_name
        )
        if government:
            government = government[0]
            government_preview = {
                'object': government,
                'name': government.name,
                'status': 'success',
            }
        else:
            government_preview = {
                'name': government_name,
                'message': "Government not found for selected sphere",
                'status': 'error',
            }
        return government, government_preview

    @classmethod
    def get_department_preview(cls, department_name, government):
        department = None
        department_preview = None

        if government:
            department = Department.objects.filter(
                government=government,
                name=department_name
            )
            if department:
                department = department[0]
                department_preview = {
                    'object': department,
                    'name': department.name,
                    'status': 'success',
                }
            else:
                department_preview = {
                    'name': department_name,
                    'message': "Department not found for specified government",
                    'status': 'error',
                }
        else:
            department_preview = {
                'name': department_name,
                'message': "Can't look up department without government",
                'status': 'error',
            }
        return department, department_preview

    @classmethod
    def get_dataset_preview(cls, dataset_name, dataset_title, group_name, department):
        dataset = None
        dataset_preview = None
        if department:
            dataset = department.get_dataset(
                name=dataset_name,
                group_name=group_name
            )
            if dataset:
                dataset_preview = {
                    'object': dataset,
                    'name': dataset.slug,
                    'title': dataset.name,
                    'status': 'success',
                    'message': "This dataset already exists",
                }
            else:
                dataset = Dataset.fetch(
                    dataset_name
                )
                if dataset:
                    dataset_preview = {
                        'object': dataset,
                        'name': dataset.slug,
                        'title': dataset.name,
                        'new_title':dataset_title,
                        'status': 'info',
                        'message': ("Dataset by this name exists but it "
                                    "is not configured correctly. It "
                                    "will be updated to be associated "
                                    "with this department."),
                    }
                else:
                    dataset_preview = {
                        'name': dataset_name,
                        'title': dataset_title,
                        'status': 'success',
                        'message': "This dataset will be created.",
                    }
        else:
            dataset_preview = {
                'name': dataset_name,
                'title': dataset_title,
                'status': 'error',
                'message': ("Department not found. We can't "
                            "upload the dataset until we can "
                            "associate it with an existing department."),
            }
        return dataset, dataset_preview

    @classmethod
    def get_group_preview(cls, group_name):
        category = None
        group_preview = None
        category = Category.get_by_slug(group_name)
        if category:
            group_preview = {
                'name': category.slug,
                'object': category,
                'status': 'success',
            }
        else:
            group_preview = {
                'name': group_name,
                'status': 'error',
                'message': ("Group not found. Ensure that group exists and "
                            "correct name is used in your metadata."),
            }
        return category, group_preview


def max_length_slugify(value):
    return slugify(value, max_length=85, word_boundary=True)
