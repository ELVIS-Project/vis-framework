.. vis documentation master file, created by
   sphinx-quickstart on Wed Sep 18 00:06:56 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ELVIS_logo-framework.png
    :alt: Logo for the VIS Music Analysis Framework
    :width: 100 %

This is the documentation for the VIS music analysis framework, made available as free software according to the terms of the Affero General Public Licence, version 3 or any later. VIS is a Python package that uses the music21 and pandas libraries to build a ridiculously flexible and preposterously easy system for writing computer music analysis programs. The developers hope to lower the barrier to empirical music analysis to the point that North American music theorists feel compelled to use techniques common among scientists since the 1980s. The VIS framework was produced by the McGill University team of the ELVIS Project. Learn more about the project at our website, http://elvisproject.ca.

About This Documentation
------------------------

Who Should Read This Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**If you are a programmer** who wishes to use the ``vis`` Python objects directly, to use the framework as part of another project, or to add functionality to your own instance of the ``vis`` Web app, you should read this document.

**If you are not a programmer**, this document is probably not for you, since we assume readers are fluent with Python. You may still wish to read the :ref:`design_principles` section to get an idea of how to use our framework, but it is still quite technical. If you wish to learn about computer-driven music analysis, if you are looking for help using the ELVIS counterpoint Web app, or if you are looking for research findings produced by the ELVIS Project, you will find these resources on the `ELVIS website <http://elvisproject.ca>`_ when they become available.

What This Documentation Covers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The VIS API documentation explains the framework's architecture, how to install and use the framework, and how to use the built-in analyzer modules.

How to Use This Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**If you are new to VIS**, we recommend you read :ref:`design_principles` and continue through both tutorials.

**If you forgot the basics**, we recommend you read this paragraph. The VIS framework uses two models (:class:`~vis.models.indexed_piece.IndexedPiece` and :class:`~vis.models.aggregated_pieces.AggregatedPieces`) to fetch results for one or multiple pieces, respectively. Use :meth:`metadata` to fetch metadata and :meth:`get_data` to run analyses and fetch results. Call :meth:`get_data` with a list of analyzers to run, and a dictionary with the settings they use. Learn what an analyzer does, what it requires for input, and what settings it uses by reading the class documentation. Learn the output format of an analyzer by reading the :meth:`run` documentation.

**If you have a question about an analyzer**, learn what it does, what it requires for input, and what settings it uses by reading the class documentation. Learn the output format by reading the :meth:`run` documentation.

.. important:: Remember to have a lot of fun.

Use the ``vis`` Framework
-------------------------
.. toctree::
    :maxdepth: 2

    about


API Specification
-----------------
.. toctree::
   :maxdepth: 3

   modules


Indices and Tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
