"""
Admin View for bulk uploading
"""

from django import forms
from django.shortcuts import render
from django.utils.text import slugify
from io import BytesIO
from openpyxl import load_workbook
from budgetportal.models import (
    Sphere,
    Government,
    Department,
    Dataset,
)
import logging

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

                    government_idx = heading_index['government']
                    department_name_idx = heading_index[u'department_name']
                    dataset_name_idx = heading_index['dataset_name']
                    dataset_title_idx = heading_index['dataset_title']
                    group_id_idx = heading_index['group_id']
                    resource_name_idx = heading_index['resource_name']
                    resource_format_idx = heading_index['resource_format']
                    resource_url_idx = heading_index['resource_url']

                else:
                    row = {}

                    government = Government.objects.filter(
                        sphere=sphere,
                        name=ws_row[government_idx].value
                    )
                    if government:
                        government = government[0]
                        row['government'] = {
                            'object': government,
                            'name': government.name,
                            'status': 'success',
                        }
                    else:
                        row['government'] = {
                            'name': ws_row[government_idx].value,
                            'message': "Government not found for selected sphere",
                            'status': 'error',
                        }

                    if government:
                        department = Department.objects.filter(
                            government=government,
                            name=ws_row[department_name_idx].value
                        )
                        if department:
                            department = department[0]
                            row['department'] = {
                                'object': department,
                                'name': department.name,
                                'status': 'success',
                            }
                        else:
                            row['department'] = {
                                'name': ws_row[department_name_idx].value,
                                'message': "Department not found for specified government",
                                'status': 'error',
                            }
                    else:
                        row['department'] = {
                            'name': ws_row[department_name_idx].value,
                            'message': "Can't look up department without government",
                            'status': 'error',
                        }

                    if department:
                        dataset = department.get_dataset(
                            name=slugify(ws_row[dataset_name_idx].value),
                            group_name=ws_row[group_id_idx].value
                        )
                        if dataset:
                            row['dataset'] = {
                                'object': dataset,
                                'name': dataset.slug,
                                'title': dataset.name,
                                'status': 'success',
                                'message': "This dataset already exists",
                            }
                        else:
                            dataset = Dataset.fetch(
                                slugify(ws_row[dataset_name_idx].value)
                            )
                            if dataset:
                                row['dataset'] = {
                                    'object': dataset,
                                    'name': dataset.slug,
                                    'title': dataset.name,
                                    'new_title': ws_row[dataset_title_idx].value,
                                    'status': 'info',
                                    'message': ("Dataset by this name exists but it "
                                                "is not configured correctly. It "
                                                "will be updated to be associated "
                                                "with this department."),
                                }
                            else:
                                row['dataset'] = {
                                    'name': slugify(ws_row[dataset_name_idx].value),
                                    'title': ws_row[dataset_title_idx].value,
                                    'status': 'success',
                                    'message': "This dataset will be created.",
                                }
                    else:
                        row['dataset'] = {
                            'name': slugify(ws_row[dataset_name_idx].value),
                            'title': ws_row[dataset_title_idx].value,
                            'status': 'error',
                            'message': ("Department not found. We can't "
                                        "upload the dataset until we can "
                                        "associate it with an existing department."),
                        }

                    row.update({
                        'group': {
                            'name': slugify(ws_row[group_id_idx].value),
                        },
                        'resource': {
                            'name': ws_row[resource_name_idx].value,
                            'format': ws_row[resource_format_idx].value,
                            'url': ws_row[resource_url_idx].value,
                            'valid': True,
                        },
                    })
                    self.rows.append(row)
