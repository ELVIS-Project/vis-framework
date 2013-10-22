#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               views/web_view.py
# Purpose:                Dialogue window to display HTML output from vis.
#
# Copyright (C) 2013 Christopher Antila
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
#--------------------------------------------------------------------------------------------------
"""
Dialogue window to HTML output from vis.
"""

from os import getcwd
from shutil import copyfile
from vis.views.Ui_web_display import Ui_Web_Display
from PyQt4 import QtGui
from PyQt4.QtCore import QUrl, Qt


class VisWebView(object):
    """
    Display an HTML file. The class was designed for an HTML-format table as outputted by
    :meth:`pandas.DataFrame.to_html` or an image as outputted by our R script.
    """

    # These shouldn't change at runtime, but they also shouldn't be publically accessible.
    # This is where the HTML output is outputted.
    _html_path = u'outputs/html_output.html'
    # Replace this text with the well-formatted <img /> tag.
    _image_replace = u'<!-- img tag goes here -->'
    # Replace this text with the well-formatted <table> from pandas.
    _table_replace = u'<!-- pandas table goes here -->'
    # Path of the HTML file for displaying images.
    _image_html = u'views/custom_image.html'
    # Path of the HTML file for displaying tables.
    _table_html = u'views/custom_table.html'
    # Replace this with the new table header.
    _old_header = """<thead>
    <tr style="text-align: right;">
      <th></th>
      <th>data</th>"""

    def __init__(self):
        self.dialog = QtGui.QDialog()
        self._gui = Ui_Web_Display()
        self._gui.setupUi(self.dialog)
        self._pathname = None  # the unicode pathname of the object to display
        self._display = None  # the resulting QString holding HTML that actually gets displayed
        self._trigger_return = []  # what to return from the trigger() method
        self._token_name = None  # the name of whatever we're displaying (intervals, 2-grams, etc.)
        self._result_type = None  # whether this is for a "table" or "image"
        # set "Ctrl + w" to close the window
        QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_W),
                        self.dialog,
                        self.dialog.accept,
                        context=Qt.WindowShortcut)

    def _make_img_tag(self):
        "Output the proper <img /> tag."
        return u'<img src="' + self._pathname + u'" />'

    def _make_table_header(self):
        "Output the proper <th> tag."
        return u'<thead><tr style="text-align: right;"><th>' + \
            self._token_name + \
            u'</th><th>Frequency</th>'

    def trigger(self, pathname, result_type, token_name=u'Object'):
        """
        Set up the window and display the HTML-format table loaded from the indicated path. The
        return value tells you whether the user requested CSV- or Excel-format output, and the
        pathname for which they requested it. HTML-format is handled internally.

        :param pathname: The pathname of the table to display.
        :type pathname: ``basestring``
        :param result_type: Whether ``pathname`` is a ``'table'`` or ``'image'``.
        :type result_type: ``basestring``
        :param token_name: The name of objects being displayed, as it should appear in the table.
            The default is "Object."
        :type token_name: '`basestring``
        :returns: A list of 2-tuples telling which type of output to save and where to save it.
        :rtype: list of (``basestring``, ``basestring``)

        Example return:

        >>> textview.trigger()
        [('CSV', '/home/christopher/results.csv'), \
         ('CSV', '/home/christopher/to_send/results.csv'), \
         ('Excel', '/home/christopher/results.xlsx')]
        """
        self._pathname = unicode(pathname)
        self._token_name = token_name
        self._result_type = result_type
        # add our custom formatting to the file
        self._custom_formatting()
        # UI setup stuff
        self._gui.webview.load(QUrl.fromLocalFile(getcwd() + u'/' + VisWebView._html_path))
        self.dialog.show()
        # Setup signals (dialog close is done automatically) and disable unusable buttons
        if u'table' == self._result_type:
            self._gui.btn_csv.clicked.connect(self._save_csv)
            self._gui.btn_html.clicked.connect(self._save_html)
            self._gui.btn_excel.clicked.connect(self._save_excel)
            self._gui.btn_png.setVisible(False)
        elif u'image' == self._result_type:
            self._gui.btn_png.clicked.connect(self._save_png)
            self._gui.btn_csv.setVisible(False)
            self._gui.btn_html.setVisible(False)
            self._gui.btn_excel.setVisible(False)
        # Show the form
        self.dialog.exec_()
        # ... (user does some stuff)...
        # if applicable, return the instructions for what to save and where
        if len(self._trigger_return) > 0:
            return self._trigger_return

    def _custom_formatting(self):
        """
        Read the template HTML file and replace the "replace_me" comment with the appropriate data,
        assigning the result to the "self._display" variable.
        """
        replace_with = u''
        if u'table' == self._result_type:
            template_pathname = self._table_html
            replace_this = VisWebView._table_replace
        elif u'image' == self._result_type:
            template_pathname = self._image_html
            replace_this = VisWebView._image_replace
        # read HTML template
        template_file = open(template_pathname, 'r')
        template_str = template_file.read()
        template_file.close()
        if u'table' == self._result_type:
            # read the pandas-produced table
            table_file = open(self._pathname, 'r')
            replace_with = table_file.read()
            table_file.close()
            # replace the old table header with a better one (i.e., put in column names)
            replace_with = replace_with.replace(VisWebView._old_header, self._make_table_header())
        elif u'image' == self._result_type:
            replace_with = self._make_img_tag()
        # replace the "replace me" comment
        self._display = template_str.replace(replace_this, replace_with)
        # save the HTML file (image-loading won't work unless we do this)
        try:
            html_file = open(VisWebView._html_path, 'w')
            html_file.write(self._display)
            html_file.close()
        except IOError as ioe:
            QtGui.QMessageBox.warning(None,
                u'Unable to Display Results',
                u'We could not display results because we could not write the HTML file.\n\n' + \
                    u'The error says:\n\n' + unicode(ioe),
                QtGui.QMessageBox.StandardButtons(\
                    QtGui.QMessageBox.Ok),
                QtGui.QMessageBox.Ok)

    def _save_png(self):
        self._save_button('png')

    def _save_csv(self):
        self._save_button('csv')

    def _save_html(self):
        self._save_button('html')

    def _save_excel(self):
        self._save_button('excel')

    def _save_button(self, format):
        """
        Copy the file from its current path to a new one, effectively "saving" it for the user.

        .. note:: The "png" output format applies only and always to images.

        :param format: The format to save (csv, html, excel, png).
        :type format: ```basestring```
        """
        poss_formats = ['csv', 'html', 'excel', 'png']
        if format not in poss_formats:
            if u'table' == self._result_type:
                format = poss_formats[0]  # default to CSV
            else:
                format = 'png'
        # deal with the pathname
        new_path = unicode(QtGui.QFileDialog.getSaveFileName(\
            None,
            u'Choose a File Name',
            u'',
            u'',
            None))
        if new_path != u'':
            if 'png' == format:
                try:
                    copyfile(self._pathname, new_path)
                except IOError as ioe:
                    QMessageBox.warning(None,
                        u'Error While Saving',
                        u'Received an error saving your image:\n\n' + unicode(ioe),
                        QMessageBox.StandardButtons(\
                            QMessageBox.Ok),
                        QMessageBox.Ok)
            elif 'html' == format:
                # we have the HTML, so we can save it
                if u'.html' != new_path[-5:] and u'.htm' != new_path[-4:]:
                    new_path += u'.html'
                try:
                    html_file = open(new_path, 'w')
                    html_file.write(self._display)
                    html_file.close()
                except IOError as ioe:
                    QtGui.QMessageBox.warning(None,
                        u'Error While Saving Text',
                        u'Received an error saving text:\n\n' + unicode(ioe),
                        QtGui.QMessageBox.StandardButtons(\
                            QtGui.QMessageBox.Ok),
                        QtGui.QMessageBox.Ok)
            # we don't have the CSV or Excel, so we have to ask the caller to do it for us
            elif 'csv' == format:
                self._trigger_return.append((u'CSV', new_path))
            elif 'excel' == format:
                self._trigger_return.append((u'Excel', new_path))
