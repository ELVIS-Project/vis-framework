#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/mpcontroller.py
# Purpose:                Manage a process pool for use by vis
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
Manage a process pool for use by vis.
"""

# Test file for a multiprocessing model for vis.
from multiprocessing import Pool, Pipe
from threading import Thread


class MPController(Thread):
    """
    Use the "shutdown()" method to properly shut down the MPController.

    Before you submit a job, you must call MPController.start(), which must be done only once.

    See "get_pipe()" for instructions on sending jobs.
    """

    def __init__(self):
        super(MPController, self).__init__()
        self._pool = None
        self._pipes = [None for i in xrange(100)]  # we'll obviously have to make this robuster
        self._next_pipe_index = 0
        self._jobs_started = 0
        self._jobs_completed = 0

    def get_pipe(self):
        """
        Make a new Pipe so it can be monitored for new jobs. Returns one of the ends.

        Send a new job through the pipe as a 2-tuple, where the first element is the function to
        call, and the second element is a list of the arguments to use.

        Returns
        =======
        _multiprocessing.Connection:
            One end of the Pipe, to be used for submitting new jobs and receiving completed jobs.

        Use
        ===
        * Send a new job in a 2-tuple:
            * index 0: function to call; it must accept at least one argument that must be returned
                       as index 0 in the resulting 2-tuple
            * index 1: list of arguments for the function; these will be given to the function after
                       the first (required) argument
            Example 1:
            Bare minimum function...
                lambda x: (x, None)
            Example 2:
            Adds "y" to every item in "the_list"...
                lambda x, y, the_list: (x, [z + y for z in the_list])
            NOTE: remember this function must be module-level, *not* in a class.
        * Send u'finished' to close the Pipe after all jobs have been received.
        * Send u'shutdown' when no more jobs will be sent through any Pipes.
        """
        mine, yours = Pipe()
        self._pipes[self._next_pipe_index] = mine
        self._next_pipe_index += 1
        return yours

    def _return_result(self, res):
        """
        A callback method for Pool.apply_async().

        "res" is a 2-tuple that has the index, in self._pipes, for where to send the result, and
        the result to send.
        """
        self._jobs_completed += 1
        try:
            self._pipes[res[0]].send(res[1])
        except IOError:
            # TODO: this happens when the Pipe was closed before we could send the result; we should
            # do something more useful about this, but what?!
            print('** IOError: the MPController could not return something to its submitter')

    def run(self):
        """
        Monitor all the pipes for new jobs to complete. You cannot submit jobs to this instance
        before calling this method.
        """
        # make sure we won't start another Pool-and-loop by accient
        if self._pool is not None:
            return None
        # set up
        self._pool = Pool()
        keep_going = True
        while keep_going:
            for pipe_i in xrange(len(self._pipes)):
                # don't ask None for a message
                if self._pipes[pipe_i] is None:
                    continue

                # see if there's a message; if so, get it
                this = None
                if self._pipes[pipe_i].poll():
                    this = self._pipes[pipe_i].recv()

                # if we got a message, process it
                if this is not None:
                    if u'shutdown' == this:
                        # TODO: what if jobs are submitted before this, but we would only see them
                        # after? As in: job submitted to lower-index pipe that we passed before
                        # "shutdown" was sent on a higher-index pipe...
                        keep_going = False
                        self._pipes[pipe_i].close()
                    elif u'finished' == this:
                        self._pipes[pipe_i].close()
                    else:
                        # prepare the list of arguments
                        the_args = [pipe_i]  # pipe index
                        the_args.extend([each for each in this[1]])  # actual arguments
                        # so we know how many jobs we've started
                        self._jobs_started += 1
                        # start it
                        self._pool.apply_async(this[0],
                                               tuple(the_args),
                                               callback=self._return_result)

    def shutdown(self):
        """
        Stop the MPController, then block until all jobs have been returned to their callers.

        TODO: if a job raised an uncaught exception, we can't know about it, and this method will
        block indefinitely.
        """
        # stop the job-checker and the pool
        pipe_end = self.get_pipe()
        pipe_end.send(u'shutdown')
        pipe_end.close()
        # stop the pool
        self._pool.close()
        self._pool.join()
        del self._pool
        # wait until all jobs have been returned
        while self._jobs_started > self._jobs_completed:
            pass


# Sample MPController program below ----------------------------------------------------------------


def add_something(pipe_i, add_this, the_list):
        return (pipe_i, [z + add_this for z in the_list])


class ThingProducer(object):
    """
    Add things to lists of integers.
    """

    def __init__(self, things, mpc):
        """
        Parameters
        ==========
        :param things : [[int]]
            A list of lists of integers that we'll add things to.

        :param mpc : MPController
            An instance of MPController that we'll use for multiprocessing.
        """
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
            self._pipe_end.send((add_something, [5, self._things[i]]))
            self._jobs_submitted += 1
            self._pipe_end.send((add_something, [10, self._things[i]]))

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


if '__main__' == __name__:
    the_lists = [[-5, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [-4, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [-3, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [-2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [-1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [0, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [3, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [4, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [5, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [6, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [7, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                 [8, 2, 3, 4, 5, 6, 7, 8, 9, 10]]

    mpc = MPController()
    mpc.start()

    the_tp = ThingProducer(the_lists, mpc)
    the_tp.start_stuff()
    results = the_tp.get_stuff()
    for res in results:
        print('ThingProducer produced ' + str(res))

    mpc.shutdown()
