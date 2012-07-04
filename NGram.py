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
   # _listOfIntervals
   # _listOfMovements
   # _heedQuality
   def __init__( self, someIntervals, heedQuality=False ):
      '''
      Create a new n-gram when given a list of the
      :class:`music21.interval.Interval` objects that are part of the n-gram.

      Note that all the Interval objects must have :class:`music21.note.Note`
      objects embedded, to calculate the "distance" between adjacent
      vertical intervals.

      The second argument, called 'heedQuality,' determines whether to consider
      intervals with their qualities, or just their species (the number). If
      possible, when calling NGram from within a program, you should use an
      visSettings instance to specify heedQuality directly, like this:
      >>> from music21 import *
      >>> from vis import *
      >>> s = visSettings()
      >>> a = interval.Interval( note.Note('C4'), note.Note('E4') )
      >>> b = interval.Interval( note.Note('D4'), note.Note('E4') )
      >>> ng = NGram( [a,b], s.propertyGet( 'heedQuality' ) )
      NGram( [music21.interval.Interval( music21.note.Note('C4'), music21.note.Note('E4') ),music21.interval.Interval( music21.note.Note('D4'), music21.note.Note('E4') )], False )
      '''
      self._heedQuality = heedQuality
      self._n = len(someIntervals)
      self._listOfIntervals = someIntervals
      self._calculateMovements()

   # internal method
   def _calculateMovements( self ):
      # Calculates the movement of between the highest notes of adjacent
      # Interval objects, then returns a list of them.

      # First make sure we have a note.Note for all the vertical intervals.
      # It doesn't matter which direction the Interval is, because if there
      # is a Note in either noteStart or noteEnd, there should be a Note
      # in the other.
      for eachInterval in self._listOfIntervals:
         if not isinstance( eachInterval.noteStart, note.Note ) or \
            not isinstance( eachInterval.noteEnd, note.Note ):
            raise NonsensicalInputError( 'NGram: (At least) one of the vertical intervals doesn\'t have noteStart.' )

      # Now calculate a list of the Interval objects between the lowest notes.
      post = []
      for i in xrange(len(self._listOfIntervals)-1):
         # We need to choose the lower Note from both Interval objects
         firstNote = secondNote = None
         if 1 == self._listOfIntervals[i].direction:
            firstNote = self._listOfIntervals[i].noteStart
         else:
            firstNote = self._listOfIntervals[i].noteEnd
         #
         if 1 == self._listOfIntervals[i+1].direction:
            secondNote = self._listOfIntervals[i+1].noteStart
         else:
            secondNote = self._listOfIntervals[i+1].noteEnd

         post.append( interval.Interval( firstNote, secondNote ) )
      #

      self._listOfMovements = post
   #

   def n( self ):
      return self._n

   # I think we shouldn't have this method because of difficulties getting
   # different answers depending on heedQuality, and because it's not
   # going to be much different from __str__() anyway.
   #def getIntervals( self ):
      #return self._listOfIntervals

   def __repr__( self ):
      # TODO: re-implement this, as per the Python standard... the return
      # value should be sufficient code to re-make an == object.
      return '<' + __name__ + ' ' + str(self) + '>'

   def stringVersion( self, simpleOrCompound='compound', heedQuality=None ):
      '''
      Return a string-format representation of this NGram object. With no
      arguments, the intervals are compound, and quality is heeded or not as
      per the setting of this NGram object.

      This function is called by str(vis.NGram) so the following should be
      true of any NGram object:
      str(vis.NGram) == NGram.stringVersion()
      '''
      # If we weren't given something, we'll take the default for this NGram.
      if None == heedQuality:
         heedQuality = self._heedQuality

      post = ''

      # for each index in _listOfIntervals
      for i in xrange(len(self._listOfIntervals)):
         # If post isn't empty, put a space between this and the previous int
         if len(post) > 0:
            post += ' '

         # Calculate this interval
         thisInt = None
         if 'simple' == simpleOrCompound:
            thisInt = self._listOfIntervals[i].semiSimpleName
         elif 'compound' == simpleOrCompound:
            thisInt = self._listOfIntervals[i].name
         else:
            raise NonsensicalInputError( "NGram.stringVersion(): 'simpleOrCompound' (2nd argument) must be either 'simple' or 'compound'." )

         # If we're ignoring quality, remove the quality.
         if not heedQuality:
            thisInt = thisInt[1:]

         # Append this interval
         post += thisInt

         # Calculate the lower-voice movement after this interval.
         thisMove = None
         try: # the last interval won't have anything
            thisMove = self._listOfMovements[i]
         except IndexError as inderr:
            pass # then just don't add it

         if isinstance( thisMove, interval.Interval ):
            if 1 == thisMove.direction:
               post += ' +'
            elif -1 == thisMove.direction:
               post += ' -'
            else:
               post += ' '

            if 'simple' == simpleOrCompound:
               zzz = thisMove.semiSimpleName
            elif 'compound' == simpleOrCompound:
               zzz = thisMove.name
            else:
               raise NonsensicalInputError( "NGram.stringVersion(): 'simpleOrCompound' (2nd argument) must be either 'simple' or 'compound'." )

            if not heedQuality:
               zzz = zzz[1:]

            post += zzz

            thisMove = None
         #

      return post
   # end stringVersion

   def __str__( self ):
      return self.stringVersion()

   def __eq__( self, other ):
      if self._heedQuality != other._heedQuality or \
         self._n != other._n or \
         len(self._listOfIntervals) != len(other._listOfIntervals): # should be same as previous line
         return False
      elif self._heedQuality: # m3 and M3 are different
         if self._listOfIntervals == other._listOfIntervals and \
            self._listOfMovements == other._listOfMovements:
            return True
         else:
            return False
      else: # m3 and M3 are equivalent
         for i in xrange(len(self._listOfIntervals)):
            l = r = None
            try:
               l = abs(int(str(self._listOfIntervals[i])[-3:-1]))
            except ValueError as emer:
               l = abs(int(str(self._listOfIntervals[i])[-2:-1]))
            #
            try:
               r = abs(int(str(other._listOfIntervals[i])[-3:-1]))
            except ValueError as emer:
               r = abs(int(str(other._listOfIntervals[i])[-2:-1]))
            #
            if l != r:
               return False
         #
         for i in xrange(len(self._listOfMovements)):
            l = r = None
            try:
               l = abs(int(str(self._listOfMovements[i])[-3:-1]))
            except ValueError as emer:
               l = abs(int(str(self._listOfMovements[i])[-2:-1]))
            #
            try:
               r = abs(int(str(other._listOfMovements[i])[-3:-1]))
            except ValueError as emer:
               r = abs(int(str(other._listOfMovements[i])[-2:-1]))
            #
            if l != r or self._listOfMovements[i].direction != other._listOfMovements[i].direction:
               return False
         #
         return True
      #
   #

   def __ne__( self, other ):
      return not self == other

#-------------------------------------------------------------------------------
