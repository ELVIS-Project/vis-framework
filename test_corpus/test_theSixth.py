#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         test_theSixth.py
# Purpose:      Creates a Score with which to test vis.
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

top_part = Part()
top_part.append( Note('F4', quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.5) )
top_part.append( Note('G4',quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.25) )
top_part.append( Note('A4',quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.25) )
top_part.append( Note('C5',quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.5) )
top_part.append( Note('D5',quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.25) )
top_part.append( Note('E5',quarterLength=0.25) )
top_part.append( Rest(quarterLength=0.25) )

bot_part = Part()
bot_part.append( Note('C3',quarterLength=0.5) )
bot_part.append( Rest(quarterLength=0.5) )
bot_part.append( Rest(quarterLength=1.0) )
bot_part.append( Note('D3',quarterLength=0.5) )
bot_part.append( Rest(quarterLength=0.5) )
bot_part.append( Rest(quarterLength=1.0) )

the_first_piece = Score( [top_part,bot_part] )

#------------------------------------------------------------------------------

top_partz = Part()
top_partz.append( Note('F4',quarterLength=0.125) )
top_partz.append( Rest(quarterLength=0.875) )
top_partz.append( Note('G4',quarterLength=0.125) )
top_partz.append( Rest(quarterLength=0.375) )
top_partz.append( Note('A4',quarterLength=0.125) )
top_partz.append( Rest(quarterLength=0.375) )
top_partz.append( Note('C5',quarterLength=0.5) )
top_partz.append( Rest(quarterLength=0.5) )
top_partz.append( Note('D5',quarterLength=0.5) )
top_partz.append( Rest(quarterLength=0.5) )

bot_partz = Part()
bot_partz.append( Note('C3',quarterLength=0.875) )
bot_partz.append( Rest(quarterLength=1.0) )
bot_partz.append( Rest(quarterLength=0.125) )
bot_partz.append( Note('D3',quarterLength=0.875) )
bot_partz.append( Rest(quarterLength=1.0) )
bot_partz.append( Rest(quarterLength=0.125) )

the_second_piece = Score( [top_partz,bot_partz] )

#------------------------------------------------------------------------------

top_partx = Part()
top_partx.append( Note('F3',quarterLength=0.125) )
top_partx.append( Rest(quarterLength=0.875) )
top_partx.append( Note('G3',quarterLength=0.125) )
top_partx.append( Rest(quarterLength=0.375) )
top_partx.append( Note('A3',quarterLength=0.125) )
top_partx.append( Rest(quarterLength=0.375) )
top_partx.append( Note('C4',quarterLength=0.5) )
top_partx.append( Rest(quarterLength=0.5) )
top_partx.append( Note('D4',quarterLength=0.5) )
top_partx.append( Rest(quarterLength=0.5) )

bot_partx = Part()
bot_partx.append( Note('C5',quarterLength=0.875) )
bot_partx.append( Rest(quarterLength=1.0) )
bot_partx.append( Rest(quarterLength=0.125) )
bot_partx.append( Note('D5',quarterLength=0.875) )
bot_partx.append( Rest(quarterLength=1.0) )
bot_partx.append( Rest(quarterLength=0.125) )

the_third_piece = Score( [bot_partx,top_partx] )