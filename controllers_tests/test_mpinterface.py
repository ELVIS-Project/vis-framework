#!/usr/bin/env python
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

# Allow missing docstrings
# pylint: disable=C0111
# pylint: disable=W0212
# pylint: disable=R0904

import unittest
from pickle import PicklingError
import mock
from vis.controllers.mpinterface import MPInterface


def test_func(*args):
    "Return the sum of a bunch of numbers."
    return sum([x for x in args])


class TestMPInterface(unittest.TestCase):  # pylint: disable=R0923
    def setUp(self):
        # pylint: disable=C0103
        with mock.patch(u'__builtin__.super') as self.duper:
            with mock.patch(u'dbus.service.Object') as self.dbus_service_Object:
                with mock.patch(u'dbus.SessionBus') as self.dbus_SessionBus:
                    with mock.patch(u'dbus.service.BusName') as self.dbus_BusName:
                        self.mpi = MPInterface()

    def test_submit_1(self):
        # - that submit() returns a unique unicode ident for each job
        # - that SystemBus.call_async() is called the right number of times with the right args
        self.mpi._bus.call_blocking = mock.MagicMock(return_value=42)
        idents = []
        for i in xrange(30, 60):
            idents.append(self.mpi.submit(test_func, i))
        self.assertEqual(len(idents), len(set(idents)))  # they're all unique
        self.assertTrue(all([isinstance(x, unicode) for x in idents]))  # they're all unicode
        self.assertEqual(30, self.mpi._bus.call_async.call_count)  # there were 30 call_async()
        self.assertEqual(30, self.mpi._bus.call_blocking.call_count)  # and 30 call_blocking()
        # ensure call_async() was called with all the right arguments
        for i, ident in enumerate(idents):
            these_args = ({u'ident': ident,
                u'func': 'cvis.controllers_tests.test_mpinterface\ntest_func\np0\n.',
                u'args': '(I' + str(i + 30) + '\ntp0\n.'},)
            self.mpi._bus.call_async.assert_any_call(bus_name=u'ca.elvisproject.vis_server',
                                                     object_path=u'/Multiprocessor',
                                                     dbus_interface=u'ca.elvisproject.vis_server',
                                                     method=u'Submit',
                                                     signature='a{ss}',
                                                     args=these_args,
                                                     reply_handler=mock.ANY,
                                                     error_handler=mock.ANY)

    def test_submit_2(self):
        # that submit() complains when an object can't be pickled
        # obviously, we can't pickle this non-module-level function
        self.mpi._bus.call_blocking = mock.MagicMock(return_value=42)
        self.assertRaises(PicklingError, self.mpi.submit, test_func, self.setUp)
        self.assertRaises(PicklingError, self.mpi.submit, self.setUp, 5)
        self.assertEqual(2, self.mpi._bus.call_blocking.call_count)

    def test_submit_3(self):
        # correct submission with no args
        self.mpi._bus.call_blocking = mock.MagicMock(return_value=42)
        ident = self.mpi.submit(test_func)
        these_args = ({u'ident': ident,
                u'func': 'cvis.controllers_tests.test_mpinterface\ntest_func\np0\n.',
                u'args': '(t.'},)
        self.mpi._bus.call_async.assert_called_once_with(bus_name=u'ca.elvisproject.vis_server',
                                                         object_path=u'/Multiprocessor',
                                                         dbus_interface=u'ca.elvisproject.vis_server',  # pylint: disable=C0301
                                                         method=u'Submit',
                                                         signature='a{ss}',
                                                         args=these_args,
                                                         reply_handler=mock.ANY,
                                                         error_handler=mock.ANY)
        self.assertEqual(1, self.mpi._bus.call_blocking.call_count)

    def test_get_ref(self):
        # call the method many times
        idents = []
        for i in xrange(10000):
            idents.append(self.mpi._get_ref())
        self.assertEqual(10000, len(set(idents)))  # there are 10000 and they're unique
        self.assertEqual(10000, self.mpi._submitted)  # proper "jobs submitted" increment
        for ident in idents:  # they're all unicode, 16 characters, and in the MPI's _refs
            self.assertTrue(isinstance(ident, unicode))
            self.assertEqual(16, len(ident))
            self.assertTrue(ident in self.mpi._refs)

    def test_poll_1(self):
        # poll() without a "ref"
        self.mpi._received = 5
        self.mpi._fetched = 0
        self.assertTrue(self.mpi.poll())
        self.mpi._received = 5
        self.mpi._fetched = 5
        self.assertFalse(self.mpi.poll())
        self.mpi._received = 0
        self.mpi._fetched = 0
        self.assertFalse(self.mpi.poll())

    def test_poll_2(self):
        # poll() with a "ref"
        # ... we have results ready
        ident = u'asdfasdfasdf'
        self.mpi._received = 1
        self.mpi._fetched = 0
        self.mpi._refs = [u'asdfasdfasdf', u'j3j3j3j3j3j3j3j3']
        self.mpi._results[ident] = [1, 2, 3]
        self.assertTrue(self.mpi.poll(ident))
        # ... we have no results
        self.mpi._results = {}
        self.assertFalse(self.mpi.poll(ident))
        # ... with invalid "ref
        self.assertTrue(self.mpi.poll(u'not here yo') is None)

    def test_fetch_1(self):
        # using patched unpicklers, test...
        with mock.patch(u'cStringIO.StringIO') as mock_stringio:
            with mock.patch(u'pickle.Unpickler') as mock_pickle:
                # - with an invalid ref
                self.mpi._refs = [u'asdf', u'bsdf', u'csdf', u'dsdf']
                self.assertRaises(LookupError, self.mpi.fetch, u'silly ref')
                # - with a ref that's not ready
                self.assertRaises(LookupError, self.mpi.fetch, u'csdf')
                # - with no ref but also no jobs waiting
                self.assertRaises(EOFError, self.mpi.fetch)
                with mock.patch(u'vis.controllers.mpinterface.MPInterface.poll') as mock_poll:
                    # - with no ref, make the method choose one (also tests proper use of pickle)
                    self.mpi._results = {u'asdf': u'fourteen', u'bsdf': u'fifteen'}
                    mock_poll.return_value = True
                    mock_stringio.return_value = u'from StringIO'
                    self.mpi.fetch()
                    mock_poll.assert_called_once_with()
                    stringio_call = mock_stringio.call_args_list[0][0][0]
                    self.assertTrue(stringio_call in [u'fourteen', u'fifteen'])
                    mock_pickle.assert_called_once_with(u'from StringIO')
                    self.assertEqual(1, len(self.mpi._results))
                    self.assertEqual(1, self.mpi._fetched)

    def test_fetch_2(self):
        # whole thing, no mocks
        self.mpi._refs = [u'asdf']
        self.mpi._results = {u'asdf': 'Vthis is a silly string for pickling\np0\n.'}
        self.mpi._received = 1
        self.mpi._fetched = 0
        expected = (u'asdf', u'this is a silly string for pickling')
        actual = self.mpi.fetch()
        self.assertSequenceEqual(expected, actual)

    def test_return_job(self):
        self.mpi._refs = [u'asdf']
        self.mpi._ReturnJob({u'ident': u'asdf', u'result': u'hello'})
        self.assertEqual(1, self.mpi._received)
        self.assertEqual(u'hello', self.mpi._results[u'asdf'])

#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
MPINTERFACE_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMPInterface)
