#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/workflow.py
# Purpose:                WorkflowManager
#
# Copyright (C) 2013, 2014, 2015 Christopher Antila, Alexander Morgan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. deprecated:: 3.0.0
    The WorkflowManager is deprecated as of VIS 3.0.0 and will be entirely removed in VIS 4.0. It 
    was an important part of VIS in earlier versions but the iterative caching strategy implemented 
    in VIS 3.0 obviates the need for the WorkflowManager and so it is being phased out for 
    simplicity. Most of its functionality still works with VIS 3.0, however, it is no longer being 
    maintained or supported.

The ``workflow`` module holds the :class:`WorkflowManager`, which automates several common music
analysis patterns for counterpoint. The :class:`TemplateWorkflow` class is a template for writing
new ``WorkflowManager`` classes.
"""

from os import path
from ast import literal_eval
import six
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
import pandas
import vis
from vis.models import indexed_piece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest, interval, offset, repeat
from vis.analyzers.experimenters import frequency, aggregator, barchart

def split_part_combo(key):
    """
    Split a comma-separated list of two integer part names into a tuple of the integers.

    :param str key: String with the part names.
    :returns: The indices of parts referred to by the key.
    :rtype: tuple of int

    >>> split_part_combo('5,6')
    (5, 6)
    >>> split_part_combo('234522,98100')
    (234522, 98100)
    >>> var = split_part_combo('1,2')
    >>> split_part_combo(str(var[0]) + ',' + str(var[1]))
    (1, 2)
    """
    post = key.split(',')
    return int(post[0]), int(post[1])


class WorkflowManager(object):
    """
    Warning: The WorkflowManager is deprecated as of VIS 3.0 and will be entirely removed in 
    VIS 4.0. Most of its functionality still works with VIS 3.0 but this is not guaranteed and it 
    is no longer being supported in development.
    
    :parameter pathnames: A list of pathnames.
    :type pathnames: list or tuple of string or :class:`~vis.models.indexed_piece.IndexedPiece`

    The :class:`WorkflowManager` automates several common music analysis patterns for counterpoint.
    Use the ``WorkflowManager`` with these four tasks:

    * :meth:`load`, to import pieces from symbolic data formats.
    * :meth:`run`, to perform a pre-defined analysis.
    * :meth:`output`, to output analysis results.

    Before you analyze, you may wish to use these methods:

    * :meth:`metadata`, to get or set the metadata of a specific :class:`IndexedPiece` managed by \
        this ``WorkflowManager``.
    * :meth:`settings`, to get or set a setting related to analysis (for example, whether to \
        display the quality of intervals).

    You may also treat a ``WorkflowManager`` as a container:

    >>> wm = WorkflowManager(['piece1.mxl', 'piece2.krn'])
    >>> len(wm)
    2
    >>> ip = wm[1]
    >>> type(ip)
    <class 'vis.models.indexed_piece.IndexedPiece'>
    """

    # Instance Variables
    # - self._data: list of IndexedPieces
    # - self._result: result of the most recent call to run()
    # - self._settings: settings unique per piece
    # - self._shared_settings: settings shared among all piecesd
    # - self._previous_exp: name of the experiments whose results are stored in self._result
    # - self._loaded: whether the load() method has been called
    # - self._R_bar_chart_path: path to the R-language script that makes bar charts

    # names of the experiments available through run()
    # NOTE: do not re-order these, or run() will break
    _experiments_list = ['intervals', 'interval n-grams', 'basic']

    # Error message when users call output() with LilyPond, but they probably called run() with
    # ``count frequency`` set to True.
    _COUNT_FREQUENCY_MESSAGE = 'LilyPond output is not possible after you call run() with ' + \
        '"count frequency" set to True.'

    # The error when we required two-voice pairs, but one of the combinations wasn't a pair.
    _REQUIRE_PAIRS_ERROR = 'All voice combinations must have two parts (found {}).'

    # The error when someone calls output() but there are no results to output.
    _NO_RESULTS_ERROR = 'Please call run() before you call output().'

    # The error when an ``instruction`` arg is invalid
    _UNRECOGNIZED_INSTRUCTION = 'Unrecognized instruction: "{}"'

    # The error when the argument to __init__() isn't a list/tuple of string
    _BAD_INIT_ARG = 'WorkflowManager() requires a list/tuple of strings.'

    def __init__(self, pathnames):
        """
        :raises: :exc:`TypeError` if ``pathnames`` is not a list or tuple of string or \
            :class:`IndexedPiece`
        """
        # ensure ``pathnames`` is a list or tuple of string...
        # this may have security repercussions, as noted in GH#332
        if not (isinstance(pathnames, (list, tuple)) and
                all(map(lambda x: isinstance(x, (six.string_types, indexed_piece.IndexedPiece)), pathnames))):
            raise TypeError(WorkflowManager._BAD_INIT_ARG)

        # create the list of IndexedPiece objects
        self._data = []
        for each_val in pathnames:
            if isinstance(each_val, six.string_types):
                self._data.append(indexed_piece.IndexedPiece(each_val))
            elif isinstance(each_val, indexed_piece.IndexedPiece):
                self._data.append(each_val)

        # hold the IndexedPiece-specific settings
        self._settings = [{} for _ in xrange(len(self._data))]
        for piece_sett in self._settings:
            for sett in ['offset interval', 'voice combinations']:
                piece_sett[sett] = None
            for sett in ['filter repeats']:
                piece_sett[sett] = False

        # hold settings common to all IndexedPieces
        self._shared_settings = {'n': 2, 'continuer': 'dynamic quality', 'mark singles': False,
                                 'interval quality': False, 'simple intervals': False,
                                 'include rests': False, 'count frequency': True}

        # hold the result of the most recent call to run()
        self._result = None
        # which was the most recent experiment run? Either 'intervals' or 'n-grams'
        self._previous_exp = None
        # whether the load() method has been called
        self._loaded = False
        # calculate the bar chart script's path
        # TODO: this moves to barchart.py
        self._R_bar_chart_path = path.join(vis.__path__[0], 'scripts', 'R_bar_chart.r')

    def __len__(self):
        """
        Return the number of pieces stored in this WorkflowManager.
        """
        return len(self._data)

    def __getitem__(self, index):
        """
        Return the IndexedPiece at a particular index.
        """
        return self._data[index]

    def load(self, instruction='pieces', pathname=None):
        """
        Import analysis data from long-term storage on a filesystem. This should primarily be \
        used for the ``'pieces'`` instruction, to control when the initial music21 import \
        happens.

        Use :meth:`load` with an instruction other than ``'pieces'`` to load results from a
        previous analysis run by :meth:`run`.

        .. note:: If one of the files imports as a :class:`music21.stream.Opus`, the number of
            pieces and their order *will* change.

        :parameter str instruction: The type of data to load. Defaults to ``'pieces'``.
        :parameter str pathname: The pathname of the data to import; not required for the \
            ``'pieces'`` instruction.

        :raises: :exc:`RuntimeError` if the ``instruction`` is not recognized.

        **Instructions**

        .. note:: only ``'pieces'`` is implemented at this time.

        * ``'pieces'``, to import all pieces, collect metadata, and run :class:`NoteRestIndexer`
        * ``'hdf5'`` to load data from a previous :meth:`output`.
        * ``'stata'`` to load data from a previous :meth:`output`.
        * ``'pickle'`` to load data from a previous :meth:`output`.
        """
        # TODO: rewrite this with multiprocessing
        # NOTE: you may want to have the worker process create a new IndexedPiece object, import it
        #       and run the NoteRestIndexer, then pickle it and send that to a callback method
        #       that will somehow unpickle it and replace the *data in* the IndexedPieces here, but
        #       not actually replace the IndexedPieces, since that would inadvertently cancel the
        #       client's pointer to the IndexedPieces, if they have one
        if 'pieces' == instruction:
            for i, piece in enumerate(self._data):
                try:
                    piece.get_data([noterest.NoteRestIndexer])
                except indexed_piece.OpusWarning:
                    new_ips = piece.get_data([noterest.NoteRestIndexer], known_opus=True)
                    self._data = self._data[:i] + self._data[i + 1:] + new_ips
        elif 'hdf5' == instruction or 'stata' == instruction or 'pickle' == instruction:
            raise NotImplementedError('The ' + instruction + ' instruction does\'t work yet!')
        else:
            raise RuntimeError('Unrecognized load() instruction: "' + six.u(instruction) + '"')
        self._loaded = True

    def _get_unique_combos(self, index):
        """
        Given the index to a piece held in this WorkflowManager, get a list of all the requested
        voice combinations, ensuring each combination appears only once.

        :raises: :exc:`ValueError` when the user-given voice combination is not valid Python
        """
        # TODO: can this method do more sanitization?
        # The Algorithm (in case you don't want to read it)
        # 1.) get the setting,
        # 2.) turn it into a string,
        # 3.) run literal_eval() to get a list of lists
        # 4.) use map() to convert the sub-lists back into strings (so set() will work)
        # 5.) use set() to remove duplicate sub-lists
        # 6.) use map() to run literal_eval() again to turn the sub-lists back into lists
        VOX_COM = 'voice combinations'
        return list(map(literal_eval, list(set(map(str, literal_eval(str(self.settings(index, VOX_COM))))))))

    def run(self, instruction):
        """
        Run an experiment's workflow. Remember to call :meth:`load` before this method.

        :parameter str instruction: The experiment to run (refer to "List of Experiments" below).

        :returns: The result of the experiment.
        :rtype: :class:`pandas.Series` or :class:`pandas.DataFrame` or a list of lists of
            :class:`pandas.Series`. If ``'count frequency'`` is set to False, the return type will
            be a list of lists of series wherein the containing list has each piece in the
            experiment as its elements (even if there is only one piece in the experiment, this will
            be a list of length one). The contained lists contain the results of the experiment for
            each piece where each element in the list corresponds to a unique voice combination in
            an unlabelled and unpredictable fashion. Finally each series corresponds the experiment
            results for a given voice combination in a given piece.

        :raises: :exc:`RuntimeError` if the ``instruction`` is not valid for this
            :class:`WorkflowManager`.
        :raises: :exc:`RuntimeError` if you have not called :meth:`load`.
        :raises: :exc:`ValueError` if the voice-pair selection is invalid or unset.

        **List of Experiments**

        * ``'intervals'``: find the frequency of vertical intervals in 2-part combinations. All \
            settings will affect analysis *except* ``'n'``. No settings are required; if you do \
            not set ``'voice combinations'``, all two-part combinations are included.
        * ``'interval n-grams'``: find the frequency of n-grams of vertical intervals connected \
            by the horizontal interval of the lowest voice. All settings will affect analysis. \
            You must set the ``'voice combinations'`` setting. The default value for ``'n'`` is \
            ``2``.
        """
        if 'dynamic quality' == self.settings(None, 'continuer'):
            was_dynamic_quality = True
            if self.settings(None, 'interval quality'):
                self.settings(None, 'continuer', 'P1')
            else:
                self.settings(None, 'continuer', '1')
        else:
            was_dynamic_quality = False

        if self._loaded is not True:
            raise RuntimeError('Please call load() before you call run()')
        error_msg = 'WorkflowManager.run() could not parse the instruction'
        post = None
        # run the experiment
        if len(instruction) < min([len(x) for x in WorkflowManager._experiments_list]):
            raise RuntimeError(error_msg)
        if instruction.startswith(WorkflowManager._experiments_list[0]):
            # intervals
            self._previous_exp = WorkflowManager._experiments_list[0]
            post = self._intervs()
        elif instruction.startswith(WorkflowManager._experiments_list[1]):
            # interval n-grams
            self._previous_exp = WorkflowManager._experiments_list[1]
            post = self._interval_ngrams()
        elif instruction.startswith(WorkflowManager._experiments_list[2]):
            # basic indexers (that import info from music21)
            self._previous_exp = WorkflowManager._experiments_list[1]
            post = self._basic()
        else:
            raise RuntimeError(error_msg)
        if was_dynamic_quality:
            self.settings(None, 'continuer', 'dynamic quality')
        self._result = post
        return post

    def _interval_ngrams(self):
        """
        Prepare a list of frequencies of interval n-grams in all pieces.

        This method automatically uses :meth:`_two_part_modules`, :meth:`_all_part_modules`, and
        :meth:`_variable_part_modules` when relevant.

        These indexers and experimenters will be run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`
        * :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        Settings are parsed automatically by piece. If the ``offset interval`` setting has a value,
        :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer` is run with that value. If
        the ``filter repeats`` setting is ``True``, the
        :class:`~vis.analyzers.repeat.FilterByRepeatIndexer` is run (after the offset indexer, if
        relevant).

        :returns: Result of the :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`
            or a list of outputs from :class:`~vis.analyzers.indexers.ngram.NGramIndexer`,
            depending on the ``count frequency`` setting.

        .. note:: To compute more than one value of ``n``, call :meth:`_interval_ngrams` once for
            each value of ``n``.
        """
        self._result = []
        # use helpers to fetch results for each piece
        for i in xrange(len(self._data)):
            if 'all' == self.settings(i, 'voice combinations'):
                self._result.append(self._all_part_modules(i))
            elif 'all pairs' == self.settings(i, 'voice combinations'):
                self._result.append(self._two_part_modules(i))
            else:
                self._result.append(self._variable_part_modules(i))
        # aggregate results across all pieces
        if self.settings(None, 'count frequency'):
            self._run_freq_agg('ngram.NGramIndexer')
        return self._result

    def _variable_part_modules(self, index):
        """
        Prepare a list of frequencies of variable-part interval n-grams in a piece. This method is
        called by :meth:`_interval_ngrams` when required (i.e., when we are not analyzing all parts
        at once or all two-part combinations).

        These indexers and experimenters will run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`

        :param int index: The index of the IndexedPiece on which to the experiment, as stored in
            ``self._data``.

        :returns: The result of :class:`NGramIndexer` for a single piece.
        :rtype: :class:`pandas.DataFrame`

        .. note:: If the piece has an invalid part-combination list, the method returns ``None``.
        """

        # figure out which combinations we need. Because this might raise a ValueError, but we can't
        # save the situation, we might as well do this before we bother wasting time computing
        needed_combos = self._get_unique_combos(index)

        piece = self._data[index]

        # make settings for interval indexers
        # NB: we have to run the offset and repeat indexers on the notes/rests
        notes = self._run_off_rep(index, piece.get_data([noterest.NoteRestIndexer]))
        settings = {'quality': self.settings(index, 'interval quality'),
                    'horiz_attach_later': True}
        settings['simple or compound'] = ('simple' if self.settings(None, 'simple intervals')
                                          is True else 'compound')
        vert_ints = piece.get_data([interval.IntervalIndexer], settings, notes)
        horiz_ints = piece.get_data([interval.HorizontalIntervalIndexer], settings, notes)

        # concatenate the vertical and horizontal DataFrames
        all_ints = pandas.concat((vert_ints, horiz_ints), axis=1)

        # each key in vert_ints corresponds to a two-voice combination we should use
        post = []
        for combo in needed_combos:
            # make the list of part combinations
            vert = [('interval.IntervalIndexer', '{},{}'.format(i, combo[-1])) for i in combo[:-1]]
            horiz = [('interval.HorizontalIntervalIndexer', str(combo[-1]))]

            # assemble settings
            setts = {'vertical': vert,
                     'horizontal': horiz,
                     'mark singles': self.settings(None, 'mark singles'),
                     'continuer': self.settings(None, 'continuer'),
                     'n': self.settings(None, 'n')}
            if not self.settings(None, 'include rests'):
                setts['terminator'] = 'Rest'

            # run NGramIndexer, then append the result to the corresponding index of the dict
            post.append(piece.get_data([ngram.NGramIndexer], setts, all_ints))

        return pandas.concat(post, axis=1)

    def _two_part_modules(self, index):
        """
        Prepare a list of frequencies of two-part interval n-grams in a piece. This method is
        called by :meth:`_interval_ngrams` when required.

        These indexers and experimenters will run:

        * :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer`
        * :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer` (optional; via
            :meth:`_run_off_rep`)
        * :class:`~vis.analyzers.indexers.repeat.FilterByRepeatIndexer` (optional; via
            :meth:`_run_off_rep`)
        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`

        :param int index: The index of the IndexedPiece on which to the experiment, as stored in
            ``self._data``.

        :returns: The result of :class:`NGramIndexer` for a single piece.
        :rtype: :class:`pandas.DataFrame`
        """

        piece = self._data[index]

        # make settings for interval indexers
        # NB: we have to run the offset and repeat indexers on the notes/rests
        notes = self._run_off_rep(index, piece.get_data([noterest.NoteRestIndexer]))
        settings = {'quality': self.settings(index, 'interval quality'),
                    'horiz_attach_later': True}
        settings['simple or compound'] = ('simple' if self.settings(None, 'simple intervals')
                                          is True else 'compound')
        vert_ints = piece.get_data([interval.IntervalIndexer], settings, notes)
        horiz_ints = piece.get_data([interval.HorizontalIntervalIndexer], settings, notes)

        # concatenate the vertical and horizontal DataFrames
        all_ints = pandas.concat((vert_ints, horiz_ints), axis=1)

        # each key in vert_ints corresponds to a two-voice combination we should use
        post = []
        for combo in all_ints['interval.IntervalIndexer'].columns:
            # make the list of part cominations
            vert = [('interval.IntervalIndexer', combo)]
            horiz = [('interval.HorizontalIntervalIndexer', combo.split(',')[1])]

            # assemble settings
            setts = {'vertical': vert,
                     'horizontal': horiz,
                     'mark singles': self.settings(None, 'mark singles'),
                     'continuer': self.settings(None, 'continuer'),
                     'n': self.settings(None, 'n')}
            if not self.settings(None, 'include rests'):
                setts['terminator'] = 'Rest'

            # run NGramIndexer, then append the result to the corresponding index of the dict
            post.append(piece.get_data([ngram.NGramIndexer], setts, all_ints))

        return pandas.concat(post, axis=1)

    def _all_part_modules(self, index):
        """
        Prepare a list of frequencies of all-part interval n-grams in a piece. This method is
        called by :meth:`_interval_ngrams` when required.

        These indexers and experimenters will run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`

        :param int index: The index of the IndexedPiece on which to the experiment, as stored in
            ``self._data``.

        :returns: The result of :class:`NGramIndexer` for a single piece.
        :rtype: :class:`pandas.DataFrame`
        """
        piece = self._data[index]

        # make settings for interval indexers
        # NB: we have to run the offset and repeat indexers on the notes/rests
        notes = self._run_off_rep(index, piece.get_data([noterest.NoteRestIndexer]))
        settings = {'quality': self.settings(index, 'interval quality'),
                    'horiz_attach_later': True}
        settings['simple or compound'] = ('simple' if self.settings(None, 'simple intervals')
                                          is True else 'compound')
        vert_ints = piece.get_data([interval.IntervalIndexer], settings, notes)
        horiz_ints = piece.get_data([interval.HorizontalIntervalIndexer], settings, notes)

        # concatenate the vertical and horizontal DataFrames
        all_ints = pandas.concat((vert_ints, horiz_ints), axis=1)

        # find the index of the lowest part in the score
        lowest_part = len(piece.metadata('parts')) - 1

        # make the list of part cominations
        vert = [('interval.IntervalIndexer', '{},{}'.format(x, lowest_part)) for x in xrange(lowest_part)]
        horiz = [('interval.HorizontalIntervalIndexer', str(lowest_part))]

        # assemble settings
        setts = {'vertical': vert,
                 'horizontal': horiz,
                 'mark singles': self.settings(None, 'mark singles'),
                 'continuer': self.settings(None, 'continuer'),
                 'n': self.settings(None, 'n')}
        if not self.settings(None, 'include rests'):
            setts['terminator'] = 'Rest'

        # run NGramIndexer, then append the result to the corresponding index of the dict
        return piece.get_data([ngram.NGramIndexer], setts, all_ints)

    def _intervs(self):
        """
        Prepare a list of the intervals found between two parts in all pieces. If particular voice
        pairs are specified for a piece, only those pairs are included. These  analyzers will run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`

        :returns: the result of :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        :rtype: dict of :class:`pandas.Series`

        .. note:: The return value is automatically stored in ``self._result``.

        Settings are parsed automatically by piece. For part combinations, ``[all]``,
        ``[all pairs]``, and ``None`` are treated as equivalent. If the ``offset interval`` setting
        has a value, :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer` is run with that
        value. If the ``filter repeats`` setting is ``True``, the
        :class:`~vis.analyzers.repeat.FilterByRepeatIndexer` is run (after the offset indexer, if
        relevant).

        .. note:: The voice combinations must be pairs. Voice combinations with fewer or greater
            than two parts are ignored, which may result in one or more pieces being omitted from
            the results if you aren't careful with settings.
        """

        # clear any previous results
        self._result = []

        # piece-by-piece analysis
        for i, piece in enumerate(self._data):
            # 1.) prepare shared settings for the IntervalIndexer
            setts = {'quality': self.settings(None, 'interval quality')}
            setts['simple or compound'] = ('simple' if self.settings(None, 'simple intervals')
                                            is True else 'compound')

            # 2.) prepare the list of analyzers to run, adding settings if relevant
            analyzer_list = [noterest.NoteRestIndexer, interval.IntervalIndexer]
            if self.settings(i, 'offset interval') is not None:
                analyzer_list.append(offset.FilterByOffsetIndexer)
                setts['quarterLength'] = self.settings(i, 'offset interval')
            if self.settings(i, 'filter repeats'):
                analyzer_list.append()

            # 3.) run the analyzers
            vert_ints = piece.get_data(analyzer_list, setts)

            # 4.) remove the voice-pair combinations we don't want
            combos = str(self.settings(i, 'voice combinations'))
            if combos != 'all' and combos != 'all pairs' and combos != 'None':  # "if we remove pairs"
                # NB: this next line may raise a ValueError, but we can't do anything to save it
                combos = self._get_unique_combos(i)
                # ensure each combination is a two-voice pair
                for pair in combos:
                    if 2 != len(pair):
                        raise RuntimeError(WorkflowManager._REQUIRE_PAIRS_ERROR.format(len(pair)))
                # convert to what we'll find in the DataFrame
                combos = [str(x).replace(' ', '')[1:-1] for x in combos]
                vert_ints = WorkflowManager._remove_extra_pairs(vert_ints, combos)

            # 6.) remove "Rest" entries, if required
            if not self.settings(None, 'include rests'):
                new_df = {}
                for col_ind in vert_ints:
                    # TODO: what happens when there are indices that aren't IntervalIndexer?
                    this_col = vert_ints[col_ind]
                    new_df[col_ind] = this_col[this_col != 'Rest']
                vert_ints = pandas.DataFrame(new_df)

            self._result.append(vert_ints)

        # if we're making an aggregated count of interval frequencies
        if self.settings(None, 'count frequency'):
            self._run_freq_agg('interval.IntervalIndexer')

        return self._result

    def _basic(self): # TODO: Make a real doc-string and add real code.
        """
        Prepare a list of frequencies of interval n-grams in all pieces.

        This method automatically uses :meth:`_two_part_modules`, :meth:`_all_part_modules`, and
        :meth:`_variable_part_modules` when relevant.

        These indexers and experimenters will be run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`
        * :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        Settings are parsed automatically by piece. If the ``offset interval`` setting has a value,
        :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer` is run with that value. If
        the ``filter repeats`` setting is ``True``, the
        :class:`~vis.analyzers.repeat.FilterByRepeatIndexer` is run (after the offset indexer, if
        relevant).

        :returns: Result of the :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`
            or a list of outputs from :class:`~vis.analyzers.indexers.ngram.NGramIndexer`,
            depending on the ``count frequency`` setting.

        .. note:: To compute more than one value of ``n``, call :meth:`_interval_ngrams` once for
            each value of ``n``.

        """
        pass


    def _run_off_rep(self, index, so_far, is_horizontal=False):
        """
        Run the filter-by-offset and filter-by-repeat indexers, as required by the piece's settings:

        * :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer`
        * :class:`~vis.analyzers.indexers.repeat.FilterByRepeatIndexer`

        Use this method from other :class:`WorkflowManager` methods for filtering by note-start
        offset and repetition.

        .. note:: If the relevant settings (``'offset interval'`` and ``'filter repeats'``) do not
            require running either indexer, ``so_far`` will be returned unchanged. Also if the
            offset filter is used the continuer will not be used no matter what it is set to.

        :param index: Index of the piece to run.
        :type index: :``int``
        :param so_far: Return value of :meth:`get_data` that we should run through the offset and
            repeat indexers.
        :type so_far: As specified in :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer`
            or :class:`~vis.analyzers.indexers.repeat.FilterByRepeatIndexer`.
        :param is_horizontal: Whether ``index`` is an index of horizontal events. Default is False.
        :type is_horizontal: bool

        :returns: The filtered results.
        :rtype: As specified in :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer` or
            :class:`~vis.analyzers.indexers.repeat.FilterByRepeatIndexer`.

        .. note:: In VIS 1, this method had an undocumented feature, where a dictionary given as
            the ``so_far`` argument would be returned as a dictionary, with a guarantee that the
            dictionary's keys corresponded to the same object on output as on input. This doesn't
            happen anymore.
        """
        if self.settings(index, 'offset interval') is not None:
            off_sets = {'quarterLength': self.settings(index, 'offset interval')}
            if is_horizontal:
                off_sets['method'] = None
            so_far = self._data[index].get_data([offset.FilterByOffsetIndexer], off_sets, so_far)
        if self.settings(index, 'filter repeats') is True:
            so_far = self._data[index].get_data([repeat.FilterByRepeatIndexer], {}, so_far)
        return so_far

    def _run_freq_agg(self, which_ind):
        """
        Run the frequency and aggregation experimenters:

        * :class:`~vis.analyzers.experimenters.frequencyFrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        Use this method from other :class:`WorkflowManager` methods for counting frequency.

        .. note:: This method runs on, then overwrites, values stored in :attr:`self._result`.

        :param str which_ind: The name of the indexer whose results should be passed through the
            frequency and aggregation experimenters, as it appears in the DataFrame's MultiIndex
            (for example, ``'interval.IntervalIndexer'``).

        :returns: Aggregated frequency counts for everything stored in :attr:`self._result`. The
            output of the :class:`ColumnAggregator`.
        :rtype: :class:`pandas.Series`
        """
        # TODO: decide whether this get_data() call should return doubly-embedded lists. From
        #       IndexedPiece it never should, but from AggregatedPieces? This may require adjustment
        #       of the models.
        agg_p = AggregatedPieces(self._data)
        self._result = agg_p.get_data([frequency.FrequencyExperimenter],
                                      None,
                                      {'column': which_ind},
                                      self._result)
        self._result = [x[0] for x in self._result]
        self._result = agg_p.get_data(None,
                                      [aggregator.ColumnAggregator],
                                      {'column': 'frequency.FrequencyExperimenter'},
                                      self._result)
        # "ascending" means highest values near the top; "columns" indicates which column to sort
        # with; otherwise sometimes pandas sorts by the index...
        self._result = self._result.sort(ascending=False, columns='aggregator.ColumnAggregator')
        return self._result

    @staticmethod
    def _remove_extra_pairs(vert_ints, combos, which_ind='interval.IntervalIndexer'):
        """
        From the result of IntervalIndexer, remove those voice pairs that aren't required. This is
        a separate function to improve test-ability.

        Note that ``combos`` should be a sequence of strings specifying the lower level of the
        DataFrame's MultiIndex.

        Note also that this method uses ``del`` to remove the specified indices; it will therefore
        not affect the results of any other indexer that may be present in ``vert_ints``.

        :param vert_ints: The results of IntervalIndexer.
        :type vert_ints: :class:`pandas.DataFrame`
        :param combos: The voice pairs to keep.
        :type combos: sequence of string
        :param str which_ind: The name of the indexer in which to remove results. The default
            is ``'interval.IntervalIndexer'``.

        :returns: Only the voice pairs you want.
        :rtype: :class:`pandas.DataFrame`
        """
        delete_these = []
        for each_present in vert_ints[which_ind]:
            if each_present not in combos:
                delete_these.append(each_present)
        for key in delete_these:
            del vert_ints[(which_ind, key)]
        return vert_ints

    def _filter_dataframe(self, top_x=None, threshold=None, name=None):
        """
        Filter :attr:`_result` to include on the top *x* results that are strictly greater than
        ``threshold``. Note that the threshold filter is applied first, so you may end up with
        fewer than ``top_x`` results.

        :param top_x: This is the "X" in "only show the top X results." The default is ``None``.
        :type top_x: int
        :param threshold: If a result is strictly less than this number, it won't be included. The
            default is ``None``.
        :type threshold: number
        :param str name: String to use for the column name of the Series currently held in
            self._result. The default is 'data'. Ignored if self._data is already a :class:`DataFrame`.
        :returns: A :class:`DataFrame` with self._result as the only column.

        **About the "name" Parameter**

        If provided, the ``name`` parameter significantly changes the inputted DataFrame. Without
        the ``name`` parameter, :meth:`_filter_dataframe` applies its filters to all columns of
        the DataFrame. With the ``name`` parameter, :meth:`_filter_dataframe` chooses the first
        column in the first level of the index, filters that Series, and creates a new
        DataFrame with ``name`` as the column name.

        .. note:: This method does not assign its return value to :attr:`_result`.

        .. note:: This method is untested, and probably performs undesired work, on a
            :class:`DataFrame` with multiple columns.
        """

        # NB: The filters don't work reliably if we run them on an entire DataFrame, so I've broken
        #     it into a Series-by-Series strategy.

        def series_filter(each_series):
            """Apply the 'threshold' and 'top_x' filters to a single Series."""
            if threshold is not None:
                each_series = each_series[each_series > threshold]
            if top_x is not None and top_x < len(each_series):
                each_series = each_series[:top_x]
            return each_series

        # if relevant, select the leftmost column and rename it as per ``name``
        if name is not None:
            starting = pandas.DataFrame({name: self._result[self._result.columns[0]]})  # pylint: disable=maybe-no-member
        else:
            starting = self._result

        return pandas.DataFrame({x: series_filter(starting[x]) for x in list(starting.columns)})

    def output(self, instruction, pathname=None, top_x=None, threshold=None):
        """
        Output the results of the most recent call to :meth:`run`, saved in a file. This method
        handles both visualizations and symbolic output formats.

        .. note:: For LiliyPond output, you must have called :meth:`run` with ``count frequency``
            set to ``False``.

        .. note:: If ``count frequency`` is set to ``False`` for CSV, Stata, Excel, or HTML output,
            the ``top_x`` and ``threshold`` parameters are ignored.

        :parameter str instruction: The type of visualization to output.
        :parameter str pathname: The pathname for the output. The default is
            ``'test_output/output_result``. Do not include a file-type "extension," since we add
            this automatically. For the LilyPond experiment, if there are multiple pieces in the
            :class:`WorkflowManager`, we append the piece's index to the pathname.
        :param top_x: This is the "X" in "only show the top X results." The default is ``None``.
            Does not apply to the LilyPond experiment.
        :type top_x: integer
        :param threshold: If a result is strictly less than this number, it will be left out. The
            default is ``None``. This is ignored for the ``'LilyPond'`` instruction. Does not
            apply to the LilyPond experiment.
        :type threshold: integer

        :returns: The pathname(s) of the outputted visualization(s). Requesting a histogram always
            returns a single string; requesting a score (or some scores) always returns a list.
            The other formats will return a list if the ``count frequency`` setting is ``False``.
        :rtype: str or [str]

        :raises: :exc:`RuntimeError` for unrecognized instructions.
        :raises: :exc:`RuntimeError` if :meth:`run` has never been called.
        :raises: :exc:`RuntiemError` if a call to R encounters a problem.
        :raises: :exc:`RuntimeError` with LilyPond output, if we think you called :meth:`run` with
            ``count frequency`` set to ``True``.

        **Instructions:**

        * ``'histogram'``: a histogram. Currently equivalent to the ``'R histogram'`` instruction.
        * ``'LilyPond'``: each score with annotations for analyzed objects.
        * ``'R histogram'``: a histogram with ggplot2 in R. Currently equivalent to the \
            ``'histogram'`` instruction. In the future, this will be used to distinguish histograms
            produced with R from those produced with other libraries, like matplotlib or bokeh.
        * ``'CSV'``: output a Series or DataFrame to a CSV file.
        * ``'Stata'``: output a Stata file for importing to R.
        * ``'Excel'``: output an Excel file for Peter Schubert.
        * ``'HTML'``: output an HTML table, as used by the VIS Counterpoint Web App.

        .. note :: We try to prevent you from requesting LilyPond output if you called :meth:`run`
            with ``count frequency`` set to ``True`` by raising a :exc:`RuntimeError` if ``count
            frequency`` is ``True``, or the number of pieces is not the same as the number of
            results. It is still possible to call :meth:`run` with ``count frequency`` set to
            ``True`` in a way we will not detect. However, this always causes :meth:`output` to
            fail. The error will probably be a :exc:`TypeError` that says ``object of type
            'numpy.float64' has no len()``.
        """
        # ensure we have some results
        if self._result is None:
            raise RuntimeError(WorkflowManager._NO_RESULTS_ERROR)
        else:
            # properly set output paths
            pathname = 'test_output/output_result' if pathname is None else str(pathname)

        # handle instructions
        if instruction in ('CSV', 'Stata', 'Excel', 'HTML'):
            pathnames = self._make_table(instruction, pathname, top_x, threshold)
            if 1 == len(pathnames):
                return pathnames[0]
            else:
                return pathnames  # TODO: test this
        elif instruction == 'LilyPond':
            return self._make_lilypond(pathname)
        elif instruction == 'histogram' or instruction == 'R histogram':
            return self._make_histogram(pathname, top_x, threshold)
        else:
            raise RuntimeError(WorkflowManager._UNRECOGNIZED_INSTRUCTION.format(instruction))

    def _make_histogram(self, pathname=None, top_x=None, threshold=None):
        """
        Make a histogram. To be called by output(). Currently (always) uses ggplot2 in R via the
        RBarChart experimenter.

        Arguments as per output().
        """

        # ensure we have a DataFrame; do the "top x" and "threshold" filters
        chart_data = self._filter_dataframe(top_x=top_x, threshold=threshold, name='freq')

        # properly set output paths
        setts = {'pathname': 'test_output/output_result' if pathname is None else str(pathname)}

        # choose the proper token
        if 'intervals' == self._previous_exp:
            setts['token'] = 'interval'
        elif 'interval n-grams' == self._previous_exp:  # TEST
            setts['token'] = '{}-gram'.format(self.settings(None, 'n'))
        else:
            setts['token'] = 'objects'

        # set the number of pieces
        setts['nr_pieces'] = len(self)

        # set the output file type
        setts['type'] = 'png'

        # run the experimenter
        png_path = barchart.RBarChart(chart_data, setts).run()

        return png_path

    def _make_lilypond(self, pathname=None):
        """
        Make annotated scores with LilyPond. To be called by output().

        Argument as per output().
        """

        file_ext = 'ly'
        if pathname is None:
            pathname = 'test_output/output_result'

        # try to determine whether they called run() properly (``count frequency`` should be False)
        if self.settings(None, 'count frequency') is True or len(self._data) != len(self._result):
            raise RuntimeError(WorkflowManager._COUNT_FREQUENCY_MESSAGE)

        # assume we have the result of a suitable Indexer
        annotation_parts = []
        # run additional indexers for annotation
        for i in xrange(len(self._data)):
            ann_p = []
            combos = list(self._result[i].columns)  # this is (Indexer, part_combo) tuples

            # run the LilyPond analyzers
            for j in combos:
                this_part = self._result[i][j].dropna()
                ann_p.append(self._data[i].get_data([lilypond_ind.AnnotationIndexer,
                                                     lilypond_exp.AnnotateTheNoteExperimenter,
                                                     lilypond_exp.PartNotesExperimenter],
                                                    {'part_names': ['{}: {}'.format(j[0], j[1])],
                                                     'column': 'lilypond.AnnotationIndexer'},
                                                    [this_part])[0])
            annotation_parts.append(ann_p)

        # run OutputLilyPond and LilyPond
        enum = True if len(self._data) > 1 else False
        pathnames = []
        for i in xrange(len(self._data)):
            setts = {'run_lilypond': True, 'annotation_part': annotation_parts[i]}
            # append piece index to pathname, if there are many pieces
            if enum:
                setts['output_pathname'] = '{}-{}.{}'.format(pathname, i, file_ext)
            else:
                setts['output_pathname'] = '{}.{}'.format(pathname, file_ext)
            self._data[i].get_data([lilypond_exp.LilyPondExperimenter], setts)
            pathnames.append(setts['output_pathname'])

        return pathnames

    def _make_table(self, form, pathname, top_x, threshold):
        """
        Output a table-style result. Called by :meth:`output`.

        :param st form: Either 'CSV', 'Stata', 'Excel', or 'HTML', depending on the desired output
            format.
        :param str pathname: As in :meth:`output`.
        :param int top_x: As in :meth:`output`.
        :param int threshold: As in :meth:`output`.

        :returns: The pathname(s) of the outputted files.
        :rtype: list of str

        .. note:: If ``count frequency`` is ``False``, the ``top_x`` and ``threshold`` parameters
            are ignored.
        """

        # key is the instruction; value is (extension, export_method)
        directory = {'CSV': ('.csv', 'to_csv'),
                     'Stata': ('.dta', 'to_stata'),
                     'Excel': ('.xlsx', 'to_excel'),
                     'HTML': ('.html', 'to_html')}

        # set file extension and the method to call for output
        file_ext, output_meth = directory[form]

        # ensure the pathname doesn't have a file extension
        if pathname.endswith(file_ext):
            pathname = pathname[:(-1 * len(file_ext))]

        pathnames = []

        if self.settings(None, 'count frequency'):
            # filter the results
            name = 'Interval Frequency' if self._previous_exp == 'intervals' else 'Interval N-Gram Frequency'
            export_me = self._filter_dataframe(top_x=top_x, threshold=threshold, name=name)
            pathnames.append('{}{}'.format(pathname, file_ext))
            getattr(export_me, output_meth)(pathnames[-1])
        else:
            enum = True if (len(self._data) > 1 and not self.settings(None, 'count frequency')) else False
            for i in xrange(len(self._data)):
                # append piece index to pathname, if there are many pieces
                if enum:
                    pathnames.append('{}-{}{}'.format(pathname, i, file_ext))
                    # call the method that actually outputs the result
                    getattr(self._result[i], output_meth)(pathnames[-1])
                else:
                    pathnames.append('{}{}'.format(pathname, file_ext))
                    # call the method that actually outputs the result
                    getattr(self._result[i], output_meth)(pathnames[-1])

        return pathnames

    def metadata(self, index, field, value=None):
        """
        Get or set a metadata field. The valid field names are determined by :class:`IndexedPiece`
        (refer to the documentation for :meth:`~vis.models.indexed_piece.IndexedPiece.metadata`).

        A metadatum is a salient musical characteristic of a particular piece, and does not change
        across analyses.

        :param int index: The index of the piece to access. The range of valid indices is ``0``
            through one fewer than the :func:`len` of this :class:`WorkflowManager`.
        :param str field: The name of the field to be accessed or modified.
        :param object value: If not ``None``, the new value to be assigned to ``field``.

        :returns: The value of the requested field or ``None``, if assigning, or if accessing a
            non-existant field or a field that has not yet been initialized.
        :rtype: object

        :raises: :exc:`TypeError` if ``field`` is not a string.
        :raises: :exc:`AttributeError` if accessing an invalid ``field``.
        :raises: :exc:`IndexError` if ``index`` is invalid for this ``WorkflowManager``.
        """
        return self._data[index].metadata(field, value)

    def settings(self, index, field, value=None):
        """
        Get or set a value related to analysis. The valid values are listed below.

        A setting is related to this particular analysis, and is not a salient musical feature of
        the work itself.

        Refer to :meth:`run` for a list of settings required or used by each experiment.

        :param index: The index of the piece to access. The range of valid indices is ``0`` through
            one fewer than the return value of calling :func:`len` on this WorkflowManager. If
            ``value`` is not ``None`` and ``index`` is ``None``, you can set a field for all pieces.
        :type index: int or ``None``
        :param str field: The name of the field to be accessed or modified.
        :param value: If not ``None``, the new value to be assigned to ``field``.
        :type value: object or ``None``

        :returns: The value of the requested field or ``None``, if assigning, or if accessing a
            non-existant field or a field that has not yet been initialized.
        :rtype: object or ``None``

        :raises: :exc:`AttributeError` if accessing an invalid ``field`` (see valid fields below).
        :raises: :exc:`IndexError` if ``index`` is invalid for this ``WorkflowManager``.
        :raises: :exc:`ValueError` if ``index`` and ``value`` are both ``None``.

        **Piece-Specific Settings**

        Pieces do not share these settings.

        * ``offset interval``: If you want to run the \
            :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer`, specify a value for this \
            setting. To avoid running the :class:`FilterByOffsetIndexer`, set this to ``0``. This \
            will become the ``quarterLength`` duration between observed offsets.
        * ``filter repeats``: If you want to run the \
            :class:`~vis.analyzers.indexers.repeat.FilterByRepeatIndexer`, set this setting to \
            ``True``.
        * ``voice combinations``: If you want to consider certain specific voice combinations, \
            set this setting to a list of a list of iterables. The following value would analyze \
            the highest three voices with each other: ``'[[0,1,2]]'`` while this would analyze the \
            every part with the lowest for a four-part piece: ``'[[0, 3], [1, 3], [2, 3]]'``. This \
            should always be a ``str`` that nominally represents a list (except the special \
            values for ``'all'`` parts at once or ``'all pairs'``).

        **Shared Settings**

        All pieces share these settings. The value of ``index`` is ignored for shared settings, so
        it can be anything.

        * ``n``: As specified in :attr:`vis.analyzers.indexers.ngram.NGramIndexer.possible_settings`.
        * ``continuer``: Determines the way unisons that arise from sustained notes in the lowest \
            voice are represented. Note that if the FilterByOffsetIndexer is used, the continuer \
            won't get used. The default is 'dynamic quality' which sets to 'P1' if interval quality \
            is set to True, and '1' if it is set to False. This is given directly to the \
            :class:`NGramIndexer`. Refer to \
            :attr:`~vis.analyzers.indexers.ngram.NGramIndexer.possible_settings`.
        * ``interval quality``: If you want to display interval quality, set this setting to \
            ``True``.
        * ``simple intervals``: If you want to display all intervals as their single-octave \
            equivalents, set this setting to ``True``.
        * ``include rests``: If you want to include ``'Rest'`` tokens as vertical intervals, \
            change this setting to ``True``. The default is ``False``.
        * ``count frequency``: When set to ``True`` (the default), experiments will return the \
            number of occurrences of each token (i.e., "each interval" or "each interval n-gram").\
            When set to ``False``, the moment-by-moment analysis of each piece is retained. We \
            recommend you only request spreadsheet-formatted output when ``count frequency`` is \
            ``False``.
        """
        if field in self._shared_settings:
            if value is None:
                return self._shared_settings[field]
            else:
                self._shared_settings[field] = value
        elif index is None:
            if value is None:
                raise ValueError('If "index" is None, "value" must not be None.')
            else:
                for i in xrange(len(self._settings)):
                    self.settings(i, field, value)
        elif not 0 <= index < len(self._settings):
            raise IndexError('Invalid piece index: {}'.format(index))
        elif field not in self._settings[index]:
            raise AttributeError('Invalid setting: {}'.format(field))
        elif value is None:
            return self._settings[index][field]
        elif field == 'offset interval' and value == 0:  # can't set directly to None :(
            self._settings[index][field] = None
        else:
            self._settings[index][field] = value
