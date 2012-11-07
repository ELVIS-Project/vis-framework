#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         VerticalIntervalStatistics.py
# Purpose:      Stores statistics for "vis"
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
'''
This module implements the VerticalIntervalStatistics class, which collects,
stores, and reports statistics for analyses with NGram objects.
'''



# Import:
# python
import re, os.path, json
from string import digits as string_digits
from string import join
from collections import defaultdict
from itertools import chain
# music21
from music21 import interval, graph, stream, clef, meter, note
from music21.metadata import Metadata
# vis
from problems import NonsensicalInputError, MissingInformationError, \
   NonsensicalInputWarning
from analytic_engine import make_lily_triangle
from NGram import NGram

# NOTE: We don't need these for now, because the methods that use them are
# commented out, because they're currently not connected to the GUI
# numpy
#from numpy import array, linalg, ones, log, corrcoef
# matplotlib
#import matplotlib
import matplotlib.pyplot as plt



class VerticalIntervalStatistics( object ):
   '''
   Holds the statistics discovered by vis. Currently these are:

   - number of occurrences of each Interval
   - number of occurrences of each n-gram
   '''

   # Instance Data
   # TODO: write what these hold, and how they do it
   # _simple_interval_dict
   # _compound_interval_dict
   # _simple_ngrams_dict
   # _compound_ngrams_dict
   # _pieces_analyzed
   def __init__( self ):
      '''
      Create a new, "empty" statistics database for a piece.
      '''
      self._simple_interval_dict = defaultdict( lambda: defaultdict( int ))
      self._compound_interval_dict = defaultdict( lambda: defaultdict( int ))
      self._simple_ngrams_dict = defaultdict( lambda: defaultdict(
                                 lambda: defaultdict(
                                 lambda: defaultdict( int ))))
      self._compound_ngrams_dict = defaultdict( lambda: defaultdict(
                                   lambda: defaultdict(
                                   lambda: defaultdict( int ))))
      self._pieces_analyzed = []



   def __repr__( self ):
      '''
      Currently returns the string-format representation of this statistics
      instance.
      '''

      return str(self)



   def __str__( self ):
      '''
      This should produce something like:
      "<VerticalIntervalStatistics for 1 piece with 14 intervals; 26 2-grams>"
      '''
      # TODO: comment this method

      nbr_pieces = len(self._pieces_analyzed)
      pieces = " pieces"
      if 1 == nbr_pieces:
         pieces = " piece"
      post = '<VerticalIntervalStatistics for ' + str(nbr_pieces) + \
             pieces + ' with ' + str(len(self._compound_interval_dict)) + \
             ' intervals; '
      for n in self._compound_ngrams_dict.iterkeys():
         post += str(len(self._compound_ngrams_dict[n])) + ' ' + \
                 str(n) + '-grams; '

      return post[:-2] + '>'



   def _validate( self ):
      '''
      This is essentially a helper method for V_I_S.from_json,
      since from_json basically converts a dict directly into
      a V_I_S instance without checking the logic of doing so.
      This method makes sure the current V_I_S instance is
      internally consistent, by checking the existence, type
      and purpose of all the attributes of a standard V_I_S
      instance. It's possible this is not necessary and it
      would be better to have from_json call all the add_*()
      methods to guarantee a logical V_I_S instance.
      '''

      # TODO: write what to expect from this method, and write internal docs

      if not isinstance( self._pieces_analyzed, list ):
         raise NonsensicalInputError( '_pieces_analyzed must be of type list' )
      for voice_pair in self._pieces_analyzed:
         if not isinstance( voice_pair, str ):
            msg = '_pieces_analyzed must contain strings'
            raise NonsensicalInputError( msg )

      easy_atts = ['_simple_interval_dict', '_compound_interval_dict']
      ngram_dicts = ['_compound_ngrams_dict', '_simple_ngrams_dict']

      def validate_values( vals, att_name ):
         for value in vals:
            if not isinstance( value, list ):
               msg = att_name + ' values must be of type list'
               raise NonsensicalInputError( msg )
            if len(value) != 2:
               msg = att_name + ' value does not have 2 items'
               raise NonsensicalInputError( msg )
            if not isinstance( value[1], list ) or \
            not isinstance( value[0], int ):
               msg = att_name + ' values must be of the form [int, list]'
               raise NonsensicalInputError( msg )
            for each in value[1]:
               if not isinstance( each, int ):
                  msg = 'second part of ' + att_name + \
                        ' values must be list of ints'
                  raise NonsensicalInputError( msg )
            if value[0] != sum(value[1]):
               msg = 'first part of ' + att_name + \
                     ' values must equal sum of second part'
               raise NonsensicalInputError( msg )
            if len(value[1]) != len(self._pieces_analyzed):
               msg = 'second part of ' + att_name + \
                     ' must have as many elements as pieces analyzed'
               raise NonsensicalInputError( msg )

      for att_name in easy_atts:
         att = getattr( self, att_name )
         if not isinstance( att, dict ):
            raise NonsensicalInputError( att_name + ' must be of type dict' )
         for each_key in att.keys():
            try:
               interval.Interval( each_key )
            except: #music21 error if not a proper interval string
               raise NonsensicalInputError( each_key + \
                                            ' is not a valid interval' )
         validate_values( att.values(), att_name )

      for att_name in ngram_dicts:
         att = getattr( self, att_name )
         if not isinstance( att, dict ):
            msg = att_name + ' must be of type dict'
            raise NonsensicalInputError( msg )
         for dictio in att.values():
            if not isinstance( dictio, dict ):
               msg = att_name + ' values must be of type dict'
               raise NonsensicalInputError( msg )
            for key, val in dictio.items():
               if not isinstance( key, NGram ):
                  msg = att_name + ' value keys must be of type NGram'
                  raise NonsensicalInputError( msg )
               if not isinstance( val, dict ):
                  msg = att_name + ' value values must be of type dict'
                  raise NonsensicalInputError( msg )
               for smaller_key in val.keys():
                  if not isinstance( smaller_key, NGram ):
                     msg = att_name + ' value value keys must be of type NGram'
                     raise NonsensicalInputError( msg )
               validate_values( val.values(), att_name + ' value' )

      return True
   # End _validate() ---------------------------------------



   def add_analyzed_piece( self, piece_string ):
      '''
      Given a string in the format...
      "Piece_title [part_name, part_name]"
      ... add this to the list of analyses in this V_I_S instance.
      '''

      self._pieces_analyzed.append( piece_string )



   @staticmethod
   def _stringify( d ):
      '''
      Given a dict or list, convert its contents into something
      which gets accurately JSON-serialized -- basically just convert
      the keys of any dict which crosses your path into strings.
      '''
      # TODO: write internal documentation

      post = None

      if isinstance( d, dict ):
         post = {VerticalIntervalStatistics._stringify( k ): \
                 VerticalIntervalStatistics._stringify( v ) \
                 for k, v in d.items()}
      elif isinstance( d, list ):
         post = map( VerticalIntervalStatistics._stringify, d )
      elif isinstance( d, int ):
         post = d
      else:
         post = str(d)

      return post



   @staticmethod
   def dictify( d ):
      '''
      Converts a nested defaultdict into a regular dict.
      '''
      # TODO: write internal documentation

      post = None

      if isinstance( d, defaultdict ):
         post = {k: VerticalIntervalStatistics.dictify( v ) \
                 for k, v in d.items()}
      else:
         post = d

      return post



   def to_json( self ):
      '''
      Returns a string containing the JSON-serialization of this
      VerticalIntervalStatistics instance.
      '''
      # _stringify ensures that the dict is JSON-serializable,
      # since all keys in a JSONObject must be strings
      return json.JSONEncoder().encode( \
      VerticalIntervalStatistics._stringify( self.__dict__ ) )



   @classmethod
   def from_json( cls, json_string ):
      '''
      Given a string containing the JSON version of a V_I_S instance,
      convert it to a python object containing the V_I_S instance and
      then check it for internal consistency (see _validate()) and
      return the object.
      '''

      def fix_keys( ngd ):
         '''
         Convert the string-format n-gram representations into NGram objects.
         '''

         if isinstance( ngd, dict ):
            return {NGram.make_from_str( k ): fix_keys( v ) \
                    for k, v in ngd.items()}
         else:
            return ngd

      vis = VerticalIntervalStatistics()

      # use _stringify since JSONDecoder interprets all strings as unicode.
      d = None
      try:
         d = VerticalIntervalStatistics._stringify( \
            json.JSONDecoder().decode( json_string ) )
      except Exception as e:
         # TODO: this won't work. We need to catch specific exceptions
         msg = 'JSON data could not be parsed: ' + str(e)
         raise NonsensicalInputError( msg )

      # TODO: these are ___ and they're stored separately because ___
      easy_atts = ['_pieces_analyzed', '_simple_interval_dict', \
                   '_compound_interval_dict']
      ngram_dicts = ['_compound_ngrams_dict', '_simple_ngrams_dict']

      # TODO: this does...
      for att in easy_atts + ngram_dicts:
         if d.get( att ) is not None:
            # TODO: in here, we're doing...
            if att in easy_atts:
               # TODO: if something is something, we can do this because ____
               val = d[att]
            else:
               # TODO: if it's not, we have to do this because ____
               val = {k: fix_keys( ngd ) for k, ngd in d[att].items()}
            # TODO: does ...
            setattr( vis, att, val )
         else:
            # TODO: otherwise why do we need this error?
            msg = 'The dict supplied is missing the attribute ' + att
            raise MissingInformationError( msg )

      # TODO: this does
      if vis._validate():
         return vis
      # TODO: need an "else" clause, which should probably raise an exception
   # End from_json() ---------------------------------------



   def add_interval( self, the_interval, the_piece ):
      '''
      Adds a :class:`music21.interval.Interval` to the occurrences information
      for the piece of the given index.
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
         self._simple_interval_dict[simple_name][the_piece] += 1
         self._simple_interval_dict[simple_name]['Total'] += 1

         # For the dictionary of compound intervals
         compound_name = the_interval.name
         compound_name = compound_name[0] + '-' + compound_name[1:]
         self._compound_interval_dict[compound_name][the_piece] += 1
         self._compound_interval_dict[compound_name]['Total'] += 1
      # Ascending or unison interval
      else:
         # For the dictionary of simple intervals
         simple_name = the_interval.semiSimpleName
         self._simple_interval_dict[simple_name][the_piece] += 1
         self._simple_interval_dict[simple_name]['Total'] += 1
         # For the dictionary of compound intervals
         compound_name = the_interval.name
         self._compound_interval_dict[compound_name][the_piece] += 1
         self._compound_interval_dict[compound_name]['Total'] += 1
   # End add_interval() ------------------------------------



   def get_simple_interval_summary_dict( self ):
      '''
      Returns a copy of the simple interval occurrences data, where all of the
      pieces-specific data are summarized and removed.
      '''
      return {k: v['Total'] for k, v in self._simple_interval_dict.iteritems()}



   def get_compound_interval_summary_dict( self ):
      '''
      Returns a copy of the compound interval occurrences data, where all of the
      pieces-specific data are summarized and removed.
      '''
      return {k: v['Total'] for k, v in self._compound_interval_dict.iteritems()}



   def get_interval_occurrences( self, which_interval, \
                                 simple_or_compound = 'simple', piece = None ):
      # TODO: rewrite this method to use a VISSettings instance
      '''
      Returns the number of occurrences of a particular
      :class:`music21.interval.Interval` in a particular piece,
      either (by default) from the table
      with compound intervals, or if the second argument is 'simple' then from
      the table with simple intervals.

      Automatically accounts for tracking quality or not.
      '''

      # str of things to help sort out what the user wants
      qualities = 'dmMPA'
      directions = '-+'

      def get_all_qualities( species, db, piece ):
         '''
         Given a species (number), finds all the occurrences of any quality.
         The second argument should be either self._simple_interval_dict or
         self._compound_interval_dict
         '''
         post = 0
         for quality in qualities:
            if ( quality + species ) in db:
               if piece is None:
                  #then the total number of occurrences
                  post += db[ quality + species ]['Total']
               else:
                  post += db[ quality + species ][piece]

         return post

      errorstr = 'Second argument must be either "simple" or "compound"'

      # Are they ignoring quality? Yes, if the interval is just a digit or if
      # the first character is a direction
      if which_interval.isdigit() or which_interval[0] in directions:
         if 'simple' == simple_or_compound:
            return get_all_qualities( which_interval, \
                                      self._simple_interval_dict, \
                                      piece )
         elif 'compound' == simple_or_compound:
            return get_all_qualities( which_interval, \
                                      self._compound_interval_dict, \
                                      piece )
         else:
            raise NonsensicalInputError( errorstr )
      # Otherwise they are paying attention to quality.
      else:
         if 'simple' == simple_or_compound:
            if which_interval in self._simple_interval_dict:
               if piece is None:
                  return self._simple_interval_dict[which_interval]['Total']
               else:
                  return self._simple_interval_dict[which_interval][piece]
            else:
               return 0
         elif 'compound' == simple_or_compound:
            if which_interval in self._compound_interval_dict:
               if piece is None:
                  return self._compound_interval_dict[which_interval]['Total']
               else:
                  return self._compound_interval_dict[which_interval][piece]
            else:
               return 0
         else:
            raise NonsensicalInputError( errorstr )
   # End get_interval_occurrences() ------------------------



   def add_ngram( self, the_ngram, the_piece ):
      '''
      Adds an n-gram to the occurrences information.

      The first argument should be an NGram object, and the second should be
      the string-format name associated with this piece-and-voice-pair
      combination.
      '''

      # set up the keys for the various nested compound-ngram dicts
      compound_no_quality_version = \
            the_ngram.get_string_version( False, 'compound' )
      compound_quality_version = \
            the_ngram.get_string_version( True, 'compound' )

      # add the occurrence to the compound-ngram dict
      self._compound_ngrams_dict[the_ngram.n()][compound_no_quality_version] \
            [compound_quality_version][the_piece] += 1
      self._compound_ngrams_dict[the_ngram.n()][compound_no_quality_version] \
            [compound_quality_version]['Total'] += 1

      # set up the keys for the various nested simple-ngram dicts
      simple_no_quality_version = the_ngram.get_string_version( False, 'simple')
      simple_quality_version = the_ngram.get_string_version( True, 'simple' )

      # add the occurrence to the simple-ngram dict
      self._simple_ngrams_dict[the_ngram.n()][simple_no_quality_version] \
            [simple_quality_version][the_piece] += 1
      self._simple_ngrams_dict[the_ngram.n()][simple_no_quality_version] \
            [simple_quality_version]['Total'] += 1
   # End add_ngram() ---------------------------------------



   def get_ngram_dict( self, settings ):
      '''
      Given a VISSettings object, return a tuple with:
      - a dict including the n-gram specified statistics, and
      - a dict with a sorted list of keys for the required values of n

      In the VISSettings instance, set "leavePieces" to "False" to omit
      voice-pair-specific data, outputting only the totals for all voice pairs.

      Note that each n-gram object is appears in the statistics dictionary as
      a string, as per the settings provided.

      The second element of the returned tuple looks like this, for example:
      {2: ['6 -2 6', '5 4 1'], 3: ['4 1 5 1 6', '6 1 5 1 4']}
      '''

      # (1) Generate the dictionary
      # (1a) do we want simple or compound ngrams?
      simple = settings.get_property( 'simpleOrCompound' ) == 'simple'
      data_dict = self._simple_ngrams_dict if simple else \
                  self._compound_ngrams_dict
      # (1b) find the list of n
      list_of_n = settings.get_property( 'showTheseNs' )
      # (1c) Make sure that we have ngrams at the values requested. If not,
      # raise an exception saying which ones were not available.
      error_enns = []
      for enn in list_of_n:
         if data_dict[enn] == {}:
            error_enns.append( enn )
      if 0 < len(error_enns):
         msg = 'No ' + str(error_enns) + '-grams available!'
         raise NonsensicalInputWarning( msg )
      # store the results
      output_dict = None
      # (1d) do we want to include quality?
      if settings.get_property( 'heedQuality' ):
         # We do need to include quality, so replace the no_quality
         # level of the dict with all of its sub-dicts
         output_dict = {n: dict( chain( *[data_dict[n][ng].items()
                                        for ng in data_dict[n].keys()]))
                        for n in list_of_n}
      else:
         # We don't need to include quality, so just forget
         # about the values of the ngram dict and sum up all their data.
         output_dict = {n:
                          {ng:
                              {p: sum( d[v][p] for v in d.keys() )
                               for p in self._pieces_analyzed + ['Total'] }
                           for ng, d in data_dict[n].items()}
                        for n in list_of_n}

      # (2) Do the filtering for "top X"
      top_x = settings.get_property( 'topX' ) # the "X"
      if top_x is not None:
         for n in list_of_n:
            # sort the keys by frequency
            sorted_ngrams = sorted( output_dict[n].keys(), \
                                   key = lambda ng: output_dict[n][ng]['Total'],
                                   reverse = True )
            # accept only the top top_x
            sorted_ngrams = sorted_ngrams[:top_x]
            # filter the dict to only include the new keys
            output_dict[n] = {ng: output_dict[n][ng] for ng in sorted_ngrams}

      # (3) Do the filtering for "threshold" (n-grams with fewer than
      # "threshold" occurrences should not be included)
      thresh = settings.get_property( 'threshold' ) # the threshold
      if thresh is not None:
         for n in list_of_n:
            keys = filter( lambda ng: output_dict[n][ng]['Total'] >= thresh, \
                           output_dict[n].keys() )
            output_dict[n] = {ng: output_dict[n][ng] for ng in keys}

      # (4) Sort the keys according to the settings
      # will we have to reverse our sorts?
      rev = settings.get_property( 'sortOrder' ) == 'descending'
      # first we just sort by NGram...
      keys = {n: sorted( output_dict[n].keys(), cmp = ngram_sorter, \
                         reverse = rev ) for n in list_of_n}
      by_freq = settings.get_property( 'sortBy' ) == 'frequency'
      # should we sort by frequency?
      if by_freq:
         # if so, sort again
         keys = {n: sorted( keys[n], \
                            key = lambda ng: output_dict[n][ng]['Total'], \
                            reverse = rev ) for n in list_of_n}
      # should we forget the piece breakdown?
      if not settings.get_property( 'leavePieces' ):
         output_dict = {n: {ng: v['Total'] \
                        for ng, v in output_dict[n].items()} \
                        for n in list_of_n}
      return ( output_dict, keys )
   # End get_ngram_dict() ----------------------------------



   #def get_ngram_occurrences( self, which_ngram ):
      #'''
      #Returns the number of occurrences of a particular n-gram. Currently, all
      #n-grams are treated as though they have compound intervals.

      #The first argument must be an NGram object or the output from either
      #NGram.stringVersion or str(NGram) (which calls stringVersion()
      #internally).

      #Automatically does or does not track quality, depending on the settings
      #of the inputted NGram objects.
      #'''

      ## TODO: determine whether we need this method; if so, write comments
      #ng = None
      #if isinstance(which_ngram,NGram):
         #ng = which_ngram
      #if isinstance(which_ngram,basestring):
         #try:
            #ng = NGram.make_from_str(which_ngram)
         #except NonsensicalInputError as nie:
            #raise
      #else:
         #raise NonsensicalInputError("Input must be of type NGram or string")
      #ng_key = ng.get_string_version(True,'compound')
      #n = ng.n()
      #settings = VISSettings()
      #settings.set_property('simpleOrCompound', 'compound')
      #settings.set_property('heedQuality', 'true')
      #settings.set_property( 'showTheseNs', [n] )
      #the_dict = self.get_ngram_dict( settings )[0][n]
      #return 0 if the_dict.get(ng_key) is None else the_dict[ng_key]['Total']
   # End get_ngram_occurrences() ---------------------------



   def extend( self, other):
      '''
      Merge an other VerticalIntervalStatistics instance with this one.
      '''

      def merge_default_dicts( left, right ):
         '''
         Given two nested defaultdicts, return a new defaultdict with all the
         keys of both, and values that correspond to summing the dicts together.
         '''

         # Here's a set with all of the keys belonging in the new defaultdict
         new_keys = set( left.keys() + right.keys() )

         # TODO: what's this "int" test for?
         if left.default_factory == int:
            # Assemble the new defaultdict by adding the values in x to
            # the values in y.
            contents = ( (key, left[key] + right[key]) for key in new_keys )
            return defaultdict( int, contents )
         else:
            # TODO: Assemble the new defaultdict by ... how?
            contents = ( (key, merge_default_dicts( left[key], right[key] )) for \
                  key in new_keys )
            return defaultdict( left.default_factory, contents )

      # Deal with the record of voice pairs and pieces
      self._pieces_analyzed += other._pieces_analyzed

      # Deal with the intervals
      self._simple_interval_dict = \
            merge_default_dicts( self._simple_interval_dict, \
                                 other._simple_interval_dict)
      self._compound_interval_dict = \
            merge_default_dicts( self._compound_interval_dict, \
                                 other._compound_interval_dict)

      # Deal with the n-grams
      self._compound_ngrams_dict = \
            merge_default_dicts( self._compound_ngrams_dict, \
                                 other._compound_ngrams_dict )
      self._simple_ngrams_dict = \
            merge_default_dicts( self._simple_ngrams_dict, \
                                 other._simple_ngrams_dict )
   # End extend() ------------------------------------------



   # TODO: decide whether we need this method, then remove or improve
   #def retrogrades( self, the_settings, specs='' ):
      ## (1) Figure out which values of 'n' we should output.
      #post = ''
      #list_of_n = the_settings.get_property('showTheseNs')

      ## (2) Decide whether to take 'quality' or 'no_quality'
      #output_dict = self.prepare_ngram_output_dict( the_settings )

      ## (3) Sort the dictionary
      #sorted_ngrams = []
      ## We need to have enough 'n' places in sorted_ngrams to hold the
      ## sorted dictionaries.
      #for n in xrange(max(list_of_n) + 1):
         #sorted_ngrams.append( [] )
      #for n in list_of_n:
         #sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), \
                                    #key = lambda ng: output_dict[n][ng] )

      ## (4) Generate the results
      #ngram_pairs = []
      #for n in xrange(max(list_of_n) + 1):
         #ngram_pairs.append( {} )
      #for n in list_of_n:
         #for ng in sorted_ngrams[n]:
            #retrograde = ng.retrograde()
            ## this is an odd workaround; used to get KeyErrors, possibly
            ## because accessing the key wasn't using __hash__ correctly?
            ## Anyway, the problem seems to have to do with changing
            ## NGram.__repr__ to include the specific pitches in the NGram.
            #matches = [gram for gram in sorted_ngrams[n] if gram == retrograde]
            #if len(matches) > 0:
               #for ngram in matches:
                  #ngram_pairs[n][( ng, retrograde )] = ( output_dict[n][ng], \
                                                         #output_dict[n][ngram])
                  #sorted_ngrams[n].remove(retrograde)
            #else:
               #ngram_pairs[n][(ng,retrograde)] = (output_dict[n][ng],0)

      ## (5.1) If some graphs are asked for, prepare them
      #if 'graph' in specs:
         #grapharr = []
         #for n in list_of_n:
            #keys = sorted( ngram_pairs[n].keys(), key = lambda ng: \
                           #float( ngram_pairs[n][ng][1] ) / \
                           #float( ngram_pairs[n][ng][0] ), \
                           #reverse=True )
            #g = graph.GraphGroupedVerticalBar(doneAction=None)
            #data = []
            #for key in keys:
               #entry = (str(key[0])+' '+str(key[1]),)
               #pair = {}
               #pair['n-gram'] = ngram_pairs[n][key][0]
               #pair['retrograde'] = ngram_pairs[n][key][1]
               #entry += (pair,)
               #data.append(entry)
            #g.setData(data)
            #g.setTitle(str(n)+'-Grams')
            ## this is a very slight edit of the
            ## music21.graph.GraphGroupedVerticalBar.process() and
            ## labelBars() methods
            #fig = plt.figure()
            #setattr(g,'fig', fig)
            #fig.subplots_adjust(bottom=.3)
            #ax = fig.add_subplot(1, 1, 1)

            ## b value is a list of values for each bar
            #for a, b in getattr(g,'data'):
               #barsPerGroup = len(b)
               ## get for legend
               #subLabels = sorted(b.keys())
               #break
            #widthShift = 1 / float(barsPerGroup)

            #xVals = []
            #yBundles = []
            #for i, (a, b) in enumerate(getattr(g,'data')):
               ## create x vals from index values
               #xVals.append(i)
               #yBundles.append([b[key] for key in sorted(b.keys())])

            #rects = []
            #for i in range(barsPerGroup):
               #yVals = []
               #for j, x in enumerate(xVals):
                  ## get position, then get bar group
                  #yVals.append(yBundles[j][i])
               #xValsShifted = []
               #for x in xVals:
                  #xValsShifted.append(x + (widthShift * i))
               #colors = getattr(g,'colors')

               #rect = ax.bar(xValsShifted, yVals, width=widthShift, alpha=.8,
                   #color=graph.getColor(colors[i % len(colors)]))
               #rects.append(rect)

            #colors = []
            #for k in range(len(rects)):
               #for j in range(len(rects[k])):
                  #height = rects[k][j].get_height()
                  #ax.text(rects[k][j].get_x()+rects[k][j].get_width()/2., \
                          #height+.05, \
                          #'%s'%(str(keys[j][k])), rotation='vertical', \
                          #ha='center', va='bottom',
                          #fontsize=getattr(g,'tickFontSize'), \
                          #family=getattr(g,'fontFamily'))
               #colors.append(rects[k][0])

            #font = matplotlib.font_manager.FontProperties(size=getattr(g,\
                        #'tickFontSize'),
                        #family=getattr(g,'fontFamily'))
            #ax.legend(colors, subLabels, prop=font)

            #g._adjustAxisSpines(ax)
            #g._applyFormatting(ax)
            #g.done()
            #grapharr.append(g)
         #post = grapharr
      ## (5.2) Else prepare a nicely formatted list of the results
      #else:
         #for n in list_of_n:
            #post += 'All the ' + str(n) + \
            #'-grams with retrogrades:\n-----------------------------\n'
            #for ng in ngram_pairs[n].keys():
               #post += str(ng[0]) + ': ' + str(ngram_pairs[n][ng][0]) +'; ' \
                       #+str(ng[1])+': '+str(ngram_pairs[n][ng][1]) + '\n'
      #return post
   # End retrogrades() -------------------------------------



   # TODO: decide whether we need this method, then remove or improve
   #def power_law_analysis( self, the_settings ):
      #list_of_n = the_settings.get_property('showTheseNs')

      ## (2) Decide whether to take 'quality' or 'no_quality'
      #output_dict = self.prepare_ngram_output_dict( the_settings )

      ## (3) Sort the dictionary
      #sorted_ngrams = []
      ## We need to have enough 'n' places in sorted_ngrams to hold the
      ## sorted dictionaries.
      #for n in xrange(max(list_of_n) + 1):
         #sorted_ngrams.append( [] )
      #post = ''
      #for n in list_of_n:
         #sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), \
                                     #key = lambda ng: output_dict[n][ng], \
                                     #reverse=True )
         ## we do a power-law regression by instead looking at
         ## the logarithmic scales and doing linear regression
         #xi = [log(i) for i in range(1,len(sorted_ngrams[n])+1)]
         #A = array([ xi, ones(len(xi))])
         #y = [log(output_dict[n][ng]) for ng in sorted_ngrams[n]]
         #w = linalg.lstsq(A.T,y)[0] #least-squares regression on the data
         ## w[0] contains the slope of the line, and we'll just display
         ## positive numbers because that's nice.
         #post += 'The power law exponent for the ' + str(n) + '-grams is ' + \
                  #str( -w[0] ) + '; correlation coefficient ' + \
                  #str( -corrcoef( xi, y )[0,1] )
      #return post
   # End power_law_analysis() ------------------------------



   def get_formatted_intervals( self, the_settings ):
      '''
      Returns a str with a nicely-formatted representation of the interval
      frequencies recoreded in this VerticalIntervalStatistics() object.

      The first argument is a VISSettings() object, from which we will use
      all of the formatting properties.
      '''
      # TODO: there are too many single-letter variable names here

      # (1) decide which dictionary to use and how to process the intervals.
      the_dict = None

      # Does 'specs' specify whether they want compound or simple intervals?
      s_or_c = the_settings.get_property( 'simpleOrCompound' )

      # Do we need compound or simple intervals?
      if 'compound' == s_or_c:
         the_dict = self._compound_interval_dict
      else:
         the_dict = self._simple_interval_dict

      # Do we need to remove quality?
      if not the_settings.get_property( 'heedQuality' ):
         # yes we do; this is done by removing any 'letters'
         # from the interval's text representation -- voila,
         # the quality-free version!
         non_numeric = re.compile( r'[^\d-]+' )
         # replace anything that isn't a number with the empty string
         red = lambda k: non_numeric.sub( '', k )
         # apply that sweet function to all of the intervals
         keys = set( red(k) for k in the_dict.keys() )
         # For each new key, replace it with a tuple containing:
         # ( key, [set of old keys which have this common quality-free form] )
         keys = [( k, filter( lambda t: red( t[0] ) == k, the_dict.items() ) )\
                 for k in keys]
         # now we make a dict with the new keys and values being the sum
         #over all the values associated to the old keys
         piece_list = self._pieces_analyzed + ['Total']
         the_dict = {k: {p: sum( v[p] for K, v in l) for p in piece_list} \
                     for k, l in keys}

      # (2) Sort the results in the specified way.
      if 'frequency' == the_settings.get_property( 'sortBy' ):
         # Sort by frequency
         if 'ascending' == the_settings.get_property( 'sortOrder' ):
            sorted_intervals = sorted( the_dict.iterkeys(), \
                                       key = lambda x: the_dict[x]['Total'] )
         else:
            # Default to 'descending'
            sorted_intervals = sorted( the_dict.iterkeys(), \
                                       key = lambda x: the_dict[x]['Total'], \
                                       reverse = True )
      else:
         # Default to 'by interval'
         if 'descending' == the_settings.get_property( 'sortOrder' ):
            sorted_intervals = sorted( the_dict.iterkeys(), \
                                       cmp = interval_sorter, \
                                       reverse = True )
         else: # elif 'ascending' in specs or 'low to high' in specs:
            # Default to 'ascending'
            sorted_intervals = sorted( the_dict.iterkeys(), \
                                       cmp = interval_sorter )

      # (3A) Make a graph, if requested.
      if 'graph' == the_settings.get_property( 'outputFormat' ):
         g = graph.GraphHistogram( doneAction = None )
         data = [(i, the_dict[interv]['Total'])\
                 for i, interv in enumerate(sorted_intervals)]
         g.setData(data)
         g.setTitle( 'Intervals in ' + join( [str(os.path.split(p)[1] ) + ', ' \
                     for p in self._pieces_analyzed] )[:-2] )
         g.setTicks( 'x', [( i + 0.4, interv ) for i, interv in \
                           enumerate(sorted_intervals)])
         g.xTickLabelHorizontalAlignment = 'center'
         setattr( g, 'xTickLabelRotation', 45 )
         g.setAxisLabel( 'x', 'Interval' )
         max_height = max([the_dict[interv]['Total'] \
                           for interv in sorted_intervals]) + 1
         tick_dist = max( max_height / 10, 1 )
         ticks = []
         k = 0
         while k*tick_dist <= max_height:
            k += 1
            ticks.append( k * tick_dist )
         g.setTicks( 'y', [( k, k ) for k in ticks] )
         g.fig = plt.figure()
         g.fig.subplots_adjust( left = 0.15 )
         ax = g.fig.add_subplot( 1, 1, 1 )

         x = []
         y = []
         for a, b in g.data:
            x.append( a )
            y.append( b )
         ax.bar( x, y, alpha=.8, color = graph.getColor( g.colors[0] ) )

         # TODO: not access these class members
         g._adjustAxisSpines( ax )
         g._applyFormatting( ax )
         ax.set_ylabel( 'Frequency', fontsize = g.labelFontSize, \
                        family = g.fontFamily, rotation = 'vertical' )
         g.done()
         return g

      # (3B) Default to formatted list.
      post = ''
      widths = []
      heading = 'Interval'

      # Calculate the width of the first column, which contains the
      # interval names
      width = max( [len(str(k)) for k in sorted_intervals] + \
                   [len(heading) + 2] )
      widths.append( width )

      for i, piece in enumerate(self._pieces_analyzed):
         width = max( [len( str( the_dict[k][piece] )) \
                       for k in sorted_intervals] + \
                      [len( os.path.split( piece )[1] ) + 3] )
         widths.append(width)
      width_total = max( [len( str( the_dict[k]['Total'] )) \
                          for k in sorted_intervals] + \
                         [len( 'Total ' )] ) + 2
      widths.append( width_total )
      row = '{0:{1:n}}'.format( heading, widths[0] )

      # Add the header
      row += '{0:{1:n}}'.format( '# Total ', widths[-1] )
      # Add the "#pN" index
      for i, piece in enumerate(self._pieces_analyzed):
         row += '{0:{1:n}}'.format( '# ' + os.path.split(piece)[1] + ' ', \
                                    widths[i + 1] )
      row += "\n"
      post += row
      row = '=' * sum(widths) + '\n'
      post += row

      # Add each interval
      for interv in sorted_intervals:
         # print the n-gram name
         row = '{0:{1:n}}'.format( str(interv), widths[0] )
         # the total for all pieces and voice pairs
         row += '{0:{1:n}}'.format( str(the_dict[interv]['Total']), \
                                    widths[-1] )
         # the totals by voice pair
         for i, piece in enumerate( self._pieces_analyzed, start = 1 ):
            row += '{0:{1:n}}'.format( str(the_dict[interv][piece]), \
                                       widths[i] )
         # end the row
         row += '\n'
         post += row

      post += '\n'

      return post
   # end get_formatted_intervals() -------------------------



   # TODO: evaluate whether we need this method--currently unused--and revise
   # accordingly.
   #def similarity( self, some_pieces, other_pieces, n, \
                   #simple_or_compound='compound', heedQuality=False ):
      #'''
      #Given two lists of indices of self._pieces_analyzed,
      #an integer n, and the other obvious settings, computes
      #the similarity between the N-Grams in the two samples.
      #'''
      ## TODO: write internal documentation
      ## TODO: rewrite this to use a VISSettings instance, rather than take
      ## arguments

      #settings = VISSettings()
      #settings.set_property( 'heedQuality', heedQuality )
      #settings.set_property( 'simpleOrCompound', simple_or_compound )
      #settings.set_property( 'showTheseNs', [n] )

      #the_dict = self.prepare_ngram_output_dict( settings )[n]
      #total_some = sum(sum(v[1][i] for i in some_pieces) \
                   #for v in the_dict.values())
      #total_other = sum(sum(v[1][i] for i in other_pieces) \
                   #for v in the_dict.values())
      #total_diff = sum(abs(( sum( v[1][i] for i in some_pieces ) * 100 ) \
                   #/ total_some -( sum( v[1][i] for i in other_pieces ) * 100) \
                   #/ total_other) for v in the_dict.values())
      #return 1.0 - float(total_diff) / 200



   def get_formatted_ngrams( self, the_settings ):
      '''
      Returns a str or music21.graph.Graph object with a nicely-formatted
      representation of the n-gram frequencies recoreded in this
      VerticalIntervalStatistics() object.

      The argument is a VISSettings() object, from which we get
      formatting options.
      '''

      # Which output format to they want?
      output_format = the_settings.get_property( 'outputFormat' )

      # Currently, this method only supports the text and Graph outputs
      if 'graph' == output_format:
         return self.get_ngram_graph(the_settings)
      elif 'list' == output_format:
         return self.get_ngram_text(the_settings)
      else:
         msg = 'get_formatted_ngrams() can only currently prepare ' + \
               'list or Graph output'
         raise NonsensicalInputWarning( msg )



   def get_ngram_graph( self, settings ):
      '''
      Given a VISSettings object, prepare a music21 "Graph" object of n-grams
      with corresponding results.
      '''

      # Get the statistics to show, and a sorted list of keys
      output_dict, keys = self.get_ngram_dict(settings)

      # Hold a list of the chart objects for every requested value of 'n'
      grapharr = []

      # Iterate through the requested values of 'n'
      for n in output_dict.keys():
         # This is what we'll return
         chart = graph.GraphHistogram( doneAction = None, tickFontSize = 12 )

         # Get the data corresponding to this 'n' value
         data = [(k, output_dict[n][key]['Total']) \
                  for k, key in enumerate(keys[n])]

         # Set the chart's data
         chart.setData( data )

         # What does this do, and why does it seem to be done differently, and
         # at a different time than "chart.setTick( 'y', ... )" ?
         chart.setTicks( 'x', [( k + 0.7, key ) \
                               for k, key in enumerate( keys[n] )])

         # Set the label for the x axis
         chart.setAxisLabel( 'x', str(n) + '-gram' )

         # Adjust the rotation and alignment of the x-axis labels
         chart.xTickLabelRotation = 45
         chart.xTickLabelVerticalAlignment = 'top'
         chart.xTickLabelHorizontalAlignment = 'right'

         # Set the chart's title
         chart.setTitle( str(n) + '-grams in ' + \
                         join( [str( os.path.split(p)[1] ) + ', ' \
                               for p in self._pieces_analyzed] )[:-2] )

         # TODO: ?
         max_height = max( [output_dict[n][key]['Total'] \
                            for key in keys[n]] ) + 1

         # TODO: ?
         tick_dist = max( max_height / 10, 1 )

         # TODO: what are ticks?
         ticks = []

         # TODO: what is k?
         k = 0

         # TODO: what does this do?
         while k * tick_dist <= max_height:
            k += 1
            ticks.append( k * tick_dist )

         # TODO: what do these four lines do?
         chart.setTicks( 'y', [(k, k) for k in ticks] )
         chart.fig = plt.figure()
         chart.fig.subplots_adjust( left = 0.15, bottom = 0.2 )
         ax = chart.fig.add_subplot( 1, 1, 1 )

         # TODO: what are these, and can we give them better names?
         x = []
         y = []

         # TODO: ?
         for a, b in chart.data:
            x.append( a )
            y.append( b )

         # TODO: ?
         ax.bar( x, y, alpha = 0.8, color = graph.getColor( chart.colors[0] ) )

         # TODO: what are these?
         chart._adjustAxisSpines( ax )
         chart._applyFormatting( ax )

         # Set the y-axis label
         ax.set_ylabel( 'Frequency', fontsize=chart.labelFontSize, \
                        family=chart.fontFamily, rotation='vertical')

         # TODO: signal that we're done preparing the chart?
         chart.done()

         # Appen this chart to the list of charts we'll return
         grapharr.append( chart )

      return grapharr
   # End get_ngram_graph() ---------------------------------



   def get_ngram_text( self, settings ):
      '''
      Given a VISSettings object, prepare text-based output in a string, with
      corresponding n-grams.
      '''

      # TODO: comment this method as extensively as get_ngram_graph()
      output_dict, keys = self.get_ngram_dict( settings )

      # Start with a title
      post = 'N-Grams\n\n'

      # Piece Title and Part Combination Assignments
      for k, piece in enumerate( self._pieces_analyzed, start=1 ):
         post += 'p' + str(k) + ' = ' + os.path.split(piece)[1] + '\n'

      post += '\n'

      # Print all requested values of n
      for n, the_dict in output_dict.items():
         total_n = sum( v['Total'] for v in the_dict.values() )
         post += "Total number of " + str(n) + "-grams: " + str(total_n) + \
                  "\n\n"
         sorted_ngrams = keys[n]
         widths = []
         heading = str(n) + "-gram"
         width = max( [ len(str(k)) for k in sorted_ngrams ] + \
                      [ len(heading) ] ) + 2
         widths.append( width )

         # Go through each piece (for this value of n)
         for i, piece in enumerate( self._pieces_analyzed ):
            width = max( [ len( str( the_dict[k][piece] ) ) \
                    for k in sorted_ngrams] + \
                    [ len( 'p' + str( i + 1 ) ) + 3 ] )
            widths.append( width )

         width_total = max([len(str(the_dict[k]['Total'])) \
                           for k in sorted_ngrams] + [len("Total ")]) + 2
         widths.append( width_total )
         row = '{0:{1:n}}'.format( heading, \
                                   widths[0] )

         row += '{0:{1:n}}'.format( '# Total ', \
                                    widths[-1] )

         for i, piece in enumerate( self._pieces_analyzed, start = 1 ):
            row += '{0:{1:n}}'.format( '# p' + str(i) + ' ', \
                                       widths[i] )

         row += '\n'
         post += row
         row = '=' * sum(widths) + '\n'
         post += row

         for ngram in sorted_ngrams:
            # add the n-gram name
            row = '{0:{1:n}}'.format( str(ngram), \
                                      widths[0] )
            # add the total
            row += '{0:{1:n}}'.format( str(the_dict[ngram]['Total']), \
                                       widths[-1] )
            # add the per-piece totals
            for i, piece in enumerate(self._pieces_analyzed, start = 1):
               row += '{0:{1:n}}'.format( str(the_dict[ngram][piece]), \
                                          widths[i] )
            row += '\n'
            post += row

         post += '\n\n'

      # Remove the final newline, which we don't really need
      post = post[:-3]
      return post
   # End get_ngram_text() ----------------------------------



   # TODO: uncomment this method and revise it as required... I commented it out
   # for AMS/SMT/SEM 2012 because it's not fully connected to the GUI.
   #def compare( self, the_settings, other_stats, file1, file2, specs='' ):
      #'''
      #Compares the relative frequencies of n-grams in two different files,
      #displaying a text chart or graph, as well as computing the "total metric"
      #difference between the two.
      #'''
      # TODO: comment this method as extensively as get_ngram_graph()
      # TODO: remove duplication with get_ngram_text() and get_ngram_graph()

      # (1) Figure out which 'n' values to display
      #post = ''
      #list_of_n = []
      #if 'n=' in specs:
         #list_of_n = specs[specs.find('n=') + 2:]
         #list_of_n = list_of_n[:list_of_n.find(' ')]
         #list_of_n = sorted(set([int(n) \
                     #for n in re.findall( '(\d+)', list_of_n )]))
         ## Check those n values are acceptable/present
         #for n in list_of_n:
            ## First check we have that index and it's potentially filled with
            ## n-gram values
            #if n < 2 or (n > (len(self._compound_ngrams_dict) - 1) and \
               #n > (len(other_stats._compound_ngrams_dict) - 1)):
               ## throw it out
               #list_of_n.remove( n )
               #post += 'Not printing ' + str(n) + \
                       #'-grams; there are none for that "n" value.\n'
               #continue # to avoid the next test
            ## Now check if there are actually n-grams in that position. If we
            ## analyzed only for 5-grams, for instance, then 2, 3, and 4 will be
            ## valid in the n-gram dictionary, but they won't actually hold
            ## any n-grams.
            #if {} == self._compound_ngrams_dict[n] and \
               #{} == other_stats._compound_ngrams_dict[n]:
               ## throw it out
               #list_of_n.remove( n )
               #post += 'Not printing ' + str(n) + \
                       #'-grams; there are none for that "n" value.\n'
      #elif self._compound_ngrams_dict[i] != {} or \
      #other_stats._compound_ngrams_dict[i] != {}:
         #list_of_n = [i for i in \
                      #xrange(max( len(self._compound_ngrams_dict), \
                      #len(other_stats._compound_ngrams_dict) )) ]

      ## What if we end up with no n values?
      #if 0 == len(list_of_n):
         #msg = "All of the 'n' values appear to have no n-grams"
         #raise MissingInformationError( msg )

      ## (2) Organize the results
      #tables = {}
      #for n in list_of_n:
         #table = {}
         #sett = copy.deepcopy( the_settings )
         #sett.set_property( 'heedQuality', False )
         #sett.set_property( 'showTheseNs', list_of_n )
         #self_dict = self.prepare_ngram_output_dict( sett )[n]
         #other_dict = other_stats.prepare_ngram_output_dict( sett )[n]
         #for ng in self_dict.iterkeys():
            #table[ng] = [self_dict[ng],0]
         #for ng in other_dict.iterkeys():
            #if ng in self_dict:
               #table[ng][1] = other_dict[ng]
            #else:
               #table[ng] = [0, other_dict[ng]]
         #tables[n] = table
      ## (3.1) If some graphs are asked for, prepare them
      #if 'graph' in specs:
         #grapharr = []
         #for n in list_of_n:
            #table = tables[n]
            #keys = table.keys()
            #g = graph.GraphGroupedVerticalBar( doneAction=None )
            #data = []
            #for k, key in enumerate(keys):
               #pair = {}
               #pair[file1] = table[key][0]
               #pair[file2] = table[key][1]
               #entry = ( 'bar%s' % str(k), pair )
               #data.append( entry )
            #g.setData( data )
            #g.setTicks( 'x', [(k + 0.4, key) for k, key in enumerate(keys)])
            #g.xTickLabelRotation = 90
            #g.xTickLabelVerticalAlignment = 'top'
            #g.setTitle( str(n) + '-grams' )
            #g.setTicks( 'y', [(k,k) \
                            #for k in xrange(max([max( int(v[0]), int(v[1]) )\
                            #for v in table.values()]))])
            #g.process()
            #grapharr.append( g )
         #post = grapharr

      ## (3.2) Otherwise make a nicely formatted list of the results
      #else:
         #s_or_c = the_settings.get_property( 'simpleOrCompound' )
         #heed_quality = the_settings.get_property( 'heedQuality' )
         #for n in list_of_n:
            #table = tables[n]
            #width1 = max( [len(ng.get_string_version( heed_quality, s_or_c )) \
                          #for ng in table.keys()] )
            #total1 = sum( [t[0] for t in table.values()] )
            #width2 = max( [len(str(t[0])) for t in table.values()] + \
                          #[len(file1) + 2] )
            #total2 = sum([t[1] for t in table.values()])
            #post += '{0:{1:n}}{2:{3:n}}{4}'.format( str(n) + '-gram', \
                                                    #width1 + 2, \
                                                    #'# ' + file1, \
                                                    #width2 + 2, \
                                                    #'# ' + file2 )
            #post += '\n' + ( '-' * (width1 + width2 + len(file2) + 6) )
            #for ng in table.iterkeys():
               #post += '\n{0:{1:n}}{2:{3:n}}{4}'.format( \
                              #ng.get_string_version( heed_quality, s_or_c ), \
                              #width1 + 2,\
                              #str(table[ng][0]), \
                              #width2 + 2, \
                              #str(table[ng][1]))
            #post += '\n'
            #totaldiff = sum([abs( float(a[0]) / total1 - float(a[1]) / total2 )\
                              #for a in table.values()])
            #post += '\nTotal difference between ' + str(n) + '-grams: ' + \
                    #str(totaldiff) + '\n'

      #return post
   # End compare() -----------------------------------------



   def make_summary_score( self, settings ):
      '''
      Returns a Score object with three Part objects. When you run the Score
      through process_score() in the OutputLilyPond module, the result is a
      LilyPond file that gives summary results about the triangles recorded by
      this instance of VerticalIntervalStatistics.

      Accepts a VISSettings instance, and modifies output according to:
      - heedQuality
      - simpleOrCompound
      - topX
      - threshold
      - showTheseNs

      You can combine "threshold" and "topX" to limit further limit the number
      of triangles that appear. For example, if the top five triangles occurred
      50, 40, 15, 15, and 13 times, and you specify a threshold of 20, you will
      only receive the top two triangles because the others occurred less than
      20 times, and do not meet the threshold.

      In the returned Score, index 0 holds a part intended for an upper staff,
      index 1 holds a part intended for a lower staff, and index 2 holds a part
      with LilyPond annotations, aligned with the upper voices.
      '''

      # (1A) What are the "n" values we need?
      list_of_n = settings.get_property( 'showTheseNs' )

      # (1B) Ensure settings are correct
      settings.set_property( 'leavePieces', False )

      # (1C) Get the formatted list of n-grams
      ngrams_dicts, sorted_ngrams = self.get_ngram_dict( settings, )

      # (2) Initialize Stream objects
      # Hold the upper and lower, and the annotation parts that we'll use
      upper_part = stream.Part()
      lower_part = stream.Part()
      lily_part = stream.Part()

      # Set up the parts with notes; this instruction means no stems will show
      upper_part.lily_instruction = "\t\override Stem #'transparent = ##t"
      lower_part.lily_instruction = "\t\override Stem #'transparent = ##t"

      # Set up the analysis Part
      lily_part.lily_analysis_voice = True

      # (3) Make the Score
      for n in list_of_n:
         # Go through all the n-grams for this value of n
         for this_ngram in sorted_ngrams[n]:
            # Convert "this_ngram" into an NGram object
            ngram_obj = NGram.make_from_str( this_ngram )

            # Hold the list of vertical intervals in this n-gram
            ints = ngram_obj.get_intervals()

            # Hold the measures for this round
            upper_measure = stream.Measure()
            lower_measure = stream.Measure()
            # Except the analysis part

            # Are these the first objects in the streams?
            if 0 == len(upper_part):
               # Add some starting-out stuff to the measures
               meter_str = str( 2 * len(ints) ) + '/4'
               upper_measure.clef = clef.TrebleClef()
               upper_measure.timeSignature = meter.TimeSignature( meter_str )
               lower_measure.clef = clef.BassClef()
               lower_measure.timeSignature = meter.TimeSignature( meter_str )
               # Except the analysis part

            # Make the upper and lower notes
            for interv in ints:
               # (6.1) Get the upper-part Note objects for this ngram
               u_note = note.Note( interv.noteEnd.pitch, quarterLength=1.0 )
               upper_measure.append( u_note )
               # This next "invisible" note, which will turn into an "s" in the
               # LilyPond string, is used to space out the quarter notes
               u_note = note.Note( interv.noteEnd.pitch, quarterLength=1.0 )
               u_note.lily_invisible = True
               upper_measure.append( u_note )

               # (6.2) Get the lower-part Note objects for this ngram
               l_note = note.Note( interv.noteStart.pitch, quarterLength=1.0 )
               lower_measure.append( l_note )
               # This next "invisible" note, which will turn into an "s" in the
               # LilyPond string, is used to space out the quarter notes
               l_note = note.Note( interv.noteStart.pitch, quarterLength=1.0 )
               l_note.lily_invisible = True
               lower_measure.append( l_note )

            # (6.3) Make the corresponding LilyPond analysis for this ngram
            lily_note = note.Note( 'C4', quarterLength=float( 2 * len(ints) ) )
            lily_note.lily_markup = '^' + make_lily_triangle( this_ngram, \
                  print_to_right=str(ngrams_dicts[n][this_ngram]) )
            lily_part.append( lily_note )

            # (6.3.5) Append the Measure objects
            upper_part.append( upper_measure )
            lower_part.append( lower_measure )

            # (6.4) Append some Rest objects to the end
            rest_measure = stream.Measure()
            rest_measure.lily_invisible = True
            the_rest = note.Rest( quarterLength = float( 2 * len(ints) ) )
            rest_measure.append( the_rest )
            upper_part.append( rest_measure )
            lower_part.append( rest_measure )
            lily_part.append( the_rest )

      # Make a Metadata object
      metad = Metadata()
      metad.composer = 'Output from vis'
      metad.title = 'N-Gram Statistics Summary'

      # Finally, make a Score and return it
      return stream.Score( [metad, upper_part, lower_part, lily_part] )
   # End make_summary_score()-------------------------------
# End class VerticalIntervalStatistics ---------------------------------------



def interval_sorter( left, right ):
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
      left = left.replace( direct, '' )
      right = right.replace( direct, '' )

   # If we have numbers with no qualities, we'll just add a 'P' to both, to
   # pretend they have the same quality (which, as far as we know, they do).
   if left[0] in string_digits and right[0] in string_digits:
      left = 'P' + left
      right = 'P' + right

   # Comparisons!
   if left == right:
      post = 0
   elif int(left[1:]) < int(right[1:]): # if x is generically smaller
      post = -1
   elif int(left[1:]) > int(right[1:]): # if y is generically smaller
      post = 1
   else: # otherwise, we're down to the species/quality
      left_qual = left[0]
      right_qual = right[0]
      if left_qual == 'd':
         post = -1
      elif right_qual == 'd':
         post = 1
      elif left_qual == 'A':
         post = 1
      elif right_qual == 'A':
         post = -1
      elif left_qual == 'm':
         post = -1
      elif right_qual == 'm':
         post = 1
      else:
         post = 0

   return post
# End interval_sorter() ------------------------------------



def ngram_sorter( left, right ):
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

   # We need the string version for this
   left = str(left)
   right = str(right)

   # Just in case there are some extra spaces
   left = left.strip()
   right = right.strip()

   # See if we have only one interval left. When there is only one interval,
   # the result of this will be -1
   left_find = left.find(' ')
   right_find = right.find(' ')

   if -1 == left_find:
      if -1 == right_find:
         # Both x and y have only one interval left, so the best we can do is
         # the output from intervalSorter()
         return interval_sorter( left, right )
      else:
         # x has one interval left, but y has more than one, so x is shorter.
         return -1
   elif -1 == right_find:
      # y has one interval left, but x has more than one, so y is shorter.
      return 1

   # See if the first interval will differentiate
   possible_result = interval_sorter( left[:left_find], right[:right_find] )

   if 0 != possible_result:
      return possible_result

   # If not, we'll rely on ourselves to solve the next mystery!
   return ngram_sorter( left[left_find + 1:], right[right_find + 1:] )
# End ngram_sorter() ---------------------------------------
