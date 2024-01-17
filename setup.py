#!/usr/bin/env python

from os import path

from setuptools import find_packages, setup

from wagtail_localize_git import __version__


# Hack to prevent "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when setup.py exits
# (see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing  # noqa
except ImportError:
    pass

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wagtail-localize-git",
    version=__version__,
    description="Wagtail Localize integration for Git-based translation services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Karl Hobley",
    author_email="karl@torchbox.com",
    url="https://github.com/wagtail/wagtail-localize-git",
    project_urls={
        "Changelog": "https://github.com/wagtail/wagtail-localize-git/blob/main/CHANGELOG.md",  # noqa: E501
    },
    packages=find_packages(),
    include_package_data=True,
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "Framework :: Wagtail :: 3",
        "Framework :: Wagtail :: 4",
    ],
    install_requires=[
        "Django>=3.2,<5.1",
        "Wagtail>=4.1,<6.0",
        "wagtail-localize>=1.0",
        "pygit2>=1.0,<2.0",
        "gitpython>=3.0,<4.0",
        "toml>=0.10,<0.11",
    ],
    extras_require={
        "testing": ["dj-database-url==0.5.0", "freezegun==1.2.2"],
    },
    zip_safe=False,
)
