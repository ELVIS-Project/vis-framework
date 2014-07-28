VERSION HISTORY
===============
This file records version-to-version changes in the VIS Framework. The most recent versions are at
the top of the file.


* 2.0.0:
    - Require pandas 0.14.1 at minimum.
    - Require music21 1.9.3 at minimum.
    - etc., ...
* 1.2.5:
    - Allow music21 1.9.x
    - Held sonorities are now correctly labeled in interval n-grams (GitHub issue 305)
    - By default, the WorkflowManager's "continuer" automatically adjusts to 'P1' or '1' depending
      on the "interval quality" setting. (GitHub issue 309).
    - Update OutputLilyPond to its commit 70d134013ed9846f8b5f60220d906c48261c8c08
* 1.2.4:
    - Allow pandas 0.14.x
* 1.2.3:
    - Improvements for Sphinx to auto-generate documentation at readthedocs.org
    - Revision to the API's installation instructions, accounting for installation from the PyPI
* 1.2.2:
    - WorkflowManager calculates full path to the "R_bar_chart.r" script at runtime
* 1.2.0:
    - WorkflowManager offers output('LilyPond') with part names on annotation lines
* 1.1.2:
    - include and install the 'outputlilypond' package
* 1.1.0:
    - add LilyPond indexers
    - add support for 'LilyPond' to WorkflowManager.output()
* 1.0.1:
    - minor change so vis-framework will install successfully with pip
* 1.0.0:
    - initial release on PyPI (the Python Package Index)
