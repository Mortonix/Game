import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


r219 = ('3440×1440', '2560×1080')
r169 = ('3840x2160', '2560x1440', '1920x1080', '1600x900', '1280x720')
r1610 = ('3840x2400', '2560x1600', '1920x1200', '1440x900')
r43 = ('1440x1080', '1024x768', '800x600')


class Start(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(20, 160, 461, 181))

        self.tab = QtWidgets.QWidget()

        self.resolutions = QtWidgets.QComboBox(self.tab)
        self.resolutions.setGeometry(QtCore.QRect(30, 60, 171, 21))

        self.difficulties = QtWidgets.QComboBox(self.tab)
        self.difficulties.setGeometry(QtCore.QRect(240, 60, 171, 21))

        self.checkBox = QtWidgets.QCheckBox(self.tab)
        self.checkBox.setGeometry(QtCore.QRect(130, 40, 70, 17))

        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(30, 40, 61, 16))

        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(240, 40, 61, 16))

        self.tabWidget.addTab(self.tab, "")
        self.play_b = QtWidgets.QPushButton(self)
        self.play_b.setGeometry(QtCore.QRect(400, 355, 80, 25))
        self.play_b.setDefault(True)

        self.initUI()
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(self)

    def initUI(self):
        self.setFixedSize(500, 400)
        self.setWindowTitle('Game Configuration')
        self.setWindowIcon(QtGui.QIcon("Data\Settings.png"))

    def retranslateUi(self):
        res = app.desktop().screenGeometry()
        for i in (r43, r169, r219, r1610):
            self_res = f'{res.width()}x{res.height()}'
            if self_res in i:
                self.resolutions.addItems(i)
                self.resolutions.setCurrentText(self_res)
        if self.resolutions.count() == 0:
            self.resolutions.addItems(r43)

        self.difficulties.addItems(("Карапуз", "Легко", "Нормально",
                                    "Сложно", "Ты Бог?"))
        self.difficulties.setCurrentText("Нормально")

        self.checkBox.setText("Windowed")
        self.label.setText("Resolution")
        self.label_3.setText("Difficultly")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "Settings")
        self.play_b.setText("Play")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Start()
    win.show()
    exit(app.exec_())
