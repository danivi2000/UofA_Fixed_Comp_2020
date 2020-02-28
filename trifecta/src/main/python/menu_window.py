from PyQt5 import QtCore, QtGui, QtWidgets

from ui_sigvisualizer import Ui_sigvisualizer


class MenuWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        MainWindow.setStyleSheet(
            "QMainWindow {"
            "    color: #282C34;"
            "    background-color: #282C34;"
            "}")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet(
            "QWidget {"
            "    color: #282C34;"
            "}")
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        spacerItem = QtWidgets.QSpacerItem(20, 40,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.verticalLayout.addItem(spacerItem)

        self.app_name = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(36)
        self.app_name.setFont(font)
        self.app_name.setStyleSheet(
            "QLabel {"
            "    color: #56B5C2;"
            "    background-color: #282C34;"
            "}")

        self.app_name.setAlignment(QtCore.Qt.AlignCenter)
        self.app_name.setObjectName("app_name")
        self.verticalLayout.addWidget(self.app_name)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.eeg_box = QtWidgets.QCheckBox(self.centralwidget)
        self.eeg_box.setStyleSheet(
        "QCheckBox {"
        "    color: #C678DD;"
        "    background-color: #282C34;"
        "    margin-left: auto;"
        "    margin-right: auto;"
        "}"
        "")
        self.eeg_box.setObjectName("eeg_box")
        self.horizontalLayout.addWidget(self.eeg_box)

        self.environment_box = QtWidgets.QCheckBox(self.centralwidget)
        self.environment_box.setStyleSheet(
            "QCheckBox {"
            "    color: #C678DD;"
            "    background-color: #282C34;"
            "    margin-left: auto;"
            "    margin-right: auto;"
            "}"
            "")
        self.environment_box.setObjectName("environment_box")
        self.horizontalLayout.addWidget(self.environment_box)
        self.verticalLayout.addLayout(self.horizontalLayout)

        spacerItem2 = QtWidgets.QSpacerItem(20, 150,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.visualize_scr = QtWidgets.QPushButton(self.centralwidget)
        self.visualize_scr.setStyleSheet(
            "QPushButton {"
            "    color: white;"
            "    background-color: #56B6C2;"
            "    border: 1px #282C34;;"
            "    padding-top: 20px;"
            "    padding-bottom:  20px;"
            "}"
            ""
            "QPushButton:pressed {"
            "    color: white;"
            "    background-color: #61AFEF;"
            "    border: 1px #282C34;;"
            "    padding-top: 20px;"
            "    padding-bottom:  20px;"
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
        eeg_window = QtWidgets.QMainWindow()
        ui = Ui_sigvisualizer()
        ui.setupUi(eeg_window)
        eeg_window.show()

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
