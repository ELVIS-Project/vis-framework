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
# music21
from music21 import interval
from music21 import stream
from music21 import note
# vis
from NGram import NGram



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
   
   Returns the number of seconds the analysis took.
   '''
   
   # Note the starting time of the analysis
   analysis_start_time = datetime.now()
   
   # Is 'thing' a Note?
   def is_note( thing ):
      if isinstance( thing, note.Note ):
         return True
      else:
         return False
   #
   
   # Is 'thing' a Rest?
   def is_rest( thing ):
      if isinstance( thing, note.Rest ):
         return True
      else:
         return False
   #
   
   # Is 'thing' a Note, Rest, or neither?
   def is_note_or_rest( thing ):
      if isinstance( thing, note.Note) or isinstance( thing, note.Rest ):
         return True
      else:
         return False
   #
   
   # Repeat the whole process with every specified value of n.
   for n in the_settings.get_property('lookForTheseNs'):
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
      
      # Initialize -----------------------
      # Prepare to compare the intervals.
      # We need to know when we get to the end
      highest_offset = max(lfn.highestOffset, hfn.highestOffset)
      # We need to start at the beginning.
      current_offset = min(lfn.lowestOffset, hfn.lowestOffset)
      # How much to increment the offset. With quarterLength of 1.0 and
      # offset_interval of 0.5, this means we're counting by eighth notes.
      offset_interval = the_settings.get_property( 'offsetBetweenInterval' )
      # These hold the most recent Note/Rest in their respective
      # voice. We can't say "current" because it implies the offset of
      # most_recent_high == current_offset, which may not be true if, for 
      # example, there is a very long Note/Rest.
      most_recent_high, most_recent_low = None, None
      # These will hold all the previous Note/Rest objects in their respective
      # voices. It's how we build n-grams, with mostRecentX and objects from
      # these lists.
      previous_highs, previous_lows = [], []
      # First offset to check is 0.0 !
      next_low_event, next_high_event = 0.0, 0.0
      current_offset = -100 # so we'll take 0.0
      
      # Loop -----------------------------
      # The most important part!
      while current_offset <= highest_offset:
         # Increment at the beginning so we can use 'continue' later.
         potential_offset = min(next_low_event,next_high_event)
         
         # Sanity check
         if potential_offset <= current_offset:
            # This shouldn't ever be needed, but it's to help prevent an endless
            # loop in a situation where, for some reason, the "next event" is
            # supposed to happen before the "current event."
            current_offset += 0.001
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
         if 0 == current_offset % offset_interval:
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
         lfnGEBO = lfn.getElementsByOffset( current_offset )
         if len(lfnGEBO) > 0:
            lfnGEBO = lfnGEBO[0]
            
            # Wether or not we should count this object, and no matter what type
            # it is, we need to take into account the fact it occupies some
            # offset space.
            next_low_event = lfnGEBO.offset + lfnGEBO.quarterLength
            
            # NOTE: This is a weird, inefficient part.
            # What happens here, basically, is I figure out what is the most recent
            # offset that we are supposed to check, then I figure out whether the
            # thing in lfnGEBO has a long enough quarterLength that it extends past
            # the next offset we're supposed to check.
            quarterLength_is_long = False
            pCO = int(current_offset*1000)
            oI = int(offset_interval*1000)
            
            while (( pCO % oI ) != 0):
               pCO -= 1
            else:
               previous_countable_offset = float(pCO) / 1000.0
            
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
         hfnGEBO = hfn.getElementsByOffset( current_offset )
         if len(hfnGEBO) > 0:
            hfnGEBO = hfnGEBO[0]
            next_high_event = hfnGEBO.offset + hfnGEBO.quarterLength
            
            # NOTE: This is a weird, inefficient part.
            quarterLength_is_long = False
            pCO = int(current_offset*1000)
            oI = int(offset_interval*1000)
            while (( pCO % oI ) != 0):
               pCO -= 1
            else:
               previous_countable_offset = float(pCO) / 1000.0
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
                  
                  # Add the interval's name to the lower note, for lilypond
                  if is_note( lfnGEBO ):
                     sng = str(this_ngram)
                     first_space = sng.find(' ')
                     second_space = first_space + sng[first_space+1:].find(' ') + 1
                     lfnGEBO.lily_markup = \
                     '_\markup{\combine \concat{\\teeny{"' + sng[:first_space] + \
                     ' " \lower #2 "' + sng[first_space+1:second_space] + \
                     '" " ' + sng[second_space+1:] + \
                     '"}} \path #0.1 #\'((moveto -1 1.25) (lineto 1.65 -2.25) (lineto 4.3 1.25) (closepath))}'
                  
                  # DEBUGGING
                  #print( '--> adding ' + str(this_ngram) + ' at ' + str(current_offset) )
                  # END DEBUGGING
         # DEBUGGING
         #else:
            #print( 'Neither low nor high was flagged as updated; skipping offset: ' + str(current_offset) )
         # END DEBUGGING
      # End of the "while" loop.
   # End of the "for" loop.
   
   # Note the ending time of the analysis...
   # $10 says there's a better way to do this but I'm too lazy to look it up right now
   duration = datetime.now() - analysis_start_time
   return float( str(duration.seconds) + '.' + str(duration.microseconds) )
# End vis_these_parts() -------------------------------------------------------
