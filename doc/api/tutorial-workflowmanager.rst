
.. _use_the_workflowmanager:

Tutorial: Use the WorkflowManager
=================================
The script developed in :ref:`make_a_new_workflow` is suitable for users comfortable with an interactive Python shell.
Application developers making a graphical interface---whether on the Web or in a desktop application---can take advantage of a further layer of abstraction offered by our :class:`~vis.workflow.WorkflowManager`.
Since developers often prefer to separate their user interface code from any of the so-called "business logic," the :class:`WorkflowManager` provides the means by which to connect the "dumb" user interface with the highly-abstracted vis framework.
You can think of the :class:`WorkflowManager` as the true back-end component of your application, and you should expect to rewrite it with every application you develop.

The :class:`WorkflowManager`'s documentation describes its functionality:

.. autoclass:: vis.workflow.WorkflowManager
    :noindex:

Port a Query into the WorkflowManager
-------------------------------------
If I want to port the :ref:`make_a_new_workflow` query to the :class:`WorkflowManager`, I need to fit its functionality into the existing methods.
The :meth:`load`, :meth:`output`, and :meth:`export` methods are all related to preparing :class:`IndexedPiece` objects for analysis and saving or outputting results.
Since my query requires no special treatment in these areas, I will not modify those methods, and all of my changes will be in the :meth:`run` method.

Since my new program only requires one query, I can make a very simple :meth:`run` method and remove the other hidden methods (:meth:`_intervs`, :meth:`_interval_ngrams`, :meth:`_variable_part_modules`, :meth:`_two_part_modules`, and :meth:`_all_part_modules`).
Of course, you may wish to use those methods for inspiration when you build your own queries.
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

To run the same analysis as in :ref:`make_a_new_workflow`, use the :class:`WorkflowManager` like this:

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

This script actually does more than the program in :ref:`make_a_new_workflow` because :meth:`export` "converts" the results to a :class:`~pandas.DataFrame`, sorts, and outputs the results.
