.. _design_principles:

Design Principles
=================
The vis framework has a simple design: write an ``analyzer`` to make an analytic judgment about a piece, then use the built-in ``models`` to ensure analyzers are run in the right order, with the right inputs and settings. Since music analysis is a complex task (really, a complicated complex of tasks), and the vis framework is highly abstracted, our simple design requires much explanation.

Write an Analyzer
-----------------
There are two types of analyzers: indexers and experimenters. Indexers take a :class:`music21.stream.Score` or the result of another indexer, perform a calculation, then produce output that can sensibly be attached to a specific moment of a piece. Indexers may be relatively simple, like the :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, which accepts an index of the notes and rests in a piece and outputs an index of the intervals between all possible part pairs. Indexers may be complicated, like the :class:`~vis.analyzers.indexers.ngram.NGramIndexer`, which accepts at least one index of anything, and outputs an index of successions found therein. An indexer might tell you the scale degrees in a part, or the harmonic function of chords in a score.

Experimenters always accept the result of an indexer or another experimenter, perform a culculation, then produce results that cannot be sensibly attached to a specific moment of a piece. Experimenters may be relatively simple, like the :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`, which accepts any index and counts the number of occurrences of unique objects found within. Experimenters may be complicated, like one that accepts the result of the :class:`FrequencyExperimenter`, then outputs a Markov transition model.

The vis framework ships analyzers for various tasks, but we think most users will extend the framework with their own analyzers.

Use a Model
-----------
The vis framework has two data models. Use :class:`~vis.models.indexed_piece.IndexedPiece` for a single piece and :class:`~vis.models.aggregated_pieces.AggregatedPieces` for pieces as a group. In a typical application, you will write analyzers but never use them directly, and never modify but always use the models. The models know how to run analyzers on the piece or pieces they hold, how to import pieces safely and efficiently, and how to find and access metadata. In the future, the models may support storing results from analyzers in a database so they need not be recalculated for future analyses, use multiprocessing to speed up analyses on multi-core computers, or facilitate transit to and from analyzers in other languages like Haskell. We recommend you use the models to benefit from new features without modifying your programs, since they (should not) change the API.

How to Start
------------
After you install the framework, we recommend you begin with the two tutorials below (refer to :ref:`make_a_new_workflow` and :ref:`use_the_workflowmanager`). When you wish to write a new analyzer, refer to the documentation and source code for the :class:`~vis.analyzers.indexers.template.TemplateIndexer` and :class:`~vis.analyzers.experimenters.template.TemplateExperimenter`.

.. _known_issues_and_limitations:

Known Issues and Limitations
============================
* Limitation: By default, the vis framework does not use multiprocessing at all. If you install the optional packages for pandas, many of the pandas-based indexers and experimenters will use multi-threading in C. However, there are many opportunities to use multiprocessing where we have yet to do so. While we initially planned for the indexers and experimenters to use multiprocessing, we later decided that the high overhead of multiprocessing in Python means we should leave the multiprocessing implementation up to application developers---the realm of the :class:`~vis.workflow.WorkflowManager`.

* Limitation: This is a point of information for users and developers concerned with counterpoint. The framework currently offers no way to sensitively process voice crossing in contrapuntal modules ("interval n-grams"). "Higher" and "lower" voices are consistently presented in score order. We have planned for several ways to deal with this situation, but the developer assigned to the task is a busy doctoral student and a novice programmer, so they have not been fully implemented yet.
