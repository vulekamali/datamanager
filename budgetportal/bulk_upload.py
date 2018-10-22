"""
Admin View for bulk uploading
"""

from django import forms
from django.shortcuts import render
from io import BytesIO
from openpyxl import load_workbook

class FileForm(forms.Form):
    file = forms.FileField()


def bulk_upload_view(request):
    file = None
    valid = None
    rows = None

    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            valid = True
            file = request.FILES['file']
            wb = load_workbook(filename=BytesIO(file.read()))
            ws = wb['Resources']
            rows = ws.rows
            # for row in ws.rows:
            #    for cell in row:

        else:
            valid = False
    else:
        valid = True
        form = FileForm()


    return render(request, "admin/bulk_upload.html", {
        'valid': valid,
        'file': file,
        'form': FileForm(),
        'rows': rows,
    })
