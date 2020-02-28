# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_sigvisualizer.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from paintwidget import PaintWidget


class Ui_sigvisualizer(object):
    stream_expanded = QtCore.pyqtSignal(str)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.toggleButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggleButton.sizePolicy().hasHeightForWidth())
        self.toggleButton.setSizePolicy(sizePolicy)
        self.toggleButton.setMaximumSize(QtCore.QSize(20, 16777215))
        self.toggleButton.setText("")
        self.toggleButton.setObjectName("toggleButton")
        self.gridLayout.addWidget(self.toggleButton, 0, 0, 2, 1)

        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMaximumSize(QtCore.QSize(180, 16777215))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.gridLayout.addWidget(self.treeWidget, 0, 1, 1, 1)

        self.widget = PaintWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 0, 2, 2, 1)
        self.updateButton = QtWidgets.QPushButton(self.centralwidget)
        self.updateButton.setObjectName("updateButton")
        self.gridLayout.addWidget(self.updateButton, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1123, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.toggleButton.setIcon(QtGui.QIcon("icons/chevron_left.svg"))
        self.toggleButton.setIconSize(QtCore.QSize(30, 30))
        self.toggleButton.clicked.connect(self.toggle_panel)
        self.updateButton.clicked.connect(
            self.widget.dataTr.update_streams)
        self.widget.dataTr.updateStreamNames.connect(
            self.update_metadata_widget)
        self.panelHidden = False

        self.treeWidget.setHeaderLabel('Streams')
        self.treeWidget.itemExpanded.connect(self.tree_item_expanded)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def tree_item_expanded(self, widget_item):
        name = widget_item.text(0)
        for it_ix in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(it_ix)
            if item.text(0) != name:
                item.setExpanded(False)

    def update_metadata_widget(self, metadata, default_idx):
        for s_ix, s_meta in enumerate(metadata):
            item = QtWidgets.QTreeWidgetItem(self.treeWidget)
            item.setText(0, s_meta["name"])

            for m in range(s_meta["ch_count"]):
                channel_item = QtWidgets.QTreeWidgetItem(item)
                channel_item.setText(0, 'Channel {}'.format(m+1))
                channel_item.setCheckState(0, QtCore.Qt.Checked)

            item.setExpanded(True if s_ix == default_idx else False)
            self.treeWidget.addTopLevelItem(item)

        self.treeWidget.setAnimated(True)
        self.statusbar.showMessage(
            "Sampling rate: {}Hz".format(metadata[default_idx]["srate"]))

    def toggle_panel(self):
        if self.panelHidden:
            self.panelHidden = False
            self.treeWidget.show()
            self.updateButton.show()
            self.toggleButton.setIcon(QtGui.QIcon("icons/chevron_left.svg"))
            self.toggleButton.setIconSize(QtCore.QSize(30, 30))
        else:
            self.panelHidden = True
            self.treeWidget.hide()
            self.updateButton.hide()
            self.toggleButton.setIcon(QtGui.QIcon("icons/chevron_right.svg"))
            self.toggleButton.setIconSize(QtCore.QSize(30, 30))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Trifecta"))
        self.updateButton.setText(_translate("MainWindow", "Update Streams"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_sigvisualizer()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
