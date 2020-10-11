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
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

import cv2.cv2 as cv
import numpy as np
from PySide2.QtCore import Signal, Qt, Slot
from PySide2.QtGui import QMouseEvent, QImage, QPixmap, QColor, QHideEvent
from PySide2.QtWidgets import QLabel, QWidget, QVBoxLayout, QGroupBox, QSlider, QButtonGroup, \
    QRadioButton, QSizePolicy, QColorDialog, QHBoxLayout, QSpinBox, QFormLayout, QPushButton, \
    QDialog

from cvisiontool.core.actions import Action


@dataclass(frozen=True)
class MatViewPosInfo:
    x: int
    y: int
    red: int
    green: int
    blue: int


class SupportedColorSpaces(Enum):
    HSV = 0


class MatView(QLabel):
    position_info = Signal(MatViewPosInfo)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__current_rgb_mat: Optional[np.ndarray] = None
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.__current_rgb_mat is not None:
            x = event.x()
            y = event.y()
            h, w, _ = self.__current_rgb_mat.shape
            if x < w and y < h:
                self.position_info.emit(MatViewPosInfo(x, y,
                                                       red=self.__current_rgb_mat[y][x][0],
                                                       green=self.__current_rgb_mat[y][x][1],
                                                       blue=self.__current_rgb_mat[y][x][2]))

    def render_bgr_mat(self, mat: np.ndarray):
        mat_rgb = cv.cvtColor(mat, cv.COLOR_BGR2RGB)
        height, width, _ = mat_rgb.shape
        bytes_per_line, *_ = mat_rgb.strides
        img = QImage(mat_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        if pixmap.width() > self.width() or pixmap.height() > self.height():
            pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio,
                                   Qt.FastTransformation)
        self.setPixmap(pixmap)
        self.__current_rgb_mat = mat_rgb


class SliderWidget(QWidget):
    value_changed = Signal(int)

    def __init__(self, title: str, min_value: int, max_value: int, parent=None):
        super().__init__(parent)
        self.__main_layout = QVBoxLayout()
        self.__group_box = QGroupBox(title)
        group_box_layout = QVBoxLayout()

        self.__min_label = QLabel(f'Min value: {min_value}')
        self.__max_label = QLabel(f'Max value: {max_value}')
        self.__current_value_label = QLabel(f'Current value: {min_value}')
        self.__slider = QSlider(Qt.Horizontal)
        self.__slider.valueChanged.connect(self.__on_slider_value_changed)
        self.__slider.setMinimum(min_value)
        self.__slider.setMaximum(max_value)

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
    toggled = Signal(int, bool)

    def __init__(self, title: str, index_to_label: Dict[int, str], is_vertical=True,
                 checked_index: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.__mapping = {}
        self.__main_layout = QVBoxLayout()
        self.__group_box = QGroupBox(title)
        self.__button_group = QButtonGroup()
        if is_vertical:
            self.__group_box_layout = QVBoxLayout()
        else:
            self.__group_box_layout = QHBoxLayout()

        for index, label in index_to_label.items():
            button = QRadioButton(label)
            self.__button_group.addButton(button, index)
            self.__group_box_layout.addWidget(button)
            if checked_index == index:
                button.setChecked(True)

        self.__group_box.setLayout(self.__group_box_layout)
        self.__button_group.idToggled.connect(self.__on_toggled)
        self.__main_layout.addWidget(self.__group_box)
        self.setLayout(self.__main_layout)

    @Slot(int, bool)
    def __on_toggled(self, index, is_checked):
        self.toggled.emit(index, is_checked)

    def get_checked(self) -> int:
        return self.__button_group.checkedId()


class FullColorPickerWidget(QWidget):
    color_changed = Signal(QColor)

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.__color_picker = QColorDialog(self)
        self.__color_picker.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        self.__color_picker.setOption(QColorDialog.ColorDialogOption.NoButtons)
        self.__color_picker.setWindowFlags(Qt.Widget)

        self.__group_box = QGroupBox(title)
        self.__group_box_layout = QVBoxLayout()
        self.__group_box_layout.addWidget(self.__color_picker)
        self.__group_box.setLayout(self.__group_box_layout)
        self.__group_box_layout.setStretch(1, 1)

        self.__main_layout = QVBoxLayout(self)
        self.__main_layout.addWidget(self.__group_box)

    @Slot(QColor)
    def __on_color_changed(self, color: QColor):
        self.color_changed.emit(color)

    def get_current_color(self) -> QColor:
        return self.__color_picker.currentColor()


class MinimalColorPickerWidget(QWidget):
    color_changed = Signal(QColor)

    def __init__(self, color_space: SupportedColorSpaces, title: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.__color_space = color_space
        color_1_label = QLabel(self)
        color_2_label = QLabel(self)
        color_3_label = QLabel(self)

        self.__color_1_sb = QSpinBox(self)
        self.__color_1_sb.valueChanged.connect(self.__on_value_changed)
        self.__color_2_sb = QSpinBox(self)
        self.__color_2_sb.valueChanged.connect(self.__on_value_changed)
        self.__color_3_sb = QSpinBox(self)
        self.__color_3_sb.valueChanged.connect(self.__on_value_changed)

        if color_space == SupportedColorSpaces.HSV:
            color_1_label.setText('H (0-359)')
            color_2_label.setText('S (0-255)')
            color_3_label.setText('V (0-255)')
            self.__color_1_sb.setRange(0, 359)
            self.__color_2_sb.setRange(0, 255)
            self.__color_3_sb.setRange(0, 255)

        main_layout = QVBoxLayout(self)
        if title is not None:
            main_layout.addWidget(QLabel(title, self))
        form_layout = QFormLayout()
        form_layout.addRow(color_1_label, self.__color_1_sb)
        form_layout.addRow(color_2_label, self.__color_2_sb)
        form_layout.addRow(color_3_label, self.__color_3_sb)
        main_layout.addLayout(form_layout)

        self.__current_color_label = QLabel()
        self.__current_color_label.setFixedHeight(20)
        main_layout.addWidget(self.__current_color_label)

        self.__open_cp_button = QPushButton('Open color picker', self)
        self.__open_cp_button.clicked.connect(self.__show_color_picker)
        main_layout.addWidget(self.__open_cp_button)

    def __resolve_current_color(self) -> Optional[QColor]:
        if self.__color_space == SupportedColorSpaces.HSV:
            color = QColor()
            color.setHsv(self.__color_1_sb.value(), self.__color_2_sb.value(),
                         self.__color_3_sb.value())
            return color
        return None

    def __set_current_color(self, color: QColor):
        if color is not None:
            if self.__color_space == SupportedColorSpaces.HSV:
                self.__color_1_sb.setValue(color.hue())
                self.__color_2_sb.setValue(color.saturation())
                self.__color_3_sb.setValue(color.value())

    @Slot(int)
    def __on_value_changed(self):
        color = self.__resolve_current_color()
        if color is not None:
            color_hex = color.name()
            self.__current_color_label.setStyleSheet(f'QLabel {{ background-color : {color_hex}; }}')
            self.color_changed.emit(color)

    @Slot()
    def __show_color_picker(self):
        color = QColorDialog.getColor(initial=self.__resolve_current_color(),
                                      parent=self,
                                      title='Select color')
        if color.isValid():
            self.__set_current_color(color)


class AbstractMatActionDialog(QDialog):
    display_action_result = Signal(Action)
    apply_action_result = Signal(Action)
    discard_action_result = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_action: Optional[Action] = None
        self.__is_applied: bool = False

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._create_main_widget())

        controls_layout = QHBoxLayout()
        self._apply_button = QPushButton('Apply')
        self._apply_button.clicked.connect(self._on_apply_clicked)
        controls_layout.addWidget(self._apply_button)

        self._revert_button = QPushButton('Revert')
        self._revert_button.clicked.connect(self._on_revert_clicked)
        controls_layout.addWidget(self._revert_button)

        main_layout.addLayout(controls_layout)

    @abstractmethod
    def _create_main_widget(self) -> QWidget:
        pass

    def hideEvent(self, event: QHideEvent):
        if self._current_action is not None and not self.__is_applied:
            self.discard_action_result.emit()

    def _on_apply_clicked(self):
        if self._current_action is not None:
            self.apply_action_result.emit(self._current_action)
        self.__is_applied = True
        self.close()

    def _on_revert_clicked(self):
        self.discard_action_result.emit()
