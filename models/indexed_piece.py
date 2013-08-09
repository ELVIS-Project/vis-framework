#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
#
# Copyright (C) 2013 Christopher Antila, Jamie Klassen
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

# Imports
from inspect import getmembers, isdatadescriptor
import re
import os
from music21 import converter
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.indexer import Indexer


def _find_piece_title(the_score):
    """
    Find the title of a Score. If there is none, return the filename without extension.

    Parameters
    ==========
    :param the_score: The score of which to find the title.
    :type the_score: music21.stream.Score

    Returns
    =======
    :returns: The title of the score.
    :rtype: unicode
    """
    # First try to get the title from a Metadata object, but if it doesn't
    # exist, use the filename without directory.
    if the_score.metadata is not None:
        post = the_score.metadata.title
    elif hasattr(the_score, 'filePath'):
        post = os.path.basename(the_score.filePath)
    else:  # if the Score was part of an Opus
        post = u'Unknown Piece'

    # Now check that there is no file extension. This could happen either if
    # we used the filename or if music21 did a less-than-great job at the
    # Metadata object.
    post = os.path.splitext(post)[0]

    return post


def _find_part_names(the_score):
    """
    Return a list of part names in a score. If the score does not have proper names, return a
    list of enumerated parts.

    Parameters
    ==========
    :param the_score:
        The score in which to find the part names.
    :type the_score: music21.stream.Score

    Returns
    =======
    :returns: The title of the score.
    :rtype: list of unicode
    """
    # hold the list of part names
    post = []

    # First try to find Instrument objects. If that doesn't work, use the "id"
    for each_part in the_score.parts:
        instr = each_part.getInstrument()
        if instr is not None and instr.partName != u'':
            post.append(unicode(instr.partName))
        else:
            post.append(unicode(each_part.id))

    # Make sure none of the part names are just numbers; if they are, use
    # a part name like "Part 1" instead.
    for part_index in xrange(len(post)):
        try:
            int(post[part_index])
            # if that worked, the part name is just an integer...
            post[part_index] = u'Part ' + unicode(part_index + 1)
        except ValueError:
            pass

    return post


class IndexedPiece(object):
    """
    Holds the indexed data from a musical score.
    """
    # pylint: diable=R0903
    class Metadata(object):
        """
        Holds metadata for an IndexedPiece. At present, it contains the following fields:

        alternative_title
            A possible alternate title for the piece; e.g. Beethoven's Symphony No. 6 in F Major
            is also known as the 'Pastoral' Symphony. Taken from music21.
        anacrusis
            The length of the pick-up measure, if there is one.
        composer
            The author of the piece. Taken from music21.
        composers
            If the piece has multiple authors. Taken from music21.
        date
            The date that the piece was composed or published. Taken from music21.
        locale_of_composition
            Where the piece was composed. Taken from music21.
        movement_name
            If the piece is part of a larger work, the name of this subsection. Taken from music21.
        movement_number
            If the piece is part of a larger work, the number of this subsection. Taken from
            music21.
        number
            Taken from music21.
        opus_number
            Number assigned by the composer to the piece or a group containing it, to help with
            identification or cataloguing. Taken from music21.
        parts
            A list of the parts in a multi-voice work.
        pathname
            The filesystem path to the music file encoding the piece.
        title
            The title of the piece. Taken from music21.
        """
        __slots__ = (u'opus_number', u'movement_name', u'composer', u'number', u'anacrusis',
                     u'movement_number', u'date', u'composers', u'alternative_title', u'title',
                     u'locale_of_composition', u'parts', u'pathname')

        def __init__(self, pathname):
            super(IndexedPiece.Metadata, self).__init__()
            self.opus_number = None
            self.movement_name = None
            self.composer = None
            self.number = None
            self.anacrusis = None
            self.movement_number = None
            self.date = None
            self.composers = None
            self.alternative_title = None
            self.title = None
            self.locale_of_composition = None
            self.parts = None
            self.pathname = pathname

    def __init__(self, pathname):
        super(IndexedPiece, self).__init__()
        self._metadata = self.__class__.Metadata(pathname)
        self._imported = False

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

    def _import_score(self):
        """
        Import the score to music21 format.

        :returns: the score
        :rtype: music21.stream.Score or music21.stream.Opus
        """
        score = converter.parse(self.metadata('pathname'))
        if not self._imported:
            def convert(name):
                """
                converts camelCase strings (as properties in music21 are named) to snake-case
                strings (which are what Python idiom dictates we should use)

                Taken from :
                http://stackoverflow.com/
                questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
                :param name: a camelCase string
                :return: a snake-case string
                """
                name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
                return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()

            # find all the properties (i.e. methods with the @property decorator)
            # for music21.metadata.Metadata which are also in our Metadata prototype
            for name, obj in getmembers(score.metadata.__class__, isdatadescriptor):
                if u'title' == name:
                    self.metadata(name, _find_piece_title(score))
                elif isinstance(obj, property) and hasattr(self._metadata, convert(name)):
                    self.metadata(convert(name), obj)
                    # music21 doesn't have a "part names" attribute in its Metadata objects
            self.metadata(u'parts', _find_part_names(score))
            self._imported = True
        return score

    def metadata(self, field, value=None):
        # TODO: update doctest so that it actually works
        """
        Get or set metadata about the piece, like filename, title, and composer.

        :param field: The name of the field to be accessed or modified
        :type field: str or unicode
        :param value: If not None, the new value to be assigned to ``field``
        :type value: object or None
        :returns: object -- the field accessed, or None -- if assigning a field or attempting to
            access a field that does not exist..

        >>> piece = IndexedPiece('a_sibelius_symphony.mei')
        >>> piece.metadata('composer')
        u'Jean Sibelius'
        >>> piece.metadata('year', 1919)
        >>> piece.metadata('year')
        1919
        >>> piece.metadata('parts')
        [u'Flute 1', u'Flute 2', u'Oboe 1', u'Oboe 2', u'Clarinet 1', u'Clarinet 2', ... ]
        """
        if not isinstance(field, basestring):
            raise TypeError("parameter 'field' must be of type 'basestring'")
        if value is None:
            if hasattr(self._metadata, field):
                return getattr(self._metadata, field)
            else:
                if not self._imported:
                    self._import_score()
                    return self.metadata(field, value)
        else:
            setattr(self._metadata, field, value)

    def get_data(self, analyzer_cls, data=None, settings=None):
        """
        Get the analysis from a specific analyzer run on this piece.

        :param analyzer_cls: the analyzer to run
        :type analyzer_cls: type
        :param data: the information for the analyzer to use
        :type data: pandas.Series or pandas.DataFrame
        :param settings: the settings to be used with the analyzer
        :type settings: dict
        :return: the results of the analysis
        """
        if data is None:
            data = self._import_score()
        if not issubclass(analyzer_cls, (Indexer, Experimenter)):
            raise TypeError(u'can only get data for Indexers or Experimenters, '
                            u'not {}'.format(analyzer_cls))
        instance = analyzer_cls(data, settings)
        return instance.run()
