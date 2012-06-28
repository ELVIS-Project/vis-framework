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

topPart = Part()
topPart.append( Note('F4', quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.5) )
topPart.append( Note('G4',quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.25) )
topPart.append( Note('A4',quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.25) )
topPart.append( Note('C5',quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.5) )
topPart.append( Note('D5',quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.25) )
topPart.append( Note('E5',quarterLength=0.25) )
topPart.append( Rest(quarterLength=0.25) )

botPart = Part()
botPart.append( Note('C3',quarterLength=0.5) )
botPart.append( Rest(quarterLength=0.5) )
botPart.append( Rest(quarterLength=1.0) )
botPart.append( Note('D3',quarterLength=0.5) )
botPart.append( Rest(quarterLength=0.5) )
botPart.append( Rest(quarterLength=1.0) )

theFirstPiece = Score( [topPart,botPart] )

#------------------------------------------------------------------------------

topPartz = Part()
topPartz.append( Note('F4',quarterLength=0.125) )
topPartz.append( Rest(quarterLength=0.875) )
topPartz.append( Note('G4',quarterLength=0.125) )
topPartz.append( Rest(quarterLength=0.375) )
topPartz.append( Note('A4',quarterLength=0.125) )
topPartz.append( Rest(quarterLength=0.375) )
topPartz.append( Note('C5',quarterLength=0.5) )
topPartz.append( Rest(quarterLength=0.5) )
topPartz.append( Note('D5',quarterLength=0.5) )
topPartz.append( Rest(quarterLength=0.5) )

botPartz = Part()
botPartz.append( Note('C3',quarterLength=0.875) )
botPartz.append( Rest(quarterLength=1.0) )
botPartz.append( Rest(quarterLength=0.125) )
botPartz.append( Note('D3',quarterLength=0.875) )
botPartz.append( Rest(quarterLength=1.0) )
botPartz.append( Rest(quarterLength=0.125) )

theSecondPiece = Score( [topPartz,botPartz] )