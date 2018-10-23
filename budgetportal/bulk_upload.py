"""
Admin View for bulk uploading
"""

from django import forms
# from forms import formset_factory
from django.shortcuts import render
from django.utils.text import slugify
from io import BytesIO
from openpyxl import load_workbook
from budgetportal.models import (
    Sphere,
    Government,
    Department,
)


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
    rows = []

    def __init__(self, sphere, metadata_file):
        wb = load_workbook(filename=BytesIO(metadata_file.read()))
        ws = wb['Resources']
        rows = list(ws.rows)
        headings = rows[0]
        rows = rows[1:]
        heading_index = {}
        for i, cell in enumerate(headings):
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

        for row in rows:
            if not row[government_idx].value:
                continue
            government = Government.objects.get(sphere=sphere,
                                                name=row[government_idx].value)
            department = Department.objects.get(government=government,
                                                name=row[department_name_idx].value)
            self.rows.append({
                'government': {
                    'object': government,
                    'label': government.name,
                },
                'department': {
                    'object': department,
                    'label': department.name,
                },
                'dataset': {
                    'name': slugify(row[dataset_name_idx].value),
                    'label': row[dataset_title_idx].value,
                },
                'group': {
                    'name': slugify(row[group_id_idx].value),
                },
                'resource': {
                    'name': row[resource_name_idx].value,
                    'format': row[resource_format_idx].value,
                    'url': row[resource_url_idx].value,
                    'valid': True,
                },
            })
