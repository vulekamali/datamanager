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


def authorise_upload(path, filename, userid, data_package_name, datastore_token):
    # TODO: get length and md5 without reading the whole thing into memory
    with open(path, 'rb') as fh:
        bytes = fh.read()
        md5 = hashlib.md5(bytes)
        md5_b64 = base64.b64encode(md5.digest())

    authorize_upload_url = "https://openspending-dedicated.vulekamali.gov.za/datastore/"
    authorize_upload_payload = {
        "metadata": {
            "owner": userid,
            "name": data_package_name,
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


def unzip_uploaded_file(obj_to_update):
    relative_path = 'iym/temp_files/'
    zip_file = obj_to_update.file

    with ZipFile(zip_file, 'r') as zip:
        file_name = zip.namelist()[0]
        zip.extractall(path=relative_path)

    original_csv_path = os.path.join(settings.BASE_DIR, relative_path, file_name)

    return original_csv_path


def create_composite_key_using_csv_headers(original_csv_path):
    # Get all the headers to come up with the composite key
    with open(original_csv_path) as original_csv_file:
        reader = csv.DictReader(original_csv_file)
        first_row = next(reader)
        fields = first_row.keys()
        composite_key = list(set(fields) - set(MEASURES))

    return composite_key


def tidy_csv_table(original_csv_path, composite_key):
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

    return table6


def create_data_package(obj_to_update, csv_filename, csv_table):
    userid = "616cdf6f2657070da7d2fa056df55206"
    financial_year = obj_to_update.financial_year.slug

    data_package_title = f"National in-year spending {financial_year}"
    data_package_name = f"national-in-year-spending-{financial_year}"
    data_package_template_path = "iym/data_package/data_package.json"
    base_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOiI2MTZjZGY2ZjI2NTcwNzBkYTdkMmZhMDU2ZGY1NTIwNiIsImV4cCI6MTY4NzQxNDkxOX0._EaRN2Izns3gaKzN4jiVmC1RWic70AaTktcGt6F__Hk"

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as csv_file:
        csv_path = csv_file.name
        etl.tocsv(csv_table, csv_path)

        authorize_query = {
            "jwt": base_token,
            "service": "os.datastore",
            "userid": userid,
        }
        authorize_url = f"https://openspending-dedicated.vulekamali.gov.za/user/authorize?{urlencode(authorize_query)}"
        print('============ aaa ============')
        print(authorize_url)
        print('============ bbb ============')
        r = requests.get(authorize_url)
        print('============ ccc ============')
        print(r)
        print('============ ddd ============')
        r.raise_for_status()
        authorize_result = r.json()
        datastore_token = authorize_result["token"]

        authorise_csv_upload_result = authorise_upload(csv_path, csv_filename, userid, data_package_name,
                                                       datastore_token)
        upload(csv_path, authorise_csv_upload_result['filedata'][csv_filename])

        ##===============================================
        with open(data_package_template_path) as data_package_file:
            data_package = json.load(data_package_file)

        data_package["title"] = data_package_title
        data_package["name"] = data_package_name
        data_package["resources"][0]["name"] = slugify(os.path.splitext(csv_filename)[0])
        data_package["resources"][0]["path"] = csv_filename
        data_package["resources"][0]["bytes"] = os.path.getsize(csv_path)

    return data_package


def upload_data_package(data_package):
    with tempfile.NamedTemporaryFile(mode="w", delete=True) as data_package_file:
        json.dump(data_package, data_package_file)
        data_package_file.flush()
        data_package_path = data_package_file.name
        authorise_data_package_upload_result = authorise_upload(data_package_path, "data_package.json", userid,
                                                                data_package_name, datastore_token)
        data_package_upload_authorisation = authorise_data_package_upload_result['filedata']["data_package.json"]
        upload(data_package_path, data_package_upload_authorisation)

    return data_package_upload_authorisation


def import_uploaded_package(data_package_url):
    import_query = {
        "data_package": data_package_url,
        "jwt": datastore_token
    }
    import_url = f"https://openspending-dedicated.vulekamali.gov.za/package/upload?{urlencode(import_query)}"
    r = requests.post(import_url)

    r.raise_for_status()
    status = r.json()["status"]

    return status


def check_and_update_status(status, data_package_url):
    status_query = {
        "data_package": data_package_url,
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


def process_uploaded_file(obj_id):
    # read file
    obj_to_update = models.IYMFileUpload.objects.get(id=obj_id)

    original_csv_path = unzip_uploaded_file(obj_to_update)

    csv_filename = os.path.basename(original_csv_path)

    composite_key = create_composite_key_using_csv_headers(original_csv_path)

    csv_table = tidy_csv_table(original_csv_path, composite_key)

    data_package = create_data_package(obj_to_update, csv_filename, csv_table)

    data_package_upload_authorisation = upload_data_package(data_package)

    ##===============================================
    # Starting import of uploaded data_package
    data_package_url = data_package_upload_authorisation["upload_url"]
    status = import_uploaded_package(data_package_url)

    ##===============================================

    check_and_update_status(status, data_package_url)

    os.remove(original_csv_path)


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
