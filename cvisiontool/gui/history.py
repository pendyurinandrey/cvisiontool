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
from typing import Dict

import numpy as np
from PySide2.QtCore import Signal, Slot, QObject, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QListWidget


@dataclass(frozen=True)
class HistoryEntry:
    description: str
    mat_bgr: np.ndarray


class HistoryManager(QObject):
    history_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__entries: Dict[int, HistoryEntry] = {}
        self.__index = 0

    def add_entry(self, entry: HistoryEntry):
        self.__entries[self.__index] = entry
        self.__index += 1
        self.history_changed.emit()

    def remove_entry(self, index):
        if index in self.__entries.keys():
            del self.__entries[index]
            self.history_changed.emit()

    def get_entries(self) -> Dict[int, HistoryEntry]:
        return self.__entries


# Instance
global_history_manager = HistoryManager()


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('History')
        self.__list_widget = QListWidget(self)
        self.__list_widget.setWordWrap(True)
        self.__list_widget.setTextElideMode(Qt.ElideNone)
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.__list_widget)
        self.setLayout(self.__layout)

        global_history_manager.history_changed.connect(self.__on_history_changed)

        self.__fill_history()

    def __fill_history(self):
        for index, entry in global_history_manager.get_entries().items():
            self.__list_widget.addItem(entry.description)

    @Slot()
    def __on_history_changed(self):
        self.__list_widget.clear()
        self.__fill_history()
