#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         NGram.py
# Purpose:      Class-based representation of an n-gram of vertical intervals.
#
# Copyright (C) 2012 Christopher Antila
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
# music21
from music21 import interval
from music21 import note
# vis
from problems import NonsensicalInputError



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
   # _string
   def __init__( self, some_intervals, heed_quality=False, simple_or_compound='compound' ):
      '''
      Create a new n-gram when given a list of the
      :class:`music21.interval.Interval` objects that are part of the n-gram.
      
      Note that all the Interval objects must have :class:`music21.note.Note`
      objects embedded, to calculate the "distance" between adjacent
      vertical intervals.
      
      The third interval is a str, either 'simple' or 'compound' depending on
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
      >>> ng = NGram( [a,b], s.get_property( 'heed_quality' ) )
      NGram( [music21.interval.Interval( music21.note.Note('C4'), music21.note.Note('E4') ),music21.interval.Interval( music21.note.Note('D4'), music21.note.Note('E4') )], False )
      '''
      # assign stuff
      self._heed_quality = heed_quality
      self._simple_or_compound = simple_or_compound
      self._n = len(some_intervals)
      self._list_of_intervals = some_intervals
      # do stuff
      self._calculate_movements()
      self._string = self.get_string_version( heed_quality, simple_or_compound )
      
   # internal method
   def _calculate_movements( self ):
      # Calculates the movement of the lower part between adjacent Interval
      # objects, then returns a list of them.
      
      # Hold the list of Interval objects.
      post = []
      # Now calculate a list of the Interval objects between the lowest notes.
      # For every note except the last...
      for i in xrange(len(self._list_of_intervals)-1):
         # Append the Interval between the .noteEnd of each Interval.
         try:
            post.append( interval.Interval( self._list_of_intervals[i].noteStart, \
                                            self._list_of_intervals[i+1].noteStart ) )
         except AttributeError as attrerr:
            raise AttributeError( 'NGram: Received an AttributeError; this probably means one of the intervals is missing a note.Note' )
            #raise NonsensicalInputError( 'NGram: Received an AttributeError; this probably means one of the intervals is missing a note.Note' )
         
      self._list_of_movements = post
   #-------------------------------------------------------

   def n( self ):
      return self._n

   # I think we shouldn't have this method because of difficulties getting
   # different answers depending on heed_quality, and because it's not
   # going to be much different from __str__() anyway.
   #def getIntervals( self ):
      #return self._list_of_intervals
   
   def __repr__( self ):
      # TODO: re-implement this, as per the Python standard... the return
      # value should be sufficient code to re-make an == object.
      return '<' + __name__ + ' ' + str(self) + '>'
   
   def get_string_version( self, heed_quality, simple_or_compound ):
      '''
      Return a string-format representation of this NGram object. With no
      arguments, the intervals are compound, and quality is heeded or not as
      per the setting of this NGram object.
      
      This function is called by str(vis.NGram) so the following should be
      true of any NGram object:
      str(vis.NGram) == NGram.stringVersion()
      '''
      
      post = ''
      
      # for each index in _listOfIntervals
      for i in xrange(len(self._list_of_intervals)):
         # If post isn't empty, put a space between this and the previous int
         if len(post) > 0:
            post += ' '
         
         # Calculate this interval
         this_interval = None
         if 'simple' == simple_or_compound:
            this_interval = self._list_of_intervals[i].directedSimpleName
         elif 'compound' == simple_or_compound:
            this_interval = self._list_of_intervals[i].directedName
         else:
            raise NonsensicalInputError( "NGram.stringVersion(): 'simple_or_compound' (2nd argument) must be either 'simple' or 'compound'." )
         
         # If we're ignoring quality, remove the quality.
         if not heed_quality:
            this_interval = this_interval[1:]
         
         # Append this interval
         post += this_interval
         
         # Calculate the lower-voice movement after this interval.
         this_move = None
         try: # the last interval won't have anything
            this_move = self._list_of_movements[i]
         except IndexError as inderr:
            pass # then just don't add it
         
         if isinstance( this_move, interval.Interval ):
            if 1 == this_move.direction:
               post += ' +'
            elif -1 == this_move.direction:
               post += ' -'
            else:
               post += ' '
            
            if 'simple' == simple_or_compound:
               zzz = this_move.semiSimpleName
            elif 'compound' == simple_or_compound:
               zzz = this_move.name
            else:
               raise NonsensicalInputError( "NGram.stringVersion(): 'simple_or_compound' (2nd argument) must be either 'simple' or 'compound'." )
            
            if not heed_quality:
               zzz = zzz[1:]
            
            post += zzz
            
            this_move = None
         #
         
      return post
   # end _calculate_string_version ------------------------
   
   def __str__( self ):
      return self._string

   def __eq__( self, other ):
      # If they have different heed_quality settings, different 'n' value, or
      # a different number of vertical intervals, then they're not equal.
      if self._heed_quality != other._heed_quality or \
         self._n != other._n or \
         len(self._list_of_intervals) != len(other._list_of_intervals): # should be same as previous line
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
         for i in xrange(len(self._list_of_intervals)):
            if self._list_of_intervals[i].generic.directed != \
               other._list_of_intervals[i].generic.directed:
                  return False
         #
         for i in xrange(len(self._list_of_movements)):
            if self._list_of_movements[i].generic.directed != \
               other._list_of_movements[i].generic.directed:
                  return False
         #
         return True
      #
   #

   def __ne__( self, other ):
      return not self == other

#-------------------------------------------------------------------------------