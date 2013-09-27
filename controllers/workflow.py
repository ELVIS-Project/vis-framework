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
Workflow controller, to automate commonly-performed tasks.
"""

import pandas
from vis.models import indexed_piece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest, interval, ngram
from vis.analyzers.experimenters import frequency, aggregator


class WorkflowController(object):
    """
    The WorkflowController automates several commonly-performed music analysis patterns.

    There are four basic tasks the WorkflowController performs, each with its own method:
    * :meth:`load`, which imports analysis data from extrnal formats, like symbolic musical scores,
        HDF5, Stata, or pickled data.
    * :meth:`run`, which blahd blah.
    * :meth:`output`, which blajal jkllkjasd, and
    * :meth:`export`, for asdf.
    """

    # Instance Variables
    # - self._data = list of IndexedPieces
    # - self._result = result of the most recent call to run()

    def __init__(self, vals):
        """
        This is how to instantiate a WorkflowController.

        If you simply want to use the WorkfloController, you should provide a list of pathnames
        corresponding to the files you want to analyze. If you want to access the
        :class:`vis.models.indexed_piece.IndexedPiece` objects directly, you should provide a list
        of those to the WorkflowController.

        Parameters
        ==========
        :parameter vals: A list of pathnames or IndexedPieces. If an item in the list is not either
            an IndexedPiece or basestring, it is silently ignored.
        :type vals: :obj:`list` of :obj:`basestring` or of :obj:`IndexedPiece`
        """
        post = []
        for each_val in vals:
            if isinstance(each_val, basestring):
                post.append(indexed_piece.IndexedPiece(each_val))
            elif isinstance(each_val, indexed_piece.IndexedPiece):
                post.append(each_val)
        self._data = post

    def load(self, instruction, pathname=None):
        """
        Import analysis data from long-term storage on a filesystem. This should primarily be used
        for the u'pieces' instruction, to control when the initial music21 import will happen.

        Parameters
        ==========
        :parameter instruction: Either u'pieces', to import all pieces, collect metadata, and run
            the NoteRestIndexer (using multiprocessing); or u'hdf5', u'stata', or u'pickle' to load
            data from a previous attempt. NOTE: only u'pieces' works at this time.
        :type instruction: :obj:`basestring`

        :parameter pathname: The pathname of the data to import; not required for the u'pieces'
            instruction.
        :type pathname: :obj:`basestring`

        Returns
        =======
        :returns: The loaded data.
        :rtype: :obj:`list` :class:`pandas.Series`
        """
        # TODO: rewrite this with multiprocessing
        # NOTE: you may want to have the worker process create a new IndexedPiece object, import it
        #       and run the NoteRestIndexer, then pickle it and send that to a callback method
        #       that will somehow unpickle it and replace the *data in* the IndexedPieces here, but
        #       not actually replace the IndexedPieces, since that would inadvertently cancel the
        #       client's pointer to the IndexedPieces, if they have one
        for piece in self._data:
            piece.get_data([noterest.NoteRestIndexer])

    def run(self, instruction, settings=None):
        """
        Run a commonly-requested experiment workflow.

        Parameters
        ==========
        :parameter instruction: The experiment workflow to run.
        :type instruction: :obj:`basestring`
        :parameter settings: Settings to be shared across all experiments that will be run. Refer
            to the relevant indexers' :obj:`possible_settings` property to know the relevant
            settings. Default is None.
        :type settings: :obj:`dict`

        Returns
        =======
        :returns: The result of the experiment workflow.
        :rtype: :class:`pandas.Series` or :class:`pandas.DataFrame`

        Raises
        ======
        :raises: :exc:`RuntimeError` if the :obj:`instruction` does not make sense.

        Instructions:
        - "all-combinations intervals": finds the frequency of vertical intervals in all
            2-part voice combinations.
        - "all 2-part interval n-grams": finds the frequency of 2-part vertical interval n-grams
            in all voice pair combinations. You should substitute "n" with a number.
        - "all-voice interval n-grams": finds the frequency of all-part vertical interval n-grams.
            You should substitute "n" with a number.

        Modifiers:
        - " for SuperCollider": append this ot "all-combinations intervals" to prepare a DataFrame
            with the information required for Mike Winters' sonification program. You should then
            call :meth:`export` with the u'CSV' instruction.
        """
        # NOTE: do not re-order the instructions or this method will break
        possible_instructions = [u'all-combinations intervals',
                                 u'all 2-part interval n-grams',
                                 u'all-voice interval n-grams']
        error_msg = u'WorkflowController.run() could not parse the instruction'
        post = None
        # run the experiment
        if len(instruction) < min([len(x) for x in possible_instructions]):
            raise RuntimeError(error_msg)
        if instruction.startswith(possible_instructions[0]):
            post = self._intervs(settings)
        elif instruction.startswith(possible_instructions[1]):
            post = self._two_part_modules(settings)
        elif instruction.startswith(possible_instructions[2]):
            post = self._all_part_modules(settings)
        else:
            raise RuntimeError(error_msg)
        # format for SuperCollider, if required
        if -1 != instruction.rfind(u' for SuperCollider'):
            post = WorkflowController._for_sc(post)
        return post

    def _two_part_modules(self, settings):
        """
        Prepare a list of frequencies of two-voice interval n-grams in all pieces. These indexers
        and experimenters will run:
        * :class:`IntervalIndexer`
        * :class:`HorizontalIntervalIndexer`
        * :class:`NGramIndexer`
        * :class:`FrequencyExperimenter`
        * :class:`ColumnAggregator`

        :parameter settings: Settings to be shared across all experiments that will be run. Refer
            to the relevant indexers' :obj:`possible_settings` property to know the relevant
            settings.
        :type settings: :obj:`dict`
        :returns: The result of :class:`ColumnAggregator`
        :rtype: :class:`pandas.Series`
        """
        pass

    def _all_part_modules(self, settings):
        """
        Prepare a list of frequencies of all-voice interval n-grams in all pieces. These indexers
        and experimenters will run:
        * :class:`IntervalIndexer`
        * :class:`HorizontalIntervalIndexer`
        * :class:`NGramIndexer`
        * :class:`FrequencyExperimenter`
        * :class:`ColumnAggregator`

        :parameter settings: Settings to be shared across all experiments that will be run. Refer
            to the relevant indexers' :obj:`possible_settings` property to know the relevant
            settings.
        :type settings: :obj:`dict`
        :returns: The result of :class:`ColumnAggregator`
        :rtype: :class:`pandas.Series`
        """
        pass

    def _intervs(self, settings):
        """
        Prepare a list of frequencies of intervals between all voice pairs of all pieces. These
        indexers and experimenters will run:
        * :class:`IntervalIndexer`
        * :class:`FrequencyExperimenter`
        * :class:`ColumnAggregator`

        :parameter settings: Settings to be shared across all experiments that will be run. Refer
            to the relevant indexers' :obj:`possible_settings` property to know the relevant
            settings.
        :type settings: :obj:`dict`
        :returns: The result of :class:`ColumnAggregator`
        :rtype: :class:`pandas.Series`
        """
        int_freqs = []
        for piece in self._data:
            vert_ints = piece.get_data([noterest.NoteRestIndexer, interval.IntervalIndexer],
                                       settings)
            # aggregate results from all voice pairs and save for later
            int_freqs.append(piece.get_data([frequency.FrequencyExperimenter,
                                             aggregator.ColumnAggregator],
                                            {},
                                            list(vert_ints.itervalues())))
        agg_p = AggregatedPieces(self._data)
        post = agg_p.get_data([aggregator.ColumnAggregator], None, {}, int_freqs)
        post.sort(ascending=False)
        return post

    @staticmethod
    def _for_sc(to_format):
        """
        Format a record for output to the vis SuperCollider application.

        :parameter to_format: The experimental results to be formatted.
        :type to_format: ???
        :returns: The results, formatted for SuperCollider.
        :rtype: ???
        """
        pass

    def output(self, instruction, pathnme=None):
        """
        Write visualization output to a file.

        Parameters
        ==========
        :parameter instruction: The type of visualization to output.
        :type instruction: :obj:`basestring`
        :parameter pathname: The pathname for the output. If not specified, we will choose.
        :type pathname: :obj:`basestring`

        Returns
        =======
        :returns: The pathname of the outputted visualization.
        :rtype: :obj:`unicode`

        Instructions:
        - u'LilyPond': not yet sure what this will be like...
        - u'R histogram': a histogram with ggplot2 in R.
        """
        pass

    def export(self, form, pathname=None):
        """
        Save the most recent return value of :meth:`run` to a file on disk.

        Parameters
        ==========
        :parameter form: The output format you want.
        :type form: :obj:`basestring`
        :parameter pathname: The pathname for the output. If not specified, we will choose.
        :type pathname: :obj:`basestring`

        Returns
        =======
        :returns: The pathname of the outputted file.
        :rtype: :obj:`unicode`

        Formats:
        - u'CSV': output a Series or DataFrame to a CSV file.
        - u'HDF5': output a Series or DataFrame to an HDF5 file.
        - u'pickle': save everything to a pickle file so we can re-load the current state later
            (NOTE: this does not work yet)
        - u'Stata': output a Stata file for importing to R.
        - u'Excel': output an Excel file for Peter Schubert.
        """
        pass
