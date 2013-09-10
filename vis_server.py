#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------------------------
# Program Name:              vis_server
# Program Description:       Arranges multiprocessing for vis.
#
# Filename: vis_server.py
# Purpose: Arrange the multiprocessing for vis.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#---------------------------------------------------------------------------------------------------
"""
Arrange the multiprocessing for vis.
"""

import sys
import pickle
import random
from multiprocessing import Pool
from cStringIO import StringIO
from PyQt4 import QtCore
import dbus
import dbus.service  # required for the "service" modules to be accessible

# set up the PyQt main loop with DBus
from dbus.mainloop.qt import DBusQtMainLoop  # required for DBusQtMainLoop to be accessible
DBusQtMainLoop(set_as_default=True)

# Ensure we can import "vis," for client methods.
import imp
try:
    imp.find_module(u'vis')
except ImportError:
    sys.path.insert(0, u'..')

# hold the QCoreApplication where a Multiprocessor can get it
APP = None

# function for testing the Multiprocessor
def test_func(zed):
    "Turn the argument into a unicode object."
    return unicode(zed)


class Multiprocessor(dbus.service.Object):
    """
    Arranges multiprocessing for vis.

    There are two public methods, both of which should be called via DBus:
    - Submit
    - Status
    """
    def __init__(self):
        self._bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(u'ca.elvisproject.vis_server', bus=self._bus)
        dbus.service.Object.__init__(self, bus_name, u'/Multiprocessor')
        self._pool = Pool(2, maxtasksperchild=100)  # "maxtasksperchild" is new in python 2.7  # DEBUG: the "2" is debugging
        # _job_record: key is "our_ident"; value is a 2-tuple with "sender" and "client_ident"
        self._job_record = {}

    @QtCore.pyqtSlot()
    def _close_the_pool(self):
        "Close and join the pool so the application can exit properly."
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None

    def _return_result(self, result):
        """
        Return a job to its caller vis DBus.

        Parameters
        ==========
        :param result: Our job ID then the result of the computation, if computation was successful.
            Otherwise, a 3-tuple with None, the job ID, then a description of an error. If the job
            ID is not found, nothing happens.
        :type result: tuple

        Returns
        =======
        Sent via DBus.
        :returns: a dict, with the u'ident' you gave, and either:
            - u'result': which is the result of the computation, or
            - u'error': which is a description of an error during computation.
        :rtype: dict
        """
        # NB: keep this synced with Submit() docstring
        print(u'GOT TO _return_result()')  # DEBUG
        bus_name, submit = None, {}
        if result[0] is None:
            submit[u'error'] = result[2]
            result = (result[1],)
        elif result[0] not in self._job_record:
            return None
        else:
            # pickle the result
            src = StringIO()
            pick = pickle.Pickler(src)
            pick.dump(result[1])
            submit[u'result'] = src.getvalue()
        # prepare DBus submission
        submit[u'ident'] = self._job_record[result[0]][1]
        bus_name = self._job_record[result[0]][0]
        self._bus.call_async(bus_name=bus_name,
                             object_path=u'/MPInterface',
                             dbus_interface=u'ca.elvisproject.vis_client',
                             method=u'_ReturnJob',
                             signature='a{ss}',
                             args=(submit,),
                             reply_handler=lambda: None,
                             error_handler=lambda: None)

    def _add_job_to_tracker(self, ident, sender):
        """
        Add a job to the internal job tracker. Get an index value that we'll use to know when the
        job has completed.

        Parameters
        ==========
        :param ident: The client's identification string.
        :type ident: basestring or None
        :param sender: The client's DBus bus name.
        :type sender: basestring

        Returns
        =======
        :returns: Our internal tracking number that you must submit to the job's function as the
            first argument, which should be returned to us. This is how we know where to return it,
            and what "ident" to give it.
        :rtype: basestring
        """
        # generate a new pseudo-random string for our local ident
        n = 16  # length of the ident strings
        our_ident = u''.join([random.choice(u'qwertyuiopasdfghjklzxcvbnm') for _ in xrange(n)])
        while our_ident in self._job_record:
            our_ident = u''.join([random.choice(u'qwertyuiopasdfghjklzxcvbnm') for _ in xrange(n)])
        # add new record
        self._job_record[our_ident] = (sender, ident)
        return our_ident

    def _process_command(self, command):
        """
        When we were sent a command via DBus, it will be sent here.

        Parameters
        ==========
        :param command: The command sent to the server.
        :type command: basestring

        Valid Commands
        ==============
        - u'shutdown': To close the server program.
        """
        if u'shutdown' == command:
            self._close_the_pool()
            APP.exit(0)

    @dbus.service.method(u'ca.elvisproject.vis_server',
                         in_signature=u'a{ss}',
                         sender_keyword=u'sender')
    def Submit(self, specs, sender):  # pylint: disable=C0103
        """
        Submit a job for multiprocessing. Call this asynchronously via DBus.

        Call from DBus
        ==============
        dbus.SessionBus().call_async(bus_name=u'ca.elvisproject.vis_server',
                                     object_path=u'/Multiprocessor',
                                     dbus_interface=u'ca.elvisproject.vis_server',
                                     method=u'Submit',
                                     signature='a{ss}',
                                     args=(PARAMETERS_HERE,),
                                     reply_handler=lambda: None,
                                     error_handler=lambda: None)
        The "args" parameter is a one-element tuple; the element is the dictionary described below.
        If you wish, you can set "reply_handler" and "error_handler" to something more interesting,
        but this method does not purposely return anything useful. Rather, we recommend using the
        call_async() method because it doesn't block.

        Parameters
        ==========
        The dictionary provided must map strings to strings. Each dictionary key should be one of
        the following. The values therein must all be pickled (since there is no feasible way for
        us to know which basestring object is supposed to be a string and which a pickled object).
        Further, DBus dictionaries must be string-to-string mappings, so that's what we have.

        Valid keys:
        - ident: for your own use. This will be included unchanged in the dict returned to you. It
          must be a string, but may be anything (pickled or not). Optional.
        - func: the function to run. This function must:
            - accept at least one argument
            - return a 2-tuple
            - return the first argument as the first element of the tuple
            - return everything else you want as the second element of the tuple
            - be a module-level function, importable by the worker process
            - exist within the PYTHONPATH or "vis" namespace
        - args: a tuple of the arguments to send to "func" as arguments
        - command: If you wish to issue a control command to the server, you should send a dict
            with only this key, whose value should be one of the following:
            - u'shutdown': to stop execution

        How to Get Results
        ==================
        Don't call us---we'll call you. You must implement the u'ca.elvisproject.vis_client' DBus
        interface on the u'/MPInterface' object path. We will keep track of your bus name, so you
        needn't worry about your results getting sent to another vis_client instance, or even about
        not actually being a vis_client.

        The dict has these keys:
        - ident: the "ident" you gave to this method
        - result: index 1 of the 2-tuple from the function you provided (remember the first is an
          index value for internal use)

        Note that you may get an error returned to you, in which case, the dict has these keys:
        - ???
        """
        # did we receive a command?
        if u'command' in specs:
            self._process_command(specs[u'command'])
            return None
        # unpack our settings
        client_ident = specs[u'ident'] if u'ident' in specs else None
        func = specs[u'func'] if u'func' in specs else None
        args = specs[u'args'] if u'args' in specs else None
        # register the job
        our_ident = self._add_job_to_tracker(client_ident, sender)
        # check for validity
        if func is None or args is None:
            self._return_result((None, our_ident, u'Neither "func" nor "args" can be None.'))
            return None
        # unpickle the function and arguments
        dst = StringIO(func)
        unpick = pickle.Unpickler(dst)
        function = unpick.load()
        dst = StringIO(args)
        unpick = pickle.Unpickler(dst)
        arguments = unpick.load()
        # submit the job
        from vis.analyzers.indexer import stream_indexer
        self._pool.apply_async(function, (our_ident, arguments), callback=self._return_result)
        print(u'SUBMITTED JOB')  # DEBUG

    @dbus.service.method(u'ca.elvisproject.vis_server', out_signature=u'i')
    def Status(self):  # pylint: disable=C0103
        """
        Check the server is alive. This method should be called via DBus as a way to know whether
        the vis_server is responsive.

        Returns
        =======
        :returns: 42 if the server is running normally; 0 if the server is shutting down
        :rtype: int
        """
        print(u'returning status')  # DEBUG
        if self._pool is not None:
            return 42
        else:
            return 0


def main():
    "Main method."
    APP = QtCore.QCoreApplication([])
    my_mpc = Multiprocessor()
    APP.aboutToQuit.connect(my_mpc._close_the_pool)  # pylint: disable=W0212
    sys.exit(APP.exec_())

if __name__ == u'__main__':
    main()
