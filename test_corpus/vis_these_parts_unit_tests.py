#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         vis_these_parts_unit_test.py
# Purpose:      Creates a set of Score objects with which to test vis.
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

from music21.stream import Part, Score
from music21.note import Note, Rest
from music21.meter import TimeSignature

# NOTE: These tests assume the quarterLength interval between checks is 0.5

# Test 1 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )

test_1 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 2 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.25) )
top.append( Rest( quarterLength=0.25 ) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Rest( quarterLength=0.25 ) )

test_2 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 3 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Rest( quarterLength=0.25 ) )

test_3 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 4 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.25) )
top.append( Rest( quarterLength=0.25 ) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )

test_4 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 5 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.5) )
top.append( Note('F4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Note('A3', quarterLength=0.5) )

test_5 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 6 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Note('A3', quarterLength=0.5) )

test_6 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 6B ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('A4', quarterLength=0.5) )
top.append( Note('G4', quarterLength=1.0) )
top.append( Note('F4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('B3', quarterLength=0.5) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Note('A3', quarterLength=0.5) )
bot.append( Note('B3', quarterLength=0.5) )

test_6B = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 7 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Rest( quarterLength=0.25 ) )
bot.append( Note('A3', quarterLength=0.5) )

test_7 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 7B ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )
top.append( Note('G4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Rest( quarterLength=0.25 ) )
bot.append( Note('A3', quarterLength=0.5) )
bot.append( Note('B3', quarterLength=0.5) )

test_7B = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 8 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Note('A3', quarterLength=0.75) )

test_8 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 9 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Note('G3', quarterLength=0.5) )

test_9 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 10 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Rest( quarterLength=0.25 ) )
bot.append( Note('G3', quarterLength=0.5) )

test_10 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 11 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=1.0) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.125) )
bot.append( Rest( quarterLength=0.125 ) )
bot.append( Note('A3', quarterLength=0.125) )
bot.append( Rest( quarterLength=0.125 ) )
#--
bot.append( Note('G3', quarterLength=0.5) )

test_11 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 12 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.0625) )
top.append( Note('G4', quarterLength=0.0625) )
top.append( Note('G4', quarterLength=0.0625) )
top.append( Note('G4', quarterLength=0.0625) )
#--
top.append( Note('G4', quarterLength=0.0625) )
top.append( Note('G4', quarterLength=0.0625) )
top.append( Note('G4', quarterLength=0.0625) )
top.append( Note('G4', quarterLength=0.0625) )
#--
top.append( Note('G4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.125) )
bot.append( Rest( quarterLength=0.125 ) )
bot.append( Note('A3', quarterLength=0.125) )
bot.append( Rest( quarterLength=0.0625 ) )
bot.append( Rest( quarterLength=0.0625 ) )
#--
bot.append( Note('G3', quarterLength=0.5) )

test_12 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 13 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.5) )
top.append( Note('G4', quarterLength=0.25) )
top.append( Rest( quarterLength=0.25 ) )
top.append( Note('G4', quarterLength=0.5) )
top.append( Note('G4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Note('G3', quarterLength=0.25) )
bot.append( Rest( quarterLength=0.25 ) )
bot.append( Rest( quarterLength=0.5 ) )
bot.append( Note('G3', quarterLength=0.5) )

test_13 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 14 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.5) )
top.append( Note('A4', quarterLength=0.75) )
top.append( Note('G4', quarterLength=0.25) )
top.append( Note('B4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Rest( quarterLength=0.25) )
bot.append( Note('F3', quarterLength=0.75) )
bot.append( Note('E3', quarterLength=0.5) )

test_14 = Score( [top, bot] )
#------------------------------------------------------------------------------



# Test 15 ----------------------------------------------------------------------
top = Part()
top.append( TimeSignature( '4/4' ) )
top.append( Note('G4', quarterLength=0.5) )
top.append( Note('A4', quarterLength=0.75) )
top.append( Note('F4', quarterLength=0.75) )
top.append( Note('E4', quarterLength=0.5) )

bot = Part()
bot.append( TimeSignature( '4/4' ) )
bot.append( Note('G3', quarterLength=0.5) )
bot.append( Note('A3', quarterLength=0.25) )
bot.append( Note('F3', quarterLength=0.375) )
bot.append( Rest( quarterLength=0.25 ) )
bot.append( Note('G3', quarterLength=0.625) )
bot.append( Note('G3', quarterLength=0.5) )

test_15 = Score( [top, bot] )
#------------------------------------------------------------------------------


































