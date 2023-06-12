from django.contrib import admin
from iym import models
from io import StringIO
import petl as etl
from decimal import Decimal
from urllib.parse import urlencode
from slugify import slugify
from zipfile import ZipFile
from django.conf import settings

import os
import csv
import tempfile
import requests
import hashlib
import base64
import json
import time
import re
import iym

RE_END_YEAR = re.compile(r"/\d+")

MEASURES = [
    "Budget",
    "AdjustmentBudget",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "January",
    "February",
    "March",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
]


def authorise_upload(path, filename, userid, datapackage_name, datastore_token):
    # TODO: get length and md5 without reading the whole thing into memory
    with open(path, 'rb') as fh:
        bytes = fh.read()
        md5 = hashlib.md5(bytes)
        md5_b64 = base64.b64encode(md5.digest())

    authorize_upload_url = "https://openspending-dedicated.vulekamali.gov.za/datastore/"
    authorize_upload_payload = {
        "metadata": {
            "owner": userid,
            "name": datapackage_name,
            "author": "Vulekamali",
        },
        "filedata": {
            filename: {
                "md5": md5_b64,
                "name": filename,
                "length": len(bytes),
                "type": "application/octet-stream"
            }
        }
    }
    authorize_upload_headers = {"auth-token": datastore_token}
    r = requests.post(
        authorize_upload_url,
        json=authorize_upload_payload,
        headers=authorize_upload_headers,
    )
    r.raise_for_status()
    return r.json()


def upload(path, authorisation):
    # Unpack values out of lists
    upload_query = {k: v[0] for k, v in authorisation["upload_query"].items()}
    upload_url = f"{authorisation['upload_url']}?{urlencode(upload_query)}"
    upload_headers = {
        "content-type": "application/octet-stream",
        "Content-MD5": authorisation["md5"]
    }
    with open(path, 'rb') as file:
        r = requests.put(upload_url, data=file, headers=upload_headers)
    r.raise_for_status()


def process_uploaded_file(obj_id):
    # read file
    obj_to_update = models.IYMFileUpload.objects.get(id=obj_id)
    zip_file = obj_to_update.file
    relative_path = 'iym/tempfiles/'

    with ZipFile(zip_file, 'r') as zip:
        file_name = zip.namelist()[0]
        zip.extractall(path=relative_path)

    original_csv_path = os.path.join(settings.BASE_DIR, relative_path, file_name)

    # ======================== copy start ========================

    datapackage_template_path = "iym/datapackage/datapackage.json"
    userid = "616cdf6f2657070da7d2fa056df55206"
    base_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOiI2MTZjZGY2ZjI2NTcwNzBkYTdkMmZhMDU2ZGY1NTIwNiIsImV4cCI6MTY4NzQxNDkxOX0._EaRN2Izns3gaKzN4jiVmC1RWic70AaTktcGt6F__Hk"
    financial_year = obj_to_update.financial_year.slug

    datapackage_title = f"National in-year spending {financial_year}"
    datapackage_name = f"national-in-year-spending-{financial_year}"

    # rewrite the data with without commas, and with only the starting year

    csv_filename = os.path.basename(original_csv_path)

    # Get all the headers to come up with the composite key
    with open(original_csv_path) as original_csv_file:
        reader = csv.DictReader(original_csv_file)
        first_row = next(reader)
        fields = first_row.keys()
        composite_key = list(set(fields) - set(MEASURES))

    table1 = etl.fromcsv(original_csv_path)
    table2 = etl.convert(table1, MEASURES, lambda v: v.replace(",", "."))
    table3 = etl.convert(table2, "Financial_Year", lambda v: RE_END_YEAR.sub("", v))
    table4 = etl.convert(table3, MEASURES, Decimal)

    # Roll up rows with the same composite key into one, summing values together
    # Prefixing each new measure header with "sum" because petl seems to need
    # different headers for aggregation output
    aggregation = {f"sum{measure}": (measure, sum) for measure in MEASURES}
    table5 = etl.aggregate(table4, composite_key, aggregation)

    # Strip sum prefix from aggregation results
    measure_rename = {key: key[3:] for key in aggregation}
    table6 = etl.rename(table5, measure_rename)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as csv_file:
        csv_path = csv_file.name
        etl.tocsv(table6, csv_path)

        authorize_query = {
            "jwt": base_token,
            "service": "os.datastore",
            "userid": userid,
        }
        authorize_url = f"https://openspending-dedicated.vulekamali.gov.za/user/authorize?{urlencode(authorize_query)}"
        r = requests.get(authorize_url)
        r.raise_for_status()
        authorize_result = r.json()
        datastore_token = authorize_result["token"]

        authorise_csv_upload_result = authorise_upload(csv_path, csv_filename, userid, datapackage_name,
                                                       datastore_token)
        upload(csv_path, authorise_csv_upload_result['filedata'][csv_filename])

        ##===============================================
        with open(datapackage_template_path) as datapackage_file:
            datapackage = json.load(datapackage_file)

        datapackage["title"] = datapackage_title
        datapackage["name"] = datapackage_name
        datapackage["resources"][0]["name"] = slugify(os.path.splitext(csv_filename)[0])
        datapackage["resources"][0]["path"] = csv_filename
        datapackage["resources"][0]["bytes"] = os.path.getsize(csv_path)

    with tempfile.NamedTemporaryFile(mode="w", delete=True) as datapackage_file:
        json.dump(datapackage, datapackage_file)
        datapackage_file.flush()
        datapackage_path = datapackage_file.name
        authorise_datapackage_upload_result = authorise_upload(datapackage_path, "datapackage.json", userid,
                                                               datapackage_name, datastore_token)
        datapackage_upload_authorisation = authorise_datapackage_upload_result['filedata']["datapackage.json"]
        upload(datapackage_path, datapackage_upload_authorisation)
        print(f'Datapackage url: {datapackage_upload_authorisation["upload_url"]}')

    ##===============================================
    # Starting import of uploaded datapackage
    datapackage_url = datapackage_upload_authorisation["upload_url"]
    import_query = {
        "datapackage": datapackage_url,
        "jwt": datastore_token
    }
    import_url = f"https://openspending-dedicated.vulekamali.gov.za/package/upload?{urlencode(import_query)}"
    r = requests.post(import_url)

    r.raise_for_status()
    status = r.json()["status"]

    ##===============================================

    status_query = {
        "datapackage": datapackage_url,
    }
    status_url = f"https://openspending-dedicated.vulekamali.gov.za/package/status?{urlencode(status_query)}"
    while status not in ["done", "fail"]:
        time.sleep(5)
        r = requests.get(status_url)
        r.raise_for_status()
        status_result = r.json()
        print(status_result)
        status = status_result["status"]

        if status == "fail":
            print(status_result["error"])

    os.remove(original_csv_path)

    # ======================== copy end ========================


class IYMFileUploadAdmin(admin.ModelAdmin):
    readonly_fields = (
        "import_report",
        "user",
        "process_completed"
    )
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "user",
                    "financial_year",
                    "latest_quarter",
                    "file",
                    "import_report",
                    "process_completed",
                )
            },
        ),
    )
    list_display = (
        "created_at",
        "user",
        "financial_year",
        "latest_quarter",
        "process_completed",
        "updated_at",
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

        process_uploaded_file(obj.id)


admin.site.register(models.IYMFileUpload, IYMFileUploadAdmin)
