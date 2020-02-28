# ===========================
#   Name: Edward Guo
#   Software Team
#   NeurAlbertaTech 2020
# ===========================

from PyQt5 import QtWidgets
import sys

from menu_window import MenuWindow
from ui_sigvisualizer import Ui_sigvisualizer


class Controller:
    def Show_FirstWindow(self):
        self.FirstWindow = QtWidgets.QMainWindow()
        self.ui = MenuWindow()
        self.ui.setupUi(self.FirstWindow)
        self.ui.visualize_scr.clicked.connect(self.Show_SecondWindow)

        self.FirstWindow.show()

    def Show_SecondWindow(self):
        self.SecondWindow = QtWidgets.QMainWindow()
        self.ui = Ui_sigvisualizer()
        self.ui.setupUi(self.SecondWindow)

        self.SecondWindow.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.Show_FirstWindow()
    sys.exit(app.exec_())
