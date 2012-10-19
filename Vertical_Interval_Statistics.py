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



## Import:
# python
import re, copy, os.path, json
from string import digits as string_digits
from string import join
# music21
from music21 import interval, graph, stream, clef, meter, note
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
   # _simple_ngrams_dict
   # _compound_ngrams_dict
   # _pieces_analyzed
   def __init__( self ):
      '''
      Create a new, "empty" statistics database for a piece.
      '''
      self._simple_interval_dict = {}
      self._compound_interval_dict = {}
      self._simple_ngrams_dict = [{},{},{}]
      self._compound_ngrams_dict = [{},{},{}]
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
      for i in xrange(2,len(self._compound_ngrams_dict)):
         post += str(len(self._compound_ngrams_dict[i])) + ' ' + \
                 str(i) + '-grams; '

      return post[:-2] + '>'

   def _validate( self ):
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
         if not isinstance(att,list):
            raise NonsensicalInputError(att_name+" must be of type list")
         for d in att:
            if not isinstance(d,dict):
               raise NonsensicalInputError(att_name+" items must be of type dict")
            for k,v in d.items():
               if not isinstance(k,NGram):
                  raise NonsensicalInputError(att_name+" keys must be of type NGram")
               if not isinstance(v,dict):
                  raise NonsensicalInputError(att_name+" values must be of type dict")
               for key in v.keys():
                  if not isinstance(key,NGram):
                     raise NonsensicalInputError(att_name+" value keys must be of type NGram")
               validate_values( v.values(), att_name+" value" )

      return True

   @staticmethod
   def _stringify( d ):
      return {Vertical_Interval_Statistics._stringify(k):Vertical_Interval_Statistics._stringify(v) \
                for k,v in d.items()} if isinstance(d,dict) else \
             map(Vertical_Interval_Statistics._stringify,d) if isinstance(d,list) else \
             d if isinstance(d,int) else \
             str(d)

   def to_json( self ):
      # _stringify ensures that the dict is JSON-serializable,
      # since all keys in a JSONObject must be strings
      return json.JSONEncoder().encode(Vertical_Interval_Statistics._stringify(self.__dict__))

   @classmethod
   def from_json( cls,json_string ):
      vis = Vertical_Interval_Statistics()
      # use _stringify since JSONDecoder interprets all strings as unicode.
      d = None
      try:
         d = Vertical_Interval_Statistics._stringify(json.JSONDecoder().decode(json_string))
      except Exception as e:
         raise NonsensicalInputError("JSON data could not be parsed: "+str(e))
      def fix_keys( ngd ):
         return {NGram.make_from_str(k):fix_keys(v) for k,v in ngd.items()} if isinstance(ngd,dict) \
                else ngd
      easy_atts = ["_pieces_analyzed","_simple_interval_dict","_compound_interval_dict"]
      ngram_dicts = ["_compound_ngrams_dict","_simple_ngrams_dict"]
      for att in easy_atts+ngram_dicts:
         if d.get(att) is not None:
            val = d[att] if att in easy_atts else [fix_keys(ngd) for ngd in d[att]]
            setattr(vis,att,val)
         else:
            raise MissingInformationError("The dict supplied is missing the attribute "+att)
      if vis._validate():
         return vis

   def add_interval( self, the_interval, piece_index=0 ):
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

      nbr_pieces = len(self._pieces_analyzed)
      ran = range(nbr_pieces) if nbr_pieces > 0 else [0]
      if -1 == the_interval.direction:
         # For the dictionary of simple intervals
         simple_name = the_interval.semiSimpleName
         simple_name = simple_name[0] + '-' + simple_name[1:]
         if simple_name not in self._simple_interval_dict:
            self._simple_interval_dict[simple_name] = [0,[0 for i in ran]]
         self._simple_interval_dict[simple_name][0] += 1
         self._simple_interval_dict[simple_name][1][piece_index] += 1

         # For the dictionary of compound intervals
         compound_name = the_interval.name
         compound_name = compound_name[0] + '-' + compound_name[1:]
         if compound_name not in self._compound_interval_dict:
            self._compound_interval_dict[compound_name] = [0,[0 for i in ran]]
         self._compound_interval_dict[compound_name][0] += 1
         self._compound_interval_dict[compound_name][1][piece_index] += 1
      # Ascending or unison interval
      else:
         # For the dictionary of simple intervals
         simple_name = the_interval.semiSimpleName
         if simple_name not in self._simple_interval_dict:
            self._simple_interval_dict[simple_name] = [0,[0 for i in ran]]
         self._simple_interval_dict[simple_name][0] += 1
         self._simple_interval_dict[simple_name][1][piece_index] += 1
         # For the dictionary of compound intervals
         compound_name = the_interval.name
         if compound_name not in self._compound_interval_dict:
            self._compound_interval_dict[compound_name] = [0,[0 for i in ran]]
         self._compound_interval_dict[compound_name][0] += 1
         self._compound_interval_dict[compound_name][1][piece_index] += 1
   # end add_interval()

   def get_simple_interval_summary_dict( self ):
      return {k:v[0] for k,v in self._simple_interval_dict.iteritems()}

   def get_compound_interval_summary_dict( self ):
      return {k:v[0] for k,v in self._compound_interval_dict.iteritems()}

   def get_interval_occurrences( self, which_interval, simple_or_compound='simple', piece_index=None ):
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
      def get_all_qualities( species, db, piece_index ):
         post = 0
         for quality in qualities:
            if ( quality + species ) in db:
               if piece_index is None:
                  #then the total number of occurrences
                  post += db[quality+species][0]
               else:
                  post += db[quality+species][1][piece_index]

         return post
      ##

      errorstr = 'Second argument must be either "simple" or "compound"'
      #errorstr = "Vertical_Interval_Statistics.get_interval_occurrences(): " + \
            #"'simple_or_compound' must be set to either 'simple' or 'compound'"

      # Are they ignoring quality? Yes, if the interval is just a digit or if
      # the first character is a direction
      if which_interval.isdigit() or which_interval[0] in directions:
         if 'simple' == simple_or_compound:
            return get_all_qualities( which_interval, self._simple_interval_dict, piece_index )
         elif 'compound' == simple_or_compound:
            return get_all_qualities( which_interval, self._compound_interval_dict, piece_index )
         else:
            raise NonsensicalInputError( errorstr )
      # Otherwise they are paying attention to quality.
      else:
         if 'simple' == simple_or_compound:
            if which_interval in self._simple_interval_dict:
               if piece_index is None:
                  return self._simple_interval_dict[which_interval][0]
               else:
                  return self._simple_interval_dict[which_interval][1][piece_index]
            else:
               return 0
         elif 'compound' == simple_or_compound:
            if which_interval in self._compound_interval_dict:
               if piece_index is None:
                  return self._compound_interval_dict[which_interval][0]
               else:
                  return self._compound_interval_dict[which_interval][1][piece_index]
            else:
               return 0
         else:
            raise NonsensicalInputError( errorstr )
   # end get_interval_occurrences()

   def add_ngram( self, the_ngram, piece_index=0 ):
      '''
      Adds an n-gram to the occurrences information. Tracks quality, since quality
      can always be ignored, but not recovered.
      '''

      # If there isn't yet a dictionary for this 'n' value, then we'll have to
      # make sure there is one.
      while len(self._compound_ngrams_dict) <= the_ngram._n:
         self._compound_ngrams_dict.append( {} )
      while len(self._simple_ngrams_dict) <= the_ngram._n:
         self._simple_ngrams_dict.append( {} )

      nbr_pieces = len(self._pieces_analyzed)
      ran = range(nbr_pieces) if nbr_pieces > 0 else [0]

      # First add the compound version
      index_ngram = Vertical_Interval_Statistics._set_heed_quality(the_ngram, False)
      detail_ngram = Vertical_Interval_Statistics._set_heed_quality(the_ngram, True)
      if index_ngram in self._compound_ngrams_dict[the_ngram._n]:
         if detail_ngram not in self._compound_ngrams_dict[the_ngram._n][index_ngram]:
            self._compound_ngrams_dict[the_ngram._n][index_ngram][detail_ngram] = [0,[0 for i in ran]]
         self._compound_ngrams_dict[the_ngram._n][index_ngram][detail_ngram][0] += 1
         self._compound_ngrams_dict[the_ngram._n][index_ngram][detail_ngram][1][piece_index] += 1
      else:
         self._compound_ngrams_dict[the_ngram._n][index_ngram] = {}
         self._compound_ngrams_dict[the_ngram._n][index_ngram][detail_ngram] = [1,[0 for i in ran]]
         self._compound_ngrams_dict[the_ngram._n][index_ngram][detail_ngram][1][piece_index] = 1

      # Then the simple version
      index_ngram = Vertical_Interval_Statistics._get_simple_version(index_ngram)
      detail_ngram = Vertical_Interval_Statistics._get_simple_version(detail_ngram)
      if index_ngram in self._simple_ngrams_dict[the_ngram._n]:
         if detail_ngram not in self._simple_ngrams_dict[the_ngram._n][index_ngram]:
            self._simple_ngrams_dict[the_ngram._n][index_ngram][detail_ngram] = [0,[0 for i in ran]]
         self._simple_ngrams_dict[the_ngram._n][index_ngram][detail_ngram][0] += 1
         self._simple_ngrams_dict[the_ngram._n][index_ngram][detail_ngram][1][piece_index] += 1
      else:
         self._simple_ngrams_dict[the_ngram._n][index_ngram] = {}
         self._simple_ngrams_dict[the_ngram._n][index_ngram][detail_ngram] = [1,[0 for i in ran]]
         self._simple_ngrams_dict[the_ngram._n][index_ngram][detail_ngram][1][piece_index] = 1

   # end add_ngram()

   def get_ngram_occurrences( self, which_ngram ):
      '''
      Returns the number of occurrences of a particular n-gram. Currently, all
      n-grams are treated as though they have compound intervals.

      The first argument must be an NGram object or the output from either
      NGram.stringVersion or str(NGram) (which calls stringVersion() internally).

      Automatically does or does not track quality, depending on the settings
      of the inputted NGram objects.
      '''
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
      ng_no_hq = Vertical_Interval_Statistics._set_heed_quality(ng.False)
      n = ng.n()
      hq = ng._heed_quality
      the_dict = self.prepare_ngram_output_dict( VIS_Settings(), [n], 'compound'+hq )[n]
      return 0 if the_dict.get(ng) is None else the_dict[ng][0] #replace 0 with piece_index?

   # end get_ngram_occurrences()

   @staticmethod
   def _set_heed_quality( ngram, heed_quality ):
      ret = copy.deepcopy(ngram)
      ret.set_heed_quality(heed_quality)
      return ret

   @staticmethod
   def _get_simple_version( ngram ):
      ng = copy.deepcopy(ngram)
      l = ng._list_of_intervals
      for i in l:
         ns = i.noteStart
         i = interval.Interval(i.semiSimpleName)
         i.noteStart = ns
      ng._simple_or_compound = 'simple'
      ng._string = ng.get_string_version(ng._heed_quality,ng._simple_or_compound)
      return ng

   def determine_list_of_n( self, the_settings, specs, post ):
      if 'n=' in specs:
         # Which values of 'n' did they specify?
         list_of_n = specs[specs.find('n=')+2:]
         list_of_n = list_of_n[:list_of_n.find(' ')]
         list_of_n = sorted(set([int(n) for n in re.findall('(\d+)', list_of_n)]))
         # Check those n values are acceptable/present
         for n in list_of_n:
            # First check we have that index and it's potentially filled with
            # n-gram values
            if n < 2 or n > (len(self._compound_ngrams_dict) - 1):
               # throw it out
               list_of_n.remove( n )
               post += 'Not printing ' + str(n) + '-grams; there are none for that "n" value.\n'
               continue # to avoid the next test
            # Now check if there are actually n-grams in that position. If we
            # analyzed only for 5-grams, for instance, then 2, 3, and 4 will be
            # valid in the n-gram dictionary, but they won't actually hold
            # any n-grams.
            if {} == self._compound_ngrams_dict[n]:
               # throw it out
               list_of_n.remove( n )
               post += 'Not printing ' + str(n) + '-grams; there are none for that "n" value.\n'
      else:
         # Which values of 'n' are present in this V_I_S instance?
         list_of_n = []
         # Check every index between 2 and however many possibilities there are,
         # and see which of these potential n values has n-grams associated.
         for n in xrange( 2, len(self._compound_ngrams_dict) ):
            if {} != self._compound_ngrams_dict[n]:
               list_of_n.append( n )
      #-----

      # What if we end up with no n values?
      if 0 == len(list_of_n):
         raise MissingInformationError( "All of the 'n' values appear to have no n-grams" )

      return list_of_n
   # End determine_list_of_n() -----------------------------

   def extend( self, other_stats ):
      # TODO: document what this method does, what the parameters are, and what everything does
      self_empty = [0,[0 for p in self._pieces_analyzed]]
      other_empty = [0,[0 for p in other_stats._pieces_analyzed]]

      #helper methods for merging the entries of the various dicts involved
      def merger(x,y):
         return merger(0,y) if x is None else \
                merger(x,0) if y is None else \
                x+y

      def merge( a,b ):
         return merge( self_empty, b ) if a is None else \
                merge(a,other_empty) if b is None else \
                map(merger,*[a,b])

      def merge_dicts( x,y ):
         return merge_dicts({},y) if x is None else \
                merge_dicts(x,{}) if y is None else \
                dict((key,merge(x.get(key),y.get(key))) for key in set(x.keys()+y.keys()))

      def merge_lists(x,y):
         return merge_lists({},y) if x is None else \
                (x,{}) if y is None else \
                (x,y)

      def merge_ngram_dicts(x,y):
         return dict((key,merge_dicts(x.get(key),y.get(key))) for key in set(x.keys()+y.keys()))

      def merge_ngram_dict_list( data_dict, other_dict ):
         return [merge_ngram_dicts(a,b) for a,b in map(merge_lists,*[data_dict,other_dict])]

      self._pieces_analyzed += other_stats._pieces_analyzed
      self._simple_interval_dict = merge_dicts(self._simple_interval_dict,other_stats._simple_interval_dict)
      self._compound_interval_dict = merge_dicts(self._compound_interval_dict,other_stats._compound_interval_dict)

      self._compound_ngrams_dict = merge_ngram_dict_list( self._compound_ngrams_dict, other_stats._compound_ngrams_dict )
      self._simple_ngrams_dict = merge_ngram_dict_list( self._simple_ngrams_dict, other_stats._simple_ngrams_dict )
   # End extend() ------------------------------------------

   def prepare_ngram_output_dict( self, the_settings, list_of_n, specs ):
      # TODO: document what this method does, what the parameters are, and what everything does
      # decide simple or compound
      data_dict = None
      if 'simple' in specs or the_settings.get_property( 'simpleOrCompound') == "simple":
         data_dict = self._simple_ngrams_dict
      else:
         data_dict = self._compound_ngrams_dict
      output_dict = None
      if 'quality' in specs or ( the_settings.get_property( 'heedQuality' ) and \
         'noQuality' not in specs ):
         # We do need to include quality
         output_dict = []
         for n in list_of_n:
            keys = []
            values = []
            for ng in data_dict[n].iterkeys():
               keys.extend(data_dict[n][ng].keys())
               values.extend(data_dict[n][ng].values())
            while len(output_dict) < n+1:
               output_dict.append( {} )
            output_dict[n] = dict(zip(keys,values))
      else:
         # We don't need to include quality
         output_dict = [{ngram:[sum([v[0] for v in d[ngram].values()]), \
                       [sum(x) for x in zip(*[v[1] for v in d[ngram].values()])]] \
                       for ngram in d.keys()} for d in data_dict]
      return output_dict
   # End prepare_ngram_output_dict() -----------------------

   def retrogrades( self, the_settings, specs='' ):
     #TODO: refactor the beginning of all the ngram methods
      # (1) Figure out which values of 'n' we should output.
      post = ''
      list_of_n = self.determine_list_of_n(the_settings,specs,post)

      # (2) Decide whether to take 'quality' or 'no_quality'
      output_dict = self.prepare_ngram_output_dict(the_settings,list_of_n,specs)

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
   #end retrogrades()

   def power_law_analysis( self, the_settings ):
      post = ''
      list_of_n = self.determine_list_of_n( the_settings,'',post )

      # (2) Decide whether to take 'quality' or 'no_quality'
      output_dict = self.prepare_ngram_output_dict( the_settings, list_of_n, '' )

      # (3) Sort the dictionary
      sorted_ngrams = []
      # We need to have enough 'n' places in sorted_ngrams to hold the
      # sorted dictionaries.
      for n in xrange(max(list_of_n) + 1):
         sorted_ngrams.append( [] )
      post = ''
      for n in list_of_n:
         sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), key = lambda ng: output_dict[n][ng], reverse=True )
         #we do a power-law regression by instead looking at the logarithmic scales and doing linear regression
         xi = [log(i) for i in range(1,len(sorted_ngrams[n])+1)]
         A = array([ xi, ones(len(xi))])
         y = [log(output_dict[n][ng]) for ng in sorted_ngrams[n]]
         w = linalg.lstsq(A.T,y)[0] #least-squares regression on the data
         #w[0] contains the slope of the line, and we'll just display positive numbers because that's nice.
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
         # TODO: write comments
         non_numeric = re.compile(r'[^\d-]+')
         red = lambda k:non_numeric.sub('',k)
         keys = set(red(k) for k in the_dict.keys())
         keys = [(k,filter(lambda t:red(t[0])==k,the_dict.items())) for k in keys]
         the_dict = {k:[sum(v[0] for K,v in l),map(sum,zip(*[v[1] for K,v in l]))] for k,l in keys}

      # (2) sort the results in the specified way.
      if 'frequency' == the_settings.get_property( 'sortBy' ):
         # Sort by frequency
         if 'ascending' == the_settings.get_property( 'sortOrder' ):
            sorted_intervals = sorted( the_dict.iterkeys(), key= lambda x: the_dict[x] )
         else:
            # Default to 'descending'
            sorted_intervals = sorted( the_dict.iterkeys(), key= lambda x: the_dict[x], reverse=True )
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
         data = [(i,the_dict[interv][0]) for i, interv in enumerate(sorted_intervals)]
         g.setData(data)
         g.setTitle("Intervals in "+join([str(os.path.split(p)[1])+", " for p in self._pieces_analyzed])[:-2])
         g.setTicks('x',[(i+0.4,interv) for i,interv in enumerate(sorted_intervals)])
         g.xTickLabelHorizontalAlignment='center'
         setattr(g,'xTickLabelRotation',45)
         g.setAxisLabel('x','Interval')
         max_height = max([the_dict[interv][0] for interv in sorted_intervals])+1
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
      post = ""
      widths = []
      heading = "Interval"
      width = max([len(str(k)) for k in sorted_intervals]+[len(heading)+2])
      widths.append(width)
      for i, piece in enumerate(self._pieces_analyzed):
         width = max([len(str(the_dict[k][1][i])) for k in sorted_intervals]+[len(os.path.split(piece)[1])+3])
         widths.append(width)
      width_total = max([len(str(the_dict[k][0])) for k in sorted_intervals]+[len("Total")])+2
      widths.append(width_total)
      row = "{0:{1:n}}".format(heading, widths[0])
      for i, piece in enumerate(self._pieces_analyzed):
         row += "{0:{1:n}}".format("# "+os.path.split(piece)[1]+" ", widths[i+1])
      row += "{0:{1:n}}".format("# Total", widths[-1])
      row += "\n"
      post += row
      row = "-"*sum(widths)+"\n"
      post += row
      for interv in sorted_intervals:
         row = "{0:{1:n}}".format(str(interv), widths[0])
         for i, piece in enumerate(self._pieces_analyzed):
            row += "{0:{1:n}}".format(str(the_dict[interv][1][i]), widths[i+1])
         row += "{0:{1:n}}".format(str(the_dict[interv][0]), widths[-1])
         row += "\n"
         post += row
      post += '\n'

      # Done!
      return post
   # end get_formatted_intervals()

   def similarity( self, some_pieces, other_pieces, n, simple_or_compound="compound", heedQuality=False ):
      '''
      Given two lists of indices of self._pieces_analyzed,
      an integer n, and the other obvious settings, computes
      the similarity between the N-Grams in the two samples.
      '''
      settings = VIS_Settings()
      settings.set_property( "heedQuality "+str(heedQuality) )
      the_dict = self.prepare_ngram_output_dict(settings,[n],simple_or_compound)[n]
      total_some = sum(sum(v[1][i] for i in some_pieces) for v in the_dict.values())
      total_other = sum(sum(v[1][i] for i in other_pieces) for v in the_dict.values())
      total_diff = sum(abs((sum(v[1][i] for i in some_pieces)*100)/total_some \
                           -(sum(v[1][i] for i in other_pieces)*100)/total_other) \
                       for v in the_dict.values())
      return 1.0 - float(total_diff)/200

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
         self_dict = self.prepare_ngram_output_dict(the_settings,list_of_n,specs+' noQuality')[n]
         other_dict = other_stats.prepare_ngram_output_dict(the_settings,list_of_n,specs+' noQuality')[n]
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
   # end compare()

   def get_formatted_ngrams( self, the_settings ):
      '''
      Returns a str or music21.graph.Graph object with a nicely-formatted
      representation of the n-gram frequencies recoreded in this
      Vertical_Interval_Statistics() object.

      The argument is a VIS_Settings() object, from where we get
      formatting options.

      Throws NonsensicalInputWarning if one or more of the "showTheseNs" values has
      no associated NGrams occurrences in the relevant statistics database.
      '''

      specs = '' # TODO: remove this temporary thing

      post = ''

      # (1) Figure out which values of 'n' we should output.
      list_of_n = the_settings.get_property('showTheseNs')

      # If they want the total number of n-grams found.
      # TODO: figure out this does, and either add better comments or remove it
      if 'total' in specs:
         t_n_ng = 0
         # Add up the number of triangles for each 'n' value.
         for n in list_of_n:
            # Use 'no_quality' because there will be fewer to go through
            for triangle in self._compound_ngrams_dict[n].values():
               t_n_ng += triangle

         return str(t_n_ng)
      #--------

      # (2) Decide whether to take 'quality' or 'no_quality' and whether we're using
      # simple or compound
      output_dict = self.prepare_ngram_output_dict( the_settings, list_of_n, specs )

      # (2a) Make sure that we have ngrams at the values requested. If not,
      # raise an exception saying which ones were not available.
      error_enns = []
      for enn in list_of_n:
         if enn >= len(output_dict) or \
            output_dict[enn] == {}:
               error_enns.append( enn )

      if 0 < len(error_enns):
         raise NonsensicalInputWarning( "No " + str(error_enns) + "-grams available!" )

      # (3) Sort the dictionary
      sorted_ngrams = []
      # We need to have enough 'n' places in sorted_ngrams to hold the
      # sorted dictionaries.
      for n in xrange(max(list_of_n) + 1):
         sorted_ngrams.append( [] )
      if 'frequency' == the_settings.get_property( 'sortBy' ):
         # Sort the frequencies
         for n in list_of_n:
            if 'ascending' == the_settings.get_property( 'sortOrder' ):
               sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), key = lambda ng: output_dict[n][ng][0] )
            else: # elif 'descending' in specs or 'high to low' in specs:
               # Default to 'descending'
               sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), key = lambda ng: output_dict[n][ng][0], reverse=True )

      # We're now working with flipped_dicts
      else: # elif 'by ngram' in specs or 'by n-gram' in specs:
         # Default to 'by ngram'
         for n in list_of_n:
            if 'descending' == the_settings.get_property( 'sortOrder' ):
               sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), cmp=ngram_sorter, reverse=True )
            else: # elif 'ascending' in specs or 'low to high' in specs:
               # Default to 'ascending'
               sorted_ngrams[n] = sorted( output_dict[n].iterkeys(), cmp=ngram_sorter )

      # (4.1) If some graphs are asked for, prepare them.
      if 'graph' == the_settings.get_property('outputFormat'):
         grapharr = []
         for n in list_of_n:
            g = graph.GraphHistogram(doneAction=None,tickFontSize=12)
            data = [(k,output_dict[n][key][0]) for k, key in enumerate(sorted_ngrams[n])]
            g.setData(data)
            g.setTicks('x',[(k+0.7,key) for k, key in enumerate(sorted_ngrams[n])])
            g.setAxisLabel('x',str(n)+"-Gram")
            g.xTickLabelRotation = 45
            g.xTickLabelVerticalAlignment='top'
            g.xTickLabelHorizontalAlignment='right'
            g.setTitle(str(n)+"-Grams in "+join([str(os.path.split(p)[1])+", " for p in self._pieces_analyzed])[:-2])
            max_height = max([output_dict[n][key][0] for key in sorted_ngrams[n]])+1
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
            ax.set_ylabel('Frequency', fontsize=g.labelFontSize, family=g.fontFamily, rotation='vertical')
            g.done()
            grapharr.append(g)
         post = grapharr

      # (4.2) Else make a nicely formatted list from the results.
      else:
         post = ""
         for k, piece in enumerate(self._pieces_analyzed,start=1):
            post += "p"+str(k)+" = "+os.path.split(piece)[1]+"\n"
         post += "\n"
         for n in list_of_n:
            the_dict = output_dict[n]
            sorted_ngrams = sorted_ngrams[n]
            widths = []
            heading = str(n)+"-Gram"
            width = max([len(str(k)) for k in sorted_ngrams]+[len(heading)])+2
            widths.append(width)
            for i, piece in enumerate(self._pieces_analyzed):
               width = max([len(str(the_dict[k][1][i])) for k in sorted_ngrams]+[len("p"+str(i+1))+3])
               widths.append(width)
            width_total = max([len(str(the_dict[k][0])) for k in sorted_ngrams]+[len("Total")])+2
            widths.append(width_total)
            row = "{0:{1:n}}".format(heading, widths[0])
            for i, piece in enumerate(self._pieces_analyzed,start=1):
               row += "{0:{1:n}}".format("# p"+str(i)+" ", widths[i])
            row += "{0:{1:n}}".format("# Total", widths[-1])
            row += "\n"
            post += row
            row = "-"*sum(widths)+"\n"
            post += row
            for ngram in sorted_ngrams:
               row = "{0:{1:n}}".format(str(ngram), widths[0])
               for i, piece in enumerate(self._pieces_analyzed):
                  row += "{0:{1:n}}".format(str(the_dict[ngram][1][i]), widths[i+1])
               row += "{0:{1:n}}".format(str(the_dict[ngram][0]), widths[-1])
               row += "\n"
               post += row
            post += '\n\n'
         post = post[:-3] #forget the last extra newline

      # Done!
      return post
   # end get_formatted_ngrams()

   def get_formatted_ngram_dict( self, simple_or_compound, *args ):
      '''
      Returns a formatted version of the ngram dictionary.

      Dictionary keys are
      stored internally as NGram objects, but these are difficult to read if,
      for example, you want to print the entire dictionary. This method returns
      a copy of the internally-stored dictionary, where keys are replaced with
      their str() output.

      If you specify an int, a str with a list of int objects, or a list of int
      objects, then only that or those cardinalities will be returned.

      If you specify no arguments, you will get an 'exact' copy of the internal
      ngram dictionary (except keys will be replaced with strings),
      which is a list of dict objects of len() >= 3 , and
      where each cardinality is stored in its position in the list (i.e. 2-grams
      will be stored in get_formatted_ngram_dict('simple')[2] ).
      '''

      if simple_or_compound != 'simple' and simple_or_compound != 'compound':
         raise NonsensicalInputError("simple_or_compound argument must be 'simple' or 'compound")
      # With no argument, we return a copy of the entire dict.
      if args is ():
         the_dict = self._simple_ngrams_dict if simple_or_compound == 'simple' \
                    else self._compound_ngrams_dict
         return self.get_formatted_ngram_dict(simple_or_compound, *range(len(the_dict)))
      elif len(args) == 1 and isinstance(args[0],basestring):
         try:
            new_args = map(int,args.split())
            return self.get_formatted_ngram_dict(simple_or_compound, *new_args)
         except ValueError: #if your string is badly formatted
            raise NonsensicalInputError("string input does not contain a list of ints")
      # With an argument, we have to make a copy of only a specific dict.
      else:
         for n in args:
            if not isinstance(n,int):
               raise NonsensicalInputError("must input a list of int objects")
         big_N = max(args)
         if big_N >= len(self._compound_ngrams_dict):
            raise NonsensicalInputError("There are no N-Grams for N="+str(big_N))
         settings = VIS_Settings()
         try:
            unformatted_dict = self.prepare_ngram_output_dict( settings, \
                             self.determine_list_of_n( settings, "", "" ), "noQuality "+simple_or_compound )
            formatted_dict = [{k:v[0] for k,v in d.iteritems()} \
                             for d in unformatted_dict]
         except MissingInformationError:
            #if there are no ngrams, just return an empty dict.
            return {}
         post = [{str(k):v for k,v in formatted_dict[n].items()} for n in args]
         if len(args) == 1:
            post = post[0]
         return post
   # End get_formatted_ngram_dict()

   def make_summary_score( self, settings, n=None, threshold=None, topX=None ):
      '''
      Returns a Score object with three Part objects. When you run the Score
      through process_score() in the output_LilyPond module, the result is a
      LilyPond file that gives summary results about the triangles recorded by
      this instance of Vertical_Interval_Statistics.

      There are four arguments, three of which are optional:
      - settings : a VIS_Settings object, which is required
      - n : a list of int, specifying which "n" values for "n-gram" are to be
         summarized. If omitted, all "n" values will be displayed.
      - threshold : either...
         - a single int, or
         - a dict whose keys and values are both int
         ... that specifies the number of occurrences required before a triangle
         is displayed in the summary results. This is tested with "equal to or
         greater than."
            If you want to display triangles that occurred more than 100 times
         (i.e. triangles that occur 100 times are not included), then you should
         specify 101.
            If there are multiple "n" values, and you want to specify different
         thresholds for each, use a dict, where the key is the "n" value and the
         value is the threshold.
      - topX : either...
         - a single int, or
         - a dict whose keys and values are both int
         ... that specifies you want to display "the most common X triangles,"
         where X is the int you specify.
            If you want to display the most common 10 triangles, then you should
         specify 10.
            If there are multiple "n" values, and you want to specify different
         most common values for each, use a dict, where the key is the "n" value
         and the value is "X."

      You can combine "threshold" and "topX" to limit further limit the number
      of triangles that appear. For example, if the top five triangles occurred
      50, 40, 15, 15, and 13 times, and you specify a threshold of 20, you will
      only receive the top two triangles because the others occurred less than
      20 times, and do not meet the threshold.

      In the returned Score, index 0 holds a part intended for an upper staff,
      index 1 holds a part intended for a lower staff, and index 2 holds a part
      with LilyPond annotations, aligned with the upper voices.
      '''

      # (1) What are the "n" values we need?
      #-----------------------------------------------------
      list_of_n = []
      if n is not None:
         # We have to parse this list.
         if isinstance( n, int ):
            list_of_n.append( n )
         else:
            # Iterate each 'n' they specified, and see whether we have any
            # triangles with that value.
            for enn in n:
               if 0 < len(self._compound_ngrams_dict[enn]):
                  list_of_n.append( enn )
      else:
         # We have to display all possible "n" values. Iterate each 'n' value
         # we have, and see whether we have any triangels with that value.
         for enn in xrange( 2, len(self._compound_ngrams_dict) ):
            if 0 < len(self._compound_ngrams_dict[enn]):
               list_of_n.append( enn )

      # Make sure we have "n" values to use
      if 0 == len(list_of_n):
         msg = 'make_summary_score(): There are no triangles with the "n" value(s) specified.'
         raise NonsensicalInputError( msg )

      # (2) Initialize
      #-----------------------------------------------------
      # Hold the upper and lower, and the annotation parts that we'll use
      upper_part = stream.Part()
      lower_part = stream.Part()
      lily_part = stream.Part()

      # Set up the analysis part
      lily_part.lily_analysis_voice = True

      # (3) Go through each "n" value separately.
      #-----------------------------------------------------
      for n in list_of_n:
         # Get a sorted list of the triangles
         # NB-1: this is stolen from get_sorted_ngrams() above).
         # NB-2: this will just use heedQuality setting from generation time.
         # TODO: improve handling of heedQuality
         sorted_ngrams = sorted( self._compound_ngrams_dict[n].iterkeys(), \
                                 key = lambda ng: self._compound_ngrams_dict[n][ng], \
                                 reverse=True )

         # Hold "the top" number of most frequent triangles for this "n"
         the_top = None

         # (4) Calculate the_top
         #--------------------------------------------------
         # NB: We need to check the length, or else we may accidentally try to
         # iterate past the number of ngrams we have. If "topX" is greater than
         # the number of ngrams with this "n" then the result is the same
         # behaviour as if there were no "topX."
         if topX is not None:
            # User specified one "topX" for all "n"
            if isinstance( topX, int ):
               # If "topX" wants more triangles than are in this "N", no good.
               if topX > len(self._compound_ngrams_dict[n]):
                  the_top = len(self._compound_ngrams_dict[n])
               else:
                  the_top = topX
            # User specified a "topX" for this "n" specifically
            elif n in topX:
               # If "topX" wants more triangles than are in this "N", no good.
               if topX[n] > len(self._compound_ngrams_dict[n]):
                  the_top = len(self._compound_ngrams_dict[n])
               else:
                  the_top = topX[n]
            # User specified "topX" for some, but not this "n"
            else:
               # Let's just do all of these.
               the_top = len(self._compound_ngrams_dict[n])
         else:
            # There's no "topX" so we'll analyze all of them.
            the_top = len(self._compound_ngrams_dict[n])

         # Hold the threshold for this ngram. The default here is equivalent
         # to no threshold.
         this_threshold = 0

         # (5) Figure out the threshold for this ngram
         #--------------------------------------------------
         if threshold is not None:
            # User specified one "threshold" for all "n"
            if isinstance( threshold, int ):
               this_threshold = threshold
            # User specified a "threshold" for this "n" specifically
            elif n in topX:
               this_threshold = threshold[n]

         # (6) Iterate through the_top
         # This may take us through all the ngrams, but that's okay.
         for i in xrange(the_top):
            # If the occurrences for this ngram is greather than or equal to
            # the threshold, then let's process this ngram!
            if self._compound_ngrams_dict[n][sorted_ngrams[i]] >= this_threshold:
               # Hold the list of vertical and horizontal Interval objects
               # associated with this NGram, respectively.
               ints = sorted_ngrams[i].get_intervals()
               moves = sorted_ngrams[i].get_movements()

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
               lily_note.lily_markup = '^' + make_lily_triangle( str(sorted_ngrams[i]), \
                                                                 print_to_right=str(self._compound_ngrams_dict[n][sorted_ngrams[i]]) )
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
            else:
               continue

      # Finally, make a Score and return it
      return stream.Score( [upper_part, lower_part, lily_part] )
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
