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
    From music21.metadata.Metadata:
    - alternativeTitle
    - composer
    - composers
    - date
    - localeOfComposition
    - movementName
    - movementNumber
    - number
    - opusNumber
    - title (only field we *must* have; at worst, it's pathname without extension)
    """

    # About the Data Model (for self._data)
    # =====================================
    # - All the indices are stored in a dict.
    # - Indices of the dict will be unicode()-format class names of the Indexer, as returned by
    #   each Indexer subclass's "name()" function.
    # - how can we store multiple results from the same Indexer, generated with different settings?

    # - for an Indexer, the stored item will be a list of pandas.Series objects, where the index
    #   of a part will be the same in self._metadata{'part names'} and this list. Each list item
    #   will be a 2-tuple, in which:
    #   - index 0 shall hold We can easily
    #   convert these into music21.stream.Stream objects, to use getElementsAtOffset() to help with
    #   the iter() method. Items in the Series, therefore, must be stored in a
    #   music21.base.ElementWrapper.
    # - for an Experiment, the stored item will be a 2-tuple, where element 0 holds a dict of the
    #   settings provided to the Experiment, and element 1 holds a pandas.DataFrame of the results
    #   produced by the Experiment.

    def __init__(self, pathname, **args):
        super(IndexedPiece, self).__init__(args)
        self._metadata = {'pathname': pathname}
        self._data = {}

    def __repr__(self):
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

    def add_index(self, which_indexers, which_settings={}):
        """
        Run an indexer (or some indexers) on the score and save the results. If the indexer has
        already been run with the same settings, the previously-calculated results are returned.

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

        Parameters
        ==========
        which_indexers : list
            A list of the vis.controllers.indexer.Indexer subclasses to run on the IndexedPiece.

        which_settings : dict
            A dict of the settings to provide the Indexer. Default is {}.

        Returns
        =======
        pandas.Series :
            The result produced by the Indexer subclass.

        Raises
        ======
        RuntimeException :
            If "which_experiments" refers to an unknown Indexer subclass, or the Indexer subclass
            raises an exception.

        Side Effects
        ============
        Results from the Indexer, and any additional Indexer subclasses required for the
        "which_index" Indexer subclass, are saved in the IndexedPiece.
        """
        pass

    def remove_index(self, **args):
        """
        To save on memory, or for some other reason like it's suddenly invalied, remove certain
        information from this IndexedPiece.

        You might want to do this, for example, after parsing chords from a piano texture.
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

    @staticmethod
    def _find_part_names(the_score):
        """
        Copy this from importer.py
        """
        pass

    @staticmethod
    def _find_piece_title(the_score):
        """
        Copy this from importer.py
        """
        pass
