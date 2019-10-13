import argparse
import tempfile

parser = argparse.ArgumentParser(description='Import/update static files from a Webflow export to this project.')
parser.add_argument('webflow_zipfile', help='Path to the .zip file downloaded from Webflow')
parser.add_argument('webflow_ap_dir', help='Path to the Django app where we keep Webflow templates and assets')
args = parser.parse_args()


# Create a ZipFile Object and load sample.zip in it
with ZipFile(args.webflow_zipfile, 'r') as zipObj:
    with tempfile.TemporaryDirectory() as tmpdirname:
        zipObj.extractall(tmpdirname)
