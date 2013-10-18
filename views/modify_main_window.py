#!/usr/bin/env python

# Modify "Ui_main_window.py" as required
filename = u'Ui_main_window.py'
old_str = u'self.gui_pieces_list = QtGui.QTableView(self.groupBox)'
new_str = u"""class GuiPiecesList(QtGui.QTableView):
            selection_changed = QtCore.pyqtSignal()
            def selectionChanged(self, selected, deselected):
                self.selection_changed.emit()
                super(GuiPiecesList, self).selectionChanged(selected, deselected)
        self.gui_pieces_list = GuiPiecesList(self.groupBox)"""

ui_file = open(filename, 'r')
ui_file_txt = ui_file.read()
ui_file.close()

ui_file_txt = ui_file_txt.replace(old_str, new_str)

ui_file = open(filename, 'w')
ui_file.write(ui_file_txt)
ui_file.close()
