import sys
from setuptools import setup, find_packages
import glob, subprocess
import os


PROJECT = "Lightning"
ICON = "Lightning"

plist = {
    "CFBundleIconFile" : ICON,
    "CFBundleIdentifier" : "com.smus.%s" % PROJECT,
    "LSUIElement" : 1,
}


setup(
    name = "Lightning",
    version = "0.1",
    packages = find_packages(),
    author = "Boris Smus",
    author_email = "boris@smus.com",
    description = "Lightning linker.",
    license = "",
    keywords = "",
    app = ["Lightning/main.py"],
    data_files = glob.glob("Lightning/*"),
    options = dict(py2app=dict(
        plist=plist,
    )),
    setup_requires=['py2app']
)
