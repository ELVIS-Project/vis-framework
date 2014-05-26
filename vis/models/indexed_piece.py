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

    :param the_score: The score of which to find the title.
    :type the_score: :class:`music21.stream.Score`

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

    :param the_score: The score in which to find the part names.
    :type the_score: :class:`music21.stream.Score`

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


class OpusWarning(RuntimeWarning):
    """
    The :class:`OpusWarning` is raised by :meth:`IndexedPiece.get_data` when ``known_opus`` is
    ``False`` but the file imports as a :class:`music21.stream.Opus` object, and when ``known_opus``
    is ``True`` but the file does not import as a :class:`music21.stream.Opus` object.

    Internally, the warning is actually raised by :meth:`IndexedPiece._import_score`.
    """
    pass


class IndexedPiece(object):
    """
    Hold indexed data from a musical score.
    """
    def __init__(self, pathname, opus_id=None):
        """
        :param pathname: Pathname to the file music21 will import for this :class:`IndexedPiece`.
        :type pathname: basestring
        :param opus_id: The index of the :class:`Score` for this :class:`IndexedPiece`, if the file
            imports as a :class:`music21.stream.Opus`.

        :returns: A new :class:`IndexedPiece`.
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
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score
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

    def _import_score(self, known_opus=False):
        """
        Import the score to music21 format.

        :param known_opus: Whether you expect the file to import as a :class:`Opus`.
        :type known_opus: boolean

        :returns: the score
        :rtype: :class:`music21.stream.Score`

        :raises: :exc:`OpusWarning` if the file imports as a :class:`music21.stream.Opus` but
            ``known_opus`` if ``False``, or if ``known_opus`` is ``True`` but the file does not
            import as an :class:`Opus`.
        """
        score = converter.parse(self.metadata('pathname'))
        if isinstance(score, stream.Opus):
            if known_opus is False and self._opus_id is None:
                # unexpected Opus---can't continue
                raise OpusWarning(self.metadata('pathname') + u' is a music21.stream.Opus '
                                  u'(refer to the IndexedPiece.get_data() documentation)')
            elif self._opus_id is None:
                # we'll make new IndexedPiece objects
                score = [IndexedPiece(self.metadata('pathname'), i) for i in xrange(len(score))]
            else:
                # we'll return the appropriate Score
                score = score.scores[self._opus_id]
        elif known_opus is True:
            raise OpusWarning(u'You expected a music21.stream.Opus but ' + \
                              self.metadata('pathname') + u' is not an Opus '
                                  u'(refer to the IndexedPiece.get_data() documentation)')
        elif not self._imported:
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

        .. note:: Some metadata fields may not be available for all pieces. The available metadata
            fields depend on the specific file imported. Unavailable fields return :const:`None`.
            We guarantee real values for ``pathname``, ``title``, and ``parts``.

        :param field: The name of the field to be accessed or modified.
        :type field: basestring
        :param value: If not :const:`None`, the value to be assigned to ``field``.
        :type value: object or :const:`None`

        :returns: The value of the requested field or :const:`None`, if assigning, or if accessing
            a non-existant field or a field that has not yet been initialized.
        :rtype: object or :const:`None` (usually a basestring)

        :raises: :exc:`TypeError` if ``field`` is not a :class:`basestring`.
        :raises: :exc:`AttributeError` if accessing an invalid ``field`` (see valid fields below).

        **Metadata Field Descriptions**

        All fields are taken directly from music21 unless otherwise noted.

        +---------------------+--------------------------------------------------------------------+
        | Metadata Field      | Description                                                        |
        +=====================+====================================================================+
        | alternativeTitle    | A possible alternate title for the piece; e.g. Bruckner's          |
        |                     | Symphony No. 8 in C minor is known as "The German Michael."        |
        +---------------------+--------------------------------------------------------------------+
        | anacrusis           | The length of the pick-up measure, if there is one. This is not    |
        |                     | determined by music21.                                             |
        +---------------------+--------------------------------------------------------------------+
        | composer            | The author of the piece.                                           |
        +---------------------+--------------------------------------------------------------------+
        | composers           | If the piece has multiple authors.                                 |
        +---------------------+--------------------------------------------------------------------+
        | date                | The date that the piece was composed or published.                 |
        +---------------------+--------------------------------------------------------------------+
        | localeOfComposition | Where the piece was composed.                                      |
        +---------------------+--------------------------------------------------------------------+
        | movementName        | If the piece is part of a larger work, the name of this            |
        |                     | subsection.                                                        |
        +---------------------+--------------------------------------------------------------------+
        | movementNumber      | If the piece is part of a larger work, the number of this          |
        |                     | subsection.                                                        |
        +---------------------+--------------------------------------------------------------------+
        | number              | Taken from music21.                                                |
        +---------------------+--------------------------------------------------------------------+
        | opusNumber          | Number assigned by the composer to the piece or a group            |
        |                     | containing it, to help with identification or cataloguing.         |
        +---------------------+--------------------------------------------------------------------+
        | parts               | A list of the parts in a multi-voice work. This is determined      |
        |                     | partially by music21.                                              |
        +---------------------+--------------------------------------------------------------------+
        | pathname            | The filesystem path to the music file encoding the piece. This is  |
        |                     | not determined by music21.                                         |
        +---------------------+--------------------------------------------------------------------+
        | title               | The title of the piece. This is determined partially by music21.   |
        +---------------------+--------------------------------------------------------------------+

        **Examples**

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

    def _get_note_rest_index(self, known_opus=False):
        """
        Return the results of the :class:`NoteRestIndexer` on this piece.

        This method is used automatically by :meth:`get_data` to cache results, which avoids having
        to re-import the music21 file for every Indexer or Experimenter that uses the
        :class:`NoteRestIndexer`.

        :param known_opus: Whether the caller knows this file will be imported as a
            :class:`music21.stream.Opus` object. Refer to the "Note about Opus Objects" in the
            :meth:`get_data` docs.
        :type known_opus: boolean

        :returns: Results of the :class:`NoteRestIndexer`.
        :rtype: list of :class:`pandas.Series`
        """
        if known_opus is True:
            return self._import_score(known_opus=known_opus)
        elif self._noterest_results is None:
            data = [x for x in self._import_score().parts]
            self._noterest_results = noterest.NoteRestIndexer(data).run()
        return self._noterest_results

    @staticmethod
    def _type_verifier(cls_list):
        """
        Verify that all classes in the list are a subclass of :class:`vis.analyzers.indexer.Indexer`
        or :class:`~vis.analyzers.experimenter.Experimenter`.

        :param cls_list: A list of the classes to check.
        :type cls_list: list of class
        :returns: :const:`None`.
        :rtype: None
        :raises: :exc:`TypeError` if a class is not a subclass of :class:`Indexer` or
            :class:`Experimenter`.

        ..note:: This is a separate function so it can be replaced with a :class:`MagicMock` in
            testing.
        """
        for each_cls in cls_list:
            if not issubclass(each_cls, (Indexer, Experimenter)):
                raise TypeError(u'IndexedPiece requires an Indexer or Experimenter '
                                u'(received {})'.format(cls_list))

    def get_data(self, analyzer_cls, settings=None, data=None, known_opus=False):
        """
        Get the results of an Experimenter or Indexer run on this :class:`IndexedPiece`.

        :param analyzer_cls: The analyzers to run, in the order they should be run.
        :type analyzer_cls: list of type
        :param settings: Settings to be used with the analyzers.
        :type settings: dict
        :param data: Input data for the first analyzer to run. If the first indexer uses a
            :class:`~music21.stream.Score`, you should leave this as :const:`None`.
        :type data: list of :class:`pandas.Series` or :class:`pandas.DataFrame`
        :param known_opus: Whether the caller knows this file will be imported as a
            :class:`music21.stream.Opus` object. Refer to the "Note about Opus Objects" below.
        :type known_opus: boolean

        :returns: Results of the analyzer.
        :rtype: :class:`pandas.DataFrame` or list of :class:`pandas.Series`

        :raises: :exc:`TypeError` if the ``analyzer_cls`` is invalid or cannot be found.
        :raises: :exc:`RuntimeError` if the first analyzer class in ``analyzer_cls`` does not use
            :class:`~music21.stream.Score` objects, and ``data`` is :const:`None`.
        :raises: :exc:`~vis.models.indexed_piece.OpusWarning` if the file imports as a
            :class:`music21.stream.Opus` object and ``known_opus`` is ``False``.
        :raises: :exc:`~vis.models.indexed_piece.OpusWarning` if ``known_opus`` is ``True`` but the
            file does not import as an :class:`Opus`.

        **Note about Opus Objects**

        Correctly importing :class:`~music21.stream.Opus` objects is a little awkward because
        we only know a file imports to an :class:`Opus` *after* we import it, but an
        :class:`Opus` should be treated as multiple :class:`IndexedPiece` objects.

        We recommend you handle :class:`Opus` objects like this:

        #. Try to call :meth:`get_data` on the :class:`IndexedPiece`.
        #. If :meth:`get_data` raises an :exc:`OpusWarning`, the file contains an :class:`Opus`.
        #. Call :meth:`get_data` again with the ``known_opus`` parameter set to ``True``.
        #. :meth:`get_data` will return multiple :class:`IndexedPiece` objects, each \
            corresponding to a :class:`~music21.stream.Score` held in the :class:`Opus`.
        #. Then call :meth:`get_data` on the new :class:`IndexedPiece` objects to get the results \
            initially desired.

        Refer to the source code for :meth:`vis.workflow.WorkflowManager.load` for an example
        implementation.
        """
        IndexedPiece._type_verifier(analyzer_cls)
        if data is None:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                data = self._get_note_rest_index(known_opus=known_opus)
            # NB: Experimenter subclasses don't have "required_score_type"
            elif hasattr(analyzer_cls[0], 'required_score_type') and \
            analyzer_cls[0].required_score_type == stream.Part:
                data = self._import_score(known_opus=known_opus)
                data = [x for x in data.parts]  # Indexers require a list of Parts
            elif analyzer_cls[0].required_score_type == stream.Score:  # TODO: test this
                data = [self._import_score()]  # TODO: test this
            else:
                msg = u'{} is missing required data from another analyzer.'.format(analyzer_cls[0])
                raise RuntimeError(msg)
        if len(analyzer_cls) > 1:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                return self.get_data(analyzer_cls[1:], settings, data)
            return self.get_data(analyzer_cls[1:], settings, analyzer_cls[0](data, settings).run())
        else:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                return data
            else:
                return analyzer_cls[0](data, settings).run()
