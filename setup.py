# setup.py for the VIS Framework

from distutils.core import setup


setup(
    name = "vis-framework",
    packages = [""],
    version = "1.0.0",
    description = "",
    author = "Christopher Antila",
    author_email = "christopher@antila.ca",
    license = "AGPLv3+",
    url = "http://elvisproject.ca/api",
    download_url = "http://elvisproject.ca/download/framework-latest.tar.xz",
    keywords = [],
    classifiers = [
        "Programming Language :: Python",
        "Natural Language :: English",
        "Development Status :: 5 - Production/Stable",
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
The VIS Music Analysis Framework
--------------------------------

VIS is a Python package that uses the music21 and pandas libraries to build a ridiculously flexible and preposterously easy system for writing computer music analysis programs.
"""
)
