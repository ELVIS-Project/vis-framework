
.. _install_and_test:

Install and Test the Framework
==============================
Install for Deployment
----------------------
You must install the VIS Framework before you use it.
If you will not write extensions for the Framework, you may use ``pip`` to install the package from the Python Package Index (PyPI---`https://pypi.python.org/pypi/vis-framework/ <https://pypi.python.org/pypi/vis-framework/>`_). Run this command::

    $ pip install vis-framework

You may also wish to install some or all of the optional dependencies:

    * ``numexpr`` and ``bottleneck``, which speed up ``pandas``.
    * ``openpyxl``, which allows ``pandas`` to export Excel-format spreadsheets.
    * ``cython`` and ``tables``, which allow ``pandas`` to export HDF5-format binary files.

You may install optional dependencies in the same ways as VIS itself. For example::

    $ pip install numexpr bottleneck

Install for Development
-----------------------
If you wish to install the VIS Framework for development work, we recommend you clone our Git repository from https://github.com/ELVIS-Project/vis/, or even make your own fork on GitHub.
You may also wish to checkout a particular version for development with the "checkout" command, as ``git checkout tags/vis-framework-1.2.3`` or ``git checkout master``.

If you installed git, but you need help to clone a repository, you may find useful information in the `git documentation <http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository>`_.

After you clone the vis repository, you should install its dependencies (currently music21, pandas, and mock), for which we recommend you use ``pip``.
From the main VIS directory, run ``pip install -r requirements.txt`` to automatically download and install the library dependencies as specified in our ``requirements.txt`` file.
We also recommend you run ``pip install -r optional_requirements.txt`` to install several additional packages that improve the speed of pandas and allow additional output formats (Excel, HDF5).
You may need to use ``sudo`` or ``su`` to run pip with the proper privileges.
If you do not have pip installed, use your package manager (the package is probably called ``python-pip``---at least for users of Fedora, Ubuntu, and openSUSE).
If you are one of those unfortunate souls who uses Windows, or worse, Mac OS X, then clearly we come from different planets.
The `pip documentation <http://www.pip-installer.org/en/latest/installing.html>`_ may help you.

During development, you should usually start ``python`` (or ``ipython``, etc.) from within the main "vis" directory to ensure proper importing.

After you install the VIS Framework, we recommend you run our automated tests.
From the main vis directory, run ``python run_tests.py``. Python prints ``.`` for every test that passes, and a large error or warning for every test that fails.
Certain versions of music21 may cause tests to fail; refer to :ref:`known_issues_and_limitations` for more information.

The :class:`~vis.workflow.WorkflowManager` is not required for the framework's operation.
We recommend you use the :class:`WorkflowManager` directly or as an example to write new applications.
The vis framework gives you tools to answer a wide variety of musical questions.
The :class:`WorkflowManager` uses the framework to answer specific questions.
Please refer to :ref:`use_the_workflowmanager` for more information.

Install R and ggplot2 for Graphs (Optional)
--------------------------------------------------

If you wish to produce graphs with the VIS Framework, you must install an R interpreter and the "ggplot2" library.
We use the version 3.0.x series of R.

If you use a "Windows" or "OS X" computer, download a pre-compiled binary from http://cran.r-project.org.
If you use a "Linux" computer (or "BSD," etc.), check your package manager for R 3.0.x.
You may have a problem if you search for "R," since it is a common letter, so we recommend you assume the package is called "R" and try to search only if that does not work.
If your distribution does not provide an R binary, or provides an older version than 3.0.0, install R from source code: http://cran.r-project.org/doc/manuals/r-release/R-admin.html.

In all cases, if you encounter a problem, the R manuals are extensive, but require careful attention.

Your distribution may provide a package for "ggplot" or "ggplot2." The following instructions work for all operating systems:

#. Start R (with superuser privileges, if not on Windows).
#. Run the following command to install ggplot::

    install.packages("ggplot2")

#. Run the following commands to test R and ggplot::

    huron <- data.frame(year=1875:1972, level=as.vector(LakeHuron))
    library(plyr)
    huron$decade <- round_any(huron$year, 10, floor)
    library(ggplot)
    h <- ggplot(huron, aes(x=year))
    h + geom_ribbon(aes(ymin=level-1, ymax=level+1))

Expect to see a chart like this:

.. figure:: geom_ribbon-6.png
    :alt: Ribbon chart produced by the ggplot package in the R language.

    Image credit: taken from the `"ggplot2" documentation <http://docs.ggplot2.org/current/geom_ribbon.html>`_ on 26 November 2013; reused here under the GNU General Public License, version 2.

Quit R. You do not need to save your workspace::

    q()
