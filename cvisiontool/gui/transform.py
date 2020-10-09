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
from typing import Optional

import cv2.cv2 as cv
import numpy as np
from PySide2.QtCore import Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QWidget, QGridLayout, QCheckBox

from cvisiontool.gui.common import ChooseOneOfWidget, SliderWidget, MinimalColorPickerWidget, \
    SupportedColorSpaces, AbstractMatActionDialog


class ErosionAndDilationDialog(AbstractMatActionDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Erosion and Dilation parameters')

    def _create_main_widget(self) -> QWidget:
        self.__main_widget = QWidget()
        self.__main_widget_layout = QGridLayout(self.__main_widget)
        self.__morph_op = ChooseOneOfWidget('Morphological operation',
                                            {
                                                0: 'Erode',
                                                1: 'Dilate'
                                            })
        self.__morph_op.toggled.connect(self.__apply_morph)
        self.__main_widget_layout.addWidget(self.__morph_op, 0, 0)
        self.__morph_type = ChooseOneOfWidget('Morphological operation type',
                                              {
                                                  cv.MORPH_RECT: 'Rect',
                                                  cv.MORPH_CROSS: 'Cross',
                                                  cv.MORPH_ELLIPSE: 'Ellipse'
                                              })
        self.__morph_type.toggled.connect(self.__apply_morph)
        self.__main_widget_layout.addWidget(self.__morph_type, 1, 0)
        self.__kernel_size_slider = SliderWidget('Anchor (Kernel size = 2*Anchor+1)', 0, 40)
        self.__kernel_size_slider.value_changed.connect(self.__apply_kernel_size)
        self.__main_widget_layout.addWidget(self.__kernel_size_slider, 0, 1)

        return self.__main_widget

    @Slot(int, bool)
    def __apply_morph(self, index, is_checked):
        if is_checked:
            self.__transform_and_emit_as_rgb()

    @Slot(int)
    def __apply_kernel_size(self, new_value: int):
        self.__transform_and_emit_as_rgb()

    def __apply_erosion(self, img: np.ndarray, erosion_size: int, erosion_type: int) -> np.ndarray:
        ksize = 2 * erosion_size + 1
        element = cv.getStructuringElement(erosion_type,
                                           (ksize, ksize),
                                           (erosion_size, erosion_size))
        return cv.erode(img, element)

    def __apply_dilation(self, img: np.ndarray, erosion_size: int, erosion_type: int) -> np.ndarray:
        ksize = 2 * erosion_size + 1
        element = cv.getStructuringElement(erosion_type,
                                           (ksize, ksize),
                                           (erosion_size, erosion_size))
        return cv.dilate(img, element)

    def __transform(self) -> Optional[np.ndarray]:
        morph_op = self.__morph_op.get_checked()
        morph_type = self.__morph_type.get_checked()
        kernel_size = self.__kernel_size_slider.get_current_value()
        if morph_type == -1 or morph_op == -1:
            return self._original_mat_bgr

        if morph_op == 0:
            return self.__apply_erosion(self._original_mat_bgr, kernel_size, morph_type)
        elif morph_op == 1:
            return self.__apply_dilation(self._original_mat_bgr, kernel_size, morph_type)

    def __transform_and_emit_as_rgb(self):
        img_bgr = self.__transform()
        if img_bgr is not None:
            self._transformed_mat_bgr = img_bgr
            self.show_image.emit(img_bgr)


class InRangeDialog(AbstractMatActionDialog):

    def _create_main_widget(self) -> QWidget:
        self.__current_left_boundary: Optional[QColor] = None
        self.__current_right_boundary: Optional[QColor] = None
        self.__supported_color_spaces = {
            0: 'HSV'
        }
        self.__chosen_color_space_index: int = 0

        self.__main_widget = QWidget()
        self.__main_widget_layout = QGridLayout(self.__main_widget)

        self.__color_space_widget = ChooseOneOfWidget('Color-space', self.__supported_color_spaces,
                                                      checked_index=self.__chosen_color_space_index)
        self.__main_widget_layout.addWidget(self.__color_space_widget, 0, 0)
        self.__show_im_cb = QCheckBox('Show result immediately', self)
        self.__main_widget_layout.addWidget(self.__show_im_cb, 0, 1)
        self.__left_boundary_picker = MinimalColorPickerWidget(SupportedColorSpaces.HSV,
                                                               'Select left boundary')
        self.__left_boundary_picker.color_changed.connect(self.__set_left_boundary)
        self.__right_boundary_picker = MinimalColorPickerWidget(SupportedColorSpaces.HSV,
                                                                'Select right boundary')
        self.__right_boundary_picker.color_changed.connect(self.__set_right_boundary)
        self.__main_widget_layout.addWidget(self.__left_boundary_picker, 1, 0)
        self.__main_widget_layout.addWidget(self.__right_boundary_picker, 1, 1)

        return self.__main_widget

    def __apply_in_range(self):
        if self._original_mat_bgr is None or self.__current_right_boundary is None \
                or self.__current_left_boundary is None:
            return None

        mat = None
        lower_boundary = []
        upper_boundary = []
        if self.__color_space_widget.get_checked() == 0:
            mat = cv.cvtColor(self._original_mat_bgr, cv.COLOR_BGR2HSV)
            h, s, v = self.__current_left_boundary.hue(), \
                      self.__current_left_boundary.saturation(), \
                      self.__current_left_boundary.value()
            lower_boundary = np.array([int(h / 2), s, v])
            h, s, v = self.__current_right_boundary.hue(), \
                      self.__current_right_boundary.saturation(), \
                      self.__current_right_boundary.value()
            upper_boundary = np.array([int(h / 2), s, v])

        self._transformed_mat_bgr = cv.inRange(mat, lower_boundary, upper_boundary)
        self.show_image.emit(self._transformed_mat_bgr)

    @Slot(QColor)
    def __set_left_boundary(self, color: QColor):
        self.__current_left_boundary = color
        if self.__show_im_cb.isChecked():
            self.__apply_in_range()

    @Slot(QColor)
    def __set_right_boundary(self, color: QColor):
        self.__current_right_boundary = color
        if self.__show_im_cb.isChecked():
            self.__apply_in_range()

    @Slot(int, bool)
    def __select_bound_toggled(self, index: int, checked: bool):
        if checked:
            self.__chosen_color_space_index = index
