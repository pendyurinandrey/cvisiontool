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
from cvisiontool.core.historymanager import HistoryList


def test_history_list_remove_newer_than_for_empty_list():
    lst = HistoryList()
    lst.remove_newer_than(1)
    assert len(lst.get_all_newest_first()) == 0


def test_history_list_remove_newer_than_for_one_element_list():
    lst = HistoryList()
    lst.add(1)
    lst.remove_newer_than(1)
    actual = lst.get_all_newest_first()
    assert len(actual) == 1
    assert all([e == a for a, e in zip(actual, [1])])


def test_history_list_remove_newer_than_for_multiple_elements():
    lst = HistoryList()
    lst.add(5)
    lst.add(4)
    lst.add(3)
    lst.add(2)
    lst.add(1)

    lst.remove_newer_than(3)
    actual = lst.get_all_newest_first()
    assert len(actual) == 3
    assert all([e == a for a, e in zip(actual, [3, 4, 5])])