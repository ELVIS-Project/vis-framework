#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.ngram.py
#
# Fileame: ngram.py
# Purpose: Class-based representation of an n-gram of vertical intervals.
#
# Copyright (C) 2012 Christopher Antila, Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
This module presents the NGram class, representing a list of musical objects
that are optionally connected by other musical objects.

The IntervalNGram subclass is for vertical intervals connected by horizontal
intervals of the lower voice; this is a contrapuntal module.

The ChordNGram subclass is for chords connected by neo-Riemannian
transformations.
"""



# Python
import re
# music21
from music21.interval import Interval
from music21.note import Note
from music21.analysis.neoRiemannian import LRP_combinations as LRP
# vis
#from vis.models.problems import MissingInformationError, NonsensicalInputError
#from VISSettings import VISSettings



class NGram(object):
   # NOTE: when subclassing, you must change "object" to "NGram"
   """
   Represents an n-gram of musical objects, optionally connected by other
   musical objects.
   """

   ## Instance Data
   # _n : how many events are in this n-gram
   # _list_of_events : list of the musical events
   # _list_of_connections : list of the musical events that connect the others
   # _string : string-format representation of this NGram

   def __init__(self, some_events):
      """
      Create a new n-gram when given a list of some events.
      """

      # Call the base class constructor
      # NOTE: uncomment this in subclasses
      #super(___NGram, self).__init__(some_events)

      # How many events are in this n-gram?
      self._n = len(some_events)

      # Assign the events
      self._list_of_events = some_events

      # Calculate connecting events between the primary events
      self._list_of_connections = []

      # (Calculation goes here)
   # End __init__() ------------------------------------------------------------



   def get_events(self):
      """
      Returns a list of the primary events in this NGram.
      """
      return self._list_of_events



   def get_connections(self):
      """
      Returns a list of the connecting events between this NGram's primary
      events.
      """
      return self._list_of_connections



   def retrograde(self):
      """
      Returns the retrograde (backwards) n-gram of self.
      """
      return self.__class__(self._list_of_events[::-1])



   def n(self):
      """
      Return the 'n' of this n-gram, which means the number of primary events.
      """
      return self._n



   def __repr__(self):
      """
      Return the code that could be used to re-create this NGram object.
      """
      # The Python standard suggests the return value from this method should
      # be sufficient to re-create the object. This is a little more complicated
      # than the music21 core classes make it seem.
      pass



   def get_string_version(self):
      """
      Return a string-format representation of this NGram object. Unlike str(),
      this method allows different formatting options.
      """

      # Hold the str we're making
      post = ''

      # We need to consider every index of _list_of_events.
      for i, event in enumerate(self._list_of_events):
         # If post isn't empty, this isn't the first interval added, so we need
         # to put a space between this and the previous int.
         if len(post) > 0:
            post += ' '

         # Calculate/format this event
         this_event = str(event)

         # (formatting goes here)

         # Append this interval
         post += this_event

         # Calculate the connection after this interval.
         # NB: The final event won't be followed by anything, and currently we
         # deal with this by simply catching the IndexError that would result,
         # and ignoring it. There's probably a more elegant way.
         try:
            post += self._list_of_connections[i]
         except IndexError:
            pass

      return post
   # end get_string_version ----------------------------------------------------



   @classmethod
   def make_from_str(cls, given_string):
      """
      Returns an NGram object corresponding to the given string
      """
      pass



   def __str__(self):
      """
      Returns a string-format representation of this NGram instance.
      """
      return self.get_string_version()



   def __eq__(self, other):
      """
      Test whether this NGram object is the same as another.
      """
      # an NGram is just a list of intervals and list of movements
      return self._list_of_events == other._list_of_events and \
             self._list_of_connections == other._list_of_connections



   def __ne__(self, other):
      """
      Test whether this NGram object and another are not equal.
      """
      return not self == other
# End class NGram-----------------------------------------------------------------------------------



class IntervalNGram(NGram):
   """
   Represents an n-gram of vertical intervals connected by the horizontal
   interval of the lower voice.
   """

   ## Instance Data
   # _n : how many events are in this n-gram
   # _list_of_events : list of the musical events
   # _list_of_connections : list of the musical events that connect the others
   # _string : string-format representation of this NGram
   # _has_voice_crossing : whether this IntervalNGram has voice crossing

   def __init__(self, some_events):
      """
      Create a new n-gram when given a list of some events.
      """

      # Call the base class constructor
      super(IntervalNGram, self).__init__(some_events)

      # How many events are in this n-gram?
      self._n = len(some_events)

      # Assign the events
      self._list_of_events = some_events

      # Calculate connecting events between the primary events
      self._list_of_connections = []

      # Set the default value for voice crossing; we'll check whether there is
      # voice crossing below
      self._has_voice_crossing = False

      # Calculate melodic intervals between vertical intervals.
      # This algorithm was inspired by...
      # http://stackoverflow.com/questions/914715/
      # python-looping-through-all-but-the-last-item-of-a-list

      # This holds pairs of vertical intervals, between which we will calculate
      # lower-voice melodic movement.
      zipped = zip(self._list_of_events, self._list_of_events[1:])

      try:
         for i, j in zipped:
            # Add the horizontal interval
            self._list_of_connections.append(Interval(i.noteStart, j.noteStart))
            # Check for voice crossing
            if -1 == i.direction:
               self._has_voice_crossing = True
         # Still need to check the last vertical interval
         if -1 == j.direction:
            self._has_voice_crossing = True
      except AttributeError:
         msg = 'NGram: One of the intervals is probably missing a Note'
         raise RuntimeError(msg)
   # End __init__() ------------------------------------------------------------




   def __repr__(self):
      """
      Return the code that could be used to re-create this NGram object.
      """
      # The Python standard suggests the return value from this method should
      # be sufficient to re-create the object. This is a little more complicated
      # than the music21 core classes make it seem.

      # Start out with IntervalNGram constructor.
      post = 'IntervalNGram(['

      # Add a constructor for every Interval.
      for each_int in self._list_of_events:
         post += "Interval(Note('" + each_int.noteStart.nameWithOctave + \
               "'), Note('" + each_int.noteEnd.nameWithOctave + "')), "

      # Remove the final ", " from the list of Intervals
      post = post[:-2]

      # Append the final parenthesis.
      post += "])"

      return post



   def canonical(self):
      """
      Return the "canonical non-crossed" str representation of this IntervalNGram
      object. This is like an "absolute value" function, in that it removes any
      positive/negative signs and does not do much else.

      Be cautious about interpreting the meaning of this method's return values.
      This 'm3 M2 m3' matches any of the following:
      - 'm-3 +M2 m-3'
      - 'm-3 +M2 m3'
      - 'm3 -M2 m-2'
      - etc.

      These are not necessarily experientially similar.
      """
      post = self.get_string_version(True, 'compound').replace('-', '')
      return post.replace('+', '')



   def voice_crossing(self):
      """
      Returns True if the IntervalNGram object has voice crossing (meaning that one
      or more of the Interval objects has a negative direction) or else False.
      """
      return self._has_voice_crossing



   def get_string_version(self, \
                          show_quality=False, \
                          simple_or_compound='compound'):
      """
      Return a string-format representation of this IntervalNGram object. With no
      arguments, the intervals are compound, and quality not displayed.

      There are two keyword arguments:
      - show_quality : boolean, whether to display interval quality
      - simple_or_compound : 'simple' or 'compound' whether to reduce compound
         intervals to their single-octave equivalent

      Example:

      >>> from music21 import *
      >>> from vis import *
      >>> a = Interval(Note('C4'), Note('E5'))
      >>> b = Interval(Note('D4'), Note('E5'))
      >>> ng = IntervalNGram([a, b])
      >>> ng.get_string_version(heed_quality=True, simple_or_compound='simple')
      'M3 M+2 M2'
      >>> ng.get_string_version(s)
      '10 +2 9'
      """

      # Hold the str we're making
      post = ''

      # We need to consider every index of _list_of_events, which contains
      # the vertical intervals of this IntervalNGram.
      for i, interv in enumerate(self._list_of_events):
         # If post isn't empty, this isn't the first interval added, so we need
         # to put a space between this and the previous int.
         if len(post) > 0:
            post += ' '

         # Calculate this interval
         this_interval = None
         if 'simple' == simple_or_compound:
            this_interval = interv.directedSimpleName
         else:
            this_interval = interv.directedName

         # If we're ignoring quality, remove the quality
         if not show_quality:
            this_interval = this_interval[1:]

         # Append this interval
         post += this_interval

         # Calculate the lower-voice movement after this interval.
         # NB: The final interval won't have anything, and currently we deal
         # with this by simply catching the IndexError that would result, and
         # ignoring it. There's probably a more elegant way.
         this_move = None
         try:
            this_move = self._list_of_connections[i]
         except IndexError:
            pass

         # Add the direction to the horizontal interval. The call to
         # isinstance() means we won't try to find the direction of None, which
         # is what would happen for the final horizontal interval.
         if isinstance(this_move, Interval):
            if 1 == this_move.direction:
               post += ' +'
            elif -1 == this_move.direction:
               post += ' -'
            else:
               post += ' '

            if 'simple' == simple_or_compound:
               zzz = this_move.semiSimpleName
            else:
               zzz = this_move.name

            if not show_quality:
               zzz = zzz[1:]

            post += zzz

            this_move = None

      return post
   # end get_string_version ----------------------------------------------------



   def get_inversion_at_the(self, interv, up_or_down='up'):
      """
      Returns an IntervalNGram with the upper and lower parts inverted at the interval
      specified.

      The interval of inversion must be either an int or a str that contains an
      int. Inversion is always diatonic.

      The second argument, up_or_down, is optional. You should specify either
      'up' or 'down', for whether the inversion should be accomplished by
      transposing the bottom note up or the top note down, respectively. The
      default is 'up'.

      Note that this method *always* assumes that .noteStart is the "bottom"
      and .noteEnd is the "top." There is no check for which Note of the
      interval has a technically higher pitch.

      >>> from music21 import *
      >>> from vis import *
      >>> i1 = Interval(Note('A4'), Note('C5'))
      >>> i2 = Interval(Note('B4'), Note('E5'))
      >>> ng = IntervalNGram([i1,i2])
      >>> str(ng.get_inversion_at_the(12, 'up'))
      'M-10 +M2 M-9'
      """

      def get_inverted_quality(start_spec):
         """
         "Inner function" to transform a quality-letter into the quality-letter
         needed for inversion
         """
         post = ''

         if 'd' == start_spec:
            post = 'A'
         elif 'm' == start_spec:
            post = 'M'
         elif 'P' == start_spec:
            post = 'P'
         elif 'M' == start_spec:
            post = 'm'
         elif 'A' == start_spec:
            post = 'd'

         return post

      def check_for_stupid(huh):
         """
         "Inner function" to check for stupid intervals like 'm4'
         """

         # Hold all the sizes that require "perfect," not "major" or "minor"
         perfect_sizes = ['1', '4', '5', '8', '11', '12', '15', '19', \
                          '20', '23']

         # Get the integer size of the interval
         if '-' == huh[1]:
            size = huh[2:]
         else:
            size = huh[1:]

         # Our only concern is if the size is supposed to be perfected.
         if size in perfect_sizes:
            # If this was destined to be minor or Major, we should change it
            # to be Perfect
            if 'm' == huh[0] or 'M' == huh[0]:
               return 'P' + huh[1:]

         # Otherwise just return what we were given
         return huh

      # Convert the inversion interval to a str, if required.
      if isinstance(interv, int):
         interv = str(interv)

      # Invert each interval in this IntervalNGram instance
      inverted_intervals = []
      for old_interv in self._list_of_events:
         # We are transposing the bottom note up
         if 'up' == up_or_down:
            # Make the str representing the interval of transposition. We have
            # to do this for every interval because we're doing diatonic
            # transposition, so the resulting quality changes depending on the
            # input quality.
            trans_interv = get_inverted_quality(old_interv.name[0]) + interv

            # Double-check that we don't have something like "m4"
            trans_interv = check_for_stupid(trans_interv)

            # Transpose it
            trans_interv = Interval(trans_interv)
            new_start = old_interv.noteStart.transpose(trans_interv)

            # Make the new interval
            new_interv = Interval(new_start, old_interv.noteEnd)
         # We're transposing the top note down
         else: # Assume 'down' == up_or_down
            # Make the str representing the interval of transposition.
            trans_interv = get_inverted_quality(old_interv.name[0]) + \
                           '-' + interv

            # Double-check that we don't have something like "m4"
            trans_interv = check_for_stupid(trans_interv)

            # Transpose it
            trans_interv = Interval(trans_interv)
            new_end = old_interv.noteEnd.transpose(trans_interv)

            # Make the new interval
            new_interv = Interval(old_interv.noteStart, new_end)

         # Append the new Interval to the list that will be sent to the
         # IntervalNGram constructor.
         inverted_intervals.append(new_interv)

      # Make a new IntervalNGram object to return
      return IntervalNGram(inverted_intervals)
   # End get_inversion_at_the() ------------------------------------------------



   @classmethod
   def make_from_str(cls, string):
      """
      Returns an IntervalIntervalNGram object with the specifications of the
      given string-format representation. A valid string would be of the format
      provided by get_string_version().

      If interval quality is not specified, it is assumed to be Major or
      Perfect, as appropriate.
      """

      vertical_re = re.compile(r'([MmAdP]?)([-]?)([\d]+)')
      horizontal_re = re.compile(r'([+-]?)([MmAdP]?)([\d]+)')

      # Error message used many times
      err_msg = 'Cannot make IntevalNGram from the wrong number of intervals'

      def make_vert(int_str):
         """
         Return a music21 Interval object corresponding to the interval string
         given as an argument. The interval string may have a quality or not,
         but it should not have a + or - symbol.
         """
         vert_match = vertical_re.match(int_str)
         if vert_match is None or vert_match.group(0) != int_str:
            raise RuntimeError(err_msg)
         if vert_match.group(1) == "":
            try:
               return Interval('M' + int_str)
            except ValueError: # Interval.__init__() throws a ValueError on things like 'M5'
               return Interval('P' + int_str)
         else:
            return Interval(int_str)
      # End make_vert()

      def make_horiz(int_str):
         """
         Return a music21 Interval object corresponding to the interval string
         given as an argument. The interval string may have a quality or not,
         but it must have a + or - symbol.
         """
         horiz_match = horizontal_re.match(int_str)
         if horiz_match is None or horiz_match.group(0) != int_str:
            raise RuntimeError(err_msg)
         sign = horiz_match.group(1) if horiz_match.group(1) == '-' else ''
         if horiz_match.group(2) == '':
            try:
               return Interval('M' + sign + horiz_match.group(3))
            except ValueError: # Interval.__init__() throws a ValueError on things like 'M5'
               return Interval('P' + sign + horiz_match.group(3))
         else:
            return Interval(horiz_match.group(2) + sign + horiz_match.group(3))
      # End make_horiz()

      intervals = string.split(' ')

      if len(intervals) % 2 == 0 or len(intervals) < 3:
         raise RuntimeError(err_msg)

      the_note = Note('C4')
      list_of_ints = []
      for i, interv in list(enumerate(intervals))[:-2:2]:
         new_int = make_vert(interv)
         new_int.noteStart = the_note
         list_of_ints.append(new_int)
         horiz = make_horiz(intervals[i+1])
         horiz.noteStart = the_note
         the_note = horiz.noteEnd
      last_int = make_vert(intervals[-1])
      last_int.noteStart = the_note
      list_of_ints.append(last_int)

      return IntervalNGram(list_of_ints)
   # End make_from_str() -------------------------------------------------------
# End class IntervalNGram---------------------------------------------------------------------------



class ChordNGram(NGram):
   """
   Represents an n-gram of simultaneities connected by neo-Riemannian
   transformations.
   """

   # Class Data
   # This is a list of all the neo-Riemannian transformations we consider
   # NB: The list includes all of, and only, thost compositions that get from one to any other
   #     12-pc-per-octave major or minor triad.
   list_of_transforms = ['LPR', 'LPRP', 'RLR', 'LRLR', 'PRP', 'PR', 'L', 'LP', 'PLR', 'RL', 'RPR',
                         'PRPR', 'LRP', 'LR', 'LPL', 'PL', 'R', 'RP', 'LRPRP', 'LRPR', 'LRL',
                         'LPLR']

   # This is what to say when two consecutive things are identical
   identical_chords = 'ident'

   # This is what to say when we don't know the transformation between two chords
   unknown_transformation = '?'

   ## Instance Data
   # _n : how many events are in this n-gram
   # _list_of_events : list of the musical events
   # _list_of_connections : list of the musical events that connect the others
   # _string : string-format representation of this NGram
   # _repr : string-format "reper" of this NGram

   def __init__(self, some_events):
      """
      Create a new n-gram when given a list of Chord objects.
      """

      # Call the base class constructor
      super(ChordNGram, self).__init__(some_events)

      # Initialize the data for __repr__()
      self._repr = None

      # How many events are in this n-gram?
      self._n = len(some_events)

      # Assign the events
      self._list_of_events = some_events

      # Calculate connecting events between the primary events
      self._list_of_connections = []

      # (Calculation goes here)
      for i in xrange(1, self._n):
         this_connection = ChordNGram.find_transformation(some_events[i-1], some_events[i])
         self._list_of_connections.append(this_connection)
   # End __init__() ------------------------------------------------------------



   @staticmethod
   def find_transformation(one, another):
      """
      Find the neo-Riemannian transformation between "one" Chord instance and "another" one.
      """
      # We can only calculate connections between major and minor triads... is that what we have?
      if 11 == one.forteClassNumber and 11 == another.forteClassNumber:
         # Are both of the chords already the same?
         if one.orderedPitchClasses == another.orderedPitchClasses:
            return ChordNGram.identical_chords
         else:
            # Then we'll try some trans formations
            for transform in ChordNGram.list_of_transforms:
               if LRP(one, transform).orderedPitchClasses == another.orderedPitchClasses:
                  return transform
            else:
               return ChordNGram.unknown_transformation
      # They aren't just triads, so we can't calculate their connections
      else:
         return ChordNGram.unknown_transformation



   def __repr__(self):
      """
      Return the code that could be used to re-create this NGram object.
      """
      # The Python standard suggests the return value from this method should
      # be sufficient to re-create the object. This is a little more complicated
      # than the music21 core classes make it seem.

      # Maybe we've previously calculated this...
      if self._repr is not None:
         return self._repr
      else:
         # Hold the string we'll return
         post = 'ChordNGram(['

         # Append all but the final Chord
         for simultaneity in self._list_of_events[:-1]:
            post += 'Chord(\'' + str(simultaneity)[21:-1] + '\'), '

         # Append the final Chord
         post += 'Chord(\'' + str(self._list_of_events[-1])[21:-1] + '\')])'

         # Save this for next time!
         self._repr = post

         return post



   def get_string_version(self):
      """
      Return a string-format representation of this ChordNGram object.
      """

      # Hold the str we're making
      post = ''

      # We need to consider every index of _list_of_events.
      for i, event in enumerate(self._list_of_events):
         # If post isn't empty, this isn't the first interval added, so we need
         # to put a space between this and the previous int.
         if len(post) > 0:
            post += ' '

         # Calculate/format this event
         this_event = '<' + str(event)[21:]

         # (formatting goes here)

         # Append this interval
         post += this_event

         # Calculate the connection after this interval.
         # NB: The final event won't be followed by anything, and currently we
         # deal with this by simply catching the IndexError that would result,
         # and ignoring it. There's probably a more elegant way.
         try:
            post +=  ' ==' + self._list_of_connections[i] + '=>'
         except IndexError:
            pass

      return post
   # end get_string_version ----------------------------------------------------



   @classmethod
   def make_from_str(cls, given_string):
      """
      This method raises a NotImplementedError.

      For this method to work, we would have to write something that transforms the result of
      music21.chord.Chord.__str__() into a Chord object. It's not worth it, because we have no
      use for this method yet anwyway.
      """
      raise NotImplementedError('ChordNGram.make_from_str() is not yet implemented.')
# End class ChordNGram------------------------------------------------------------------------------
