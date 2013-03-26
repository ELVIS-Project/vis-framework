vis
===

A "vertical interval series" analysis program for music21.

Copyright Information:

All source code is subject to the GNU GPL 3.0 Licence. A copy of this licence is included as GPL.txt.

All other content is subject to the CC-BY-SA Unported 3.0 Licence. A copy of this licence is included as CC-BY-SA.txt

All content in the test_corpus directory is subject to the licence in the file test_corpus/test_corpus_licence.txt

Software Dependencies
=====================
vis uses many software libraries to help with analysis. The following version numbers are the versions we use for development, but you may be able to use earlier and later versions too.

- Python 2.7.3
- SciPy 0.9.0
- NumPy 1.6.1
- matplotlib 1.1.0
- PyQt4 4.9.1
- music21 1.3.0

How to Use
==========
After you installed the dependencies listed in the previous section, open a terminal in the same directory as this README file, and run this command:

`$ python __main__.py`

Stand-alone Executable
======================
To create a Mac application bundle for vis (.app), we use PyInstaller. Download it, and from your
pyinstaller folder, run:

`$ python pyinstaller.py --windowed --name=vis --runtime-hook=PyInstaller/loader/rthooks/pyi_rth_encodings.py /path/to/vis/__main__.py`

In the (newly-created) `dist` folder there will be a file called `vis.app`.
