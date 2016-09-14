#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Jamie Klassen, Alexander Morgan
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
.. codeauthor:: Alexander Morgan
This model represents an indexed and analyzed piece of music.
"""

# Imports
import os
import six
import requests
import warnings
import json
import music21
import music21.chord as chord
import pandas
import numpy
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
from music21 import converter, stream, analysis
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.experimenters import aggregator, barchart, frequency, lilypond #, dendrogram
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest, cadence, meter, interval, dissonance, fermata, offset, repeat, active_voices, offset, over_bass, contour, ngram, windexer
# from vis.analyzers.indexers import lilypond as lily_ind
from multi_key_dict import multi_key_dict as mkd


# the title given to a piece when we cannot determine its title
_UNKNOWN_PIECE_TITLE = 'Unknown Piece'
# Types for noterest indexing
_noterest_types = ('Note', 'Rest', 'Chord')
_default_interval_setts = {'quality':True, 'directed':True, 'simple or compound':'compound', 'horiz_attach_later':True}
# Multi-key dictionary for calls to get_data().
_mkd = mkd({ # Indexers (in alphabetical order of their two-letter abbreviation):
            # ('an', 'annotation', 'lilypond.AnnotationIndexer', lilypond.AnnotationIndexer): lily_ind.AnnotationIndexer,
            ('ac', 'active_voices', 'active_voices.ActiveVoicesIndexer', active_voices.ActiveVoicesIndexer): active_voices.ActiveVoicesIndexer,
            ('be', 'beat_strength', 'meter.NoteBeatStrengthIndexer', meter.NoteBeatStrengthIndexer): meter.NoteBeatStrengthIndexer,
            ('ca', 'cadence', 'cadence.CadenceIndexer', cadence.CadenceIndexer): cadence.CadenceIndexer,
            ('co', 'contour', 'contour.ContourIndexer', contour.ContourIndexer): contour.ContourIndexer,
            ('di', 'dissonance', 'dissonance.DissonanceIndexer', dissonance.DissonanceIndexer): dissonance.DissonanceIndexer,
            ('du', 'duration', 'meter.DurationIndexer', meter.DurationIndexer): meter.DurationIndexer,
            ('fe', 'fermata', 'fermata.FermataIndexer', fermata.FermataIndexer): fermata.FermataIndexer,
            ('ho', 'horizontal_interval', 'interval.HorizontalIntervalIndexer', interval.HorizontalIntervalIndexer): interval.HorizontalIntervalIndexer,
            ('me', 'measure', 'meter.MeasureIndexer', meter.MeasureIndexer): meter.MeasureIndexer,
            ('mu', 'multistop', 'noterest.MultiStopIndexer', noterest.MultiStopIndexer): noterest.MultiStopIndexer,
            ('ng', 'ngram', 'ngram.NGramIndexer', ngram.NGramIndexer): ngram.NGramIndexer,
            ('no', 'noterest', 'noterest.NoteRestIndexer', noterest.NoteRestIndexer): noterest.NoteRestIndexer,
            ('of', 'offset', 'offset.FilterByOffsetIndexer', offset.FilterByOffsetIndexer): offset.FilterByOffsetIndexer,
            ('ov', 'over_bass', 'over_bass.OverBassIndexer', over_bass.OverBassIndexer): over_bass.OverBassIndexer,
            ('re', 'repeat', 'repeat.FilterByRepeatIndexer', repeat.FilterByRepeatIndexer): repeat.FilterByRepeatIndexer,
            ('ve', 'vertical_interval', 'interval.IntervalIndexer', interval.IntervalIndexer): interval.IntervalIndexer,
            ('wi', 'windexer', 'windexer.Windexer', windexer.Windexer): windexer.Windexer,
            # Experimenters (in alphabetical order of their two-letter abbreviation):
            ('ae', 'annotate_the_note', 'lilypond.AnnotateTheNoteExperimenter', lilypond.AnnotateTheNoteExperimenter): lilypond.AnnotateTheNoteExperimenter,
            ('ag', 'aggregator', 'aggregator.ColumnAggregator', aggregator.ColumnAggregator): aggregator.ColumnAggregator,
            ('ba', 'bar_chart', 'barchart.RBarChart', barchart.RBarChart): barchart.RBarChart,
            # The dendrogram experimenter has been commented out to allow us to remove our SciPy dependency
            # ('de', 'dendrogram', 'dendrogram.HierarchicalClusterer', dendrogram.HierarchicalClusterer): dendrogram.HierarchicalClusterer,
            ('fr', 'frequency', 'frequency.FrequencyExperimenter', frequency.FrequencyExperimenter): frequency.FrequencyExperimenter,
            ('li', 'lilypond', 'lilypond.LilyPondExperimenter', lilypond.LilyPondExperimenter): lilypond.LilyPondExperimenter,
            ('pa', 'part_notes', 'lilypond.PartNotesExperimenter', lilypond.PartNotesExperimenter): lilypond.PartNotesExperimenter})

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

def _get_offset(event, part):
    """This method finds the offset of a music21 event. There are other ways to get the offset of a 
    music21 object, but this is the fastest and most reliable.

    :param event: music21 object contained in a music21 part stream.
    :param part: music21 part stream.
    """
    for y in event.contextSites():
        if y[0] is part:
            return y[1]

def _eliminate_ties(event):
    """Gets rid of the notes and rests that have non-start ties. This is used internally for 
    noterest and beatstrength indexing."""
    if hasattr(event, 'tie') and event.tie is not None and event.tie.type != 'start':
        return float('nan')
    return event

def _type_func_noterest(event):
    """Used internally by _get_m21_nrc_objs() to filter for just the 'Note', 'Rest', and 'Chord' 
    objects in a piece."""
    if any([typ in event.classes for typ in _noterest_types]):
        return event
    return float('nan')

def _type_func_measure(event):
    """Used internally by _get_m21_measure_objs() to filter for just the 'Measure' objects in a 
    piece."""
    if 'Measure' in event.classes:
        return event
    return float('nan')

def _type_func_voice(event):
    """Used internally by _combine_voices() to filter for just the 'Voice' objects in a part."""
    if 'Voice' in event.classes:
        return event
    return float('nan')

def _get_pitches(event):
    """Used internally by _combine_voices() to represent all the note and chord objects of a part as 
    music21 pitches. Rests get discarded in this stage, but later re-instated with 
    _reinsert_rests()."""
    if isinstance(event, float):
        return event
    elif event.isNote:
        return (music21.pitch.Pitch(event.nameWithOctave),)
    elif event.isRest:
        return float('nan')
    else: # The event is a chord
        return event.pitches

def _reinsert_rests(event):
    """Used internally by _combine_voices() to put rests back into its intermediate representation 
    of a piece which had to temporarily remove the rests."""
    if isinstance(event, float):
        return music21.note.Rest()
    return event

def _combine_voices(ser, part):
    """Used internally by _get_m21_nrc_objs() to combine the voices of a single part into one 
    pandas.Series of music21 chord objects."""
    temp = []
    indecies = [0]
    voices = part.apply(_type_func_voice).dropna()
    if len(voices.index) < 1:
        return ser
    for voice in voices:
        indecies.append(len(voice) + indecies[-1])
        temp.append(ser.iloc[indecies[-2] : indecies[-1]])
    # Put each voice in separate columns in a dataframe.
    df = pandas.concat(temp, axis=1).applymap(_get_pitches)
    # Condense the voices (df's columns) into chord objects in a series.
    res = df.apply(lambda x: chord.Chord(sorted([pitch for lyst in x.dropna() for pitch in lyst], reverse=True)), axis=1)
    # Note that if a part has two voices, and one voice has a note or a chord, and the other a rest, 
    # only the rest will be lost even after calling _reinsert_rests().
    return res.apply(_reinsert_rests)

def _attach_before(df):
    """Used internally by _get_horizontal_interval() to change the index values of the cached 
    results of the interval.HorizontalIntervalIndexer so that they start on 0.0 instead of whatever 
    value they start on. This shift makes the index values correspond to the first of two notes in 
    a horizontal interval in any given voice rather than that of the second."""
    re_indexed = []
    for x in range(len(df.columns)):
        ser = df.iloc[:, x].dropna()
        ser.index = numpy.insert(ser.index, 0, 0.0)[:-1]
        re_indexed.append(ser)
    return pandas.concat(re_indexed, axis=1)

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

def ImportScore(pathname, score=None):
    """
    Import the score to music21 format.
    :param pathname: Location of the file to import on the local disk.
    :type pathname: str
    :returns: An :class:`IndexedPiece` or an :class:`AggregatedPieces` object if the file passed 
        imports as a :class:`music21.stream.Score` or :class:`music21.stream.Opus` object
        respectively.
    :rtype: A new :class:`IndexedPiece` or :class:`AggregatedPieces` object.
    """
    score = converter.Converter()
    score.parseFile(pathname, forceSource=True, storePickle=False)
    score = score.stream
    if isinstance(score, stream.Opus):
        # make an AggregatedPieces object containing IndexedPiece objects of each movement of the opus.
        score = [IndexedPiece(pathname, opus_id=i) for i in xrange(len(score))]
    elif isinstance(score, stream.Score):
        score = (IndexedPiece(pathname, score=score),)
    for ip in score:
        for field in ip._metadata:
            if hasattr(ip.metadata, field):
                ip._metadata[field] = getattr(ip.metadata, field)
                if ip._metadata[field] is None:
                    ip._metadata[field] = '???'
        ip._metadata['parts'] = _find_part_names(ip._score)
        ip._metadata['title'] = _find_piece_title(ip._score)
        ip._metadata['partRanges'] = _find_part_ranges(ip._score)
        ip._metadata['pieceRange'] = _find_piece_range(ip._score)
        ip._imported = True
    if len(score) == 1:
        score = score[0]
    return score


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
    def __init__(self, pathname, opus_id=None, score=None, metafile=None, username=None, password=None):
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
                'localeOfComposition', 'parts']
            for field in field_list:
                self._metadata[field] = ''
            self._metadata['pathname'] = pathname

        super(IndexedPiece, self).__init__()
        self._imported = False
        self._analyses = {}
        self._score = score
        self._noterest_results = None
        self._pathname = pathname
        self._metadata = {}
        self._known_opus = False
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score
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

    def _get_part_streams(self):
        """Returns a list of the part streams in this indexed_piece."""
        if 'part_streams' not in self._analyses:
            self._analyses['part_streams'] = self._score.parts
        return self._analyses['part_streams']

    def _get_m21_objs(self):
        """
        Return the all the music21 objects found in the piece. This is a list of pandas.Series 
        where each series contains the events in one part. It is not concatenated into a 
        dataframe at this stage because this step should be done after filtering for a certain
        type of event in order to get the proper index.

        This list of voices with their events can easily be turned into a dataframe of music21 
        objects that can be filtered to contain, for example, just the note and rest objects.
        Filtered dataframes of music21 objects like this can then have an indexer_func applied 
        to them all at once using df.applymap(indexer_func).

        :returns: All the objects found in the music21 voice streams. These streams are made 
            into pandas.Series and collected in a list.
        :rtype: list of :class:`pandas.Series`
        """
        if 'm21_objs' not in self._analyses:
            # save the results as a list of series in the indexed_piece attributes
            sers =[]
            for p in self._get_part_streams():
                ser = pandas.Series(p.recurse())
                ser.index = ser.apply(_get_offset, args=(p,))
                sers.append(ser)
            self._analyses['m21_objs'] = sers
        return self._analyses['m21_objs']

    def _get_m21_nrc_objs(self):
        """
        This method takes a list of pandas.Series of music21 objects in each part in a piece and
        filters them to reveal just the 'Note', 'Rest', and 'Chord' objects. It then aligns these
        events with their offsets, and returns a pandas dataframe where each column has the events 
        of a single part.

        :returns: The note, rest, and chord music21 objects in each part of a piece, aligned with 
            their offsets.
        :rtype: A pandas.DataFrame of music21 note, rest, and chord objects.
        """
        if 'm21_nrc_objs' not in self._analyses:
            # get rid of all m21 objects that aren't notes, rests, or chords in each part series
            sers = [s.apply(_type_func_noterest).dropna() for s in self._get_m21_objs()]
            for i, ser in enumerate(sers): # and index  the offsets
                if not ser.index.is_unique: # the index is often not unique if there is an embedded voice
                    sers[i] = _combine_voices(ser, self._get_m21_objs()[i])
            self._analyses['m21_nrc_objs'] = pandas.concat(sers, axis=1)
        return self._analyses['m21_nrc_objs']

    def _get_m21_nrc_objs_no_tied(self):
        """Used internally by _get_noterest() and _get_multistop(). Returns a pandas dataframe where 
        each column corresponds to one part in the score. Each part has the note, rest, and chord 
        objects as the elements in its column as long as they don't have a non-start tie, otherwise 
        they are omitted."""
        if 'm21_nrc_objs_no_tied' not in self._analyses:
           # This if statement is necessary because of a pandas bug, see pandas issue #8222.
            if len(self._get_m21_nrc_objs()) == 0: # If parts have no note, rest, or chord events in them
                self._analyses['m21_nrc_objs_no_tied'] = self._get_m21_nrc_objs()
            else: # This is the normal case.
                self._analyses['m21_nrc_objs_no_tied'] = self._get_m21_nrc_objs().applymap(_eliminate_ties).dropna(how='all')
        return self._analyses['m21_nrc_objs_no_tied']

    def _get_noterest(self):
        """Used internally by get_data() to cache and retrieve results from the 
        noterest.NoteRestIndexer."""
        if 'noterest' not in self._analyses:
            self._analyses['noterest'] = noterest.NoteRestIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['noterest']

    def _get_multistop(self):
        """Used internally by get_data() to cache and retrieve results from the 
        noterest.MultiStopIndexer."""
        if 'multistop' not in self._analyses:
            self._analyses['multistop'] = noterest.MultiStopIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['multistop']

    def _get_duration(self):
        """Used internally by get_data() to cache and retrieve results from the 
        meter.DurationIndexer."""
        if 'duration' not in self._analyses:
            self._analyses['duration'] = meter.DurationIndexer(self._get_noterest(), self._get_part_streams()).run()
        return self._analyses['duration']

    def _get_beat_strength(self):
        """Used internally by get_data() to cache and retrieve results from the 
        meter.NoteBeatStrengthIndexer."""
        if 'beat_strength' not in self._analyses:
            self._analyses['beat_strength'] = meter.NoteBeatStrengthIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['beat_strength']

    def _get_fermata(self):
        """Used internally by get_data() to cache and retrieve results from the 
        fermata.FermataIndexer."""
        if 'fermata' not in self._analyses:
            self._analyses['fermata'] = fermata.FermataIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['fermata']

    def _get_vertical_interval(self, settings=None):
        """Used internally by get_data() to cache and retrieve results from the 
        interval.IntervalIndexer. Since there are many possible settings for intervals, no matter 
        what the user asks for intervals are calculated as compound, directed, and diatonic with 
        quality. The results with these settings are stored and if the user asked for different 
        settings, they are recalculated from these 'complete' cached results. This reindexing is 
        done with the interval.IntervalReindexer."""
        if 'vertical_interval' not in self._analyses:
            self._analyses['vertical_interval'] = interval.IntervalIndexer(self._get_noterest(), settings=_default_interval_setts.copy()).run()
        if settings is not None and not ('directed' in settings and settings['directed'] == True and
                'quality' in settings and settings['quality'] in (True, 'diatonic with quality') and
                'simple or compound' in settings and settings['simple or compound'] == 'compound'):
            return interval.IntervalReindexer(self._analyses['vertical_interval'], settings).run()
        return self._analyses['vertical_interval']

    def _get_horizontal_interval(self, settings=None):
        """Used internally by get_data() to cache and retrieve results from the 
        interval.IntervalIndexer. Since there are many possible settings for intervals, no matter 
        what the user asks for intervals are calculated as compound, directed, and diatonic with 
        quality. The results with these settings are stored and if the user asked for different 
        settings, they are recalculated from these 'complete' cached results. This reindexing is 
        done with the interval.IntervalReindexer. Those details are the same as for the 
        _get_vertical_interval() method, but this method has an added check to see if the user asked 
        for horiz_attach_later == False. In this case the index of each part's horizontal intervals 
        is shifted forward one element and 0.0 is assigned as the first element."""
        # No matter what settings the user specifies, calculate the intervals in the most complete way.
        if 'horizontal_interval' not in self._analyses:
            self._analyses['horizontal_interval'] = interval.HorizontalIntervalIndexer(self._get_noterest(), _default_interval_setts.copy()).run()
        # If the user's settings were different, reindex the stored intervals.
        if settings is not None and not ('directed' in settings and settings['directed'] == True and
                'quality' in settings and settings['quality'] in (True, 'diatonic with quality') and
                'simple or compound' in settings and settings['simple or compound'] == 'compound'):
            post = interval.IntervalReindexer(self._analyses['horizontal_interval'], settings).run()
            # Switch to 'attach before' if necessary.
            if 'horiz_attach_later' not in settings or not settings['horiz_attach_later']:
                post = _attach_before(post)
            return post
        return self._analyses['horizontal_interval']

    def _get_dissonance(self):
        """Used internally by get_data() to cache and retrieve results from the 
        dissonance.DissonanceIndexer. This method automatically supplies the input dataframes from 
        the indexed_piece that is the self argument. If you want to call this with indexer results 
        other than those associated with self, you can call the indexer directly."""
        if 'dissonance' not in self._analyses:
            h_setts = {'quality': False, 'simple or compound': 'compound', 'horiz_attach_later': False}
            v_setts = setts = {'quality': True, 'simple or compound': 'simple', 'directed': True}
            in_dfs = [self._get_beat_strength(), self._get_duration(),
                      self._get_horizontal_interval(h_setts), self._get_vertical_interval(v_setts)]
            self._analyses['dissonance'] = dissonance.DissonanceIndexer(in_dfs).run()
        return self._analyses['dissonance']

    def _get_m21_measure_objs(self):
        """Makes a dataframe of the music21 measure objects in the indexed_piece. Note that midi 
        files do not have measures."""
        if 'm21_measure_objs' not in self._analyses:
            # filter for just the measure objects in each part of this indexed piece
            sers = [s.apply(_type_func_measure).dropna() for s in self._get_m21_objs()]
            self._analyses['m21_measure_objs'] = pandas.concat(sers, axis=1)
        return self._analyses['m21_measure_objs']

    def _get_measure(self):
        if 'measure' not in self._analyses:
            self._analyses['measure'] = meter.MeasureIndexer(self._get_m21_measure_objs()).run()
        return self._analyses['measure']

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
        if isinstance(analyzer_cls[0], str):
            analyzer_cls = [_mkd[analyzer_cls[0]]]
        IndexedPiece._type_verifier(analyzer_cls)
        if data is None:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                data = self._get_noterest()
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
