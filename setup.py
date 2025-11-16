#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

VERSION = 'v0.6.1'
PACKAGE_NAME = 'lcr_api_2'
HERE = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_URL = ('https://github.com/SpencerMKSmith/LCR-API-2/archive/'
                '{}.zip'.format(VERSION))

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

REQUIRES = [
    "requests>=2,<3",
    "selenium>=4.0,<5",
    "webdriver_manager>=3.0,<4",
]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    license='MIT License',
    download_url=DOWNLOAD_URL,
    author='Spencer Smith',
    author_email='spencermksmith@gmail.com',
    description='An API for the LDS churches Leader and Clerk Resources (LCR),',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SpencerMKSmith/LCR-API-2',
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=REQUIRES,
    test_suite='tests',
)
