#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name:         int_indexer_short.py
# Purpose:      Creates a set of Score objects with which to test vis.
#
# Copyright (C) 2012, 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Initialize the test environments for the IntervalIndexer tests.
"""

from music21.stream import Part, Score
from music21.note import Note, Rest
from music21.meter import TimeSignature
# NOTE: These tests assume the quarterLength interval between checks is 0.5
# pylint: disable=C0111


def _setup_parts():
    top = Part()
    top.append(TimeSignature('4/4'))
    bottom = Part()
    bottom.append(TimeSignature('4/4'))
    return top, bottom


def test_1():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.5))
    return Score([top, bot])


def test_2():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.25))
    top.append(Rest(quarterLength=0.25))
    bot.append(Note('G3', quarterLength=0.25))
    bot.append(Rest(quarterLength=0.25))
    return Score([top, bot])


def test_3():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.25))
    bot.append(Rest(quarterLength=0.25))
    return Score([top, bot])


def test_4():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.25))
    top.append(Rest(quarterLength=0.25))
    bot.append(Note('G3', quarterLength=0.5))
    return Score([top, bot])


def test_5():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    top.append(Note('F4', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Note('A3', quarterLength=0.5))
    return Score([top, bot])


def test_6():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Note('A3', quarterLength=0.5))
    return Score([top, bot])


def test_7():
    top, bot = _setup_parts()
    top.append(Note('A4', quarterLength=0.5))
    top.append(Note('G4', quarterLength=1.0))
    top.append(Note('F4', quarterLength=0.5))
    bot.append(Note('B3', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Note('A3', quarterLength=0.5))
    bot.append(Note('B3', quarterLength=0.5))
    return Score([top, bot])


def test_8():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    bot.append(Note('G3', quarterLength=0.25))
    bot.append(Rest(quarterLength=0.25))
    bot.append(Note('A3', quarterLength=0.5))
    return Score([top, bot])


def test_9():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    top.append(Note('G4', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.25))
    bot.append(Rest(quarterLength=0.25))
    bot.append(Note('A3', quarterLength=0.5))
    bot.append(Note('B3', quarterLength=0.5))
    return Score([top, bot])


def test_10():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    bot.append(Note('G3', quarterLength=0.25))
    bot.append(Note('A3', quarterLength=0.75))
    return Score([top, bot])


def test_11():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.5))
    return Score([top, bot])


def test_12():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    bot.append(Note('G3', quarterLength=0.25))
    bot.append(Rest(quarterLength=0.25))
    bot.append(Note('G3', quarterLength=0.5))
    return Score([top, bot])


def test_13():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=1.0))
    bot.append(Note('G3', quarterLength=0.125))
    bot.append(Rest(quarterLength=0.125))
    bot.append(Note('A3', quarterLength=0.125))
    bot.append(Rest(quarterLength=0.125))
    bot.append(Note('G3', quarterLength=0.5))
    return Score([top, bot])


def test_14():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.0625))
    top.append(Note('G4', quarterLength=0.0625))  # 0.0625
    top.append(Note('G4', quarterLength=0.0625))  # 0.125
    top.append(Note('G4', quarterLength=0.0625))  # 0.1875
    top.append(Note('G4', quarterLength=0.0625))  # 0.25
    top.append(Note('G4', quarterLength=0.0625))  # 0.3125
    top.append(Note('G4', quarterLength=0.0625))  # 0.375
    top.append(Note('G4', quarterLength=0.0625))  # 0.4375
    top.append(Note('G4', quarterLength=0.5))  # 0.5
    bot.append(Note('G3', quarterLength=0.125))
    bot.append(Rest(quarterLength=0.125))  # 0.125
    bot.append(Note('A3', quarterLength=0.125))  # 0.25
    bot.append(Rest(quarterLength=0.0625))  # 0.375
    bot.append(Rest(quarterLength=0.0625))  # 0.4375
    bot.append(Note('G3', quarterLength=0.5))  # 0.5
    return Score([top, bot])


def test_15():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    top.append(Note('G4', quarterLength=0.25))  # 0.5
    top.append(Rest(quarterLength=0.25))  # 0.75
    top.append(Note('G4', quarterLength=0.5))  # 1.0
    top.append(Note('G4', quarterLength=0.5))  # 1.5
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.25))  # 0.5
    bot.append(Rest(quarterLength=0.25))  # 0.75
    bot.append(Rest(quarterLength=0.5))  # 1.0
    bot.append(Note('G3', quarterLength=0.5))  # 1.5
    return Score([top, bot])


def test_16():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    top.append(Note('A4', quarterLength=0.75))  # 0.5
    top.append(Note('G4', quarterLength=0.25))  # 1.25
    top.append(Note('B4', quarterLength=0.5))  # 1.5
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Rest(quarterLength=0.25))  # 0.5
    bot.append(Note('F3', quarterLength=0.75))  # 0.75
    bot.append(Note('E3', quarterLength=0.5))  # 1.5
    return Score([top, bot])


def test_17():
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    top.append(Note('A4', quarterLength=0.75))  # 0.5
    top.append(Note('F4', quarterLength=0.75))  # 1.25
    top.append(Note('E4', quarterLength=0.5))  # 2.0
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Note('A3', quarterLength=0.25))  # 0.5
    bot.append(Note('F3', quarterLength=0.375))  # 0.75
    bot.append(Rest(quarterLength=0.25))  # 1.125
    bot.append(Note('G3', quarterLength=0.625))  # 1.375
    bot.append(Note('G3', quarterLength=0.5))  # 2.0
    return Score([top, bot])


def test_18():
    """
    NB: This test is designed specifically to ensure that the _event_finder()
    doesn't stop processing when it doesn't find an element of the expected types
    at an offset. You should ask it to look for Rest objects only.
    """
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    top.append(Rest(quarterLength=0.5))
    bot.append(TimeSignature('4/4'))
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Rest(quarterLength=0.5))
    return Score([top, bot])


def test_19():
    """
    NB: This test is designed specifically to ensure that the _event_finder()
    finds Rest objects when the happen at the same time as Note objects, when
    only Rest objects are requested to be found.
    """
    top, bot = _setup_parts()
    top.append(Note('G4', quarterLength=0.5))
    top.append(Note('G5', quarterLength=0.5))
    bot.append(Note('G3', quarterLength=0.5))
    bot.append(Rest(quarterLength=0.5))
    return Score([top, bot])
