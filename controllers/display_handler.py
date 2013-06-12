#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: DisplayHandler.py
# Purpose: Holds the DisplayHandler controller.
#
# Copyright (C) 2012, 2013 Jamie Klassen, Christopher Antila
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
"""
Holds the DisplayHandler controller.
"""

# Imports from...
# matplotlib
import matplotlib.pyplot as plt
# PyQt
from PyQt4 import QtCore, QtGui
# music21
from music21 import graph, base
# vis
from controller import Controller
import file_output
from views.Ui_text_display import Ui_Text_Display
import OutputLilyPond


class DisplayHandler(Controller):
    """
    This class takes an ExperimentResults object, if relevant determines which
    Display format to use and its DisplaySettings, then actually displays the
    results for the user.

    Really, the DisplayHandler waits for an Experimenter.experimented
    signal, then processes it.
    """

    # PyQt4 Signals
    # -------------
    # when the user should be able to see the results of an experiment on the
    # screen in a particular format
    display_shown = QtCore.pyqtSignal()
    # description of an error in the DisplayHandler
    error = QtCore.pyqtSignal(str)
    # obvious
    status = QtCore.pyqtSignal(str)

    def __init__(self):
        """
        Create a new DisplayHandler instance.
        """
        super(DisplayHandler, self).__init__()  # required for signals

    @QtCore.pyqtSlot(tuple)  # for Experimenter.experiment_finished
    def show_result(self, signal_result):
        """
        Slot for the Experimenter.experiment_finished signal. This method is
        called when the Experimenter controller has finished analysis.

        The argument is a 2-tuple, where the first element is a list of the
        possible Display objects to use for the results, and the second is the
        data needed by that Display object.

        If there is more than one possible display type, the DisplayHandler will
        somehow choose.

        NOTE: the list of possible Display types must have this format:
        ['FileOutput'] to use the class FileOutputDisplay.
        """

        # (1) Choose which display type to use
        # Currently, we can't deal with choosing Display class after the Experiment has run,
        # so we'll have to panic if there is more than one choice.
        if u'error' == signal_result[0]:
            # there was an error in the Experimenter, already reported
            self.display_shown.emit()
            return
        elif 1 < len(signal_result[0]):
            msg = 'Internal Error: DisplayHandler cannot choose its display method independently.'
            self.error.emit(msg)
            self.display_shown.emit()
            return
        else:
            # NOTE: remember to update this selection code as different Display objects are added
            if 'SpreadsheetFile' in signal_result[0]:
                display_type = SpreadsheetFileDisplay
            elif 'StatisticsListDisplay' in signal_result[0]:
                display_type = StatisticsListDisplay
            elif 'GraphDisplay' in signal_result[0]:
                display_type = GraphDisplay
            elif 'LilyPondDisplay' in signal_result[0]:
                display_type = LilyPondDisplay

        # (2) Instantiate and show the display
        this_display = display_type(self, signal_result[1])
        msg = 'Results are displayed. Please close the display to continue using vis.'
        self.status.emit(msg)
        this_display.show()

        # (3) Send the signal of success
        self.display_shown.emit()


class Display(object):
    """
    Base class for all Displays.
    """

    def __init__(self, controller, data, settings=None):
        """
        Create a new Display.

        There are three arguments, the first two of which are mandatory:
        - controller : the DisplayHandler controller to which this Display belongs
        - data : argument of any type, as required by the Display subclass
        - settings : the optional ExperimentSettings object
        """
        # NOTE: You must re-implement this, and change "object" to "Display"
        super(Display, self).__init__()
        self._controller = controller
        self._data = data
        self._settings = settings

    def show(self):
        """
        Show the data in the display.

        This method emits a VisSignals.display_shown signal when it finishes.
        """
        # NOTE: You must reimplement this method in subclasses.
        self._controller.display_shown.emit()


class FileOutputDisplay(Display):
    """
    Saves a string into a file.

    You can use this class from another Display subclass, in a situation where the other Display
    subclass converts a non-string result into a string, then calls this class.
    """

    def __init__(self, controller, data, settings=None):
        """
        Create a new FileOutputDisplay.

        There are three arguments, the first two of which are mandatory:
        - controller : the DisplayHandler controller to which this Display belongs
        - data : a string that should be the contents of the text file
        - settings : the optional ExperimentSettings object

        The filename is determined dynamically by the show() method.
        """
        # NOTE: You do not need to reimplement this method for subclasses.
        super(FileOutputDisplay, self).__init__(controller, data, settings)

    def show(self):
        """
        Saves the data in a file on the filesystem.

        This method emits a VisSignals.display_shown signal when it finishes.
        """

        # get a VisTextDisplay to handle the display, then possible saving, of the data
        veeteedee = VisTextDisplay(self._data)
        veeteedee.trigger()


class SpreadsheetFileDisplay(Display):
    """
    Converts a list of tuples into a string suitable for CSV-format output, then uses the
    FileOutputDisplay class to save the result into a file.
    """

    def __init__(self, controller, data, settings=None):
        """
        Create a new SpreadsheetFileDisplay.

        There are three arguments, the first two of which are mandatory:
        - controller : the DisplayHandler controller to which this Display belongs
        - data : a list of tuples
        - settings : the optional ExperimentSettings object

        Note: The "data" argument is converted to a CSV-format string with the
        following assumptions:
        - each tuple represents a row in the spreadsheet (and a \n character is printed after)
        - each value in the tuple is run through its str() method
        - no header information is appended
        """
        # NOTE: You must re-implement this, and change "object" to "Display"
        super(SpreadsheetFileDisplay, self).__init__(controller, data, settings)

    def show(self):
        """
        Show the data in the display.

        The FileOutputDisplay instance emits the VisSignals.display_shown signal.
        """
        post = ''

        for each_row in self._data:
            for each_column in each_row:
                post += str(each_column) + ', '
            # remove the final ', ' and append a newline
            post = post[:-2] + '\n'

        # We will *not* emit this signal, but rather let the FileOutputDisplay do it.
        # self._controller.display_shown.emit()

        # Create a FileOutputDisplay and use it
        f_o_disp = FileOutputDisplay(self._controller, post, self._settings)
        f_o_disp.show()


class StatisticsListDisplay(Display):
    """
    Converts a list of 2-tuples into a string for file output.

    In each 2-tuple, the first object should represent something meaningful when run through str(),
    and the second object should be an int that represents the occurrences of the thing.

    The total number of things is printed before the number of each thing.

    If the first element is a 3-tuple, and the first object is the string 'description', then the
    next two elements are used as table headers for the rest of the data.
    """

    def __init__(self, controller, data, settings=None):
        """
        Create a new StatisticsListDisplay.

        There are three arguments, the first two of which are mandatory:
        - controller : the DisplayHandler controller to which this Display belongs
        - data : a list of tuples
        - settings : the optional ExperimentSettings object

        Note: The "data" argument is converted to a string with the following assumptions:
        - each tuple represents a row in the table (and a \n character is printed after)
        - each 0th element in the tuple is run through its str() method
        - each 1st element must be an int
        - if the first tuple is a 3-tuple, and the 0th element is the string 'description', the
        following two elements are used as table headers for the rest of the data
        """
        # NOTE: You must re-implement this, and change "object" to "Display"
        super(StatisticsListDisplay, self).__init__(controller, data, settings)

    def show(self):
        """
        Show the data in the display.

        The FileOutputDisplay instance emits the VisSignals.display_shown signal.
        """
        header_data = ''
        post = ''
        total_occurrences = 0

        # ensure the Experiment produced valid output
        if 0 == len(self._data):
            msg = u'StatisticsListDisplay: The Experiment produced no data! Cannot continue.'
            self._controller.error.emit(msg)
            return None

        # prepare the header data (except total number of occurrences)
        if 3 == len(self._data[0]) and 'description' == self._data[0][0]:
            header_data += self._data[0][1] + u': ' + self._data[0][2] + u'\n'
            self._data = self._data[1:]
        else:
            header_data += u'object:  occurrences\n'

        header_data += u'========================\n'

        # prepare per-object data
        for each_row in self._data:
            # add the object to the table
            post += str(each_row[0]) + ':\t' + str(each_row[1]) + '\n'
            # count the number of things to the total number of things
            total_occurrences += each_row[1]

        # add the total occurrences after the header, and concatenate both parts
        post = header_data + 'Total occurrences of displayed objects: ' + \
            str(total_occurrences) + '\n' + post

        # We will *not* emit this signal, but rather let the FileOutputDisplay do it.
        # self._controller.display_shown.emit()

        # Create a FileOutputDisplay and use it
        f_o_disp = FileOutputDisplay(self._controller, post, self._settings)
        f_o_disp.show()


class VisTextDisplay(Ui_Text_Display):
    """
    I brought this class back from vis7 as a temporary measure, meant to satisfy our need to see
    results before saving them, just for the Hack Day in May 2013.
    """
    def __init__(self, text):
        """
        Make a new VisTextDisplay
        """
        self.text_display = QtGui.QDialog()
        self.setupUi(self.text_display)
        self.text = text
        self.show_text.setPlainText(text)

    def trigger(self):
        """
        Cause the window to show up.
        """
        self.btn_save_as.clicked.connect(self.save_as)
        self.btn_close.clicked.connect(self.close)
        self.text_display.exec_()

    def save_as(self):
        """
        Save the file.
        """
        filename = str(QtGui.QFileDialog.getSaveFileName(None,
                        'Save As',
                        '',
                        '*.txt'))
        result = file_output.file_outputter(self.text, filename, overwrite=True)
        if result[1] is not None:
            QtGui.QMessageBox.information(None,
                'File Output Failed',
                result[1],
                QtGui.QMessageBox.StandardButtons(
                    QtGui.QMessageBox.Ok),
                    QtGui.QMessageBox.Ok)

    def close(self):
        """
        Close the window.
        """
        self.text_display.done(0)


class GraphDisplay(Display):
    """
    Output a graph.
    """

    def __init__(self, controller, data, settings=None):
        """
        Create a new Display.

        There are three arguments, the first two of which are mandatory:
        - controller : the DisplayHandler controller to which this Display belongs
        - data : A list of two-tuples, where the first is a descriptive string and the second is
                 a number... like this...
                 [('m3 -P4 M6', 10), ('M3 -P4 m6', 4), ...]
        - settings : the optional ExperimentSettings object, ignored in GraphDisplay
        """
        # NOTE: You must re-implement this, and change "object" to "Display"
        super(GraphDisplay, self).__init__(controller, data, settings)

    def show(self):
        """
        Show the data in the display.

        This method emits a VisSignals.display_shown signal when it finishes.
        """

        # ensure the Experiment produced valid output
        if 0 == len(self._data):
            msg = u'GraphDisplay: The Experiment produced no data! Cannot continue.'
            self._controller.error.emit(msg)
            return None

        # Filter out the "description" fields, if they exist
        if u'description' == self._data[0][0]:
            self._data = self._data[1:]

        # prepare the GraphHistogram
        try:  # this has something to do with Windows being Windows
            import matplotlib
            if 'matplotlib' in base._missingImport:
                base._missingImport.remove('matplotlib')
        except:
            pass
        the_graph = graph.GraphHistogram(doneAction=None)
        the_graph.setData(self._data)
        the_graph.setTitle('A Chart Produced by vis')

        # figure out x-axis ticks
        garbage_tick_list = []
        for i in xrange(len(self._data)):
            # make a label that's like "things: occurrences"
            x_label = self._data[i][0] + u': ' + unicode(self._data[i][1])
            garbage_tick_list.append((i + 0.4, x_label))
        the_graph.setTicks('x', garbage_tick_list)
        the_graph.xTickLabelHorizontalAlignment = 'center'
        setattr(the_graph, 'xTickLabelRotation', 45)
        the_graph.setAxisLabel('x', 'Object')
        the_graph.setAxisLabel('y', 'Number')

        # figure out y-axis ticks
        max_height = max([i[1] for i in self._data])
        tick_dist = max(max_height / 10, 1)
        ticks = []
        k = 0
        while k * tick_dist <= max_height:
            k += 1
            ticks.append(k * tick_dist)
        the_graph.setTicks('y', [(k, k) for k in ticks])

        # process and show the data; emit completion signal
        # BEGIN SEGMENT COPIED FROM graph.py
        # figure size can be set w/ figsize=(5,10)
        the_graph.fig = plt.figure()
        the_graph.fig.subplots_adjust(left=0.15)
        the_subplot = the_graph.fig.add_subplot(1, 1, 1)

        list_of_x = []
        list_of_y = []
        color = graph.getColor('Steel Blue')
        for ecks in xrange(len(self._data)):
            list_of_x.append(ecks + 0.4)
            list_of_y.append(self._data[ecks][1])
        the_subplot.bar(list_of_x,
            list_of_y,
            width=the_graph.binWidth,
            alpha=the_graph.alpha,
            color=color,
            edgecolor=color)

        the_graph._adjustAxisSpines(the_subplot)
        the_graph._applyFormatting(the_subplot)
        the_graph.done()
        # END SEGMENT COPIED FROM graph.py

        the_graph.show()
        self._controller.display_shown.emit()


class LilyPondDisplay(Display):
    """
    Prepares a
    """

    def __init__(self, controller, data, settings=None):
        """
        Create a new LilyPondDisplay.

        There are three arguments, the first two of which are mandatory:
        - controller : the DisplayHandler controller to which this Display belongs
        - data : argument of any type, as required by the Display subclass
        - settings : the optional ExperimentSettings object
        """
        super(LilyPondDisplay, self).__init__(controller, data, settings)

    def show(self):
        """
        Show the data in the display.

        This method emits a VisSignals.display_shown signal when it finishes.
        """
        for i in xrange(len(self._data)):
            pathname = ''
            extension = '.ly'
            # get the place they want to save the LilyPond file
            file_save = QtGui.QFileDialog.getSaveFileName(None,
                u'Where to Save the LilyPond File?',
                u'.ly',
                u'',
                None)
            # remove the extension, if they put it
            if len(file_save) > '.ly' == file_save[-3:]:
                pathname = file_save[:-3]
            else:
                pathname = file_save
            # make sure we have a (potentially) viable pathname
            if len(pathname) < 1:
                msg = u'LilyPond pathname is not viable.' + unicode(pathname)
                self._controller.error.emit(msg)
                return
            # output the LilyPond file
            ly_me = file_output.file_outputter(
                contents=self._data[i],
                pathname=pathname,
                extension=extension,
                overwrite=True)
            # run LilyPond
            if ly_me[1] is not None:
                # There was an error while writing the file, so we can't continue
                msg = 'File output problem in LilyPondDisplay: \n' + str(ly_me[1])
                self._controller.error.emit(msg)
                return
            else:
                OutputLilyPond.run_lilypond(ly_me[0])
        self._controller.display_shown.emit()
