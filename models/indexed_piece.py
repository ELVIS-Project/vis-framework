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
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

This model represents an indexed and analyzed piece of music.
"""

# Imports
import os
from music21 import converter, stream
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest


def _find_piece_title(the_score):
    """
    Find the title of a score. If there is none, return the filename without an extension.

    Parameters
    ==========
    :param the_score: The score of which to find the title.
    :type the_score: :class:`music21.stream.Score`

    Returns
    =======
    :returns: The title of the score.
    :rtype: :obj:`unicode`
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
    Return a list of part names in a score. If the score does not have proper part names, return a
    list of enumerated parts.

    Parameters
    ==========
    :param the_score: The score in which to find the part names.
    :type the_score: :class:`music21.stream.Score`

    Returns
    =======
    :returns: The title of the score.
    :rtype: :obj:`list` of :obj:`unicode`
    """
    # hold the list of part names
    post = []

    # First try to find Instrument objects. If that doesn't work, use the "id"
    for each_part in the_score.parts:
        instr = each_part.getInstrument()
        if instr is not None and instr.partName != u'' and instr.partName is not None:
            post.append(unicode(instr.partName))
        elif each_part.id is not None:
            try:
                int(each_part.id)  # if it worked, the part name is an integer, so use "Part X"
                post.append(u'rename')
            except ValueError:
                # this is actually where we prefer to end up
                post.append(unicode(each_part.id))
        else:
            post.append(u'rename')

    # Make sure none of the part names are just numbers; if they are, use
    # a part name like "Part 1" instead.
    for i, part_name in enumerate(post):
        if u'rename' == part_name:
            post[i] = u''.join([u'Part ', unicode(i + 1)])

    return post


class IndexedPiece(object):
    """
    Hold indexed data from a musical score.
    """
    def __init__(self, pathname):
        """
        Create a new :class:`IndexedPiece`.

        Parameters
        ==========
        :param pathname: Pathname to the file music21 will import for this IndexedPiece.
        :type pathname: :obj:`basestring`

        Returns
        =======
        :returns: A new IndexedPiece.
        :rtype: :class:`IndexedPiece`
        """
        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length unicode.
            """
            field_list = [u'opusNumber', u'movementName', u'composer', u'number', u'anacrusis',
                u'movementNumber', u'date', u'composers', u'alternativeTitle', u'title',
                u'localeOfComposition', u'parts']
            for field in field_list:
                self._metadata[field] = u''
            self._metadata[u'pathname'] = pathname

        super(IndexedPiece, self).__init__()
        self._imported = False
        self._noterest_results = None
        self._metadata = {}
        init_metadata()

    def __repr__(self):
        return u''.join([u'vis.models.indexed_piece.IndexedPiece(u\'',
                         self.metadata(u'pathname'),
                         u'\')'])

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        post = [u'<IndexedPiece (']
        if self._imported:
            post.append(self.metadata(u'title'))
            post.append(u' by ')
            post.append(self.metadata(u'composer'))
        else:
            post.append(self.metadata(u'pathname'))
        post.append(u')>')
        return u''.join(post)

    def _import_score(self):
        """
        Import the score to music21 format.

        Returns
        =======
        :returns: the score
        :rtype: :class:`music21.stream.Score`

        Raises
        ======
        :raises: :exc:`NotImplementedError` if the file imports as a :class:`music21.stream.Opus`
            since we do not yet support them.
        """
        score = converter.parse(self.metadata('pathname'))
        if isinstance(score, stream.Opus):
            # TODO: finish this and test it (we'll need to deal with Opus objects somehow)
            raise NotImplementedError(u'IndexedPiece cannot process music21 Opus objects')
        if not self._imported:
            for field in self._metadata:
                if hasattr(score.metadata, field):
                    self._metadata[field] = getattr(score.metadata, field)
                    if self._metadata[field] is None:
                        self._metadata[field] = u'???'
            self._metadata[u'parts'] = _find_part_names(score)
            self._metadata[u'title'] = _find_piece_title(score)
            self._imported = True
        return score

    def metadata(self, field, value=None):
        """
        Get or set metadata about the piece.

        Parameters
        ==========
        :param field: The name of the field to be accessed or modified.
        :type field: :obj:`basestring`

        :param value: If not None, the new value to be assigned to ``field``.
        :type value: :obj:`object` or :obj:`None`

        Returns
        =======
        :returns: The value of the requested field or None, if assigning, or if accessing a
            non-existant field or a field that has not yet been initialized.
        :rtype: :obj:`object` or :obj:`None`

        Raises
        ======
        :raises: :exc:`TypeError` if ``field`` is not a :obj:`basestring`.
        :raises: :exc:`AttributeError` if accessing an invalid ``field`` (see valid fields below).

        +---------------------+--------------------------------------------------------------------+
        | Metadata Field      | Description                                                        |
        +=====================+====================================================================+
        | alternativeTitle    | A possible alternate title for the piece; e.g. Beethoven's         |
        |                     | Symphony No. 6 in F Major is also known as the 'Pastoral' Symphony.|
        |                     | Taken from music21.                                                |
        +---------------------+--------------------------------------------------------------------+
        | anacrusis           | The length of the pick-up measure, if there is one.                |
        +---------------------+--------------------------------------------------------------------+
        | composer            | The author of the piece. Taken from music21.                       |
        +---------------------+--------------------------------------------------------------------+
        | composers           | If the piece has multiple authors. Taken from music21.             |
        +---------------------+--------------------------------------------------------------------+
        | date                | The date that the piece was composed or published. Taken from      |
        |                     | music21.                                                           |
        +---------------------+--------------------------------------------------------------------+
        | localeOfComposition | Where the piece was composed. Taken from music21.                  |
        +---------------------+--------------------------------------------------------------------+
        | movementName        | If the piece is part of a larger work, the name of this            |
        |                     | subsection. Taken from music21.                                    |
        +---------------------+--------------------------------------------------------------------+
        | movementNumber      | If the piece is part of a larger work, the number of this          |
        |                     | subsection. Taken from music21.                                    |
        +---------------------+--------------------------------------------------------------------+
        | number              | Taken from music21.                                                |
        +---------------------+--------------------------------------------------------------------+
        | opusNumber          | Number assigned by the composer to the piece or a group            |
        |                     | containing it, to help with identification or cataloguing. Taken   |
        |                     | from music21.                                                      |
        +---------------------+--------------------------------------------------------------------+
        | parts               | A list of the parts in a multi-voice work.                         |
        +---------------------+--------------------------------------------------------------------+
        | pathname            | The filesystem path to the music file encoding the piece.          |
        +---------------------+--------------------------------------------------------------------+
        | title               | The title of the piece. Taken from music21.                        |
        +---------------------+--------------------------------------------------------------------+

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
            raise TypeError(u"metadata(): parameter 'field' must be of type 'basestring'")
        elif field not in self._metadata:
            raise AttributeError(u'metadata(): invalid field')
        if value is None:
            return self._metadata[field]
        else:
            self._metadata[field] = value

    def _get_note_rest_index(self):
        """
        Return the results of the :class:`NoteRestIndexer` on this piece.

        This method is used automatically by :meth:`get_data` to cache results, which avoids having
        to re-import the music21 file for every Indexer or Experimenter that uses the
        :class:`NoteRestIndexer`.

        Returns
        =======
        :returns: Results of the :class:`NoteRestIndexer`.
        :rtype: :obj:`list` of :class:`pandas.Series`
        """
        if self._noterest_results is None:
            data = [x for x in self._import_score().parts]
            self._noterest_results = noterest.NoteRestIndexer(data).run()
        return self._noterest_results

    def get_data(self, analyzer_cls, settings=None, data=None):
        """
        Get the results of an Experimenter or Indexer run on this :class:`IndexedPiece`.

        Parameters
        ==========
        :param analyzer_cls: the analyzers to run, in the order they should be run
        :type analyzer_cls: :obj:`list` of :obj:`type`

        :param settings: Settings to be used with the analyzers.
        :type settings: :obj:`dict`

        :param data: Input data for the first analyzer to run. If the first indexer uses a Score,
            you should leave this as None.
        :type data: :obj:`list` of :class:`pandas.Series` or :class:`pandas.DataFrame`

        Returns
        =======
        :returns: Results of the analyzer.
        :rtype: :class:`pandas.DataFrame` or :obj:`list` of :class:`pandas.Series`

        Raises
        ======
        :raises: :exc:`TypeError` if the ``analyzer_cls`` is invalid or cannot be found.
        :raises: :exc:`RuntimeError` if the first analyzer class in ``analyzer_cls`` does not use
            :class:`music21.stream.Score` objects, and ``data`` is :obj:`None`.
        :raises: :exc:`NotImplementedError` if the file imports as a :class:`music21.stream.Opus`
            object, since we cannot yet deal with those properly (since they should be treated as
            more than one piece).
        """
        # TODO: the NotImplementedError should be removed once _import_score() supports Opus
        for each_cls in analyzer_cls:
            if not issubclass(each_cls, (Indexer, Experimenter)):
                raise TypeError(u'IndexedPiece requires an Indexer or Experimenter '
                                u'(received {})'.format(analyzer_cls))
        if data is None:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                data = self._get_note_rest_index()
            if analyzer_cls[0].required_score_type == stream.Part:
                data = self._import_score()
                data = [x for x in data.parts]  # Indexers require a list of Parts
            else:
                msg = u'{} is missing required data from another analyzer.'.format(analyzer_cls[0])
                raise RuntimeError(msg)
        if len(analyzer_cls) > 1:
            return self.get_data(analyzer_cls[1:], settings, analyzer_cls[0](data, settings).run())
        else:
            return analyzer_cls[0](data, settings).run()
