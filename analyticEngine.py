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
def visTheseParts( theseParts, theSettings, theStatistics ):
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
   analysisStartingTime = datetime.now()
   
   # Is 'thing' a Note?
   def isNote( thing ):
      if isinstance( thing, note.Note ):
         return True
      else:
         return False
   #

   # Is 'thing' a Rest?
   def isRest( thing ):
      if isinstance( thing, note.Rest ):
         return True
      else:
         return False
   #

   # Is 'thing' a Note, Rest, or neither?
   def noteOrRest( thing ):
      if isinstance( thing, note.Note) or isinstance( thing, note.Rest ):
         return True
      else:
         return False
   #

   n = 2 # TODO: get this from settings
   # TODO: Make it so that, if we get a List of integers from settings, we
   # can process the whole list.

   # Now we'll take just the notes and rests. I don't want to use 
   # .notesAndRests because then I get chords and None and other garbage.
   #hfn = theseParts[0].notesAndRests
   #lfn = theseParts[1].notesAndRests
   hfn, lfn = stream.Stream(), stream.Stream()
   for thing in theseParts[0].flat:
      if noteOrRest( thing ):
         hfn.append( thing )
      ## DEBUGGING
      #else:
         #print( "Not a note or rest, not in hfn: " + str(type(thing)) )
      ## END DEBUGGING
   #
   for thing in theseParts[1].flat:
      if noteOrRest( thing ):
         lfn.append( thing )
      ## DEBUGGING
      #else:
         #print( "Not a note or rest, not in hfn: " + str(type(thing)) )
      ## END DEBUGGING
   #
   
   # Initialize -----------------------
   # Prepare to compare the intervals.
   # We need to know when we get to the end
   highestOffset = max(lfn.highestOffset, hfn.highestOffset)
   # We need to start at the beginning.
   currentOffset = min(lfn.lowestOffset, hfn.lowestOffset)
   # How much to increment the offset. With quarterLength==1.0 and offsetInterval
   # of 0.5, this means we're counting by eighth notes.
   offsetInterval = theSettings.get_property( 'offsetBetweenInterval' )
   # These hold the most recent Note/Rest in their respective
   # voice. We can't say "current" because it implies the offset of
   # mostRecentHigh == currentOffset, which may not be true if, for example
   # there is a very long Note/Rest.
   mostRecentHigh, mostRecentLow = None, None
   # These will hold all the previous Note/Rest objects in their respective
   # voices. It's how we build n-grams, with mostRecentX and objects from
   # these lists.
   previousHighs, previousLows = [], []
   # First offset to check is 0.0 !
   nextLowEvent, nextHighEvent = 0.0, 0.0
   currentOffset = -100 # so we'll take 0.0
   
   # Loop -----------------------------
   # The most important part!
   while currentOffset <= highestOffset:
      # Increment at the beginning so we can use 'continue' later.
      potentialOffset = min(nextLowEvent,nextHighEvent)
      
      # Sanity check
      if potentialOffset <= currentOffset:
         # This shouldn't ever be needed, but it's to help prevent an endless
         # loop in a situation where, for some reason, the "next event" is
         # supposed to happen before the "current event."
         currentOffset += 0.001
      else:
         currentOffset = potentialOffset
      
      # DEBUGGING
      #print( '!!! new currentOffset: ' + str(currentOffset) )
      # END DEBUGGING
      
      # To know whether we should count the intervals and n-grams at this
      # offset. If currentOffset / offsetInterval has no remainder, we know
      # currentInterval is a multiple of offsetInterval, so we should count
      # the interval and n-gram(s) at this offset.
      countingThisOffset = False
      if 0 == currentOffset % offsetInterval:
         countingThisOffset = True
      
      # For a situation like a melisma, we need to cause the static
      # voice to update its record of previous positions, or else it will seem
      # as though every n-gram has the correct moving voice, but the static
      # voice always has the notes leading up to the start of the period of
      # inactivity.
      lowMustUpdate = highMustUpdate = False
      # But we also need to make sure that we're not updating a part that was
      # already updated.
      lowUpdated = highUpdated = False
      
      # If currentOffset has a Note/Rest in the lower part, and we're supposed
      # to be counting the objects at this offset, accept it as the 
      # mostRecentLow object. This should be the same as just below for "high."
      lfnGEBO = lfn.getElementsByOffset( currentOffset )
      if len(lfnGEBO) > 0:
         lfnGEBO = lfnGEBO[0]
         
         # Wether or not we should count this object, and no matter what type
         # it is, we need to take into account the fact it occupies some
         # offset space.
         nextLowEvent = lfnGEBO.offset + lfnGEBO.quarterLength
         
         # NOTE: This is a weird, inefficient part.
         # What happens here, basically, is I figure out what is the most recent
         # offset that we are supposed to check, then I figure out whether the
         # thing in lfnGEBO has a long enough quarterLength that it extends past
         # the next offset we're supposed to check.
         quarterLengthIsLong = False
         pCO = int(currentOffset*1000)
         oI = int(offsetInterval*1000)
         
         while (( pCO % oI ) != 0):
            pCO -= 1
         else:
            previousCountableOffset = float(pCO) / 1000.0
         
         if nextLowEvent > (previousCountableOffset + offsetInterval):
            quarterLengthIsLong = True
         # NOTE: End of the weird, inefficient part.
         
         if countingThisOffset or quarterLengthIsLong:
            # If this is the first thing in the piece, mostRecentLow will be empty
            # and we must put something there.
            if mostRecentLow is None:
               mostRecentLow = lfnGEBO
               # Indicate that other part must update and that we already did.
               highMustUpdate, lowUpdated = True, True
            # If the most recent object is the other of Note/Rest than this, we
            # should add it on.
            elif type(mostRecentLow) != type(lfnGEBO):
               # Add the most (now ex-)most recent object to the list of previous
               # objects, then assign lfnGEBO as the most recent object.
               previousLows.append( mostRecentLow )
               mostRecentLow = lfnGEBO
               # Indicate that other part must update and that we already did.
               highMustUpdate, lowUpdated = True, True
            # If the current and most recent objects are Note objects.
            elif isNote( lfnGEBO ):
               # If the current and most recent objects both have the same pitch,
               # we can just add the current to the list.
               if ( lfnGEBO.pitch != mostRecentLow.pitch ):
                  # DEBUGGING
                  #print( 'different pitches in l, so adding at offset ' + str(currentOffset) )
                  # END DEBUGGING
                  # Add the most (now ex-)most recent object to the list of previous
                  # objects, then assign lfnGEBO as the most recent object.
                  previousLows.append( mostRecentLow )
                  mostRecentLow = lfnGEBO
                  # Indicate that other part must update and that we already did.
                  highMustUpdate, lowUpdated = True, True
               # But if lfnGEBO and mostRecentLow do in fact have the same pitch,
               # we need to put lfnGEBO into mostRecentLow because it is in fact
               # the most recent. This helps when we calculate the next offset
               # we expect something to happen. Only difference is we won't update
               # previousLows.
               else:
                  # DEBUGGING
                  #print( 'same pitches in l, so updating at offset ' + str(currentOffset) )
                  # END DEBUGGING
                  mostRecentLow = lfnGEBO
            else: # True == isRest( lfnGEBO )
               # DEBUGGING
               #print( 'l still resting, so updating at offset ' + str(currentOffset) )
               # END DEBUGGING
               mostRecentLow = lfnGEBO
               #print( '***!!! lfnGEBO is offset ' + str(lfnGEBO.offset) + ' and qL ' + str(lfnGEBO.quarterLength) )
               #print( '***!!! mRL is offset ' + str(lfnGEBO.offset) + ' and qL ' + str(lfnGEBO.quarterLength) )
         else:
            pass
      #--------
      
      # If currentOffset has a Note/Rest in the higher part, accept it as the
      # mostRecentHigh object. This should be the same as just above,
      # except with 'high' parts substituted for 'low', so I'm removing the
      # comments here, to emphasize this.
      hfnGEBO = hfn.getElementsByOffset( currentOffset )
      if len(hfnGEBO) > 0:
         hfnGEBO = hfnGEBO[0]
         nextHighEvent = hfnGEBO.offset + hfnGEBO.quarterLength
         
         # NOTE: This is a weird, inefficient part.
         quarterLengthIsLong = False
         pCO = int(currentOffset*1000)
         oI = int(offsetInterval*1000)
         while (( pCO % oI ) != 0):
            pCO -= 1
         else:
            previousCountableOffset = float(pCO) / 1000.0
         if nextHighEvent > (previousCountableOffset + offsetInterval):
            quarterLengthIsLong = True
         # NOTE: End of the weird, inefficient part.
         
         if countingThisOffset or quarterLengthIsLong:
            if mostRecentHigh is None:
               mostRecentHigh = hfnGEBO
               lowMustUpdate, highUpdated = True, True
            elif type(mostRecentHigh) != type(hfnGEBO):
               previousHighs.append( mostRecentHigh )
               mostRecentHigh = hfnGEBO
               lowMustUpdate, highUpdated = True, True
            elif isNote( hfnGEBO ):
               if ( hfnGEBO.pitch != mostRecentHigh.pitch ):
                  # DEBUGGING
                  #print( 'different pitches in h, so adding at offset ' + str(currentOffset) )
                  # END DEBUGGING
                  previousHighs.append( mostRecentHigh )
                  mostRecentHigh = hfnGEBO
                  lowMustUpdate, highUpdated = True, True
               else:
                  # DEBUGGING
                  #print( 'same pitches in h, so updating at offset ' + str(currentOffset) )
                  # END DEBUGGING
                  mostRecentHigh = hfnGEBO
            else: #if isRest( hfnGEBO ):
               # DEBUGGING
               #print( 'h still resting, so updating at offset ' + str(currentOffset) )
               # END DEBUGGING
               mostRecentHigh = hfnGEBO
      #--------
      
      # If one part was updated, but the other was not, as in a melisma, we
      # need to copy the most recent object in the not-updated part into our
      # list of previously-happened stuff. This has the effect of keeping the
      # two parts "in sync," such that the same index in previousLows and
      # previousHighs yields a vertical interval that actually happened in the
      # piece.
      if lowMustUpdate and not lowUpdated:
         previousLows.append( mostRecentLow )
         lowUpdated = True
      if highMustUpdate and not highUpdated:
         previousHighs.append( mostRecentHigh )
         highUpdated = True
      
      # What are the next notes in each voice? It's tempting to do this at the
      # end of the loop, but if we do, we can't easily use the next bit to avoid
      # counting things that don't fall on an offsetInterval boundary.
      # Note: I *think* that a nextXxxxEvent less than currentOffset is not a
      # big deal, so I won't put a sanity check here.
      #nextLowEvent = mostRecentLow.offset + mostRecentLow.quarterLength
      #nextHighEvent = mostRecentHigh.offset + mostRecentHigh.quarterLength
      # DEBUGGING
      #print( "*!* nextLowEvent: " + str(nextLowEvent) + ' as ' + str(mostRecentLow.offset) + ' + ' + str(mostRecentLow.quarterLength) )
      #print( "*!* nextHighEvent: " + str(nextHighEvent) + ' as ' + str(mostRecentHigh.offset) + ' + ' + str(mostRecentHigh.quarterLength) )
      # END DEBUGGING
      
      # If this offset isn't on a division of our offsetInterval, we won't be
      # adding anything to the statistics, so let's just skip out now
      if not countingThisOffset:
         # DEBUGGING
         #print( '*** Skipping out because we don\'t count this offset: ' + str(currentOffset) )
         # END DEBUGGING
         continue
      
      # If one of the voices was updated, we haven't yet counted this
      # vertical interval.
      if lowUpdated or highUpdated:
         # If the mostRecent high and low objects are both Notes, we can count
         # them as an Interval, and potentially into an NGram.
         if isNote( mostRecentLow ) and isNote( mostRecentHigh ):
            # count this Interval
            thisInterval = interval.Interval( mostRecentLow, mostRecentHigh )
            # DEBUGGING
            #print( '--> adding ' + thisInterval.name + ' at offset ' + str(max(mostRecentLow.offset,mostRecentHigh.offset)) )
            # END DEBUGGING
            theStatistics.addInterval( thisInterval )
            
            # Make sure there are enough previous objects to make an n-gram.
            # TODO: make this work for n != 2
            if len(previousLows) < (n-1) or len(previousHighs) < (n-1):
               # DEBUGGING
               #print( '--< not enough intervals for a ' + str(n) + '-gram (too short) at offset ' + str(currentOffset) )
               # END DEBUGGING
               pass
            # Make sure those previous objects are Note and not Rest objects.
            # TODO: make this work for n != 2
            elif isRest( previousLows[-1] ) or isRest( previousHighs[-1] ):
               # DEBUGGING
               #print( '--< not enough intervals for a ' + str(n) + '-gram (rests) at offset ' + str(currentOffset) )
               # END DEBUGGING
               pass
            # If we're still going, then make an NGram and add it to the
            # statistics!
            else:
               thisNGram = NGram( [interval.Interval( previousLows[-1], previousHighs[-1] ), thisInterval] )
               theStatistics.addNGram( thisNGram )
               
               # Add the interval's name to the lower note, for lilypond
               if isNote( lfnGEBO ):
                  sng = str(thisNGram)
                  firstSpace = sng.find(' ')
                  secondSpace = firstSpace + sng[firstSpace+1:].find(' ') + 1
                  lfnGEBO.visLilyMarkup = \
                  '_\markup{\combine \concat{\\teeny{"' + sng[:firstSpace] + \
                  ' " \lower #2 "' + sng[firstSpace+1:secondSpace] + \
                  '" " ' + sng[secondSpace+1:] + \
                  '"}} \path #0.1 #\'((moveto -1 1.25) (lineto 1.65 -2.25) (lineto 4.3 1.25) (closepath))}'
               
               # DEBUGGING
               #print( '--> adding ' + str(thisNGram) + ' at ' + str(currentOffset) )
               # END DEBUGGING
      # DEBUGGING
      #else:
         #print( 'Neither low nor high was flagged as updated; skipping offset: ' + str(currentOffset) )
      # END DEBUGGING
   # End of the "while" loop.
   
   # Note the ending time of the analysis
   durationTime = datetime.now() - analysisStartingTime
   return durationTime.seconds
# End visTheseParts() -------------------------------------------------------