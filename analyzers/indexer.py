#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
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
The controllers that deal with indexing data from music21 Score objects.
"""

import copy
import pandas
from music21 import stream, note, base, interval, duration


def mp_indexer(parts, indexer_func, types=None):
    """
    Perform the indexation of a part, or part combination. This is a module-level function designed
    to ease implementation of multiprocessing with the MPController module.

    Calling Indexers with settings should adjust for these before calling mp_indexer().

    Calling Indexers with required indexers must ensure their presence before calling mp_indexer().

    Parameters:
    ===========
    parts : [music21.stream.Part] or [pandas.Series]
        A list of at least one Part or Series object. Every new event, or change of simlutaneity,
        will appear in the outputted index. Therefore, the new index will contain at least as many
        events as the inputted Part or Series with the most events.

    indexer_func : function
        This function transforms found events into another suitable format. The output of this
        function is put into an ElementWrapper object.

    types : list of type objects
        Required only if "parts" contains Part objects (otherwise ignored). Only objects of a type
        in this list will be passed to the indexer_func for inclusion in the resulting index.

    Returns:
    ========
    pandas.Series :
        The new index. Each element is an instance of music21.base.ElementWrapper. The output of
        the indexer_func is stored in the "obj" attribute. Each ElementWrapper has an appropriate
        offset according to its place in the score.
    """
    # NB: It's hard to tell, but this function is based on music21.stream.Stream.chordify()

    # copy the streams/series
    all_parts = copy.deepcopy(parts)

    # flatten the streams or change Series to Parts, as required
    if isinstance(parts[0], stream.Stream):
        all_parts = [x.flat.getElementsByClass(types) for x in all_parts]
    else:
        all_parts = [stream.Part(x) for x in all_parts]

    # first, collect all unique offsets for each measure
    unique_offsets = []
    for each_part in all_parts:
        part_uniques = each_part._uniqueOffsetsAndEndTimes()
        for each_offset in part_uniques:
            if each_offset not in unique_offsets:
                unique_offsets.append(each_offset)

    unique_offsets = sorted(unique_offsets)

    for each_part in all_parts:
        each_part.sliceAtOffsets(offsetList=unique_offsets, inPlace=True)

    # Convert to requested index format
    post = []
    for each_offset in unique_offsets:
        # copied/modified from _event_finder() in controllers/analyzer.py of vis9c
        current_events = []
        for each_part in all_parts:
            possible = []
            try:
                possible = each_part.getElementsByOffset(each_offset, mustBeginInSpan=False)
            except stream.StreamException:
                pass
            if 0 < len(possible):
                current_events.append(possible[0])
        if 0 == len(current_events):
            continue  # TODO: why do I need this?
        new_obj = base.ElementWrapper(indexer_func(current_events))
        new_obj.offset = each_offset  # copy offset to new Stream
        try:  # set duration for previous event
            post[-1].duration = duration.Duration(each_offset - post[-1].offset)
        except IndexError:
            pass
        post.append(new_obj)

    return pandas.Series(post)


class Indexer(object):
    # NOTE: Change "object" to "Indexer" in subclasses.
    """
    Create an index of a music21 stream.

    Use the "requires_score" attribute to know whether the __init__() method should be given a
    list of music21.stream.Part objects. If False, use the "required_indices" attribute to get a
    list of the names of Indexers that should be provided instead.

    The name of the indexer, as stored in an IndexedPiece, is the unicode-format version of the
    class name, accessible through the "name()" function (or Indexer.__name__).
    """

    # NOTE: re-implement this in subclasses as needed. The default value, an empty list, means this
    # Indexer operates directly on Part objects.
    required_indices = []

    # NOTE: activate one of these in subclasses
    required_score_type = stream.Part
    #required_score_type = pandas.Series

    # NOTE: re-implement these in subclasses as needed
    possible_settings = {}
    default_settings = {}
    requires_score = False

    #def __init__(self, score, settings={}):
        #"""
        #Create a new Indexer.

        #Parameters
        #==========
        #score : [pandas.Series] or [music21.stream.Part]
            #Depending on how this Indexer works, this is a list of either Part or Series obejcts
            #to use in creating a new index.

        #settings : dict
            #A dict of all the settings required by this Indexer. All required settings should be
            #listed in subclasses. Default is {}.

        #Raises
        #======
        #RuntimeError :
            #- If the "score" argument is the wrong type.
            #- If the "score" argument is not a list of the same types.
            #- If required settings are not present in the "settings" argument.
        #"""
        ## NOTE: Implement this method when writing subclasses.

        ## Check all required settings are present in the "settings" argument. You must ignore
        ## extra settings.
        ## self._settings = settings

        ## Change "Indexer" to the current class name
        #super(Indexer, self).__init__(score)

        ## If self._score is a Stream (subclass), change to a list of types you want to process
        ## self._types = []

        ## Change to the function you want to use
        ## NB: The lambda function receives events in a list of all voices in the current voice
        ##     combination; if this Indexer processes one voice at a time, it's a one-element list.
        ## self._indexer_func = lambda x: None

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
        """

        # NOTE-1: Implement this method when writing subclasses.
        # NOTE-2: We recommend indexing all possible combinations, whenever feasible.

        combinations = []

        # To calculate each part separately:
        combinations = [[x] for x in xrange(len(self._score))]

        # To calculate all 2-part combinations:
        #for left in xrange(len(self._score)):
            #for right in xrange(left + 1, len(self._score)):
                #combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.

        # Return the results.
        return results

    # NOTE: Do not implement any methods below this line in subclasses. ----------------------------
    def __init__(self, score, settings={}):
        """
        Create a new Indexer.

        Parameters
        ==========
        score : [pandas.Series] or [music21.stream.Part]
            Depending on how this Indexer works, this is a list of either Part or Series obejcts
            to use in creating a new index.

        settings : dict
            A dict of all the settings required by this Indexer. All required settings should be
            listed in subclasses. Default is {}.

        Raises
        ======
        RuntimeError :
            - If the "score" argument is the wrong type.
            - If the "score" argument is not a list of the same types.
            - If required settings are not present in the "settings" argument.
        """
        # NOTE: Do not change this method; when writing subclasses, use template __init__() above.

        # Check the "score" argument is either uniformly Part or Series objects.
        for i in xrange(len(score) - 1):
            if type(score[i]) != type(score[i + 1]):
                raise RuntimeError(u'All elements of "score" must be the same type.')
        if not isinstance(score[0], self.required_score_type):
            raise RuntimeError(u'All elements of "score" must be a ' +
                               unicode(self.required_score_type) + '.')

        # Clean up
        super(Indexer, self).__init__()
        self._score = score

    def name(self):
        """
        Return the name used to identify this indexer.
        """
        # NOTE: Do not reimplement this method in subclasses.
        return unicode(self.__name__)

    def _do_multiprocessing(self, combos):
        """
        Dispatch jobs to the MPController for multiprocessing, then await the jobs' completion.

        Parameters
        ==========
        combos : list of list of integers
            A list of all voice combinations to be analyzed. For example:
            - [[0], [1], [2], [3]]
                Analyze each of four parts independently.
            - [[0, 1], [0, 2], [0, 3]]
                Analyze the highest part compared with all others.
            - [[0, 1, 2, 3]]
                Analyze all parts at once.
            The function stored in "self._indexer_func" must know how to deal with the number of
            simultaneous events it will receive.

        Returns
        =======
        [pandas.Series]
            A list of Series.

        Side Effects
        ============
        1.) Blocks until all voice combinations have completed.
        """
        # NOTE: Do not reimplement this method in subclasses.
        # TODO: use the MPController
        # TODO: make this work for IndexedPieces

        #score_arg = None
        post = []

        for each_combo in combos:
            voices = [self._score[x] for x in each_combo]
            if self.required_score_type is stream.Part:
                post.append(mp_indexer(voices, self._indexer_func, self._types))
            else:
                post.append(mp_indexer(voices, self._indexer_func))

        return post


class NoteRestIndexer(Indexer):
    """
    Index music21.note.Note and Rest objects found in a music21.stream.Part.

    Rest objects are indexed as u'Rest', and Note objects as the unicode-format version of their
    "pitchWithOctave" attribute.
    """

    required_indices = []
    required_score_type = stream.Part
    requires_score = True

    def __init__(self, score, settings=None):
        """
        Create a new Indexer.

        Parameters
        ==========
        score : [music21.stream.Part]
            A list of all the Parts to index.

        Raises
        ======
        RuntimeError :
            If the "score" argument is the wrong type.
        """
        # Change "Indexer" to the current class name
        super(NoteRestIndexer, self).__init__(score)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = [note.Rest, note.Note]

        # Change to the function you want to use
        self._indexer_func = lambda x: u'Rest' if isinstance(x[0], note.Rest) \
                                       else unicode(x[0].nameWithOctave)

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        [pandas.Series] :
            A list of the new indices. The index of each Series corresponds to the index of the Part
            used to generate it, in the order specified to the constructor. Each element in the
            Series is an instance of music21.base.ElementWrapper.
        """

        combinations = [[x] for x in xrange(len(self._score))]  # calculate each voice separately
        return self._do_multiprocessing(combinations)


class IntervalIndexer(Indexer):
    """
    Create an index of music21.interval.Interval objects found in the result of a NoteRestIndexer.

    This indexer does not require a score.
    """

    required_indices = [u'NoteRestIndexer']
    required_score_type = pandas.Series
    possible_settings = [u'simple or compound', u'quality']
    default_settings = {u'simple or compound': u'compound', u'quality': False}

    def __init__(self, score, settings={}):
        """
        Create a new IntervalIndexer.

        Parameters
        ==========
        score : vis.models.IndexedPiece
            The piece with parts to index.

        settings : dict
            A dict of relevant settings, both optional. These are:
            - 'simple or compound' : 'simple' or 'compound'
                Whether intervals should be represented in their single-octave form. Defaults to
                'compound'.
            - 'quality' : boolean
                Whether to consider the quality of intervals. Optional. Defaults to False.

        Raises
        ======
        Nothing. There are no required settings.
        """
        # NOTE: Implement this method when writing subclasses.

        # Check all required settings are present in the "settings" argument
        self._settings = {}
        if 'simple or compound' in settings:
            self._settings['simple or compound'] = settings['simple or compound']
        else:
            self._settings['simple or compound'] = IntervalIndexer.default_settings['simple or compound']
        if 'quality' in settings:
            self._settings['quality'] = settings['quality']
        else:
            self._settings['quality'] = IntervalIndexer.default_settings['quality']

        # Change "Indexer" to the current class name
        super(IntervalIndexer, self).__init__(score)

        # If self._score is a Stream (subclass), change to a list of types you want to process
        # self._types = []

        # Change to the function you want to use
        # TODO: optimize this
        # TODO: modify this to use the settings
        self._indexer_func = lambda x: interval.Interval(note.Note(x[0].obj), note.Note(x[1].obj)).name

    def run(self):
        """
        Make a new index of the piece.

        Returns
        =======
        {pandas.Series} :
            A dict of the new indices. The index of each Series corresponds to the indices of the
            Part combinations used to generate it, in the order specified to the constructor. Each
            element in the Series is an instance of music21.base.ElementWrapper.
            Example, if you stored output of run() in the "result" variable:
                result['[0, 1]'] : the highest and second highest parts
        """

        combinations = []

        # To calculate all 2-part combinations:
        for left in xrange(len(self._score)):
            for right in xrange(left + 1, len(self._score)):
                combinations.append([left, right])

        # This method returns once all computation is complete. The results are returned as a list
        # of Series objects in the same order as the "combinations" argument.
        results = self._do_multiprocessing(combinations)

        # Do applicable post-processing, like adding a label for voice combinations.
        post = {}
        for i, combo in enumerate(combinations):
            post[str(combo)] = results[i]

        # Return the results.
        return post
