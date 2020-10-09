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

import sys
from PySide2.QtWidgets import QApplication

from cvisiontool.gui.mainwindow import MainWindow

app = QApplication(sys.argv)

main_window = MainWindow()
main_window.resize(800, 600)
main_window.show()

sys.exit(app.exec_())