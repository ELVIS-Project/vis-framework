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
from vis.models.aggregated_pieces import AggregatedPieces
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.experimenters import aggregator, barchart, frequency
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest, approach, meter, interval, dissonance, fermata, offset, repeat, active_voices, offset, over_bass, contour, ngram, windexer
from multi_key_dict import multi_key_dict as mkd
from collections import Counter

# Error message when importing doesn't work because of unknown file type
_UNKNOWN_INPUT = 'This file type was not recognized. The file is probably not \
a score in symbolic notation.'
# the title given to a piece when we cannot determine its title
_UNKNOWN_PIECE_TITLE = 'Unknown Piece'
# Types for noterest indexing
_noterest_types = ('Note', 'Rest', 'Chord')
_default_interval_setts = {'quality':True, 'directed':True, 'simple or compound':'compound', 'horiz_attach_later':True}

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


def _find_part_names(list_of_parts):
    """
    Return a list of part names in a score. If the score does not have proper 
    part names, return a list of enumerated parts.
    :param list_of_parts: The parts of the score.
    :type list_of_parts: List of :class:`music21.stream.Part`
    :returns: List of part names.
    :rtype: :obj:`list` of str
    """
    # hold the list of part names
    post = []

    # First try to find Instrument objects. If that doesn't work, use the "id"
    for i, each_part in enumerate(list_of_parts):
        name = 'None'
        instr = each_part.getInstrument()
        if instr is not None and instr.partName != '' and instr.partName is not None:
            name = instr.partName
        elif each_part.id is not None:
            if isinstance(each_part.id, six.string_types):
                # part ID is a string, so that's what we were hoping for
                name = each_part.id
        # Make sure none of the part names are just 'None'.
        if name == 'None' or name == '':
            name = 'Part {}'.format(i + 1)
        post.append(name)

    # If there are duplicates, add enumerated suffixes.
    counts = {k:v for k,v in Counter(post).items() if v > 1}      
    for i in reversed(range(len(post))):
        item = post[i]
        if item in counts and counts[item]:
            post[i] = ''.join((post[i], '_', str(counts[item])))
            counts[item] -= 1

    return post

def _get_offsets(event, part):
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

def _type_func_time_signature(event):
    """Used internally by _get_time_signature() to filter for just the time signatures in a piece."""
    if 'TimeSignature' in event.classes:
        return event.ratioString
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

def _import_file(pathname, metafile=None):
    """
    Import the score to music21 format.
    :param pathname: Location of the file to import on the local disk.
    :type pathname: str
    :returns: A 1-tuple of :class:`IndexedPiece` if the file imported as a 
        :class:`music21.stream.Score` object or a multi-element list if it imported as a 
        :class:`music21.stream.Opus` object.
        respectively.
    :rtype: 1-tuple or list of :class:`IndexedPiece`
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
        ip._metadata['parts'] = _find_part_names(ip._get_part_streams())
        ip._metadata['title'] = _find_piece_title(ip._score)
        ip._metadata['partRanges'] = _find_part_ranges(ip._score)
        ip._metadata['pieceRange'] = _find_piece_range(ip._score)
        ip._imported = True

    return score

def _import_directory(directory, metafile=None):
    """
    Helper method to import files from a directory. Also handles what 
    file types to skip over.
    """
    pieces = [] # a list of the pieces being imported
    meta = metafile

    if isinstance(directory, list):
        file_paths = directory

    else: # the `directory` argument is the pathname of a directory
        file_paths = []
        for root, dirs, files in os.walk(directory):
            for f in files:
                # exclude ds_stores
                if f == '.DS_Store': 
                    continue
                # skip python files
                if f.endswith('.py'):  
                    continue
                # skip compiled python files
                if f.endswith('.pyc'): 
                    continue
                # filter out hidden files if they show up
                if len(f) > 1 and f[:2] == '._': 
                    continue
                # attach meta files if they exist
                if f == 'meta': 
                    meta = root + '/meta'
                    continue
                file_paths.append('/'.join((root, f)))

    if not file_paths:
        raise RuntimeError(vis.models.aggregated_piece.AggregatedPieces._NO_FILES)

    for path in file_paths:
        # use extend rather than append because it could import as a multi-movement opus
        pieces.extend(_import_file(pathname=path, metafile=meta))

    return (pieces, meta)

def Importer(location, metafile=None):
    """
    Import the file, website link, or directory of files designated by ``location`` to music21 
    format.

    :param location: Location of the file to import on the local disk.
    :type location: str
    :returns: An :class:`IndexedPiece` or an :class:`AggregatedPieces` object if the file passed 
        imports as a :class:`music21.stream.Score` or :class:`music21.stream.Opus` object
        respectively.
    :rtype: A new :class:`IndexedPiece` or :class:`AggregatedPieces` object.
    """
    pieces = []

    # load directory of pieces
    if isinstance(location, list) or os.path.isdir(location):
        directory_return = _import_directory(location, metafile)
        pieces.extend(directory_return[0])
        metafile = directory_return[1]

    # index piece if it is a file or a link
    elif os.path.isfile(location):
        pieces.extend(_import_file(location))

    else:
        raise RuntimeError(_UNKNOWN_INPUT)

    if len(pieces) == 1: # there was a single piece that imported as a score (not an opus)
        return(pieces[0]) # this returns an IndexedPiece object
    else: # there were multiple pieces or a single piece that imported as an opus
        return(AggregatedPieces(pieces=pieces, metafile=metafile))


class IndexedPiece(object):
    """
    Hold indexed data from a musical score, and the score itself. IndexedPiece objects are VIS's 
    basic representations of a piece of music and also a container for metadata and analyses about 
    that piece. An IndexedPiece object should be created by passing the pathname of a symbolic 
    notation file to the Importer() method in this file. The Importer() will return an IndexedPiece 
    object as long as the piece did not import as an opus. In this case Importer() will return an 
    AggregatedPieces object. Information about an IndexedPiece object from an indexer or an 
    experimenter should be requested via the get_data() method. If you want to access the full 
    music21 score object of a VIS IndexedPiece object, access the _score attribute of the 
    IndexedPiece object. See the examples below:

    **Examples**
    # Creat an IndexedPiece object
    from vis.models.indexed_piece import Importer
    ip = Importer('path_to_file.xml')

    # Get the results of an indexer or experimenter (noterest and dissonance indexers shown)
    noterest_results = ip.get_data('noterest')
    dissonance_results = ip.get_data('dissonance')

    # Access the full music21 score object of the file
    ip._score
    """

    # When get_data() is missing the "settings" and/or data" argument but needed them, or was 
    # supplied this information, but couldn't use it.
    _SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS = 'You made improper use of the settings and/or data \
arguments. Please refer to the {} documentation to see what is required by the Indexer or \
Experimenter requested.'

    # When get_data() gets an analysis_cls argument that isn't a key in IndexedPiece._mkd.
    _NOT_AN_ANALYZER = 'Could not recognize the requested Indexer or Experimenter (received {}). \
When using IndexedPiece.get_data(), please use one of the following short- or long-format \
strings to identify the desired Indexer or Experimenter: {}.'

    # When measure_index() is run on a piece with no measure information.
    _NO_MEASURES = 'VIS is unable to detect measures in this IndexedPiece. Please note that measures \
are not encoded in midi files so VIS currently cannot detect measures in midi files.'

    # When measure_index() is passed something other than a dataframe.
    _NOT_DATAFRAME = 'The passed argument must be a pandas.DataFrame and cannot be empty.'

    # When metadata() gets an invalid field name
    _INVALID_FIELD = 'metadata(): invalid field ({})'

    # When metadata()'s "field" is not a string
    _META_INVALID_TYPE = "metadata(): parameter 'field' must be of type 'string'"

    _MISSING_USERNAME = ('You must enter a username to access the elvis database')
    _MISSING_PASSWORD = ('You must enter a password to access the elvis database')
    def __init__(self, pathname='', opus_id=None, score=None, metafile=None, username=None, password=None):
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
        self._pathname = pathname
        self._metadata = {}
        self._known_opus = False
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score
        self._username = username
        self._password = password
        # Multi-key dictionary for calls to get_data()
        self._mkd = mkd({ # Indexers (in alphabetical order of their long-format strings):
                        ('active_voices', 'active_voices.ActiveVoicesIndexer', active_voices.ActiveVoicesIndexer): self._get_active_voices,
                        ('approach', 'approach.ApproachIndexer', approach.ApproachIndexer): self._get_approach,
                        ('contour', 'contour.ContourIndexer', contour.ContourIndexer): contour.ContourIndexer,
                        ('dissonance', 'dissonance.DissonanceIndexer', dissonance.DissonanceIndexer): self._get_dissonance,
                        ('fermata', 'fermata.FermataIndexer', fermata.FermataIndexer): self._get_fermata,
                        ('horizontal_interval', 'interval.HorizontalIntervalIndexer', interval.HorizontalIntervalIndexer): self._get_horizontal_interval,
                        ('vertical_interval', 'interval.IntervalIndexer', interval.IntervalIndexer): self._get_vertical_interval,
                        ('duration', 'meter.DurationIndexer', meter.DurationIndexer): self._get_duration,
                        ('measure', 'meter.MeasureIndexer', meter.MeasureIndexer): self._get_measure,
                        ('beat_strength', 'meter.NoteBeatStrengthIndexer', meter.NoteBeatStrengthIndexer): self._get_beat_strength,
                        ('ngram', 'ngram.NGramIndexer', ngram.NGramIndexer): self._get_ngram,
                        ('multistop', 'noterest.MultiStopIndexer', noterest.MultiStopIndexer): self._get_multistop,
                        ('noterest', 'noterest.NoteRestIndexer', noterest.NoteRestIndexer): self._get_noterest,
                        ('offset', 'offset.FilterByOffsetIndexer', offset.FilterByOffsetIndexer): self._get_offset,
                        ('over_bass', 'over_bass.OverBassIndexer', over_bass.OverBassIndexer): over_bass.OverBassIndexer,
                        ('repeat', 'repeat.FilterByRepeatIndexer', repeat.FilterByRepeatIndexer): repeat.FilterByRepeatIndexer,
                        ('windexer', 'windexer.Windexer', windexer.Windexer): windexer.Windexer,
                        # Experimenters (in alphabetical order of their long-format strings):
                        ('aggregator', 'aggregator.ColumnAggregator', aggregator.ColumnAggregator): aggregator.ColumnAggregator,
                        ('bar_chart', 'barchart.RBarChart', barchart.RBarChart): barchart.RBarChart,
                        # The dendrogram experimenter should only be used by an AggregatedPieces object
                        ('frequency', 'frequency.FrequencyExperimenter', frequency.FrequencyExperimenter): frequency.FrequencyExperimenter
						})

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
            for i, p in enumerate(self._get_part_streams()):
                # NB: since we don't use ActiveSites, not restoring them is a minor speed-up. Also, 
                # skipSelf will soon change its default to True in music21.
                ser = pandas.Series(p.recurse(restoreActiveSites=False, skipSelf=True),
                                    name=self.metadata('parts')[i])
                ser.index = ser.apply(_get_offsets, args=(p,))
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

    def _get_duration(self, data=None):
        """Used internally by get_data() to cache and retrieve results from the 
        meter.DurationIndexer. The `data` argument should be a 2-tuple where the first element is 
        a dataframe of results with one column per voice (like the noterest indexer) and the second 
        element is a list of the part streams, one per part."""
        if data is not None:
            return meter.DurationIndexer(data[0], data[1]).run()
        elif 'duration' not in self._analyses:
            self._analyses['duration'] = meter.DurationIndexer(self._get_noterest(), self._get_part_streams()).run()
        return self._analyses['duration']

    def _get_active_voices(self, data=None, settings=None):
        """Used internally by get_data() to cache and retrieve results from the 
        active_voices.ActiveVoicesIndexer."""
        if data is not None:
            return active_voices.ActiveVoicesIndexer(data, settings).run()
        elif 'active_voices' not in self._analyses and (settings is None or settings == 
                active_voices.ActiveVoicesIndexer.default_settings):
            self._analyses['active_voices'] = active_voices.ActiveVoicesIndexer(self._get_noterest()).run()
            return self._analyses['active_voices']
        return active_voices.ActiveVoicesIndexer(self._get_noterest(), settings).run()

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

    def _get_approach(self, data=[], settings=None):
        """Used internally by get_data() as a convenience method to simplify getting results from 
        the ApproachIndexer. Since the results of the FermataIndexer are required for this and do not 
        take any settings, they are automatically provided for the user, so only the results of the 
        OverBassIndexer must necessarily be provided in the 'data' argument."""
        if len(data) == 1: # If data has more than two dfs, or the wrong dfs, this will be caught later
            temp = [self._get_fermata()]
            temp.extend(data)
            data = temp
        return approach.ApproachIndexer(data, settings).run()

    def _get_m21_measure_objs(self):
        """Makes a dataframe of the music21 measure objects in the indexed_piece. Note that midi 
        files do not have measures."""
        if 'm21_measure_objs' not in self._analyses:
            # filter for just the measure objects in each part of this indexed piece
            sers = [s.apply(_type_func_measure).dropna() for s in self._get_m21_objs()]
            self._analyses['m21_measure_objs'] = pandas.concat(sers, axis=1)
        return self._analyses['m21_measure_objs']

    def _get_measure(self):
        """Fetches and caches a dataframe of the measure numbers in a piece."""
        if 'measure' not in self._analyses:
            self._analyses['measure'] = meter.MeasureIndexer(self._get_m21_measure_objs()).run()
        return self._analyses['measure']

    def _get_ngram(self, data, settings=None):
        """Convenience method for fethcing ngram indexer results. These results never get cached 
        though, because there are too many unpredictable variables in ngram queries."""
        return ngram.NGramIndexer(data, settings).run()

    def _get_offset(self, data, settings=None):
        if (settings is not None and settings['quarterLength'] == 'dynamic' and 
            ('dom_data' not in settings or type(settings['dom_data']) != list)):
            settings['dom_data'] = [self._get_dissonance(), self._get_duration(),
                                     self._get_beat_strength(), self._get_noterest(),
                                     self._get_time_signature(), 
                                     self._get_part_streams()[0].highestTime]
        return offset.FilterByOffsetIndexer(data, settings).run()

    def _get_time_signature(self):
        """Experimental method used only by the offset indexer when its 'dynamic' setting is 
        active. This returns a dataframe of the time signature strings in a piece."""
        if 'time_signature' not in self._analyses:
            lyst = [ser.apply(_type_func_time_signature).dropna() for ser in self._get_m21_objs()]
            self._analyses['time_signature'] = pandas.concat(lyst, axis=1)
        return self._analyses['time_signature']


    def get_data(self, analyzer_cls, data=None, settings=None):
        """
        Get the results of an Experimenter or Indexer run on this :class:`IndexedPiece`.

        :param analyzer_cls: The analyzer to run.
        :type analyzer_cls: str or VIS Indexer or Experimenter class.
        :param settings: Settings to be used with the analyzer. Only use if necessary.
        :type settings: dict
        :param data: Input data for the analyzer to run. If this is provided for an indexer that 
            normally caches its results (such as the NoteRestIndexer, the DurationIndexer, etc.), 
            the results will not be cached since it is uncertain if the input passed in the ``data`` 
            argument was calculated on this indexed_piece.
        :type data: Depends on the requirement of the analyzer designated by the ``analyzer_cls`` 
            argument. Usually a :class:`pandas.DataFrame` or a list of :class:`pandas.Series`.
        :returns: Results of the analyzer.
        :rtype: Usually :class:`pandas.DataFrame` or list of :class:`pandas.Series`.
        :raises: :exc:`RuntimeWarning` if the ``analyzer_cls`` is invalid or cannot be found.
        :raises: :exc:`RuntimeError` if the first analyzer class in ``analyzer_cls`` does not use
            :class:`~music21.stream.Score` objects, and ``data`` is ``None``.
        """
        if analyzer_cls not in self._mkd: # Make sure the analyzer requested exists.
            raise KeyError(IndexedPiece._NOT_AN_ANALYZER.format(analyzer_cls, sorted([k[0] for k in self._mkd.keys()])))

        args_dict = {} # Only pass the settings argument if it is not ``None``.
        if settings is not None:
            args_dict['settings'] = settings

        try: # Fetch or calculate the actual results requested.
            if data is None:
                results = self._mkd[analyzer_cls](**args_dict)
            else:
                results = self._mkd[analyzer_cls](data, **args_dict)
            if hasattr(results, 'run'): # execute analyzer if there is no caching method for this one
                results = results.run()
        except TypeError: # There is some issue with the 'settings' and/or 'data' arguments.
            for key in self._mkd.keys():
                if analyzer_cls in key:
                    analyzer_name = key[1]
                    break
            raise RuntimeWarning(IndexedPiece._SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS.format(analyzer_name))

        return results

    def measure_index(self, dataframe):
        """Multi-indexes the index of the passed dataframe by adding the measures to the offsets. 
        The passed dataframe should be of an indexer's results, not an experimenters. Also adds 
        index labels. Note that this method currently does not work with midi files, because VIS 
        cannot detect measures in midi files since they are not encoded in midi. Also note that this 
        method should ideally only be used at the end of a set of analysis steps, because there is 
        no guarantee that the resultant multi-indexed dataframe will not cause problems if passed to 
        a subsequent indexer.

        **Example**
        from vis.models.indexed_piece import Importer()
        # Make an IndexedPiece object out of a symbolic notation file:
        ip = Importer('path_to_file.xml')
        # Get some results from an indexer (not an experimenter):
        df = ip.get_data('horizontal_interval')
        # Multi-index the dataframe index by adding the measure informaiton:
        ip.measure_index(df)
        """
        if not isinstance(dataframe, pandas.DataFrame):
            raise RuntimeWarning(IndexedPiece._NOT_DATAFRAME)
        # Make a copy of the dataframe to avoid altering it inplace
        df = dataframe.copy()
        # Get a series of the measures from the first part of this IndexedPiece
        measures = self.get_data('measure').iloc[:, 0]
        # Make sure it actually has measure events in it. NB: measure detection doesn't work with midi files
        if measures.empty:
            raise RuntimeWarning(IndexedPiece._NO_MEASURES)
        # Add measures as a column of the dataframe which merges the indecies
        df['Measure'] = measures
        # Forward-fill measure observations so that there's one label per event
        df['Measure'] = df['Measure'].ffill().apply(int)
        # Provide label for existing index
        df.index.name = 'Offset'
        # Reassign new column as an extra index
        df.set_index('Measure', append=True, inplace=True)
        # Rearrange indecies and return result. NB: rearranging cannot be done in place
        return df.reorder_levels(('Measure', 'Offset'))

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
