##! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:             vis
# Program Description:      Measures sequences of vertical intervals.
#
# Filename: interfaces/visqtinterface.py
# Purpose: PyQt4 implementation of VisInterface.
#
# Attribution: Based on the 'harrisonHarmony.py' module available at...
#                   https://github.com/crantila/harrisonHarmony/
#
# Copyright (C) 2013 Christopher Antila, Jamie Klassen
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
Holds the VisQtInterface class, responsible for all PyQt4 stuff.
"""
# imports
from common import VisInterface, view_getter, _InterfaceMeta
from PyQt4 import QtCore, QtGui
import icons_rc

# Just a note: This file is (probably) going to become bulging huge -- the
# point is to implement a proper MVC framework, not make things pretty. We'll
# do some aesthetic refactoring once the roles have been properly divided.


class _VisQtMeta(_InterfaceMeta, QtCore.pyqtWrapperType):
    pass


class VisQtInterface(VisInterface, QtCore.QObject):
    """
    Interface for desktop app via PyQt4
    """
    __metaclass__ = _VisQtMeta
    def __init__(self, vis_controller, argv):
        super(VisQtInterface, self).__init__(vis_controller)
        self.app = QtGui.QApplication(argv)
        self.mainwindow = self.get_view(vis_controller)

    def exec_(self):
        self.mainwindow.show()
        return self.app.exec_()

    # Helper functions

    def get_multi_view(self, multi_setting, **kwargs):
        parent = kwargs['parent']
        groupBox = QtGui.QGroupBox(parent)
        groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        groupBox.setTitle(self.translate(multi_setting.display_name))
        verticalLayout = QtGui.QVBoxLayout(groupBox)
        for chk in self.get_view(multi_setting.settings, **kwargs):
            verticalLayout.addWidget(chk)
        return groupBox

    def get_lbl_line(self, setting, **kwargs):
        parent = kwargs['parent']
        lbl = QtGui.QLabel(parent)
        lbl.setText(self.translate(setting.display_name))
        line = QtGui.QLineEdit(parent)
        line.setInputMask("")
        line.setMaxLength(256)
        line.setText(self.translate(setting.value))
        def text_edited():
            setting.value = line.text()
        line.textEdited.connect(text_edited)
        return (lbl, line)

    def popup_error(self, component, description):
        """
        Notify the user that an error has happened.
        INPUTS:
        `component` - the name of the component raising the error
        `description` - a useful description of the error
        """
        # TODO: the `error` signals in the controllers should output a
        # (name, error) 2-tuple and this function can take that as an
        # argument instead of having the view-getter look at the controller's class.
        return QtGui.QMessageBox.warning(None,
                                         '{0} Error'.format(component),
                                         description,
                                         QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok),
                                         QtGui.QMessageBox.Ok)

    def setup_thread(self, controller):
        """
        Does the basic configuration for a controller
        class to use the "working" screen.
        """
        if not hasattr(self, "threads"):
            self.threads = {}
        class_name = controller.__class__.__name__
        self.threads[class_name] = QtCore.QThread()
        controller.moveToThread(self.threads[class_name])
        def thread_started():
            self.main_screen.setCurrentWidget(self.work_page)
            self.app.processEvents()
        controller.started.connect(thread_started)
        self.threads[class_name].start()

        def update_progress(progress):
            """
            Updates the "working" screen in the following ways:
            - If the argument is a two-character string that can be converted into
              an integer, or the string '100', the progress bar is set to that
              percentage completion.
            - If the argument is another string, the text below the progress bar is
              set to that string.
            """
            if isinstance(progress, basestring):
                if '100' == progress:
                    self.progress_bar.setValue(100)
                elif 3 > len(progress):
                    try:
                        new_val = int(progress)
                        self.progress_bar.setValue(new_val)
                    except ValueError:
                        self.lbl.setText(progress)
                else:
                    self.lbl.setText(progress)
            self.app.processEvents()
        controller.status.connect(update_progress)

        def popup_error(description):
            return self.popup_error(controller.__class__.__name__, description)
        controller.error.connect(popup_error)

    def working_page(self):
        page_working = QtGui.QWidget()
        verticalLayout_21 = QtGui.QVBoxLayout(page_working)
        spacerItem10 = QtGui.QSpacerItem(20,
                                         40,
                                         QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.Expanding)
        verticalLayout_21.addItem(spacerItem10)
        horizontalLayout_8 = QtGui.QHBoxLayout()
        spacerItem11 = QtGui.QSpacerItem(40,
                                         20,
                                         QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Minimum)
        horizontalLayout_8.addItem(spacerItem11)
        btn_wait_clock = QtGui.QPushButton(page_working)
        btn_wait_clock.setEnabled(True)
        btn_wait_clock.setText("")
        btn_wait_clock.setToolTip(self.translate("Hi, mom!"))
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/icons/working.png"),
                        QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        btn_wait_clock.setIcon(icon8)
        btn_wait_clock.setIconSize(QtCore.QSize(64, 64))
        btn_wait_clock.setCheckable(False)
        btn_wait_clock.setChecked(False)
        btn_wait_clock.setFlat(True)
        horizontalLayout_8.addWidget(btn_wait_clock)
        spacerItem12 = QtGui.QSpacerItem(40,
                                         20,
                                         QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Minimum)
        horizontalLayout_8.addItem(spacerItem12)
        verticalLayout_21.addLayout(horizontalLayout_8)
        lbl_status_text = QtGui.QLabel(page_working)
        lbl_status_text.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        lbl_status_text.setText(self.translate("Please wait..."))
        verticalLayout_21.addWidget(lbl_status_text)
        progress_bar = QtGui.QProgressBar(page_working)
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        self.progress_bar = progress_bar
        verticalLayout_21.addWidget(progress_bar)
        lbl_currently_processing = QtGui.QLabel(page_working)
        lbl_currently_processing.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        lbl_currently_processing.setText(self.translate("(processing)"))
        self.lbl = lbl_currently_processing
        verticalLayout_21.addWidget(lbl_currently_processing)
        spacerItem13 = QtGui.QSpacerItem(20,
                                         40,
                                         QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.Expanding)
        verticalLayout_21.addItem(spacerItem13)
        return page_working

    def translate(self, text):
        ret = QtGui.QApplication.translate("MainWindow",
                                                      str(text),
                                                      None,
                                                      QtGui.QApplication.UnicodeUTF8)
        return ret

    def make_tool_button(self, icon_path, size, tooltip, parent):
        btn = QtGui.QToolButton(parent)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path),
                            QtGui.QIcon.Normal,
                            QtGui.QIcon.Off)
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(size, size))
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setAutoRaise(True)
        btn.setText("")
        btn.setToolTip(self.translate(tooltip))
        return btn

    def make_push_button(self, icon_path, size, tooltip, parent):
        btn = QtGui.QPushButton(parent)
        btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path),
                             QtGui.QIcon.Normal,
                             QtGui.QIcon.Off)
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(size, size))
        btn.setFlat(True)
        btn.setToolTip(self.translate(tooltip))
        return btn

    # Settings Views

    @view_getter('BooleanSetting')
    def view(self, boolean_setting, **kwargs):
        parent = kwargs['parent']
        chk = QtGui.QCheckBox(parent)
        chk.setLayoutDirection(QtCore.Qt.LeftToRight)
        chk.setToolTip(self.translate(boolean_setting.extra_detail))
        chk.setText(self.translate(boolean_setting.display_name))
        chk.setChecked(boolean_setting.value)
        chk.stateChanged.connect(lambda state: setattr(boolean_setting, 'value', state))
        def on_change_display_name(name):
            chk.setText(self.translate(name))
        boolean_setting.display_name_changed.connect(on_change_display_name)
        return chk

    @view_getter('MultiChoiceSetting')
    def view(self, multi_choice_setting, **kwargs):
        return self.get_multi_view(multi_choice_setting, **kwargs)

    @view_getter('PartsComboSetting')
    def view(self, parts_combo_setting, **kwargs):
        parent = kwargs['parent']
        groupBox = QtGui.QGroupBox(parent)
        groupBox.setTitle(self.translate(parts_combo_setting.display_name))
        def on_display_name_change(name):
            groupBox.setTitle(self.translate(name))
        parts_combo_setting.display_name_changed.connect(on_display_name_change)
        vlayout = QtGui.QVBoxLayout(groupBox)
        for i, chk in enumerate(self.get_view(parts_combo_setting.settings,
                                              parent=groupBox)):
            lay = QtGui.QHBoxLayout()
            btn = QtGui.QPushButton(groupBox)
            btn.setText(self.translate('Edit Part Name'))
            def onclick(i):
                def on_click():
                    current_name = parts_combo_setting.part_names[i]
                    new_name, ok = QtGui.QInputDialog.getText(
                        None,
                        "Part Name!",
                        "Choose New Part Name",
                        QtGui.QLineEdit.Normal,
                        current_name
                    )
                    parts_combo_setting.set_part_name(i, str(new_name))
                return on_click
            btn.clicked.connect(onclick(i))
            lay.addWidget(chk)
            lay.addWidget(btn)
            vlayout.addLayout(lay)
        return groupBox

    @view_getter('StringSetting')
    def view(self, string_setting, **kwargs):
        return self.get_lbl_line(string_setting, **kwargs)

    @view_getter('OffsetSetting')
    def view(self, offset_setting, **kwargs):
        lbl, line = self.get_lbl_line(offset_setting, **kwargs)
        line.setEnabled(False)
        parent = kwargs['parent']
        btn = QtGui.QPushButton(parent)
        btn.setEnabled(False)
        btn.setText(self.translate("Choose Offset Note"))
        # TODO: connect signals
        return (lbl, line, btn)

    @view_getter('Settings')
    def view(self, settings, **kwargs):
        for sett in settings:
            yield self.get_view(sett, **kwargs)

    # Model Views

    @view_getter('ListOfFiles')
    def view(self, list_of_files, **kwargs):
        parent = kwargs['parent']
        gui_file_list = QtGui.QListView(parent)
        gui_file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        gui_file_list.setModel(list_of_files)
        return gui_file_list

    @view_getter('PiecesSelection')
    def view(self, selection, **kwargs):
        parent = kwargs['parent']
        container = QtGui.QWidget(parent)
        layout = QtGui.QVBoxLayout(container)
        self.selection_view = None
        self.partscombo_widget = None
        self.msg_widget = None
        self.chk_basso_seguente = None
        self.chk_all_pairs = None
        def on_pieces_change(pieces):
            if self.selection_view:
                self.selection_view.deleteLater()
                if self.partscombo_widget or self.msg_widget:
                    if self.partscombo_widget:
                        for sett in selection.settings.current_parts_combo.settings:
                            # this is a fix for a bug in PyQt4
                            sett.display_name_changed.connect(lambda:None)
                            sett.display_name_changed.disconnect()
                        selection.settings.current_parts_combo.display_name_changed.disconnect()
                        self.partscombo_widget = None
                    if self.msg_widget:
                        self.msg_widget = None
                    selection.parts_enabled_changed.disconnect()
                if self.chk_basso_seguente and self.chk_all_pairs:
                    selection.bs_ap_enabled_changed.disconnect()
                    selection.settings.basso_seguente.display_name_changed.disconnect()
                    selection.settings.all_pairs.display_name_changed.disconnect()
                    self.chk_basso_seguente = None
                    self.chk_all_pairs = None
                layout.removeWidget(self.selection_view)
                self.selection_view = None
            if pieces:
                grp_settings_for_selection = QtGui.QGroupBox(parent)
                grp_settings_for_selection.setTitle(
                    self.translate(selection.settings.description.value)
                )
                (
                    (lbl_title, line_title),
                    self.chk_all_pairs,
                    self.chk_basso_seguente,
                    (lbl_offset, line_offset, btn_offset),
                    chk_salami
                ) = self.get_view(selection.settings, parent=grp_settings_for_selection)
                line_title.textEdited.connect(selection.title_changed.emit)
                gridLayout_3 = QtGui.QGridLayout(grp_settings_for_selection)
                spacerItem6 = QtGui.QSpacerItem(20,
                                                40,
                                                QtGui.QSizePolicy.Minimum,
                                                QtGui.QSizePolicy.Expanding)
                gridLayout_3.addItem(spacerItem6, 3, 1, 1, 1)
                spacerItem7 = QtGui.QSpacerItem(20,
                                                40,
                                                QtGui.QSizePolicy.Minimum,
                                                QtGui.QSizePolicy.Expanding)
                gridLayout_3.addItem(spacerItem7, 6, 1, 1, 1)
                spacerItem8 = QtGui.QSpacerItem(40,
                                                20,
                                                QtGui.QSizePolicy.Expanding,
                                                QtGui.QSizePolicy.Minimum)
                gridLayout_3.addItem(spacerItem8, 9, 1, 1, 2)
                gridLayout_3.addWidget(self.get_view(selection.add_parts_combo,
                                                     parent=grp_settings_for_selection),
                                       9, 0, 1, 1)
                gridLayout_3.addWidget(line_offset, 0, 1, 1, 1)
                gridLayout_3.addWidget(lbl_offset, 0, 0, 1, 1)
                gridLayout_3.addWidget(btn_offset, 0, 2, 1, 1)
                widget_2 = QtGui.QWidget(grp_settings_for_selection)
                horizontalLayout_9 = QtGui.QHBoxLayout(widget_2)
                horizontalLayout_9.setMargin(0)
                spacerItem9 = QtGui.QSpacerItem(40,
                                                20,
                                                QtGui.QSizePolicy.Maximum,
                                                QtGui.QSizePolicy.Minimum)
                horizontalLayout_9.addItem(spacerItem9)
                widget_part_boxes = QtGui.QWidget(widget_2)
                verticalLayout_22 = QtGui.QVBoxLayout(widget_part_boxes)
                verticalLayout_22.setMargin(0)
                verticalLayout_22.addWidget(self.chk_all_pairs)
                verticalLayout_22.addWidget(self.chk_basso_seguente)
                def on_parts_enabled_change(state):
                    if self.partscombo_widget:
                        for sett in selection.settings.current_parts_combo.settings:
                            sett.display_name_changed.disconnect()
                        selection.settings.current_parts_combo.display_name_changed.disconnect()
                        self.partscombo_widget.deleteLater()
                        verticalLayout_22.removeWidget(self.partscombo_widget)
                        self.partscombo_widget = None
                    if self.msg_widget:
                        self.msg_widget.deleteLater()
                        verticalLayout_22.removeWidget(self.msg_widget)
                        self.msg_widget = None
                    if state:
                        self.partscombo_widget = self.get_view(
                            selection.settings.current_parts_combo,
                            parent=container
                        )
                        for sett in selection.settings.current_parts_combo.settings:
                            print sett.display_name
                        verticalLayout_22.addWidget(self.partscombo_widget)
                    else:
                        groupBox = QtGui.QGroupBox(container)
                        vlayout = QtGui.QVBoxLayout(groupBox)
                        lbl = QtGui.QLabel(groupBox)
                        lbl.setText(self.translate(selection.parts_message))
                        lbl.setAlignment(QtCore.Qt.AlignCenter)
                        vlayout.addWidget(lbl)
                        self.msg_widget = groupBox
                        verticalLayout_22.addWidget(self.msg_widget)
                selection.parts_enabled_changed.connect(on_parts_enabled_change)
                on_parts_enabled_change(selection.parts_enabled)
                def on_bs_ap_enabled_change(state):
                    self.chk_all_pairs.setEnabled(state)
                    self.chk_basso_seguente.setEnabled(state)
                on_bs_ap_enabled_change(selection.bs_ap_enabled)
                selection.bs_ap_enabled_changed.connect(on_bs_ap_enabled_change)
                lbl_title.setEnabled(selection.title_editable)
                line_title.setEnabled(selection.title_editable)
                horizontalLayout_9.addWidget(widget_part_boxes)
                gridLayout_3.addWidget(widget_2, 8, 0, 1, 3)
                gridLayout_3.addWidget(line_title, 5, 1, 1, 2)
                gridLayout_3.addWidget(lbl_title, 5, 0, 1, 1)
                gridLayout_3.addWidget(chk_salami, 1, 0, 1, 3)
                self.selection_view = grp_settings_for_selection
            else:
                lbl_select_piece = QtGui.QLabel(parent)
                lbl_select_piece.setText(
                    self.translate('Select piece(s) to see possible settings.')
                )
                lbl_select_piece.setAlignment(QtCore.Qt.AlignCenter)
                self.selection_view = lbl_select_piece
            layout.addWidget(self.selection_view)
        selection.pieces_changed.connect(on_pieces_change)
        on_pieces_change(selection.pieces)
        return container

    @view_getter('ListOfPieces')
    def view(self, list_of_pieces, **kwargs):
        parent = kwargs['parent']

        class PiecesListView(QtGui.QTableView):
            def selectionChanged(self, selected, unselected):
                selected_rows = set(ind.row() for ind in self.selectedIndexes())
                list_of_pieces.selected_rows = selected_rows
                super(PiecesListView, self).selectionChanged(selected, unselected)

        gui_pieces_list = PiecesListView(parent)
        gui_pieces_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        gui_pieces_list.horizontalHeader().setMinimumSectionSize(2)
        gui_pieces_list.verticalHeader().setVisible(False)
        gui_pieces_list.setModel(list_of_pieces)
        gui_pieces_list.resizeColumnsToContents()
        return gui_pieces_list

    @view_getter('VisInfo')
    def view(self, info):
        page_about = QtGui.QWidget()
        verticalLayout_5 = QtGui.QVBoxLayout(page_about)
        groupBox_4 = QtGui.QGroupBox(page_about)
        groupBox_4.setTitle(self.translate(info.title))
        verticalLayout_6 = QtGui.QVBoxLayout(groupBox_4)
        label_copyright = QtGui.QLabel(groupBox_4)
        label_copyright.setText(self.translate(info.copyright))
        verticalLayout_6.addWidget(label_copyright)
        line = QtGui.QFrame(groupBox_4)
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        verticalLayout_6.addWidget(line)
        label_about = QtGui.QLabel(groupBox_4)
        label_about.setText(self.translate(info.about))
        verticalLayout_6.addWidget(label_about)
        verticalLayout_5.addWidget(groupBox_4)
        return page_about

    # Main Window Views

    @view_getter('VisController')
    def view(self, vis_controller):
        MainWindow = QtGui.QMainWindow()
        centralwidget = QtGui.QWidget(MainWindow)
        verticalLayout = QtGui.QVBoxLayout(centralwidget)
        function_menu = QtGui.QWidget(centralwidget)
        horizontalLayout = QtGui.QHBoxLayout(function_menu)
        horizontalLayout.setMargin(0)
        main_screen = self.get_view(vis_controller.set_active_controller,
                                    parent=centralwidget)
        horizontalLayout.addWidget(self.get_view(vis_controller.choose_files,
                                                 parent=function_menu))
        horizontalLayout.addWidget(self.get_view(vis_controller.import_files,
                                                 parent=function_menu))
        horizontalLayout.addWidget(self.get_view(vis_controller.setup_analysis,
                                                 parent=function_menu))
        horizontalLayout.addWidget(self.get_view(vis_controller.analyze_pieces,
                                                 parent=function_menu))
        horizontalLayout.addWidget(self.get_view(vis_controller.setup_experiment,
                                                 parent=function_menu))
        # TODO: extra buttons for progressing from Experiment to Visualization,
        # and implement their associated VisController methods
        spacerItem = QtGui.QSpacerItem(40,
                                       20,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        horizontalLayout.addItem(spacerItem)
        horizontalLayout.addWidget(self.get_view(vis_controller.get_info,
                                                 parent=function_menu))
        verticalLayout.addWidget(function_menu)
        verticalLayout.addWidget(main_screen)
        MainWindow.setCentralWidget(centralwidget)
        statusbar = QtGui.QStatusBar(MainWindow)
        MainWindow.setStatusBar(statusbar)
        MainWindow.setWindowTitle(self.translate("vis"))
        # MainWindow.setGeometry(300, 300, 250, 150)
        return MainWindow

    @view_getter('set_active_controller')
    def view(self, set_active_controller, **kwargs):
        # This is a bit weird -- maybe it should go in the
        # main VisController view-getter
        parent = kwargs['parent']
        vis_controller = set_active_controller.__self__
        main_screen = QtGui.QStackedWidget(parent)
        controllers = [
            vis_controller.importer,
            vis_controller.analyzer,
            vis_controller.experimenter,
        ]
        widgets = {
            controller.__class__.__name__: self.get_view(controller)
            for controller in controllers
        }
        for widget in widgets.itervalues():
            main_screen.addWidget(widget)
        def switch_widget(class_name):
            main_screen.setCurrentWidget(widgets[str(class_name)])
        vis_controller.active_controller_changed.connect(switch_widget)
        self.work_page = self.working_page()
        main_screen.addWidget(self.work_page)
        info_widget = self.get_view(vis_controller.info)
        main_screen.addWidget(info_widget)
        def info_requested():
            main_screen.setCurrentWidget(info_widget)
        vis_controller.info_signal.connect(info_requested)
        self.main_screen = main_screen
        main_screen.setCurrentIndex(0)
        return main_screen

    @view_getter('choose_files')
    def view(self, choose_files, **kwargs):
        btn_choose_files = self.make_tool_button(":/icons/icons/choose_files.png",
                                                              64,
                                                              "Choose Files",
                                                              kwargs['parent'])
        btn_choose_files.setChecked(True)
        btn_choose_files.clicked.connect(choose_files)
        return btn_choose_files

    @view_getter('import_files')
    def view(self, import_files, **kwargs):
        btn_step1 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                                     32,
                                                     "Continue to Step 2",
                                                     kwargs['parent'])
        btn_step1.clicked.connect(import_files)
        return btn_step1

    @view_getter('setup_analysis')
    def view(self, setup_analysis, **kwargs):
        btn_analyze = self.make_tool_button(":/icons/icons/analyze.png",
                                                        64,
                                                        "Prepare and Assemble for Analysis",
                                                        kwargs['parent'])
        btn_analyze.setEnabled(False)
        btn_analyze.setChecked(False)
        btn_analyze.clicked.connect(setup_analysis)
        return btn_analyze

    @view_getter('analyze_pieces')
    def view(self, analyze_pieces, **kwargs):
        btn_step2 = self.make_tool_button(":/icons/icons/right-arrow.png",
                                                     32,
                                                     "Continue to the Step 3",
                                                     kwargs['parent'])
        btn_step2.setEnabled(False)
        btn_step2.clicked.connect(analyze_pieces)
        return btn_step2

    @view_getter('setup_experiment')
    def view(self, setup_experiment, **kwargs):
        btn_experiment = self.make_tool_button(":/icons/icons/show_results.png",
                                                            64,
                                                            "Show and Save Results",
                                                            kwargs['parent'])
        btn_experiment.setEnabled(False)
        btn_experiment.clicked.connect(setup_experiment)
        return btn_experiment

    @view_getter('get_info')
    def view(self, get_info, **kwargs):
        btn_about = self.make_tool_button(":/icons/icons/help-about.png",
                                                     64,
                                                     "About \"vis\"",
                                                     kwargs['parent'])
        btn_about.clicked.connect(get_info)
        return btn_about

    # "Import" Frame Views

    @view_getter('Importer')
    def view(self, importer):
        self.setup_thread(importer)
        page_choose = QtGui.QWidget()
        verticalLayout_2 = QtGui.QVBoxLayout(page_choose)
        grp_choose_files = QtGui.QGroupBox(page_choose)
        grp_choose_files.setTitle(self.translate("Choose Files"))
        horizontalLayout_3 = QtGui.QHBoxLayout(grp_choose_files)
        widget_3 = QtGui.QWidget(grp_choose_files)
        verticalLayout_7 = QtGui.QVBoxLayout(widget_3)
        verticalLayout_7.setMargin(0)
        widget_4 = QtGui.QWidget(widget_3)
        horizontalLayout_4 = QtGui.QHBoxLayout(widget_4)
        horizontalLayout_4.setMargin(0)
        label_3 = QtGui.QLabel(widget_4)
        label_3.setText(self.translate("Files to Analyze:"))
        horizontalLayout_4.addWidget(label_3)
        spacerItem1 = QtGui.QSpacerItem(40,
                                        20,
                                        QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Minimum)
        horizontalLayout_4.addItem(spacerItem1)
        files_list_view = self.get_view(importer.list_of_files, parent=widget_3)
        horizontalLayout_4.addWidget(self.get_view(importer.add_directory,
                                                   parent=widget_4))
        horizontalLayout_4.addWidget(self.get_view(importer.add_files,
                                                   parent=widget_4))
        horizontalLayout_4.addWidget(self.get_view(importer.remove_files,
                                                   parent=widget_4,
                                                   files_list=files_list_view))
        verticalLayout_7.addWidget(widget_4)
        verticalLayout_7.addWidget(files_list_view)
        widget_5 = QtGui.QWidget(widget_3)
        widget_5.setLayoutDirection(QtCore.Qt.RightToLeft)
        horizontalLayout_7 = QtGui.QHBoxLayout(widget_5)
        horizontalLayout_7.setMargin(0)
        horizontalLayout_7.addWidget(self.get_view(importer.multiprocess,
                                                   parent=widget_5))

        spacerItem2 = QtGui.QSpacerItem(40,
                                                  20,
                                                  QtGui.QSizePolicy.Expanding,
                                                  QtGui.QSizePolicy.Minimum)
        horizontalLayout_7.addItem(spacerItem2)
        verticalLayout_7.addWidget(widget_5)
        horizontalLayout_3.addWidget(widget_3)
        widget = QtGui.QWidget(grp_choose_files)
        widget.setMaximumSize(QtCore.QSize(200, 16777215))
        verticalLayout_8 = QtGui.QVBoxLayout(widget)
        verticalLayout_8.setMargin(0)
        horizontalLayout_3.addWidget(widget)
        verticalLayout_2.addWidget(grp_choose_files)
        return page_choose

    @view_getter('add_directory')
    def view(self, add_directory, **kwargs):
        btn_dir_add = self.make_push_button(":/icons/icons/add-dir.png",
                                                        32,
                                                        "Add Directory",
                                                        kwargs['parent'])
        def on_click():
            d = QtGui.QFileDialog.getExistingDirectory(
                None,
                "Choose Directory to Analyze",
                '',
                QtGui.QFileDialog.ShowDirsOnly
            )
            add_directory(str(d))
        btn_dir_add.clicked.connect(on_click)
        return btn_dir_add

    @view_getter('add_files')
    def view(self, add_files, **kwargs):
        btn_file_add = self.make_push_button(":/icons/icons/add-file.png",
                                                         32,
                                                         "Add Files",
                                                         kwargs['parent'])
        def on_click():
            files = QtGui.QFileDialog.getOpenFileNames(
                None,
                "Choose Files to Analyze",
                '',
                '*.nwc *.mid *.midi *.mxl *.krn *.xml *.md',
                None)
            add_files(files)
        btn_file_add.clicked.connect(on_click)
        return btn_file_add

    @view_getter('remove_files')
    def view(self, remove_files, **kwargs):
        files_list = kwargs.pop('files_list')
        btn_file_remove = self.make_push_button(":/icons/icons/list-remove.png",
                                                             32,
                                                             "Remove Selected Items",
                                                             kwargs['parent'])
        def on_click():
            currently_selected = files_list.selectedIndexes()
            remove_files(currently_selected)
        btn_file_remove.clicked.connect(on_click)
        return btn_file_remove

    # "Analyze" Frame Views

    @view_getter('Analyzer')
    def view(self, analyzer):
        page_analyze = QtGui.QWidget()
        verticalLayout_23 = QtGui.QVBoxLayout(page_analyze)
        groupBox = QtGui.QGroupBox(page_analyze)
        groupBox.setTitle(self.translate("Assemble Results, Statistics, Analyses"))
        gridLayout = QtGui.QGridLayout(groupBox)
        gridLayout.addWidget(self.get_view(analyzer.list_of_pieces, parent=groupBox), 1, 0)
        gridLayout.setColumnStretch(0, 2)
        gridLayout.addWidget(self.get_view(analyzer.current_pieces, parent=groupBox), 1, 1)
        widget_6 = QtGui.QWidget(groupBox)
        horizontalLayout_5 = QtGui.QHBoxLayout(widget_6)
        horizontalLayout_5.setMargin(0)
        for widget in self.get_view(analyzer.settings, parent=widget_6):
            horizontalLayout_5.addWidget(widget)
        gridLayout.addWidget(widget_6, 0, 1)
        verticalLayout_23.addWidget(groupBox)
        self.setup_thread(analyzer)
        return page_analyze

    @view_getter('add_parts_combo')
    def view(self, add_parts_combo, **kwargs):
        parent = kwargs['parent']
        btn_add_check_combo = QtGui.QPushButton(parent)
        btn_add_check_combo.setEnabled(False)
        btn_add_check_combo.setText(self.translate("Add Combination"))
        # TODO: connect signals
        return btn_add_check_combo

    # "Experiment" Frame Views

    @view_getter('set_experiment')
    def view(self, set_experiment, **kwargs):
        parent = kwargs['parent']
        combo_choose_experiment = QtGui.QComboBox(parent)
        # TODO: connect signals
        return combo_choose_experiment

    @view_getter('Experimenter')
    def view(self, experimenter):
        page_show = QtGui.QWidget()
        verticalLayout_3 = QtGui.QVBoxLayout(page_show)
        groupBox_2 = QtGui.QGroupBox(page_show)
        groupBox_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        groupBox_2.setTitle(self.translate("Conduct an Experiment"))
        formLayout = QtGui.QFormLayout(groupBox_2)
        formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        formLayout.setContentsMargins(12, -1, -1, -1)
        formLayout.setWidget(0,
                                    QtGui.QFormLayout.FieldRole,
                                    self.get_view(experimenter.set_experiment,
                                                      parent=groupBox_2))
        lbl_choose_experiment = QtGui.QLabel(groupBox_2)
        lbl_choose_experiment.setText(self.translate("Choose an Experiment:"))
        formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, lbl_choose_experiment)
        verticalLayout_3.addWidget(groupBox_2)
        def experiment_error(description):
            return self.error_popup(experimenter.__class__.__name__, description)
        experimenter.error.connect(experiment_error)
        return page_show
