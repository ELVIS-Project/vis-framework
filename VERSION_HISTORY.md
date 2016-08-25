VERSION HISTORY
===============
This file records version-to-version changes in the VIS Framework. The most recent versions are at
the top of the file.

* 2.4.1:
    - Cosmetic changes to more closely comply with Python coding conventions.

* 2.4.0:
    - Deprecates n-gram indexer.
    - Adds new_ngram indexer and accompanying tests.
    - Removes version ranges for scipy and matplotlib, and replaces them with specific versions.
    - Minor change to dissonance indexer to avoid issues when dissonances are not preceded by a legal dissonance.
    - Increases testing coverage for dissonance indexer.

* 2.3.1:
    - Importing no longer uses/stores cached pickle files.
    - WorkflowManager.output() produces many table-format results if "count frequency" is False.
    - WorkflowManager.output() changes the column name for table-like outputs, according to the experiment.
    - stops checking midi files for some of the checks.
    - interval indexer improvements
    - required_score_type can now be a list of pandas.dataframes.
* 2.3.0:
    - support for interval direction, i.e. an 'M3' is a '-M3' if the interval is between two voices that are crossed with respect to their staff position
    - inclusion of experimental qualityControl file in scripts which can be used to make sure that a file can be imported by music21 and to run a basic verification that the parts line up properly
    - begin tracking experimental MedievalNoteRestIndexer script in scripts folder
    - basic testing suite for DissonanceIndexer
    - tons of docs improvements (thanks @maxalbert)
* 2.2.0:
    - Python 3 compatibility.
    - New: hierarchical clustering and dendrogram graphical output with dendrogram.py
    - Refactoring/rewrite: update make_return() method in indexer.py to greatly enhance performance when creating dataframes. Uses pandas.concat() instead of pandas.DataFrame()
    - Refactoring: simplified the way several indexers and experimenters internally set their settings to make their init methods easier to read. Uses .update() instead of making piecemeal changes.
    - Tests: includes 15 new tests in a test suite for the dendrogram.py file and comments out 2 tests in offset.py because they are incompatible with the new version of make_return() as they pass magic mock objects to a be concatenated by pandas.concat().
    - Automated test and code coverage fix
    - cleanup of dependencies/requirements (big thanks to maxalbert, https://github.com/maxalbert)
    - 'scripts' directory for helpful scripts
* 2.1.3
    - can turn on/off multiprocessing
    - fixed issue with Pandas converting strings to floats (or, rather, hacked a solution)
* 2.1.2
    - reverted music21 requirement to pip (not git)
* 2.1.1
    - fixed music21 dependency
* 2.1.0
    - NoteBeatStrengthIndexer and accompanying tests
    - DurationIndexer and accompanying tests
    - Rewrite of indexer.py's stream_indexer
    - Integration of multiprocessing into series_indexer
* 2.0.3
    - added test for fermata indexer
    - now depends on latest music21 which fixed a bug for fermatas associated with rests; music21 >= 2.0.3 < 2.1
* 2.0.2
    - fixed bug that now allows support for music21 >= 1.9.3 < 2.1
* 2.0.1:
    - WorkflowManager didn't output histograms with proper labels, for "interval n-grams."
* 2.0.0:
    - 2014/12/05 at 14h45 (commit e053ccc5a81b0ae49f589c147412d0f936e470ac)
    - Analyzers must now accept and return DataFrame objects.
    - Require pandas 0.14.1 at minimum.
    - Require music21 1.9.3 at minimum.
    - The "R_bar_chart.r" script is now run by an experimenter (GH#283)
    - Documentation upgrades.
* 2.0.0 Release Candidates:
    - 1.99.5: 2014/11/05 at 07h28 (commit f0edf9cdab685ff2da1689e1388379d312dbf80c): Taipei Airport Edition
    - 1.99.4: 2014/10/15 at 23h56 (commit ef89815d971a5934b31ee60afd8eee9fcca5b44e)
    - 1.99.3: 2014/10/15 at 19h18 (commit 855b77b98954609530a53cf50ea02ee6f6e2082b)
    - 1.99.2: 2014/10/10 at 1h23 (commit 1f6e88be6767a6a471006eb2ec70355933c5b101)
    - 1.99.1: 2014/10/10 at 0h41 (commit 3db0533255bc972ca2603f7cbbadf3bff7d3270d)
    - 1.99.0: 2014/10/10 at 0h15 (commit 2253dc1b25a60dabd0a884bbb9cad55c648ad4e8)
* 1.2.6:
    - 2014/08/20 at 19h32 (commit 8fd2280634007b87cbfacaa7d6e58740025126df)
    - Deprecate WorkflowManager.export() in favour of output()
    - Fix: for "simple intervals," compound octaves reduced to octaves, rather than to unison
    - Minor documentation fixes
* 1.2.5:
    - 2014/07/07 at 18h50 (commit 4b9895490d3922f2ac82be5924ab2fc0f2f0e7dc)
    - Allow music21 1.9.x
    - Held sonorities are now correctly labeled in interval n-grams (GitHub issue 305)
    - By default, the WorkflowManager's "continuer" automatically adjusts to 'P1' or '1' depending
      on the "interval quality" setting. (GitHub issue 309).
    - Update OutputLilyPond to its commit 70d134013ed9846f8b5f60220d906c48261c8c08
* 1.2.4:
    - Allow pandas 0.14.x
* 1.2.3:
    - 2014/05/26 at 17h47 (commit 242706391f02795225f0b220011f37b5eb6edf43)
    - Improvements for Sphinx to auto-generate documentation at readthedocs.org
    - Revision to the API's installation instructions, accounting for installation from the PyPI
* 1.2.2:
    - 2014/05/26 at 16h34 (commit a2301c260eaff9b93a752f13d084ed97b96ad3bb)
    - WorkflowManager calculates full path to the "R_bar_chart.r" script at runtime
* 1.2.0:
    - 2014/05/20 at 13h34 (commit 0ab7c375f797085bc66e0ee38ac948803fea3f95)
    - WorkflowManager offers output('LilyPond') with part names on annotation lines
* 1.1.2:
    - include and install the 'outputlilypond' package
* 1.1.0:
    - 2014/05/13 at 13h17 (commit ffa832708611da70ecc667857d4092ed1adf80c1)
    - add LilyPond indexers
    - add support for 'LilyPond' to WorkflowManager.output()
* 1.0.1:
    - minor change so vis-framework will install successfully with pip
* 1.0.0:
    - 2014/03/24 at 01h17 (commit 2ccf5f142b7f75b8fbda82bb6bb29ef071010c5b)
    - initial release on PyPI (the Python Package Index)