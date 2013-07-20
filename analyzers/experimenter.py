#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/experimenter.py
# Purpose:                Help with transforming time-attached analytic information to other types.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
The controllers that deal with experimenting on indices or the results of other experiments.
Whereas an Indexer produces information that can be attached to a particular moment of a score,
an Experimenter produces information that can't sensibly be described as starting at the beginning
and going to the end of a piece.
"""


class Experimenter(object):
    # NB: Change "object" to "Experimenter" in subclasses.
    """
    Run an experiment on an IndexedPiece.

    Use the "Experimenter.needed_indices" attribute to know which Indexer subclasses should have
    been run on the IndexedPiece. If they have not been run, they will be run before this experiment
    is conducted.

    Use the "Experimenter.needed_experiments" attribute to know which, if any, Experimenter
    subclasses should have been run on the IndexedPiece. If they have not yet been run, they will
    be run before this experiment is conducted.

    The name of the experimenter, as stored in an IndexedPiece, is the unicode-format version of
    the class name, accessible through the "name()" function (or Experimenter.__name__).
    """

    # NB: you should re-implement these in subclasses
    needed_indices = []
    needed_experiments = []

    def __init__(self, score, settings={}):
        """
        Create a new Experimenter.

        Parameters
        ==========
        score : vis.models.IndexedPiece
            The score on which to conduct this experiment.

        settings : dict
            A dict of all the settings required by this Experimenter. All required settings should
            be listed in subclasses. Default is {}.

        Raises
        ======
        RuntimeError :
            - If required settings are not present in the "settings" argument.
        """
        # NOTE: You should reimplement this method in subclasses.

        # Check that all required settings are present in the "settings" argument

        # Change the class name to the current class
        super(Experimenter, self).__init__()

        # Leave this
        self._score = score

    def name(self):
        """
        Return the name used to identify this experimenter.
        """
        # NOTE: Do not reimplement this method in subclasses.
        return unicode(self.__name__)

    def run(self):
        """
        Run an experiment on a piece.

        Returns
        =======
        pandas.Series or pandas.DataFrame :
            The result of the experiment. Data is stored somehow.
        """
        # NOTE-1: You should reimplement this method in subclasses.
        # NOTE-2: You should update the "Returns" part of the docstring to describe the format of
        #         data returned by the Experimenter.
        # NOTE-3: You must run any required Indexers or Experimenters, as specified in the
        #         "needed_indices" and "needed_experiments" class properties.
        pass


class IntervalFrequencyExperimenter(Experimenter):
    """
    Count the number of occurrences of intervals in a piece.
    """

    needed_indices = ['NoteRestIndexer']

    def __init__(self, score, settings={}):
        """
        Create a new IntervalFrequencyExperimenter.

        Parameters
        ==========
        score : vis.models.IndexedPiece
            The score on which to conduct this experiment.

        settings : dict
            A dict of all the settings required by this Experimenter. Includes:
            - 'simple or compound' : 'simple' or 'compound'
                Whether intervals should be represented in their single-octave form. Optional.
                Defaults to 'compound'
            - 'quality' : boolean
                Whether to consider the quality of intervals. Optional. Defaults to False.

        Raises
        ======
        Nothing. There are no required settings.
        """
        # Check that all required settings are present in the "settings" argument
        self._settings = {}
        if 'simple or compound' in settings:
            self._settings['simple or compound'] = settings['simple or compound']
        else:
            self._settings['simple or compound'] = 'compound'
        if 'quality' in settings:
            self._settings['quality'] = settings['quality']
        else:
            self._settings['quality'] = False
        # Other stuff
        super(IntervalFrequencyExperimenter, self).__init__()
        self._score = score

    def run(self):
        """
        Count the number of occurrences of intervals in all voice-pair combinations, then create a
        summary of all of them.

        Returns
        =======
        pandas.DataFrame :
            Data is stored somehow. We'll always just run all voice pairs the first time, and
            create another field that stores totals for all voice pairs together.
        """
        # NOTE-1: You should reimplement this method in subclasses.
        # NOTE-2: You should update the "Returns" part of the docstring to describe the format of
        #         data returned by the Experimenter.
        # NOTE-3: You must run any required Indexers or Experimenters, as specified in the
        #         "needed_indices" and "needed_experiments" class properties.

        # Implementation notes:
        # - I'll probably want to somehow accumulate a list of all the intervals in each of the
        #   voice-pair combinations.
        # - I'll probably want to do multiprocessing, one process per voice pair
        # - I'll want to make sure to have already run the Indexer that labels intervals from start
        #   to finish, in all voice pairs... wonder how to coordinate that!
        pass
