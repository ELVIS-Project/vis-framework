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

from vis.models import indexed_piece
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.indexers import noterest


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

    def run(self, instruction):
        """
        Run a commonly-requested experiment workflow.

        Parameters
        ==========
        :parameter instruction: The experiment workflow to run.
        :type instruction: :obj:`basestring`

        Returns
        =======
        :returns: The result of the experiment workflow.
        :rtype: :class:`pandas.Series` or :class:`pandas.DataFrame`

        Instructions:
        - "all-combinations intervals": finds the frequency of vertical intervals in all
            2-part voice combinations.
        - "all 2-part interval n-grams": finds the frequency of 2-part vertical interval n-grams
            in all voice pair combinations. You should substitute "n" with a number.
        - "all-voice interval n-grams": finds the frequency of all-part vertical interval n-grams.
            You should substitute "n" with a number.

        Modifiers:
        - " for R": append this to any instruction to produce output in a format more suitable for
            R, which likes to count things by itself. Rather than a simple DataFrame with an object
            and its number of occurrences, this would simply produce a Series where each object
            appears the appropriate number of times. You should then call :meth:`export` with the
            u'Stata' instruction or :meth:`output` with the u'R histogram' instruction.
        - " for SuperCollider": append this ot "all-combinations intervals" to prepare a DataFrame
            with the information required for Mike Winters' sonification program. You should then
            call :meth:`export` with the u'CSV' instruction.
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
        - u'R histogram': a histogram with ggplot2 in R. You should have just run :meth:`run` with
            the " for R" modifier.
        """
        pass

    def export(self, format, pathname=None):
        """
        Save the most recent return value of :meth:`run` to a file on disk.

        Parameters
        ==========
        :parameter format: The output format you want.
        :type format: :obj:`basestring`
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
