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
from music21 import converter, stream
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
    # pylint: disable=R0903
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
            access a field that does not exist.
        :raises: TypeError -- if ``field`` is not a basestring, AttributeError -- if attempting
            to set a field which is not in the :py:class:`IndexedPiece.Metadata` prototype.

        >>> piece = IndexedPiece('a_sibelius_symphony.mei')
        >>> piece.metadata('composer')
        u'Jean Sibelius'
        >>> piece.metadata('date', 1919)
        >>> piece.metadata('date')
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
            # since we explicitly set the __slots__ variable in the Metadata class definition,
            # this will raise an AttributeError if you try to set a nonexistent field.
            setattr(self._metadata, field, value)

    def get_data(self, analyzer_cls, settings=None, data=None):
        """
        Get the results of an Experimenter or Indexer run on this IndexedPiece.

        Parameters
        ==========
        :param analyzer_cls: the analyzers to run, in the order they should be run
        :type analyzer_cls: list of types

        :param settings: Settings to be used with the analyzers.
        :type settings: dict

        :param data: Input data for the first analyzer to run. If the first indexer uses a Score,
            you should leave this as None.
        :type data: list of pandas.Series or pandas.DataFrame

        Returns
        =======
        :returns: Results of the analyzer.
        :rtype: pandas.DataFrame or list of pandas.Series

        Raises
        ======
        TypeError: If the "analyzer_cls" is invalid or cannot be found.
        RuntimeError: If the first analyzer class in "analyzer_cls" does not use Score objects, and
            the "data" argument is None.
        NotImplementedError: If the file imports as a music21.stream.Opus object, since we cannot
            yet deal with those properly (since they should be treated as more than one piece).
        """
        for each_cls in analyzer_cls:
            if not issubclass(each_cls, (Indexer, Experimenter)):
                raise TypeError(u'IndexedPiece requires an Indexer or Experimenter '
                                u'(received {})'.format(analyzer_cls))
        if data is None:
            if issubclass(analyzer_cls[0], Indexer) and analyzer_cls[0].requires_score:
                data = self._import_score()
            else:
                msg = u'{} is missing required data from another analyzer.'.format(analyzer_cls[0])
                raise RuntimeError(msg)
            if isinstance(data, stream.Opus):
                # TODO: finish this and test it (we'll need to deal with Opus objects somehow)
                raise NotImplementedError(u'IndexedPiece cannot process music21 Opus objects')
            else:
                data = [x for x in data.parts]  # Indexers require a list of Parts
        if len(analyzer_cls) > 1:
            return self.get_data(analyzer_cls[1:], settings, analyzer_cls[0](data, settings).run())
        else:
            return analyzer_cls[0](data, settings).run()
