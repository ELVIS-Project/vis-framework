#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:         experiment.py
# Purpose:      Describes the form of experiments done with vis
#
# Copyright (C) 2012 Christopher Antila, Jamie Klassen
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


class Experiment(object):
	"""
	Base class for all Experiments done in vis.
	"""
	def __init__(self, records):
		"""
		INPUTS:
		-records: a list of Record objects; this is the data
		which will be experimented with.
		"""
		super(Experiment, self).__init__()
		self.inputs = []
		self.settings = None
		self.records = records
	
	def run():
		"""
		This method must be implemented in subclasses to be
		where the main busines logic/processing for the
		experiment is done.
		"""
		pass
	

class Entropy(Experiment):
	"""
	Computes the statistical entropy of some aspect of a dataset.
	"""
	def __init__(self, arg):
		super(Entropy, self).__init__()
		self.arg = arg
		