#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
from shutil import rmtree
from setuptools import setup, Command, find_packages

readme_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README.rst')
with io.open(readme_file, encoding='utf-8') as f:
    long_description = '\n' + f.read()


class TestUploadCommand(Command):
    """Allow testing setup.py upload to testpypi."""

    description = 'Build and publish the package to the test pypi server.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import twine
        except ImportError:
            print('Twine is required for testing uploads')
            sys.exit()

        assert twine

        try:
            print('Removing previous builds…')
            rmtree(os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'dist'))
        except OSError:
            pass

        print('Building Source and Wheel (universal) distribution…')
        os.system('{} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        print('Uploading the package to PyPi via Twine…')
        os.system('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')

        sys.exit()


class UploadCommand(Command):
    """Allow uploading to pypi with setup.py"""

    description = 'Build and publish the package to pypi.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import twine
        except ImportError:
            print('Twine is required for testing uploads')
            sys.exit()

        assert twine

        try:
            print('Removing previous builds…')
            rmtree(os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'dist'))
        except OSError:
            pass

        print('Building Source and Wheel (universal) distribution…')
        os.system('{} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        print('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name="PyTumblr2",
    version="0.2.2",
    description="A Python API v2 wrapper for Tumblr, updated for NPF compliance (and beyond!)",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="nostalgebraist",
    author_email="nostalgebraist@gmail.com",
    url="https://github.com/nostalgebraist/pytumblr",
    packages=find_packages('.'),
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords=['pytumblr', 'pytumblr2', 'tumblr'],
    python_requires=">=3.6",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    test_suite='nose.collector',

    install_requires=[
        'future',
        'requests-oauthlib',
    ],

    tests_require=[
        'nose',
        'nose-cov',
        'mock'
    ],

    cmdclass={
        'testupload': TestUploadCommand,
        'upload': UploadCommand,
    },
)
