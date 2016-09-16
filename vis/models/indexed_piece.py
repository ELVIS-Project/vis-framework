#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
#
# Copyright (C) 2013, 2014 Christopher Antila, Jamie Klassen
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
import six
import requests
import warnings
import json
import music21
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
from music21 import converter, stream, analysis
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest


# the title given to a piece when we cannot determine its title
_UNKNOWN_PIECE_TITLE = 'Unknown Piece'


def login_edb(username, password):
    """Return csrf and session tokens for a login."""
    ANON_CSRF_TOKEN = "pkYF0M7HQpBG4uZCfDaBKjvTNe6u1UTZ"
    data = {"username": username, "password": password}
    headers = {
        "Cookie": "csrftoken={}; test_cookie=null".format(ANON_CSRF_TOKEN),
        "X-CSRFToken": ANON_CSRF_TOKEN
    }
    resp = requests.post('http://database.elvisproject.ca/login/',
                         data=data, headers=headers, allow_redirects=False)
    if resp.status_code == 302:
        return dict(resp.cookies)
    else:
        raise ValueError("Failed login.")


def auth_get(url, csrftoken, sessionid):
    """Use a csrftoken and sessionid to request a url on the elvisdatabase."""
    headers = {
        "Cookie": "test_cookie=null; csrftoken={}; sessionid={}".format(csrftoken, sessionid)
    }
    resp = requests.get(url, headers=headers)
    return resp


def _find_piece_title(the_score):
    """
    Find the title of a score. If there is none, return the filename without an extension.
    :param the_score: The score of which to find the title.
    :type the_score: :class:`music21.stream.Score`
    :returns: The title of the score.
    :rtype: str
    """
    # First try to get the title from a Metadata object, but if it doesn't
    # exist, use the filename without directory.
    if the_score.metadata is not None:
        post = the_score.metadata.title
    elif hasattr(the_score, 'filePath'):
        post = os.path.basename(the_score.filePath)
    else:  # if the Score was part of an Opus
        post = _UNKNOWN_PIECE_TITLE

    # Now check that there is no file extension. This could happen either if
    # we used the filename or if music21 did a less-than-great job at the
    # Metadata object.
    # TODO: test this "if" stuff
    if not isinstance(post, six.string_types):  # uh-oh
        try:
            post = str(post)
        except UnicodeEncodeError:
            post = unicode(post) if six.PY2 else _UNKNOWN_PIECE_TITLE
    post = os.path.splitext(post)[0]

    return post


def _find_part_names(the_score):
    """
    Return a list of part names in a score. If the score does not have proper part names, return a
    list of enumerated parts.
    :param the_score: The score in which to find the part names.
    :type the_score: :class:`music21.stream.Score`
    :returns: The title of the score.
    :rtype: :obj:`list` of str
    """
    # hold the list of part names
    post = []

    # First try to find Instrument objects. If that doesn't work, use the "id"
    for each_part in the_score.parts:
        instr = each_part.getInstrument()
        if instr is not None and instr.partName != '' and instr.partName is not None:
            post.append(instr.partName)
        elif each_part.id is not None:
            if isinstance(each_part.id, six.string_types):
                # part ID is a string, so that's what we were hoping for
                post.append(each_part.id)
            else:
                # the part name is probably an integer, so we'll try to rename it
                post.append('rename')
        else:
            post.append('rename')

    # Make sure none of the part names are just numbers; if they are, use
    # a part name like "Part 1" instead.
    for i, part_name in enumerate(post):
        if 'rename' == part_name:
            post[i] = 'Part {}'.format(i + 1)

    return post


def _find_piece_range(the_score):

    p = analysis.discrete.Ambitus()
    p_range = p.getPitchSpan(the_score)

    if p_range is None:
        return (None, None)
    else:
        return (p_range[0].nameWithOctave, p_range[1].nameWithOctave)


def _find_part_ranges(the_score):

    ranges = []
    for x in range(len(the_score.parts)):
        p = analysis.discrete.Ambitus()
        p_range = p.getPitchSpan(the_score.parts[x])
        if p_range is None:
            ranges.append((None, None))
        else:
            ranges.append((p_range[0].nameWithOctave, p_range[1].nameWithOctave))

    return ranges


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

    # When get_data() is missing the "data" argument.
    _MISSING_DATA = '{} is missing required data from another analyzer.'

    # When get_data() gets something that isn't an Indexer or Experimenter
    _NOT_AN_ANALYZER = 'IndexedPiece requires an Indexer or Experimenter (received {})'

    # When metadata() gets an invalid field name
    _INVALID_FIELD = 'metadata(): invalid field ({})'

    # When metadata()'s "field" is not a string
    _META_INVALID_TYPE = "metadata(): parameter 'field' must be of type 'string'"

    # When _import_score() gets an unexpected Opus
    _UNEXP_OPUS = '{} is a music21.stream.Opus (refer to the IndexedPiece.get_data() documentation)'

    # When _import_score() gets an unexpected Opus
    _UNEXP_NONOPUS = ('You expected a music21.stream.Opus but {} is not an Opus (refer to the '
                      'IndexedPiece.get_data() documentation)')

    _MISSING_USERNAME = ('You must enter a username to access the elvis database')
    _MISSING_PASSWORD = ('You must enter a password to access the elvis database')
    def __init__(self, pathname, opus_id=None, metafile=None, username=None, password=None):
        """
        :param str pathname: Pathname to the file music21 will import for this :class:`IndexedPiece`.
        :param opus_id: The index of the :class:`Score` for this :class:`IndexedPiece`, if the file
            imports as a :class:`music21.stream.Opus`.
        :returns: A new :class:`IndexedPiece`.
        :rtype: :class:`IndexedPiece`
        """

        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length string.
            """
            field_list = ['opusNumber', 'movementName', 'composer', 'number', 'anacrusis',
                'movementNumber', 'date', 'composers', 'alternativeTitle', 'title',
                'localeOfComposition', 'parts', 'pieceRange', 'partRanges']
            for field in field_list:
                self._metadata[field] = ''
            self._metadata['pathname'] = pathname

        super(IndexedPiece, self).__init__()
        self._imported = False
        self._noterest_results = None
        self._pathname = pathname
        self._metadata = {}
        self._username = username
        self._password = password
        init_metadata()
        if metafile is not None:
            self._metafile = metafile
            self._open_file()
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score

    def __repr__(self):
        return "vis.models.indexed_piece.IndexedPiece('{}')".format(self.metadata('pathname'))

    def __str__(self):
        post = []
        if self._imported:
            return '<IndexedPiece ({} by {})>'.format(self.metadata('title'), self.metadata('composer'))
        else:
            return '<IndexedPiece ({})>'.format(self.metadata('pathname'))

    def __unicode__(self):
        return six.u(str(self))

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
        score = converter.Converter()
        score.parseFile(self.metadata('pathname'), forceSource=True, storePickle=False)
        # piece = self.metadata('pathname')
        # score = music21.converter.parse(piece)
        score = score.stream
        if isinstance(score, stream.Opus):
            if known_opus is False and self._opus_id is None:
                # unexpected Opus---can't continue
                raise OpusWarning(IndexedPiece._UNEXP_OPUS.format(self.metadata('pathname')))
            elif self._opus_id is None:
                # we'll make new IndexedPiece objects
                score = [IndexedPiece(self.metadata('pathname'), i) for i in xrange(len(score))]
            else:
                # we'll return the appropriate Score
                score = score.scores[self._opus_id]
        elif known_opus is True:
            raise OpusWarning(IndexedPiece._UNEXP_NONOPUS.format(self.metadata('pathname')))
        elif not self._imported:
            for field in self._metadata:
                if hasattr(score.metadata, field):
                    self._metadata[field] = getattr(score.metadata, field)
                    if self._metadata[field] is None:
                        self._metadata[field] = '???'
            self._metadata['parts'] = _find_part_names(score)
            self._metadata['title'] = _find_piece_title(score)
            self._metadata['partRanges'] = _find_part_ranges(score)
            self._metadata['pieceRange'] = _find_piece_range(score)
            self._imported = True
        return score

    def metadata(self, field, value=None):
        """
        Get or set metadata about the piece.
        .. note:: Some metadata fields may not be available for all pieces. The available metadata
            fields depend on the specific file imported. Unavailable fields return ``None``.
            We guarantee real values for ``pathname``, ``title``, and ``parts``.
        :param str field: The name of the field to be accessed or modified.
        :param value: If not ``None``, the value to be assigned to ``field``.
        :type value: object or ``None``
        :returns: The value of the requested field or ``None``, if assigning, or if accessing
            a non-existant field or a field that has not yet been initialized.
        :rtype: object or ``None`` (usually a string)
        :raises: :exc:`TypeError` if ``field`` is not a string.
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
        'Jean Sibelius'
        >>> piece.metadata('date', 1919)
        >>> piece.metadata('date')
        1919
        >>> piece.metadata('parts')
        ['Flute 1'{'Flute 2'{'Oboe 1'{'Oboe 2'{'Clarinet 1'{'Clarinet 2', ... ]
        """
        if not isinstance(field, six.string_types):
            raise TypeError(IndexedPiece._META_INVALID_TYPE)
        elif field not in self._metadata:
            raise AttributeError(IndexedPiece._INVALID_FIELD.format(field))
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
        :returns: ``None``.
        :rtype: None
        :raises: :exc:`TypeError` if a class is not a subclass of :class:`Indexer` or
            :class:`Experimenter`.
        ..note:: This is a separate function so it can be replaced with a :class:`MagicMock` in
            testing.
        """
        for each_cls in cls_list:
            if not issubclass(each_cls, (Indexer, Experimenter)):
                raise TypeError(IndexedPiece._NOT_AN_ANALYZER.format(cls_list))

    def get_data(self, analyzer_cls, settings=None, data=None, known_opus=False):
        """
        Get the results of an Experimenter or Indexer run on this :class:`IndexedPiece`.
        :param analyzer_cls: The analyzers to run, in the order they should be run.
        :type analyzer_cls: list of type
        :param settings: Settings to be used with the analyzers.
        :type settings: dict
        :param data: Input data for the first analyzer to run. If the first indexer uses a
            :class:`~music21.stream.Score`, you should leave this as ``None``.
        :type data: list of :class:`pandas.Series` or :class:`pandas.DataFrame`
        :param known_opus: Whether the caller knows this file will be imported as a
            :class:`music21.stream.Opus` object. Refer to the "Note about Opus Objects" below.
        :type known_opus: boolean
        :returns: Results of the analyzer.
        :rtype: :class:`pandas.DataFrame` or list of :class:`pandas.Series`
        :raises: :exc:`TypeError` if the ``analyzer_cls`` is invalid or cannot be found.
        :raises: :exc:`RuntimeError` if the first analyzer class in ``analyzer_cls`` does not use
            :class:`~music21.stream.Score` objects, and ``data`` is ``None``.
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
            elif (hasattr(analyzer_cls[0], 'required_score_type') and
                  analyzer_cls[0].required_score_type == 'stream.Part'):
                data = self._import_score(known_opus=known_opus)
                data = [x for x in data.parts]  # Indexers require a list of Parts
            elif (hasattr(analyzer_cls[0], 'required_score_type') and
                  analyzer_cls[0].required_score_type == 'stream.Score'):
                data = [self._import_score(known_opus=known_opus)]
            else:
                raise RuntimeError(IndexedPiece._MISSING_DATA.format(analyzer_cls[0]))
        if len(analyzer_cls) > 1:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                return self.get_data(analyzer_cls[1:], settings, data)
            return self.get_data(analyzer_cls[1:], settings, analyzer_cls[0](data, settings).run())
        else:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                return data
            else:
                return analyzer_cls[0](data, settings).run()

    def _open_file(self):

        if os.path.isfile(self._metafile):
            with open(self._metafile) as mf:
                f = []
                x = 0

                lines = mf.readlines()
                exists = False
                if '/' in self._pathname:
                    pth = self._pathname.split('/')
                    pth = pth[len(pth) - 1]
                else:
                    pth = self._pathname
                for line in lines:
                    if self._pathname in line or pth in line:
                        exists = True
                if not exists:
                    warnings.warn('The meta file you have included does not seem to correspond to the file.')
                    return

                for n, line in enumerate(lines):
                    if line.startswith('}'):
                        line_range = [x, n]
                        x = n + 1
                        f.append(line_range)

                if len(f) == 1:
                    self._json_reader()

                for pair in f:
                    for line in lines[pair[0]: pair[1]]:
                        if self._pathname in line:
                            target = open('temp', 'w')
                            for line1 in lines[pair[0]: pair[1]]:
                                target.write(line1)
                            target.write('}' + '\n')
                            target.close()
                            self._metafile = 'temp'
                            self._json_reader()
        else:
            self._json_reader()

    def load_url(self, url):

        if self._username is None:
            raise RuntimeError(self._MISSING_USERNAME)
        elif self._password is None:
            raise RuntimeError(self._MISSING_PASSWORD)
        else:
            self._logged = login_edb(self._username, self._password)
        resp = auth_get(url, self._logged['csrftoken'], self._logged['sessionid'])

        try:
            resp.json()
        except ValueError:
            if url[len(url) - 1] == '/':
                url = url + '?format=json'
            else:
                url = url + '&format=json'

        resp = auth_get(url, self._logged['csrftoken'], self._logged['sessionid'])

        jason = resp.json()
        return url, jason

    def _json_reader(self):

        if os.path.isfile(self._metafile):
            with open(self._metafile) as mf:
                data = json.load(mf)
                mf.close()

        else:
            url, data = self.load_url(self._metafile)

        self._metadata['composer'] = data['composer']['title']
        self._metadata['languages'] = []
        for lang in data['languages']:
            for title in lang:
                self._metadata['languages'].append(lang[title])
        self._metadata['tags'] = []
        for tag in data['tags']:
            for title in tag:
                self._metadata['tags'].append(tag[title])
        if 'piece' in data:
            self._metadata['title'] = data['piece']['title'] + ': ' + data['title']
        else:
            self._metadata['title'] = data['title']
        self._metadata['composer'] = data['composer']['title']
        types = ['vocalization', 'sources', 'religiosity', 'locations', 'instruments_voices', 'genres', 'creator']
        for dat in types:
            self._metadata[dat] = data[dat]

        if self._metafile is 'temp':
            os.remove('temp')

    def run(self):
        self._import_score()
        return self
