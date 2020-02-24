# ===========================
#   Name: Edward Guo
#   Software Team
#   NeurAlbertaTech 2020
# ===========================

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from ui_sigvisualizer import Visualizer


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("QMainWindow {\n"
            "    color: #282C34;\n"
            "    background-color: #282C34;\n"
            "}")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("QWidget {\n"
            "    color: #282C34;\n"
            "}")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.app_name = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(36)
        self.app_name.setFont(font)
        self.app_name.setStyleSheet("QLabel {\n"
            "    color: #56B5C2;\n"
            "    background-color: #282C34;\n"
            "}")

        self.app_name.setAlignment(QtCore.Qt.AlignCenter)
        self.app_name.setObjectName("app_name")
        self.verticalLayout.addWidget(self.app_name)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.eeg_box = QtWidgets.QCheckBox(self.centralwidget)
        self.eeg_box.setStyleSheet("QCheckBox {\n"
        "    color: #C678DD;\n"
        "    background-color: #282C34;\n"
        "    margin-left: auto;\n"
        "    margin-right: auto;\n"
        "}\n"
        "")
        self.eeg_box.setObjectName("eeg_box")
        self.horizontalLayout.addWidget(self.eeg_box)

        self.environment_box = QtWidgets.QCheckBox(self.centralwidget)
        self.environment_box.setStyleSheet("QCheckBox {\n"
            "    color: #C678DD;\n"
            "    background-color: #282C34;\n"
            "    margin-left: auto;\n"
            "    margin-right: auto;\n"
            "}\n"
            "")
        self.environment_box.setObjectName("environment_box")
        self.horizontalLayout.addWidget(self.environment_box)
        self.verticalLayout.addLayout(self.horizontalLayout)

        spacerItem2 = QtWidgets.QSpacerItem(20, 150,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.visualize_scr = QtWidgets.QPushButton(self.centralwidget)
        self.visualize_scr.setStyleSheet("QPushButton {\n"
            "    color: white;\n"
            "    background-color: #56B6C2;\n"
            "    border: 1px #282C34;;\n"
            "    padding-top: 20px;\n"
            "    padding-bottom:  20px;\n"
            "}\n"
            "\n"
            "QPushButton:pressed {\n"
            "    color: white;\n"
            "    background-color: #61AFEF;\n"
            "    border: 1px #282C34;;\n"
            "    padding-top: 20px;\n"
            "    padding-bottom:  20px;\n"
            "}")
        self.visualize_scr.setObjectName("visualize_scr")
        self.verticalLayout.addWidget(self.visualize_scr)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.visualize_scr.clicked.connect(self.goto_visualize_scr)

    def goto_visualize_scr(self):
        MainWindow.hide()
        self.Form = QtWidgets.QWidget()
        self.ui = Visualizer()
        self.ui.setupUi(self.Form)
        self.Form.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Trifecta"))
        self.app_name.setText(_translate("MainWindow",
            "Welcome to Trifecta"))
        self.eeg_box.setText(_translate("MainWindow", "EEG"))
        self.environment_box.setText(_translate("MainWindow",
            "Environment Tracking"))
        self.visualize_scr.setText(_translate("MainWindow",
            "Start Visualization"))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
