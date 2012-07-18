#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Vertical_Interval_Statistics.py
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
# python
import re
from string import digits as string_digits
# music21
from music21 import interval
# vis
from problems import NonsensicalInputError, MissingInformationError



#-------------------------------------------------------------------------------
class Vertical_Interval_Statistics( object ):
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
   # _simple_interval_dict
   # _compound_interval_dict
   # _compound_quality_ngrams_dict
   # _compound_no_quality_ngrams_dict
   def __init__( self ):
      '''
      Create a new, "empty" statistics database for a piece.
      '''
      self._simple_interval_dict = {}
      self._compound_interval_dict = {}
      self._compound_quality_ngrams_dict = [{},{},{}]
      self._compound_no_quality_ngrams_dict = [{},{},{}]
   
   def __repr__( self ):
      return self.__str__( self )
   
   def __str__( self ):
      # This should produce something like...
      # "<Vertical_Interval_Statistics with 14 intervals; 26 2-grams; 19 3-grams>"
      post = '<Vertical_Interval_Statistics with ' + \
            str(len(self._compound_interval_dict)) + ' intervals; '
      for i in xrange(2,len(self._compound_quality_ngrams_dict)):
         post += str(len(self._compound_quality_ngrams_dict[i])) + ' ' + \
                 str(i) + '-grams; '
      
      return post[:-2] + '>'
   
   def add_interval( self, the_interval ):
      '''
      Adds a :class:`music21.interval.Interval` to the occurrences information.
      If given a simple interval, add that to both the table of simple and
      compound intervals. If given a compound interval, adds that to the table
      of compound intervals and the single-octave equivalent to the table of
      simple intervals.
      
      Automatically accounts for tracking quality or not.
      '''
      
      # NB: the "Automatically accounts for tracking quality or not" above
      # really means "it doesn't yet matter whether to track quality or not."
      
      # Descending interval
      if -1 == the_interval.direction:
         # For the dictionary of simple intervals
         simple_name = the_interval.semiSimpleName
         simple_name = simple_name[0] + '-' + simple_name[1:]
         if simple_name in self._simple_interval_dict:
            self._simple_interval_dict[simple_name] += 1
         else:
            self._simple_interval_dict[simple_name] = 1
         # For the dictionary of compound intervals
         compound_name = the_interval.name
         compound_name = compound_name[0] + '-' + compound_name[1:]
         if compound_name in self._compound_interval_dict:
            self._compound_interval_dict[compound_name] += 1
         else:
            self._compound_interval_dict[compound_name] = 1
      # Ascending or unison interval
      else:
         # For the dictionary of simple intervals
         simple_name = the_interval.semiSimpleName
         if simple_name in self._simple_interval_dict:
            self._simple_interval_dict[simple_name] += 1
         else:
            self._simple_interval_dict[simple_name] = 1
         # For the dictionary of compound intervals
         compound_name = the_interval.name
         if compound_name in self._compound_interval_dict:
            self._compound_interval_dict[compound_name] += 1
         else:
            self._compound_interval_dict[compound_name] = 1
   # end add_interval()

   def get_interval_occurrences( self, which_interval, simple_or_compound='simple' ):
      '''
      Returns the number of occurrences of a particular
      :class:`music21.interval.Interval`, either (by default) from the table
      with compound intervals, or if the second argument is 'simple' then from
      the table with simple intervals.
      
      Automatically accounts for tracking quality or not.
      '''
      
      # str of things to help sort out what the user wants
      qualities = 'dmMPA'
      directions = '-+'
      
      # Given a species (number), finds all the occurrences of any quality.
      # The second argument should be either self._simple_interval_dict or
      # self._compound_interval_dict
      def get_all_qualities( species, db ):
         post = 0
         for quality in qualities:
            if ( quality + species ) in db:
               post += db[quality+species]
         
         return post
      ##
      
      errorstr = 'Second argument must be either "simple" or "compound"'
      #errorstr = "Vertical_Interval_Statistics.get_interval_occurrences(): " + \
            #"'simple_or_compound' must be set to either 'simple' or 'compound'"
      
      # Are they ignoring quality? Yes, if the interval is just a digit or if
      # the first character is a direction
      if which_interval.isdigit() or which_interval[0] in directions:
         if 'simple' == simple_or_compound:
            return get_all_qualities( which_interval, self._simple_interval_dict )
         elif 'compound' == simple_or_compound:
            return get_all_qualities( which_interval, self._compound_interval_dict )
         else:
            raise NonsensicalInputError( errorstr )
      # Otherwise they are paying attention to quality.
      else:
         if 'simple' == simple_or_compound:
            if which_interval in self._simple_interval_dict:
               return self._simple_interval_dict[which_interval]
            else:
               return 0
         elif 'compound' == simple_or_compound:
            if which_interval in self._compound_interval_dict:
               return self._compound_interval_dict[which_interval]
            else:
               return 0
         else:
            raise NonsensicalInputError( errorstr )
   # end get_interval_occurrences()
   
   def add_ngram( self, the_ngram ):
      '''
      Adds an n-gram to the occurrences information. Automatically does or does
      not track quality, depending on the settings of the inputted NGram.
      '''
      
      # If there isn't yet a dictionary for this 'n' value, then we'll have to
      # make sure there is one.
      while len(self._compound_quality_ngrams_dict) <= the_ngram._n:
         self._compound_quality_ngrams_dict.append( {} )
         self._compound_no_quality_ngrams_dict.append( {} )
         
      # self._compound_quality_ngrams_dict
      zzz = the_ngram.get_string_version( True, 'compound' )
      if zzz in self._compound_quality_ngrams_dict[the_ngram._n]:
         self._compound_quality_ngrams_dict[the_ngram._n][zzz] += 1
      else:
         self._compound_quality_ngrams_dict[the_ngram._n][zzz] = 1
      # self._compound_no_quality_ngrams_dict
      zzz = the_ngram.get_string_version( False, 'compound' )
      if zzz in self._compound_no_quality_ngrams_dict[the_ngram._n]:
         self._compound_no_quality_ngrams_dict[the_ngram._n][zzz] += 1
      else:
         self._compound_no_quality_ngrams_dict[the_ngram._n][zzz] = 1
   # end add_ngram()
   
   def get_ngram_occurrences( self, which_ngram, n ):
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
         if which_ngram[0].isalpha(): # heedQuality
            if which_ngram in self._compound_quality_ngrams_dict[n]:
               return self._compound_quality_ngrams_dict[n][which_ngram]
            else:
               return 0
         else: # noQuality!
            if which_ngram in self._compound_no_quality_ngrams_dict[n]:
               return self._compound_no_quality_ngrams_dict[n][which_ngram]
            else:
               return 0
      except IndexError as indE:
         return 0
   # end get_ngram_occurrences()
   
   @staticmethod
   def _reduce_qualities( intervals_in ):
      ###
      # Given a dictionary of intervals with qualities, like 
      # V_I_S._compound_interval_dict, produces a list where the intervals
      # don't have qualities.
      # 
      # ['m3':5, 'M3':6, 'P4':1] ==> ['3':11, '4':1]
      ###
      qualities = 'dmMPA'
      post = {}
      # TODO: there must be a way to get only and all of the intervals that are
      # actually present
      for size in xrange(-30,30):
         for quality in qualities:
            look_for = quality + str(size)
            if look_for in intervals_in:
               if str(size) in post:
                  post[str(size)] += intervals_in[look_for]
               else:
                  post[str(size)] = intervals_in[look_for]
      return post
   
   def get_formatted_intervals( self, the_settings, specs = '' ):
      '''
      Returns a str with a nicely-formatted representation of the interval
      frequencies recoreded in this Vertical_Interval_Statistics() object.
      
      The first argument is a VIS_Settings() object, from which we will use
      the heedQuality and simpleOrCompound properties.
      
      The second argument is optional, and should be a str specifying how to
      sort the list of intervals. The str can contain any words in any order,
      because unrecognized words will be ignored.
      
      Useful list of things for the format str to contain:
      - 'by interval' if you want to sort the list by intervals
      - 'by frequency' if you want to sort the list by number of occurrences
      - 'ascending' or 'low to high' if you want the lowest or least common
         interval at the top of the list
      - 'descending' or 'high to low' if you want the highest or most common
         interval at the top of the list
      '''
      
      # (1) decide which dictionary to use and how to process the intervals.
      the_dict = None
      # Do we need to include quality?
      if True == the_settings.get_property( 'heedQuality' ):
         # Do we need compound or simple intervals?
         # We need compound intervals.
         if 'compound' == the_settings.get_property( 'simpleOrCompound' ):
            the_dict = self._compound_interval_dict
         # We need simple intervals.
         else:
            the_dict = self._simple_interval_dict
      # We don't need to include quality
      else:
         # Do we need compound or simple intervals?
         # We need compound intervals.
         if 'compound' == the_settings.get_property( 'simpleOrCompound' ):
            the_dict = Vertical_Interval_Statistics._reduce_qualities( self._compound_interval_dict )
         # We need simple intervals.
         else:
            the_dict = Vertical_Interval_Statistics._reduce_qualities( self._simple_interval_dict )
      
      # (2) sort the results in the specified way.
      if 'by frequency' in specs:
         # We'll have to swap value/key pairs
         flipped_dict = {}
         for key, val in the_dict.items():
            if val in flipped_dict:
               flipped_dict[val] += ', ' + key
            else:
               flipped_dict[val] = key
         
         # Sort the frequencies
         if 'descending' in specs or 'high to low' in specs:
            sorted_intervals = sorted( flipped_dict.iterkeys(), reverse=True )
         else: # elif 'ascending' in specs or 'low to high' in specs:
            # Default to 'ascending'
            sorted_intervals = sorted( flipped_dict.iterkeys() )
         
         # We're now working with flipped_dict in
         the_dict = flipped_dict
      else: # elif 'by interval' in specs:
         # Default to 'by interval'
         if 'descending' in specs or 'high to low' in specs:
            sorted_intervals = sorted( the_dict.iterkeys(), cmp=interval_sorter, reverse=True )
         else: # elif 'ascending' in specs or 'low to high' in specs:
            # Default to 'ascending'
            sorted_intervals = sorted( the_dict.iterkeys(), cmp=interval_sorter )
      
      # (3) make a nicely formatted list from the results.
      post = 'All the Intervals:\n------------------\n'
      if 'by frequency' in specs:
         for freq in sorted_intervals:
            post += str(freq) + ': ' + the_dict[freq] + '\n'
      else: # elif 'by interval' in specs:
         # Default to 'by interval'
         for interv in sorted_intervals:
            post += interv + ': ' + str(the_dict[interv]) + '\n'
      post += '\n'
      
      # Done!
      return post
   # end get_formatted_intervals()
   
   def get_formatted_ngrams( self, the_settings, specs='' ):
      '''
      Returns a str with a nicely-formatted representation of the n-gram
      frequencies recoreded in this Vertical_Interval_Statistics() object.
      
      The first argument is a VIS_Settings() object, from which we will use
      the heedQuality property. For now, all n-grams use compound intervals.
      
      The second argument is optional, and should be a str specifying how to
      sort the list of intervals and which value of 'n' to output. The str can
      contain any words in any order, because unrecognized words are ignored.
      
      Useful list of things for the format str to contain:
      - 'n=int,int' where "int" is an integer or a list of integers that are
         the values of 'n' to output. The 'n' values should be separated by a
         comma and end with a space or the end of the str. For example:
            'n=4,5 ascending'
            'n=3'
         If you do not specify 'n=' then the method outputs all values in this
         Vertical_Interval_Statistics instance. If you specify invalid values
         of 'n' they will be ignored. If you specify only invalid values of 'n'
         the method will raise a MissingInformationError().
      - 'by ngram' or 'by n-gram' if you want to sort the list by intervals
      - 'by frequency' if you want to sort the list by number of occurrences
      - 'ascending' or 'low to high' if you want the lowest or least common
         interval at the top of the list
      - 'descending' or 'high to low' if you want the highest or most common
         interval at the top of the list
      '''
      
      post = ''
      
      # (1) Figure out which values of 'n' we should output.
      list_of_n = []
      if 'n=' in specs:
         # Which values of 'n' did they specify?
         list_of_n = specs[specs.find('n=')+2:]
         list_of_n = list_of_n[:list_of_n.find(' ')]
         list_of_n = sorted(set([int(n) for n in re.findall('(\d+)', list_of_n)]))
         # Check those n values are acceptable/present
         for n in list_of_n:
            # First check we have that index and it's potentially filled with
            # n-gram values
            if n < 2 or n > (len(self._compound_no_quality_ngrams_dict) - 1):
               # throw it out
               list_of_n.remove( n )
               post += 'Not printing ' + str(n) + '-grams; there are none for that "n" value.\n'
               continue # to avoid the next test
            # Now check if there are actually n-grams in that position. If we
            # analyzed only for 5-grams, for instance, then 2, 3, and 4 will be
            # valid in the n-gram dictionary, but they won't actually hold
            # any n-grams.
            if {} == self._compound_no_quality_ngrams_dict[n]:
               # throw it out
               list_of_n.remove( n )
               post += 'Not printing ' + str(n) + '-grams; there are none for that "n" value.\n'
      else:
         # Which values of 'n' are present in this V_I_S instance?
         # Make a list starting at 2, extending to number of 'n' values in
         # this V_I_S instance.
         list_of_n = range( 2, len(self._compound_no_quality_ngrams_dict) )
         # Now check if there are actually n-grams in that position. If we
         # analyzed only for 5-grams, for instance, then 2, 3, and 4 will be
         # valid in the n-gram dictionary, but they won't actually hold
         # any n-grams.
         for n in list_of_n:
            if {} == self._compound_no_quality_ngrams_dict[n]:
               # throw it out
               list_of_n.remove( n )
      #-----
      
      # What if we end up with no n values?
      if 0 == len(list_of_n):
         raise MissingInformationError( "All of the 'n' values appear to have no n-grams" )
      
      # (2) Decide whether to take 'quality' or 'no_quality'
      output_dict = None
      if True == the_settings.get_property( 'heedQuality' ):
         # We do need to include quality
         output_dict = self._compound_quality_ngrams_dict
      else:
         # We don't need to include quality
         output_dict = self._compound_no_quality_ngrams_dict
      
      # (3) Sort the dictionary
      if 'by frequency' in specs:
         # Sort by frequency
         # We'll have to swap value/key pairs
         flipped_dicts = []
         # Make the right number of places for an 'n'
         for i in xrange(max(list_of_n) + 1):
            flipped_dicts.append( {} )
         
         # Do the flipping
         for n in list_of_n:
            for key, val in output_dict[n].items():
               if val in flipped_dicts[n]:
                  flipped_dicts[n][val] += ' and ' + key
               else:
                  flipped_dicts[n][val] = key
         
         # Sort the frequencies
         for n in list_of_n:
            if 'descending' in specs or 'high to low' in specs:
               sorted_ngrams = sorted( flipped_dicts[n].iterkeys(), reverse=True )
            else: # elif 'ascending' in specs or 'low to high' in specs:
               # Default to 'ascending'
               sorted_ngrams = sorted( flipped_dicts[n].iterkeys() )
            
         # We're now working with flipped_dicts
         output_dict = flipped_dicts
      else: # elif 'by ngram' in specs or 'by n-gram' in specs:
         # Default to 'by ngram'
         for n in list_of_n:
            if 'descending' in specs or 'high to low' in specs:
               sorted_ngrams = sorted( output_dict[n].iterkeys(), cmp=ngram_sorter, reverse=True )
            else: # elif 'ascending' in specs or 'low to high' in specs:
               # Default to 'ascending'
               sorted_ngrams = sorted( output_dict[n].iterkeys(), cmp=ngram_sorter )
      
      # (4) Make a nicely formatted list from the results.
      if 'by frequency' in specs:
         for n in list_of_n:
            post += 'All the ' + str(n) + '-grams:\n-----------------------------\n'
            for freq in sorted_ngrams:
               post += str(freq) + ': ' + output_dict[n][freq] + '\n'
            post += '\n'
      else: # elif 'by interval' in specs:
         # Default to 'by interval'
         for n in list_of_n:
            post += 'All the ' + str(n) + '-grams:\n-----------------------------\n'
            for ng in sorted_ngrams:
               post += ng + ': ' + str(output_dict[n][ng]) + '\n'
            post += '\n'
      
      # Done!
      return post
   # end getFormatted NGrams()
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
def interval_sorter( x, y ):
   '''
   Returns -1 if the first argument is a smaller interval.
   Returns 1 if the second argument is a smaller interval.
   Returns 0 if both arguments are the same.
   
   Input should be a str of the following form:
   - d, m, M, or A
   - an int
   
   Examples:
   >>> from vis import interval_sorter
   >>> interval_sorter( 'm3', 'm3' )
   0
   >>> interval_sorter( 'm3', 'M3' )
   1
   >>> interval_sorter( 'A4', 'd4' )
   -1
   '''
   
   list_of_directions = ['+', '-']
   
   # I want to sort based on generic size, so the direction is irrelevant. If
   # we have directions, they'll be removed with this. If we don't have
   # directions, this will have no effect.
   for direct in list_of_directions:
      x = x.replace( direct, '' )
      y = y.replace( direct, '' )
   
   # If we have numbers with no qualities, we'll just add a 'P' to both, to
   # pretend they have the same quality (which, as far as we know, they do).
   if x[0] in string_digits and y[0] in string_digits:
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
      x_qual = x[0]
      y_qual = y[0]
      if x_qual == 'd':
         return -1
      elif y_qual == 'd':
         return 1
      elif x_qual == 'A':
         return 1
      elif y_qual == 'A':
         return -1
      elif x_qual == 'm':
         return -1
      elif y_qual == 'm':
         return 1
      else:
         return 0
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
def ngram_sorter( x, y ):
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
   >>> from vis import ngram_sorter
   >>> ngram_sorter( '3 +4 7', '5 +2 4' )
   -1
   >>> ngram_sorter( '3 +5 6', '3 +4 6' )
   1
   >>> ngram_sorter( 'M3 1 m2', 'M3 1 M2' )
   -1
   >>> ngram_sorter( '9 -2 -3', '9 -2 -3' )
   0
   >>> ngram_sorter( '3 -2 3 -2 3', '6 +2 6' )
   -1
   >>> ngram_sorter( '3 -2 3 -2 3', '3 -2 3' )
   1
   '''
   
   # Just in case there are some extra spaces
   x = x.strip()
   y = y.strip()
   
   def calc_units_in_ngram( ng ):
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
   x_find = x.find(' ')
   y_find = y.find(' ')
   if -1 == x_find:
      if -1 == y_find:
         # Both x and y have only one interval left, so the best we can do is
         # the output from intervalSorter()
         return interval_sorter( x, y )
      else:
         # x has one interval left, but y has more than one, so x is shorter.
         return -1
   elif -1 == y_find:
      # y has one interval left, but x has more than one, so y is shorter.
      return 1
   
   # See if the first interval will differentiate
   possible_result = interval_sorter( x[:x_find], y[:y_find] )
   if 0 != possible_result:
      return possible_result
   
   # If not, we'll rely on ourselves to solve the next mystery!
   return ngram_sorter( x[x_find+1:], y[y_find+1:] )
#-------------------------------------------------------------------------------
