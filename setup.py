import setuptools
import os
import sys
from setuptools.command.install import install

VERSION = "0.0.3"

# Send to pypi
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="farmlayers",
    version=VERSION,
    author="Kipling Crossing",
    author_email="kip.crossing@gmail.com",
    description="Helper scripts for fetching and managing basic input layers Farm Mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Open-Source-Agriculture/farmlayers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License", 
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "Shapely==1.*",
        "pylandsat == 0.6.*",
        "geotiff==0.1.*",
        "numpy",
        "geojson",
        "pyshp==2.*",
        "Pillow",
        "elevation",
        "imagecodecs",
    ],

)