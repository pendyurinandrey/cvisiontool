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
from typing import Any, List, Optional

import numpy as np
from PySide2.QtCore import Signal, QObject

from cvisiontool.core.actions import Action


@dataclass(frozen=True)
class HistoryEntry:
    action: Action
    mat_bgr: np.ndarray


class HistoryManager(QObject):
    history_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__history = HistoryList()

    def add_entry(self, entry: HistoryEntry):
        self.__history.add(entry)
        self.history_changed.emit()

    def get_entries(self) -> List[HistoryEntry]:
        return self.__history.get_all_newest_first()

    def remove_newer_than(self, entry: HistoryEntry):
        self.__history.remove_newer_than(entry)
        self.history_changed.emit()


class _ListNode:
    def __init__(self, element, prev_node, next_node):
        self.__element = element
        self.__prev_node = prev_node
        self.__next_node = next_node

    def set_next_node(self, next_node):
        self.__next_node = next_node

    def set_prev_node(self, prev_node):
        self.__prev_node = prev_node

    def get_next_node(self):
        return self.__next_node

    def get_prev_node(self):
        return self.__prev_node

    def get_element(self):
        return self.__element


class HistoryList:

    def __init__(self):
        self.__head: Optional[_ListNode] = None

    def add(self, element: Any):
        if self.__head is None:
            self.__head = _ListNode(element, None, None)
        else:
            new_head = _ListNode(element, prev_node=None, next_node=self.__head)
            self.__head.set_prev_node(new_head)
            self.__head = new_head

    def get_all_newest_first(self) -> List[Any]:
        if self.__head is None:
            return []
        else:
            next_node: _ListNode = self.__head
            result = [next_node.get_element()]
            next_node = next_node.get_next_node()
            while next_node is not None:
                result.append(next_node.get_element())
                next_node = next_node.get_next_node()
            return result

    def remove_newer_than(self, element: Any):
        current: _ListNode = self.__head
        while current is not None:
            if current.get_element() is element:
                prev: _ListNode = current.get_prev_node()
                if prev is not None:
                    prev.set_next_node(None)
                current.set_prev_node(None)
                self.__head = current
                return
            else:
                current = current.get_next_node()
