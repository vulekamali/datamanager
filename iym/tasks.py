from django.contrib import admin
from iym import models
from io import StringIO
import petl as etl
from decimal import Decimal
from urllib.parse import urlencode
from slugify import slugify
from zipfile import ZipFile
from django.conf import settings
from django_q.tasks import async_task
import logging

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
import datetime

logger = logging.getLogger(__name__)
ckan = settings.CKAN

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
    md5 = hashlib.md5()
    with open(path, "rb") as fh:
        while True:
            bytes = fh.read(1000)
            if not bytes:
                break
            else:
                md5.update(bytes)

    md5_b64 = base64.b64encode(md5.digest())

    authorize_upload_url = f"{settings.OPENSPENDING_HOST}/datastore/"
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
                "length": os.stat(path).st_size,
                "type": "application/octet-stream",
            }
        },
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
        "Content-MD5": authorisation["md5"],
    }
    with open(path, "rb") as file:
        r = requests.put(upload_url, data=file, headers=upload_headers)
    r.raise_for_status()


def unzip_uploaded_file(obj_to_update):
    relative_path = "iym/temp_files/"
    zip_file = obj_to_update.file

    with ZipFile(zip_file, "r") as zip:
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


def authenticate_openspending():
    headers = {"x-api-key": settings.OPENSPENDING_API_KEY}
    url = (
        f"{settings.OPENSPENDING_HOST}/user/authenticate_api_key"
    )
    r = requests.get(url)
    r.raise_for_status()
    return r.json()["token"]


def create_data_package(
    csv_filename,
    csv_table,
    userid,
    data_package_name,
    data_package_title,
    obj_to_update,
):
    data_package_template_path = "iym/data_package/data_package_template.json"
    base_token = authenticate_openspending()

    with tempfile.NamedTemporaryFile(mode="w", delete=True) as csv_file:
        csv_path = csv_file.name
        etl.tocsv(csv_table, csv_path)
        update_import_report(obj_to_update, "Getting authorisation for datastore")

        authorize_query = {
            "jwt": base_token,
            "service": "os.datastore",
            "userid": userid,
        }
        authorize_url = (
            f"{settings.OPENSPENDING_HOST}/user/authorize?{urlencode(authorize_query)}"
        )
        r = requests.get(authorize_url)

        r.raise_for_status()

        authorize_result = r.json()
        if "token" not in authorize_result:
            raise Exception("JWT token is invalid")

        datastore_token = authorize_result["token"]

        update_import_report(obj_to_update, f"Uploading CSV {csv_path}")

        authorise_csv_upload_result = authorise_upload(
            csv_path, csv_filename, userid, data_package_name, datastore_token
        )

        upload(csv_path, authorise_csv_upload_result["filedata"][csv_filename])

        ##===============================================
        update_import_report(obj_to_update, "Creating and uploading datapackage.json")
        with open(data_package_template_path) as data_package_file:
            data_package = json.load(data_package_file)

        data_package["title"] = data_package_title
        data_package["name"] = data_package_name
        data_package["resources"][0]["name"] = slugify(
            os.path.splitext(csv_filename)[0]
        )
        data_package["resources"][0]["path"] = csv_filename
        data_package["resources"][0]["bytes"] = os.path.getsize(csv_path)

    return {"data_package": data_package, "datastore_token": datastore_token}


def upload_data_package(
    data_package, userid, data_package_name, datastore_token, obj_to_update
):
    with tempfile.NamedTemporaryFile(mode="w", delete=True) as data_package_file:
        json.dump(data_package, data_package_file)
        data_package_file.flush()
        data_package_path = data_package_file.name
        authorise_data_package_upload_result = authorise_upload(
            data_package_path,
            "data_package.json",
            userid,
            data_package_name,
            datastore_token,
        )

        data_package_upload_authorisation = authorise_data_package_upload_result[
            "filedata"
        ]["data_package.json"]
        upload(data_package_path, data_package_upload_authorisation)
        update_import_report(
            obj_to_update,
            f'Datapackage url: {data_package_upload_authorisation["upload_url"]}',
        )

    return data_package_upload_authorisation


def import_uploaded_package(data_package_url, datastore_token, obj_to_update):
    import_query = {"datapackage": data_package_url, "jwt": datastore_token}
    import_url = (
        f"{settings.OPENSPENDING_HOST}/package/upload?{urlencode(import_query)}"
    )
    r = requests.post(import_url)
    update_import_report(obj_to_update, f"Initial status: {r.text}")

    r.raise_for_status()
    status = r.json()["status"]

    return status


def update_import_report(obj_to_update, message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    obj_to_update.import_report += f"{now} - {message}" + os.linesep
    obj_to_update.save()


def check_and_update_status(status, data_package_url, obj_to_update):
    last_logged_progress = -1
    status_query = {
        "datapackage": data_package_url,
    }
    status_url = (
        f"{settings.OPENSPENDING_HOST}/package/status?{urlencode(status_query)}"
    )
    update_import_report(
        obj_to_update, f"Monitoring status until completion ({status_url}):"
    )
    while status not in ["done", "fail"]:
        time.sleep(5)
        r = requests.get(status_url)
        r.raise_for_status()
        status_result = r.json()
        new_progress = int(float(status_result["progress"]) * 100)
        if new_progress != last_logged_progress:
            update_status(
                obj_to_update,
                f"loading data ({new_progress}%)",
            )
            update_import_report(
                obj_to_update,
                f"loading data ({new_progress}%)",
            )
            last_logged_progress = new_progress
        status = status_result["status"]

        if status == "fail":
            print(status_result["error"])

    update_status(obj_to_update, status)


def update_status(obj_to_update, status):
    obj_to_update.status = status
    obj_to_update.save()


def process_uploaded_file(obj_id):
    # read file
    obj_to_update = models.IYMFileUpload.objects.get(id=obj_id)
    if obj_to_update.process_completed:
        return
    try:
        update_status(obj_to_update, "process started")
        update_import_report(obj_to_update, "Cleaning CSV")

        financial_year = obj_to_update.financial_year.slug
        userid = settings.OPENSPENDING_USER_ID
        data_package_name = f"national-in-year-spending-{financial_year}{settings.OPENSPENDING_DATASET_CREATE_SUFFIX}"
        data_package_title = f"National in-year spending {financial_year}{settings.OPENSPENDING_DATASET_CREATE_SUFFIX}"

        original_csv_path = unzip_uploaded_file(obj_to_update)

        update_status(obj_to_update, "cleaning data")

        csv_filename = os.path.basename(original_csv_path)

        composite_key = create_composite_key_using_csv_headers(original_csv_path)

        csv_table = tidy_csv_table(original_csv_path, composite_key)

        update_status(obj_to_update, "uploading data")

        func_result = create_data_package(
            csv_filename,
            csv_table,
            userid,
            data_package_name,
            data_package_title,
            obj_to_update,
        )

        data_package = func_result["data_package"]
        datastore_token = func_result["datastore_token"]

        data_package_upload_authorisation = upload_data_package(
            data_package, userid, data_package_name, datastore_token, obj_to_update
        )

        ##===============================================
        # Starting import of uploaded data_package
        update_status(obj_to_update, "import queued")
        update_import_report(obj_to_update, "Starting import of uploaded datapackage.")
        data_package_url = data_package_upload_authorisation["upload_url"]
        status = import_uploaded_package(
            data_package_url, datastore_token, obj_to_update
        )

        ##===============================================

        check_and_update_status(status, data_package_url, obj_to_update)

        os.remove(original_csv_path)

        create_or_update_dataset(
            obj_to_update,
            financial_year,
            userid,
            data_package_name,
            obj_to_update.latest_quarter,
        )

        obj_to_update.process_completed = True
        obj_to_update.save()
    except Exception as e:
        logger.exception("Error processing file")
        update_import_report(obj_to_update, str(e))
        update_status(obj_to_update, "fail")


def create_or_update_dataset(
    obj_to_update, financial_year, userid, data_package_name, latest_quarter
):
    update_import_report(obj_to_update, "CKAN process started")
    vocab_map = get_vocab_map()
    tags = [
        {"vocabulary_id": vocab_map["financial_years"], "name": financial_year},
        {"vocabulary_id": vocab_map["spheres"], "name": "national"},
    ]

    dataset_fields = {
        "title": f"National in-year spending {financial_year}",
        "name": f"national_in_year_spending_{financial_year}",
        "owner_org": "national-treasury",
        "groups": [{"name": "in-year-spending"}],
        "tags": tags,
        "extras": [{"key": "latest_quarter", "value": latest_quarter}],
    }

    query = {"fq": (f"+name:{dataset_fields['name']}")}
    search_response = ckan.action.package_search(**query)

    if search_response["count"] == 0:
        # create dataset and add resource
        update_import_report(obj_to_update, "Creating a new dataset in CKAN")
        response = create_dataset(dataset_fields)
        add_resource(response, dataset_fields, userid, data_package_name)
    else:
        # update dataset
        dataset_fields["id"] = search_response["results"][0]["id"]
        update_import_report(obj_to_update, "Updating the dataset in CKAN")
        response = update_dataset(dataset_fields)


def add_resource(response, dataset_fields, userid, data_package_name):
    query = {"id": response["id"]}

    dataset_data = ckan.action.package_show(**query)

    if len(dataset_data["resources"]) == 0:
        # add resource
        should_add_resource = True
    else:
        should_add_resource = True
        for resource in dataset_data["resources"]:
            if resource["format"] == "OpenSpending API":
                # resource is added - update it
                should_add_resource = False

    if should_add_resource:
        add_resource_to_dataset(dataset_fields, userid, data_package_name)


def create_dataset(dataset_fields):
    response = ckan.action.package_create(**dataset_fields)
    return response


def update_dataset(dataset_fields):
    response = ckan.action.package_patch(**dataset_fields)
    return response


def add_resource_to_dataset(dataset_fields, userid, data_package_name):
    url = (
        f"{settings.OPENSPENDING_HOST}/api/3/cubes/{userid}:{data_package_name}/model/"
    )
    resource_fields = {
        "package_id": dataset_fields["name"],
        "name": data_package_name,
        "url": url,
        "format": "OpenSpending API",
    }
    result = ckan.action.resource_create(**resource_fields)


def get_vocab_map():
    vocab_map = {}
    for vocab in ckan.action.vocabulary_list():
        vocab_map[vocab["name"]] = vocab["id"]

    return vocab_map
