vis
===

The VIS music analysis framework.

VIS is a Python package that uses the music21 and pandas libraries to build a ridiculously flexible and preposterously easy system for writing computer music analysis programs.

Copyright Information:
* All source code is subject to the GNU AGPL 3.0 Licence. A copy of this licence is included as doc/apg-3.0.txt.
* All other content is subject to the CC-BY-SA Unported 3.0 Licence. A copy of this licence is included as doc/CC-BY-SA.txt
* All content in the test_corpus directory is subject to the licence in the file test_corpus/test_corpus_licence.txt

Software Dependencies
=====================

The VIS framework uses many software libraries to help with analysis. These are required dependencies:

- Python 2.7
- music21
- pandas
- mock (for testing)

These are recommended dependencies:

- numexpr (improved performance for pandas)
- Bottleneck (improved performance for pandas)
- tables (HDF5 output for pandas)
- openpyxl (Excel output for pandas)

Citation
========

To cite the VIS Framework in publications use:

Antila, Christopher and Jamie Klassen. The VIS Framework for Music Analysis. Montréal: The ELVIS Project, 2013. URL https://github.com/ELVIS-Project/vis.

A BibTeX entry for LaTeX users is

```
@Manual{,
    title = {The VIS Framework for Music Analysis},
    author = {Antila, Christopher and Klassen, Jamie},
    organization = {The ELVIS Project},
    location = {Montréal, Québec},
    year = {2013},
    url = {https://github.com/ELVIS-Project/vis},
}
```
