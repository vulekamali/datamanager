"""
Admin View for bulk uploading
"""

from django import forms
from django.shortcuts import render
from io import BytesIO
from openpyxl import load_workbook
from budgetportal.models import (
    Sphere,
)

class FileForm(forms.Form):
    sphere_queryset = Sphere.objects.all()
    sphere = forms.ModelChoiceField(queryset=sphere_queryset, empty_label=None)
    file = forms.FileField()


def bulk_upload_view(request):
    form = None
    file = None
    valid = None
    rows = []

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            valid = True
            form = FileForm(initial = {'sphere': form.cleaned_data['sphere'].pk })
            file = request.FILES['file']
            wb = load_workbook(filename=BytesIO(file.read()))
            ws = wb['Resources']
            for row in ws.rows:
                rows.append([cell for cell in row if cell.value is not None])

        else:
            valid = False
    else:
        valid = True
        form = FileForm()


    return render(request, "admin/bulk_upload.html", {
        'valid': valid,
        'file': file,
        'form': form,
        'rows': rows,
    })
