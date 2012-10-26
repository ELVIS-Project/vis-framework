#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         NGram.py
# Purpose:      Class-based representation of an n-gram of vertical intervals.
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



## Import:
# Python
import re
#from string import lower as lowercase
#from string import digits as str_digits
#from string import replace as str_replace
# music21
from music21 import interval
from music21 import note
# vis
from problems import MissingInformationError, NonsensicalInputError
from VIS_Settings import VIS_Settings



#-------------------------------------------------------------------------------
class NGram( object ):
   '''
   Represents an n-gram. In other words, holds 'n'
   :class:`music21.interval.Interval` objects and information about the voice
   movement between them.
   '''
   ## Instance Data
   # _n
   # _list_of_intervals
   # _list_of_movements
   # _string
   # _has_voice_crossing
   def __init__( self, some_intervals ):
      '''
      Create a new n-gram when given a list of the
      :class:`music21.interval.Interval` objects that are part of the n-gram.

      Note that all the Interval objects must have :class:`music21.note.Note`
      objects embedded, to calculate the "distance" between adjacent
      vertical intervals.

      If an Interval is descending, this is considered to be a voice crossing.
      The lower voice is assumed to be the .noteStart property of every Interval.
      '''
      # How many intervals are in this triangle/n-gram?
      self._n = len(some_intervals)

      # Assign the intervals. Check each one to see if there is a negative
      # interval, which would signify voice crossing.
      self._has_voice_crossing = False
      self._list_of_intervals = []
      for interv in some_intervals:
         # Check direction
         if -1 == interv.direction:
            self._has_voice_crossing = True
         # Assign to new NGram
         self._list_of_intervals.append( interv )

      # Calculate melodic intervals between vertical intervals.
      self._calculate_movements()
   # End NGram() ------------------------------------------

   # internal method
   def _calculate_movements( self ):
      '''
      Calculates the movement of the lower part between adjacent Interval
      objects, then returns a list of them.
      '''

      # This choice of iteration is a nice hack from
      # http://stackoverflow.com/questions/914715/
      # python-looping-through-all-but-the-last-item-of-a-list
      post = []
      zipped = zip( self._list_of_intervals, self._list_of_intervals[1:] )
      try:
         post = [interval.Interval( i.noteStart, j.noteStart ) for i, j in zipped]
      except AttributeError:
         msg = 'NGram: Probably one of the intervals is missing a note.Note'
         raise MissingInformationError( msg )

      self._list_of_movements = post
   #-------------------------------------------------------

   def get_intervals( self ):
      '''
      Returns a list of the vertical Interval objects of this NGram.
      '''
      return self._list_of_intervals

   def get_movements( self ):
      '''
      Returns a list of the horizontal Interval objects between the lower voice
      in each of the vertical Interval objects of this NGram.
      '''
      return self._list_of_movements

   def retrograde( self ):
      '''
      Returns the retrograde (backwards) n-gram of self.

      >>> from music21 import *
      >>> from vis import *
      >>> s = visSettings()
      >>> a = interval.Interval( note.Note('C4'), note.Note('E4') )
      >>> b = interval.Interval( note.Note('D4'), note.Note('E4') )
      >>> ng = NGram( [a, b], s )
      >>> ng.retrograde() == NGram( [b, a], s )
      True
      '''
      return NGram( self._list_of_intervals[::-1] )

   def n( self ):
      '''
      Return the 'n' of this n-gram, which means the number of vertical
      intervals in this object.
      '''
      return self._n

   def __repr__( self ):
      # The Python standard suggests the return value from this method should
      # be sufficient to re-create the object. This is a little more complicated
      # than the music21 core classes make it seem.

      # Start out with NGram constructor.
      post = __name__ + '( ['

      # Add a constructor for every Interval.
      for each_int in self._list_of_intervals:
         post += "Interval( Note( '" + each_int.noteStart.nameWithOctave + \
               "' ), Note( '" + each_int.noteEnd.nameWithOctave + "' ) ), "

      # Remove the final ", " from the list of Intervals
      post = post[:-2]

      # Append the final parenthesis.
      post += "] )"

      return post

   def canonical( self ):
      '''
      Return the "canonical non-crossed" str representation of this NGram
      object. This is like an "absolute value" function, in that it removes any
      positive/negative signs and does not do much else.

      Be cautious about interpreting the meaning of this method's return values.
      This 'm3 M2 m3' matches any of the following:
      - 'm-3 +M2 m-3'
      - 'm-3 +M2 m3'
      - 'm3 -M2 m-2'
      - etc.
      These are not necessarily experientially similar.
      '''
      post = self.get_string_version(True, 'compound').replace( '-', '' )
      return post.replace( '+', '' )

   def voice_crossing( self ):
      '''
      Returns True if the NGram object has voice crossing (meaning that one
      or more of the Interval objects has a negative direction) or else False.
      '''
      return self._has_voice_crossing

   def get_string_version( self, heed_quality=False, \
                           simple_or_compound='compound' ):
      '''
      Return a string-format representation of this NGram object. With no
      arguments, the intervals are compound, and quality not heeded.

      If the first argument is a VIS_Settings object, the parameters are taken
      from it and the second argument is ignored.

      Example:

      >>> from music21 import *
      >>> from vis import *
      >>> s = VIS_Settings()
      >>> a = interval.Interval( note.Note('C4'), note.Note('E5') )
      >>> b = interval.Interval( note.Note('D4'), note.Note('E5') )
      >>> ng = NGram( [a, b] )
      >>> ng.get_string_version( heed_quality=False, simple_or_compound='simple' )
      '3 +2 2'
      >>> s.set_property( 'heedQuality False' )
      >>> ng.get_string_version( s )
      '10 +2 9'
      '''

      # Deal with the settings
      if isinstance( heed_quality, VIS_Settings ):
         # Extract settings from the VIS_Settings instance.
         # NB: We have to set heed_quality last, or we can't get further
         # settings from it.
         simple_or_compound = heed_quality.get_property( 'simpleOrCompound' )
         heed_quality = heed_quality.get_property( 'heedQuality' )

      # Hold the str we're making
      post = ''

      # We need to consider every index of _list_of_intervals, which contains
      # the vertical intervals of this NGram.
      for i, interv in enumerate(self._list_of_intervals):
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
         if not heed_quality:
            this_interval = this_interval[1:]

         # Append this interval
         post += this_interval

         # Calculate the lower-voice movement after this interval.
         # NB: The final interval won't have anything, and currently we deal
         # with this by simply catching the IndexError that would result, and
         # ignoring it. There's probably a more elegant way.
         this_move = None
         try:
            this_move = self._list_of_movements[i]
         except IndexError:
            pass

         # Add the direction to the horizontal interval. The call to
         # isinstance() means we won't try to find the direction of None, which
         # is what would happen for the final horizontal interval.
         if isinstance( this_move, interval.Interval ):
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

            if not heed_quality:
               zzz = zzz[1:]

            post += zzz

            this_move = None
      # End the "for"

      return post
   # end get_string_version --------------------------------------------

   def get_inversion_at_the( self, interv, up_or_down='up' ):
      '''
      Returns an NGram with the upper and lower parts inverted at the interval
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
      >>> i1 = interval.Interval( note.Note( 'A4' ), note.Note( 'C5' ) )
      >>> i2 = interval.Interval( note.Note( 'B4' ), note.Note( 'E5' ) )
      >>> ng = NGram( [i1,i2] )
      >>> str(ng.get_inversion_at_the( 12, 'up' ))
      'M-10 +M2 M-9'
      '''

      def get_inverted_quality( start_spec ):
         '''
         "Inner function" to transform a quality-letter into the quality-letter
         needed for inversion
         '''
         if 'd' == start_spec:
            return 'A'
         elif 'm' == start_spec:
            return 'M'
         elif 'P' == start_spec:
            return 'P'
         elif 'M' == start_spec:
            return 'm'
         elif 'A' == start_spec:
            return 'd'
         else:
            msg = 'Unexpected interval quality: ' + str(start_spec)
            raise MissingInformationError( msg )

      def check_for_stupid( huh ):
         '''
         "Inner function" to check for stupid intervals like 'm4'
         '''

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
      if isinstance( interv, int ):
         interv = str(interv)

      # Go through the intervals in this NGram instance and invert each one.
      inverted_intervals = []
      for old_interv in self._list_of_intervals:
         # We are transposing the bottom note up
         if 'up' == up_or_down:
            # Make the str representing the interval of transposition. We have
            # to do this for every interval because we're doing diatonic
            # transposition, so the resulting quality changes depending on the
            # input quality.
            trans_interv = get_inverted_quality( old_interv.name[0] ) + interv

            # Double-check that we don't have something like "m4"
            trans_interv = check_for_stupid( trans_interv )

            # Transpose it
            trans_interv = interval.Interval( trans_interv )
            new_start = old_interv.noteStart.transpose( trans_interv )

            # Make the new interval
            new_interv = interval.Interval( new_start, old_interv.noteEnd )
         # We're transposing the top note down
         elif 'down' == up_or_down:
            # Make the str representing the interval of transposition.
            trans_interv = get_inverted_quality( old_interv.name[0] ) + \
                           '-' + interv

            # Double-check that we don't have something like "m4"
            trans_interv = check_for_stupid( trans_interv )

            # Transpose it
            trans_interv = interval.Interval( trans_interv )
            new_end = old_interv.noteEnd.transpose( trans_interv )

            # Make the new interval
            new_interv = interval.Interval( old_interv.noteStart, new_end )
         else:
            msg = 'Inversion direction must be either "up" or "down"; received ' + \
                  str(up_or_down)
            raise NonsensicalInputError( msg )

         # Append the new Interval to the list that will be sent to the NGram
         # constructor.
         inverted_intervals.append( new_interv )

      # Make a new NGram object to return
      return NGram( inverted_intervals )
   # End get_inversion_at_the() ------------------------------------------------

   @classmethod
   def make_from_str( cls, string ):
      # TODO: write documentation and follow style guidelines
      # TODO: docstring
      # TODO: refactor this method to use better variable names
      vertical = re.compile( r'([MmAdP]?)([-]?)([\d]+)')
      horizontal = re.compile( r'([+-]?)([MmAdP]?)([\d]+)' )

      # Error message used many times
      err_msg = 'cannot make N-Gram from badly formatted string'

      def make_vert( s ):
         '''
         Given a string s representing a vertical
         interval (no + or - before it) with or
         without quality, return a music21
         Interval object corresponding to it.
         '''
         m = vertical.match( s )
         if m is None or m.group( 0 ) != s:
            raise NonsensicalInputError( err_msg )
         if m.group( 1 ) == "":
            try:
               return interval.Interval( 'M' + s )
            except:
               return interval.Interval( 'P' + s )
         else:
            return interval.Interval( s )

      def make_horiz( s ):
         '''
         Given a string s representing a horizontal
         interval (with + or - out front), return
         an appropriate music21 Interval object.
         '''
         m = horizontal.match( s )
         if m is None or m.group( 0 ) != s:
            raise NonsensicalInputError( err_msg )
         sign = m.group( 1 ) if m.group( 1 ) == "-" else ""
         if m.group( 2 ) == "":
            try:
               return interval.Interval( 'M' + sign + m.group(3) )
            except:
               return interval.Interval( 'P' + sign + m.group(3) )
         else:
            return interval.Interval( m.group(2) + sign + m.group(3) )

      intervals = string.split(' ')

      if len(intervals) % 2 == 0 or len(intervals) < 3:
         msg = 'cannot make N-Gram from wrong number of intervals'
         raise NonsensicalInputError( msg )

      nt = note.Note( 'C4' )
      l_i = []
      for i, interv in list(enumerate(intervals))[:-2:2]:
         new_int = make_vert( interv )
         new_int.noteStart = nt
         l_i.append( new_int )
         horiz = make_horiz( intervals[i+1] )
         horiz.noteStart = nt
         nt = horiz.noteEnd
      last_int = make_vert( intervals[-1] )
      last_int.noteStart = nt
      l_i.append( last_int )

      ng = NGram( l_i )
      return ng

   def __str__( self ):
      return repr(self)

   def __eq__( self, other ):
      # an NGram is purely a list of intervals and list of movements
      return self._list_of_intervals == other._list_of_intervals and \
             self._list_of_movements == other._list_of_movements

   def __ne__( self, other ):
      return not self == other
#-------------------------------------------------------------------------------
