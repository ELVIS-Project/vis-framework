#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/analyzers/indexers/__init__.py
# Purpose:                Init file.
#
# Copyright (C) 2013, 2014 Christopher Antila
#
# As this file contains only documentation, it is copyrighted under the Creative Commons CC-BY-SA
# license, as described in the "doc/CC-BY-SA.txt" file in this repository.
#--------------------------------------------------------------------------------------------------
"""
Indexers produce an "index" of a symbolic musical score. Each index provides one type of data, and
each event can be attached to a particular moment in the original score. Some indexers produce
their index directly from the score, like the :class:`~noterest.NoteRestIndexer`, which describes
pitches. Others create new information by analyzing another index, like the
:class:`~interval.IntervalIndexer`, which describes harmonic intervals between two-part combinations
in the score, or the :class:`~repeat.FilterByRepeatIndexer`, which removes consecutive identical
events, leaving only the first.

Analysis modules of the subclass :class:`~vis.analyzers.experimenter.Experimenter`, by contrast,
produce results that cannot be attached to a moment in a score.

Indexers work only on single :class:`~vis.models.indexed_piece.IndexedPiece` instances. To analyze
many :class:`~vis.models.indexed_piece.IndexedPiece` objects together, use an experimenter with an
:class:`~vis.models.aggregated_pieces.AggregatedPieces` object.
"""
