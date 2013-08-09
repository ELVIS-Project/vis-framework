#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_mpcontroller.py
# Purpose:                Test file for multiprocessing in vis.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Test file for multiprocessing in vis.
"""

import unittest
import mock
from vis.controllers.mpcontroller import MPController


def add_something(pipe_i, add_this, the_list):
    """
    anything, number, list of numbers
    ==>
    anything, list of numbers with "number" added
    """
    return pipe_i, [z + add_this for z in the_list]


class ThingProducer(object):
    """
    Add things to lists of integers.
    """

    def __init__(self, things, add, mpc):
        """
        Parameters
        ==========
        :param things: [[int]]
            A list of lists of integers that we'll add things to.

        :param add: int
            An integer to add to all the things in the lists.

        :param mpc: MPController
            An instance of MPController that we'll use for multiprocessing.
        """
        self._add_this = add
        self._things = things
        self._pipe_end = mpc.get_pipe()
        self._jobs_submitted = 0

    def start_stuff(self):
        """
        Submit jobs to the MPController. Each list given to the constructor will have two versions
        produced: one with 5 added to each item, and one with 10 added to each item.

        You cannot call this method after calling get_stuff().
        """
        for i in xrange(len(self._things)):
            self._jobs_submitted += 1
            self._pipe_end.send((add_something, [self._add_this, self._things[i]]))

    def get_stuff(self):
        """
        Return a list of the results. Also closes the Pipe.
        """
        post = []
        for times in xrange(self._jobs_submitted):
            shoop = self._pipe_end.recv()
            post.append(shoop)
        self._pipe_end.send('finished')
        self._pipe_end.close()
        return post

class TestMpcTests(unittest.TestCase):
    # TODO: test ThingProducer with mock objects
    def test_add_something_1(self):
        in_val = (0, 0, [0])
        expected = (0, [0])
        actual = add_something(in_val[0], in_val[1], in_val[2])
        self.assertEqual(expected, actual)

    def test_add_something_2(self):
        in_val = (0, 0, [1, 2, 3])
        expected = (0, [1, 2, 3])
        actual = add_something(in_val[0], in_val[1], in_val[2])
        self.assertEqual(expected, actual)

    def test_add_something_3(self):
        in_val = (0, 123, [0])
        expected = (0, [123])
        actual = add_something(in_val[0], in_val[1], in_val[2])
        self.assertEqual(expected, actual)

    def test_add_something_4(self):
        in_val = (u'symbol', 15, [0, 5, 15])
        expected = (u'symbol', [15, 20, 30])
        actual = add_something(in_val[0], in_val[1], in_val[2])
        self.assertEqual(expected, actual)


class TestMPControllerRuns(unittest.TestCase):
    def setUp(self):
        self.mpc = MPController()
        self.mpc.start()

    def tearDown(self):
        self.mpc.shutdown()

    def test_mpc_1(self):
        the_lists = [[0, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [3, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [4, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [5, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [6, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [7, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [8, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        expected = [[0, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [3, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [4, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [5, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [6, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [7, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [8, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        the_tp = ThingProducer(the_lists, 0, self.mpc)
        the_tp.start_stuff()
        actual = the_tp.get_stuff()
        self.assertEqual(expected, actual)

    def test_mpc_2(self):
        the_lists = [[0, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [3, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [4, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [5, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [6, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [7, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                     [8, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        expected = [[5, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [7, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [8, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [9, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [10, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [11, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [12, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    [13, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
        the_tp = ThingProducer(the_lists, 5, self.mpc)
        the_tp.start_stuff()
        actual = the_tp.get_stuff()
        self.assertEqual(expected, actual)

class TestMPController(unittest.TestCase):
    def test_mpc_1(self):
        # that calling MPController.get_pipe() calls the Pipe() constructor once
        with mock.patch('multiprocessing.Pool') as m_pool:
            mpc = MPController()
            mpc.start()
            end = mpc.get_pipe()
            end.send((add_something, [5, [1, 2, 3]]))
            #mpc.shutdown()
            m_pool.apply_async.assert_called_once_with((add_something, [5, [1, 2, 3]]))


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
MPC_TESTER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMpcTests)
MPCONTROLLER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMPController)
MPCONTROLLER_RUNS_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMPControllerRuns)
