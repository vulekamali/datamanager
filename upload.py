import sys
import requests
from urllib.parse import urlencode
import hashlib
import base64
import time
import logging

logger = logging.getLogger(__name__)


datapackage_path = sys.argv[2]
base_token = sys.argv[1]
userid = "b9d2af843f3a7ca223eea07fb608e62a"

# token from local storage ngStorage-jwt
# GET https://openspending-dedicated.vulekamali.gov.za/user/authorize?jwt=eyJ0eXAiOiJ...Jidc0Z2RISR5to0&service=os.datastore
# Response {"permissions": {"datapackage-upload": true }, "service": "os.datastore", "token": "eyJ0eXAiOiJKV1QiLCJhbG...gchTaijz-7DQ", "userid": "b9d2af843f3a7ca223eea07fb608e62a"}

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

# token from authoriza
# GET https://openspending-dedicated.vulekamali.gov.za/datastore/info?jwt=eyJ0eXAiOiJKV1Qi...A_mgchTaijz-7DQ
# Response {"prefixes": ["http://s3.eu-west-1.amazonaws.com:80/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "http://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "http://openspending-vulekamali:80/b9d2af843f3a7ca223eea07fb608e62a", "http://openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "https://s3.eu-west-1.amazonaws.com:443/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "https://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "https://openspending-vulekamali:443/b9d2af843f3a7ca223eea07fb608e62a", "https://openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a"]}

datastore_info_query = { "jwt": datastore_token }
datastore_info_url = f"https://openspending-dedicated.vulekamali.gov.za/datastore/info?{ urlencode(datastore_info_query)}"
r = requests.get(datastore_info_url)
r.raise_for_status()
info_result = r.json()

# POST https://openspending-dedicated.vulekamali.gov.za/datastore/
# auth-token: eyJ0eXAiOiJKV1QiLCJhbG...gchTaijz-7DQ
# Payload {"metadata":{"owner":"b9d2af843f3a7ca223eea07fb608e62a","name":"test-2023","author":"test-2023"},"filedata":{"fiscaltest2.csv":{"md5":"NvO8/F0aNOxhc5Z2a9MH1w==","name":"fiscaltest2.csv","length":94,"type":"application/octet-stream"}}}
# Response {"filedata": {"fiscaltest2.csv": {"md5": "NvO8/F0aNOxhc5Z2a9MH1w==", "name": "fiscaltest2.csv", "length": 94, "upload_url": "https://s3.eu-west-1.amazonaws.com:443/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/fiscaltest2.csv", "upload_query": {"Signature": ["u/mE1gPw12YoyYVov..."], "Expires": ["1685026446"], "AWSAccessKeyId": ["AKIA3LMODSMQDUVA32EH"]}, "type": "application/octet-stream"}}}

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
            "name": "vulindleladata-202122-ytd-quarter4-some-rows-with-spend",
            "author": "vulindleladata-202122-ytd-quarter4-some-rows-with-spend",
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


# PUT https://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/fiscaltest2.csv?Signature=u%2FmE1gPw12YoyYV...Expires=1685026446&AWSAccessKeyId=AKIA3LMODSMQDUVA32EH
# Content-Type: application/octet-stream


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

# POST https://openspending-dedicated.vulekamali.gov.za/datastore/
# auth-token: eyJ0eXAiOiJKV1QiLCJhbG...gchTaijz-7DQ
# Payload {"metadata":{"owner":"b9d2af843f3a7ca223eea07fb608e62a","name":"test-2023","author":"test-2023"},"filedata":{"datapackage.json":{"md5":"WQqSjKoZmhck3uydX+a/dw==","name":"datapackage.json","length":2348,"type":"application/octet-stream"}}}
# Response {"filedata": {"datapackage.json": {"md5": "WQqSjKoZmhck3uydX+a/dw==", "name": "datapackage.json", "length": 2348, "upload_url": "https://s3.eu-west-1.amazonaws.com:443/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/datapackage.json", "upload_query": {"Signature": ["S0IpD6AskJhqExC..."], "Expires": ["1685026447"], "AWSAccessKeyId": ["AKIA3LMODSMQDUVA32EH"]}, "type": "application/octet-stream"}}}


# PUT https://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/datapackage.json?Signature=S0IpD6AskJhq...&Expires=1685026447&AWSAccessKeyId=AKIA3LMODSMQDUVA32EH
# Content-Type: application/octet-stream
# Payload see datapackage.json

csv_path = "datapackage/vulindleladata-202122-ytd-quarter4-some-rows-with-spend.csv"
csv_filename = "vulindleladata-202122-ytd-quarter4-some-rows-with-spend.csv"
authorise_csv_upload_result = authorise_upload(csv_path, csv_filename)
upload(csv_path, authorise_csv_upload_result['filedata'][csv_filename])

datapackage_path = "datapackage/datapackage.json"
datapackage_filename = "datapackage.json"
authorise_datapackage_upload_result = authorise_upload(datapackage_path, datapackage_filename)
datapackage_upload_authorisation = authorise_datapackage_upload_result['filedata'][datapackage_filename]
upload(datapackage_path, datapackage_upload_authorisation)
print(f'Datapackage url: {datapackage_upload_authorisation["upload_url"]}')

# POST https://openspending-dedicated.vulekamali.gov.za/package/upload?datapackage=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%3A443%2Fopenspending-vulekamali%2Fb9d2af843f3a7ca223eea07fb608e62a%2Ftest-2023%2Fdatapackage.json&jwt=
# Response {"progress": 0, "status": "queued"}

datapackage_url = datapackage_upload_authorisation["upload_url"]
import_query = {
    "datapackage": datapackage_url,
    "jwt": datastore_token
}
import_url = f"https://openspending-dedicated.vulekamali.gov.za/package/upload?{ urlencode(import_query) }"
r = requests.post(import_url)
print(r.text)
r.raise_for_status()

status = r.json()["status"]

# GET https://openspending-dedicated.vulekamali.gov.za/package/status?datapackage=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%3A443%2Fopenspending-vulekamali%2Fb9d2af843f3a7ca223eea07fb608e62a%2Ftest-2023%2Fdatapackage.json
# Response {"progress": 0, "status": "queued"}
# Response {progress: 0.09090909090909091, status: "loading-data"}
# Response {progress: 1, status: "done"}

while status not in ["done", "fail"]:
    time.sleep(5)
    status_query = {
        "datapackage": datapackage_url,
    }
    status_url = f"https://openspending-dedicated.vulekamali.gov.za/package/status?{ urlencode(status_query) }"
    r = requests.get(status_url)
    r.raise_for_status()
    status_result = r.json()
    print(status_result)
    status = status_result["status"]

    if status == "fail":
        print(status_result["error"])