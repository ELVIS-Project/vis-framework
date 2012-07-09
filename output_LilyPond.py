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
from subprocess import Popen, PIPE # for running bash things
from string import letters as string_letters
from random import choice as random_choice
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
from music21 import humdrum
# vis
from file_output import file_outputter

#------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
class UnidentifiedObjectError( Exception ):
   '''
   When something can't be identified.
   '''
   def __init__( self, val ):
      self.value = val
   def __str__( self ):
      return repr( self.value )
#-------------------------------------------------------------------------------


#------------------------------------------------------------------------------
def string_of_n_letters( n ):
   '''
   Generates a string of n random letters.
   '''
   post = ""
   for i in xrange(n):
      post += random_choice( string_letters )
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def octave_num_to_lily( num ):
   '''
   Returns the LilyPond symbol corresponding to the octave number.
   '''
   
   dictionary_of_octaves = { 0:",,,", 1:",,", 2:",", 3:"", 4:"'", 5:"''", \
      6:"'''", 7:"''''", 8:"'''''", 9:"''''''", 10:"'''''''", 11:"''''''''", \
      12:"'''''''''" }
   
   if num in dictionary_of_octaves:
      return dictionary_of_octaves[num]
   else:
      raise UnidentifiedObjectError( 'Octave out of range: ' + str(num) )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def pitch_to_lily( p, include_octave = 'yes' ):
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
   
   if 'yes' == include_octave:
      if p.octave is None:
         post += octave_num_to_lily( p.implicitOctave )
      else:
         post += octave_num_to_lily( p.octave )
   
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def duration_to_lily( dur ): # "dur" means "duration"
   # TODO: Figure out what this quarterLength is, and make it work: 7.99609375
   '''
   Returns a LilyPond length integer (like '4' for quarter note) corresponding
   to the Duration passed in.
   '''
   
   # We need both a list of our potential durations and a dictionary of what
   # they mean in LilyPond terms.
   list_of_durations = [16.0, 8.0, 4.0, 2.0, 1.0, 0.5,  0.25, 0.125, 0.0625, \
      0.3125]
   dictionary_of_durations = { 16.0:'\longa', 8.0:'\\breve', 4.0:'1', 2.0:'2', \
      1.0:'4', 0.5:'8', 0.25:'16', 0.125:'32', 0.0625:'64', 0.3125:'128' }
   
   # So we only access the quarterLength once
   dur_qL = dur.quarterLength
   
   # If there are no dots, the value should be in the dictionary, and we can
   # simply return it.
   if dur_qL in dictionary_of_durations:
      return dictionary_of_durations[dur_qL]
   else:
      # We have to figure out the largest value that will fit, then append the
      # correct number of dots.
      post = ''
      for d in list_of_durations:
         if (dur_qL - d) > 0.0:
            post += dictionary_of_durations[d]
            break
      else:
         raise UnidentifiedObjectError( 'A-Duration appears to be invalid (' + str(dur.quarterLength) + ')' )
      #
      try:
         for i in xrange(dur.dots):
            post += "."
      except TypeError as err:
         print( "Didn't work " + str(dur.quarterLength) )
         #raise UnidentifiedObjectError( 'B-Duration appears to be invalid (' + str(dur.quarterLength) + ') || ' + str(err) )
      #
      return post
#------------------------------------------------------------------------------
   
#------------------------------------------------------------------------------
def note_to_lily( lily_this ):
   '''
   Returns a str that is a LilyPond representation of the inputted note.Note.
   
   Additionally appends any value in the Note object's "lily_markup" property.
   '''
   
   post = ''
   
   if len(lily_this.duration.components) > 1:
      the_pitch = pitch_to_lily( lily_this.pitch )
      for durational_component in lily_this.duration.components:
         post += the_pitch + duration_to_lily( durational_component ) + '~ '
      post = post[:-2]
   elif lily_this.isRest:
      post += "r" + duration_to_lily( lily_this.duration )
   else:
      post += pitch_to_lily( lily_this.pitch ) + duration_to_lily( lily_this.duration )
   
   if lily_this.tie is not None:
      if lily_this.tie.type is 'start':
         post += "~"
   
   if hasattr( lily_this, 'lily_markup' ):
      post += str(lily_this.lily_markup)
   
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def barline_to_lily( bl ):
   '''
   Given a music21.bar.Barline object, will return a str that has the LilyPond
   representation of that barline.
   '''
   # From the music21 source code... a list of barline styles...
   # 
   # barStyleList = ['regular', 'dotted', 'dashed', 'heavy', 'double', 'final', 
   #               'heavy-light', 'heavy-heavy', 'tick', 'short', 'none']
   
   dictionary_of_barlines = { 'regular':"|", 'dotted':":", 'dashed':"dashed", \
      'heavy':"|.|", 'double':"||", 'final':"|.", 'heavy-light':".|", \
      'heavy-heavy':".|.", 'tick':"'", 'short':"'", 'none':"" }
   
   post = '\\bar "'
   
   if bl.style in dictionary_of_barlines:
      post += dictionary_of_barlines[bl.style] + '"'
      return post
   else:
      UnidentifiedObjectError( 'Barline type not recognized (' + bl.style + ')' )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def process_measure( the_meas ):
   '''
   Returns a str that is one line of a LilyPond score, containing one Measure.
   
   Input should be a Measure.
   '''
   post = "   "
   
   # first check if it's a partial (pick-up) measure
   if 0.0 <the_meas.duration.quarterLength < the_meas.barDuration.quarterLength:
      post += "\\partial " + duration_to_lily( the_meas.duration ) + "\n   "
   
   # now fill in all the stuff
   for obj in the_meas:
      # Note or Rest
      if isinstance( obj, note.Note ) or isinstance( obj, note.Rest ):
         post += note_to_lily( obj ) + " "
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
            raise UnidentifiedObjectError( 'Clef type not recognized: ' + obj )
      # Time Signature
      elif isinstance( obj, meter.TimeSignature ):
         post += "\\time " + str(obj.beatCount) + "/" + str(obj.denominator) + "\n   "
      # Key Signature
      elif isinstance( obj, key.KeySignature ):
         pm = obj.pitchAndMode
         if 2 == len(pm) and pm[1] is not None:
            post += "\\key " + pitch_to_lily( pm[0], include_octave='no' ) + " \\" + pm[1] + "\n   "
         else:
            # We'll have to assume it's \major, because music21 does that.
            post += "\\key " + pitch_to_lily( pm[0], include_octave='no' ) + " \\major\n   "
      # Barline
      elif isinstance( obj, bar.Barline ):
         # There's no need to write down a regular barline, because they tend
         # to happen by themselves. Of course, this will have to change once
         # we have the ability to override the standard barline.
         if 'regular' != obj.style:
            post += barline_to_lily( obj ) + " "
      # PageLayout and SystemLayout
      elif isinstance( obj, layout.SystemLayout ) or isinstance( obj, layout.PageLayout ):
         # I don't know what to do with these undocumented features.
         pass
      # **kern importer garbage... well, it's only garbage to us
      elif isinstance( obj, humdrum.spineParser.MiscTandam ):
         # http://mit.edu/music21/doc/html/moduleHumdrumSpineParser.html
         # Is there really nothing we can use this for? Seems like these
         # exist only to help music21 developers.
         pass
      # We don't know what it is, and should probably figure out!
      else:
         raise UnidentifiedObjectError( 'Unknown object in Bar: ' + str(obj) )
   #----
   
   # Append a bar-check symbol, if there was anything outputted.
   if len(post) > 3:
      post += "|\n"
      return post
   else:
      return ""
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def process_stream( s, the_settings ):
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
   # Score
   if isinstance( s, stream.Score ):
      # Things Before Parts -------------------------------
      # Our mark!
      post = '% LilyPond output from music21 via "output_LilyPond.py"\n'
      # Version
      post += '\\version "' + \
         the_settings.get_setting( 'lilypond_version' ) + \
         '"\n\n'
      # Set paper size
      post += '\\paper {\n   #(set-paper-size "' + \
         the_settings.get_setting( 'paper_size' ) + \
         '")\n}\n\n'
      
      # Parts ---------------------------------------------
      # This can hold all of our parts... they might also be a StaffGroup,
      # a Metadata object, or something else.
      list_of_parts = []
      # Go through the possible parts and see what we find.
      for possible_part in s:
         list_of_parts.append( process_stream( possible_part, the_settings ) + "\n" )
      # Append the parts to the score we're building. In the future, it'll
      # be important to re-arrange the parts if necessary, or maybe to filter
      # things, so we'll keep everything in this supposedly efficient loop.
      for i in xrange(len(list_of_parts)):
         post += list_of_parts[i]
      
      # Things After Parts --------------------------------
      # Output the \score{} block
      post += '\\score {\n   \\new StaffGroup\n   <<\n'
      for each_part in the_settings._partsInThisScore:
         post += '      \\new Staff = "' + each_part + '" \\' + each_part + '\n'
      post += '   >>\n'
      # Output the \layout{} block
      post += '   \\layout{\n'
      if the_settings.get_setting( 'indent' ) is not None:
         post += '      indent = ' + the_settings.get_setting( 'indent' ) + '\n'
      post += '   }\n}\n'
   # Part
   elif isinstance( s, stream.Part ):
      # TODO: some metadata thing
      # TODO: some LilyPond formatting things
      
      # Start the Part
      # We used to use some of the part's .bestName, but many scores (like
      # for **kern) don't have this.
      callThisPart = string_of_n_letters( 8 )
      the_settings._partsInThisScore.append( callThisPart )
      post +=  callThisPart + " =\n" + "{\n"
      
      # Deal with the measures
      for thing in s:
         if isinstance( thing, stream.Measure ):
            post += process_measure( thing )
         elif isinstance( thing, instrument.Instrument ):
            # TODO: we'll have to deal with this better, in the future
            post += '   %% ' + thing.bestName() + '\n'
         # **kern importer garbage... well, it's only garbage to us
         elif isinstance( thing, humdrum.spineParser.MiscTandam ):
            # http://mit.edu/music21/doc/html/moduleHumdrumSpineParser.html
            # Is there really nothing we can use this for? Seems like these
            # exist only to help music21 developers.
            pass
         else:
            raise UnidentifiedObjectError( 'Unknown object in Stream while processing Part: ' + str(thing) )
      # finally, to close the part
      post += "}\n"
   # Header (Metadata)
   elif isinstance( s, metadata.Metadata ):
      post += "\header {\n"
      
      if s.composer is not None:
         post += '   composer = \markup{ "' + s.composer.name + '" }\n'
      if s.composers is not None: # I don't really know what to do with non-composer contributors
         pass
      if 'None' != s.date:
         post += '   date = "' + str(s.date) + '"\n'
      if s.movementName is not None:
         post += '   subtitle = \markup{ "'
         if None != s.movementNumber:
            post += str(s.movementNumber) + ': '
         post += s.movementName + '" }\n'
      if s.opusNumber is not None:
         post += '   opus = "' + str(s.opusNumber) + '"\n'
      if s.title is not None:
         post += '   title = \markup{ \"' + s.title
         if s.alternativeTitle is not None:
            post += '(\\"' + s.alternativeTitle + '\\")'
         post += '" }\n'
      
      # Extra Formatting Options --------------------------
      # Tagline
      if the_settings.get_setting( 'tagline' ) is None:
         post += '   tagline = ""\n'
      elif the_settings.get_setting( 'tagline' ) == '':
         pass
      else:
         post += '   tagline = "' + the_settings.get_setting( 'tagline' ) + '"\n'
      
      # close the \header{} block
      post += "}\n"
   # StaffGroup
   elif isinstance( s, layout.StaffGroup ):
      # Ignore this undocumented non-feature!
      pass
   # **kern importer garbage... well, it's only garbage to us
   elif isinstance( obj, humdrum.spineParser.MiscTandam ):
      # http://mit.edu/music21/doc/html/moduleHumdrumSpineParser.html
      # Is there really nothing we can use this for? Seems like these
      # exist only to help music21 developers.
      pass
   # Something else...
   else:
      raise UnidentifiedObjectError( 'Unknown object in Stream: ' + str(s) )
   
   return post
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
class LilyPond_Settings:
   '''
   Holds the settings relevant to output formatting of a LilyPond file.
   
   List of Settings:
   - bar_numbers : print bar numbers on 'every' bar, the start of every 'system'
      or 'never'
   - tagline : either 'default' ("Music engraving my LilyPond...") or a str
      that is what you want the tagline to be.
   - indent : either 'default' or a str that is the indentation you want (like
      "0\cm" for example)
   - print_instrument_names : True or False whether to print instrument names
   - lilypond_version: a str that contains the LilyPond version (default is
      "2.14.2")
   '''
   def __init__( self ):
      # Hold a list of the part names in this Score
      self._partsInThisScore = []
      # Hold the other settings for this Score
      self._secret_settings = {}
      # Establish default values for settings in this Score
      self._secret_settings['bar_numbers'] = 'system' # TODO: implement this
      self._secret_settings['tagline'] = ''
         # empty string means "default tagline"
         # None means "no tagline"
      self._secret_settings['indent'] = None
      self._secret_settings['print_instrument_names'] = True # TODO: implement this
      self._secret_settings['paper_size'] = 'letter'
      # Super-fancy discovery of where LilyPond is on this computer, and which
      # version is available.
      proc = Popen( ['which', 'lilypond'], stdout=PIPE )
      self._secret_settings['lilypond_path'] = proc.stdout.read()[:-1] # slice gets rid of terminating newline
      proc = Popen( ['lilypond', '--version'], stdout=PIPE )
      lv = proc.stdout.read()
      lily_version = lv[lv.find('LilyPond')+9:lv.find('\n')]
      self._secret_settings['lilypond_version'] = lily_version
   
   def set_setting( self, setting_name, setting_value=None ):
      '''
      Modify the value of a setting. There are two forms:
      
      >>> from output_LilyPond import *
      >>> the_settings = LilyPond_Settings()
      >>> the_settings.set_setting( 'indent 0\mm' )
      >>> the_settings.get_setting( 'indent' )
      '0\mm'
      >>> the_settings.set_setting( 'indent', '4\mm' )
      >>> the_settings.get_setting( 'indent' )
      '4\mm'
      '''
      # TODO: implement the second form of whatever
      self._secret_settings[setting_name] = setting_value
   
   def get_setting( self, setting_name ):
      return self._secret_settings[setting_name]
   
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def output_the_file( contents, filename='test_output/output_thing' ):
   # TODO: exception handling, if possible
   return file_outputter( contents, filename, '.ly' )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def run_lilypond( filename, the_settings ):
   # file to output
   proc = Popen( [the_settings.get_setting('lilypond_path'), '--pdf', '-o', filename, filename], stdout=PIPE, stderr=PIPE )
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def process_score( the_score, the_settings=None ):
   '''
   Use this method to output an entire Score object. The second argument is
   an optional LilyPond_Settings object.
   '''
   
   if the_settings is None:
      the_settings = LilyPond_Settings()
   
   score_to_write = process_stream( the_score, the_settings )
   run_lilypond( output_the_file( score_to_write ), the_settings )
#------------------------------------------------------------------------------

if __name__ == '__main__':
   print( "Sorry, but you can't yet run output_LilyPond.py by itself!" )























