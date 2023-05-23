import sys
import requests
from urllib.parse import urlencode
import hashlib
import base64

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

print(authorize_result)

# token from authoriza
# GET https://openspending-dedicated.vulekamali.gov.za/datastore/info?jwt=eyJ0eXAiOiJKV1Qi...A_mgchTaijz-7DQ
# Response {"prefixes": ["http://s3.eu-west-1.amazonaws.com:80/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "http://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "http://openspending-vulekamali:80/b9d2af843f3a7ca223eea07fb608e62a", "http://openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "https://s3.eu-west-1.amazonaws.com:443/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "https://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a", "https://openspending-vulekamali:443/b9d2af843f3a7ca223eea07fb608e62a", "https://openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a"]}

datastore_info_query = { "jwt": datastore_token }
datastore_info_url = f"https://openspending-dedicated.vulekamali.gov.za/datastore/info?{ urlencode(datastore_info_query)}"
r = requests.get(datastore_info_url)
r.raise_for_status()
info_result = r.json()

print(info_result)

# POST https://openspending-dedicated.vulekamali.gov.za/datastore/
# auth-token: eyJ0eXAiOiJKV1QiLCJhbG...gchTaijz-7DQ
# Payload {"metadata":{"owner":"b9d2af843f3a7ca223eea07fb608e62a","name":"test-2023","author":"test-2023"},"filedata":{"fiscaltest2.csv":{"md5":"NvO8/F0aNOxhc5Z2a9MH1w==","name":"fiscaltest2.csv","length":94,"type":"application/octet-stream"}}}
# Response {"filedata": {"fiscaltest2.csv": {"md5": "NvO8/F0aNOxhc5Z2a9MH1w==", "name": "fiscaltest2.csv", "length": 94, "upload_url": "https://s3.eu-west-1.amazonaws.com:443/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/fiscaltest2.csv", "upload_query": {"Signature": ["u/mE1gPw12YoyYVov..."], "Expires": ["1685026446"], "AWSAccessKeyId": ["AKIA3LMODSMQDUVA32EH"]}, "type": "application/octet-stream"}}}

with open(f"datapackage/myfilename.csv", 'rb') as csv_file:
    csv_bytes = csv_file.read()
    csv_md5 = hashlib.md5(csv_bytes)
    csv_md5_b64 = base64.b64encode(csv_md5.digest())

authorize_upload_url = "https://openspending-dedicated.vulekamali.gov.za/datastore/"
authorize_csv_upload_payload = {
    "metadata": {
        "owner": userid,
        "name": "auto-upload-test",
        "author": "auto-upload-test",
    },
    "filedata": {
        "myfilename.csv": {
            "md5": csv_md5_b64,
            "name": "myfilename.csv",
            "length": len(csv_bytes),
            "type": "application/octet-stream"
        }
    }
}
print("authorize_csv_upload_payload", authorize_csv_upload_payload)
authorize_csv_upload_headers = {"auth-token": datastore_token}
r = requests.post(
    authorize_upload_url,
    json=authorize_csv_upload_payload,
    headers=authorize_csv_upload_headers,
)
r.raise_for_status()
authorize_csv_upload_result = r.json()
print("authorize_csv_upload_result", authorize_csv_upload_result)

# PUT https://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/fiscaltest2.csv?Signature=u%2FmE1gPw12YoyYV...Expires=1685026446&AWSAccessKeyId=AKIA3LMODSMQDUVA32EH
# Content-Type: application/octet-stream

# POST https://openspending-dedicated.vulekamali.gov.za/datastore/
# auth-token: eyJ0eXAiOiJKV1QiLCJhbG...gchTaijz-7DQ
# Payload {"metadata":{"owner":"b9d2af843f3a7ca223eea07fb608e62a","name":"test-2023","author":"test-2023"},"filedata":{"datapackage.json":{"md5":"WQqSjKoZmhck3uydX+a/dw==","name":"datapackage.json","length":2348,"type":"application/octet-stream"}}}
# Response {"filedata": {"datapackage.json": {"md5": "WQqSjKoZmhck3uydX+a/dw==", "name": "datapackage.json", "length": 2348, "upload_url": "https://s3.eu-west-1.amazonaws.com:443/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/datapackage.json", "upload_query": {"Signature": ["S0IpD6AskJhqExC..."], "Expires": ["1685026447"], "AWSAccessKeyId": ["AKIA3LMODSMQDUVA32EH"]}, "type": "application/octet-stream"}}}

with open(datapackage_path, 'b') as datapackage_file:
    datapackage_bytes = datapackage_file.read()
    result = hashlib.md5(datapackage_bytes)

# PUT https://s3.eu-west-1.amazonaws.com/openspending-vulekamali/b9d2af843f3a7ca223eea07fb608e62a/test-2023/datapackage.json?Signature=S0IpD6AskJhq...&Expires=1685026447&AWSAccessKeyId=AKIA3LMODSMQDUVA32EH
# Content-Type: application/octet-stream
# Payload see datapackage.json


# POST https://openspending-dedicated.vulekamali.gov.za/package/upload?datapackage=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%3A443%2Fopenspending-vulekamali%2Fb9d2af843f3a7ca223eea07fb608e62a%2Ftest-2023%2Fdatapackage.json&jwt=
# Response {"progress": 0, "status": "queued"}

# GET https://openspending-dedicated.vulekamali.gov.za/package/status?datapackage=https%3A%2F%2Fs3.eu-west-1.amazonaws.com%3A443%2Fopenspending-vulekamali%2Fb9d2af843f3a7ca223eea07fb608e62a%2Ftest-2023%2Fdatapackage.json
# Response {"progress": 0, "status": "queued"}
# Response {progress: 0.09090909090909091, status: "loading-data"}
# Response {progress: 1, status: "done"}

