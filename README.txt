The VIS Framework
=================

The VIS Framework for Music Analysis

[![Build Status](https://travis-ci.org/ELVIS-Project/vis.svg?branch=master)](https://travis-ci.org/ELVIS-Project/vis)
[![Coverage Status](https://img.shields.io/coveralls/ELVIS-Project/vis.svg)](https://coveralls.io/r/ELVIS-Project/vis)
[![Latest Version](https://pypip.in/version/vis-framework/badge.svg?text=version)](https://pypi.python.org/pypi/vis-framework/)
[![License](https://pypip.in/license/vis-framework/badge.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

The VIS Framework is a Python package that uses the music21 and pandas libraries to build a ridiculously flexible and preposterously easy system for writing computer music analysis programs.

Copyright Information:
* All source code is subject to the GNU AGPL 3.0 Licence. A copy of this licence is included as doc/apg-3.0.txt.
* All other content is subject to the CC-BY-SA Unported 3.0 Licence. A copy of this licence is included as doc/CC-BY-SA.txt
* All content in the test_corpus directory is subject to the licence in the file test_corpus/test_corpus_licence.txt

Software Dependencies
=====================

The VIS Framework uses many software libraries to help with analysis. These are required dependencies:

- Python 2.7
- music21
- pandas
- mock (for testing)
- coverage (for testing)
- python-coveralls (to for automated coverage with coveralls.io)

These are recommended dependencies:

- numexpr (improved performance for pandas)
- Bottleneck (improved performance for pandas)
- tables (HDF5 output for pandas)
- openpyxl (Excel output for pandas)

Citation
========

If you wish to cite the VIS Framework, please use this ISMIR 2014 article:

Antila, Christopher and Julie Cumming. "The VIS Framework: Analyzing Counterpoint in Large Datasets."
    In Proceedings of the International Society for Music Information Retrieval, 2014.

A BibTeX entry for LaTeX users is

```
@inproceedings{,
    title = {The VIS Framework: Analyzing Counterpoint in Large Datasets},
    author = {Antila, Christopher and Cumming, Julie},
    booktitle = {Proceedings of the International Society for Music Information Retrieval},
    location = {Taipei, Taiwan},
    year = {2014},
}
```

You may also wish to cite the software itself:

Antila, Christopher and Jamie Klassen. The VIS Framework for Music Analysis. Montréal: The ELVIS Project, 2014. URL https://github.com/ELVIS-Project/vis.

A BibTeX entry for LaTeX users is

```
@Manual{,
    title = {The VIS Framework for Music Analysis},
    author = {Antila, Christopher and Klassen, Jamie},
    organization = {The ELVIS Project},
    location = {Montréal, Québec},
    year = {2014},
    url = {https://github.com/ELVIS-Project/vis},
}
```
