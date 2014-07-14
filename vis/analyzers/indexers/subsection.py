#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexers/metre.py
# Purpose:                Indexers for metric concerns.
#
# Copyright (C) 2013, 2014 
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
.. 

Indexer to extract a subsection of a piece by offsets (e.g. a subsection from offset 7.0 to offset 18.0) and remove everything else from the workflow.
"""

# disable "string statement has no effect" warning---they do have an effect with Sphinx!
# pylint: disable=W0105

from music21 import note, meter
from vis.analyzers import indexer

class SubsectionIndexer(indexer.Indexer):

    required_score_type = 'pandas.Series'
  

    def __init__(self, score, settings=None):

        super(SubsectionIndexer, self).__init__(score, settings)

        if settings is None or u'subsection' not in settings:
            raise RuntimeError(u'SubsectionIndexer requires a subsection setting.')
        elif not isinstance(settings[u'subsection'], tuple) or not len(settings[u'subsection']) == 2 :
            raise RuntimeError(u'SubsectionIndexer requires a subsection setting formatted as (start_index, end_index) -- a float pair.')
        else:
            self._settings[u'subsection'] = settings[u'subsection']

        # If self._score is a Stream (subclass), change to a list of types you want to process
        self._types = []

        # This Indexer uses pandas magic, not an _indexer_func().
        #self._indexer_func = None

    def run(self):

        for series in self._score:
            #print series
            #series.name, otherwise try self._score.index(series)          
            self._score[int(series.name)] = series.loc[self._settings['subsection'][0] : self._settings['subsection'][1]]
            #print series.loc[self._settings['subsection'][0] : self._settings['subsection'][1]]

        combinations = [[x] for x in xrange(len(self._score))]
        return self.make_return([unicode(x)[1:-1] for x in combinations], self._score)