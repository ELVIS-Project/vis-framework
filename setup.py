#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               setup.py
# Purpose:                Distutils Information for the VIS Framework
#
# Copyright (C) 2014 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>

Distutils information for the VIS Framework.
"""

from setuptools import setup
import vis  # to get the version numbers
import os # to create file paths

# NOTE: update this from 'vis/__init__.py'
MAJOR = vis._MAJOR
MINOR = vis._MINOR
PATCH = vis._PATCH
VERSION = vis.__version__

setup(
    name = "vis-framework",
    version = VERSION,
    description = "The VIS Framework for Music Analysis",
    author = "Christopher Antila, Ryan Bannon, Marina Cottrell, Jamie Klassen, Reiner Kramer, Alexander Morgan",
    author_email = "christopher@antila.ca",
    license = "AGPLv3+",
    url = "http://elvisproject.ca/api/",
    download_url = 'https://pypi.python.org/packages/source/v/vis-framework/vis-framework-%s.tar.bz2' % VERSION,
    platforms = 'any',
    keywords = ['music', 'music analysis', 'music theory', 'musicology', 'counterpoint'],
    requires = [
        'music21 (== 2.1.2)',
        'pandas (== 0.18.1)',
        'multi_key_dict (== 2.0.3)',
		'requests (== 2.11.1)'
        ],
    install_requires = [
        'music21 == 2.1.2',
        'pandas == 0.18.1',
        'multi_key_dict == 2.0.3',
		'requests == 2.11.1'
        ],
    packages = [
        'vis',
        'vis.models',
        'vis.analyzers',
        'vis.analyzers.indexers',
        'vis.analyzers.experimenters',
        ],
    include_package_data=True,
    #package_data = {'vis': ['scripts/*','corpora/*']},
    classifiers = [
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.5",
        "Natural Language :: English",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    long_description = """\
The VIS Framework for Music Analysis
------------------------------------

VIS is a Python package that uses the music21 and pandas libraries to build a system for writing computer music analysis scripts.
"""
)
