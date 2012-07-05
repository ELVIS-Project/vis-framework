#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         outputLilypond.py
# Purpose:      Outputs music21 Objects into LilyPond Format
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
import os # needed for writing the output file
from string import letters as stringLetters
from random import choice as randomChoice
# music21
from music21 import note
from music21 import clef
from music21 import meter
from music21 import key
from music21 import stream
from music21 import instrument
from music21 import metadata
from music21 import layout
from music21 import bar
# vis
from dealsWithFiles import fileOutputter

#------------------------------------------------------------------------------

# TODO: must be replaced with instance variable
# this holds the names of all the parts in this score
_partsInThisScore = []

#------------------------------------------------------------------------------
def stringOfNLetters( n ):
   '''
   Generates a string of n random letters.
   '''
   post = ""
   for i in xrange(n):
      post += randomChoice( stringLetters )
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def octaveNumberToLilySymbol( num ):
   '''
   Returns the LilyPond symbol corresponding to the octave number.
   '''
   if ( 0 == num ):
      return ",,,"
   elif ( 1 == num ):
      return ",,"
   elif ( 2 == num ):
      return ","
   elif ( 3 == num ):
      return ""
   elif ( 4 == num ):
      return "'"
   elif ( 5 == num ):
      return "''"
   elif ( 6 == num ):
      return "'''"
   elif ( 7 == num ):
      return "''''"
   elif ( 8 == num ):
      return "'''''"
   elif ( 9 == num ):
      return "''''''"
   elif ( 10 == num ):
      return "'''''''"
   elif ( 11 == num ):
      return "''''''''"
   elif ( 12 == num ):
      return "'''''''''"
   else:
      # TODO: raise an exception
      print( "octaveNumberToLilySymbol(): I don't know what this octave is (" + str(num) + ")" )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def pitchToLilyPitch( p, includeOctave = 'yes' ):
   '''
   Returns a str that is the LilyPond pitch name for the pitch.Pitch
   
   Second argument can be set to 'no' to avoid the commas or apostrophes that
   indicate octave.
   '''
   pc = p.name.lower()
   post = pc[0]
   for accidental in pc[1:]:
      if '-' == accidental:
         post += 'es'
      elif '#' == accidental:
         post += 'is'
   
   if 'yes' == includeOctave:
      o = p.octave
      if None == o:
         post += octaveNumberToLilySymbol( p.implicitOctave )
      else:
         post += octaveNumberToLilySymbol( o )
   else: # we assume 'no'
      pass
   
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def durationToLengthInt( dur ): # "dur" means "duration"
   '''
   Returns a length integer (like '4' for quarter note) corresponding to the
   Duration passed in.
   '''
   
   durType = dur.type
   
   if 'breve' == durType:
      post = ''
   elif 'whole' == durType:
      post = '1'
   elif 'half' == durType:
      post = '2'
   elif 'quarter' == durType:
      post = '4'
   elif 'eighth' == durType:
      post = '8'
   elif '16th' == durType:
      post = '16'
   elif '32nd' == durType:
      post = '32'
   elif '64th' == durType:
      post = '64'
   elif '128th' == durType:
      post = '128'
   elif '256th' == durType:
      post = '256'
   else:
      # TODO: raise an exception
      print( "durationToLengthInt(): I don't know what this quarterLength is (" + str(durType) + ")" )
   
   #numDots = 0
   #try:
      #numDots = dur.dots
   #except AttributeError:
      #pass
   
   for i in xrange(dur.dots):
      post += "."
   
   return post
#------------------------------------------------------------------------------
   
#------------------------------------------------------------------------------
def lilyFromNote( lilyThis ):
   '''
   Returns a str that is a LilyPond representation of the inputted note.Note
   '''
   post = ""
   if lilyThis.isRest:
      post += "r" + durationToLengthInt( lilyThis.duration )
   else:
      post += pitchToLilyPitch( lilyThis.pitch ) + durationToLengthInt( lilyThis.duration )
   
   try:
      post += str(lilyThis.visLilyMarkup)
   except AttributeError as ae:
      pass
   except Exception as exc:
      print( 'EE: ' + str(exc) )
   
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def barlineToLily( bl ):
   '''
   Given a music21.bar.Barline object, will return a str that has the LilyPond
   representation of that barline.
   '''
   # From the music21 source code... a list of barline styles...
   # 
   # barStyleList = ['regular', 'dotted', 'dashed', 'heavy', 'double', 'final', 
   #               'heavy-light', 'heavy-heavy', 'tick', 'short', 'none']
   
   post = "\\bar \""
   bls = bl.style
   
   if 'regular' == bls:
      post += "|"
   elif 'dotted' == bls:
      post += ":"
   elif 'dashed' == bls:
      post += "dashed"
   elif 'heavy' == bls:
      post += "|.|"
   elif 'double' == bls:
      post += "||"
   elif 'final' == bls:
      post += "|."
   elif 'heavy-light' == bls:
      post += ".|"
   elif 'heavy-heavy' == bls:
      post += ".|."
   elif 'tick' == bls:
      pass
   elif 'short' == bls:
      pass
   elif 'none' == bls:
      post += ""
   else:
      # TODO: raise an exception?
      return ""
   
   post += "\""
   
   return post
   
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def processMeasure( theMeas ):
   '''
   Returns a str that is one line of a LilyPond score, containing one Measure.
   
   Input should be a Measure.
   '''
   post = "   "
   
   # first check if it's a partial (pick-up) measure
   if theMeas.duration.quarterLength < theMeas.barDuration.quarterLength:
      post += "\\partial " + durationToLengthInt( theMeas.duration ) + "\n   "
   
   # now fill in all the stuff
   for obj in theMeas:
      # Note
      if isinstance( obj, note.Note ):
         post += lilyFromNote( obj ) + " "
      # Clef
      elif isinstance( obj, clef.Clef ):
         if isinstance( obj, clef.TrebleClef ):
            post += "\\clef treble\n   "
         elif isinstance( obj, clef.BassClef ):
            post += "\\clef bass\n   "
         elif isinstance( obj, clef.TenorClef ):
            post += "\\clef tenor\n   "
         elif isinstance( obj, clef.AltoClef ):
            post += "\\clef alto\n   "
         else:
            print( "Didn't process clef: " + str(obj) )
      # Time Signature
      elif isinstance( obj, meter.TimeSignature ):
         post += "\\time " + str(obj.beatCount) + "/" + str(obj.denominator) + "\n   "
      # Key Signature
      elif isinstance( obj, key.KeySignature ):
         pm = obj.pitchAndMode
         if 2 == len(pm):
            post += "\\key " + pitchToLilyPitch( pm[0], includeOctave='no' ) + " \\" + pm[1] + "\n   "
         else:
            post += "\\key " + pitchToLilyPitch( pm[0], includeOctave='no' ) + "\n   "
      # Barline
      elif isinstance( obj, bar.Barline ):
         post += barlineToLily( obj ) + " "
      # PageLayout and SystemLayout
      elif isinstance( obj, layout.SystemLayout ) or isinstance( obj, layout.PageLayout ):
         # I don't know what to do with these undocumented features.
         pass
      # We don't know what it is, and should probably figure out!
      else:
         # TODO: raise an exception
         print( "processMeasure(): didn't process " + str(obj) )
   
   # append bar-check symbol, if required
   if len(post) > 3:
      post += "|\n"
      return post
   else:
      return ""
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def processStream( s ):
   '''
   Outputs a str containing part or all of a LilyPond source file, when given
   a stream.*
   
   So far, can be called with:
   - stream.Part
   - stream.Score
   - metadata.Metadata
   - layout.StaffGroup
   '''
   post = ""
   # Part
   if isinstance( s, stream.Part ):
      # TODO: some metadata thing
      # TODO: some LilyPond formatting things
      for thing in s:
         if isinstance( thing, stream.Measure ):
            post += processMeasure( thing )
         elif isinstance( thing, instrument.Instrument ):
            thing.partIdRandomize()
            callThisPart = thing.bestName() + stringOfNLetters( 8 )
            _partsInThisScore.append( callThisPart )
            post +=  callThisPart + " = % \\with { instrumentName = \\markup{ \"" + thing.bestName() + "\" } }\n" + "{\n"
            #post += "   instrumentName = \markup{ \"" + thing.bestName() + "\" }\n"
         else:
            # TODO: raise exception
            print( "processStream(): while processing Part, didn't know how to deal with " + str(thing) )
      # finally, to close the part
      post += "}\n"
   # Score
   elif isinstance( s, stream.Score ):
      # add some basic metadata needed to process/format a LilyPond file
      post = '% LilyPond output from music21 via "outputLilypond.py"\n\\version "2.14.2"\n\n'
      # TODO: maybe later we can set the paper size dynamically?
      post += '\\paper {\n   #(set-paper-size "letter")\n}\n\n'
      
      # loop through the things that might be a Part or a Metadata or a StaffGroup
      for possiblePart in s:
         post += processStream( possiblePart ) + "\n"
      
      # Output the \score{} block
      post += '\\score {\n   \\new StaffGroup\n   <<\n'
      for eachPart in _partsInThisScore:
         post += '      \\new Staff = "' + eachPart + '" \\' + eachPart + '\n'
      post += '   >>\n   \\layout{ }\n}\n'
      
   # Header (Metadata)
   elif isinstance( s, metadata.Metadata ):
      post += "\header {\n"
      
      if None != s.composer:
         post += '   composer = \markup{ "' + s.composer.name + '" }\n'
      if None != s.composers: # I don't really know what to do with non-composer contributors
         pass
      if 'None' != s.date:
         post += '   date = "' + str(s.date) + '"\n'
      if None != s.movementName:
         post += '   subtitle = \markup{ "'
         if None != s.movementNumber:
            post += str(s.movementNumber) + ': '
         post += s.movementName + '" }\n'
      if None != s.opusNumber:
         post += '   opus = "' + str(s.opusNumber) + '"\n'
      if None != s.title:
         post += '   title = \markup{ \"' + s.title
         if None != s.alternativeTitle:
            post += '(\\"' + s.alternativeTitle + '\\")'
         post += '" }\n'
      
      post += "}\n"
   # StaffGroup
   elif isinstance( s, layout.StaffGroup ):
      # Ignore this undocumented non-feature!
      pass
   # Something else...
   else:
      # TODO: raise an exception
      print( "processStream(): didn't know what to do with this " + str(s) )
   
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
class LilyPondSettings:
   '''
   Holds the settings relevant to output formatting of a LilyPond file.
   
   List of Settings:
   - barNumbers : print bar numbers on 'every' bar, the start of every 'system'
      or 'never'
   - tagline : either 'default' ("Music engraving my LilyPond...") or a str
      that is what you want the tagline to be.
   - indent : either 'default' or a str that is the indentation you want (like
      "0\cm" for example)
   - printInstrNames : 'yes' or 'no' whether to print instrument names
   '''
   def __init__( self, barNumbers='system', tagline='default', indent='default', \
      printInstrNames='yes' ):
      self.barNumber = barNumbers
      self.tagline = tagline
      self.indent = indent
      self.printInstrNames = printInstrNames
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputTheFile( contents, filename='test_output/output_thing.ly' ):
   # TODO: a better job on this
   fileOutputter( contents, filename )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def processScore( scoreToProcess ):
   scoreToWrite = processStream( scoreToProcess )
   outputTheFile( scoreToWrite )
#------------------------------------------------------------------------------
