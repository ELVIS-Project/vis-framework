#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/mpinterface.py
# Purpose:                An interface for the vis multiprocessing infrastructure.
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
This module provides the MPInterface class, which is an interface to the vis multiprocessing
infrastructue. Although currently intended for SMP use, the MPInterface abstraction layer allows
you to change the multiprocessing strategy for all vis classes simply by modifying the MPInterface
implementation.
"""

import threading
import pickle
import cStringIO
import random
from PyQt4 import QtCore
import dbus
import dbus.service  # required for the "service" modules to be accessible

# set up the PyQt main loop with DBus
from dbus.mainloop.qt import DBusQtMainLoop  # required for DBusQtMainLoop to be accessible
DBusQtMainLoop(set_as_default=True)


class MPInterface(dbus.service.Object):  # pylint: disable=R0923
    "The MPInterface class is an interface to the vis multiprocessing infrastructure."

    def __init__(self):
        # pylint: disable=E1002
        super(MPInterface, self).__init__()
        # set up DBus
        self._bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(u'ca.elvisproject.vis_client', bus=self._bus)
        dbus.service.Object.__init__(self, bus_name, u'/MPInterface')
        # instance variables
        self._refs = []  # job reference numbers---actually unicode strings
        self._submitted = 0  # number of jobs submitted
        self._received = 0  # number of completed jobs received
        self._fetched = 0  # number of completed jobs fetched
        self._results = {}  # results of execution, by job number

    @dbus.service.method(u'ca.elvisproject.vis_client', in_signature=u'a{ss}')
    def _ReturnJob(self, result):  # pylint: disable=C0103
        """
        This method receives results from the vis Multiprocessor server.

        Parameters
        ==========
        :param results: Two-element dictionary, where u'ident' is the "ref" for this MPInterface
            instance, and u'result' is the pickled result of the function we submitted.
        :type results: dict
        """
        if result[0] not in self._refs:
            # dunno?
            pass
        else:
            self._results[result[0]] = result[1]
            self._received += 1

    def _get_ref(self):
        """
        Get a reference number for a new job. It will automatically be stored in the reference
        number database, and the number of submitted jobs will be incremented by one.

        Returns
        =======
        :returns: A unique, alphanumeric reference number for this job.
        :rtype: unicode
        """
        n = 16  # length of the ident strings
        ident = u''.join([random.choice(u'qwertyuiopasdfghjklzxcvbnm') for _ in xrange(n)])
        while ident in self._refs:
            ident = u''.join([random.choice(u'qwertyuiopasdfghjklzxcvbnm') for _ in xrange(n)])
        self._submitted += 1
        return ident

    def submit(self, func, *args):
        """
        Submit work to the multiprocessing infrastructure.

        Parameters
        ==========
        :param func: A module-level function to execute.
        :type func: function
        :param args: Arguments to supply to the function. You must handle pickling and unpickling
            of music21 streams, both here and in your function.
        :type args: list of "pickleable" objects

        Returns
        =======
        :returns: A unique, alphanumeric reference number for this job.
        :rtype: unicode

        Raises
        ======
        PicklingError: If one or more of the args cannot be pickled.
        """
        submit = {}
        # the function
        src = cStringIO.StringIO()
        pick = pickle.Pickler(src)
        try:
            pick.dump(func)
        except TypeError:
            msg = u'Could not pickle un-import-able function for multiprocessing' + unicode(func)
            raise pickle.PicklingError(msg)
        submit[u'func'] = src.getvalue()
        # the args
        src = cStringIO.StringIO()
        pick = pickle.Pickler(src)
        try:
            pick.dump(args)
        except TypeError:
            msg = u'Could not pickle arguments for multiprocessing: ' + unicode(args)
            raise pickle.PicklingError(msg)
        submit[u'args'] = src.getvalue()
        # our ident
        submit[u'ident'] = self._get_ref()
        res = self._bus.call_async(bus_name=u'ca.elvisproject.vis_server',
                                   object_path=u'/Multiprocessor',
                                   dbus_interface=u'ca.elvisproject.vis_server',
                                   method=u'Submit',
                                   signature='a{ss}',
                                   args=(submit,),
                                   reply_handler=lambda: None,
                                   error_handler=lambda: None)
        return submit[u'ident']

    def waiting_on(self):
        """
        Find out how many jobs have not yet been completed. If no jobs have been submitted, this
        will be 0. Failed jobs are counted as "completed." The number of fetched jobs is not
        considered.

        Returns
        =======
        :returns: The number of jobs that have not yet been completed.
        :rtype: int
        """
        return self._submitted - self._received

    def poll(self, ref=None):
        """
        Find out if there are completed jobs that have not been fetched. You can also find out if a
        specific job is completed but has not been fetched.

        Parameters
        ==========
        :param ref: The reference number of a job. Optional.
        :type ref: int

        Returns
        =======
        :returns: Whether or not there are completed jobs that have not been fetched. If a reference
            number was given as input, returns whether that job has been completed and not fetched.
            Returns None if the reference number is invalid. Returns False if the referenced job
            has not been completed or has already been fetched.
        :rtype: bool or None
        """
        if ref is None:
            post = self._received > self._fetched
        elif ref not in self._refs:
            post = None
        elif ref in self._results:
            post = True
        else:
            post = False
        return post

    def fetch(self, ref=None):
        """
        Fetch the result of a completed job.

        Parameters
        ==========
        :param ref: The reference number of a job. Optional.
        :type ref: int

        Returns
        =======
        :returns: A 2-tuple with the job reference number and the result of the job.
        :rtype: tuple of int and pickleable type

        Raises
        ======
        EOFError: If there are no completed -but-unfetched jobs.
        LookupError: If the job reference number is invalid, or if the referred job has already
            been fetched or is not yet available.
        """
        if ref is not None:
            if ref not in self._refs:
                raise LookupError(u'Invalid job reference number.')
            elif ref not in self._results:
                raise LookupError(u'Job not completed or already fetched.')
        elif not self.poll():
            raise EOFError(u'There are no jobs to be fetched.')
        elif ref is None:
            # we'll find the "first" completed job
            # NOTE: does this generator save any time/memory over calling keys() ?
            for each_ref in self._results.iterkeys():
                ref = each_ref
                break
        # unpickle everything to prepare for return
        dst = cStringIO.StringIO(self._results[ref])
        upick = pickle.Unpickler(dst)
        post = (ref, upick.load())
        # (remove the stored result, increment number of returned results)
        del self._results[ref]
        self._fetched += 1
        return post


class _LoopHandler(QtCore.QCoreApplication, threading.Thread):
    """
    This class exists for DBus-related reasons.
    """
    def __init__(self):
        QtCore.QCoreApplication.__init__(self, [])
        threading.Thread.__init__(self)

    def run(self):
        self.exec_()


APP = _LoopHandler()
APP.start()
