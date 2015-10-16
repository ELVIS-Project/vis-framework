.. _design_principles:

Design Principles
=================

Three Simple Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In essence, the VIS Framework is built on three simple components: *analyzers* make music analysis decisions; *models* run analyzers on a score; the *WorkflowManager* determines the order analyzers are run.
In other words, the three components are about analysis decisions, making the decisions happen, and ordering the decision-happening.

Consider this example.
A common task for VIS is to count the number of vertical intervals in a piece of music.
You ask the *WorkflowManager* to run this query.
The *WorkflowManager* knows the steps involved: (1) name the notes in a score, (2) find the vertical intervals between simultaneous notes, and (3) count the number of occurrences of every interval.
For each step, the *WorkflowManager* asks a *model* for results.
The model represents a piece, and it knows, for example, how to find simultaneous events, and how to meaningfully organize the results of an analyzer.
Finally, an *analyzer* makes a single type of music analysis decision, for a single moment.
For example, the analyzer called *IntervalIndexer* takes two note names and determines the interval between them.

For a relatively simple music analysis task like counting the number of vertical intervals, these three components may seem anything *but* simple.
For more complicated music analysis tasks, the Framework's architecture begins to pay off.
Whether finding contrapuntal modules, analyzing harmonic function, or anything else, these components will be enough to get the job done.
To design a new query (say, if you want to label chordal dissonances) you only need to add one analyzer for every analysis decision, then tell the WorkflowManager the order the analyzers should run.
Complicated analysis tasks will always be complicated, but VIS provides a solid, predictable Framework for any task, allowing you to focus on what's special about your query, rather than on making sure you remember how to load pieces properly.

Three Levels of Interaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because of its flexibility, you may choose to interact with the VIS Framework on one of three levels, depending on the flexibility required for your task.

If you simply want to use VIS for one of its built-in queries, like finding vertical intervals or contrapuntal modules, you can use VIS **as a program**.
You may do this through a graphical interface like the `Counterpoint Web App <https://counterpoint.elvisproject.ca>`_ or through the Python shell directly, as described in :ref:`use_as_a_program`.

If the built-in :class:`WorkflowManager` does not provide the workflow you need, but you can still accomplish your query with the built-in analyzers, you can use VIS **as a library**.
For example, you may wish to analyze melodic patterns with *n*-grams, as described in :ref:`tutorial-melodic_ngrams`.

Finally, if your query cannot be implemented using the built-in analyzers, you can use VIS **as a framework**, adding analyzer modules and modifying the :class:`WorkflowManager` as necessary.
For example, you may wish to DO WHATEVER WILL BE DESCRIBED IN THIS CROSS-REF.

A More Detailed Look
=========================

Two Types of Analyzers
^^^^^^^^^^^^^^^^^^^^^^^^^

Analyzers make music analysis decisions.
The VIS Framework has two types of analyzers: indexers and experimenters.

**Indexers** use a :class:`music21.stream.Score`, or a :class:`pandas.DataFrame` from another indexer, to perform a music analytic calculation.
The output of any indexer can be sensibly attached to a specific moment of a piece.
That is, indexers are for events that "happen" at an identifiable time.
Indexers may be relatively simple, like the :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, which accepts an index of the notes and rests in a piece, transforming it into an index of the vertical intervals between all the pairs of parts.
Indexers may also be complicated, like the :class:`~vis.analyzers.indexers.ngram.NGramIndexer`, which accepts at least one index of anything, and outputs an index of successions found therein.
An indexer might tell you scale degrees, the harmonic function of a chord, the figured bass signature of a simultaneity, or the moment of a modulation.

**Experimenters** always start with a :class:`~pandas.DataFrame` produced by another analyzer, producing results that cannot be sensibly attached to a specific moment of a piece.
That is, experimenters are for characteristics of a piece (or movement) as a whole.
Experiments may be relatively simple, like the :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`, which counts the number of occurrences of the objects in a :class:`DataFrame`.
Experimenters may also be complicated, like one that produces a Markov transition model of figured bass signatures.

The distinction between indexers and experimenters helps to organize valid workflows.
Analyses may flow from indexer to indexer, from indexer to experimenter, and from experimenter to experimenter.
However, an analysis may not move from an experimenter to an indexer; once moment-specific information is lost, it cannot be recovered.
(The exception to the rule: indexers may use data from experimenters---as long as they also use data from another indexer or a :class:`Score`).

When designing your own analyzers, we encourage you to avoid the temptation to include many analysis steps in the same analyzer, and instead to follow the design pattern set out with our own analyzers and our :class:`~vis.analyzers.indexers.TemplateIndexer` and :class:`~vis.analyzers.experimenters.TemplateExperimenter`.
Following this design pattern helps ensure your program is easy to test, and therefore more trustworthy.
In addition, you may be able to contribute valuable new analyzer modules that will help other scholars get started with VIS more easily.

If required, you may use an analyzer to run external programs, possibly written in a different programming language.
For example, the :class:`~vis.analyzers.experimenters.barchart.RBarChart` experimenter runs a program in the R language, using the *ggplot2* library to produce a bar chart.
Another example is the :class:`~vis.analyzers.experimenters.lilypond.LilyPondExperimenter`, which uses the external :mod:`outputlilypond` Python module to produce a file for `LilyPond <https://lilypond.org>`_, a C program, which that module calls directly.

Two Types of Models
^^^^^^^^^^^^^^^^^^^^^^^^^

VIS uses two types of models: :class:`~vis.models.indexed_piece.IndexedPiece` and :class:`~vis.models.aggregated_pieces.AggregatedPieces`.
These models represent a single piece (or movement), and a group of pieces (and movements), respectively.
In a typical application, you will write analyzers but never call their methods directly.
On the other hand, you will almost never modify the models, but call their methods very often.
Models know how to run analyzers on the piece or pieces they represent, how to import music21 :class:`Score` objects safely and efficiently, and how to find and access metadata.
The models also perform some level of automated error-handling and data-coordination.
In the future, the models may also help coordinate multiprocessing or results-caching, and they should be able to do this without a change in the API.

.. _known_issues_and_limitations:

Known Issues and Limitations
============================
* Limitation: By default, the vis framework does not use multiprocessing at all. If you install the optional packages for pandas, many of the pandas-based indexers and experimenters will use multi-threading in C. However, there are many opportunities to use multiprocessing where we have yet to do so. While we initially planned for the indexers and experimenters to use multiprocessing, we later decided that the high overhead of multiprocessing in Python means we should leave the multiprocessing implementation up to application developers---the realm of the :class:`~vis.workflow.WorkflowManager`.

* Limitation: For users and developers concerned with counterpoint. The framework currently offers no way to sensitively process voice crossing in contrapuntal modules ("interval n-grams"). "Higher" and "lower" voices are consistently presented in score order. We have planned for several ways to deal with this situation, but the developer assigned to the task is a busy doctoral student and a novice programmer, so the solutions have not been fully implemented yet.
