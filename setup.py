import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vulekamali-datamanager",
    version="1.0.0",
    author="OpenUp",
    author_email="webapps@openup.org.za",
    description="Prepare data for user-friendly vulekamali views",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vulekamali/datamanager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
