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
from string import lower as lowercase
from string import digits as str_digits
from string import replace as str_replace
# music21
from music21 import interval
from music21 import note
# vis
from problems import MissingInformationError, NonsensicalInputError, \
                     NonsensicalInputWarning
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
   # _heed_quality
   # _simple_or_compound
   # _string
   # _has_voice_crossing
   def __init__( self, some_intervals, heed_quality=False, simple_or_compound='compound' ):
      '''
      Create a new n-gram when given a list of the
      :class:`music21.interval.Interval` objects that are part of the n-gram.

      Note that all the Interval objects must have :class:`music21.note.Note`
      objects embedded, to calculate the "distance" between adjacent
      vertical intervals.

      The third argument is a str, either 'simple' or 'compound' depending on
      which type of str output you want.

      If an Interval is descending, this is considered to be a voice crossing.
      The lower voice is assumed to be the .noteStart property of every Interval.

      The second argument, called 'heed_quality,' determines whether to consider
      intervals with their qualities, or just their species (the number). If
      possible, when calling NGram from within a program, you should use an
      visSettings instance to specify heed_quality directly, like this:
      >>> from music21 import *
      >>> from vis import *
      >>> s = visSettings()
      >>> a = interval.Interval( note.Note('C4'), note.Note('E4') )
      >>> b = interval.Interval( note.Note('D4'), note.Note('E4') )
      >>> ng = NGram( [a, b], s )
      NGram( [music21.interval.Interval( music21.note.Note('C4'), music21.note.Note('E4') ),music21.interval.Interval( music21.note.Note('D4'), music21.note.Note('E4') )], False )

      The second argument could also be a VIS_Settings object, in which case
      the third argument is ignored.
      '''
      # Deal with the settings
      if isinstance( heed_quality, VIS_Settings ):
         self._heed_quality = heed_quality.get_property( 'heedQuality' )
         self._simple_or_compound = heed_quality.get_property( 'simpleOrCompound' )
      else:
         self._heed_quality = heed_quality
         self._simple_or_compound = simple_or_compound

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

      # Generate the str representation of this NGram
      self._string = self.get_string_version( self._heed_quality, self._simple_or_compound )
   # End NGram() ------------------------------------------

   # internal method
   def _calculate_movements( self ):
      # Calculates the movement of the lower part between adjacent Interval
      # objects, then returns a list of them.

      # Hold the list of Interval objects.
      post = []
      # Now calculate a list of the Interval objects between the lowest notes.
      # For every note except the last...
      for i, j in zip(self._list_of_intervals,self._list_of_intervals[1:]):
         # this choice of iteration is a nice hack from 
         # http://stackoverflow.com/questions/914715/python-looping-through-all-but-the-last-item-of-a-list

         # Append the Interval between the .noteEnd of each Interval.
         try:
            post.append( interval.Interval( i.noteStart, j.noteStart ) )
         except AttributeError as attrerr:
            raise MissingInformationError( 'NGram: Probably one of the intervals is missing a note.Note' )

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

   def set_heed_quality( self, heed_quality ):
      self._heed_quality = heed_quality
      self._string = self.get_string_version( self._heed_quality, self._simple_or_compound )

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
      reversed_intervals = self._list_of_intervals[::-1]
      return NGram(reversed_intervals, self._heed_quality, self._simple_or_compound)

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
      post = str(self).replace( '-', '' )
      return post.replace( '+', '' )

   def voice_crossing( self ):
      '''
      Returns True if the NGram object has voice crossing (meaning that one
      or more of the Interval objects has a negative direction) or else False.
      '''
      return self._has_voice_crossing

   def get_string_version( self, heed_quality=None, simple_or_compound=None ):
      '''
      Return a string-format representation of this NGram object. With no
      arguments, the intervals are compound, and quality is heeded or not as
      per the setting of this NGram object.

      This function is called internally by str(vis.NGram) so the following
      should be true of any NGram object:
      str(vis.NGram) == NGram.get_string_version()

      You can also call this method directly for different formatting options
      than those at NGram-creation time. If you do this, specify the new
      formatting options either directly or through a VIS_Settings object.

      >>> from music21 import *
      >>> from vis import *
      >>> s = VIS_Settings()
      >>> a = interval.Interval( note.Note('C4'), note.Note('E5') )
      >>> b = interval.Interval( note.Note('D4'), note.Note('E5') )
      >>> ng = NGram( [a, b], s )
      >>> ng.get_string_version()
      'M10 +M2 M9'
      >>> ng.get_string_version( heed_quality=False, simple_or_compound='simple )
      '3 +2 2'
      >>> s.set_property( 'heedQuality False' )
      >>> ng.get_string_version( s )
      '10 +2 9'

      Note that calling this method does not change the internally-stored
      str representation or the internally-stored settings.
      '''

      # Deal with the settings.
      if isinstance( heed_quality, VIS_Settings ):
         # Extract settings from the VIS_Settings instance.
         # NB: We have to set heed_quality last, or we can't get further
         # settings from it.
         simple_or_compound = heed_quality.get_property( 'simpleOrCompound' )
         heed_quality = heed_quality.get_property( 'heedQuality' )
      else:
         if simple_or_compound is None:
            simple_or_compound = self._simple_or_compound
         if heed_quality is None:
            heed_quality = self._heed_quality

      # Hold the str we're making.
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

         # If we're ignoring quality, remove the quality.
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
         except IndexError as inderr:
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
   # end _calculate_string_version --------------------------------------------

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
      >>> ng = NGram( [i1,i2], True )
      >>> str(ng.get_inversion_at_the( 12, 'up' ))
      'M-10 +M2 M-9'
      '''

      # Helper method to transform a quality-letter into the quality-letter
      # needed for inversion
      def get_inverted_quality( start_spec ):
         #start_spec = lowercase( start_spec )
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

      # Helper method to check for stupid intervals like 'm4'
      def check_for_stupid( huh ):
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
            new_start = old_interv.noteStart.transpose( interval.Interval( trans_interv ) )

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
            new_end = old_interv.noteEnd.transpose( interval.Interval( trans_interv ) )

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
      return NGram( inverted_intervals, \
                    self._heed_quality, \
                    self._simple_or_compound )
   # End get_inversion_at_the() ------------------------------------------------

   @staticmethod
   def make_from_str( spec ):
      '''
      Accepts a str of the same format outputted by str(NGram) and outputs a
      new NGram object with the indicated vertical intervals and movements.

      The .noteStart component of the first vertical interval is always C4, and
      all other pitches are determined in relation to that.
      '''

      # (1) Separate the vertical and horizontal components
      #----------------------------------------------------

      # Keep track of whether the previous thing we recorded was vertical or
      # horizontal. We start with "horizontal" so the first thing we record
      # will be vertical
      previous_was = 'horizontal'

      # Hold the intervals remaining to be parsed. We'll start out by removing
      # whitespace characters at the start and end, and by removing any '+'
      # characters, since we assume that non '-' intervals are positive.
      remaining_spec = str_replace( spec, '+', '' ).strip()

      # Hold the vertical and horizontal interval strings, respectively
      vert_interv_str = []
      horiz_interv_str = []

      # For when we're on the last interval
      last_interval = False

      # Do this until there are no more intervals
      while last_interval is not True:
         # DEBUGGING
         #print( "*** shooping with " + remaining_spec )
         # END DEBUGGING
         # Is this the last interval?
         remaining_spec.strip()
         if -1 == remaining_spec.find( ' ' ):
            last_interval = True

         # Break off the first interval... use strip() because music21 doesn't
         # like extra space characters.
         if last_interval:
            this_interval = remaining_spec
         else:
            this_interval = remaining_spec[:remaining_spec.find(' ')].strip()

         # If this is a negative interval, remove the '-' and put it at the end,
         # so that our "is there a quality?" check doesn't get tripped up by the
         # first character not being a digit.
         if '-' in this_interval:
            this_interval = str_replace( this_interval, '.', '' ) + '-'

         # Append to the correct list
         if 'horizontal' == previous_was:
            # This is vertical
            vert_interv_str.append( this_interval )
            previous_was = 'vertical'
         else: # 'vertical' == previous_was
            horiz_interv_str.append( this_interval )
            previous_was = 'horizontal'

         # Remove this interval from the front of the string
         if not last_interval:
            remaining_spec = remaining_spec[remaining_spec.find(' '):].strip()

      # Check that we have the right number of components. This should be one
      # more vertical than horizontal interval.
      if len(vert_interv_str) != ( len(horiz_interv_str) + 1 ):
         msg = 'NGram.make_from_str(): There are the wrong number of intervals'
         raise NonsensicalInputWarning( msg )

      # Final thing... we need to know whether the intervals had a quality
      if vert_interv_str[0][0] in str_digits:
         heed_quality = False
      else:
         heed_quality = True

      # (2) Make Interval objects of all the interval components.
      #----------------------------------------------------------
      # NB1: The reason this is a separate step from the previous is that, if we
      # have intervals without quality, I'll need to assign a quality.
      # NB2: We try to catch some of our mistakes, but if the interval
      # specification is too mangled, we just won't bother.

      # Hold all the sizes that require "perfect," not "major" or "minor."
      perfect_sizes = ['1', '4', '5', '8', '11', '12', '15', '19', '20', '23']

      # Hold the vertical and horizontal intervals, respectively
      vert_intervs = []
      horiz_intervs = []

      # Make all the vertical intervals
      for interv in vert_interv_str:
         # If the first character is a digit, there's no quality, so we add one
         if interv[0] in str_digits:
            if interv in perfect_sizes:
               # This is a "perfect" interval size like 4 or 5
               try:
                  vert_intervs.append( interval.Interval( 'P' + interv ) )
               except ValueError:
                  # This probably means it wasn't "perfect"
                  vert_intervs.append( interval.Interval( 'M' + interv ) )
               except TypeError:
                  # This probably means we have two qualities
                  vert_intervs.append( interval.Interval( interv ) )
            else:
               # This is an "imperfect" interval size like 2 or 3
               try:
                  vert_intervs.append( interval.Interval( 'M' + interv ) )
               except ValueError:
                  # This probably means it wasn't "imperfect"
                  vert_intervs.append( interval.Interval( 'P' + interv ) )
               except TypeError:
                  # This probably means we have two qualities
                  vert_intervs.append( interval.Interval( interv ) )
         else:
            # We already had the quality in the str version
            vert_intervs.append( interval.Interval( interv ) )

      # Make all the horizontal intervals
      for interv in horiz_interv_str:
         # If the first character is a digit, there's no quality, so we add one
         if interv[0] in str_digits:
            if interv in perfect_sizes:
               # This is a "perfect" interval size like 4 or 5
               try:
                  horiz_intervs.append( interval.Interval( 'P' + interv ) )
               except ValueError:
                  # This probably means it wasn't "perfect"
                  horiz_intervs.append( interval.Interval( 'M' + interv ) )
               except TypeError:
                  # This probably means we have two qualities
                  horiz_intervs.append( interval.Interval( interv ) )
            else:
               # This is an "imperfect" interval size like 2 or 3
               try:
                  horiz_intervs.append( interval.Interval( 'M' + interv ) )
               except ValueError:
                  # This probably means it wasn't "imperfect"
                  horiz_intervs.append( interval.Interval( 'P' + interv ) )
               except TypeError:
                  # This probably means we have two qualities
                  horiz_intervs.append( interval.Interval( interv ) )
         else:
            # We already had the quality in the str version
            horiz_intervs.append( interval.Interval( interv ) )

      # (3) Integrate the vertical and horizontal components.
      #------------------------------------------------------

      # We'll use vert_intervs to hold the list of vertical intervals with Note
      # objects that we will pass to the NGram() constructor in step (4)

      # Start off with the first vertical interval. music21 automatically sets
      # the noteEnd property for us.
      vert_intervs[0].noteStart = note.Note( 'C4' )

      # Now loop through the rest of the vertical intervals, setting the
      # noteStart property to the value specified by the horizontal intervals.
      for i in xrange( 1, len(vert_intervs) ):
         vert_intervs[i].noteStart = vert_intervs[i-1].noteStart.transpose( horiz_intervs[i-1] )

      # (4) Call the NGram() constructor and return the result.
      #--------------------------------------------------------
      return NGram( vert_intervs, heed_quality )
   # End make_from_str() -------------------------------------------------------

   def __str__( self ):
      return self._string

   def __hash__( self):
      return hash(self._string)

   def __eq__( self, other ):
      # If they have different heed_quality settings, different 'n' value, or
      # a different number of vertical intervals, then they're not equal.
      if self._heed_quality != other._heed_quality or \
         self._n != other._n or \
         len(self._list_of_intervals) != len(other._list_of_intervals):
         return False

      # If we pay attention to quality...
      elif self._heed_quality:
         # Then we just need to know that the _list_of_itnervals and the
         # _list_of_movements are the same.
         if self._list_of_intervals == other._list_of_intervals and \
            self._list_of_movements == other._list_of_movements:
            return True
         else:
            return False

      # If we don't pay attention to quality...
      else:
         # ... things are more difficult because, as long as the numbers are
         # the same, we're supposed to consider them equal.
         for i, interv in enumerate(self._list_of_intervals):
            if interv.generic.directed != \
               other._list_of_intervals[i].generic.directed:
                  return False

         for i, interv in enumerate(self._list_of_movements):
            if interv.generic.directed != \
               other._list_of_movements[i].generic.directed:
                  return False

         return True

   def __ne__( self, other ):
      return not self == other

#-------------------------------------------------------------------------------
