
.. _tutorial-melodic_ngrams:

Tutorial: Use *N*-Grams to Find Melodic Patterns
------------------------------------------------

Once you understand our framework's architecture (explained in :ref:`design_principles`), you can design new queries to answer your own questions.

Develop a Question
------------------

Our research question involves numerically comparing melodic styles of multiple composers.
To help focus our findings on the differences between *composers*, our test sets should consist of pieces that are otherwise as similar as possible.
One of the best ways to compare styles is using patterns, which are represented in the VIS Framework as *n*-grams: a unit of *n* objects in a row.
While the Framework's *n*-gram functionality is fairly complex, in this tutorial we will focus on simple *n*-grams of melodic intervals, which will help us find melodic patterns.
The most frequently occurring melodic patterns will tell us something about the melodic styles of the composers under consideration: we will be pointed to some similarities and some differences that, taken together, will help us refine future queries.

Since *n*-grams are at the centre of the preliminary investigation described in this tutorial, we will use the corresponding :class:`~vis.analyzers.indexers.ngram.NGramIndexer` to guide our development.
We must answer two questions:

    #. What data will the :class:`NGramIndexer` require to find melodic patterns?
    #. What steps are required after the :class:`NGramIndexer` to produce meaningful results?

We investigate these two questions in the following sections.

What Does the NGramIndexer Require?
-----------------------------------

To begin, try reading the documentation for the :class:`~vis.analyzers.indexers.ngram.NGramIndexer`.
At present, this Indexer is the most powerful and most complicated module in the VIS Framework, and as such it may pose difficulties and behave in unexpected ways.
For this tutorial we focus on the basic functionality: the "n" and "vertical" settings.

TODO: continue revising here

For this simple preliminary investigation, we need only provide the melodic intervals of every part in an :class:`IndexedPiece`.
The melodic intervals will be the "vertical" events; there will be no "horizontal" events.
We can change the "mark_singles" and "continuer" settings any time as we please.
We will probably want to try many different pattern lengths by changing the "n" setting.
If we do not wish our melodic patterns to include rests, we can set "terminator" to ``['Rest']``.

Thus the only information :class:`NGramIndexer` requires from another analyzer is the melodic intervals, produced by :class:`~vis.analyzers.indexers.HorizontalIntervalIndexer`, which will confusingly be the "vertical" event.
As specified in its documentation, the :class:`HorizontalIntervalIndexer` requires the output of the :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer`, which operates directly on the music21 :class:`Score`.

The first part of our query looks like this:

.. code-block:: python
    :linenos:

    from vis.analyzers.indexers import noterest, interval, ngram
    from vis.models.indexed_piece import IndexedPiece

    # prepare inputs and output-collectors
    pathnames = [list_of_pathnames_here]
    ind_ps = [IndexedPiece(x) for x in pathnames]
    interval_settings = {'quality': True}
    ngram_settings = {'vertical': 0, 'n': 3}  # change 'n' as required
    ngram_results = []

    # prepare for and run the NGramIndexer
    for piece in ind_ps:
        intervals = piece.get_data([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer], interval_settings)
        for part in intervals:
            ngram_results.append(piece.get_data([ngram.NGramIndexer], ngram_settings, [part])

After the imports, we start by making a list of all the pathnames to use in this query, then use a Python list comprehension to make a list of :class:`IndexedPiece` objcects for each file.
We make the settings dictionaries to use for the interval then n-gram indexers on lines 7 and 8, but note we have not included all possible settings.
The empty ``ngram_results`` list will store results from the :class:`NGramIndexer`.

The loop started on line 12 is a little confusing: why not use an :class:`AggregatedPieces` object to run the :class:`NGramIndexer` on all pieces with a single call to :meth:`get_data`?
The reason is the inner loop, started on line 14: if we run the :class:`NGramIndexer` on an :class:`IndexedPiece` once, we can only index a single part, but we want results from all parts.
This is the special burden of using the :class:`NGramIndexer`, which is flexible but not (yet) intelligent.
In order to index the melodic intervals in every part using the :meth:`get_data` call on line 15, we must add the nested loops.

How Shall We Prepare Results?
-----------------------------

For this analysis, I will simply count the number of occurrences of each harmonic interval pattern, which is called the "frequency."
It makes sense to calculate each piece separately, then combine the results across pieces.
We'll use the :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter` and :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator` experimenters for these tasks.
The :class:`FrequencyExperimenter` counts the number of occurrences of every unique token in another index into a :class:`pandas.Series`, and the :class:`ColumnAggregator` combines results across a list of :class:`Series` or a :class:`~pandas.DataFrame` (which it treats as a list of :class:`Series`) into a single :class:`Series`.

With these modifications, our program looks like this:

.. code-block:: python
    :linenos:

    from vis.analyzers.indexers import noterest, interval, ngram
    from vis.analyzers.experimenters import frequency, aggregator
    from vis.models.indexed_piece import IndexedPiece
    from vis.models.aggregated_pieces import AggregatedPieces
    from pandas import DataFrame

    # prepare inputs and output-collectors
    pathnames = [list_of_pathnames_here]
    ind_ps = [IndexedPiece(x) for x in pathnames]
    interval_settings = {'quality': True}
    ngram_settings = {'vertical': [0], 'n': 3}  # change 'n' as required
    ngram_freqs = []

    # prepare for and run the NGramIndexer
    for piece in ind_ps:
        intervals = piece.get_data([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer], interval_settings)
        for part in intervals:
            ngram_freqs.append(piece.get_data([ngram.NGramIndexer, frequency.FrequencyExperimenter], ngram_settings, [part]))

    # aggregate results of all pieces
    agg_p = AggregatedPieces(ind_ps)
    result = agg_p.get_data([aggregator.ColumnAggregator], [], {}, ngram_freqs)
    result = DataFrame({'Frequencies': result})

The first thing to note is that I modified the loop from the previous step by adding the :class:`FrequencyExperimenter` to the :meth:`get_data` call on line 18 that uses the :class:`NGramIndexer`.
As you can see, the aggregation step is actually the easiest; it simply requires we create an :class:`AggregatedPieces` object and call its :meth:`get_data` method with the appropriate input, which is the frequency data we collected in the loop.

On line 22, ``result`` holds a :class:`Series` with all the information we need!
To export your data to one of the supported formats (CSV, Excel, etc.) you must create a :class:`DataFrame` and use one of the methods described in the `pandas documentation <http://pandas.pydata.org/pandas-docs/stable/io.html>`_.
The code on line 23 "converts" ``result`` into a :class:`DataFrame` by giving the :class:`Series` to the :class:`DataFrame` constructor in a dictionary.
The key is the name of the column, which you can change to any value valid as a Python dictionary key.
Since the :class:`Series` holds the frequencies of melodic interval patterns, it makes sense to call the column ``'Frequencies'`` in this case.
You may also wish to sort the results by running ``result.sort()`` before you "convert" to a :class:`DataFrame`.
You can sort in descending order (with the most common events at the top) with ``result.sort(ascending=False)``.

Next Steps
----------

After the preliminary investigation, I would make my query more useful by using the "horizontal" and "vertical" functionality of the :class:`NGramIndexer` to coordinate disparate musical elements that make up melodic identity.
Writing a new :class:`Indexer` to help combine melodic intervals with the duration of the note preceding the interval would be relatively easy, since music21 knows the duration of every note.
A more subtle, but possibly more informative, query would combine melodic intervals with the scale degree of the preceding note.
This is a much more complicated query, since it would require an indexer to find the key at a particular moment (an extremely complicated question) and an indexer that knows the scale degree of a note.
