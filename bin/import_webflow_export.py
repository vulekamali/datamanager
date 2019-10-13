import argparse
import tempfile
from glob import glob
import os
from zipfile import ZipFile
import shutil
from distutils.dir_util import copy_tree


parser = argparse.ArgumentParser(description='Import/update static files from a Webflow export to this project.')
parser.add_argument('webflow_zipfile', help='Path to the .zip file downloaded from Webflow')
parser.add_argument('webflow_app_dir', help='Path to the Django app where we keep Webflow templates and assets')
args = parser.parse_args()


def copy_static_dir(src, dst):
    print(f"Copying {src} to {dst}")
    copy_tree(src, dst)



# Create a ZipFile Object and load sample.zip in it
with ZipFile(args.webflow_zipfile, 'r') as zipObj:
    with tempfile.TemporaryDirectory() as tmp_dir:
        print(f"Extracting {args.webflow_zipfile} to {tmp_dir}")
        zipObj.extractall(tmp_dir)
        for htmlfile in glob(tmp_dir + "/*.html"):
            template_dir = os.path.join(args.webflow_app_dir, "templates/webflow")
            print(f"Copying {htmlfile} to {template_dir}")
            shutil.copy(htmlfile, template_dir)

        copy_static_dir(os.path.join(tmp_dir, "css"),
                        os.path.join(args.webflow_app_dir, "static/css"))
        copy_static_dir(os.path.join(tmp_dir, "js"),
                        os.path.join(args.webflow_app_dir, "static/js"))
        copy_static_dir(os.path.join(tmp_dir, "images"),
                        os.path.join(args.webflow_app_dir, "static/images"))
