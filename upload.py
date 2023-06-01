# TODO: Use OpenSpending URL base from config


import sys
import requests
from urllib.parse import urlencode
import hashlib
import base64
import time
import os
import tempfile 
import csv
import re
import json
import petl as etl
from decimal import Decimal

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

def authorise_upload(path, filename):
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
    upload_url = f"{ authorisation['upload_url'] }?{ urlencode(upload_query) }"
    upload_headers = {
        "content-type": "application/octet-stream",
        "Content-MD5": authorisation["md5"]
    }
    with open(path, 'rb') as file:
        r = requests.put(upload_url, data=file, headers=upload_headers)
    r.raise_for_status()

if __name__ == '__main__':
    datapackage_template_path = "datapackage/datapackage.json"
    userid = sys.argv[1] # vulekamali is "b9d2af843f3a7ca223eea07fb608e62a"
    base_token = sys.argv[2] # token from local storage ngStorage-jwt
    original_csv_path = sys.argv[3]
    financial_year = sys.argv[4] # in the form 2021-22

    datapackage_title = f"National in-year spending {financial_year}"
    datapackage_name = f"national-in-year-spending-{financial_year}"

    # rewrite the data with without commas, and with only the starting year

    csv_filename = os.path.basename(original_csv_path)

    print("Cleaning CSV")

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

        print("Getting authorisation for datastore")
        authorize_query = {
            "jwt": base_token,
            "service": "os.datastore",
            "userid": userid,
        }
        authorize_url = f"https://openspending-dedicated.vulekamali.gov.za/user/authorize?{ urlencode(authorize_query) }"
        r = requests.get(authorize_url)
        r.raise_for_status()
        authorize_result = r.json()
        datastore_token = authorize_result["token"]

        print(f"Uploading CSV {csv_path}")
        authorise_csv_upload_result = authorise_upload(csv_path, csv_filename)
        upload(csv_path, authorise_csv_upload_result['filedata'][csv_filename])

        ##===============================================
        print("Creating and uploading datapackage.json")
        with open(datapackage_template_path) as datapackage_file:
            datapackage = json.load(datapackage_file)

        datapackage["title"] = datapackage_title
        datapackage["name"] = datapackage_name
        datapackage["resources"][0]["name"] = os.path.splitext(csv_filename)[0]
        datapackage["resources"][0]["path"] = csv_filename
        datapackage["resources"][0]["bytes"] = os.path.getsize(csv_path) 

    with tempfile.NamedTemporaryFile(mode="w", delete=True) as datapackage_file:
        json.dump(datapackage, datapackage_file)
        datapackage_file.flush()
        datapackage_path = datapackage_file.name
        authorise_datapackage_upload_result = authorise_upload(datapackage_path, "datapackage.json")
        datapackage_upload_authorisation = authorise_datapackage_upload_result['filedata']["datapackage.json"]
        upload(datapackage_path, datapackage_upload_authorisation)
        print(f'Datapackage url: {datapackage_upload_authorisation["upload_url"]}')

    ##===============================================
    print("Starting import of uploaded datapackage.")
    datapackage_url = datapackage_upload_authorisation["upload_url"]
    import_query = {
        "datapackage": datapackage_url,
        "jwt": datastore_token
    }
    import_url = f"https://openspending-dedicated.vulekamali.gov.za/package/upload?{ urlencode(import_query) }"
    r = requests.post(import_url)
    print(f"Initial status: {r.text}")
    r.raise_for_status()
    status = r.json()["status"]

    ##===============================================

    status_query = {
        "datapackage": datapackage_url,
    }
    status_url = f"https://openspending-dedicated.vulekamali.gov.za/package/status?{ urlencode(status_query) }"
    print(f"Monitoring status until completion ({status_url}):")
    while status not in ["done", "fail"]:
        time.sleep(5)
        r = requests.get(status_url)
        r.raise_for_status()
        status_result = r.json()
        print(status_result)
        status = status_result["status"]

        if status == "fail":
            print(status_result["error"])