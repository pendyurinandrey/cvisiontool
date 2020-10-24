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
from PySide2.QtCore import Slot, Signal
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog, QLabel, \
    QDialog

from cvisiontool.core.actions import Action, ActionFactory
from cvisiontool.core.actionproc import ActionProcessor
from cvisiontool.core.historymanager import HistoryManager, HistoryEntry
from cvisiontool.gui.common import MatView, MatViewPosInfo
from cvisiontool.gui.detect import HoughCircleDialog
from cvisiontool.gui.history import HistoryDialog
from cvisiontool.gui.transform import ErosionAndDilationDialog, InRangeDialog


class MainWindow(QMainWindow):
    image_loaded = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.__action_processor = ActionProcessor()
        self.__lasted_chosen_dir = None
        self.__history_manager = HistoryManager()
        self.__current_mat_bgr: np.ndarray = None
        self.__history_dialog: QDialog = None
        self.__current_dialog: QDialog = None
        self.__mat_view: MatView = MatView()
        self.__mat_view.setFixedHeight(self.height() - 30)
        self.__mat_view.setFixedWidth(self.width() - 30)
        self.__mat_view.position_info.connect(self.__render_view_position_info)
        self.__central_widget = QWidget()
        self.__status_label = QLabel()
        self.__status_label.setMargin(2)
        self.statusBar().addPermanentWidget(self.__status_label, 1)

        self.__create_main_menu()

        layout = QVBoxLayout()
        layout.addWidget(self.__mat_view)
        self.__central_widget.setLayout(layout)

        self.setCentralWidget(self.__central_widget)

    def __create_main_menu(self) -> None:
        menu = self.menuBar()
        menu.setNativeMenuBar(False)

        file_menu = menu.addMenu('File')
        load_file_action = QAction(text='Load file', parent=menu)
        load_file_action.triggered.connect(self.__load_file)
        file_menu.addAction(load_file_action)

        view_menu = menu.addMenu('View')
        history_action = QAction(text='History', parent=menu)
        history_action.triggered.connect(self.__show_history_dialog)
        view_menu.addAction(history_action)

        detect_menu = menu.addMenu('Detect')
        hough_circle_action = QAction(text='Hough Circle', parent=menu)
        hough_circle_action.triggered.connect(self.__show_hough_circle_dialog)
        detect_menu.addAction(hough_circle_action)

        self.__transform_menu = menu.addMenu('Transform')
        erosion_and_dilation_action = QAction(text='Erosion and Dilation', parent=menu)
        erosion_and_dilation_action.triggered.connect(self.__open_er_di_dialog)
        self.__transform_menu.addAction(erosion_and_dilation_action)

        thresholding_menu = self.__transform_menu.addMenu('Thresholding')
        in_range_action_action = QAction('inRange', parent=thresholding_menu)
        in_range_action_action.triggered.connect(self.__show_in_range_dialog)
        thresholding_menu.addAction(in_range_action_action)
        self.__transform_menu.setEnabled(False)

    def __activate_menu_on_image_load(self):
        self.__transform_menu.setEnabled(True)

    @Slot()
    def __load_file(self):
        selected_file, _ = QFileDialog.getOpenFileName(self, 'Choose image',
                                                       self.__lasted_chosen_dir)
        if selected_file is not None:
            path = Path(selected_file)
            self.__lasted_chosen_dir = str(path.parent)
            self.__current_mat_bgr = cv.imread(selected_file)
            self.__mat_view.render_bgr_mat(self.__current_mat_bgr)
            self.image_loaded.emit(self.__current_mat_bgr)
            self.__history_manager.add_entry(HistoryEntry(
                ActionFactory.create_image_loaded_action(selected_file),
                self.__current_mat_bgr
            ))
            self.__activate_menu_on_image_load()

    @Slot()
    def __show_history_dialog(self):
        if self.__history_dialog is not None:
            if not self.__history_dialog.isVisible():
                self.__history_dialog.show()
        else:
            self.__history_dialog = HistoryDialog(self.__history_manager, self)
            self.__history_dialog.apply_history_entry.connect(self.__on_apply_history_entry)
            self.__history_dialog.show()

    @Slot()
    def __open_er_di_dialog(self):
        # TODO: It's necessary to close a dialog gracefully
        if self.__current_dialog is not None:
            self.__current_dialog.close()

        self.__current_dialog = ErosionAndDilationDialog(self)
        self.__connect_current_dialog()
        self.__current_dialog.show()

    @Slot()
    def __show_in_range_dialog(self):
        # TODO: It's necessary to close a dialog gracefully
        if self.__current_dialog is not None:
            self.__current_dialog.close()

        self.__current_dialog = InRangeDialog()
        self.__connect_current_dialog()
        self.__current_dialog.show()

    @Slot()
    def __show_hough_circle_dialog(self):
        if self.__current_dialog is not None:
            self.__current_dialog.close()

        self.__current_dialog = HoughCircleDialog()
        self.__connect_current_dialog()
        self.__current_dialog.show()

    @Slot(MatViewPosInfo)
    def __render_view_position_info(self, info: MatViewPosInfo):
        original = np.uint8([[[info.red, info.green, info.blue]]])
        # OpenCV HSV ranges are [0,179] for Hue, [0,255] for Saturation and Value
        # Multiply by 2, 1/2.55, 1/2.55 to convert to conventional HSV
        hsv = cv.cvtColor(original, cv.COLOR_RGB2HSV)
        h, s, v = hsv[0][0]
        self.__status_label.setText(
            f'x = {info.x}, y = {info.y}, RGB: [r = {info.red}, g = {info.green}, b = {info.blue}], '
            f'HSV (Open CV format): [h = {h}, s = {s}, v={v}]')

    @Slot(Action)
    def display_action_result(self, action: Action):
        image_bgr = self.__action_processor.process(action, self.__current_mat_bgr)
        self.__mat_view.render_bgr_mat(image_bgr)

    @Slot(Action)
    def apply_action_result(self, action: Action):
        self.__current_mat_bgr = self.__action_processor.process(action, self.__current_mat_bgr)
        self.__history_manager.add_entry(HistoryEntry(action, self.__current_mat_bgr))
        self.__mat_view.render_bgr_mat(self.__current_mat_bgr)

    @Slot()
    def discard_non_applied_changes(self):
        self.__mat_view.render_bgr_mat(self.__current_mat_bgr)

    def __connect_current_dialog(self):
        self.__current_dialog.display_action_result.connect(self.display_action_result)
        self.__current_dialog.apply_action_result.connect(self.apply_action_result)
        self.__current_dialog.discard_action_result.connect(self.discard_non_applied_changes)

    @Slot(HistoryEntry)
    def __on_apply_history_entry(self, entry: HistoryEntry):
        if entry is not None and entry.mat_bgr is not None:
            self.__current_mat_bgr = entry.mat_bgr
            self.__mat_view.render_bgr_mat(self.__current_mat_bgr)