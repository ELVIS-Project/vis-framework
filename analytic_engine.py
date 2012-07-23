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
   # NB: I broke this into a function so I can use a unit test on it.
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
   
   # Helper Methods ---------------------------------------
   # Is 'thing' a Note?
   def is_note( thing ):
      if isinstance( thing, note.Note ):
         return True
      else:
         return False
   
   # Is 'thing' a Rest?
   def is_rest( thing ):
      if isinstance( thing, note.Rest ):
         return True
      else:
         return False
   
   # Is 'thing' a Note, Rest, or neither?
   def is_note_or_rest( thing ):
      if isinstance( thing, note.Note) or isinstance( thing, note.Rest ):
         return True
      else:
         return False
   # End Helper Methods -----------------------------------
   
   # Initialize -------------------------------------------
   # NB: These things will not change when we look for different 'n' values.
   # Note the starting time of the analysis
   analysis_start_time = datetime.now()
   
   # Keep track of whether this is the first 'n' we're looking for; we should
   # only add intervals to the Vertical_Interval_Statistics object if this is
   # the first time, otherwise we'll get len(list_of_n) times as many intervals
   # reported as are actually in the piece
   on_the_first_n = True
   
   # This records whether we should bother to produce new stream with LilyPond
   # annotations. This would help save time.
   produce_lilypond = the_settings.get_property( 'produceLabeledScore' )
   list_of_lilypond_parts = []
   
   # The quarterLength at which we should record intervals and n-grams. The
   # default is 0.5, which means intervals and n-grams will be recorded on
   # the eighth-note beat.
   offset_interval = Decimal( str(the_settings.get_property( 'offsetBetweenInterval' )) )
   
   # Repeat the whole process with every specified value of n.
   for n in the_settings.get_property('lookForTheseNs'):
      # Create a new stream.Part just for holding LilyPond annotations for this
      # 'n' value.
      if produce_lilypond:
         lily_for_this_n = stream.Part()
         lily_for_this_n.lily_analysis_voice = True
         list_of_lilypond_parts.append( lily_for_this_n )
      
      # Now we'll take just the notes and rests. I don't want to use 
      # .notesAndRests because then I get chords and None and other garbage.
      #hfn = these_parts[0].notesAndRests
      #lfn = these_parts[1].notesAndRests
      hfn, lfn = stream.Stream(), stream.Stream()
      for thing in these_parts[0].flat:
         if is_note_or_rest( thing ):
            hfn.append( thing )
         ## DEBUGGING
         #else:
            #print( "Not a note or rest, not in hfn: " + str(type(thing)) )
         ## END DEBUGGING
      #
      for thing in these_parts[1].flat:
         if is_note_or_rest( thing ):
            lfn.append( thing )
         ## DEBUGGING
         #else:
            #print( "Not a note or rest, not in hfn: " + str(type(thing)) )
         ## END DEBUGGING
      #
      
      # Initialize ----------------------------------------
      # NB: These things must be refreshed when we look for a different 'n'.
      
      # So we know where the end is.
      highest_offset = Decimal( str(max(lfn.highestOffset, hfn.highestOffset)) )
      
      # Start at the beginning of this passage. But we actually have to set the
      # offset to 0.001 *before* the lowest offset, so that when the "sanity
      # check" applies, we'll be "upgraded" to the actual lowest offset.
      current_offset = Decimal( str(min(lfn.lowestOffset, hfn.lowestOffset)) ) - Decimal('0.001')
      
      # These hold the most recent Note/Rest in their respective
      # voice. We can't say "current" because it implies the offset of
      # most_recent_high is the same as current_offset, which may not be true
      # if, for example, there is a long Note/Rest.
      most_recent_high, most_recent_low = None, None
      
      # These hold all the previous Note/Rest objects in their respective
      # voices. It's how we build n-grams, with mostRecentX and objects from
      # these lists.
      previous_highs, previous_lows = [], []
      
      # These hold the offset of the next event in their respective voices. But
      # for now, we don't know where that will be, so we have to set them to 
      # the starting offset.
      next_low_event, next_high_event = current_offset, current_offset
      
      # Inspect the Piece ---------------------------------
      while current_offset <= highest_offset:
         # Increment at the beginning so we can use 'continue' later.
         potential_offset = min(next_low_event,next_high_event)
         
         # Sanity check
         i = Decimal( '0.001' )
         if potential_offset <= current_offset:
            # This shouldn't ever be needed, but it's to help prevent an endless
            # loop in a situation where, for some reason, the "next event" is
            # supposed to happen before the "current event."
            current_offset += i
         else:
            current_offset = potential_offset
         
         # DEBUGGING
         #print( '!!! new current_offset: ' + str(current_offset) )
         # END DEBUGGING
         
         # To know whether we should count the intervals and n-grams at this
         # offset. If current_offset / offset_interval has no remainder, we know
         # currentInterval is a multiple of offset_interval, so we should count
         # the interval and n-gram(s) at this offset.
         counting_this_offset = False
         if Decimal('0') == current_offset % offset_interval:
            counting_this_offset = True
         
         # For a situation like a pedal, we need to cause the static
         # voice to update its record of previous positions, or else it will seem
         # as though every n-gram has the correct moving voice, but the static
         # voice always has the notes leading up to the start of the period of
         # inactivity.
         low_must_update = high_must_update = False
         # But we also need to make sure that we're not updating a part that was
         # already updated.
         low_updated = high_updated = False
         
         # If current_offset has a Note/Rest in the lower part, and we're supposed
         # to be counting the objects at this offset, accept it as the 
         # most_recent_low object. This should be the same as just below for "high."
         lfnGEBO = lfn.getElementsByOffset( float(current_offset) )
         if len(lfnGEBO) > 0:
            lfnGEBO = lfnGEBO[0]
            
            # Wether or not we should count this object, and no matter what type
            # it is, we need to take into account the fact it occupies some
            # offset space.
            next_low_event = Decimal(str(lfnGEBO.offset)) + Decimal(str(lfnGEBO.quarterLength))
            
            # NOTE: This is a weird, inefficient part.
            # What happens here, basically, is I figure out what is the most recent
            # offset that we are supposed to check, then I figure out whether the
            # thing in lfnGEBO has a long enough quarterLength that it extends past
            # the next offset we're supposed to check.
            quarterLength_is_long = False
            previous_countable_offset = current_offset
            
            while (( previous_countable_offset % offset_interval ) != Decimal('0')):
               previous_countable_offset -= Decimal('0.001')
            
            if next_low_event > (previous_countable_offset + offset_interval):
               quarterLength_is_long = True
            # NOTE: End of the weird, inefficient part.
            
            if counting_this_offset or quarterLength_is_long:
               # If this is the first thing in the piece, most_recent_low will be empty
               # and we must put something there.
               if most_recent_low is None:
                  most_recent_low = lfnGEBO
                  # Indicate that other part must update and that we already did.
                  high_must_update, low_updated = True, True
               # If the most recent object is the other of Note/Rest than this, we
               # should add it on.
               elif type(most_recent_low) != type(lfnGEBO):
                  # Add the most (now ex-)most recent object to the list of previous
                  # objects, then assign lfnGEBO as the most recent object.
                  previous_lows.append( most_recent_low )
                  most_recent_low = lfnGEBO
                  # Indicate that other part must update and that we already did.
                  high_must_update, low_updated = True, True
               # If the current and most recent objects are Note objects.
               elif is_note( lfnGEBO ):
                  # If the current and most recent objects both have the same pitch,
                  # we can just add the current to the list.
                  if ( lfnGEBO.pitch != most_recent_low.pitch ):
                     # DEBUGGING
                     #print( 'different pitches in l, so adding at offset ' + str(current_offset) )
                     # END DEBUGGING
                     # Add the most (now ex-)most recent object to the list of previous
                     # objects, then assign lfnGEBO as the most recent object.
                     previous_lows.append( most_recent_low )
                     most_recent_low = lfnGEBO
                     # Indicate that other part must update and that we already did.
                     high_must_update, low_updated = True, True
                  # But if lfnGEBO and most_recent_low do in fact have the same pitch,
                  # we need to put lfnGEBO into most_recent_low because it is in fact
                  # the most recent. This helps when we calculate the next offset
                  # we expect something to happen. Only difference is we won't update
                  # previous_lows.
                  else:
                     # DEBUGGING
                     #print( 'same pitches in l, so updating at offset ' + str(current_offset) )
                     # END DEBUGGING
                     most_recent_low = lfnGEBO
               else: # True == is_rest( lfnGEBO )
                  # DEBUGGING
                  #print( 'l still resting, so updating at offset ' + str(current_offset) )
                  # END DEBUGGING
                  most_recent_low = lfnGEBO
                  #print( '***!!! lfnGEBO is offset ' + str(lfnGEBO.offset) + ' and qL ' + str(lfnGEBO.quarterLength) )
                  #print( '***!!! mRL is offset ' + str(lfnGEBO.offset) + ' and qL ' + str(lfnGEBO.quarterLength) )
            else:
               pass
         #--------
         
         # If current_offset has a Note/Rest in the higher part, accept it as the
         # most_recent_high object. This should be the same as just above,
         # except with 'high' parts substituted for 'low', so I'm removing the
         # comments here, to emphasize this.
         hfnGEBO = hfn.getElementsByOffset( float(current_offset) )
         if len(hfnGEBO) > 0:
            hfnGEBO = hfnGEBO[0]
            next_high_event = Decimal(str(hfnGEBO.offset)) + Decimal(str(hfnGEBO.quarterLength))
            
            # NOTE: This is a weird, inefficient part.
            quarterLength_is_long = False
            previous_countable_offset = current_offset
            
            while (( previous_countable_offset % offset_interval ) != Decimal('0')):
               previous_countable_offset -= Decimal('0.001')
            
            if next_high_event > (previous_countable_offset + offset_interval):
               quarterLength_is_long = True
            # NOTE: End of the weird, inefficient part.
            
            if counting_this_offset or quarterLength_is_long:
               if most_recent_high is None:
                  most_recent_high = hfnGEBO
                  low_must_update, high_updated = True, True
               elif type(most_recent_high) != type(hfnGEBO):
                  previous_highs.append( most_recent_high )
                  most_recent_high = hfnGEBO
                  low_must_update, high_updated = True, True
               elif is_note( hfnGEBO ):
                  if ( hfnGEBO.pitch != most_recent_high.pitch ):
                     # DEBUGGING
                     #print( 'different pitches in h, so adding at offset ' + str(current_offset) )
                     # END DEBUGGING
                     previous_highs.append( most_recent_high )
                     most_recent_high = hfnGEBO
                     low_must_update, high_updated = True, True
                  else:
                     # DEBUGGING
                     #print( 'same pitches in h, so updating at offset ' + str(current_offset) )
                     # END DEBUGGING
                     most_recent_high = hfnGEBO
               else: #if is_rest( hfnGEBO ):
                  # DEBUGGING
                  #print( 'h still resting, so updating at offset ' + str(current_offset) )
                  # END DEBUGGING
                  most_recent_high = hfnGEBO
         #--------
         
         # If one part was updated, but the other was not, as in a pedal point, we
         # need to copy the most recent object in the not-updated part into our
         # list of previously-happened stuff. This has the effect of keeping the
         # two parts "in sync," such that the same index in previous_lows and
         # previous_highs yields a vertical interval that actually happened in the
         # piece.
         if low_must_update and not low_updated:
            previous_lows.append( most_recent_low )
            low_updated = True
         if high_must_update and not high_updated:
            previous_highs.append( most_recent_high )
            high_updated = True
         
         # What are the next notes in each voice? It's tempting to do this at the
         # end of the loop, but if we do, we can't easily use the next bit to avoid
         # counting things that don't fall on an offset_interval boundary.
         # Note: I *think* that a nextXxxxEvent less than current_offset is not a
         # big deal, so I won't put a sanity check here.
         #next_low_event = most_recent_low.offset + most_recent_low.quarterLength
         #next_high_event = most_recent_high.offset + most_recent_high.quarterLength
         # DEBUGGING
         #print( "*!* next_low_event: " + str(next_low_event) + ' as ' + str(most_recent_low.offset) + ' + ' + str(most_recent_low.quarterLength) )
         #print( "*!* next_high_event: " + str(next_high_event) + ' as ' + str(most_recent_high.offset) + ' + ' + str(most_recent_high.quarterLength) )
         # END DEBUGGING
         
         # If this offset isn't on a division of our offset_interval, we won't be
         # adding anything to the statistics, so let's just skip out now
         if not counting_this_offset:
            # DEBUGGING
            #print( '*** Skipping out because we don\'t count this offset: ' + str(current_offset) )
            # END DEBUGGING
            continue
         # DEBUGGING
         #else:
            #print( '___ We\'ll check this offset: ' + str(current_offset) )
         # END DEBUGGING
         
         # If one of the voices was updated, we haven't yet counted this
         # vertical interval.
         if low_updated or high_updated:
            # If the mostRecent high and low objects are both Notes, we can count
            # them as an Interval, and potentially into an NGram.
            if is_note( most_recent_low ) and is_note( most_recent_high ):
               # count this Interval
               this_interval = interval.Interval( most_recent_low, most_recent_high )
               # DEBUGGING
               #print( '--> adding ' + this_interval.name + ' at offset ' + str(max(most_recent_low.offset,most_recent_high.offset)) )
               # END DEBUGGING
               # Only count this interval if we're "on the first 'n'" meaning
               # the intervals haven't been counted yet.
               if on_the_first_n:
                  the_statistics.add_interval( this_interval )
               
               # If there are insufficient previous objects to make an n-gram
               # here, then continue onto the next objects.
               if len(previous_lows) < (n-1) or len(previous_highs) < (n-1):
                  # DEBUGGING
                  #print( '--< not enough intervals for a ' + str(n) + '-gram (too short) at offset ' + str(current_offset) )
                  # END DEBUGGING
                  continue
               
               # If some of the previous objects we'll use are Rest rather than
               # Note objects, continue onto the next objects.
               there_are_rests = False
               for i in xrange(1,n):
                  if is_rest( previous_lows[-1*i] ) or \
                     is_rest( previous_highs[-1*i] ):
                        there_are_rests = True
                        break
               
               if there_are_rests:
                  # DEBUGGING
                  #print( '--< not enough intervals for a ' + str(n) + '-gram (rests) at offset ' + str(current_offset) )
                  # END DEBUGGING
                  continue
               # If we're still going, then make an NGram and add it to the
               # statistics!
               else:
                  # Construct the n-gram's previous intervals
                  ngram_history = []
                  for i in xrange(-1*(n-1),0):
                     ngram_history.append( interval.Interval( previous_lows[i], \
                                                              previous_highs[i] ) )
                  ngram_history.append( this_interval )
                  this_ngram = NGram( ngram_history )
                  the_statistics.add_ngram( this_ngram )
                  
                  # Process the LilyPond annotated part, if applicable.
                  if produce_lilypond:
                     # TODO: reduce code duplication
                     ## Add the interval's name to the lower note, for lilypond
                     sng = str(this_ngram)
                     first_space = sng.find(' ')
                     second_space = first_space + sng[first_space+1:].find(' ') + 1
                     
                     # This is the first annotation going into the score.
                     if 0 == len(lily_for_this_n):
                        # What if the annotations don't start at the beginning? I'll need to
                        # fill the space with Rest objects.
                        if current_offset > 0.0:
                           list_of_needed_qLs = fill_space_between_offsets( 0.0, current_offset )
                           z = note.Rest( quarterLength = list_of_needed_qLs[0] )
                           lily_for_this_n.append( z )
                           for needed_qL in list_of_needed_qLs[1]:
                              z = note.Rest( quarterLength = needed_qL )
                              lily_for_this_n.append( z )
                        
                        # Make a new Note in the lily_for_this_n stream, with the same offset as
                        # the start of this n-gram.
                        this_n_lily = note.Note( 'C4' ) # could be any pitch
                        this_n_lily.lily_markup = '^' + make_lily_triangle( sng )
                        #lily_for_this_n[-1].lily_markup = '^' + make_lily_triangle( sng )
                        
                        # Trouble is, I also have to fit in the right number of
                        # measures and filler material, or it'll be too
                        # difficult for output_LilyPond to invent this stuff.
                        lily_for_this_n.insert( current_offset, this_n_lily )
                        # DEBUGGING
                        #print( '~~~ inserted starter at offset ' + str(current_offset) )
                        # END DEBUGGING
                     # This is not the first annotation going into the score.
                     else:
                        # Figure out what's required to fill the space between the previous and this annotation
                        # DEBUGGING
                        #print( '~~~ lily_for_this_n[-1].offset: ' + str(lily_for_this_n[-1].offset) + '; current_offset: ' + str(current_offset) )
                        # END DEBUGGING
                        list_of_needed_qLs = fill_space_between_offsets( lily_for_this_n[-1].offset, current_offset )
                        # DEBUGGING
                        #print( '    list_of_needed_qLs: ' + str(list_of_needed_qLs) )
                        # END DEBUGGING
                        
                        # Set the previous annotation to the right quarterLength
                        lily_for_this_n[-1].quarterLength = list_of_needed_qLs[0]
                        
                        # Fill the remaining required space with Rest objects
                        for needed_qL in list_of_needed_qLs[1]:
                           z = note.Rest( quarterLength = needed_qL )
                           lily_for_this_n.append( z )
                        
                        # Put in the correct label.
                        lily_for_this_n[-1].lily_markup = '^' + make_lily_triangle( sng )
                        
                        # DEBUGGING
                        #print( '    offset ' + str(lily_for_this_n[-1].offset) + ' has label ' + sng )
                        #print( '    lily_for_this_n[-1].quarterLength: ' + str(lily_for_this_n[-1].quarterLength) )
                        # END DEBUGGING
                        
                        # Make a new Note in the lily_for_this_n stream.
                        this_n_lily = note.Note( 'C4' ) # could be any pitch
                        
                        # Trouble is, I also have to fit in the right number of
                        # measures and filler material, or it'll be too
                        # difficult for output_LilyPond to invent this stuff.
                        lily_for_this_n.insert( current_offset, this_n_lily )
                  #-----
                  
                  # DEBUGGING
                  #print( '--> adding ' + str(this_ngram) + ' at ' + str(current_offset) )
                  # END DEBUGGING
         # DEBUGGING
         #else:
            #print( 'Neither low nor high was flagged as updated; skipping offset: ' + str(current_offset) )
         # END DEBUGGING
      # End of the "while" loop.
      
      # Keep track of whether this is the first 'n' we're looking for; we should
      # only add intervals to the Vertical_Interval_Statistics object if this is
      # the first time, otherwise we'll get len(list_of_n) times as many intervals
      # reported as are actually in the piece
      on_the_first_n = False
   # End of the "for" loop.
   
   # Note the ending time of the analysis...
   # $10 says there's a better way to do this but I'm too lazy to look it up right now
   duration = datetime.now() - analysis_start_time
   duration = float( str(duration.seconds) + '.' + str(duration.microseconds) )
   return ( duration, list_of_lilypond_parts )
# End vis_these_parts() -------------------------------------------------------
