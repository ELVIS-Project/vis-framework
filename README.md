vis
===

A "vertical interval series" analysis program for music21.

Copyright Information:
* All source code is subject to the GNU GPL 3.0 Licence. A copy of this licence is included as doc/GPL.txt.
* All other content is subject to the CC-BY-SA Unported 3.0 Licence. A copy of this licence is included as doc/CC-BY-SA.txt
* All content in the test_corpus directory is subject to the licence in the file test_corpus/test_corpus_licence.txt

Software Dependencies
=====================
vis uses many software libraries to help with analysis. The following version numbers are the versions we use for development, but you may be able to use earlier and later versions too.

- Python 2.7.3
- NumPy 1.6.1
- matplotlib 1.1.0
- PyQt4 4.9.1
- music21 1.4.0 (earlier versions do not work)

Run vis
=======
1. Install the software listed above.
2. Open a terminal emulator.
3. Run this command: `$ python main.py`

Make an Installable Executable File
===================================
We use PyInstaller to create executable versions of vis for Windows and Mac OS X.

Note: If you use Windows, you must have pywin32.

Follow these instructions to make an executable:
1. Download and install PyInstaller.
2. Open a terminal emulator.
3. Change to the PyInstaller directory.
4. Run this command to generate a "spec file":
```
$ python utils/makespec.py -p /Users/christopherantila/Documents/vis/vis_env/lib/python2.7/site-packages -F -w 
--name=vis /Users/christopherantila/Documents/vis/main.py
```
5. Run this command to compile an executable:
```
$ python pyinstaller.py vis/vis.spec
```
6. Look for the compiled file in the vis/dist sub-directory.

```
$ python pyinstaller.py --windowed --name=vis
 --runtime-hook=PyInstaller/loader/rthooks/pyi_rth_encodings.py /path/to/vis/__main__.py
```

