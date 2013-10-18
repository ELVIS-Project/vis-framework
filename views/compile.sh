#!/bin/bash

# Compile the UI files
for ui in ui/*.ui; do
	file=$(basename $ui .ui)
	pyuic4 "ui/${file}.ui" -o "Ui_${file}.py"
done

# Compile the resource files (for icons)
for qrc in ui/*.qrc; do
	file=$(basename $qrc .qrc)
	pyrcc4 "ui/${file}.qrc" -o "${file}_rc.py"
done

# Modify "Ui_main_window.py" as required
exec `python modify_main_window.py`
