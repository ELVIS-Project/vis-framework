#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               analyzers/indexers/__init__.py
# Purpose:                Init file.
#
# Copyright (C) 2013 Christopher Antila
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
Indexers produce an "index" of a symbolic musical score. Each index provides one type of data, and
each event in can be attached to a particular moment in the original score. Some indexers produce
their index directly from the score, like the :class:`noterest.NoteRestIndexer`, which describes
pitches. Others create new information by analyzing another index, like the
:class:`interval.IntervalIndexer`, which describes harmonic intervals between two-part combinations
in the score, or the :class:`repeat.FilterByRepeatIndexer`, which removes consecutive identical
events, leaving only the first.

Analysis modules that subclass :class:`vis.analyzers.experimenter.Experimenter`, by contrast, produce results
that cannot be attached to a moment in a score.

Indexers work only on single :class:`vis.models.indexed_piece.IndexedPiece` instances. To analyze many
:class:`IndexedPiece` objects together, use an experimenter with an
:class:`vis.models.aggregated_pieces.AggregatedPieces` object.
"""
__all__ = ['noterest', 'interval', 'ngram', 'offset', 'repeat']

from vis.analyzers.indexers import interval
from vis.analyzers.indexers import noterest
from vis.analyzers.indexers import ngram
from vis.analyzers.indexers import offset
from vis.analyzers.indexers import repeat
