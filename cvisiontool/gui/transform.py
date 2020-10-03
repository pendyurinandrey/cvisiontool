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
from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QWidget, QGridLayout, QDialog, QVBoxLayout

from cvisiontool.gui.common import ChooseOneOfWidget, SliderWidget


class ErosionAndDilationDialog(QDialog):
    image_ready = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__layout = QVBoxLayout()
        self.__widget = ErodeAndDilateWidget(self)
        self.__layout.addWidget(self.__widget)
        self.setLayout(self.__layout)
        self.setWindowTitle('Erosion and Dilation parameters')
        self.__widget.image_ready.connect(self.__image_ready)

    @Slot(np.ndarray)
    def __image_ready(self, mat: np.ndarray):
        self.image_ready.emit(mat)

    @Slot(np.ndarray)
    def set_image(self, mat: np.ndarray):
        self.__widget.set_image(mat)

class ErodeAndDilateWidget(QWidget):
    image_ready = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__current_image: np.ndarray = None
        self.__create_controls()

    def __create_controls(self):
        controls_layout = QGridLayout()
        self.__morph_op = ChooseOneOfWidget('Morph operation',
                                            {
                                                0: 'Erode',
                                                1: 'Dilate'
                                            },
                                            self.__apply_morph)
        controls_layout.addWidget(self.__morph_op, 0, 0)
        self.__morph_type = ChooseOneOfWidget('Morph operation type',
                                              {
                                                  cv.MORPH_RECT: 'Rect',
                                                  cv.MORPH_CROSS: 'Cross',
                                                  cv.MORPH_ELLIPSE: 'Ellipse'
                                              },
                                              self.__apply_morph
                                              )
        controls_layout.addWidget(self.__morph_type, 1, 0)
        self.__kernel_size_slider = SliderWidget('Kernel size', 0, 40)
        self.__kernel_size_slider.value_changed.connect(self.__apply_kernel_size)
        controls_layout.addWidget(self.__kernel_size_slider, 0, 1)
        self.setLayout(controls_layout)

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
            return self.__current_image

        if morph_op == 0:
            return self.__apply_erosion(self.__current_image, kernel_size, morph_type)
        elif morph_op == 1:
            return self.__apply_dilation(self.__current_image, kernel_size, morph_type)

    def __transform_and_emit_as_rgb(self):
        img_bgr = self.__transform()
        if img_bgr is not None:
            self.image_ready.emit(img_bgr)

    def set_image(self, img: np.ndarray):
        self.__current_image = img
        self.__transform_and_emit_as_rgb()
