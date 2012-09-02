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
from music21 import interval, stream, note, chord
# vis
from NGram import NGram
from problems import NonsensicalInputError



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
         raise NonsensicalInputError( 'Impossible quarterLength remaining: ' + str(qL_remains) )
   #-----

   result = the_solver( end_o - start_o )
   return (result[0], result[1:])
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
def make_lily_triangle( ngram, which_colour=None, print_to_right=None ):
   '''
   Given the str for an n-gram with arbitrary 'n', writes the LilyPond "markup"
   block required to make a well-formed triangle around the well-formatted
   numbers that make up the n-gram's intervals.

   Returns a str like this:
   "\markup{ <<ngram_here>> }"
   ... so you must prepend your own positional indicator.

   Optional Keyword Arguments:
   ---------------------------
   - which_colour : Should be the LilyPond command for the colour of everything
                    that follows.
   - print_to_right : This is a str appended to the right of the ngram.

   NB: Currently only works for 2-grams.
   '''

   # Find the locations of the two spaces in the n-gram representation.
   first_space = ngram.find(' ')
   second_space = first_space + ngram[first_space+1:].find(' ') + 1

   # Calculate the number of characters in thie ngrams width
   char_len = len(ngram) - 2 # 2 spaces!

   # Start the markup
   post = '\\markup{ '

   # Append the colour
   if which_colour is not None:
      post += '\\with-color ' + which_colour + ' '

   # Continue the beginning
   post += '\combine \concat{ \\teeny{ "'

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

   # Close the ngram
   post += '"} '

   # Append the print_to_right str
   if print_to_right is not None:
      post += ' "   ' + print_to_right + '" } '
   else:
      post += '} '

   # Draw the triangle
   post += '\path #0.1 #\'((moveto -1 1.25) '
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
def make_basso_seguente( from_this ):
   '''
   Given a score with multiple parts, this method returns a new part that
   represents the lowest sounding pitch at all times.

   For a good on-score demonstration:
   >>> from music21 import *
   >>> from analytic_engine import make_basso_seguente
   >>> z = converter.parse( 'test_corpus/Kyrie.krn' )
   >>> ell = make_basso_seguente( z )
   >>> z.insertAtNativeOffset( ell )
   >>> z.show()
   '''

   # Hold the basso seguente part
   bs = stream.Part()

   # "Chordify" the score, so it's easy to traverse every time the "chord"
   # changes.
   from_this = from_this.chordify( addTies = False )

   # Flatten Measure objects
   from_this = from_this.flat

   # Go through every item. If it's a Chord, get the lowest Note object and add
   # it to the new Part.
   for thing in from_this:
      if isinstance( thing, chord.Chord ):
         # Make a new Note with the right duration
         this_note = note.Note( thing.bass(), quarterLength=thing.quarterLength )

         # Send ignoreSort=True so that we don't sort every time something is
         # added, only once.
         bs.insert( thing.offset, this_note, ignoreSort = True )

   # Then sort the new Part.
   bs.sort()

   # Done!
   return bs

# End make_basso_seguente() ---------------------------------------------------



#------------------------------------------------------------------------------
def vis_these_parts( these_parts, the_settings, the_statistics, \
                     targeted_output = None ):
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
   # targeted_output : the instructions given to (the GUI version of) analyze_this()

   # Helper Methods ---------------------------------------
   # Is 'thing' a Rest?
   def is_rest( thing ):
      return isinstance( thing, note.Rest )

   # Rounds n to the nearest "precision". For instance...
   # round_to( 12.6, 0.5 ) ==> 12.5
   #
   # My thanks to the Internet:
   # http://stackoverflow.com/questions/4265546/python-round-to-nearest-05
   def round_to( n, precision ):
      correction = 0.5 if n >= 0 else -0.5
      return int( n / precision + correction ) * precision
   # End Helper Methods -----------------------------------

   # Initialize --------------------------------------------
   # Note the starting time of the analysis
   analysis_start_time = datetime.now()

   # Parse targeted_output ---------------------------------
   # Hold instructions from 'only annotate'
   list_to_annotate = []

   # Hold instructions from 'only colour'
   list_to_colour = []

   # Hold the colour instruction
   annotation_colour = None

   # Go through all the instructions
   if targeted_output is not None:
      # Do we have instructions on which voices to analyze?
      for instruction in targeted_output:
         if 'only annotate' == instruction[0]:
            list_to_annotate.append( instruction[1] )
         elif 'only colour' == instruction[0]:
            list_to_colour.append( instruction[1] )
         elif 'annotate colour' == instruction[0]:
            annotation_colour = instruction[1]
   # End parsing of targeted_output ------------------------

   # Prepare the parts we're analyzing ---------------------
   # NOTE: If we decide to allow Chord objects in the future, this step is
   # essentially not useful. In that case, we should revert to .notesAndRests
   temp_high_part = these_parts[0].flat
   temp_low_part = these_parts[1].flat
   higher_part = stream.Part()
   lower_part = stream.Part()

   # Seems like the best way to get only the objects we want is to filter both
   # of the parts, object by object
   for obj in temp_high_part:
      if isinstance( obj, note.Note ) or \
         isinstance( obj, note.Rest ):
            higher_part.insert( obj, ignoreSort=True )

   for obj in temp_low_part:
      if isinstance( obj, note.Note ) or \
         isinstance( obj, note.Rest ):
            lower_part.insert( obj, ignoreSort=True )

   higher_part.sort()
   lower_part.sort()

   # End of parts preparation ------------------------------

   # The current index we're checking
   current_lower_index = 0
   current_higher_index = 0

   # The highest indices.
   len_lower = len(lower_part)
   len_higher = len(higher_part)

   # The interval by which to count every event. That is, Note/Rest objects
   # will be counted every offset_interval.
   offset_interval = the_settings.get_property( 'offsetBetweenInterval' )

   # Record the offset of the most recently added interval.
   current_offset = None

   # Hold a list of all previously-recorded moments--whether an actual Interval
   # or just a Note/Rest, or even a Rest/Rest.
   interval_history = []

   # Hold a list of int objects that are the 'n' values in 'n-gram' that we're
   # supposed to be looking for.
   find_these_ns = the_settings.get_property( 'lookForTheseNs' )

   # Hold all the parts that contain LilyPond annotations. There will be one
   # Part object in this list for every 'n' value we're looking for.
   #list_of_lilypond_parts = []
   list_of_lilypond_parts = stream.Part()
   list_of_lilypond_parts.lily_analysis_voice = True

   # Go through all the things!
   # The highest valid index is one less than the len().
   while current_lower_index < len_lower or current_higher_index < len_higher:
      # Make sure the current indices aren't past the end of the parts.
      if current_lower_index >= len_lower:
         #current_lower_index = len_lower - 1
         current_lower_index -= 1
      if current_higher_index >= len_higher:
         #current_higher_index = len_higher - 1
         current_higher_index -= 1

      # Sanity check. If we've already recorded something *past* the current
      # objects' offsets, then we're moving backwards.
      # TODO: handle this intelligently (raise exception)
      if current_offset >= lower_part[current_lower_index].offset and \
         current_offset >= higher_part[current_higher_index].offset:
         pass

      # Make sure we have the right objects. --------------
      # This protects against situations where, for instance, a long note is
      # held through many notes in the other part. This will keep us on the
      # right note. We know there's a problem if the current objects don't
      # have the same offset.

      # If the current stream objects don't have the same offset, we should set
      # the stream with the higher offset to use the previous object.

      # If the offsets aren't the same...
      if lower_part[current_lower_index].offset != \
            higher_part[current_higher_index].offset:

         # If the objects are the last in their streams...
         if current_lower_index == ( len_lower - 1 ) and \
               current_higher_index == ( len_higher - 1 ):
            pass
         # If the higher object is last in its stream...
         elif current_higher_index == ( len_higher - 1 ):
            # We can only decrement the higher stream, if it's what occurs later.
            if higher_part[current_higher_index].offset > \
                  lower_part[current_lower_index].offset:
               current_higher_index -= 1
         # If the lower object is last in its stream...
         elif current_lower_index == ( len_lower - 1 ):
            # We can only decrement the lower stream, if it's what occurs later.
            if lower_part[current_lower_index].offset > \
                  higher_part[current_higher_index].offset:
               current_lower_index -= 1
         # Neither object is last in its stream...
         else:
            # Which object has the greater offset?
            if higher_part[current_higher_index].offset > \
                  lower_part[current_lower_index].offset:
               # Must be the higher part with the greater offset.
               current_higher_index -= 1
            else:
               # Must be the lower part with the greater offset.
               current_lower_index -= 1

      # Decide whether to add the interval -----------------
      # These conditions must be true for us to bother counting this interval.

      # We'll use this to keep track of whether we should continue processing
      # these particular indices.
      contin = False

      # Q: Is the current thing at an offset we're counting?
      # We'll use this to try different yes-counting offsets, to see if we can
      # match with the offset of the current thing.
      if current_offset is None:
         # We'll start at the start of the streams.
         potential_new_offset = min( higher_part[0].offset, lower_part[0].offset )
      else:
         # Round current_offset to the nearest yes-counting interval.
         potential_new_offset = round_to( current_offset, offset_interval )
         # If potential_new_offset is greater than current_offset, we may have
         # missed something, so go back!
         if potential_new_offset > current_offset:
            potential_new_offset -= offset_interval

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

      # Does this event continue past the next offset we're supposed to measure?
      # NB: We only need to ask this if we aren't already continuing.
      if not contin:
         # We'll see if the offset of *both* the next events in our streams are
         # greater than the "potential_new_offset". If we reach this code, the
         # "potential_new_offset" will hold the next yes-record offset after the
         # current event.

         # First see whether we're at the end of the streams.
         if current_higher_index == len_higher - 1 or \
               current_lower_index == len_lower - 1:
            # Then we'll have to use the quarterLength duration. We don't want
            # to use this unless we have to, because this kind of arithmetic
            # could lead to errors.
            end_of_higher = higher_part[current_higher_index].offset + \
                            higher_part[current_higher_index].quarterLength
            end_of_lower = lower_part[current_lower_index].offset + \
                           lower_part[current_lower_index].quarterLength

            # Now do the test
            if end_of_lower > potential_new_offset and \
                  end_of_higher > potential_new_offset:
               contin = True
         else:
            # We're not at the end of the streams, so we can test without
            # arithmetic.
            if higher_part[current_higher_index+1].offset > potential_new_offset and \
                  lower_part[current_lower_index+1].offset > potential_new_offset:
               contin = True

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
            this_interval = interval.Interval( lower_part[current_lower_index], \
                                               higher_part[current_higher_index] )
            # Set the offset to the higher of the objects it's made from
            this_interval.offset = max( lower_part[current_lower_index].offset, \
                                        higher_part[current_higher_index].offset )
            # Is this the first Interval, or is it the same as the previous?
            if 0 < len(interval_history) and \
                  this_interval == interval_history[-1]:
               # This means it's the same interval, but does it have the same notes?
               if this_interval.noteStart.nameWithOctave == interval_history[-1].noteStart.nameWithOctave:
                  # This is the same
                  contin = False
            # else # This is a new thing, so we should keep processing.
            if contin:
               the_statistics.add_interval( this_interval )
               interval_history.append( this_interval )
               # Update the current offset, because we added a new thing.
               current_offset = max( higher_part[current_higher_index].offset, \
                                     lower_part[current_lower_index].offset )

      # Process this moment for triangles. ----------------
      # Hold the NGram object we'll create.
      this_ngram = None
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
            for i in xrange( ( -1 * n ), 0 ):
               previous_thing = interval_history[i]
               if 'rest' == previous_thing:
                  enough_non_rests = False
                  break
               else:
                  # If there are no rests, we can add this interval to the list
                  # of things that will be passed to the NGram() constructor.
                  list_of_intervals.append( previous_thing )

            # Finish making the n-gram
            if enough_non_rests:
               # Make an NGram object, then add it to the statistics database.
               this_ngram = NGram( list_of_intervals, \
                                   the_settings.get_property( 'heedQuality' ), \
                                   the_settings.get_property( 'simpleOrCompound' ) )
               the_statistics.add_ngram( this_ngram )
            else:
               # There aren't enough non-rests, so we won't be putting a
               # triangle here. We need to set 'contin' to False so that we
               # won't try to add a LilyPond annotation.
               contin = False

      # Annotate the score for LilyPond.
      if contin:
         # Get the str representation of this n-gram.
         str_this_ngram = str(this_ngram)

         # If there are restrictions on what to annotate...
         if 0 < len(list_to_annotate):
            # If this isn't one of the things to annotate...
            if str_this_ngram not in list_to_annotate:
               # Then move on to the next ngram
               continue

         # If this is the first annotation going into the score.
         if 0 == len(list_of_lilypond_parts):
            # Maybe the annotations don't start at the beginning of the Part, so
            # let's fill the empty space with Rest objects. Remember, if we get
            # here, then current_offset has the offset of the just-added object.
            if current_offset > 0.0:
               list_of_needed_qLs = fill_space_between_offsets( 0.0, current_offset )
               z = note.Rest( quarterLength = list_of_needed_qLs[0] )
               list_of_lilypond_parts.append( z )
               for needed_qL in list_of_needed_qLs[1]:
                  z = note.Rest( quarterLength = needed_qL )
                  list_of_lilypond_parts.append( z )

            # Figure out whether we need to colour this ngram
            this_colour = None
            if 0 < len(list_to_colour) and str_this_ngram in list_to_colour:
               # We must colour this ngram
               this_colour = annotation_colour

            # Make a new Note in the lily_for_this_n stream, with the same offset as
            # the start of this n-gram.
            this_n_lily = note.Note( 'C4' ) # could be any pitch
            this_n_lily.lily_markup = '^' + make_lily_triangle( str_this_ngram, this_colour )
            #lily_for_this_n[-1].lily_markup = '^' + make_lily_triangle( str_this_ngram )

            # Trouble is, I also have to fit in the right number of
            # measures and filler material, or it'll be too
            # difficult for output_LilyPond to invent this stuff.
            list_of_lilypond_parts.insert( current_offset, this_n_lily )

         # If this is not the first annotation going into the score.
         else:
            # Figure out what's required to fill the space between the previous and this annotation
            list_of_needed_qLs = fill_space_between_offsets( list_of_lilypond_parts[-1].offset, current_offset )

            # Set the previous annotation to the right quarterLength
            list_of_lilypond_parts[-1].quarterLength = list_of_needed_qLs[0]

            # Fill the remaining required space with Rest objects
            for needed_qL in list_of_needed_qLs[1]:
               z = note.Rest( quarterLength = needed_qL )
               list_of_lilypond_parts.append( z )

            # Figure out which colour we need
            this_colour = None
            if 0 < len(list_to_colour) and str_this_ngram in list_to_colour:
               # We must colour this ngram
               this_colour = annotation_colour
            elif 0 == len(list_to_colour):
               # We must colour all ngrams
               this_colour = annotation_colour
            # else:
            #     this_colour = None, because there are ngrams to colour, but
            #     this ngram isn't one of them.

            # Put in the correct label.
            list_of_lilypond_parts[-1].lily_markup = '^' + make_lily_triangle( str_this_ngram, this_colour )

            # Make a new Note in the lily_for_this_n stream.
            this_n_lily = note.Note( 'C4' ) # could be any pitch

            # Trouble is, I also have to fit in the right number of
            # measures and filler material, or it'll be too
            # difficult for output_LilyPond to invent this stuff.
            list_of_lilypond_parts.insert( current_offset, this_n_lily )
      # End LilyPond section ------------------------------

      # TODO: update this section, and analyze_this(), to accept a list of
      # Part objects for LilyPond annotation, rather than a single Part object
      # that is the only possible annotation.
      # NB: There should be one part here for every 'n' value we looked for.
      #list_of_lilypond_parts.append( lily_part )

      # Finally, increment the current index.
      current_lower_index += 1
      current_higher_index += 1
   # End "while" loop -------------------------------------

   # Note the ending time of the analysis...
   # TODO: come up with a better timing thing
   duration = datetime.now() - analysis_start_time
   duration = float( str(duration.seconds) + '.' + str(duration.microseconds) )
   return ( duration, list_of_lilypond_parts )
# End vis_these_parts() -------------------------------------------------------
