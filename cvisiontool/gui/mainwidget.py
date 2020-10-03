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
import cv2.cv2 as cv
from pathlib import Path
import numpy as np
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog, QLabel

from cvisiontool.gui.common import MatView, MatViewPosInfo
from cvisiontool.gui.transform import ErodeAndDilateWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__lasted_chosen_dir = None
        self.__original_mat_bgr: np.ndarray = None
        self.__mat_view: MatView = MatView()
        self.__mat_view.position_info.connect(self.__render_view_position_info)
        self.__central_widget = QWidget()
        self.__controls_widget = ErodeAndDilateWidget()
        self.__controls_widget.image_ready.connect(self.render_image)
        self.__status_label = QLabel()
        self.__status_label.setMargin(2)
        self.statusBar().addPermanentWidget(self.__status_label, 1)

        self.__create_main_menu()

        layout = QVBoxLayout()
        layout.addWidget(self.__mat_view)
        layout.addWidget(self.__controls_widget)
        self.__central_widget.setLayout(layout)

        self.setCentralWidget(self.__central_widget)

    def __create_main_menu(self) -> None:
        menu = self.menuBar()
        menu.setNativeMenuBar(False)

        file_menu = menu.addMenu('File')
        load_file_action = QAction(text='Load file', parent=self)
        load_file_action.triggered.connect(self.__load_file)
        file_menu.addAction(load_file_action)

    def __load_file(self):
        selected_file, _ = QFileDialog.getOpenFileName(self, 'Choose image',
                                                       self.__lasted_chosen_dir)
        if selected_file is not None:
            path = Path(selected_file)
            self.__lasted_chosen_dir = str(Path(selected_file).parent)
            self.__original_mat_bgr = cv.imread(selected_file)
            self.__controls_widget.set_image(self.__original_mat_bgr)

    @Slot(MatViewPosInfo)
    def __render_view_position_info(self, info: MatViewPosInfo):
        self.__status_label.setText(
            f'x = {info.x}, y = {info.y}, r = {info.red}, g = {info.green}, b = {info.blue}')

    @Slot(np.ndarray)
    def render_image(self, image_bgr: np.ndarray):
        self.__mat_view.render_bgr_mat(image_bgr)
