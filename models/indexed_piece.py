#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
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
The model representing an indexed and analyzed piece of music.
"""


class IndexedPiece(object):
    """
    Holds the indexed data from a musical score.

    Here is a list of all the metadata we'll have about a piece:
    From vis:
    - pathname
    - part names
    - quarterLength duration of anacrusis, if applicable
    From musi21.metadata.Metadata:
    - alternativeTitle
    - composer
    - composers
    - date
    - localeOfComposition
    - movementName
    - movementNumber
    - number
    - opusNumber
    - title
    """

    # About the Data Model (for self._data)
    # =====================================
    # - All the indices and experiment results are stored in a dict.
    # - Indices of the dict will be unicode()-format class names of the Indexer or Experiment
    # - for an Indexer, the stored item will be a pandas.Series, which we can easily convert into a
    #   music21.stream.Stream, so we can use getElementsAtOffset() to help with the iter() method.
    #   Items in the Series, therefore, must be stored in a music21.base.ElementWrapper.
    # - for an Experiment, the stored item will be a 2-tuple, where element 0 holds a dict of the
    #   settings provided to the Experiment, and element 1 holds a pandas.DataFrame of the results
    #   produced by the Experiment.

    def __init__(self, pathname, **args):
        super(IndexedPiece, self).__init__(args)
        self._metadata = {'pathname': pathname}
        self._data = {}

    def __repr(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

    def metadata(self, field, value=None):
        """
        Get or set metadata about the piece, like filename, title, and composer.

        It'll be like this:
        >>> piece.metadata('composer')
        u'Jean Sibelius'
        >>> piece.metadata('year', 1919)
        >>> piece.metadata('year')
        1919

        If the piece hasn't yet been imported, and none of the file-derived metadata are available
        yet, an exception will be raised (KeyError) *unless* the field has been set manually, in
        which case its value is returned. If the piece *has* been imported, and you try to get a
        metadatum that isn't available, we'll just return None.
        """
        pass

    def indexers_used(self):
        """
        Return a list of the names of the indexers used so far in this IndexedPiece.
        """
        pass

    def experiments_used(self):
        """
        Return a list of the names of the experiments used so far in this IndexedPiece.
        """
        pass

    def _add_index(self, which_indexer):
        """
        For internal use. Without any additional checking, just run the specified indexer and
        add its results to the DataFrame.

        Maybe we won't need this.
        """
        pass

    def add_index(self, which_indexers):
        """
        Run an indexer (or some indexers) on the score.

        During the initial import/indexation stage, you'll just call this method with a list of
        indices to add, in which case we'll run the indexation processes in parallel. If only one
        indexer is given, we'll not use multiprocessing. Not sure this is possible quite like
        this, but I guess we'll figure it out.

        This method checks whether the piece has ever been imported yet. If not, it'll be done now,
        and the offsets will be indexed first, since it's needed for everything else, and the
        metadata will also be collected from the file.

        Also, since the Score object is never actually retained after the add_indexation() method
        finishes, it makes sense to supply a list of all the indices you'll want, all at the same
        time, so that the import need only happen once.

        BUT: I think not all the indexers will need the music21 Score object, since some of them
        will use the results of other indexers, like the thing that labels interval series through
        the score.
        """
        # NB: use the Indexer.needs_score attribute to know whether to import the Score
        pass

    def add_experiment(self, which_experiments, which_settings):
        """
        Run an experiment (or some experiments) on the score and save the results. If the
        experiment has already been run with the same settings, the previously-calculated results
        are returned.

        Parameters
        ==========
        which_experiments : list
            A list of the vis.models.experiment.Experiment subclasses to run on the IndexedPiece.

        which_settings : dict
            A dict of the settings to provide the Experiment.

        Returns
        =======
        pandas.DataFrame :
            The result produced by the Experiment subclass.

        Raises
        ======
        RuntimeException :
            If "which_experiments" refers to an unknown Experiment subclass.

        Side Effects
        ============
        Results from the Experiment, and any additional Experiment subclasses or Indexer subclasses
        required for the "which_experiment" Experiment subclass, are saved in the IndexedPiece.
        """
        pass

    def remove_index(self, **args):
        """
        To save on memory, or for some other reason like it's suddenly invalied, remove the
        particular indexed information from this IndexedPiece.

        You might want to do this after, for example, when parsing chords from a piano texture.
        """
        pass

    def iter(self, index, parts, offset=None, repeated=False):
        """
        Get an iterable for events from the beginning to the end of the piece.

        Parameters
        ==========
        index : subclass of vis.controllers.indexers.Indexer
            The indexer whose output you wish to access.

        parts : list or integer
            Either an integer, corresponding to the part whose index you want, or a list of the
            integers corresponding to the parts whose indices you want.

        offset : float or None
            Either the quarterLength offset between events you wish to consider, or "None," which
            is the default, which returns every recorded event.

        repeated : boolean
            Whether to return events that are identical to the previously-returned event. Default
            is False.

        Returns
        =======
        Either a music21.base.ElementWrapper (if "parts" was an integer) or else a list of
        ElementWrapper objects. The "obj" attribute of an ElementWrapper instance holds the
        indexed data.

        Raises
        ======
        RuntimeError :
            - If the "index" class has not been used in this IndexedPiece.
        """
        pass

    def get_experiment(self, which_experiment, which_settings=None):
        """
        Access the results produced by a previously-run experiment.

        Parameters
        ==========
        which_experiment : vis.models.experiment.Experiment subclass
            The experiment whose results you wish to access.

        which_settings : dict
            A dict of the settings you want to have been provided to the experiment. You can omit
            some or all of the settings the Experiment requires, in which case, if only one set of
            results matches the settings you *do* provide, they will be returned, or if multiple
            sets of results match, a RuntimeError will be raised.

        Returns
        =======
        2-tuple :
            0 : The dict of settings used to produce the results.
            1 : The result of the Experiment.

        Raises
        ======
        RuntimeError :
            If which_experiment has not yet been run on this IndexedPiece, or if the keys in
            which_settings are insufficient to choose a single experiment.
        """
        pass
