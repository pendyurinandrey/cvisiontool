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
from typing import Optional, Dict, Callable

import cv2.cv2 as cv
import numpy as np
from PySide2.QtCore import Signal, Qt, Slot
from PySide2.QtGui import QMouseEvent, QImage, QPixmap, QColor
from PySide2.QtWidgets import QLabel, QWidget, QVBoxLayout, QGroupBox, QSlider, QButtonGroup, \
    QRadioButton


@dataclass(frozen=True)
class MatViewPosInfo:
    x: int
    y: int
    red: int
    green: int
    blue: int


class MatView(QLabel):
    position_info = Signal(MatViewPosInfo)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__current_rgb_mat: Optional[np.ndarray] = None
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.__current_rgb_mat is not None:
            x = event.x()
            y = event.y()
            img = self.pixmap().toImage()
            if x < img.width() and y < img.height():
                color: QColor = img.pixelColor(x, y)
                self.position_info.emit(MatViewPosInfo(x, y, color.red(), color.green(), color.blue()))


    def render_bgr_mat(self, mat: np.ndarray):
        mat_rgb = cv.cvtColor(mat, cv.COLOR_BGR2RGB)
        height, width, _ = mat_rgb.shape
        bytes_per_line, *_ = mat_rgb.strides
        img = QImage(mat_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.setPixmap(pixmap)
        self.setGeometry(0, 0, pixmap.width(), pixmap.height())
        self.__current_rgb_mat = mat_rgb


class SliderWidget(QWidget):
    value_changed = Signal(int)

    def __init__(self, title: str, min: int, max: int, parent=None):
        super().__init__(parent)
        self.__main_layout = QVBoxLayout()
        self.__group_box = QGroupBox(title)
        group_box_layout = QVBoxLayout()

        self.__min_label = QLabel(f'Min value: {min}')
        self.__max_label = QLabel(f'Max value: {max}')
        self.__current_value_label = QLabel(f'Current value: {min}')
        self.__slider = QSlider(Qt.Horizontal)
        self.__slider.valueChanged.connect(self.__on_slider_value_changed)
        self.__slider.setMinimum(min)
        self.__slider.setMaximum(max)

        group_box_layout.addWidget(self.__slider)
        group_box_layout.addWidget(self.__min_label)
        group_box_layout.addWidget(self.__max_label)
        group_box_layout.addWidget(self.__current_value_label)

        self.__group_box.setLayout(group_box_layout)
        self.__main_layout.addWidget(self.__group_box)
        self.setLayout(self.__main_layout)

    @Slot(int)
    def __on_slider_value_changed(self, new_value: int):
        self.__current_value_label.setText(f'Current value: {new_value}')
        self.value_changed.emit(new_value)

    def get_current_value(self):
        return self.__slider.value()


class ChooseOneOfWidget(QWidget):
    def __init__(self, title: str, index_to_label: Dict[int, str],
                 on_checked_slot: Callable[[int, bool], None], parent=None):
        super().__init__(parent)
        self.__mapping = {}
        self.__main_layout = QVBoxLayout()
        self.__group_box = QGroupBox(title)
        self.__button_group = QButtonGroup()
        self.__layout = QVBoxLayout()

        for index, label in index_to_label.items():
            button = QRadioButton(label)
            self.__button_group.addButton(button, index)
            self.__layout.addWidget(button)

        self.__group_box.setLayout(self.__layout)
        self.__button_group.idToggled.connect(on_checked_slot)
        self.__main_layout.addWidget(self.__group_box)
        self.setLayout(self.__main_layout)

    def get_checked(self) -> int:
        return self.__button_group.checkedId()