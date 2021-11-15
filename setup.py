import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = "0.2.0"
PACKAGE_NAME = "sgio"
AUTHOR = "Daniel Goodman"
AUTHOR_EMAIL = ""
URL = ""

LICENSE = ''
DESCRIPTION = ''
LONG_DESCRIPTION = ''
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'construct'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    )

