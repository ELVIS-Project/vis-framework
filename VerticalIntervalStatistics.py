#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         VerticalIntervalStatistics.py
# Purpose:      Stores statistics for "vis"
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
# vis
from problems import NonsensicalInputError



#-------------------------------------------------------------------------------
class VerticalIntervalStatistics( object ):
   '''
   Holds the statistics discovered by vis. Currently these are:

   - number of occurrences of each Interval
   - number of occurrences of each n-gram
   '''
   # I suspect it's too much work to interactively try to find the
   # quality/no-quality and simple/compound version of everything whenever you
   # want to just find the number of occurrences. Instead, we'll store all four
   # versions of that information. Memory is cheap!

   ## Instance Data
   # _simpleIntervalDict
   # _compoundIntervalDict
   # _compoundQualityNGramsDict
   # _compoundNoQualityNGramsDict
   def __init__( self ):
      '''
      Create a new, "empty" statistics database for a piece.
      '''
      self._simpleIntervalDict = {}
      self._compoundIntervalDict = {}
      self._compoundQualityNGramsDict = [{},{},{}]
      self._compoundNoQualityNGramsDict = [{},{},{}]

   def __repr__( self ):
      return self.__str__( self )

   def __str__( self ):
      return '<VerticalIntervalStatistics about intervals and n-grams>'

   def addInterval( self, theInterval ):
      '''
      Adds a :class:`music21.interval.Interval` to the occurrences information.
      If given a simple interval, add that to both the table of simple and
      compound intervals. If given a compound interval, adds that to the table
      of compound intervals and the single-octave equivalent to the table of
      simple intervals.

      Automatically accounts for tracking quality or not.
      '''

      # it's a simple interval
      if theInterval.name == theInterval.semiSimpleName:
         if theInterval.name in self._simpleIntervalDict:
            self._simpleIntervalDict[theInterval.name] += 1
         else:
            self._simpleIntervalDict[theInterval.name] = 1

         if theInterval.name in self._compoundIntervalDict:
            self._compoundIntervalDict[theInterval.name] += 1
         else:
            self._compoundIntervalDict[theInterval.name] = 1
      # it's a compound interval
      else:
         if theInterval.semiSimpleName in self._simpleIntervalDict:
            self._simpleIntervalDict[theInterval.semiSimpleName] += 1
         else:
            self._simpleIntervalDict[theInterval.semiSimpleName] = 1

         if theInterval.name in self._compoundIntervalDict:
            self._compoundIntervalDict[theInterval.name] += 1
         else:
            self._compoundIntervalDict[theInterval.name] = 1
   # end addInterval()

   def getIntervalOccurrences( self, whichInterval, simpleOrCompound='simple' ):
      '''
      Returns the number of occurrences of a particular
      :class:`music21.interval.Interval`, either (by default) from the table
      with compound intervals, or if the second argument is 'simple' then from
      the table with simple intervals.

      Automatically accounts for tracking quality or not.
      '''
      # Given a species (number), finds all the occurrences of any quality.
      # The second argument should be either self._simpleIntervalDict or
      # self._compoundIntervalDict
      def findNumberOfAllQualities( species, db ):
         qualities = 'dmMPA'
         post = 0
         for quality in qualities:
            if ( quality + species ) in db:
               post += db[quality+species]

         return post
      ##

      # they're ignoring quality
      if whichInterval.isdigit():
         if 'simple' == simpleOrCompound:
            return findNumberOfAllQualities( whichInterval, self._simpleIntervalDict )
         elif 'compound' == simpleOrCompound:
            return findNumberOfAllQualities( whichInterval, self._compoundIntervalDict )
         else:
            errorstr = "VerticalIntervalStatistics.getIntervalOccurrences(): 'simpleOrCompound' must be set to either 'simple' or 'compound'"
            raise NonsensicalInputError( errorstr )
      # they're paying attention to quality
      else:
         if 'simple' == simpleOrCompound:
            if whichInterval in self._simpleIntervalDict:
               return self._simpleIntervalDict[whichInterval]
            else:
               return 0
         elif 'compound' == simpleOrCompound:
            if whichInterval in self._compoundIntervalDict:
               return self._compoundIntervalDict[whichInterval]
            else:
               return 0
         else:
            errorstr = "VerticalIntervalStatistics.getIntervalOccurrences(): 'simpleOrCompound' must be set to either 'simple' or 'compound'"
            raise NonsensicalInputError( errorstr )
   # end getIntervalOccurrences()

   def addNGram( self, theNGram ):
      '''
      Adds an n-gram to the occurrences information. Automatically does or does
      not track quality, depending on the settings of the inputted NGram.
      '''

      # If there isn't yet a dictionary for this 'n' value, then we'll have to
      # make sure there is one.
      while len(self._compoundQualityNGramsDict) <= theNGram._n:
         self._compoundQualityNGramsDict.append( {} )
         self._compoundNoQualityNGramsDict.append( {} )

      # self._compoundQualityNGramsDict
      zzz = theNGram.stringVersion( 'compound', True )
      if zzz in self._compoundQualityNGramsDict[theNGram._n]:
         self._compoundQualityNGramsDict[theNGram._n][zzz] += 1
      else:
         self._compoundQualityNGramsDict[theNGram._n][zzz] = 1
      # self._compoundNoQualityNGramsDict
      zzz = theNGram.stringVersion( 'compound', False )
      if zzz in self._compoundNoQualityNGramsDict[theNGram._n]:
         self._compoundNoQualityNGramsDict[theNGram._n][zzz] += 1
      else:
         self._compoundNoQualityNGramsDict[theNGram._n][zzz] = 1
   # end addNGram()

   def getNGramOccurrences( self, whichNGram, n ):
      '''
      Returns the number of occurrences of a particular n-gram. Currently, all
      n-grams are treated as though they have compound intervals.

      The first argument must be the output from either NGram.stringVersion
      or str(NGram) (which calles stringVersion() internally).

      The second argument is the value 'n' for the n-gram you seek.

      Automatically does or does not track quality, depending on the settings
      of the inputted NGram objects.
      '''

      # I tried to implement this in a cleaner way, predicting whether or not
      # we had a dictionary for the value of n we were given, but it didn't
      # work properly, so I implemented this. This solution is clearly not
      # very good, but at least it works.
      try:
         if whichNGram[0].isalpha(): # heedQuality
            if whichNGram in self._compoundQualityNGramsDict[n]:
               return self._compoundQualityNGramsDict[n][whichNGram]
            else:
               return 0
         else: # noQuality!
            if whichNGram in self._compoundNoQualityNGramsDict[n]:
               return self._compoundNoQualityNGramsDict[n][whichNGram]
            else:
               return 0
      except IndexError as indE:
         return 0
   # end getNGramOccurrences()
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
def intervalSorter( x, y ):
   '''
   Returns -1 if the first argument is a smaller interval.
   Returns 1 if the second argument is a smaller interval.
   Returns 0 if both arguments are the same.

   Input should be a str of the following form:
   - d, m, M, or A
   - an int

   Examples:
   >>> from vis import intervalSorter
   >>> intervalSorter( 'm3', 'm3' )
   0
   >>> intervalSorter( 'm3', 'M3' )
   1
   >>> intervalSorter( 'A4', 'd4' )
   -1
   '''
   if x == y:
      return 0
   elif int(x[1:]) < int(y[1:]): # if x is generically smaller
      return -1
   elif int(x[1:]) > int(y[1:]): # if y is generically smaller
      return 1
   else: # otherwise, we're down to the species/quality
      xQual = x[0]
      yQual = y[0]
      if xQual == 'd':
         return -1
      elif yQual == 'd':
         return 1
      elif xQual == 'A':
         return 1
      elif yQual == 'A':
         return -1
      elif xQual == 'm':
         return -1
      elif yQual == 'm':
         return 1
      else:
         return 0
#-------------------------------------------------------------------------------