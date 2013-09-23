#!/bin/bash
for ui in ui/*.ui; do
	file=$(basename $ui .ui)
	pyuic4 "ui/${file}.ui" -o "Ui_${file}.py"
done
for qrc in ui/*.qrc; do
	file=$(basename $qrc .qrc)
	pyrcc4 "ui/${file}.qrc" -o "${file}_rc.py"
done