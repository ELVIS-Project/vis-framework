#! /usr/bin/python
# -*- coding: utf-8 -*-

# Test file for a multiprocessing model for vis.
from multiprocessing import Pool, Pipe
from threading import Thread


def run_me(the_list, pipe_index):
    return (pipe_index, [x + 5 for x in the_list])


class MPController(Thread):
    """
    The following two lines of code shuts down the MPController:
    >>> pipe_end = mpc.get_pipe()
    >>> pipe_end.send(u'shutdown')
    """

    def __init__(self):
        super(MPController, self).__init__()
        self.pool = Pool()
        self._pipes = [None for i in xrange(100)]  # we'll obviously have to make this robuster
        self._next_pipe_index = 0

    def get_pipe(self):
        """
        Make a new Pipe so it can be monitored for new jobs. Returns one of the ends.

        You should send a new job in the pipe as a 2-tuple, where the first element is the function
        to call, and the second element is the arguments to use.

        Send u'finished' when no more jobs will be sent through a Pipe.
        Send u'shutdown' when no more jobs will be sent through any Pipes, and you want to disallow
        new Pipes.
        """
        mine, yours = Pipe()
        self._pipes[self._next_pipe_index] = mine
        self._next_pipe_index += 1
        return yours

    def return_result(self, res):
        """
        A callback method for Pool.apply_async().

        "res" is a 2-tuple that has the index, in self._pipes, for where to send the result, and
        the result to send.
        """
        self._pipes[res[0]].send(res[1])

    def _shutting_down(self):
        """
        Does things to ensure no data is lost when we shut down.
        """
        pass

    def run(self):
        """
        Monitor all the pipes for new jobs to complete.
        """
        keep_going = True
        while keep_going:
            for pipe_i in xrange(len(self._pipes)):
                if self._pipes[pipe_i] is None:
                    continue
                this = None
                try:
                    if self._pipes[pipe_i].poll():
                        this = self._pipes[pipe_i].recv()
                except EOFError:
                    print('EOFError')  # DEBUG

                if this is not None:
                    if u'shutdown' == this:
                        keep_going = False
                    elif u'finished' == this:
                        self._pipes[pipe_i].close()
                    else:
                        self.pool.apply_async(
                            this[0],
                            (this[1], pipe_i),
                            callback=self.return_result)
        self._shutting_down()

    def close_and_join(self):
        self.pool.close()
        self.pool.join()


class ThingProducer(object):

    def __init__(self, thing, pipe_end):
        self.thing = thing
        self.pipe_end = pipe_end

    def start_stuff(self):
        self.pipe_end.send((run_me, self.thing))


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

the_tps = []

for each_list in the_lists:
    this_tp = ThingProducer(each_list, mpc.get_pipe())
    this_tp.start_stuff()
    the_tps.append(this_tp)

for tp_index in xrange(len(the_tps)):
    print('tp index ' + str(tp_index) + ' has ' + str(the_tps[tp_index].pipe_end.recv()))
    the_tps[tp_index].pipe_end.send('finished')
    the_tps[tp_index].pipe_end.close()

pipe_end = mpc.get_pipe()
pipe_end.send(u'shutdown')

mpc.close_and_join()
