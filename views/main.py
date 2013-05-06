#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:             vis
# Program Description:      Measures sequences of vertical intervals.
#
# Filename: main.py
# Purpose: The main view class.
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
Holds the VisQtMainWindow class, which is the GUI-controlling thing for vis' PyQt4 interface.
"""

# Imports from...
# Python
from itertools import chain
import os
from os import walk
from os.path import splitext, join
# PyQt4
from PyQt4 import QtGui, uic, QtCore
# music21
from music21 import metadata, converter
# vis
from models.analyzing import ListOfPieces
from views.VisOffsetSelector import VisOffsetSelector


class VisQtMainWindow(QtGui.QMainWindow, QtCore.QObject):
    """
    This class makes the GUI-controlling objects for vis' PyQt4 interface.
    """
    # Signals for connecting to the vis_controller
    show_import = QtCore.pyqtSignal()
    show_analyze = QtCore.pyqtSignal()
    show_working = QtCore.pyqtSignal()
    show_about = QtCore.pyqtSignal()
    show_experiment = QtCore.pyqtSignal()
    update_progress = QtCore.pyqtSignal(str)
    report_error = QtCore.pyqtSignal(str)

    def __init__(self, vis_controller):
        """
        The argument is the instance of VisController controlling this class. It's
        used to send signals.
        """
        super(VisQtMainWindow, self).__init__()  # required for signals
        self.vis_controller = vis_controller
        self.ui = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/ui/main_window.ui')
        self._tool_import()
        self.ui.show()
        # Hold a lists of checkboxes, "Edit" buttons, and layouts that represent
        # the parts in a piece for the "assemble" panel
        self.part_checkboxes = None
        self.edit_buttons = None
        self.part_layouts = None
        # Setup GUI-only Signals
        mapper = [
            # Signals interacting with VISController
            (self.show_import, self._tool_import),
            (self.show_analyze, self._tool_analyze),
            (self.show_working, self._tool_working),
            (self.show_about, self._tool_about),
            (self.show_experiment, self._tool_experiment),
            (self.update_progress, self._update_progress_bar),
            (self.report_error, self._error_reporter),
            (self.ui.btn_choose_files.clicked, self._tool_import),
            (self.ui.btn_about.clicked, self._tool_about),
            (self.ui.btn_analyze.clicked, self._tool_analyze),
            (self.ui.btn_experiment.clicked, self._tool_experiment),
            (self.ui.btn_dir_add.clicked, self._add_dir),
            (self.ui.btn_file_add.clicked, self._add_files),
            (self.ui.btn_file_remove.clicked, self._remove_files),
            (self.ui.btn_show_results.clicked, self._prepare_experiment_submission),
            # NB: these are connected to sub-controllers by VisController
            (self.ui.btn_step1.clicked, self._check_for_pieces),
            (self.ui.btn_step2.clicked, self._start_the_analysis),
            # Things that operate the GUI
            (self.ui.chk_all_voice_combos.stateChanged, self._adjust_bs),
            (self.ui.chk_all_voice_combos.clicked, self._all_voice_combos),
            (self.ui.line_piece_title.editingFinished, self._update_piece_title),
            (self.ui.btn_add_check_combo.clicked, self._add_parts_combination),
            (self.ui.line_compare_these_parts.editingFinished, self._add_parts_combo_by_line_edit),
            (self.ui.line_offset_interval.editingFinished, self._update_offset_interval),
            (self.ui.gui_pieces_list.clicked, self._update_pieces_selection),
            (self.ui.btn_choose_note.clicked, self._launch_offset_selection),
            (self.ui.rdo_consider_chord_ngrams.clicked, self._update_experiment_from_object),
            (self.ui.rdo_consider_interval_ngrams.clicked, self._update_experiment_from_object),
            (self.ui.rdo_consider_intervals.clicked, self._update_experiment_from_object),
            (self.ui.chk_repeat_identical.stateChanged, self._update_repeat_identical),
            (self.ui.btn_cancel_operation.clicked, self._cancel_operation),
            (self.ui.rdo_spreadsheet.clicked, self._output_format_changed),
            (self.ui.rdo_list.clicked, self._output_format_changed),
            (self.ui.rdo_chart.clicked, self._output_format_changed),
        ]
        for signal, slot in mapper:
            signal.connect(slot)
        # Setup the progress bar
        self.ui.progress_bar.setMinimum(0)
        self.ui.progress_bar.setMaximum(100)
        self.ui.progress_bar.setValue(42)

    # Methods Doing GUI Stuff ---------------------------------------------------
    # Pressing Buttons in the Toolbar -----------------------
    @QtCore.pyqtSlot()
    def _tool_import(self):
        """
        Activate the "import" panel
        """
        self.ui.main_screen.setCurrentWidget(self.ui.page_choose)
        self.ui.btn_about.setEnabled(True)
        self.ui.btn_choose_files.setEnabled(True)
        self.ui.btn_analyze.setEnabled(False)
        self.ui.btn_experiment.setEnabled(False)
        self.ui.btn_step1.setEnabled(True)
        self.ui.btn_step2.setEnabled(False)

    @QtCore.pyqtSlot()
    def _tool_analyze(self):
        """
        Activate the "analyze" panel (corresponding to the Analyzer).
        """
        self.ui.main_screen.setCurrentWidget(self.ui.page_analyze)
        self.ui.btn_choose_files.setEnabled(False)
        self.ui.btn_analyze.setChecked(True)
        self.ui.btn_about.setEnabled(True)
        self.ui.btn_analyze.setEnabled(True)
        self.ui.btn_experiment.setEnabled(False)
        self.ui.btn_step1.setEnabled(False)
        self.ui.btn_step2.setEnabled(True)

    @QtCore.pyqtSlot()
    def _tool_working(self):
        """
        Activate the "working" panel, for when vis is processing.
        """
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
        """
        Activate the "about" panel.
        """
        self.ui.main_screen.setCurrentWidget(self.ui.page_about)
        # leave enabled/disabled as-is, but make sure only "about" is checked
        self.ui.btn_about.setChecked(True)
        self.ui.btn_analyze.setChecked(False)
        self.ui.btn_choose_files.setChecked(False)
        self.ui.btn_experiment.setChecked(False)

    @QtCore.pyqtSlot()
    def _tool_experiment(self):
        """
        Activate the "show" panel, which corresponds to the Experimenter controller.
        """
        self.ui.main_screen.setCurrentWidget(self.ui.page_show)
        self.ui.btn_about.setEnabled(True)
        self.ui.btn_choose_files.setEnabled(False)
        self.ui.btn_analyze.setEnabled(True)
        self.ui.btn_experiment.setEnabled(True)
        self.ui.btn_experiment.setChecked(True)
        self.ui.btn_step1.setEnabled(False)
        self.ui.btn_step2.setEnabled(False)
        # call the thing to update this panel
        self._update_experiment_from_object()
        # call the thing to to what it says it does
        self._output_format_changed()

    # Operations on the Importer panel ----------------------
    @QtCore.pyqtSlot()
    def _check_for_pieces(self):
        """
        Check there is at least one piece set to be imported. If there is, start importing. If not,
        ask the user to choose some pieces.
        """
        # check there are more than 0 pieces for the Importer
        if self.vis_controller.importer.has_files():
            # then go!
            self._tool_working()
            self.vis_controller.run_the_import.emit()
        else:
            # then ask the user to stop being a jerk
            QtGui.QMessageBox.information(None,
            "Please Select Pieces",
            """The list of pieces is empty.

You must choose pieces before we can import them.""",
            QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def _add_files(self):
        """
        Add files to the "importer" panel.
        """
        files = QtGui.QFileDialog.getOpenFileNames(
            None,  # parent
            "Choose Files to Analyze",  # title
            '',  # default directory
            )  # NB: This should be the 'filter' line, which is below, but commented out... it seems
            # that, for some reason, the filter isn't working. For me on Fedora 17, the result is
            # that all file types are "selectable"... but others have reported occasional issues
            # that entirely prevent them from selecting files. So here we are.
            # 'music21 Files (*.nwc *.mid *.midi *.mxl *.krn *.xml *.md)')  # filter
        if files:
            self.vis_controller.import_files_added.emit([str(f) for f in files])

    @QtCore.pyqtSlot()
    def _add_dir(self):
        """
        Add a directory to the "importer" panel.
        """
        d = QtGui.QFileDialog.getExistingDirectory(
            None,  # parent
            "Choose Directory to Analyze",  # title
            '',  # default directory
            QtGui.QFileDialog.ShowDirsOnly)  # options
        d = str(d)
        extensions = ['.nwc.', '.mid', '.midi', '.mxl', '.krn', '.xml', '.md']
        possible_files = chain(*[[join(path, fp) for fp in files if
                        splitext(fp)[1] in extensions]
                        for path, ___, files in walk(d)])
        self.vis_controller.import_files_added.emit(list(possible_files))

    @QtCore.pyqtSlot()
    def _remove_files(self):
        """
        Method which finds which files the user has selected for
        removal and emits a signal containing their names.
        """
        # which indices are currently selected?
        currently_selected = self.ui.gui_file_list.selectedIndexes()

        # send this to the VISController
        self.vis_controller.import_files_removed.emit(currently_selected)

    # Operations on the "Working" Panel ---------------------
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
        if not isinstance(progress, (str, QtCore.QString)):
            return None
        else:
            if '100' == progress:
                self.ui.progress_bar.setValue(100)
            elif 3 > len(progress):
                try:
                    new_val = int(progress)
                    self.ui.progress_bar.setValue(new_val)
                except ValueError:
                    self.ui.lbl_currently_processing.setText(progress)
            else:
                self.ui.lbl_currently_processing.setText(progress)

    @QtCore.pyqtSlot()
    def _cancel_operation(self):
        """
        If possible, cancels the currently-running operation (import, analysis, experiment).
        """
        # confirm with the user that they want to cancel whatever's happening
        feedback = QtGui.QMessageBox.question(
            None,
            "Confirm",
            "Are you sure you want to cancel the running operation?",
            QtGui.QMessageBox.StandardButtons(
                QtGui.QMessageBox.No |
                QtGui.QMessageBox.Yes))

        if QtGui.QMessageBox.Yes != feedback:
            return None
        # else... we'll figure out which operation is running, and cancel it
        if self.vis_controller.importer.import_is_running:
            self.vis_controller.importer.cancel_import.emit()
        elif self.vis_controller.analyzer.analysis_is_running:
            self.vis_controller.analyzer.cancel_analysis.emit()
            self.vis_controller.analyzer.analysis_is_running = False
            self.vis_controller.analyzer._list_of_analyses = []
            self.show_analyze.emit()

    # Other Things ------------------------------------------
    @QtCore.pyqtSlot(str)  # for self.report_error
    def _error_reporter(self, description):
        """
        Notify the user that an error has happened. The argument should be a
        description of the error.
        """
        QtGui.QMessageBox.warning(None,
                                'Error in an Internal Component',
                                description,
                                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
                                QtGui.QMessageBox.Ok)

    #----------------
    # Not a PyQt slot
    def _start_the_analysis(self):
        """
        Start the analysis, but first... check to make sure a user didn't forget to choose the
        "add voice pair" button!
        """
        # loop through the part checkboxes, see if they're checked
        part_cbs_are_checked = False
        for each_box in self.part_checkboxes:
            if each_box.isChecked():
                part_cbs_are_checked = True
                break
        # if a checkbox was checked, inform the user they may have made a mistake, and *don't*
        # start the analysis yet
        if part_cbs_are_checked:
            response = QtGui.QMessageBox.question(None,
                'vis',
                """At least one part checkbox is selected, but you did not add the part combination to the list of parts to analyze.

Do you want to go back and add the part combination?""",
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes),
                QtGui.QMessageBox.Yes)
            if response == QtGui.QMessageBox.Yes:
                return
        # this happens if none of the QCheckBoxes are selected, or if the response is "No"
        self._tool_working()
        self.vis_controller.run_the_analysis.emit()

    #------------------------------------------------------
    # Signal for: self.ui.chk_all_voice_combos.stateChanged
    @QtCore.pyqtSlot()
    def _adjust_bs(self):
        """
        Adjust the 'basso seguente' checkbox's text, depending on whether the
        "all combinations" checkbox is checked.
        """
        pass

    #-------------------------------------------------
    # Signal for: self.ui.chk_all_voice_combos.clicked
    @QtCore.pyqtSlot()
    def _all_voice_combos(self):
        """
        Deal with the situation when a user checks or unchecks the "all voice
        combinations" checkbox.
        """
        # Hold the new value for the part-combination-specification QLineEdit
        part_spec = ''

        # Are we enabling "all" or disabling?
        if self.ui.chk_all_voice_combos.isChecked():
            part_spec = '[all]'
        else:
            part_spec = '(no selection)'

        self._update_parts_selection(part_spec)

    #-----------------------------------------------
    # Signal for: self.ui.chk_basso_seguente.clicked
    @QtCore.pyqtSlot()
    def _chose_bs(self):
        """
        When somebody chooses the "basso seguente" checkbox, if "all" is also
        selected, we should update the QLineEdit
        """
        if self.ui.chk_all_voice_combos.isChecked():
            part_spec = '[all]'

            self._update_parts_selection(part_spec)

    #-----------------------------------------------------
    # Signal for: self.ui.line_piece_title.editingFinished
    @QtCore.pyqtSlot()
    def _update_piece_title(self):
        """
        When users change the piece title on the "assemble" panel.
        """
        # Which piece is/pieces are selected?
        currently_selected = self.ui.gui_pieces_list.selectedIndexes()

        # Find the piece title and update it
        for cell in currently_selected:
            if ListOfPieces.score == cell.column():
                # This is a little tricky, because we'll change the Score object's
                # Metadata object directly...
                # Get the Score
                piece = self.vis_controller.l_o_pieces.data(cell, ListOfPieces.ScoreRole)
                # unpickle the score
                piece = converter.thawStr(piece)
                # Make sure there's a Metadata object
                if piece.metadata is None:
                    piece.insert(metadata.Metadata())
                # Update the title, saving it for later
                new_title = str(self.ui.line_piece_title.text())
                piece.metadata.title = new_title
                # re-pickle the score
                piece = converter.freezeStr(piece, fmt='pickle')
                # Tell the Analyzer to change its setting!
                # NB: the second argument has to be 2-tuple with the Score object
                # and the string that is the title, as specified in ListOfPieces
                self.vis_controller.analyzer.change_settings.emit(cell, (piece, new_title))

    #------------------------------------------------------
    # Signal for: self.ui.chk_repeat_identical.stateChanged
    @QtCore.pyqtSlot()
    def _update_repeat_identical(self):
        """
        When users change "repeat consecutive identical events" on the "assemble" panel.
        """
        # Which piece is/pieces are selected?
        currently_selected = self.ui.gui_pieces_list.selectedIndexes()

        # what was the QCheckBox changed to?
        changed_to = self.ui.chk_repeat_identical.isChecked()

        # Find the piece title and update it
        for cell in currently_selected:
            if ListOfPieces.repeat_identical == cell.column():
                # Update the piece
                self.vis_controller.analyzer.change_settings.emit(cell, changed_to)

    #------------------------------------------------
    # Signal for: self.ui.btn_add_check_combo.clicked
    @QtCore.pyqtSlot()
    def _add_parts_combination(self):
        """
        When users choose the "Add Combination" button to add the currently
        selected part combination to the list of parts to analyze.
        """
        # TODO: rewrite this to deal with a wide range of part selections

        # If there are no named parts, we can't do this
        if self.part_checkboxes is None:
            return None

        # Hold indices of the selected checkboxes
        selected_checkboxes = [i for i, box in enumerate(self.part_checkboxes)
                                if box.isChecked()]

        # Hold the vis-format specification
        vis_format = None

        # How many checkboxes are selected?
        if 1 == len(selected_checkboxes):
            # If we have one checkbox and bs, okay
            #if self.ui.chk_basso_seguente.isChecked():
            #vis_format = '[' + str(selected_checkboxes[0]) + ',bs]'
            ## Otherwise, complain
            #else:
            QtGui.QMessageBox.warning(None,
                "Unusable Part Selection",
                "Please select two parts at a time.",
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
                QtGui.QMessageBox.Ok)
        elif 2 == len(selected_checkboxes):
            # Is "basso seguente" also selected?
            #if self.ui.chk_basso_seguente.isChecked():
            ## That's not good
            #QtGui.QMessageBox.warning(None,
                #"Cannot Add Part",
                #"When you choose \"basso seguente,\" you can only choose one other part.",
                #QtGui.QMessageBox.StandardButtons(\
                    #QtGui.QMessageBox.Ok),
                #QtGui.QMessageBox.Ok)
            #else:
            # We have two parts; choose them.
            vis_format = '[' + str(selected_checkboxes[0]) + ',' + \
                                str(selected_checkboxes[1]) + ']'
        else:
            # Greater or fewer than two parts?
            QtGui.QMessageBox.warning(None,
            "Unusable Part Selection",
            "Please select two parts at a time.",
            QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)

        # Now update the lists
        if vis_format is not None:
            # Hold the new part-combinations specification
            new_spec = ''

            # What's the current specification?
            curr_spec = str(self.ui.line_compare_these_parts.text())

            # Is curr_spec the default filler?
            if 'e.g., [[0,3]] or [[0,3],[1,3]]' == curr_spec or \
            '(no selection)' == curr_spec or \
            '' == curr_spec:
                # Then just make a new one
                new_spec = '[' + vis_format + ']'

                # Update the parts selection
                self._update_parts_selection(new_spec)
            # Does curr_spec include "[all]"?
            elif '[all]' == curr_spec:
                # we'll just make a new one, and un-check the "all" QCheckBox
                new_spec = '[' + vis_format + ']'
                self._update_parts_selection(new_spec)
                self.ui.chk_all_voice_combos.setChecked(False)
            # Does curr_spec contain vis_format?
            elif vis_format in curr_spec:
                pass
            # Else we must add this new thing
            else:
                # Otherwise, we should remove the final ']' in the list, and put
                # our new combo on the end
                new_spec = curr_spec[:-1] + ',' + vis_format + ']'

                # Update the parts selection
                self._update_parts_selection(new_spec)

        # Also clear the part-selection checkboxes
        #self.ui.chk_basso_seguente.setChecked(False)
        for box in self.part_checkboxes:
            box.setChecked(False)

    #-------------------------------------------------------------
    # Signal for: self.ui.line_compare_these_parts.editingFinished
    @QtCore.pyqtSlot()
    def _add_parts_combo_by_line_edit(self):
        """
        Blindly put the contents of the part-specification QLineEdit into the
        table, trusting that the user knows what they're doing.
        """
        self._update_parts_selection(str(self.ui.line_compare_these_parts.text()))

    #---------------
    # Not a pyqtSlot
    def _update_parts_selection(self, part_spec):
        """
        Updates line_compare_these_parts and the model data for all selected
        pieces so that the "parts to compare" contains part_spec.
        """

        # update the UI
        self.ui.line_compare_these_parts.setText(part_spec)

        # Update the selected pieces
        # get the list of selected cells... for each one that is the "voices"
        # column(), set it to the thing specified
        selected_cells = self.ui.gui_pieces_list.selectedIndexes()
        for cell in selected_cells:
            if ListOfPieces.parts_combinations == cell.column():
                self.vis_controller.analyzer.change_settings.emit(cell, part_spec)

    #---------------------------------------------------------
    # Signal for: self.ui.line_offset_interval.editingFinished
    def _update_offset_interval(self):
        """
        Take the value of the "offset interval" field, and sets it.

        Assumes, with no good reason, that the value put in the textbox is good.
        """
        new_offset_interval = str(self.ui.line_offset_interval.text())

        # Update the selected pieces
        # get the list of selected cells... for each one that is the "n"
        # column(), set it to the thing specified
        selected_cells = self.ui.gui_pieces_list.selectedIndexes()
        for cell in selected_cells:
            if ListOfPieces.offset_intervals == cell.column():
                self.vis_controller.analyzer.change_settings.emit(cell, new_offset_interval)

    #--------------------------------
    # self.ui.gui_pieces_list.clicked
    def _update_pieces_selection(self):
        """
        Update the detail-selection widgets when the user changes the pieces that
        are selected.
        """
        # TODO: finish the other things for this method
        # When the user changes the piece(s) selected in self.gui_pieces_list

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
            self.ui.chk_all_voice_combos.setEnabled(False)
            self.ui.btn_add_check_combo.setEnabled(False)
            self.ui.line_piece_title.setEnabled(False)
            self._piece_settings_visibility(False)
            # (2) Remove the part list
            if self.part_checkboxes is not None:
                for part in self.part_checkboxes:
                    self.ui.verticalLayout_22.removeWidget(part)
                    part.close()
                self.part_checkboxes = None
        elif len(currently_selected) > 6:
            # Multiple pieces selected... possible customization
            # (1) Enable all the controls
            self.ui.line_offset_interval.setEnabled(True)
            self.ui.btn_choose_note.setEnabled(True)
            self.ui.line_compare_these_parts.setEnabled(True)
            self.ui.chk_all_voice_combos.setEnabled(True)
            self.ui.btn_add_check_combo.setEnabled(True)
            self.ui.line_piece_title.setEnabled(False)  # not applicable
            self._piece_settings_visibility(True)
            self.ui.grp_settings_for_piece.setTitle('Settings for Selected Pieces')
            # (2) if the pieces have the same part names, display them
            # 2.1: get a list of all the lists-of-part-names
            lists_of_part_names = []
            for cell in currently_selected:
                if ListOfPieces.parts_list == cell.column():
                    lists_of_part_names.append(self.vis_controller.l_o_pieces.data(cell, ListOfPieces.ScoreRole))
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
                self.ui.chk_all_voice_combos.setEnabled(True)
                self._update_part_checkboxes('erase')
            # (3) if the pieces have the same offset interval, display it
            first_offset = None
            for cell in currently_selected:
                if ListOfPieces.offset_intervals == cell.column():
                    if first_offset is None:
                        # TODO: whatever
                        first_offset = self.vis_controller.l_o_pieces.\
                        data(cell, QtCore.Qt.DisplayRole).toPyObject()
                    elif first_offset == self.vis_controller.l_o_pieces.\
                    data(cell, QtCore.Qt.DisplayRole).toPyObject():
                        continue
                    else:
                        first_offset = ''
                        break
            self.ui.line_offset_interval.setText(str(first_offset))
            # (4) Update "Compare These Parts"
            first_comp = None
            for cell in currently_selected:
                if ListOfPieces.parts_combinations == cell.column():
                    if first_comp is None:
                        first_comp = self.vis_controller.l_o_pieces.\
                        data(cell, QtCore.Qt.DisplayRole).toPyObject()
                    elif first_comp == self.vis_controller.l_o_pieces.\
                    data(cell, QtCore.Qt.DisplayRole).toPyObject():
                        continue
                    else:
                        first_comp = ''
                        break
            if '' == first_comp:
                # Multiple parts have different specs
                self.ui.line_compare_these_parts.setText('')
                self.ui.chk_all_voice_combos.setChecked(False)
                self._adjust_bs()
            else:
                # Multiple parts have the same spec
                self._update_comparison_parts(currently_selected)
        else:
            # Only one piece... customize for it
            # (1) Enable all the controls
            self.ui.line_offset_interval.setEnabled(True)
            self.ui.btn_choose_note.setEnabled(True)
            self.ui.line_compare_these_parts.setEnabled(True)
            self.ui.chk_all_voice_combos.setEnabled(True)
            self.ui.btn_add_check_combo.setEnabled(True)
            self.ui.line_piece_title.setEnabled(True)
            self._piece_settings_visibility(True)
            self.ui.grp_settings_for_piece.setTitle('Settings for Selected Piece')
            # (2) Populate the part list
            self._update_part_checkboxes(currently_selected)
            # (3) Update "offset interval"
            for cell in currently_selected:
                if ListOfPieces.offset_intervals == cell.column():
                    self.ui.line_offset_interval.setText(str(
                    self.vis_controller.l_o_pieces.data(cell, QtCore.Qt.DisplayRole).toPyObject()))
                    break
            # (4) Update "Compare These Parts"
            self._update_comparison_parts(currently_selected)
            # (5) Update "Pice Title"
            for cell in currently_selected:
                if ListOfPieces.score == cell.column():
                    self.ui.line_piece_title.setText(
                    str(self.vis_controller.l_o_pieces.data(cell,
                        QtCore.Qt.DisplayRole).toPyObject()))
                    break

    #---------------
    # Not a pyqtSlot
    def _update_comparison_parts(self, currently_selected):
        """
        When a different part combination is selected, call this method to update
        the "All Combinations" and "Basso Seguente" checkboxes.

        You should only call this method if all of the selected pieces have the
        same part names (which is true when only one part is selected).

        The argument should be a list of the currently selected cells.
        """

        for cell in currently_selected:
            if ListOfPieces.parts_combinations == cell.column():
                comparison_parts = str(self.vis_controller.l_o_pieces.
                    data(cell, QtCore.Qt.DisplayRole).toPyObject())
                self.ui.line_compare_these_parts.setText(comparison_parts)
                if '[all]' == comparison_parts:
                    self.ui.chk_all_voice_combos.setChecked(True)
                    #self.ui.chk_basso_seguente.setChecked(False)
                    # Update the QCheckBox for "All Combinations" and "Basso Seguente"
                    self._all_voice_combos()
                    self._chose_bs()
                elif '[all,bs]' == comparison_parts:
                    self.ui.chk_all_voice_combos.setChecked(True)
                    #self.ui.chk_basso_seguente.setChecked(True)
                    # Update the QCheckBox for "All Combinations" and "Basso Seguente"
                    self._all_voice_combos()
                    self._chose_bs()
                else:
                    self.ui.chk_all_voice_combos.setChecked(False)
                    #self.ui.chk_basso_seguente.setChecked(False)
                break

        # Adjust the text for "Basso Seguente," if needed
        self._adjust_bs()

    #---------------
    # Not a pyqtSlot
    def _edit_part_name(self, part_index=None):
        """
        Change the name of a part.

        This is called by lambda methods, which are slots that respond to signals emitted by
        buttons on the interface, which when they are displayed correspond each to a part in the
        score.
        """
        # Get the current part name from the checkbox...
        current_name = str(self.part_checkboxes[part_index].text())

        # Get the new name
        new_name = QtGui.QInputDialog.getText(
            None,
            "Part Name!",
            "Choose New Part Name",
            QtGui.QLineEdit.Normal,
            current_name)

        new_name = str(new_name[0])

        # Which piece is/pieces are selected?
        currently_selected = self.ui.gui_pieces_list.selectedIndexes()

        # Find the parts lists and update them
        for cell in currently_selected:
            if ListOfPieces.parts_list == cell.column():
                # We're just going to change the part name in the model, not in the
                # actual Score object itself (which would require re-loading)
                # 1.) Get the parts list
                parts = self.vis_controller.l_o_pieces.data(cell, ListOfPieces.ScoreRole)
                # 2.) Update the part name as requested
                parts[part_index] = new_name
                # 3.) Convert the part names to str objects (from QString)
                parts = [str(name) for name in parts]
                # 4.) Update the data model and QCheckBox objects
                self.vis_controller.l_o_pieces.setData(cell, parts, QtCore.Qt.EditRole)
                self._update_pieces_selection()

    #---------------
    # Not a pyqtSlot
    def _update_part_checkboxes(self, currently_selected, no_name=False):
        """
        Update the part-selection QCheckBox objects to reflect the currently
        selected part(s).

        You should only call this method if all of the selected pieces have the
        same part names (which is true when only one part is selected).

        The argument should be a list of the currently selected cells.

        If the argument is == 'erase' then the method removes all current
        checkboxes and stops.

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
                self.ui.verticalLayout_22.removeItem(lay)
                lay.invalidate()

        self.part_layouts = None
        self.part_checkboxes = None
        self.edit_buttons = None

        # (1a) If currently_selected is "erase" then we should only erase the
        # current checkboxes, and we should stop now.
        if 'erase' == currently_selected:
            return

        # (2) Get the list of parts
        list_of_parts = None
        for cell in currently_selected:
            if ListOfPieces.parts_list == cell.column():
                list_of_parts = self.vis_controller.l_o_pieces.data(cell, ListOfPieces.ScoreRole)
                break
        # deal with a possible "no_name" argument
        if no_name:
            how_many_parts = len(list_of_parts)
            list_of_parts = []
            for i in xrange(how_many_parts):
                list_of_parts.append('Part ' + str(i + 1))

        # (3) Put up a checkbox for each part
        self.part_checkboxes = []
        self.edit_buttons = []
        self.part_layouts = []
        for i in xrange(len(list_of_parts)):
            part_name = str(list_of_parts[i])
            # This is the New CheckBox to select this part
            n_c_b = QtGui.QCheckBox(self.ui.widget_part_boxes)
            n_c_b.setObjectName('chk_' + part_name)
            n_c_b.setText(part_name)

            # This is the New BuTtoN to "Edit" this part's name
            n_btn = QtGui.QPushButton(self.ui.widget_part_boxes)
            n_btn.setObjectName('btn_' + part_name)
            n_btn.setText('Edit Part Name')

            def the_thing(ell):
                """
                This method runs when the button is clicked
                """
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
            self.ui.verticalLayout_22.addLayout(part)

    #-----------------------------------------
    # Slot for self.ui.btn_choose_note.clicked
    def _launch_offset_selection(self):
        """
        Launch the dialogue box to help users visually select offset values.
        """
        # Launch the offset-selection QDialog
        selector = VisOffsetSelector()
        chosen_offset = selector.trigger()

        # Update the QLineEdit
        self.ui.line_offset_interval.setText(str(chosen_offset))

        # Set values in the model
        selected_cells = self.ui.gui_pieces_list.selectedIndexes()
        for cell in selected_cells:
            if ListOfPieces.offset_intervals == cell.column():
                self.vis_controller.l_o_pieces.setData(cell, chosen_offset, QtCore.Qt.EditRole)

        # Just to make sure we get rid of this
        selector = None

    #---------------
    # Not a pyqtSlot
    def _piece_settings_visibility(self, set_to):
        """
        Given True or False, makes visible and enables (or makes invisible and
        disables) everything in the "Settings for Piece" QGroupBox (and the box
        itself), and the opposite for self.lbl_select_piece
        """
        self.ui.grp_settings_for_piece.setVisible(set_to)
        self.ui.grp_settings_for_piece.setEnabled(set_to)
        self.ui.lbl_select_piece.setVisible(not set_to)

    #-------------------------------------------
    # Slot for: self.ui.btn_show_results.clicked
    @QtCore.pyqtSlot()
    def _prepare_experiment_submission(self):
        """
        Make sure the Experimenter has a properly-configured Settings
        instance, then ask it to run the experiment.
        """

        # move to the "working" panel and update it
        self.show_working.emit()
        self.update_progress.emit('0')
        self.update_progress.emit('Initializing experiment.')

        # hold a list of tuples to be signalled as settings
        list_of_settings = []

        def do_experiment():
            """
            Which experiment does the user want to run?
            """
            # NOTE: as we add different Experiment and Display combinations, we have to update this

            if self.ui.rdo_consider_intervals.isChecked():
                if self.ui.rdo_spreadsheet.isChecked():
                    list_of_settings.append(('experiment', 'IntervalsList'))
                    list_of_settings.append(('output format', 'SpreadsheetFile'))
                elif self.ui.rdo_list.isChecked():
                    list_of_settings.append(('experiment', 'IntervalsStatistics'))
                    list_of_settings.append(('output format', 'StatisticsListDisplay'))
                elif self.ui.rdo_chart.isChecked():
                    list_of_settings.append(('experiment', 'IntervalsStatistics'))
                    list_of_settings.append(('output format', 'GraphDisplay'))
            elif self.ui.rdo_consider_chord_ngrams.isChecked():
                list_of_settings.append(('experiment', 'ChordsList'))
                list_of_settings.append(('output format', 'SpreadsheetFile'))
            elif self.ui.rdo_consider_interval_ngrams.isChecked():
                if self.ui.rdo_list.isChecked():
                    list_of_settings.append(('experiment', 'IntervalNGramStatistics'))
                    list_of_settings.append(('output format', 'StatisticsListDisplay'))
                elif self.ui.rdo_chart.isChecked():
                    list_of_settings.append(('experiment', 'IntervalNGramStatistics'))
                    list_of_settings.append(('output format', 'GraphDisplay'))

        def do_threshold():
            """
            Is there a threshold value?
            """
            threshold = str(self.ui.line_threshold.text())
            if '' != threshold:
                list_of_settings.append(('threshold', threshold))

        def do_top_x():
            """
            Is there a "top x" value?
            """
            top_x = str(self.ui.line_top_x.text())
            if '' != top_x:
                list_of_settings.append(('topX', top_x))

        def do_print_quality():
            """
            Print quality?
            """
            if self.ui.rdo_heedQuality.isChecked():
                list_of_settings.append(('quality', True))
            else:
                list_of_settings.append(('quality', False))

        def do_simple_or_compound():
            """
            Simple or compound?
            """
            if self.ui.rdo_simple.isChecked():
                list_of_settings.append(('simple or compound', 'simple'))
            else:
                list_of_settings.append(('simple or compound', 'compound'))

        def do_values_of_n():
            """
            Are there values of 'n' specified?
            """
            # TODO: this has to be done safer... because this is *truly terrible*!
            # get the potential values of 'n'
            raw_of_n = str(self.ui.line_values_of_n.text())

            # Try to parse and format everything
            try:
                raw_of_n = eval(raw_of_n)
            except SyntaxError:
                pass
            else:
                post = []
                for thing in raw_of_n:
                    post.append(int(thing))
                # Put it onnnnnn
                list_of_settings.append(('values of n', post))

        # (1) Figure out the settings
        # TODO: ensure these are chosen dynamically, to correspond to the GUI
        # (1a) Which experiment?
        do_experiment()
        # (1b) Print quality?
        do_print_quality()
        # (1c) Simple or compound?
        do_simple_or_compound()
        # (1d) Is there a "values_of_n" value?
        do_values_of_n()
        # (1e) Threshold
        do_threshold()
        # (1f) Top X
        do_top_x()

        # (2) Set the settings
        for setting in list_of_settings:
            self.vis_controller.experiment_setting.emit(setting)

        # (3) Run the experiment
        self.vis_controller.run_the_experiment.emit()

    #---------------------------------------------
    # Slot for: self.ui.rdo_consider_***.clicked()
    @QtCore.pyqtSlot()
    def _update_experiment_from_object(self):
        """
        When one of the self.ui.rdo_consider_*** radio buttons is selected, this method updates the
        rest of the GUI to reflect the options relevant to that output method.
        """

        all_the_widgets = [self.ui.rdo_spreadsheet,
                            self.ui.rdo_list,
                            self.ui.rdo_chart,
                            self.ui.grp_octaves,
                            self.ui.grp_quality,
                            self.ui.grp_values_of_n]

        def on_offer(enable_these):
            """
            Given a list of the GUI objects in the "experiment" panel that should be "on," this
            method enables them and disables all the others.
            """

            # (1) Disable everything
            for each_widget in all_the_widgets:
                each_widget.setEnabled(False)

            # (2) Enable the valid things
            for each_widget in enable_these:
                each_widget.setEnabled(True)

        # Determine which widgets to enable
        which_to_enable = []

        if self.ui.rdo_consider_intervals.isChecked():
            which_to_enable = [self.ui.rdo_spreadsheet, self.ui.grp_octaves, self.ui.grp_quality,
                            self.ui.rdo_list, self.ui.rdo_chart]
        elif self.ui.rdo_consider_interval_ngrams.isChecked():
            which_to_enable = [self.ui.rdo_list, self.ui.grp_values_of_n, self.ui.grp_octaves,
                            self.ui.grp_quality, self.ui.rdo_chart]
        elif self.ui.rdo_consider_chord_ngrams.isChecked():
            which_to_enable = [self.ui.rdo_spreadsheet, self.ui.grp_values_of_n]

        # Run the on_offer()
        on_offer(which_to_enable)

    def _output_format_changed(self):
        """
        When a user chooses a different output format (in "How to Show Results" on the "show"
        panel), we may have to enable/disable the Top X and Threshold filter.
        """
        if self.ui.rdo_spreadsheet.isChecked():
            self.ui.group_top_x.setEnabled(False)
            self.ui.group_threshold.setEnabled(False)
        elif self.ui.rdo_list.isChecked():
            self.ui.group_top_x.setEnabled(True)
            self.ui.group_threshold.setEnabled(True)
        elif self.ui.rdo_chart.isChecked():
            self.ui.group_top_x.setEnabled(True)
            self.ui.group_threshold.setEnabled(True)
