#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/workflow.py
# Purpose:                Workflow Controller
#
# Copyright (C) 2013 Christopher Antila
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
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

The ``workflow`` module holds the :class:`WorkflowManager`, which automates several common music
analysis patterns for counterpoint. The :class:`TemplateWorkflow` class is a template for writing
new ``WorkflowManager`` classes.
"""

import ast
import subprocess
import pandas
from vis.models import indexed_piece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest, interval, ngram, offset, repeat, harmony, key
from vis.analyzers.experimenters import frequency, aggregator


class WorkflowManager(object):
    """
    :parameter pathnames: A list of pathnames.
    :type pathnames: ``list`` of ``basestring``

    The :class:`WorkflowManager` automates several common music analysis patterns for counterpoint.
    Use the ``WorkflowManager`` with these four tasks:

    * :meth:`load`, to import pieces from symbolic data formats.
    * :meth:`run`, to perform a pre-defined analysis.
    * :meth:`output`, to output a visualization of the analysis results.
    * :meth:`export`, to output a text-based version of the analysis results.

    Before you analyze, you may wish to use these methods:

    * :meth:`metadata`, to get or set the metadata of a specific :class:`IndexedPiece` managed by \
        this ``WorkflowManager``.
    * :meth:`settings`, to get or set a setting related to analysis (for example, whether to \
        display the quality of intervals).

    You may also treat a ``WorkflowManager`` as a container:

    >>> wm = WorkflowManager('piece1.mxl', 'piece2.krn')
    >>> len(wm)
    2
    >>> ip = wm[1]
    >>> type(ip)
    <class 'vis.models.indexed_piece.IndexedPiece'>
    """

    # Instance Variables
    # - self._data: list of IndexedPieces
    # - self._result: result of the most recent call to run()
    # - self._settings: list of dicts with settings
    # - self._previous_exp: name of the most recently run experiment (see _experiments_list)

    # path to the R-language script that makes bar charts
    _R_bar_chart_path = u'scripts/R_bar_chart.r'

    # names of the experiments available through run()
    # NOTE: do not re-order these, or run() will break
    _experiments_list = [u'intervals', u'interval n-grams', u'harmonic function']

    def __init__(self, pathnames):
        # create the list of IndexedPiece objects
        self._data = []
        for each_val in pathnames:
            if isinstance(each_val, basestring):
                self._data.append(indexed_piece.IndexedPiece(each_val))
            elif isinstance(each_val, indexed_piece.IndexedPiece):
                self._data.append(each_val)
        # hold the result of the most recent call to run()
        self._result = None
        # hold the IndexedPiece-specific settings
        self._settings = [{} for _ in xrange(len(self._data))]
        for piece_sett in self._settings:
            for sett in [u'offset interval', u'voice combinations']:
                piece_sett[sett] = None
            for sett in [u'filter repeats']:
                piece_sett[sett] = False
        # hold settings common to all IndexedPieces
        self._shared_settings = {u'n': 2, u'continuer': u'_', u'mark singles': False,
                                 u'interval quality': False, u'simple intervals': False}
        # which was the most recent experiment run? Either 'intervals' or 'n-grams'
        self._previous_exp = None

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

    def load(self, instruction, pathname=None):
        """
        Import analysis data from long-term storage on a filesystem. This should primarily be \
        used for the ``u'pieces'`` instruction, to control when the initial music21 import \
        happens.

        Use :meth:`load` with an instruction other than ``u'pieces'`` to load results from a
        previous analysis run by :meth:`run`.

        Parameters
        ==========
        :parameter instruction: The type of data to load.
        :type instruction: :obj:`basestring`
        :parameter pathname: The pathname of the data to import; not required for the \
            ``u'pieces'`` instruction.
        :type pathname: :obj:`basestring`

        **Instructions:**

        .. note:: only ``u'pieces'`` is implemented at this time.

        * :obj:`u'pieces'`, to import all pieces, collect metadata, and run :class:`NoteRestIndexer`
        * :obj:`u'hdf5'` to load data from a previous :meth:`export`.
        * :obj:`u'stata'` to load data from a previous :meth:`export`.
        * :obj:`u'pickle'` to load data from a previous :meth:`export`.
        """
        # TODO: rewrite this with multiprocessing
        # NOTE: you may want to have the worker process create a new IndexedPiece object, import it
        #       and run the NoteRestIndexer, then pickle it and send that to a callback method
        #       that will somehow unpickle it and replace the *data in* the IndexedPieces here, but
        #       not actually replace the IndexedPieces, since that would inadvertently cancel the
        #       client's pointer to the IndexedPieces, if they have one
        if u'pieces' == instruction:
            for piece in self._data:
                piece.get_data([noterest.NoteRestIndexer])
        elif u'hdf5' == instruction or u'stata' == instruction or u'pickle' == instruction:
            raise NotImplementedError(u'The ' + instruction + u' instruction does\'t work yet!')

    def run(self, instruction):
        """
        Run the workflow of an experiment.

        Parameters
        ==========
        :parameter instruction: The experiment to run.
        :type instruction: ``basestring``

        Returns
        =======
        :returns: The result of the experiment.
        :rtype: :class:`pandas.Series` or :class:`pandas.DataFrame`

        Raises
        ======
        :raises: :exc:`RuntimeError` if the ``instruction`` is not valid for this
            ``WorkflowManager``.

        **Instructions:**

        * ``u'intervals'``: finds the frequency of vertical intervals in all \
            2-part voice combinations.
        * ``u'interval n-grams'``: finds the frequency of any-part vertical interval n-grams in \
            voice pairs specified in the settings. Remember to provide the ``u'n'`` setting.
        """
        # NOTE: this method relies on the order of instructions in _experiments_list
        error_msg = u'WorkflowManager.run() could not parse the instruction'
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
            # harmonic function
            self._previous_exp = WorkflowManager._experiments_list[2]
            post = self._harmonic_function()
        else:
            raise RuntimeError(error_msg)
        self._result = post
        return post

    def _interval_ngrams(self):
        """
        Prepare a list of frequencies of interval n-grams in all pieces.

        This method automatically uses :met:`_two_part_modules` and :meth:`_all_part_modules`
        when relevant.

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

        :returns: The result of the :class:`ColumnAggregator`.

        .. note:: To compute more than one value of ``n``, call :meth:`_interval_ngrams` many times.
        """
        all_results = []
        # user helpers to fetch results for each piece
        for i in xrange(len(self._data)):
            if u'[all]' == self.settings(i, u'voice combinations'):
                all_results.append(self._all_part_modules(i))
            elif u'[all pairs]' == self.settings(i, u'voice combinations'):
                all_results.append(self._two_part_modules(i))
            else:
                all_results.append(self._variable_part_modules(i))
        # aggregate results across all pieces
        agg_p = AggregatedPieces(self._data)
        self._result = agg_p.get_data([aggregator.ColumnAggregator], None, {}, all_results)
        self._result.sort(ascending=False)
        return self._result

    def _harmonic_function(self):
        """
        Prepare a list of harmonic functions of every simultaneity in the pieces.

        These indexers and experimenters will be run:

        * :class:`vis.analyzers.indexers.key.KeyIndexer`
        * :class:`vis.analyzers.indexers.harmony.ScaleDegreeIndexer`
        * :class:`~vis.analyzers.indexers.harmony.PossFuncIndexer`
        * :class:`~vis.analyzers.indexers.harmony.ChooseFuncIndexer`
        * :class:`~vis.analyzers.indexers.harmony.ChordLabelIndexer`

        There are no settings.

        :returns: The result of the :class:`ChordLabel` indexer.
        """
        self._result = []
        for piece in self._data:
            key_ind = piece.get_data([key.KeyIndexer])
            pass_in = piece.get_data([noterest.NoteRestIndexer])
            pass_in.append(key_ind)
            pass_in = piece.get_data([harmony.ScaleDegreeIndexer], None, pass_in)
            pass_in.append(key_ind)
            self._result.append(piece.get_data([harmony.PossFuncIndexer,
                                                harmony.ChooseFuncIndexer,
                                                harmony.ChordLabelIndexer],
                                               None,
                                               pass_in))
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
        * :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        :param index: The index of the IndexedPiece on which to the experiment, as stored in
            ``self._data``.
        :type index: integer

        :returns: The result of :class:`ColumnAggregator` for a single piece.
        :rtype: :class:`pandas.Series` or ``None``

        .. note:: If the piece has an invalid part-combination list, the method returns ``None``.
        """
        piece = self._data[index]
        # make settings for interval indexers
        settings = {u'quality': self.settings(index, u'interval quality')}
        settings[u'simple or compound'] = u'simple' if self.settings(index, u'interval quality') \
                                          else u'compound'
        vert_ints = piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer], settings)
        horiz_ints = piece.get_data([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer],
                                    settings)
        # run the offset and repeat indexers, if required
        if self.settings(index, u'offset interval') is not None:
            off_sets = {u'quarterLength': self.settings(index, u'offset interval')}
            vert_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, vert_ints)
            horiz_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, horiz_ints)
        if self.settings(index, u'filter repeats') is True:
            vert_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, vert_ints)
            horiz_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, horiz_ints)
        # figure out which combinations we need... this might raise a ValueError, but there's not
        # much we can do to save the situation, so we might as well let it go up
        needed_combos = ast.literal_eval(unicode(self.settings(index, u'voice combinations')))
        # each key in vert_ints corresponds to a two-voice combination we should use
        for combo in needed_combos:
            # make the list of parts
            parts = [vert_ints[str(i) + u',' + str(combo[-1])] for i in combo[:-1]]
            parts.append(horiz_ints[combo[-1]])
            # assemble settings
            setts = {u'vertical': range(len(combo[:-1])), u'horizontal': [len(combo[:-1])]}
            setts[u'mark singles'] = self.settings(None, u'mark singles')
            setts[u'continuer'] = self.settings(None, u'continuer')
            setts[u'n'] = self.settings(None, u'n')
            # run NGramIndexer and FrequencyExperimenter, then append the result to the
            # corresponding index of the dict
            result = piece.get_data([ngram.NGramIndexer, frequency.FrequencyExperimenter],
                                    setts,
                                    parts)
        return result

    def _two_part_modules(self, index):
        """
        Prepare a list of frequencies of two-part interval n-grams in a piece. This method is
        called by :meth:`_interval_ngrams` when required.

        These indexers and experimenters will run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`
        * :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        :param index: The index of the IndexedPiece on which to the experiment, as stored in
            ``self._data``.
        :type index: integer

        :returns: The result of :class:`ColumnAggregator` for a single piece.
        :rtype: :class:`pandas.Series`
        """
        piece = self._data[index]
        # make settings for interval indexers
        settings = {u'quality': self.settings(index, u'interval quality')}
        settings[u'simple or compound'] = u'simple' if self.settings(index, u'interval quality') \
                                          else u'compound'
        vert_ints = piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer], settings)
        horiz_ints = piece.get_data([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer],
                                    settings)
        # run the offset and repeat indexers, if required
        if self.settings(index, u'offset interval') is not None:
            off_sets = {u'quarterLength': self.settings(index, u'offset interval')}
            vert_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, vert_ints)
            horiz_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, horiz_ints)
        if self.settings(index, u'filter repeats') is True:
            vert_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, vert_ints)
            horiz_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, horiz_ints)
        # each key in vert_ints corresponds to a two-voice combination we should use
        for combo in vert_ints.iterkeys():
            # which "horiz" part to use?
            horiz_i = interval.key_to_tuple(combo)[1]
            # make the list of parts
            parts = [vert_ints[combo], horiz_ints[horiz_i]]
            # assemble settings
            setts = {u'vertical': [0], u'horizontal': [1]}
            setts[u'mark singles'] = self.settings(None, u'mark singles')
            setts[u'continuer'] = self.settings(None, u'continuer')
            setts[u'n'] = self.settings(None, u'n')
            # run NGramIndexer and FrequencyExperimenter, then append the result to the
            # corresponding index of the dict
            result = piece.get_data([ngram.NGramIndexer, frequency.FrequencyExperimenter],
                                    setts,
                                    parts)
        return result

    def _all_part_modules(self, index):
        """
        Prepare a list of frequencies of all-part interval n-grams in a piece. This method is
        called by :meth:`_interval_ngrams` when required.

        These indexers and experimenters will run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.indexers.interval.HorizontalIntervalIndexer`
        * :class:`~vis.analyzers.indexers.ngram.NGramIndexer`
        * :class:`~vis.analyzers.experimenters.frequency.FrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        :param index: The index of the IndexedPiece on which to the experiment, as stored in
            ``self._data``.
        :type index: integer

        :returns: The result of :class:`ColumnAggregator` for a single piece.
        :rtype: :class:`pandas.Series`
        """
        piece = self._data[index]
        # make settings for interval indexers
        settings = {u'quality': self.settings(index, u'interval quality')}
        settings[u'simple or compound'] = u'simple' if self.settings(index, u'interval quality') \
                                          else u'compound'
        vert_ints = piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer],
                                   settings)
        horiz_ints = piece.get_data([noterest.NoteRestIndexer,
                                     interval.HorizontalIntervalIndexer],
                                    settings)
        # run the offset and repeat indexers, if required
        if self.settings(index, u'offset interval') is not None:
            off_sets = {u'quarterLength': self.settings(index, u'offset interval')}
            vert_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, vert_ints)
            horiz_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, horiz_ints)
        if self.settings(index, u'filter repeats') is True:
            vert_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, vert_ints)
            horiz_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, horiz_ints)
        # figure out the weird string-index things for the vertical part combos
        lowest_part = len(piece.metadata(u'parts')) - 1
        vert_combos = [str(x) + u',' + str(lowest_part) for x in xrange(lowest_part)]
        # make the list of parts
        parts = [vert_ints[x] for x in vert_combos]
        parts.append(horiz_ints[-1])  # always the lowest voice
        # assemble settings
        settings = {u'vertical': range(len(parts) - 1), u'horizontal': [len(parts) - 1]}
        settings[u'mark singles'] = self.settings(None, u'mark singles')
        settings[u'continuer'] = self.settings(None, u'continuer')
        settings[u'n'] = self.settings(None, u'n')
        # run NGramIndexer and FrequencyExperimenter, then append the result to the
        # corresponding index of the dict
        result = piece.get_data([ngram.NGramIndexer, frequency.FrequencyExperimenter],
                                settings,
                                parts)
        return result

    def _intervs(self):
        """
        Prepare a list of frequencies of intervals between all voice pairs of all pieces. These \
        indexers and experimenters will run:

        * :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
        * :class:`~vis.analyzers.experimenters.frequencyFrequencyExperimenter`
        * :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`

        Settings are parsed automatically by piece. For part combinations, ``[all]``,
        ``[all pairs]``, and ``None`` are treated as equivalent. If the ``offset interval`` setting
        has a value, :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer` is run with that
        value. If the ``filter repeats`` setting is ``True``, the
        :class:`~vis.analyzers.repeat.FilterByRepeatIndexer` is run (after the offset indexer, if
        relevant).

        .. note:: The voice combinations must be pairs. Voice combinations with fewer or greater
        than two parts are ignored, which may result in one or more pieces being omitted from the
        results if you aren't careful with settings.

        :returns: the result of :class:`~vis.analyzers.experimenters.aggregator.ColumnAggregator`
        :rtype: :class:`pandas.Series`
        """
        int_freqs = []
        # shared settings for the IntervalIndexer
        setts = {u'quality': self.settings(None, u'interval quality')}
        setts[u'simple or compound'] = u'simple' if self.settings(None, u'simple intervals') == \
                                       True else u'compound'
        for i, piece in enumerate(self._data):
            vert_ints = piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer], setts)
            # see which voice pairs we need; if relevant, remove unneeded voice pairs
            combos = self.settings(i, u'voice combinations')
            if combos != u'[all]' and combos != u'[all pairs]' and combos is not None:
                vert_ints = WorkflowManager._remove_extra_pairs(vert_ints, combos)
            # we no longer need to know the combinations' names, so we can make a list
            vert_ints = list(vert_ints.itervalues())
            # run the offset and repeat indexers, if required
            if self.settings(i, u'offset interval') is not None:
                off_sets = {u'quarterLength': self.settings(i, u'offset interval')}
                vert_ints = piece.get_data([offset.FilterByOffsetIndexer], off_sets, vert_ints)
            if self.settings(i, u'filter repeats') is True:
                vert_ints = piece.get_data([repeat.FilterByRepeatIndexer], {}, vert_ints)
            # aggregate results and save for later
            int_freqs.append(piece.get_data([frequency.FrequencyExperimenter,
                                             aggregator.ColumnAggregator],
                                            {},
                                            vert_ints))
        # TODO: find out what happens when there are no results in int_freqs?
        agg_p = AggregatedPieces(self._data)
        post = agg_p.get_data([aggregator.ColumnAggregator], None, {}, int_freqs)
        post.sort(ascending=False)
        return post

    @staticmethod
    def _remove_extra_pairs(vert_ints, combos):
        """
        From the result of IntervalIndexer, remove those voice pairs that aren't required. This is
        a separate function to improve test-ability.

        **Parameters:**
        :param vert_ints: The results of IntervalIndexer.
        :type vert_ints: dict of any
        :param combos: The voice pairs to keep. Note that any element in this list longer than 2
            will be silently ignored.
        :type combos: list of list of int

        **Returns:**
        :returns: Only the voice pairs you want.
        :rtype: dict of any
        """
        these_pairs = []
        for pair in combos:
            if 2 == len(pair):
                these_pairs.append(unicode(pair[0]) + u',' + unicode(pair[1]))
        if 0 == len(these_pairs):
            return {}
        else:
            delete_these = []
            for each_key in vert_ints.itereach_keys():
                if each_key not in these_pairs:
                    delete_these.append(each_key)
            for each_key in delete_these:
                del vert_ints[each_key]
            return vert_ints

    def _get_dataframe(self, name=u'data', top_x=None, threshold=None):
        """
        "Convert" ``self._result`` into a :class:`DataFrame`, including only the top ``X`` results
        that are greater than ``threshold``. Note that the threshold filter is applied first.

        :param name: String to use for the column name of the Series currently held in self._result.
            The default is u'data'.
        :type name: ``basestring``
        :param top_x: This is the "X" in "only show the top X results." The default is ``None``.
        :type top_x: ``int``
        :param threshold: If a result is strictly less than this number, it won't be included. The
            default is ``None``.
        :type threshold: number

        :returns: A DataFrame with self._result as the only column.
        :rtype: :class:`DataFrame`
        """
        post = None
        if threshold is not None:
            post = self._result[self._result > threshold]
        else:
            post = self._result
        if top_x is not None:
            post = post[:top_x]
        return pandas.DataFrame({name: post})

    def output(self, instruction, pathname=None, top_x=None, threshold=None):
        """
        Create a visualization from the most recent result of :meth:`run` and save it to a file.

        Parameters
        ==========
        :parameter instruction: The type of visualization to output.
        :type instruction: ``basestring``
        :parameter pathname: The pathname for the output. The default is
            ``'test_output/output_result``. A file extension is applied automatically.
        :type pathname: ``basestring``
        :param top_x: This is the "X" in "only show the top X results." The default is ``None``.
        :type top_x: ``int``
        :param threshold: If a result is strictly less than this number, it will be left out. The
            default is ``None``.
        :type threshold: number

        Returns
        =======
        :returns: The pathname of the outputted visualization.
        :rtype: :obj:`unicode`

        Raises
        ======
        :raises: :exc:`NotImplementedError` if you use the ``u'LilyPond'`` instruction.
        :raises: :exc:`RuntimeError` for unrecognized instructions.
        :raises: :exc:`RuntimeError` if :meth:`run` has never been called.

        **Instructions:**

        .. note:: Only the ``u'R histogram'`` instruction works at the moment.

        * :obj:`u'LilyPond'`: not yet sure what this will be like...
        * :obj:`u'R histogram'`: a histogram with ggplot2 in R.
        """
        if instruction == u'LilyPond':
            raise NotImplementedError(u'I didn\'t write that part yet!')
        elif instruction == u'R histogram':
            # ensure we have some results
            if self._result is None:
                raise RuntimeError(u'Call run() before calling export()')
            else:
                # properly set output paths
                pathname = u'test_output/output_result' if pathname is None else unicode(pathname)
                stata_path = pathname + u'.dta'
                png_path = pathname + u'.png'
                # ensure we have a DataFrame
                if not isinstance(self._result, pandas.DataFrame):
                    out_me = self._get_dataframe(u'freq', top_x, threshold)
                else:
                    out_me = self._result
                out_me.to_stata(stata_path)
                token = None
                if u'intervals' == self._previous_exp:
                    token = u'int'
                elif u'n-grams' == self._previous_exp:
                    token = unicode(self.settings(None, u'n'))
                else:
                    token = u'things'
                call_to_r = [u'R', u'--vanilla', u'-f', WorkflowManager._R_bar_chart_path,
                             u'--args', stata_path, png_path, token, str(len(self._data))]
                subprocess.call(call_to_r)
                return png_path
        else:
            raise RuntimeError(u'Unrecognized instruction: ' + unicode(instruction))

    def export(self, form, pathname=None, top_x=None, threshold=None):
        """
        Save data from the most recent result of :meth:`run` to a file.

        Parameters
        ==========
        :parameter form: The output format you want.
        :type form: :obj:`basestring`
        :parameter pathname: The pathname for the output. The default is
            ``test_output/output_result``. File extensions are applied automatically.
        :type pathname: :obj:`basestring`
        :param top_x: This is the "X" in "only show the top X results." The default is ``None``.
        :type top_x: :obj:`int`
        :param threshold: If a result is strictly less than this number, it won't be included. The
            default is :obj:`None`.
        :type threshold: :obj:`int` or :obj:`float`

        Returns
        =======
        :returns: The pathname of the outputted file.
        :rtype: :obj:`unicode`

        Raises
        ======
        :raises: :exc:`RuntimeError` for unrecognized instructions.
        :raises: :exc:`RuntimeError` if :meth:`run` has never been called.

        Formats:

        * ``u'CSV'``: output a Series or DataFrame to a CSV file.
        * ``u'Stata'``: output a Stata file for importing to R.
        * ``u'Excel'``: output an Excel file for Peter Schubert.
        * ``u'HTML'``: output an HTML table, as used by the vis PyQt4 GUI.
        """
        # ensure we have some results
        if self._result is None:
            raise RuntimeError(u'Call run() before calling export()')
        # ensure we have a DataFrame
        if not isinstance(self._result, pandas.DataFrame):
            export_me = self._get_dataframe(u'data', top_x, threshold)
        else:
            export_me = self._result
        # key is the instruction; value is (extension, export_method)
        directory = {u'CSV': (u'.csv', export_me.to_csv),
                     u'Stata': (u'.dta', export_me.to_stata),
                     u'Excel': (u'.xlsx', export_me.to_excel),
                     u'HTML': (u'.html', export_me.to_html)}
        # ensure we have a valid output format
        if form not in directory:
            raise RuntimeError(u'Unrecognized output format: ' + unicode(form))
        # ensure we have an output path
        pathname = u'test_output/no_path' if pathname is None else unicode(pathname)
        # ensure there's a file extension
        if directory[form][0] != pathname[-1 * len(directory[form][0]):]:
            pathname += directory[form][0]
        # call the to_whatever() method
        directory[form][1](pathname)
        return pathname

    def metadata(self, index, field, value=None):
        """
        Get or set a metadata field. The valid field names are determined by :class:`IndexedPiece`
        (refer to the documentation for :meth:`~vis.models.indexed_piece.IndexedPiece.metadata`).

        A metadatum is a salient musical characteristic of a particular piece, and does not change
        across analyses.

        :param index: The index of the piece to access. The range of valid indices is ``0`` through
            one fewer than the return value of calling :func:`len` on this :class:`WorkflowManager`.
        :type index: :obj:`int`
        :param field: The name of the field to be accessed or modified.
        :type field: :obj:`basestring`
        :param value: If not ``None``, the new value to be assigned to ``field``.
        :type value: :obj:`object` or :obj:`None`

        :returns: The value of the requested field or ``None``, if assigning, or if accessing a
            non-existant field or a field that has not yet been initialized.
        :rtype: :obj:`object` or :obj:`None`

        :raises: :exc:`TypeError` if ``field`` is not a ``basestring``.
        :raises: :exc:`AttributeError` if accessing an invalid ``field``.
        :raises: :exc:`IndexError` if ``index`` is invalid for this ``WorkflowManager``.
        """
        return self._data[index].metadata(field, value)

    def settings(self, index, field, value=None):
        """
        Get or set a value related to analysis. The valid values are listed below.

        A setting is related to this particular analysis, and is not a salient musical feature of
        the work itself.

        :param index: The index of the piece to access. The range of valid indices is ``0`` through
            one fewer than the return value of calling :func:`len` on this WorkflowManager. If
            ``value`` is not ``None`` and ``index`` is ``None``, you can set a field for all pieces.
        :type index: :``int`` or ``None``
        :param field: The name of the field to be accessed or modified.
        :type field: ``basestring``
        :param value: If not ``None``, the new value to be assigned to ``field``.
        :type value: ``object`` or ``None``

        :returns: The value of the requested field or ``None``, if assigning, or if accessing a
            non-existant field or a field that has not yet been initialized.
        :rtype: :obj:`object` or :obj:`None`

        :raises: :exc:`AttributeError` if accessing an invalid ``field`` (see valid fields below).
        :raises: :exc:`IndexError` if ``index`` is invalid for this ``WorkflowManager``.
        :raises: :exc:`ValueError` if ``index`` and ``value`` are both ``None``.

        **Piece-Specific Settings:**
        Pieces do not share these settings.

        * ``offset interval``: If you want to run the \
            :class:`~vis.analyzers.indexers.offset.FilterByOffsetIndexer`, specify a value for this
            setting that will become the ``quarterLength`` duration between observed offsets.
        * ``filter repeats``: If you want to run the \
            :class:`~vis.analyzers.indexers.repeat.FilterByRepeatIndexer`, set this setting to \
            ``True``.
        * ``voice combinations``: If you want to consider certain specific voice combinations, \
            set this setting to a list of a list of iterables. The following value would analyze \
            the highest three voices with each other: ``'[[0,1,2]]'`` while this would analyze the \
            every part with the lowest for a four-part piece: ``'[[0, 3], [1, 3], [2, 3]]'``. This \
            should always be a ``basestring`` that nominally represents a list (like the values \
            shown above or ``'[all]'`` or ``'[all pairs]'``).

        **Shared Settings:**
        All pieces share these settings. The value of ``index`` is ignored for shared settings, so
        it can be anything.

        * ``n``: As specified in :attr:`vis.analyzers.indexers.ngram.NGramIndexer.possible_settings`
        * ``continuer``: As specified in \
            :attr:`vis.analyzers.indexers.ngram.NGramIndexer.possible_settings`
        * ``interval quality``: If you want to display interval quality, set this setting to \
            ``True``.
        * ``simple intervals``: If you want to display all intervals as their single-octave \
            equivalents, set this setting to ``True``.
        """
        if field in self._shared_settings:
            if value is None:
                return self._shared_settings[field]
            else:
                self._shared_settings[field] = value
        elif index is None:
            if value is None:
                raise ValueError(u'If "index" is None, "value" must not be None.')
            else:
                for i in xrange(len(self._settings)):
                    self.settings(i, field, value)
        elif not 0 <= index < len(self._settings):
            raise IndexError(u'Invalid inex for this WorkflowManager (' + unicode(index) + u')')
        elif field not in self._settings[index]:
            raise AttributeError(u'Invalid setting: ' + unicode(field))
        elif value is None:
            return self._settings[index][field]
        else:
            self._settings[index][field] = value
