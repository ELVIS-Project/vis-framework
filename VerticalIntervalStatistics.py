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
      
      errorstr = "VerticalIntervalStatistics.getIntervalOccurrences(): " + \
            "'simpleOrCompound' must be set to either 'simple' or 'compound'"
      
      # they're ignoring quality
      if whichInterval.isdigit():
         if 'simple' == simpleOrCompound:
            return findNumberOfAllQualities( whichInterval, self._simpleIntervalDict )
         elif 'compound' == simpleOrCompound:
            return findNumberOfAllQualities( whichInterval, self._compoundIntervalDict )
         else:
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
      zzz = theNGram.get_string_version( True, 'compound' )
      if zzz in self._compoundQualityNGramsDict[theNGram._n]:
         self._compoundQualityNGramsDict[theNGram._n][zzz] += 1
      else:
         self._compoundQualityNGramsDict[theNGram._n][zzz] = 1
      # self._compoundNoQualityNGramsDict
      zzz = theNGram.get_string_version( False, 'compound' )
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
   
   def getFormattedIntervals( self, theSettings ):
      '''
      Formats the intervals nicely.
      '''
      # TODO: heed heedQuality
      # TODO: heed compound/simple
      post = 'All the Intervals:\n------------------\n'
      sortedIntervals = sorted( self._compoundIntervalDict, cmp=intervalSorter )
      for interv in sortedIntervals:
         post += interv + ': ' + str(self._compoundIntervalDict[interv]) + '\n'
      post += '\n'
      
      return post
   # end getFormattedIntervals()
   
   def getFormattedNGrams( self, theSettings, n=None ):
      '''
      Formats the n-grams nicely. If you specify 'n' as a second argument, only
      those values of n-grams will be outputted. If you do not specify 'n', all
      available values of n-grams will be outputted.
      '''
      # TODO: heed heedQuality
      # TODO: heed compound/simple
      # TODO: heed parameter n
      post = 'All the N-Grams:\n----------------\n'
      sortedNGrams = sorted( self._compoundNoQualityNGramsDict[2], cmp=ngramSorter )
      for gram in sortedNGrams:
         post += gram + ': ' + str(self._compoundNoQualityNGramsDict[2][gram]) + '\n'
      post += '\n'
      
      return post
   # end getFormatted NGrams()
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
   
   listOfDirections = ['+', '-']
   listOfQualities = ['d', 'm', 'P', 'M', 'A']
   
   # What if we have directional intervals?
   if x[0] in listOfDirections:
      x = x[1:]
   if y[0] in listOfDirections:
      y = y[1:]
   
   # What if we have numbers with no qualities? Add a 'P' to make it work.
   if not x[0] in listOfQualities and \
      not y[0] in listOfQualities:
      x = 'P' + x
      y = 'P' + y
   
   # Comparisons!
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



#-------------------------------------------------------------------------------
def ngramSorter( x, y ):
   '''
   Returns -1 if the first argument is a smaller n-gram.
   Returns 1 if the second argument is a smaller n-gram.
   Returns 0 if both arguments are the same.
   
   If one n-gram is a subset of the other, starting at index 0, we consider the
   shorter n-gram to be the "smaller."
   
   Input should be like this, at minimum with three non-white-space characters
   separated by at most one space character.
   3 +4 7
   m3 +P4 m7
   -3 +4 1
   m-3 +P4 P1
   
   Examples:
   >>> from vis import ngramSorter
   >>> ngramSorter( '3 +4 7', '5 +2 4' )
   -1
   >>> ngramSorter( '3 +5 6', '3 +4 6' )
   1
   >>> ngramSorter( 'M3 1 m2', 'M3 1 M2' )
   -1
   >>> ngramSorter( '9 -2 -3', '9 -2 -3' )
   0
   >>> ngramSorter( '3 -2 3 -2 3', '6 +2 6' )
   -1
   >>> ngramSorter( '3 -2 3 -2 3', '3 -2 3' )
   1
   '''
   
   # Just in case there are some extra spaces
   x = x.strip()
   y = y.strip()
   
   def calcUnitsInNGram( ng ):
      # Calculate the 'units' in the n-gram, which is the number of elements
      # separated by a space, which is sort of like finding 'n'.
      units = 0
      while len(ng) > 0 and ng.find(' ') != -1:
         ng = ng[ng.find(' ')+1:]
         units += 1
      else:
         units += 1
      return units
   #-------------------------------------------------------
   
   # See if we have only one interval left. When there is only one interval,
   # the result of this will be -1
   xFind = x.find(' ')
   yFind = y.find(' ')
   if -1 == xFind:
      if -1 == yFind:
         # Both x and y have only one interval left, so the best we can do is
         # the output from intervalSorter()
         return intervalSorter( x, y )
      else:
         # x has one interval left, but y has more than one, so x is shorter.
         return -1
   elif -1 == yFind:
      # y has one interval left, but x has more than one, so y is shorter.
      return 1
   
   # See if the first interval will differentiate
   possibleResult = intervalSorter( x[:xFind], y[:yFind] )
   if 0 != possibleResult:
      return possibleResult
   
   # If not, we'll rely on ourselves to solve the next mystery!
   return ngramSorter( x[xFind+1:], y[yFind+1:] )
#-------------------------------------------------------------------------------
