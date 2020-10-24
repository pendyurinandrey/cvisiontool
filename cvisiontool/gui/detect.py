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
from typing import Tuple

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QFormLayout, QLabel, \
    QMessageBox

from cvisiontool.core.actions import ActionFactory
from cvisiontool.gui.common import AbstractMatActionDialog, ChooseOneOfWidget

import cv2.cv2 as cv


class HoughCircleDialog(AbstractMatActionDialog):

    def _create_main_widget(self) -> QWidget:
        self.__main_widget = QWidget()
        self.__main_layout = QVBoxLayout(self.__main_widget)

        self.__method_widget = ChooseOneOfWidget('Method', {
            cv.HOUGH_GRADIENT: 'HOUGH_GRADIENT',
            cv.HOUGH_GRADIENT_ALT: 'HOUGH_GRADIENT_ALT'
        }, checked_index=cv.HOUGH_GRADIENT_ALT)

        self.__main_layout.addWidget(self.__method_widget)

        params_layout = QFormLayout()
        self.__dp_line_edit = QLineEdit()
        params_layout.addRow(QLabel('dp'), self.__dp_line_edit)
        self.__min_dist_line_edit = QLineEdit()
        params_layout.addRow(QLabel('minDist'), self.__min_dist_line_edit)
        self.__param1_line_edit = QLineEdit()
        params_layout.addRow(QLabel('param1'), self.__param1_line_edit)
        self.__param2_line_edit = QLineEdit()
        params_layout.addRow(QLabel('param2'), self.__param2_line_edit)
        self.__min_radius_line_edit = QLineEdit()
        params_layout.addRow(QLabel('minRadius'), self.__min_radius_line_edit)
        self.__max_radius_line_edit = QLineEdit()
        params_layout.addRow(QLabel('maxRadius'), self.__max_radius_line_edit)

        self.__main_layout.addLayout(params_layout)

        self.__detect_button = QPushButton('Detect')
        self.__detect_button.clicked.connect(self.__on_detect_button_clicked)
        self.__main_layout.addWidget(self.__detect_button)

        return self.__main_widget

    @Slot()
    def __on_detect_button_clicked(self):
        wrong_fields = []
        dp, success = self.__to_float(self.__dp_line_edit.text())
        if not success:
            wrong_fields.append('dp')
        min_dist, success = self.__to_float(self.__min_dist_line_edit.text())
        if not success:
            wrong_fields.append('minDist')
        param1, success = self.__to_float(self.__param1_line_edit.text())
        if not success:
            wrong_fields.append('param1')
        param2, success = self.__to_float(self.__param2_line_edit.text())
        if not success:
            wrong_fields.append('param2')
        min_radius, success = self.__to_int(self.__min_radius_line_edit.text())
        if not success:
            wrong_fields.append('min_radius')
        max_radius, success = self.__to_int(self.__max_radius_line_edit.text())
        if not success:
            wrong_fields.append('max_radius')

        if len(wrong_fields) > 0:
            QMessageBox.critical(self, 'Error',
                                 'Following fields has empty or wrong values: ' + ', '.join(
                                     wrong_fields),
                                 QMessageBox.Ok, QMessageBox.NoButton)
            return
        action = ActionFactory.create_hough_circle_action(
            method=self.__method_widget.get_checked(),
            dp=dp,
            min_dist=min_dist,
            param1=param1,
            param2=param2,
            min_radius=min_radius,
            max_radius=max_radius)
        self.display_action_result.emit(action)

    @staticmethod
    def __to_float(value: str) -> Tuple[float, bool]:
        try:
            return float(value), True
        except ValueError:
            return 0, False

    @staticmethod
    def __to_int(value: str) -> Tuple[int, bool]:
        try:
            return int(value), True
        except ValueError:
            return 0, False
