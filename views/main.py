#! /usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:             vis
# Program Description:      Measures sequences of vertical intervals.
#
# Filename: views/main.py
# Purpose: Hold VisQtMainWindow class, which controls the GUI for vis' PyQt4 interface.
#
# Copyright (C) 2012, 2013 Jamie Klassen, Christopher Antila
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
#-------------------------------------------------------------------------------
"""
Hold VisQtMainWindow class, which controls the GUI for vis' PyQt4 interface.
"""

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from vis.models.pyqt import ListOfFiles, WorkflowWrapper
from vis.views.VisOffsetSelector import VisOffsetSelector
from vis.views.web_view import VisWebView
from vis.views.Ui_main_window import Ui_MainWindow


class VisQtMainWindow(QtGui.QMainWindow, QtCore.QObject):
    "This class makes the GUI-controlling objects for vis' PyQt4 interface."

    def __init__(self):
        "Parameter is an instance of VisController to use for sending signals."
        super(VisQtMainWindow, self).__init__()  # required for signals
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._tool_import()
        self.show()
        # Hold a lists of checkboxes, "Edit" buttons, and layouts that represent
        # the parts in a piece for the "assemble" panel
        self.part_checkboxes = None
        self.edit_buttons = None
        self.part_layouts = None
        # Setup GUI-only Signals
        mapper = [
            # Workflow management
            (self.ui.btn_step1.clicked, self._check_for_pieces),
            (self.ui.btn_step2.clicked, self._start_the_analysis),
            # To operate the GUI
            (self.ui.btn_choose_files.clicked, self._tool_import),
            (self.ui.btn_about.clicked, self._tool_about),
            (self.ui.btn_analyze.clicked, self._tool_analyze),
            (self.ui.btn_experiment.clicked, self._tool_experiment),
            (self.ui.btn_file_add.clicked, self._add_files),
            (self.ui.btn_file_remove.clicked, self._remove_files),
            (self.ui.btn_show_results.clicked, self._prepare_experiment_submission),
            (self.ui.line_piece_title.editingFinished, self._update_piece_title),
            (self.ui.line_offset_interval.editingFinished, self._update_offset_interval),
            (self.ui.btn_choose_note.clicked, self._launch_offset_selection),
            (self.ui.chk_repeat_identical.stateChanged, self._update_repeat_identical),
            (self.ui.btn_cancel_operation.clicked, self._cancel_operation),
            # About part combinations
            (self.ui.line_compare_these_parts.editingFinished, self._add_parts_combo_by_line_edit),
            (self.ui.btn_add_check_combo.clicked, self._add_parts_combination),
            (self.ui.gui_pieces_list.selection_changed, self._update_pieces_selection),
            (self.ui.chk_all_voices.clicked, self._all_voices),
            (self.ui.chk_all_voice_combos.clicked, self._all_voice_pairs),
            # Things causing GUI adjustment
            (self.ui.rdo_consider_interval_ngrams.clicked, self._update_experiment_from_object),
            (self.ui.rdo_consider_intervals.clicked, self._update_experiment_from_object),
            (self.ui.rdo_consider_score.clicked, self._update_experiment_from_object),
            # Clicked an output format radio button (on the GUI: "How to Show Results")
            (self.ui.rdo_table.clicked, self._output_format_changed),
            (self.ui.rdo_chart.clicked, self._output_format_changed),
            (self.ui.rdo_score.clicked, self._output_format_changed),
            # "Shared Settings" from the "Analyzer" panel
            (self.ui.rdo_heedQuality.clicked, self._update_quality),
            (self.ui.rdo_noHeedQuality.clicked, self._update_quality),
            (self.ui.rdo_simple.clicked, self._update_octaves),
            (self.ui.rdo_compound.clicked, self._update_octaves),
        ]
        for signal, slot in mapper:
            signal.connect(slot)
        # Setup the progress bar
        self.ui.progress_bar.setMinimum(0)
        self.ui.progress_bar.setMaximum(100)
        self.ui.progress_bar.setValue(42)
        # set "Ctrl + q" to close the window
        QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Q),
                        self,
                        self.close,
                        context=Qt.WindowShortcut)
        # visX setup
        self._list_of_ips = None  # holds the IndexedPiece instances
        self._list_of_files = ListOfFiles()
        self.ui.gui_file_list.setModel(self._list_of_files)
        self._work_wrap = WorkflowWrapper()
        self.ui.gui_pieces_list.setModel(self._work_wrap)
        self._prev_setts = None  # hold settings of previous experiment

    # Methods Doing GUI Stuff ---------------------------------------------------
    # Pressing Buttons in the Toolbar -----------------------
    @QtCore.pyqtSlot()
    def _tool_import(self):
        "Activate the 'import' panel"
        self.ui.main_screen.setCurrentWidget(self.ui.page_choose)
        self.ui.btn_about.setEnabled(True)
        self.ui.btn_choose_files.setEnabled(True)
        self.ui.btn_analyze.setEnabled(False)
        self.ui.btn_experiment.setEnabled(False)
        self.ui.btn_step1.setEnabled(True)
        self.ui.btn_step2.setEnabled(False)
        self.ui.btn_cancel_operation.setVisible(True)

    @QtCore.pyqtSlot()
    def _tool_analyze(self):
        "Activate the 'analyze' panel (corresponding to the Analyzer)."
        self.ui.main_screen.setCurrentWidget(self.ui.page_analyze)
        self.ui.btn_choose_files.setEnabled(False)
        self.ui.btn_analyze.setChecked(True)
        self.ui.btn_about.setEnabled(True)
        self.ui.btn_analyze.setEnabled(True)
        self.ui.btn_experiment.setEnabled(False)
        self.ui.btn_step1.setEnabled(False)
        self.ui.btn_step2.setEnabled(True)
        self.ui.btn_cancel_operation.setVisible(True)
        self._update_pieces_selection()
        self._update_global_settings()

    @QtCore.pyqtSlot()
    def _tool_working(self):
        "Activate the 'working' panel, for when vis is processing."
        self.ui.main_screen.setCurrentWidget(self.ui.page_working)
        # make sure nothing is enabled
        self.ui.btn_about.setEnabled(False)
        self.ui.btn_choose_files.setEnabled(False)
        self.ui.btn_analyze.setEnabled(False)
        self.ui.btn_experiment.setEnabled(False)
        self.ui.btn_step1.setEnabled(False)
        self.ui.btn_step2.setEnabled(False)
        # make sure nothing is checked
        self.ui.btn_about.setChecked(False)
        self.ui.btn_analyze.setChecked(False)
        self.ui.btn_choose_files.setChecked(False)
        self.ui.btn_experiment.setChecked(False)
        # Disable the details-selection until a particular piece is selected
        self.ui.grp_settings_for_piece.setEnabled(False)
        self.ui.grp_settings_for_piece.setVisible(False)

    @QtCore.pyqtSlot()
    def _tool_about(self):
        "Activate the 'about' panel."
        self.ui.main_screen.setCurrentWidget(self.ui.page_about)
        # leave enabled/disabled as-is, but make sure only "about" is checked
        self.ui.btn_about.setChecked(True)
        self.ui.btn_analyze.setChecked(False)
        self.ui.btn_choose_files.setChecked(False)
        self.ui.btn_experiment.setChecked(False)

    @QtCore.pyqtSlot()
    def _tool_experiment(self):
        "Activate the 'show' panel, which corresponds to the Experimenter controller."
        self.ui.main_screen.setCurrentWidget(self.ui.page_show)
        self.ui.btn_about.setEnabled(True)
        self.ui.btn_choose_files.setEnabled(False)
        self.ui.btn_analyze.setEnabled(True)
        self.ui.btn_experiment.setEnabled(True)
        self.ui.btn_experiment.setChecked(True)
        self.ui.btn_step1.setEnabled(False)
        self.ui.btn_step2.setEnabled(False)
        self.ui.btn_cancel_operation.setVisible(False)
        # call the thing to update this panel
        self._update_experiment_from_object()
        # call the thing to to what it says it does
        self._output_format_changed()

    @QtCore.pyqtSlot()
    def _check_for_pieces(self):
        """
        Check there is at least one piece set to be imported. If there is, start importing. If not,
        ask the user to choose some pieces.
        """
        if 0 != self._list_of_files.rowCount():
            self._tool_working()
            # put everything in the WorkflowWrapper, so we can collect settings and whatever
            self._work_wrap.insertRows(None, self._list_of_files.rowCount())
            for new_row, pathname in enumerate(self._list_of_files):
                self._work_wrap.setData((new_row, WorkflowWrapper.filename),
                                        pathname,
                                        QtCore.Qt.EditRole)
            self._tool_analyze()
        else:
            # then ask the user to stop being a jerk
            QtGui.QMessageBox.information(None,
            u"Please Select Files",
            u"""The list of files is empty.

You must choose pieces before we can import them.""",
            QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def _add_files(self):
        "Add files to the 'importer' panel."
        files = QtGui.QFileDialog.getOpenFileNames(
            None,  # parent
            u"Choose Files to Analyze",  # title
            u'',  # default directory
            )  # NB: This should be the 'filter' line, which is below, but commented out... it seems
            # that, for some reason, the filter isn't working. For me on Fedora 17, the result is
            # that all file types are "selectable"... but others have reported occasional issues
            # that entirely prevent them from selecting files. So here we are.
            # 'music21 Files (*.nwc *.mid *.midi *.mxl *.krn *.xml *.md)')  # filter
        if files:
            row_count = self._list_of_files.rowCount()
            self._list_of_files.insertRows(row_count, len(files))
            for i, each_file in enumerate(files):
                self._list_of_files.setData(row_count + i, each_file, QtCore.Qt.EditRole)

    # TODO: re-enable removing files
    @QtCore.pyqtSlot()
    def _remove_files(self):
        """
        Method which finds which files the user has selected for removal and emits a signal
        containing their names.
        """
        # which indices are currently selected?
        #currently_selected = self.ui.gui_file_list.selectedIndexes()
        # take the cheap way out
        QtGui.QMessageBox.information(None,
            "vis",
            "I didn't write that yet.",
            QtGui.QMessageBox.StandardButtons(\
                QtGui.QMessageBox.RestoreDefaults))

    @QtCore.pyqtSlot(str)
    def _update_progress_bar(self, progress):
        """
        Updates the "working" screen in the following ways:
        - If the argument is a two-character string that can be converted into
        an integer, or the string '100', the progress bar is set to that
        percentage completion.
        - If the argument is another string, the text below the progress bar is
        set to that string.
        """
        if not isinstance(progress, (basestring, QtCore.QString)):
            return None
        else:
            if u'100' == progress:
                self.ui.progress_bar.setValue(100)
            elif 3 > len(progress):
                try:
                    new_val = int(progress)
                    self.ui.progress_bar.setValue(new_val)
                except ValueError:
                    self.ui.lbl_currently_processing.setText(progress)
            else:
                self.ui.lbl_currently_processing.setText(progress)

    # TODO: re-enable operation cancellation
    @QtCore.pyqtSlot()
    def _cancel_operation(self):
        "If possible, cancel a running operation (import, analysis, experiment)."
        # confirm with the user that they want to cancel whatever's happening
        QtGui.QMessageBox.question(
            None,
            u"Confirm",
            u"This doesn't work yet!\n\nAre you sure you want to cancel the running operation?",
            QtGui.QMessageBox.StandardButtons(
                QtGui.QMessageBox.No |
                QtGui.QMessageBox.Yes))
        return None

    @staticmethod
    def _error_reporter(description):
        "Notify the user that an error has happened. Parameter is a description of the error."
        QtGui.QMessageBox.warning(None,
                                  u'Error in an Internal Component',
                                  description,
                                  QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
                                  QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()  # self.ui.btn_step1.clicked
    def _start_the_analysis(self):
        """
        Start the analysis, but first... check to make sure a user didn't forget to choose the
        "add voice pair" button!
        """
        # check that all the pieces have at least one part combination selected
        for i in xrange(len(self._work_wrap)):
            combos = unicode(self._work_wrap.data((i, WorkflowWrapper.parts_combinations),
                                                  Qt.DisplayRole).toPyObject())
            combos = combos.toPyObject() if isinstance(combos, QtCore.QVariant) else combos
            combos = unicode(combos)
            if WorkflowWrapper.default_value == combos:
                # we can't analyze, but we *should* tell our user
                QtGui.QMessageBox.information(None,
                    u'vis',
                    u'You forgot to add part combinations for analysis in at least one piece.',
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
                    QtGui.QMessageBox.Ok)
                return None

        # See if any of the part-name checkboxes are checked... if so, we gotta warn our user!
        part_cbs_are_checked = False
        if self.part_checkboxes is not None:
            for each_box in self.part_checkboxes:
                if each_box.isChecked():
                    part_cbs_are_checked = True
                    break
            # if a checkbox was checked, inform the user they may have made a mistake, and *don't*
            # start the analysis yet
            if part_cbs_are_checked:
                response = QtGui.QMessageBox.question(None,
                    u'vis',
                    u'At least one part checkbox is selected, but you did not add the part ' + \
                        u'combination to the list of parts to analyze.\n\nDo you want to go ' + \
                        u'back and add the part combination?',
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes),
                    QtGui.QMessageBox.Yes)
                if response == QtGui.QMessageBox.Yes:
                    return None

        # Since we don't do any computation during this stage, we'll just go straight to the
        # experiment-selection panel.
        self._tool_experiment()

    @QtCore.pyqtSlot()  # self.ui.chk_all_voice_combos.clicked
    def _all_voice_pairs(self):
        "When a user chooses the 'all voice pairs' checkbox"
        part_spec = None
        if self.ui.chk_all_voice_combos.isChecked():
            if self.ui.chk_all_voices.isChecked():
                self.ui.chk_all_voices.setChecked(False)
            part_spec = u'[all pairs]'
        else:
            part_spec = WorkflowWrapper.default_value
        self._update_parts_selection(part_spec)

    @QtCore.pyqtSlot()  # self.ui.line_piece_title.editingFinished
    def _update_piece_title(self):
        "When users change the piece title on the 'assemble' panel."
        # Which piece is/pieces are selected?
        currently_selected = self.ui.gui_pieces_list.selectedIndexes()

        # Find the piece title and update it
        for cell in currently_selected:
            if WorkflowWrapper.title == cell.column():
                new_title = unicode(self.ui.line_piece_title.text())
                self._work_wrap.setData(cell, new_title, Qt.EditRole)

    @QtCore.pyqtSlot()  # self.ui.chk_repeat_identical.stateChanged
    def _update_repeat_identical(self):
        "When users change 'repeat consecutive identical events' on the 'assemble' panel."
        # what was the QCheckBox changed to?
        changed_to = self.ui.chk_repeat_identical.isChecked()

        # Find the piece and update its settings
        for cell in self.ui.gui_pieces_list.selectedIndexes():
            if WorkflowWrapper.repeat_identical == cell.column():
                self._work_wrap.setData(cell, changed_to, QtCore.Qt.EditRole)

    @QtCore.pyqtSlot()  # self.ui.btn_add_check_combo.clicked
    def _add_parts_combination(self):
        """
        When users choose the "Add Combination" button to add the currently selected part
        combination to the list of parts to analyze.
        """
        # If there are no named parts, we can't do this
        if self.part_checkboxes is None:
            return None

        # Hold indices of the selected checkboxes
        selected_checkboxes = [i for i, box in enumerate(self.part_checkboxes) if box.isChecked()]

        # Hold the vis-format specification
        vis_format = None

        # How many checkboxes are selected?
        if 1 == len(selected_checkboxes):
            # If we have one checkbox, it means we need to do monophonic analysis
            vis_format = u'[' + unicode(selected_checkboxes[0]) + u',' + \
                unicode(selected_checkboxes[0]) + u']'
        elif 1 < len(selected_checkboxes):
            # 2 or more checkboxes are selected
            vis_format = u'['
            for each_box in selected_checkboxes:
                vis_format += unicode(each_box) + u','
            vis_format = vis_format[:-1] + u']'
        else:
            # No checkboxes. Just give up.
            return

        # Now update the lists
        if vis_format is not None:
            # Hold the new part-combinations specification
            new_spec = ''
            # What's the current specification?
            curr_spec = unicode(self.ui.line_compare_these_parts.text())
            # Is curr_spec the default filler?
            if WorkflowWrapper.default_value == curr_spec:
                # Then just make a new one
                new_spec = u'[' + vis_format + u']'
                # Update the parts selection
                self._update_parts_selection(new_spec)
            # Does curr_spec include "[all]"?
            elif u'[all]' == curr_spec or u'[all pairs]' == curr_spec:
                # we'll just make a new one, and un-check the "all" QCheckBox
                new_spec = u'[' + vis_format + u']'
                self.ui.chk_all_voice_combos.setChecked(False)
                self.ui.chk_all_voices.setChecked(False)
                # NB: this has to be done after the setChecked(), since setChecked() emits a signal
                # that would otherwise obliterate the new_spec
                self._update_parts_selection(new_spec)
            # Does curr_spec contain vis_format?
            elif vis_format in curr_spec:
                pass
            # Else we must add this new thing
            else:
                # Otherwise, we should remove the final ']' in the list, and put
                # our new combo on the end
                new_spec = curr_spec[:-1] + u',' + vis_format + u']'

                # Update the parts selection
                self._update_parts_selection(new_spec)

        # Also clear the part-selection checkboxes
        for box in self.part_checkboxes:
            box.setChecked(False)

    @QtCore.pyqtSlot()  # self.ui.line_compare_these_parts.editingFinished
    def _add_parts_combo_by_line_edit(self):
        """
        Blindly put the contents of the part-specification QLineEdit into the table, trusting that
        the user knows what they're doing.
        """
        self._update_parts_selection(unicode(self.ui.line_compare_these_parts.text()))

    # Not a pyqtSlot
    def _update_parts_selection(self, part_spec):
        """
        Updates line_compare_these_parts and the model data for all selected pieces so that the
        "parts to compare" contains part_spec.
        """

        # update the UI
        self.ui.line_compare_these_parts.setText(part_spec)

        # Update the selected pieces
        # get the list of selected cells... for each one that is the "voices"
        # column(), set it to the thing specified
        selected_cells = self.ui.gui_pieces_list.selectedIndexes()
        for cell in selected_cells:
            if WorkflowWrapper.parts_combinations == cell.column():
                self._work_wrap.setData(cell, part_spec, QtCore.Qt.EditRole)

    @QtCore.pyqtSlot()  # self.ui.line_offset_interval.editingFinished
    def _update_offset_interval(self):
        """
        Take the value of the "offset interval" field, and sets it.

        Assumes, with no good reason, that the value put in the textbox is good.
        """
        new_offset_interval = unicode(self.ui.line_offset_interval.text())

        # Update the selected pieces
        # get the list of selected cells... for each one that is the "n"
        # column(), set it to the thing specified
        selected_cells = self.ui.gui_pieces_list.selectedIndexes()
        for cell in selected_cells:
            if WorkflowWrapper.offset_interval == cell.column():
                self._work_wrap.setData(cell, new_offset_interval, QtCore.Qt.EditRole)

    @QtCore.pyqtSlot()  # self.ui.gui_pieces_list.clicked
    def _update_pieces_selection(self):
        "Update detail-selection widgets when the selected pieces are changed."

        # Which piece is/pieces are selected?
        currently_selected = self.ui.gui_pieces_list.selectedIndexes()

        # NB: we get a list of all the cells selected, and this is definitely done
        # in rows, so because each row has 6 things, if we have 6 cells, it means
        # we have only one row... but more than 6 cells means more than one row
        if len(currently_selected) == 0:
            # (1) Disable all the controls
            self.ui.line_offset_interval.setEnabled(False)
            self.ui.btn_choose_note.setEnabled(False)
            self.ui.line_compare_these_parts.setEnabled(False)
            self.ui.chk_all_voices.setEnabled(False)
            self.ui.chk_all_voice_combos.setEnabled(False)
            self.ui.btn_add_check_combo.setEnabled(False)
            self.ui.line_piece_title.setEnabled(False)
            self._piece_settings_visibility(False)
            # (2) Remove the part list
            if self.part_checkboxes is not None:
                self._update_part_checkboxes(u'erase')
        elif len(currently_selected) > 6:
            # Multiple pieces selected... possible customization
            # (1) Enable all the controls
            self.ui.line_offset_interval.setEnabled(True)
            self.ui.btn_choose_note.setEnabled(True)
            self.ui.line_compare_these_parts.setEnabled(True)
            self.ui.chk_all_voices.setEnabled(True)
            self.ui.chk_all_voice_combos.setEnabled(True)
            self.ui.btn_add_check_combo.setEnabled(True)
            self.ui.line_piece_title.setEnabled(False)  # not applicable
            self._piece_settings_visibility(True)
            self.ui.grp_settings_for_piece.setTitle(u'Settings for Selected Pieces')
            # (2) if the pieces have the same part names, display them
            # 2.1: get a list of all the lists-of-part-names
            lists_of_part_names = []
            for cell in currently_selected:
                if WorkflowWrapper.parts_list == cell.column():
                    lists_of_part_names.append(\
                        self._work_wrap.data(cell, WorkflowWrapper.ListRole).toPyObject())
            # 2.2: See if each piece has the same number of parts
            number_of_parts = 0
            for parts_list in lists_of_part_names:
                if 0 == number_of_parts:
                    number_of_parts = len(parts_list)
                elif number_of_parts != len(parts_list):
                    number_of_parts = False
                    break
            # 2.3: See if the names in each of the parts is the same
            same_names = True
            for i in xrange(len(lists_of_part_names) - 1):
                if lists_of_part_names[i] != lists_of_part_names[i + 1]:
                    same_names = False
            # 2.4: If all the part names are the same, we'll use them
            if same_names:
                self._update_part_checkboxes(currently_selected)
            # 2.5: If all the pieces have the same number of parts, we can still do it
            elif number_of_parts:
                self._update_part_checkboxes(currently_selected, no_name=True)
            # 2.6: Otherwise, we can't display part checkboxes
            else:
                #self.ui.chk_all_voice_combos.setEnabled(True)
                self._update_part_checkboxes(u'erase')
            # (3) if the pieces have the same offset interval, display it
            first_offset = None
            for cell in currently_selected:
                if WorkflowWrapper.offset_interval == cell.column():
                    if first_offset is None:
                        first_offset = self._work_wrap.\
                        data(cell, QtCore.Qt.DisplayRole).toPyObject()
                    elif first_offset == self._work_wrap.\
                    data(cell, QtCore.Qt.DisplayRole).toPyObject():
                        continue
                    else:
                        first_offset = ''
                        break
            self.ui.line_offset_interval.setText(unicode(first_offset))
            # (4) Update "Compare These Parts"
            first_comp = None
            for cell in currently_selected:
                if WorkflowWrapper.parts_combinations == cell.column():
                    if first_comp is None:
                        first_comp = self._work_wrap.\
                        data(cell, QtCore.Qt.DisplayRole).toPyObject()
                    elif first_comp == self._work_wrap.\
                    data(cell, QtCore.Qt.DisplayRole).toPyObject():
                        continue
                    else:
                        first_comp = u''
                        break
            if '' == first_comp:
                # Multiple parts have different specs
                self.ui.line_compare_these_parts.setText('')
                self.ui.chk_all_voice_combos.setChecked(False)
                self.ui.chk_all_voices.setChecked(False)
            else:
                # Multiple parts have the same spec
                self._update_comparison_parts(currently_selected)
        else:
            # Only one piece... customize for it
            # (1) Enable all the controls
            self.ui.line_offset_interval.setEnabled(True)
            self.ui.btn_choose_note.setEnabled(True)
            self.ui.line_compare_these_parts.setEnabled(True)
            self.ui.chk_all_voices.setEnabled(True)
            self.ui.chk_all_voice_combos.setEnabled(True)
            self.ui.btn_add_check_combo.setEnabled(True)
            self.ui.line_piece_title.setEnabled(True)
            self._piece_settings_visibility(True)
            self.ui.grp_settings_for_piece.setTitle(u'Settings for Selected Piece')
            # (2) Populate the part list
            self._update_part_checkboxes(currently_selected)
            # (3) Update "offset interval"
            for cell in currently_selected:
                if WorkflowWrapper.offset_interval == cell.column():
                    self.ui.line_offset_interval.setText(unicode(
                    self._work_wrap.data(cell, QtCore.Qt.DisplayRole).toPyObject()))
                    break
            # (4) Update "Compare These Parts"
            self._update_comparison_parts(currently_selected)
            # (5) Update "Pice Title"
            for cell in currently_selected:
                if WorkflowWrapper.title == cell.column():
                    self.ui.line_piece_title.setText(
                    unicode(self._work_wrap.data(cell,
                        QtCore.Qt.DisplayRole).toPyObject()))
                    break

    # Not a pyqtSlot
    def _update_comparison_parts(self, currently_selected):
        """
        When a different part combination is selected, call this method to update the "All
        Combinations" and "Basso Seguente" checkboxes.

        You should only call this method if all of the selected pieces have the same part names
        (which is true when only one part is selected).

        The argument should be a list of the currently selected cells.
        """

        for cell in currently_selected:
            if WorkflowWrapper.parts_combinations == cell.column():
                comparison_parts = unicode(self._work_wrap.
                    data(cell, QtCore.Qt.DisplayRole).toPyObject())
                self.ui.line_compare_these_parts.setText(comparison_parts)
                if u'[all]' == comparison_parts:
                    self.ui.chk_all_voice_combos.setChecked(False)
                    self.ui.chk_all_voices.setChecked(True)
                elif u'[all pairs]' == comparison_parts:
                    self.ui.chk_all_voice_combos.setChecked(True)
                    self.ui.chk_all_voices.setChecked(False)
                else:
                    self.ui.chk_all_voice_combos.setChecked(False)
                    self.ui.chk_all_voices.setChecked(False)
                break

    # Not a pyqtSlot
    def _edit_part_name(self, part_index=None):
        """
        Change the name of a part.

        This is called by lambda methods, which are slots that respond to signals emitted by
        buttons on the interface, which when they are displayed correspond each to a part in the
        score.
        """
        # Get the new name
        new_name = unicode(QtGui.QInputDialog.getText(
            None,
            u"Part Name!",
            u"Choose New Part Name",
            QtGui.QLineEdit.Normal,
            unicode(self.part_checkboxes[part_index].text()))[0])  # default filled with new name

        # Find the parts lists and update them
        for cell in self.ui.gui_pieces_list.selectedIndexes():
            if WorkflowWrapper.parts_list == cell.column():
                # We're just going to change the part name in the model, not in the
                # actual Score object itself (which would require re-loading)
                # 1.) Get the parts list
                parts = self._work_wrap.data(cell, WorkflowWrapper.ListRole).toPyObject()
                # 2.) Update the part name as requested
                parts[part_index] = new_name
                # 3.) Convert the part names to str objects (from QString)
                parts = [unicode(name) for name in parts]
                # 4.) Update the data model and QCheckBox objects
                self._work_wrap.setData(cell, parts, QtCore.Qt.EditRole)
                self._update_pieces_selection()

    # Not a pyqtSlot
    def _update_part_checkboxes(self, currently_selected, no_name=False):
        """
        Update the part-selection QCheckBox objects to reflect the currently selected part(s).

        You should only call this method if all of the selected pieces have the same part names
        (which is true when only one part is selected).

        The argument should be a list of the currently selected cells.

        If the argument is == 'erase' then the method removes all current checkboxes and stops.

        The "no_name" keyword argument means we'll use generically numbered parts, rather than
        specific part names. This is useful when, for example, a bunch of pieces are selected, and
        they all have the same number of parts but with different names.
        """

        # (1) Remove previous checkboxes from the layout
        if self.part_layouts is not None:
            for lay in self.part_layouts:
                for part in self.part_checkboxes:
                    lay.removeWidget(part)
                    part.close()
                for button in self.edit_buttons:
                    lay.removeWidget(button)
                    button.close()
                self.ui.verticalLayout_part_boxes.removeItem(lay)
                lay.invalidate()

        self.part_layouts = None
        self.part_checkboxes = None
        self.edit_buttons = None

        # (1a) If currently_selected is "erase" then we should only erase the
        # current checkboxes, and we should stop now.
        if u'erase' == currently_selected:
            return

        # (2) Get the list of parts
        list_of_parts = None
        for cell in currently_selected:
            if WorkflowWrapper.parts_list == cell.column():
                list_of_parts = self._work_wrap.data(cell, WorkflowWrapper.ListRole).toPyObject()
                break
        # deal with a possible "no_name" argument
        if no_name:
            how_many_parts = len(list_of_parts)
            list_of_parts = []
            for i in xrange(how_many_parts):
                list_of_parts.append(u'Part ' + unicode(i + 1))

        # (3) Put up a checkbox for each part
        self.part_checkboxes = []
        self.edit_buttons = []
        self.part_layouts = []
        for i in xrange(len(list_of_parts)):
            part_name = unicode(list_of_parts[i])
            # This is the New CheckBox to select this part
            n_c_b = QtGui.QCheckBox(self.ui.widget_part_boxes)
            n_c_b.setObjectName(u'chk_' + part_name)
            n_c_b.setText(part_name)

            # This is the New BuTtoN to "Edit" this part's name
            n_btn = QtGui.QPushButton(self.ui.widget_part_boxes)
            n_btn.setObjectName(u'btn_' + part_name)
            n_btn.setText(u'Edit Part Name')

            def the_thing(ell):
                "This method runs when the button is clicked"
                return lambda: self._edit_part_name(ell)
            n_btn.clicked.connect(the_thing(i))

            # Add the checkbox and button to the horizontal layout
            lay = QtGui.QHBoxLayout()
            lay.addWidget(n_c_b)
            lay.addWidget(n_btn)

            # Add the layout to the list of part-name checkboxes
            self.edit_buttons.append(n_btn)
            self.part_checkboxes.append(n_c_b)
            self.part_layouts.append(lay)

        # (4) Add all the widgets to the layout
        for part in self.part_layouts:
            self.ui.verticalLayout_part_boxes.addLayout(part)

    @QtCore.pyqtSlot() # self.ui.btn_choose_note.clicked
    def _launch_offset_selection(self):
        "Launch the dialogue box to help users visually select offset values."
        # Launch the offset-selection QDialog
        selector = VisOffsetSelector()
        chosen_offset = selector.trigger()
        # Update the QLineEdit
        if u'ALL' == chosen_offset:
            chosen_offset = u'(optional)'
        self.ui.line_offset_interval.setText(chosen_offset)
        # Set values in the model
        selected_cells = self.ui.gui_pieces_list.selectedIndexes()
        for cell in selected_cells:
            if WorkflowWrapper.offset_interval == cell.column():
                self._work_wrap.setData(cell, chosen_offset, QtCore.Qt.EditRole)
        # Just to make sure we get rid of this
        del selector

    # Not a pyqtSlot
    def _piece_settings_visibility(self, set_to):
        """
        Given True or False, makes visible and enables (or makes invisible and disables)
        everything in the "Settings for Piece" QGroupBox (and the box itself), and the opposite
        for self.lbl_select_piece
        """
        self.ui.grp_settings_for_piece.setVisible(set_to)
        self.ui.grp_settings_for_piece.setEnabled(set_to)
        self.ui.widget_select_piece.setVisible(not set_to)

    @QtCore.pyqtSlot()  # self.ui.rdo_consider_***.clicked()
    def _update_experiment_from_object(self):
        """
        When one of the self.ui.rdo_consider_*** radio buttons is selected, this method updates the
        rest of the GUI to reflect the options relevant to that output method.
        """

        all_the_widgets = [self.ui.rdo_table,
                           self.ui.rdo_chart,
                           self.ui.grp_values_of_n,
                           self.ui.rdo_score,
                           self.ui.grp_annotate_these,
                           self.ui.grp_ignore_inversion,
                           self.ui.grp_annotate_these]

        def on_offer(enable_these):
            """
            Given a list of the GUI objects in the "experiment" panel that should be "on," this
            method enables them and disables all the others.
            """

            # (1) Disable everything
            for each_widget in all_the_widgets:
                each_widget.setVisible(False)

            # (2) Enable the valid things
            for each_widget in enable_these:
                each_widget.setVisible(True)

        # Determine which widgets to enable
        which_to_enable = []

        if self.ui.rdo_consider_intervals.isChecked():
            which_to_enable = [self.ui.rdo_table, self.ui.rdo_chart, self.ui.rdo_score,
                               self.ui.grp_ignore_inversion, self.ui.grp_annotate_these]
        elif self.ui.rdo_consider_interval_ngrams.isChecked():
            which_to_enable = [self.ui.rdo_table, self.ui.grp_values_of_n, self.ui.rdo_chart,
                               self.ui.grp_ignore_inversion]
        elif self.ui.rdo_consider_score.isChecked():
            which_to_enable = [self.ui.rdo_score]

        # Run the on_offer()
        on_offer(which_to_enable)

        # Choose the first enabled output format in "How to Show Results"; update filters
        outs = [self.ui.rdo_table, self.ui.rdo_chart, self.ui.rdo_score]
        for each_box in outs:
            if each_box.isVisible():
                each_box.setChecked(True)
                break
        which_to_enable = [self.ui.rdo_score]
        self._output_format_changed()

    def _output_format_changed(self):
        """
        When a user chooses a different output format (in "How to Show Results" on the "show"
        panel), we may have to enable/disable the Top X and Threshold filter.
        """
        if self.ui.rdo_table.isChecked() or self.ui.rdo_chart.isChecked():
            self.ui.group_top_x.setVisible(True)
            self.ui.group_threshold.setVisible(True)
        else:
            self.ui.group_top_x.setVisible(False)
            self.ui.group_threshold.setVisible(False)

    @QtCore.pyqtSlot()  # self.ui.chk_all_voices.stateChanged
    def _all_voices(self):
        "When a user chooses the 'all voices' checkbox"
        part_spec = None
        if self.ui.chk_all_voices.isChecked():
            if self.ui.chk_all_voice_combos.isChecked():
                self.ui.chk_all_voice_combos.setChecked(False)
            part_spec = u'[all]'
        else:
            part_spec = WorkflowWrapper.default_value
        self._update_parts_selection(part_spec)

    @QtCore.pyqtSlot()  # self.ui.rdo_heedQuality and rdo_noHeedQuality
    def _update_quality(self):
        "When a user changes the 'display quality' radio buttons."
        set_to_what = True if self.ui.rdo_heedQuality.isChecked() else False
        self._work_wrap.setData((0, WorkflowWrapper.quality), set_to_what, Qt.EditRole)

    @QtCore.pyqtSlot()  # self.ui.rdo_compound and rdo_simple
    def _update_octaves(self):
        "When a user changes the 'simple/compound' radio buttons."
        set_to_what = True if self.ui.rdo_simple.isChecked() else False
        self._work_wrap.setData((0, WorkflowWrapper.simple_ints), set_to_what, Qt.EditRole)

    def _update_global_settings(self):
        """
        Update the radio buttons associated with global settings (at the moment, quality and simple)
        """
        if self._work_wrap.data((0, WorkflowWrapper.quality), Qt.DisplayRole).toPyObject():
            self.ui.rdo_heedQuality.setChecked(True)
        else:
            self.ui.rdo_noHeedQuality.setChecked(True)
        if self._work_wrap.data((0, WorkflowWrapper.simple_ints), Qt.DisplayRole).toPyObject():
            self.ui.rdo_simple.setChecked(True)
        else:
            self.ui.rdo_compound.setChecked(True)

    @QtCore.pyqtSlot()  # self.ui.btn_show_results.clicked
    def _prepare_experiment_submission(self):
        """
        Make sure the Experimenter has a properly-configured Settings instance, then ask it to run
        the experiment.
        """

        # move to the "working" panel and update it
        self._tool_working()
        self._update_progress_bar(u'0')
        self._update_progress_bar(u'Initializing experiment.')

        # hold a list of tuples to be signalled as settings
        list_of_settings = {}

        def do_experiment():
            "Which experiment does the user want to run?"
            # experiment
            if self.ui.rdo_consider_intervals.isChecked():
                list_of_settings['experiment'] = u'intervals'
            elif self.ui.rdo_consider_interval_ngrams.isChecked():
                list_of_settings['experiment'] = u'interval n-grams'
            elif self.ui.rdo_consider_score.isChecked():
                list_of_settings['experiment'] = 'LilyPondExperiment'
                list_of_settings['output format'] = 'LilyPondDisplay'
            # output format
            if self.ui.rdo_table.isChecked():
                list_of_settings['output format'] = 'table'
            elif self.ui.rdo_chart.isChecked():
                list_of_settings['output format'] = 'chart'
            elif self.ui.rdo_score.isChecked():
                list_of_settings['output format'] = 'lilypond'

        def do_threshold():
            "Is there a threshold value?"
            threshold = self.ui.spin_threshold.value()
            if 0 != threshold:
                list_of_settings['threshold'] = threshold

        def do_top_x():
            "Is there a 'top x' value?"
            top_x = self.ui.spin_top_x.value()
            if 0 != top_x:
                list_of_settings['topX'] = top_x

        def do_values_of_n():
            "Are there values of 'n' specified?"
            enn = self.ui.spin_n.value()
            list_of_settings['n'] = enn

        def do_ignore_inversion():
            "Ignore inversion?"
            if self.ui.chk_ignore_inversion.isChecked():
                list_of_settings['ignore direction'] = True
            else:
                list_of_settings['ignore direction'] = False

        # (1) Figure out the settings
        # (1a) Which experiment?
        do_experiment()
        # (1d) Is there a "values_of_n" value?
        if u'interval n-grams' == list_of_settings[u'experiment']:
            do_values_of_n()
        # (1e) Threshold
        do_threshold()
        # (1f) Top X
        do_top_x()
        # (1g) Ignore Voice Crossing
        do_ignore_inversion()

        # (2) Run the experiment
        self._run_the_experiment(list_of_settings)

    def _run_the_experiment(self, settings):
        """
        Run the experiment as instructed by the 'settings' argument.
        """
        # 1.) Do we need to run the experiment at all?
        workm = self._work_wrap.get_workflow_manager()
        run_exp = None
        # 1.a) If the model thinks settings were changed (i.e., user went back to "analyze" page).
        if self._work_wrap.settings_changed():
            run_exp = True
        # 1.b) If there was no previous experiment, then yes.
        elif self._prev_setts is None:
            run_exp = True
        # 1.c) If the previous experiment is different, then yes.
        elif self._prev_setts['experiment'] != settings['experiment']:
            run_exp = True
        # 1.d) If the experiments are the same, but they have 'n' and they're different, then yes.
        elif 'n' in self._prev_setts and self._prev_setts['n'] != settings['n']:
            run_exp = True
        # 1.e) Save the settings for next time.
        self._prev_setts = settings

        # 2.) Run the experiment, if required.
        if run_exp is True:
            if u'n' in settings:
                workm.settings(None, u'n', settings[u'n'])
            workm.run(settings[u'experiment'])

        # 3.) Run the output-getting stuff.
        path = None
        result_type = None
        top_x = settings['topX'] if 'topX' in settings else None
        threshold = settings['threshold'] if 'threshold' in settings else None
        if u'chart' == settings[u'output format']:
            result_type = u'image'
            path = workm.output(u'R histogram', u'outputs/R_chart.png', top_x, threshold)
            # We add "../" because we expect the image to be in the "outputs" directory, but so is
            # the HTML file. We could just set "path" to "R_chart.png" but output() doesn't
            # guarantee that it'll actually output to the pathname requested, so we need it.
            path = u'../' + path
        elif u'table' == settings[u'output format']:
            result_type = u'table'
            path = workm.export(u'HTML', u'outputs/pandas_table.html', top_x, threshold)
        else:
            VisQtMainWindow._error_reporter(u'Unrecognized output format: "' + \
                                            unicode(settings[u'output format']) + u'"')

        if path is not None:
            token_name = u'Interval' if u'intervals' == settings[u'experiment'] else \
                    unicode(settings['n']) + u'-Gram'
            webview = VisWebView()
            trig_ret = webview.trigger(path, result_type, token_name)
            # we may have to save the output!
            if trig_ret is not None:
                for form, pathname in trig_ret:
                    workm.export(form, pathname, top_x, threshold)
            del webview  # make sure we free dat memory!

        self._tool_experiment()
