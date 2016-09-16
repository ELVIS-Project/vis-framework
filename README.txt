The VIS Framework
=================

The VIS Framework for Music Analysis

[![Build Status](https://travis-ci.org/ELVIS-Project/vis-framework.svg?branch=master)](https://travis-ci.org/ELVIS-Project/vis-framework)
[![Coverage Status](https://coveralls.io/repos/ELVIS-Project/vis-framework/badge.svg?branch=master&service=github)](https://coveralls.io/github/ELVIS-Project/vis-framework?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/vis-framework.svg)](https://pypi.python.org/pypi/vis-framework/)
[![License](https://img.shields.io/badge/license-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

The VIS Framework is a Python package that uses the music21 and pandas libraries to build a flexible system for writing computational music analysis programs.

Copyright Information:
* All source code is subject to the GNU AGPL 3.0 Licence. A copy of this licence is included as doc/apg-3.0.txt.
* All other content is subject to the CC-BY-SA Unported 3.0 Licence. A copy of this licence is included as doc/CC-BY-SA.txt
* All content in the test_corpus directory is subject to the licence in the file test_corpus/test_corpus_licence.txt

Installation
=====================

There are a number of options for downloading and installing the VIS Framework:

- Clone this GitHub repository
- Download the windows executable file from the latest release
- Download the tar.gz file from the latest release
- Run the pip install vis-framework command in the command line

For developers:

For a new release, you will want to create .exe and .tar.gz files for easy installation. To do so, simply run the following commands in the command line:
python setup.py bdist --format=wininst
python setup.py bdist --format=gztar

Software Dependencies
=====================

The VIS Framework uses many software libraries to help with analysis. These are required dependencies:

- [Python 2.7](https://www.python.org)
- [music21](http://web.mit.edu/music21/)
- [pandas](http://pandas.pydata.org)

These are recommended dependencies:

- numexpr (improved performance for pandas)
- Bottleneck (improved performance for pandas)
- tables (HDF5 output for pandas)
- openpyxl (Excel output for pandas)
- mock (for testing)
- coverage (for testing)
- python-coveralls (to for automated coverage with coveralls.io)
- matplotlib (plotting)
- scipy (plotting)

Documentation
=============

You can find current documentation here:
- [Stable Release Documentation](http://vis-framework.readthedocs.org/en/stable/)
- [Latest Release Documentation](http://vis-framework.readthedocs.org/en/latest/)

Citation
========

If you wish to cite the VIS Framework, please use this ISMIR 2014 article:

Antila, Christopher and Julie Cumming. "The VIS Framework: Analyzing Counterpoint in Large Datasets."
    In Proceedings of the International Society for Music Information Retrieval, 2014.

A BibTeX entry for LaTeX users is:

```
@inproceedings{,
    title = {The VIS Framework: Analyzing Counterpoint in Large Datasets},
    author = {Antila, Christopher and Cumming, Julie},
    booktitle = {Proceedings of the International Society for Music Information Retrieval},
    location = {Taipei, Taiwan},
    year = {2014},
}
```
