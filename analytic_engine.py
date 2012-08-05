#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         analyticEngine.py
# Purpose:      Holds the intense parts of "vis."
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
# python standard library
from datetime import datetime, timedelta
from decimal import *
# music21
from music21 import interval
from music21 import stream
from music21 import note
# vis
from NGram import NGram
from problems import NonsensicalInputError # TODO: find the right error



#------------------------------------------------------------------------------
def fill_space_between_offsets( start_o, end_o ):
   '''
   Given two float numbers, finds the quarterLength durations required to make
   the two objects viable. Assumes there is a Note starting both at the "start"
   and "end" offset.
   
   Returns a 2-tuplet, where the first index is the required quarterLength of
   the Note at offset start_o, and the second index is a list of the required
   quarterLength values for a series of Rest objects that fill space to the
   end_o. Ideally the list will be empty and no Rest objects will be required.
   
   The algorithm tries to fill the entire offset range with a single Note that
   starts at start_o, up to a maximum quarterLength of 4.0 (to avoid LilyPond
   duration representations longer than one character). The algorithm prefers
   multiple durations over a single dotted duration.
   '''
   
   # This method tells the largest quarterLength less than 4.0, that is a valid
   # quarterLength we could use as a Note/Rest value.
   def highest_valid_qL( rem ):
      # Holds the valid quarterLength durations from whole note to 256th.
      list_of_durations = [2.0, 1.0, 0.5,  0.25, 0.125, 0.0625, 0.03125, \
         0.015625, 0.0]
      # Easy terminal condition
      if rem in list_of_durations:
         return rem
      # Otherwise, we have to look around
      for dur in list_of_durations:
         if dur < rem:
            return dur
   #--------
   
   start_o = float(start_o)
   end_o = float(end_o)
   
   # This method recursively solves the problem. The rest of the outer method
   # serves only to start the_solver() and to format its output.
   # 
   # The parameter name means "quarterLength that remains to be dealt with" or
   # something else ridiculously obvious and long.
   def the_solver( qL_remains ):
      if 4.0 == qL_remains:
         # Terminal condition, just return!
         return [ 4.0 ]
      elif 4.0 > qL_remains >= 0.0:
         if 0.015625 > qL_remains:
            # give up... ?
            return [ qL_remains ]
         else:
            possible_finish = highest_valid_qL( qL_remains )
            if possible_finish == qL_remains:
               return [ qL_remains ]
            else:
               return [ possible_finish ] + the_solver( qL_remains - possible_finish )
      elif qL_remains > 4.0 :
         return [ 4.0 ] + the_solver( qL_remains - 4.0 )
      else:
         # TODO: this isn't the right exception
         raise NonsensicalInputError( 'How\'d we end up with quarterLength ' + str(qL_remains) + ' remaining?' )
   #-----
   
   result = the_solver( end_o - start_o )
   return (result[0], result[1:])
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
def make_lily_triangle( ngram ):
   '''
   Given the str for an n-gram with arbitrary 'n', writes the LilyPond "markup"
   block required to make a well-formed triangle around the well-formatted
   numbers that make up the n-gram's intervals.
   
   Returns a str like this:
   "\markup{ <<ngram_here>> }"
   ... so you must prepend your own positional indicator.
   
   NB: Currently only works for 2-grams.
   '''
   
   # Find the locations of the two spaces in the n-gram representation.
   first_space = ngram.find(' ')
   second_space = first_space + ngram[first_space+1:].find(' ') + 1
   
   # Calculate the number of characters in thie ngrams width
   char_len = len(ngram) - 2 # 2 spaces!
   
   # Start the markup
   post = '\\markup{ \combine \concat{ \\teeny{ "'
   
   # Add the first interval
   post += ngram[:first_space]
   
   # Make the horizontal interval lower
   post += '" \\lower #1 "'
   
   # Add the horizontal interval
   post += ngram[first_space+1:second_space]
   
   # Space after horiz. and 2nd vert.
   post += '" "'
   
   # Add the second vertical interval
   post += ngram[second_space+1:]
   
   # Close the path and add the triangle ------------------
   post += '"}} \path #0.1 #\'((moveto -1 1.25) '
   # Middle-bottom triangle point
   if char_len > 4: # for four-sided triangles...
      # This goes down to the left-bottom triangle node.
      post += '(lineto 1.0 -1.5) '
      # This is the right-bottom triangle node. It's 2.0 (x-wise) before the
      # top-right triangle node, just as the bottom-left node is 2.0 from the
      # top-left triangle node.
      x_pos = round( ((float(char_len) + 0.3) - 2.0), 2 )
      post += '(lineto ' + str(x_pos) + ' -1.5) '
   else: # for three-sided triangles...
      x_pos = round(((float(char_len) + 1.0)/2.0)-1.0, 2)
      post += '(lineto ' + str(x_pos) + ' -2.0) '
   # Right-most triangle point
   # NB: This is 3.3 for 3 characters, 4.3 for 4 characters, etc.
   post += '(lineto ' + str(char_len) + '.3 1.25) (closepath))}'
   
   return post
# End make_lily_triangle() ----------------------------------------------------



#------------------------------------------------------------------------------
def vis_these_parts( these_parts, the_settings, the_statistics ):
   '''
   Given a list of two :class:`music21.stream.Part` objects, an visSettings
   object, and a VerticalIntervalStatistics object, calculate the n-grams
   specified in the settings object, then put the statistics in the statistics
   object.

   Note that the parts must be specified so the higher part has index 0, and
   the lower part has index 1.
   
   Returns a 2-tuplet with a float that is the number of seconds the analysis,
   and a list of stream.Part objects that represent a way for LilyPond to
   output analytic n-gram symbols correctly. If the VIS_Settings instance is
   not set to produce a labeled score, this list will be empty.
   '''
   
   # Parameters:
   # these_parts : a two-element list of the parts to analyze, with the "upper part" first
   # the_settings : a VIS_Settings instance
   # the_statistics : a Vertical_Interval_Statistics instance
   
   ## Helper Methods ---------------------------------------
   # TODO: see whether we need these or not
   ## Is 'thing' a Note?
   #def is_note( thing ):
      #if isinstance( thing, note.Note ):
         #return True
      #else:
         #return False
   
   # Is 'thing' a Rest?
   def is_rest( thing ):
      if isinstance( thing, note.Rest ):
         return True
      else:
         return False
   
   ## Is 'thing' a Note, Rest, or neither?
   #def is_note_or_rest( thing ):
      #if isinstance( thing, note.Note) or isinstance( thing, note.Rest ):
         #return True
      #else:
         #return False
   ## End Helper Methods -----------------------------------
   
   # Initialize -------------------------------------------
   # Note the starting time of the analysis
   analysis_start_time = datetime.now()
   
   # The parts we're analyzing
   lower_part = these_parts[1].flat.notesAndRests
   higher_part = these_parts[0].flat.notesAndRests
   
   # The current index we're checking
   current_lower_index = 0
   current_higher_index = 0
   
   # The highest indices.
   len_lower = len(lower_part)
   len_higher = len(higher_part)
   
   # The interval by which to count every event. That is, Note/Rest objects
   # will be counted every offset_interval.
   offset_interval = the_settings.get_property( 'offsetBetweenInterval' )
   
   # Keep track of which offsets we've checked. We'll take the lower offset of
   # the first notes in the streams as the starting point. We increment this
   # only when we record something at an offset. This will help us be sure
   # we don't accidentally go backwards.
   current_offset = min( lower_part[0].offset, higher_part[0].offset )
   
   # Hold a list of all previously-recorded moments--whether an actual Interval
   # or just a Note/Rest, or even a Rest/Rest.
   interval_history = []
   
   # Hold a list of int objects that are the 'n' values in 'n-gram' that we're
   # supposed to be looking for.
   find_these_ns = the_settings.get_property( 'lookForTheseNs' )
   
   # Go through all the things!
   while current_lower_index <= len_lower and current_higher_index <= len_higher:
		# Make sure the current indices aren't past the end of the parts.
		if current_lower_index >= len_lower:
			current_lower_index = len_lower - 1
		if current_higher_index >= len_higher:
			current_higher_index = len_higher - 1
		
		# Sanity check. If we've already recorded something *past* the current
		# objects' offsets, then we're moving backwards.
		# TODO: handle this intelligently (raise exception)
		if current_offset >= lower_part[current_lower_index].offset and \
			current_offset >= higher_part[current_higher_index].offset and \
			current_offset != 0.0:
			# DEBUGGING
			print( 'panic! current_offset is ' + str(current_offset) + ' but higher is ' + str(higher_part[current_higher_index].offset) + ' and lower is ' +  str(lower_part[current_lower_index].offset) )
			# END DEBUGGING
		
		# Make sure we have the right objects. --------------
		# This protects against situations where, for instance, a long note is
		# held through many notes in the other part. This will keep us on the
		# right note.
		
		# If the current stream objects don't have the same offset, we should set
		# the stream with the higher offset to use the previous object.
		if lower_part[current_lower_index].offset != \
				higher_part[current_higher_index].offset:
			# Which object has the greater offset?
			greater_offset = max( higher_part[current_higher_index].offset, \
									    lower_part[current_lower_index].offset )
			if greater_offset == higher_part[curent_higher_index].offset:
				current_higher_index -= 1
			else: # must be the lower part with the greater offset
				current_lower_index -= 1
		#-----
		
		# Decide whether to add the inteval -----------------
		# These conditions must be true for us to bother counting this interval.
		
		# We'll use this to keep track of whether we should continue processing
		# these particular indices.
		contin = False
		
		# Q: Is the current thing at an offset we're counting?
		# We'll use this to try different yes-counting offsets, to see if we can
		# match with the offset of the current thing.
		potential_new_offset = current_offset
		
		# The new thing will be registered at the greater of the two offsets of
		# the objects we currently have.
		# NB: This *must* be recalculated, because the objects may have changed
		# since the previous time it was calculated.
		greater_offset = max( higher_part[current_higher_index].offset, \
									 lower_part[current_lower_index].offset )
		
		# We start at current_offset, which is still set to the most recently
		# recorded interval. Then we'll increment by offset_interval until either
		# we hit the offset at which the current event would be registered, or
		# until we pass that offset, which means we won't hit it.
		# NB: We need to keep potential_new_offset, because it records the
		# yes-record offset either at or next after the greater_offset.
		while potential_new_offset <= greater_offset:
			if potential_new_offset == greater_offset:
				contin = True
				break
			else:
				potential_new_offset += offset_interval
		#-----
		
		# Does this event continue past the next offset we're supposed to measure?
		# NB: We only need to ask this if we aren't already continuing.
		if not contin:
			# We'll see if the offset of *both* the next events in our streams are
			# greater than the "potential_new_offset". If we reach this code, the
			# "potential_new_offset" will hold the next yes-record offset after the
			# current event.
			if higher_part[current_higher_index+1].offset > potential_new_offset and \
					lower_part[current_lower_index+1].offset > potential_new_offset:
				contin = True
		#-----
		
		# Process this moment for intervals. ----------------
		if contin:
			# Does one or do both parts have a Rest or have Rests?
			if is_rest( higher_part[current_higher_index] ) or \
					is_rest( lower_part[current_lower_index] ):
				# It doesn't really matter which part; we just have to add this as
				# a "this moment has a Rest" moment.
				interval_history.append( 'rest' )
				contin = False
			# Otherwise, we're "go" for adding this as an Interval.
			else:
				this_interval = interval.Interval( higher_part[current_higher_index], \
				                                   lower_part[current_lower_index] )
				# Is this the first Interval, or is it the same as the previous?
				if 0 == len(interval_history) or \
						this_interval == interval_history[-1]:
					# Then we should stop processing it.
					contin = False
				else:
					# This is a new thing, so we should keep processing.
					the_statistics.add_interval( this_interval )
					interval_histroy.append( this_interval )
					# Update the current offset, because we added a new thing.
					current_offset = max( higher_part[current_higher_index].offset, \
					                      lower_part[current_lower_index].offset )
		#--------
		
		# Process this moment for triangles. ----------------
		if contin:
			# For all the 'n' values we're looking for, we need to first make sure
			# there are enough pre-recorded things in the interval_history, then
			# make sure there are enough that are Interval objects and not the
			# str 'rest' that means a Rest.
			for n in find_these_ns:
				# Is the interval history long enough?
				if len(interval_history) < n:
					continue
				
				# Hold a list of intervals that will make up this n-gram.
				list_of_intervals = []
				
				# Are there enough non-"rest" elements to make an n-gram?
				enough_non_rests = True
				
				# Are there enough non-"rest" elements?
				# We'll go through each of the previous n-1 elements, and if none
				# of them is a "rest" then we can build an n-gram with this 'n'.
				# We only need n-1 elements from the interval_history because we're
				# getting an additional interval from this_interval.
				for previous_thing in xrange( 1, n ):
					if 'rest' == interval_history[(-1 * previous_thing)]:
						enough_non_rests = False
						break
					else:
						# If there are no rests, we can add this interval to the list
						# of things that will be passed to the NGram() constructor.
						list_of_intervals.append( previous_thing )
				
				# Finish making the n-gram
				if enough_non_rests:
					# Append the final interval (the current one).
					list_of_intervals.append( this_interval )
					
					# Make an NGram object, then add it to the statistics database.
					this_ngram = NGram( list_of_intervals, \
					                    the_settings.get_property( 'heedQuality' ), \
					                    the_settings.get_property( 'simpleOrCompound' ) )
					the_statistics.add_ngram( this_ngram )
		#--------
		
		# Annotate the score for LilyPond.
		# TODO: write this
		
		# Finally, increment the current index.
		current_lower_index += 1
		current_higher_index += 1
	# End "while" loop -------------------------------------
   
   
   # -we'll need to keep track of which offsets we've checked
   # 1.) Go through each "thing"
   # 		1) take .notesAndRests
   # 		2) are the offsets the same? YES
   # 		3) are the offsets different? YES (with the lower-offset Note/Rest and the previous Note/Rest of the other part)
   # 2.) Decide whether to add it to the list of intervals.
   # 		-is the current thing *at* an offset we're checking? YES
   # 		-is the next thing past the next offset we're checking? YES
   # 		-is this thing the same as the previous thing? NO
   # 3.) If it's a viable interval, decide whether to add it to the list of n-grams.
   # 		-are there enough intervals in a row to build the n-gram? YES
   # 4.) If we're annotating the score, add the appropriate LilyPond annotations.
   
   
   
   
   
   # Note the ending time of the analysis...
   # TODO: come up with a better timing thing
   # NOTE: list_of_lilypond_parts is a list of all the parts that contain spacing Note objects with annotations.
   duration = datetime.now() - analysis_start_time
   duration = float( str(duration.seconds) + '.' + str(duration.microseconds) )
   return ( duration, list_of_lilypond_parts )
# End vis_these_parts() -------------------------------------------------------
