#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         Vertical_Interval_Statistics.py
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



# Import:
# python
import re, copy, os.path, json
from string import digits as string_digits
from string import join
from collections import defaultdict
from itertools import chain
# music21
from music21 import interval, graph, stream, clef, meter, note
from music21.metadata import Metadata
# vis
from VIS_Settings import VIS_Settings
from problems import NonsensicalInputError, MissingInformationError, \
   NonsensicalInputWarning
from analytic_engine import make_lily_triangle
from NGram import NGram
# numpy
from numpy import array, linalg, ones, log, corrcoef
# matplotlib
import matplotlib
import matplotlib.pyplot as plt



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
   # _simple_ngrams_dict
   # _compound_ngrams_dict
   # _pieces_analyzed
   def __init__( self ):
      '''
      Create a new, "empty" statistics database for a piece.
      '''
      self._simple_interval_dict = defaultdict(lambda:defaultdict(int))
      self._compound_interval_dict = defaultdict(lambda:defaultdict(int))
      self._simple_ngrams_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(int))))
      self._compound_ngrams_dict = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(int))))
      self._pieces_analyzed = []



   def __repr__( self ):
      return str(self)



   def __str__( self ):
      # This should produce something like...
      # "<Vertical_Interval_Statistics for 1 piece with 14 intervals; 26 2-grams; 19 3-grams>"
      nbr_pieces = len(self._pieces_analyzed)
      pieces = " pieces"
      if 1 == nbr_pieces:
         pieces = " piece"
      post = '<Vertical_Interval_Statistics for '+str(nbr_pieces)+pieces+' with ' + \
            str(len(self._compound_interval_dict)) + ' intervals; '
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
      if not isinstance(self._pieces_analyzed,list):
         raise NonsensicalInputError("_pieces_analyzed must be of type list")
      for s in self._pieces_analyzed:
         if not isinstance(s,str):
            raise NonsensicalInputError("_pieces_analyzed may contain only strings")

      easy_atts = ["_simple_interval_dict","_compound_interval_dict"]
      ngram_dicts = ["_compound_ngrams_dict","_simple_ngrams_dict"]

      def validate_values( vals,att_name ):
         for v in vals:
            if not isinstance(v,list):
               raise NonsensicalInputError(att_name+" values must be of type list")
            if len(v) != 2:
               raise NonsensicalInputError(att_name+" value does not have 2 items")
            if not isinstance(v[1],list) or not isinstance(v[0],int):
               raise NonsensicalInputError(att_name+" values must be of the form [int,list]")
            for i in v[1]:
               if not isinstance(i,int):
                  raise NonsensicalInputError("second part of "+att_name+" values must be list of ints")
            if v[0] != sum(v[1]):
               raise NonsensicalInputError("first part of "+att_name+" values must equal sum of second part")
            if len(v[1]) != len(self._pieces_analyzed):
               raise NonsensicalInputError("second part of "+att_name+" must have as many elements as pieces analyzed")

      for att_name in easy_atts:
         att = getattr(self,att_name)
         if not isinstance(att,dict):
            raise NonsensicalInputError(att_name+" must be of type dict")
         for k in att.keys():
            try:
               i = interval.Interval(k)
            except: #music21 error if not a proper interval string
               raise NonsensicalInputError(k+" is not a valid interval")
         validate_values( att.values(), att_name )

      for att_name in ngram_dicts:
         att = getattr(self,att_name)
         if not isinstance(att,dict):
            raise NonsensicalInputError(att_name+" must be of type dict")
         for d in att.values():
            if not isinstance(d,dict):
               raise NonsensicalInputError(att_name+" values must be of type dict")
            for k,v in d.items():
               if not isinstance(k,NGram):
                  raise NonsensicalInputError(att_name+" value keys must be of type NGram")
               if not isinstance(v,dict):
                  raise NonsensicalInputError(att_name+" value values must be of type dict")
               for key in v.keys():
                  if not isinstance(key,NGram):
                     raise NonsensicalInputError(att_name+" value value keys must be of type NGram")
               validate_values( v.values(), att_name+" value" )

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
      return {Vertical_Interval_Statistics._stringify(k):Vertical_Interval_Statistics._stringify(v) \
                for k,v in d.items()} if isinstance(d,dict) else \
             map(Vertical_Interval_Statistics._stringify,d) if isinstance(d,list) else \
             d if isinstance(d,int) else \
             str(d)


   @staticmethod
   def dictify( d ):
      '''
      Converts a nested defaultdict into a regular dict.
      '''
      return {k:Vertical_Interval_Statistics.dictify(v) for k,v in d.items()} if isinstance(d,defaultdict) else d


   def to_json( self ):
      '''
      Returns a string containing the JSON-serialization of this
      Vertical_Interval_Statistics instance.
      '''
      # _stringify ensures that the dict is JSON-serializable,
      # since all keys in a JSONObject must be strings
      return json.JSONEncoder().encode(Vertical_Interval_Statistics._stringify(self.__dict__))



   @classmethod
   def from_json( cls, json_string ):
      '''
      Given a string containing the JSON version of a V_I_S instance,
      convert it to a python object containing the V_I_S instance and
      then check it for internal consistency (see _validate()) and
      return the object.
      '''
      vis = Vertical_Interval_Statistics()
      # use _stringify since JSONDecoder interprets all strings as unicode.
      d = None
      try:
         d = Vertical_Interval_Statistics._stringify(json.JSONDecoder().decode(json_string))
      except Exception as e:
         raise NonsensicalInputError("JSON data could not be parsed: "+str(e))
      def fix_keys( ngd ):
         '''
         since JSON objects have string keys, convert the
         strings to NGrams for the ngram dict ngd.
         '''
         return {NGram.make_from_str(k):fix_keys(v) for k,v in ngd.items()} if isinstance(ngd,dict) \
                else ngd
      easy_atts = ["_pieces_analyzed","_simple_interval_dict","_compound_interval_dict"]
      ngram_dicts = ["_compound_ngrams_dict","_simple_ngrams_dict"]
      for att in easy_atts+ngram_dicts:
         if d.get(att) is not None:
            val = d[att] if att in easy_atts else {k:fix_keys(ngd) for k,ngd in d[att].items()}
            setattr(vis,att,val)
         else:
            raise MissingInformationError("The dict supplied is missing the attribute "+att)
      if vis._validate():
         return vis



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
      Since the interval dicts normally keep track of the occurrences
      of an interval in each piece, this method returns the "summary"
      version which matches a simple interval to the total number of
      its occurrences in this V_I_S instance.
      '''
      return {k:v['Total'] for k,v in self._simple_interval_dict.iteritems()}



   def get_compound_interval_summary_dict( self ):
      '''
      Since the interval dicts normally keep track of the occurrences
      of an interval in each piece, this method returns the "summary"
      version which matches a compound interval to the total number of
      its occurrences in this V_I_S instance.
      '''
      return {k:v['Total'] for k,v in self._compound_interval_dict.iteritems()}



   def get_interval_occurrences( self, which_interval, simple_or_compound='simple', piece=None ):
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

      # Given a species (number), finds all the occurrences of any quality.
      # The second argument should be either self._simple_interval_dict or
      # self._compound_interval_dict
      def get_all_qualities( species, db, piece ):
         post = 0
         for quality in qualities:
            if ( quality + species ) in db:
               if piece is None:
                  #then the total number of occurrences
                  post += db[quality+species]['Total']
               else:
                  post += db[quality+species][piece]

         return post

      errorstr = 'Second argument must be either "simple" or "compound"'

      # Are they ignoring quality? Yes, if the interval is just a digit or if
      # the first character is a direction
      if which_interval.isdigit() or which_interval[0] in directions:
         if 'simple' == simple_or_compound:
            return get_all_qualities( which_interval, self._simple_interval_dict, piece )
         elif 'compound' == simple_or_compound:
            return get_all_qualities( which_interval, self._compound_interval_dict, piece )
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
      '''

      # set up the keys for the various nested compound-ngram dicts
      compound_no_quality_version = the_ngram.get_string_version(False, 'compound')
      compound_quality_version = the_ngram.get_string_version(True, 'compound')

      # add the occurrence to the compound-ngram dict
      self._compound_ngrams_dict[the_ngram._n][compound_no_quality_version]\
         [compound_quality_version][the_piece] += 1
      self._compound_ngrams_dict[the_ngram._n][compound_no_quality_version]\
         [compound_quality_version]['Total'] += 1

      # set up the keys for the various nested simple-ngram dicts
      simple_no_quality_version = the_ngram.get_string_version(False, 'simple')
      simple_quality_version = the_ngram.get_string_version(True, 'simple')

      # add the occurrence to the simple-ngram dict
      self._simple_ngrams_dict[the_ngram._n][simple_no_quality_version]\
         [simple_quality_version][the_piece] += 1
      self._simple_ngrams_dict[the_ngram._n][simple_no_quality_version]\
         [simple_quality_version]['Total'] += 1


   # End add_ngram() ---------------------------------------



   def get_ngram_dict( self, settings, leave_pieces = True ):
      '''
      Given a VIS_Settings object, return a tuple with:
      - a dict including the n-gram specified statistics, and
      - a dict with a sorted list of keys for the required values of n

      Set the "leave_pieces" argument to "False" to omit voice-pair-specific
      data, outputting only the totals for all voice pairs.

      Note that each n-gram object is appears in the statistics dictionary as
      a string, as per the settings provided.
      '''

      # (1) Generate the dictionary
      # (1a) do we want simple or compound ngrams?
      simple = settings.get_property('simpleOrCompound') == 'simple'
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
         output_dict = {n:
                       dict(chain(*[data_dict[n][ng].items() for ng in data_dict[n].keys()]))
                     for n in list_of_n}
      else:
         # We don't need to include quality, so just forget
         # about the values of the ngram dict and sum up all their data.
         output_dict = {n:
                          {ng:
                              {p:sum(d[v][p] for v in d.keys())
                               for p in self._pieces_analyzed+['Total']}
                           for ng, d in data_dict[n].items()}
                        for n in list_of_n}

      # (2) Do the filtering for "top X"
      topX = settings.get_property( 'topX' ) # the "X"
      if topX is not None:
         for n in list_of_n:
            # sort the keys by frequency
            sorted_ngrams = sorted( output_dict[n].keys(), \
                                    key = lambda ng: output_dict[n][ng]['Total'], \
                                    reverse = True )
            # accept only the top topX
            sorted_ngrams = sorted_ngrams[:topX]
            # filter the dict to only include the new keys
            output_dict[n] = {ng:output_dict[n][ng] for ng in sorted_ngrams}

      # (3) Do the filtering for "threshold" (n-grams with fewer occurrences
      # "threshold" should not be included)
      thresh = settings.get_property( 'threshold' ) # the threshold
      if thresh is not None:
         for n in list_of_n:
            keys = filter(lambda ng: output_dict[n][ng]['Total'] >= thresh, output_dict[n].keys())
            output_dict[n] = {ng:output_dict[n][ng] for ng in keys}

      # (4) Sort the keys according to the settings
      # will we have to reverse our sorts?
      rev = settings.get_property( 'sortOrder' ) == 'descending'
      # first we just sort by NGram...
      keys = {n: sorted(output_dict[n].keys(), cmp = ngram_sorter, reverse = rev)
                 for n in list_of_n}
      by_freq = settings.get_property( 'sortBy' ) == 'frequency'
      # should we sort by frequency?
      if by_freq:
         # if so, sort again
         keys = {n: sorted(keys[n], key = lambda ng: output_dict[n][ng]['Total'], reverse = rev)
                    for n in list_of_n}
      # should we forget the piece breakdown?
      if leave_pieces is False:
         output_dict = {n:{ng:v['Total'] for ng,v in output_dict[n].items()} for n in list_of_n}
      return (output_dict,keys)
   # End get_ngram_dict() ----------------------------------



   def get_ngram_occurrences( self, which_ngram ):
      '''
      Returns the number of occurrences of a particular n-gram. Currently, all
      n-grams are treated as though they have compound intervals.

      The first argument must be an NGram object or the output from either
      NGram.stringVersion or str(NGram) (which calls stringVersion() internally).

      Automatically does or does not track quality, depending on the settings
      of the inputted NGram objects.
      '''

      # TODO: write comments for this method
      ng = None
      if isinstance(which_ngram,NGram):
         ng = which_ngram
      if isinstance(which_ngram,basestring):
         try:
            ng = NGram.make_from_str(which_ngram)
         except NonsensicalInputError as nie:
            raise
      else:
         raise NonsensicalInputError("Input must be of type NGram or string")
      ng_key = ng.get_string_version(True,'compound')
      n = ng.n()
      settings = VIS_Settings()
      settings.set_property('simpleOrCompound', 'compound')
      settings.set_property('heedQuality', 'true')
      settings.set_property( 'showTheseNs', [n] )
      the_dict = self.get_ngram_dict( settings )[0][n]
      return 0 if the_dict.get(ng_key) is None else the_dict[ng_key]['Total']
   # End get_ngram_occurrences() ---------------------------



   def extend( self, other_stats ):
      '''
      Given a Vertical_Interval_Statistics instance, take all of its relevant data
      and merge it into self.
      '''

      def merge_default_dicts(x,y):
         '''
         Given two nested defaultdicts, return a defaultdict
         which has all of the keys of both and values which are
         the sums of the corresponding values in each.
         '''
         new_keys = set(x.keys()+y.keys())
         if x.default_factory == int:
            return defaultdict(int,((key,x[key]+y[key]) for key in new_keys))
         else:
            return defaultdict(x.default_factory,((key,merge_default_dicts(x[key],y[key]))
                               for key in new_keys))

      self._pieces_analyzed += other_stats._pieces_analyzed
      self._simple_interval_dict = merge_default_dicts(self._simple_interval_dict, \
                                      other_stats._simple_interval_dict)
      self._compound_interval_dict = merge_default_dicts(self._compound_interval_dict, \
                                        other_stats._compound_interval_dict)

      self._compound_ngrams_dict = merge_default_dicts( self._compound_ngrams_dict, \
                                      other_stats._compound_ngrams_dict )
      self._simple_ngrams_dict = merge_default_dicts( self._simple_ngrams_dict, \
                                    other_stats._simple_ngrams_dict )
   # End extend() ------------------------------------------



   # NB: this method does NOT get used in the GUI
   def retrogrades( self, the_settings, specs='' ):
      # (1) Figure out which values of 'n' we should output.
      post = ''
      list_of_n = the_settings.get_property('showTheseNs')

      # (2) Decide whether to take 'quality' or 'no_quality'
      output_dict = self.prepare_ngram_output_dict( the_settings )

      # (3) Sort the dictionary
      sorted_ngrams = []
      # We need to have enough 'n' places in sorted_ngrams to hold the
      # sorted dictionaries.
      for n in xrange(max(list_of_n) + 1):
         sorted_ngrams.append( [] )
      for n in list_of_n:
         sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), key = lambda ng: output_dict[n][ng] )

      # (4) Generate the results
      ngram_pairs = []
      for n in xrange(max(list_of_n) + 1):
         ngram_pairs.append( {} )
      for n in list_of_n:
         for ng in sorted_ngrams[n]:
            retrograde = ng.retrograde()
            # this is an odd workaround; used to get KeyErrors, possibly because accessing the key
            # wasn't using __hash__ correctly? Anyway, the problem seems to have to do with
            # changing NGram.__repr__ to include the specific pitches in the NGram.
            matches = [gram for gram in sorted_ngrams[n] if gram == retrograde]
            if len(matches) > 0:
               for ngram in matches:
                  ngram_pairs[n][(ng,retrograde)] = (output_dict[n][ng],output_dict[n][ngram])
                  sorted_ngrams[n].remove(retrograde)
            else:
               ngram_pairs[n][(ng,retrograde)] = (output_dict[n][ng],0)

      # (5.1) If some graphs are asked for, prepare them
      if 'graph' in specs:
         grapharr = []
         for n in list_of_n:
            keys = sorted(ngram_pairs[n].keys(), key = lambda ng: \
                          float(ngram_pairs[n][ng][1])/float(ngram_pairs[n][ng][0]), reverse=True)
            g = graph.GraphGroupedVerticalBar(doneAction=None)
            data = []
            for key in keys:
               entry = (str(key[0])+' '+str(key[1]),)
               pair = {}
               pair['n-gram'] = ngram_pairs[n][key][0]
               pair['retrograde'] = ngram_pairs[n][key][1]
               entry += (pair,)
               data.append(entry)
            g.setData(data)
            g.setTitle(str(n)+'-Grams')
            # this is a very slight edit of the music21.graph.GraphGroupedVerticalBar.process()
            # and labelBars() methods
            fig = plt.figure()
            setattr(g,'fig', fig)
            fig.subplots_adjust(bottom=.3)
            ax = fig.add_subplot(1, 1, 1)

            # b value is a list of values for each bar
            for a, b in getattr(g,'data'):
               barsPerGroup = len(b)
               # get for legend
               subLabels = sorted(b.keys())
               break
            widthShift = 1 / float(barsPerGroup)

            xVals = []
            yBundles = []
            for i, (a, b) in enumerate(getattr(g,'data')):
               # create x vals from index values
               xVals.append(i)
               yBundles.append([b[key] for key in sorted(b.keys())])

            rects = []
            for i in range(barsPerGroup):
               yVals = []
               for j, x in enumerate(xVals):
                  # get position, then get bar group
                  yVals.append(yBundles[j][i])
               xValsShifted = []
               for x in xVals:
                  xValsShifted.append(x + (widthShift * i))
               colors = getattr(g,'colors')

               rect = ax.bar(xValsShifted, yVals, width=widthShift, alpha=.8,
                   color=graph.getColor(colors[i % len(colors)]))
               rects.append(rect)

            colors = []
            for k in range(len(rects)):
               for j in range(len(rects[k])):
                  height = rects[k][j].get_height()
                  ax.text(rects[k][j].get_x()+rects[k][j].get_width()/2., height+.05, \
                          '%s'%(str(keys[j][k])), rotation='vertical', ha='center', va='bottom',
                          fontsize=getattr(g,'tickFontSize'), family=getattr(g,'fontFamily'))
               colors.append(rects[k][0])

            font = matplotlib.font_manager.FontProperties(size=getattr(g,'tickFontSize'),
                        family=getattr(g,'fontFamily'))
            ax.legend(colors, subLabels, prop=font)

            g._adjustAxisSpines(ax)
            g._applyFormatting(ax)
            g.done()
            grapharr.append(g)
         post = grapharr
      # (5.2) Else prepare a nicely formatted list of the results
      else:
         for n in list_of_n:
            post += 'All the ' + str(n) + '-grams with retrogrades:\n-----------------------------\n'
            for ng in ngram_pairs[n].keys():
               post += str(ng[0]) + ': ' + str(ngram_pairs[n][ng][0]) +'; ' \
                       +str(ng[1])+': '+str(ngram_pairs[n][ng][1]) + '\n'
      return post
   # End retrogrades() -------------------------------------


   # NB: This method does NOT get used in the GUI
   def power_law_analysis( self, the_settings ):
      list_of_n = the_settings.get_property('showTheseNs')

      # (2) Decide whether to take 'quality' or 'no_quality'
      output_dict = self.prepare_ngram_output_dict( the_settings )

      # (3) Sort the dictionary
      sorted_ngrams = []
      # We need to have enough 'n' places in sorted_ngrams to hold the
      # sorted dictionaries.
      for n in xrange(max(list_of_n) + 1):
         sorted_ngrams.append( [] )
      post = ''
      for n in list_of_n:
         sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), key = lambda ng: output_dict[n][ng], reverse=True )
         # we do a power-law regression by instead looking at
         # the logarithmic scales and doing linear regression
         xi = [log(i) for i in range(1,len(sorted_ngrams[n])+1)]
         A = array([ xi, ones(len(xi))])
         y = [log(output_dict[n][ng]) for ng in sorted_ngrams[n]]
         w = linalg.lstsq(A.T,y)[0] #least-squares regression on the data
         # w[0] contains the slope of the line, and we'll just display
         # positive numbers because that's nice.
         post += 'The power law exponent for the '+str(n)+'-grams is '+str(-w[0])+ \
                 '; correlation coefficient '+str(-corrcoef(xi,y)[0,1])
      return post
   # End power_law_analysis() ------------------------------



   def get_formatted_intervals( self, the_settings ):
      '''
      Returns a str with a nicely-formatted representation of the interval
      frequencies recoreded in this Vertical_Interval_Statistics() object.

      The first argument is a VIS_Settings() object, from which we will use
      all of the formatting properties.
      '''

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
         non_numeric = re.compile(r'[^\d-]+')
         # replace anything that isn't a number with the empty string
         red = lambda k:non_numeric.sub('',k)
         # apply that sweet function to all of the intervals
         keys = set(red(k) for k in the_dict.keys())
         # now for each new key, replace it with a tuple containing
         # (key,[set of old keys which have this common quality-free form])
         keys = [(k,filter(lambda t:red(t[0])==k,the_dict.items())) for k in keys]
         # now we make a dict with the new keys and values being the sum
         #over all the values associated to the old keys
         piece_list = self._pieces_analyzed+['Total']
         the_dict = {k:
                       {p:sum(v[p] for K,v in l) for p in piece_list}
                     for k,l in keys}

      # (2) Sort the results in the specified way.
      if 'frequency' == the_settings.get_property( 'sortBy' ):
         # Sort by frequency
         if 'ascending' == the_settings.get_property( 'sortOrder' ):
            sorted_intervals = sorted( the_dict.iterkeys(), key= lambda x: the_dict[x]['Total'] )
         else:
            # Default to 'descending'
            sorted_intervals = sorted( the_dict.iterkeys(), key= lambda x: the_dict[x]['Total'], reverse=True )
      else:
         # Default to 'by interval'
         if 'descending' == the_settings.get_property( 'sortOrder' ):
            sorted_intervals = sorted( the_dict.iterkeys(), cmp=interval_sorter, reverse=True )
         else: # elif 'ascending' in specs or 'low to high' in specs:
            # Default to 'ascending'
            sorted_intervals = sorted( the_dict.iterkeys(), cmp=interval_sorter )

      # (3A) Make a graph, if requested.
      if 'graph' == the_settings.get_property( 'outputFormat' ):
         g = graph.GraphHistogram(doneAction=None)
         data = [(i,the_dict[interv]['Total']) for i, interv in enumerate(sorted_intervals)]
         g.setData(data)
         g.setTitle("Intervals in "+join([str(os.path.split(p)[1])+", " for p in self._pieces_analyzed])[:-2])
         g.setTicks('x',[(i+0.4,interv) for i,interv in enumerate(sorted_intervals)])
         g.xTickLabelHorizontalAlignment='center'
         setattr(g,'xTickLabelRotation',45)
         g.setAxisLabel('x','Interval')
         max_height = max([the_dict[interv]['Total'] for interv in sorted_intervals])+1
         tick_dist = max(max_height/10,1)
         ticks = []
         k = 0
         while k*tick_dist <= max_height:
            k += 1
            ticks.append(k*tick_dist)
         g.setTicks('y',[(k,k) for k in ticks])
         g.fig = plt.figure()
         g.fig.subplots_adjust(left=0.15)
         ax = g.fig.add_subplot(1, 1, 1)

         x = []
         y = []
         for a, b in g.data:
            x.append(a)
            y.append(b)
         ax.bar(x, y, alpha=.8, color=graph.getColor(g.colors[0]))

         g._adjustAxisSpines(ax)
         g._applyFormatting(ax)
         ax.set_ylabel('Frequency', fontsize=g.labelFontSize, family=g.fontFamily, rotation='vertical')
         g.done()
         return g

      # (3B) Default to formatted list.
      post = ''
      widths = []
      heading = 'Interval'

      # Calculate the width of the first column, which contains the interval names
      width = max([len(str(k)) for k in sorted_intervals]+[len(heading)+2])
      widths.append( width )

      for i, piece in enumerate(self._pieces_analyzed):
         width = max([len(str(the_dict[k][piece])) for k in sorted_intervals]+[len(os.path.split(piece)[1])+3])
         widths.append(width)
      width_total = max([len(str(the_dict[k]['Total'])) for k in sorted_intervals]+[len("Total ")])+2
      widths.append(width_total)
      row = "{0:{1:n}}".format( heading, widths[0] )

      # Add the header
      row += "{0:{1:n}}".format("# Total ", widths[-1])
      # Add the "#pN" index
      for i, piece in enumerate(self._pieces_analyzed):
         row += "{0:{1:n}}".format( '# ' + os.path.split(piece)[1] + ' ', widths[i + 1] )
      row += "\n"
      post += row
      row = '=' * sum(widths) + '\n'
      post += row

      # Add each interval
      for interv in sorted_intervals:
         # print the n-gram name
         row = "{0:{1:n}}".format( str(interv), widths[0] )
         # the total for all pieces and voice pairs
         row += "{0:{1:n}}".format(str(the_dict[interv]['Total']), widths[-1])
         # the totals by voice pair
         for i, piece in enumerate(self._pieces_analyzed,start=1):
            row += "{0:{1:n}}".format(str(the_dict[interv][piece]), widths[i])
         # end the row
         row += "\n"
         post += row

      post += '\n'

      return post
   # end get_formatted_intervals() -------------------------



   def similarity( self, some_pieces, other_pieces, n, simple_or_compound="compound", heedQuality=False ):
      '''
      Given two lists of indices of self._pieces_analyzed,
      an integer n, and the other obvious settings, computes
      the similarity between the N-Grams in the two samples.
      '''
      settings = VIS_Settings()
      settings.set_property( 'heedQuality', heedQuality )
      settings.set_property( 'simpleOrCompound', simple_or_compound )
      settings.set_property( 'showTheseNs', [n] )
      the_dict = self.prepare_ngram_output_dict( settings )[n]
      total_some = sum(sum(v[1][i] for i in some_pieces) for v in the_dict.values())
      total_other = sum(sum(v[1][i] for i in other_pieces) for v in the_dict.values())
      total_diff = sum(abs((sum(v[1][i] for i in some_pieces)*100)/total_some \
                           -(sum(v[1][i] for i in other_pieces)*100)/total_other) \
                       for v in the_dict.values())
      return 1.0 - float(total_diff)/200



   def get_formatted_ngrams( self, the_settings ):
      '''
      Returns a str or music21.graph.Graph object with a nicely-formatted
      representation of the n-gram frequencies recoreded in this
      Vertical_Interval_Statistics() object.

      The argument is a VIS_Settings() object, from which we get
      formatting options.
      '''

      graph = the_settings.get_property( 'outputFormat' ) == 'graph'
      if graph:
         return self.get_ngram_graph(the_settings)
      else:
         return self.get_ngram_text(the_settings)
   # end get_formatted_ngrams() ----------------------------

   def get_ngram_graph( self, settings ):
      output_dict, keys = self.get_ngram_dict(settings)
      grapharr = []
      for n in output_dict.keys():
         g = graph.GraphHistogram(doneAction=None,tickFontSize=12)
         data = [(k,output_dict[n][key]['Total']) \
                  for k, key in enumerate(keys[n])]
         g.setData(data)
         g.setTicks('x',[(k+0.7,key) for k, key in enumerate(keys[n])])
         g.setAxisLabel('x',str(n)+"-Gram")
         g.xTickLabelRotation = 45
         g.xTickLabelVerticalAlignment='top'
         g.xTickLabelHorizontalAlignment='right'
         g.setTitle(str(n)+"-Grams in "+join([str(os.path.split(p)[1])+", " \
                    for p in self._pieces_analyzed])[:-2])
         max_height = max([output_dict[n][key]['Total'] for key in keys[n]])+1
         tick_dist = max(max_height/10,1)
         ticks = []
         k = 0
         while k*tick_dist <= max_height:
            k += 1
            ticks.append(k*tick_dist)
         g.setTicks('y',[(k,k) for k in ticks])
         g.fig = plt.figure()
         g.fig.subplots_adjust(left=0.15, bottom=0.2)
         ax = g.fig.add_subplot(1, 1, 1)

         x = []
         y = []
         for a, b in g.data:
            x.append(a)
            y.append(b)
         ax.bar(x, y, alpha=.8, color=graph.getColor(g.colors[0]))

         g._adjustAxisSpines(ax)
         g._applyFormatting(ax)
         ax.set_ylabel('Frequency', fontsize=g.labelFontSize, family=g.fontFamily, \
                        rotation='vertical')
         g.done()
         grapharr.append(g)
      return grapharr

   def get_ngram_text( self, settings ):
      output_dict, keys = self.get_ngram_dict(settings)
      # Start with a title
      post = 'N-Grams\n\n'

      # Piece Title and Part Combination Assignments
      for k, piece in enumerate( self._pieces_analyzed, start=1 ):
         post += 'p' + str(k) + " = " + os.path.split(piece)[1] + '\n'

      post += '\n'

      # Print all requested values of n
      for n, the_dict in output_dict.items():
         total_n = sum( v['Total'] for v in the_dict.values() )
         post += "Total number of " + str(n) + "-grams: " + str(total_n) + "\n\n"
         sorted_ngrams = keys[n]
         widths = []
         heading = str(n) + "-gram"
         width = max( [ len(str(k)) for k in sorted_ngrams ] + \
                      [ len(heading) ] ) + 2
         widths.append( width )

         # Go through each piece (for this value of n)
         for i, piece in enumerate( self._pieces_analyzed ):
            width = max( [ len( str( the_dict[k][piece] ) ) \
                    for k in sorted_ngrams] + [ len( 'p' + str( i + 1 ) ) + 3 ] )
            widths.append( width )

         width_total = max([len(str(the_dict[k]['Total'])) \
                           for k in sorted_ngrams]+[len("Total ")])+2
         widths.append(width_total)
         row = "{0:{1:n}}".format(heading, widths[0])

         row += "{0:{1:n}}".format( '# Total ', widths[-1])

         for i, piece in enumerate( self._pieces_analyzed, start=1 ):
            row += "{0:{1:n}}".format( '# p' + str(i) + ' ', widths[i] )

         row += '\n'
         post += row
         row = '=' * sum(widths) + '\n'
         post += row

         for ngram in sorted_ngrams:
            # add the n-gram name
            row = "{0:{1:n}}".format(str(ngram), widths[0])
            # add the total
            row += "{0:{1:n}}".format(str(the_dict[ngram]['Total']), widths[-1])
            # add the per-piece totals
            for i, piece in enumerate(self._pieces_analyzed, start = 1):
               row += "{0:{1:n}}".format(str(the_dict[ngram][piece]), widths[i])
            row += "\n"
            post += row

         post += '\n\n'

      # Remove the final newline, which we don't really need
      post = post[:-3]
      return post

   def compare( self, the_settings, other_stats, file1, file2, specs='' ):
      '''
      Compares the relative frequencies of n-grams in two different files,
      displaying a text chart or graph, as well as computing the "total metric"
      difference between the two.
      '''
      # (1) Figure out which 'n' values to display
      post = ''
      list_of_n = []
      if 'n=' in specs:
         list_of_n = specs[specs.find('n=')+2:]
         list_of_n = list_of_n[:list_of_n.find(' ')]
         list_of_n = sorted(set([int(n) for n in re.findall('(\d+)', list_of_n)]))
         # Check those n values are acceptable/present
         for n in list_of_n:
            # First check we have that index and it's potentially filled with
            # n-gram values
            if n < 2 or (n > (len(self._compound_ngrams_dict) - 1) and n > (len(other_stats._compound_ngrams_dict) - 1)):
               # throw it out
               list_of_n.remove( n )
               post += 'Not printing ' + str(n) + '-grams; there are none for that "n" value.\n'
               continue # to avoid the next test
            # Now check if there are actually n-grams in that position. If we
            # analyzed only for 5-grams, for instance, then 2, 3, and 4 will be
            # valid in the n-gram dictionary, but they won't actually hold
            # any n-grams.
            if {} == self._compound_ngrams_dict[n] and {} == other_stats._compound_ngrams_dict[n]:
               # throw it out
               list_of_n.remove( n )
               post += 'Not printing ' + str(n) + '-grams; there are none for that "n" value.\n'
      else:
         list_of_n = [i for i in range(max(len(self._compound_ngrams_dict),len(other_stats._compound_ngrams_dict))) if \
                     self._compound_ngrams_dict[i] != {} or other_stats._compound_ngrams_dict[i] != {}]
      # What if we end up with no n values?
      if 0 == len(list_of_n):
         raise MissingInformationError( "All of the 'n' values appear to have no n-grams" )

      # (2) Organize the results
      tables = {}
      for n in list_of_n:
         table = {}
         sett = copy.deepcopy(the_settings)
         sett.set_property('heedQuality false')
         sett.set_property( 'showTheseNs', list_of_n )
         self_dict = self.prepare_ngram_output_dict( sett )[n]
         other_dict = other_stats.prepare_ngram_output_dict( sett )[n]
         for ng in self_dict.iterkeys():
            table[ng] = [self_dict[ng],0]
         for ng in other_dict.iterkeys():
            if ng in self_dict:
               table[ng][1] = other_dict[ng]
            else:
               table[ng] = [0,other_dict[ng]]
         tables[n] = table
      # (3.1) If some graphs are asked for, prepare them
      if 'graph' in specs:
         grapharr = []
         for n in list_of_n:
            table = tables[n]
            keys = table.keys()
            g = graph.GraphGroupedVerticalBar(doneAction=None)
            data = []
            for k, key in enumerate(keys):
               pair = {}
               pair[file1] = table[key][0]
               pair[file2] = table[key][1]
               entry = ("bar%s"%str(k),pair)
               data.append(entry)
            g.setData(data)
            g.setTicks('x',[(k+0.4,key) for k, key in enumerate(keys)])
            g.xTickLabelRotation = 90
            g.xTickLabelVerticalAlignment='top'
            g.setTitle(str(n)+'-Grams')
            g.setTicks('y',[(k,k) for k in xrange(max([max(int(v[0]),int(v[1])) for v in table.values()]))])
            g.process()
            grapharr.append(g)
         post = grapharr

      # (3.2) Otherwise make a nicely formatted list of the results
      else:
         s_or_c = the_settings.get_property( 'simpleOrCompound' )
         heed_quality = the_settings.get_property( 'heedQuality' )
         for n in list_of_n:
            table = tables[n]
            width1 = max([len(ng.get_string_version(heed_quality,s_or_c)) for ng in table.keys()])
            total1 = sum([t[0] for t in table.values()])
            width2 = max([len(str(t[0])) for t in table.values()]+[len(file1)+2])
            total2 = sum([t[1] for t in table.values()])
            post += "{0:{1:n}}{2:{3:n}}{4}".format(str(n)+"-Gram",width1+2,"# "+file1,width2+2,"# "+file2)
            post += "\n"+("-"*(width1+width2+len(file2)+6))
            for ng in table.iterkeys():
               post += "\n{0:{1:n}}{2:{3:n}}{4}".format(ng.get_string_version(heed_quality,s_or_c),width1+2,\
                        str(table[ng][0]),width2+2,str(table[ng][1]))
            post += '\n'
            totaldiff = sum([abs(float(a[0])/total1-float(a[1])/total2) for a in table.values()])
            post += "\nTotal difference between "+str(n)+"-grams: "+str(totaldiff)+"\n"
      return post
   # end compare() -----------------------------------------



   def make_summary_score( self, settings ):
      '''
      Returns a Score object with three Part objects. When you run the Score
      through process_score() in the output_LilyPond module, the result is a
      LilyPond file that gives summary results about the triangles recorded by
      this instance of Vertical_Interval_Statistics.

      Accepts a VIS_Settings instance, and modifies output according to:
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

      # (1B) Get the formatted list of n-grams
      ngrams_dicts, keys = self.get_ngram_dict( settings, leave_pieces = False )

      # (2) Initialize Stream objects

      # Hold the upper and lower, and the annotation parts that we'll use
      upper_part = stream.Part()
      lower_part = stream.Part()
      lily_part = stream.Part()

      # Set up the analysis Part
      lily_part.lily_analysis_voice = True

      # (3) Make the Score
      for n in list_of_n:
         # Go through all the n-grams for this value of n
         for this_ngram in ngrams_dicts[n]:
            # Convert "this_ngram" into an NGram object
            ngram_obj = NGram.make_from_str( this_ngram )

            # Hold the list of vertical intervals in this n-gram
            ints = ngram_obj.get_intervals()

            # Hold the measures for this round
            upper_measure = stream.Measure()
            #upper_measure.timeSignature = meter.TimeSignature( '4/4' )
            lower_measure = stream.Measure()
            #lower_measure.timeSignature = meter.TimeSignature( '4/4' )
            # Except the analysis part

            # Are these the first objects in the streams?
            if 0 == len(upper_part):
               # Add some starting-out stuff to the measures
               upper_measure.clef = clef.TrebleClef()
               upper_measure.timeSignature = meter.TimeSignature( '4/4' )
               lower_measure.clef = clef.BassClef()
               lower_measure.timeSignature = meter.TimeSignature( '4/4' )
               # Except the analysis part

            # Make the upper and lower notes
            for interv in ints:
               # (6.1) Get the upper-part Note objects for this ngram
               upper_measure.append( note.Note( interv.noteEnd.pitch, quarterLength=2.0 ) )

               # (6.2) Get the lower-part Note objects for this ngram
               lower_measure.append( note.Note( interv.noteStart.pitch, quarterLength=2.0 ) )

            # (6.3) Make the corresponding LilyPond analysis for this ngram
            lily_note = note.Note( 'C4', quarterLength=4.0 )
            lily_note.lily_markup = '^' + make_lily_triangle( this_ngram, print_to_right=str(ngrams_dicts[n][this_ngram]) )
            lily_part.append( lily_note )

            # (6.3.5) Append the Measure objects
            upper_part.append( upper_measure )
            lower_part.append( lower_measure )

            # (6.4) Append some Rest objects to the end
            rest_measure = stream.Measure()
            rest_measure.lily_invisible = True
            rest_measure.append( note.Rest( quarterLength=4.0 ) )
            upper_part.append( rest_measure )
            lower_part.append( rest_measure )
            lily_part.append( note.Rest( quarterLength=4.0 ) )

      # Make a Metadata object
      metad = Metadata()
      metad.composer = 'Output from vis'
      metad.title = 'N-Gram Statistics Summary'

      # Finally, make a Score and return it
      return stream.Score( [metad, upper_part, lower_part, lily_part] )
   # End make_summary_score()-------------------------------
# End class Vertical_Interval_Statistics ---------------------------------------



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
# End interval_sorter() ------------------------------------



def ngram_sorter( a, b ):
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

   x,y = str(a), str(b)
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
# End ngram_sorter() ---------------------------------------
