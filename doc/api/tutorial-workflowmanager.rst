
.. _use_the_workflowmanager:

Tutorial: Use the WorkflowManager
---------------------------------
The script developed in :ref:`tutorial-melodic_ngrams` is suitable for users doing exploratory work in an interactive Python shell.
When a query becomes regularized and you want it to be easily repeatable, or if you are an application developer making a graphical interface (whether on the Web or in a desktop application) you can take advantage of a further layer of abstraction offered by our :class:`~vis.workflow.WorkflowManager`.
The :class:`WorkflowManager` is designed as the point of interaction for end-user applications, providing a consistent interface and reference implementations of the steps involved in all queries.
While every new query will involve modifying a portion of the :meth:`run` method's code, you may be able to re-use the existing input and output methods without change.

The :class:`WorkflowManager`'s documentation describes its functionality:

.. autoclass:: vis.workflow.WorkflowManager
    :noindex:

Port a Query into the WorkflowManager
-------------------------------------
Porting an existing query to the :class:`WorkflowManager` involves fitting its code into the appropriate pre-existing methods.
The :meth:`load` method prepares :class:`IndexedPiece` objects and metadata by loading files for analysis.
The :meth:`output` method outputs query results to a variety of formats, including spreadsheets, charts, and scores.
You will not usually need to modify :meth:`load`, and you may not need to modify :meth:`output` either.

The majority of development work will be spent in the :meth:`run` method or its related hidden methods (like the :meth:`_intervs`, :meth:`_inteval_ngrams`, and other methods that are included in the default :class:`WorkflowManager`).

TODO: continue revising here.

When I add my new query's logic to the :meth:`run` method, I get this:

.. code-block:: python
    :linenos:

    def run(self):
        ngram_settings = {'vertical': [0], 'n': self.settigns(None, 'n')}
        ngram_freqs = []

        for i, piece in enumerate(self._data):
            interval_settings = {'quality': self.settings(i, 'interval quality')}
            intervals = piece.get_data( \
                [noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer], \
                interval_settings)
            for part in intervals:
                ngram_freqs.append( \
                    piece.get_data([ngram.NGramIndexer, frequency.FrequencyExperimenter], \
                                   ngram_settings, \
                                   [part]))

        agg_p = AggregatedPieces(ind_ps)
        self._result = agg_p.get_data([aggregator.ColumnAggregator], [], {}, ngram_freqs)

I made the following changes:

* Remove the ``instruction`` parameter from :meth:`run`, since there is only one experiment.
* Use the ``import`` statements at the top of the file.
* Use ``self._data`` rather than building my own list of :class:`IndexedPiece` objects (in :func:`enumerate` on line 5).
* Set ``interval_settings`` per-piece, and use the value from built-in :class:`WorkflowManager` settings.
* Set ``n`` from the built-in :class:`WorkflowManager` settings.

I could also use the :meth:`WorkflowManager.settings` method to get other settings by piece or shared across all pieces, like ``'simple intervals'``, which tells the :class:`HorizontalIntervalIndexer` whether to display all intervals as their single-octave equivalents.

To run the same analysis as in :ref:`tutorial-melodic_ngrams`, use the :class:`WorkflowManager` like this:

.. code-block:: python
    :linenos:

    from vis.workflow import WorkflowManager

    pathnames = [list_of_pathnames]
    work = WorkflowManager(pathnames)
    work.load('pieces')
    for i in xrange(len(work)):
        work.settings(i, 'quality', True)
    work.run()
    work.export('CSV', 'output_filename.csv')

This script actually does more than the program in :ref:`tutorial-melodic_ngrams` because :meth:`export` "converts" the results to a :class:`~pandas.DataFrame`, sorts, and outputs the results.
