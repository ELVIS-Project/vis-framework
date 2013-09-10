#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers_tests/test_vis_server.py
# Purpose:                Test file for the multiprocessing server in vis.
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
Test file for the multiprocessing server in vis.
"""

# Allow missing docstrings
# pylint: disable=C0111
# pylint: disable=W0212
# pylint: disable=R0904

import unittest
import time
import mock
from vis import vis_server


class TestMPServer(unittest.TestCase):  # pylint: disable=R0923
    def setUp(self):
        # pylint: disable=C0103
        with mock.patch(u'dbus.service.Object') as self.dbus_service_Object:
            with mock.patch(u'dbus.SessionBus') as self.dbus_SessionBus:
                with mock.patch(u'dbus.service.BusName') as self.dbus_BusName:
                    self.mper = vis_server.Multiprocessor()

    def tearDown(self):
        self.mper._close_the_pool()

    def test_close_pool_1(self):
        # The point of closing the pool twice is that it should actually close the pool the first
        # time, then not try to close the pool the second time (which would raise an exception).
        self.mper._close_the_pool()
        self.assertEqual(None, self.mper._pool)
        self.mper._close_the_pool()
        self.assertTrue(True)

    def test_status_1(self):
        # We should get 42 before the pool is closed, and 0 after.
        self.assertEqual(42, self.mper.Status())
        self.mper._close_the_pool()
        self.assertEqual(0, self.mper.Status())

    def test_process_command_1(self):
        # just the u'shutdown' command... that's all we have for now!
        with mock.patch(u'vis.vis_server.APP') as mock_app:
            self.mper._process_command(u'shutdown')
            self.assertEqual(None, self.mper._pool)
            mock_app.exit.assert_called_once_with(0)

    def test_add_job_to_tracker_1(self):
        # Add a thousand jobs to the tracker; make sure we get a unique ident for each one, and
        # that it's a 16-character unicode, and that it's associated with the correct "sender" and
        # "sender ident" in self._job_record
        our_record = []  # holds 3-tuples: our_ident, sender_ident, sender
        idents = []
        for i in xrange(1000):
            our_ident = self.mper._add_job_to_tracker(u'ID: ' + unicode(i),
                                                      u'Sender: ' + unicode(i))
            our_record.append((our_ident, u'ID: ' + unicode(i), u'Sender: ' + unicode(i)))
            idents.append(our_ident)
        self.assertEqual(1000, len(self.mper._job_record))
        self.assertEqual(1000, len(set(idents)))
        for rec in our_record:
            self.assertEqual(rec[1], self.mper._job_record[rec[0]][1])
            self.assertEqual(rec[2], self.mper._job_record[rec[0]][0])

    def test_return_result_1(self):
        # nothing happens with invalid job ID
        self.mper._return_result((u'funkytown', 12))
        self.assertEqual(0, self.mper._bus.call_async.call_count)

    def test_return_result_2(self):
        # error condition is properly reported
        self.mper._job_record[u'our ident'] = (u'sender', u'client ident')
        self.mper._return_result((u'our ident', 400))
        self.mper._bus.call_async.assert_any_call(bus_name=u'sender',
                                                  object_path=u'/MPInterface',
                                                  dbus_interface=u'ca.elvisproject.vis_client',
                                                  method=u'_ReturnJob',
                                                  signature='a{ss}',
                                                  args=({u'ident': u'client ident',
                                                         u'result': 'I400\n.'},),
                                                  reply_handler=mock.ANY,
                                                  error_handler=mock.ANY)

    def test_return_result_3(self):
        # normal results are properly returned
        self.mper._job_record[u'our ident'] = (u'sender', u'client ident')
        self.mper._return_result((None, u'our ident', u'Things got all messed up.'))
        self.mper._bus.call_async.assert_any_call(bus_name=u'sender',
                                                  object_path=u'/MPInterface',
                                                  dbus_interface=u'ca.elvisproject.vis_client',
                                                  method=u'_ReturnJob',
                                                  signature='a{ss}',
                                                  args=({u'ident': u'client ident',
                                                         u'error': u'Things got all messed up.'},),
                                                  reply_handler=mock.ANY,
                                                  error_handler=mock.ANY)

    def test_submit_1(self):
        # ensure a command is sent to self._process_command(), which we'll mock
        with mock.patch(u'vis.vis_server.Multiprocessor._process_command') as mock_pc:
            self.mper.Submit({u'command': u'Be awesome!'}, u'Sender')
            mock_pc.assert_called_once_with(u'Be awesome!')

    def test_submit_2(self):
        # if func is None, or args is None, ensure we call self._return_result() with an error
        # report... we'll mock _return_result()
        with mock.patch(u'vis.vis_server.Multiprocessor._return_result') as mock_rr:
            with mock.patch(u'vis.vis_server.Multiprocessor._add_job_to_tracker') as mock_ajtt:
                ajtt_returns = [u'asdf', u'fdsa']
                def ajtt_ret_func(*args):
                    return ajtt_returns.pop(0)
                mock_ajtt.side_effect = ajtt_ret_func
                self.mper.Submit({u'ident': u'JOB1', u'func': u'silly'}, u'Sender')
                self.mper.Submit({u'ident': u'JOB2', u'args': u'silly'}, u'Sender')
                mock_rr.assert_any_call((None, u'asdf', u'Neither "func" nor "args" can be None.'))
                mock_rr.assert_any_call((None, u'fdsa', u'Neither "func" nor "args" can be None.'))

    def test_submit_3(self):
        # otherwise, make sure everything gets submitted correctly to the (mock!) Pool
        with mock.patch(u'vis.vis_server.Multiprocessor._add_job_to_tracker') as mock_ajtt:
            self.mper._pool = mock.MagicMock()
            mock_ajtt.return_value = u'asdf'
            submit = {u'func': 'cvis.vis_server\ntest_func\np0\n.',
                      u'args': '(Varg1\np0\nVarg2\np1\ntp2\n.'}
            self.mper.Submit(submit, u'DBus Sender ID')
            self.mper._object_path = None  # without this, something in python-dbus gets called...
            self.mper._pool.apply_async.assert_called_once_with(vis_server.test_func,
                                                                (u'asdf', (u'arg1', u'arg2')),
                                                                callback=self.mper._return_result)

    #def test_submit_4(self):
        ## TODO: can't get this to work because the Pool causes Multiprocessor to be re-imported,
        ##       but it doesn't have the mock DBus in that case.
        ## test_submit_3() with a real Pool
        ## But we have to use a different module name for the u'func' because mock-vs-whatevs
        #with mock.patch(u'vis_server.Multiprocessor._return_result') as mock_rr:
            #submit = {u'func': 'cvis_server\ntest_func\np0\n.',
                      #u'args': '(Varg1\np0\nVarg2\np1\ntp2\n.'}
            #self.mper.Submit(submit, u'DBus Sender ID')
            #time.sleep(1)
            #print(str(self.mper._bus.call_async.call_args_list))  # DEBUG
            #self.mper._bus.call_async.assert_any_call(bus_name=u'sender',
                                                  #object_path=u'/MPInterface',
                                                  #dbus_interface=u'ca.elvisproject.vis_client',
                                                  #method=u'_ReturnJob',
                                                  #signature='a{ss}',
                                                  #args=({u'ident': u'client ident',
                                                         #u'error': u'Things got all messed up.'},),
                                                  #reply_handler=mock.ANY,
                                                  #error_handler=mock.ANY)
#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
MPSERVER_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestMPServer)
