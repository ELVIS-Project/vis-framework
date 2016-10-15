#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------- #
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/noterest.py
# Purpose:                Index note and rest objects.
#
# Copyright (C) 2013, 2014, 2015 Christopher Antila, and Alexander 
# Morgan
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
# You should have received a copy of the GNU Affero General Public 
# License along with this program. If not, see 
# <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------- #
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Alexander Morgan

Index note and rest objects into pandas DataFrame(s).

"""

import six
import pandas
from music21 import pitch, note, chord
from vis.analyzers import indexer

def noterest_ind_func(event):
    """
    Used internally by :class:`NoteRestIndexer`. Convert 
    :class:`~music21.note.Note`, :class:`~music21.note.Rest`, and 
    :class:`~music21.chord.Chord`objects into strings. For the chords, 
    only the first pitch of the chord is kept which is usually the 
    highest pitch. If you want to keep all the pitches in chords, 
    consider using the :class:`MultiStopIndexer` instead.

    :param event: A music21 note, rest, or chord object which get 
        queried for their names.
    
    :type event: A music21 note, rest, or chord object.

    :returns: A one-tuple containing a string representation of the note 
        or rest, or if the event is a chord, a list of the strings of 
        the names of its constituent pitches.
    
    :rtype: 1-tuple of str or list of strings

    **Examples:**
    
    >>> from noterest.py import indexer_func
    >>> from music21 import note, 
    >>> indexer_func(note.Note('C4'))
    u'C4'
    >>> indexer_func(note.Rest())
    u'Rest'
    >>> indexer_func(chord.Chord([note.Note('E5'), note.Note('C4')]))
    u'E5'
    
    """
    if isinstance(event, float):
        return event
    elif event.isNote:
        return six.u(event.nameWithOctave)
    elif event.isRest:
        return u'Rest'
    else: # The event is a chord
        return six.u(event.pitches[0].nameWithOctave)

def multistop_ind_func(event):
    """
    Used internally by :class:`MultiStopIndexer`. Convert 
    :class:`~music21.note.Note` and :class:`~music21.note.Rest` objects 
    into a string and convert the :class:`~music21.chord.Chord` objects 
    into a list of the strings of their consituent pitch objects. The 
    results must be contained in a tuple or a list so that chords can 
    later be unpacked into different 1-voice strands.

    :param event: A music21 note, rest, or chord object which get 
        queried for their names.
    
    :type event: A music21 note, rest, or chord object.

    :returns: A one-tuple containing a string representation of the note 
        or rest, or if the event is a chord, a list of the strings of 
        the names of its constituent pitches.
    
    :rtype: 1-tuple of str or list of strings

    **Examples:**
    
    >>> from noterest.py import indexer_func
    >>> from music21 import note, 
    >>> indexer_func(note.Note('C4'))
    (u'C4',)
    >>> indexer_func(note.Rest())
    (u'Rest',)
    >>> indexer_func(chord.Chord([note.Note('C4'), note.Note('E5')]))
    [u'C4', u'E5']
    
    """
    if isinstance(event, float):
        return event
    elif event.isNote:
        return (six.u(event.nameWithOctave),)
    elif event.isRest:
        return (u'Rest',)
    else: # The event is a chord
        return [six.u(p.nameWithOctave) for p in event.pitches]

def unpack_chords(df):
    """
    The c in nrc in methods like _get_m21_nrc_objs() stands for chord. 
    This method unpacks music21 chords into a list of their constituent 
    pitch objects. These pitch objects can be queried for their 
    ``nameWithOctave`` in the same way that note objects can in music21.
    This works by broadcasting the list of pitches in each chord object 
    in each part's elements to a dataframe of note, pitch, and rest 
    objects. So each part that had chord objects in it gets represented 
    as a dataframe instead of just a series. Then the series from the 
    parts that didn't have chords in them get concatenated with the 
    parts that did, resulting in potentially more columns in the final 
    dataframe then there are parts in the score.
    """
    post = pandas.concat([pandas.DataFrame(df.iloc[:,x].dropna().tolist(),
                                           index=df.iloc[:,x].dropna().index)
                          for x in range(len(df.columns))], axis=1)
    return post.fillna(float('nan')) 
    # without this fillna call, some na values are None's.


class NoteRestIndexer(indexer.Indexer):
    """
    Index :class:`~music21.note.Note` and :class:`~music21.note.Rest` 
    objects in a :class:`~music21.stream.Part`.

    :class:`Rest` objects become ``'Rest'``, and :class:`Note` objects 
    become the string-format version of their 
    :attr:`~music21.note.Note.nameWithOctave` attribute.

    This indexer is meant to be called indirectly with a call to 
    ``get_data`` on an indexed piece in the manner of the following 
    example.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')
    >>> ip.get_data('noterest')
    
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: A dataframe of the note, rest, and chord objects 
            in a piece.
        
        :type score: pandas Dataframe
        
        :raises: :exc:`RuntimeError` if ``score`` is not a pandas 
            Dataframe.
        
        """
        super(NoteRestIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = noterest_ind_func

    # NB: The noterest indexer inherits the run() method from indexer.py

class MultiStopIndexer(indexer.Indexer):
    """
    Index :class:`~music21.note.Note`, :class:`~music21.note.Rest`, and 
    :class:`~music21.chord.Chord` objects in a 
    :class:`~pandas.DataFrame`.

    :class:`Rest` objects become ``'Rest'``, and :class:`Note` objects 
    become the string-format version of their 
    :attr:`~music21.note.Note.nameWithOctave` attribute.
    :class:`~music21.chord.Chord` objects get unpacked into their 
    constituent pitches.

    This indexer is meant to be called indirectly with a call to 
    ``get_data`` on an indexed piece in the manner of the following 
    example.

    **Example:**

    >>> from vis.models.indexed_piece import Importer
    >>> ip = Importer('path_to_piece.xml')
    >>> ip.get_data('multistop')
    
    """

    required_score_type = 'pandas.DataFrame'

    def __init__(self, score):
        """
        :param score: A dataframe of the note, rest, and chord objects 
            in a piece.
        
        :type score: pandas Dataframe
        
        :raises: :exc:`RuntimeError` if ``score`` is not a pandas 
            Dataframe.
        
        """
        super(MultiStopIndexer, self).__init__(score, None)
        self._types = ('Note', 'Rest', 'Chord')
        self._indexer_func = multistop_ind_func

    def run(self):
        """
        Make a new index of the note and rest names in the piece. When a 
        single part has chord objects, those chords get separated out 
        into as many columns as there are notes in the chord with the 
        greatest number of notes. This means that there can be more 
        columns in this dataframe than there are parts in the piece.

        :returns: A :class:`DataFrame` of the new indices. 
            The columns have a :class:`MultiIndex`.
        
        :rtype: :class:`pandas.DataFrame`
        
        """
        # This if statement is necessary because of a pandas bug, see 
        # pandas issue #8222.
        if len(self._score.index) == 0: 
            # If parts have no note, rest, or chord events in them
            result = self._score.copy()
        else: # This is the normal case
            temp = self._score.applymap(self._indexer_func) 
            # Do indexing.
            result = unpack_chords(temp) 
            # Unpack chords into individual pitches.
        return self.make_return([str(x) 
            for x in range(len(result.columns))], result)
