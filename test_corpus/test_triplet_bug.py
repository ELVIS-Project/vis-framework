# stringified for safe keeping, and so pylint stops bothering me.
"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         test_triplet_bug.py
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
from music21.meter import TimeSignature

top_part = Part()
top_part.append( TimeSignature( '2/1' ) )
top_part.append( Note('G4', quarterLength=2.0) )
top_part.append( Note('B-4', quarterLength=3.0) )
top_part.append( Note('A4', quarterLength=1.0) )
top_part.append( Note('G4', quarterLength=2.0) )
top_part.append( Note('G4', quarterLength=2.0) )
top_part.append( Note('F#4', quarterLength=1.0) )
top_part.append( Note('E4', quarterLength=1.0) )
top_part.append( Note('F#4', quarterLength=4.0) )
top_part.append( Note('G4', quarterLength=8.0) )

bot_part = Part()
bot_part.append( TimeSignature( '2/1' ) )
bot_part.append( Note('G3', quarterLength=3.0) )
bot_part.append( Note('A3', quarterLength=1.0) )
bot_part.append( Note('B-3', quarterLength=2.0) )
bot_part.append( Note('C4', quarterLength=1.0) )
bot_part.append( Note('D4', quarterLength=1.0) )
bot_part.append( Note('E4', quarterLength=8.0/3.0) )
bot_part.append( Note('C4', quarterLength=8.0/3.0) )
bot_part.append( Note('D4', quarterLength=8.0/3.0) )
bot_part.append( Note('G3', quarterLength=4.0) )
bot_part.append( Note('G6', quarterLength=4.0) )

triplet_test_piece = Score( [top_part,bot_part] )
#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
top_part = Part()
top_part.append( TimeSignature( '2/1' ) )
top_part.append( Note('G4', quarterLength=2.0) )
top_part.append( Note('B-4', quarterLength=3.0) )
top_part.append( Note('A4', quarterLength=1.0) )
top_part.append( Note('G4', quarterLength=2.0) )
top_part.append( Note('G4', quarterLength=2.0) )
top_part.append( Note('F#4', quarterLength=1.0) )
top_part.append( Note('E4', quarterLength=1.0) )
top_part.append( Note('F#4', quarterLength=4.0) )
top_part.append( Note('G4', quarterLength=8.0) )

bot_part = Part()
bot_part.append( TimeSignature( '2/1' ) )
bot_part.append( Note('G3', quarterLength=3.0) )
bot_part.append( Note('A3', quarterLength=1.0) )
bot_part.append( Note('B-3', quarterLength=2.0) )
bot_part.append( Note('C4', quarterLength=1.0) )
bot_part.append( Note('D4', quarterLength=1.0) )
bot_part.append( Note('E4', quarterLength=2.25) )
bot_part.append( Note('C4', quarterLength=3.0) )
bot_part.append( Note('D4', quarterLength=2.75) )
bot_part.append( Note('G3', quarterLength=4.0) )
bot_part.append( Note('G6', quarterLength=4.0) )

simple_test_piece = Score( [top_part,bot_part] )
#------------------------------------------------------------------------------
"""
pass
