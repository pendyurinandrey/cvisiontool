#   cvisiontool - the software for exploring Computer Vision
#   Copyright (C) 2020 pendyurinandrey
#  #
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  #
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
from dataclasses import dataclass
from typing import Dict, Optional, Any, List

from PySide2.QtCore import Slot, Qt, QPoint, Signal
from PySide2.QtWidgets import QDialog, QVBoxLayout, QListWidget, QMenu, QAction

from cvisiontool.core.historymanager import HistoryManager, HistoryEntry


class HistoryDialog(QDialog):
    apply_history_entry = Signal(HistoryEntry)

    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle('History')
        self.__current_entries: Dict[int, HistoryEntry] = {}
        self.__history_manager = history_manager
        self.__list_widget = self.__create_history_widget()
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.__list_widget)
        self.setLayout(self.__layout)

        self.__history_manager.history_changed.connect(self.__on_history_changed)

        self.__fill_history()

    def __create_history_widget(self) -> QListWidget:
        list_widget = QListWidget(self)
        list_widget.setWordWrap(True)
        list_widget.setTextElideMode(Qt.ElideNone)

        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.__on_history_widget_context_menu)
        return list_widget

    @Slot(QPoint)
    def __on_history_widget_context_menu(self, point: QPoint):
        if len(self.__list_widget.selectedItems()) == 0:
            return

        global_pos = self.__list_widget.mapToGlobal(point)

        menu = QMenu()
        show_action: QAction = menu.addAction('Show')
        show_action.triggered.connect(self.__on_show_action_triggered)
        discard_above_action: QAction = menu.addAction('Discard actions above')
        discard_above_action.triggered.connect(self.__on_discard_above_action_triggered)

        menu.exec_(global_pos)

    def __fill_history(self):
        entries = self.__history_manager.get_entries()
        self.__current_entries.clear()
        for i in range(0, len(entries)):
            self.__list_widget.addItem(entries[i].action.to_string())
            self.__current_entries[i] = entries[i]

    @Slot()
    def __on_history_changed(self):
        self.__list_widget.clear()
        self.__fill_history()

    @Slot()
    def __on_show_action_triggered(self):
        chosen_id = self.__list_widget.currentRow()
        chosen_entry = self.__current_entries[chosen_id]
        self.apply_history_entry.emit(chosen_entry)

    def __on_discard_above_action_triggered(self):
        chosen_id = self.__list_widget.currentRow()
        chosen_entry = self.__current_entries[chosen_id]
        self.__history_manager.remove_newer_than(chosen_entry)
