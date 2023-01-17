import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from os import system

app = QtWidgets.QApplication(sys.argv)


class Start(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        try:
            self.con = sqlite3.connect('Data\gamebase.sqlite')
        except:
            raise sqlite3.Error("Could not open the database")

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(20, 190, 461, 151))

        self.tab = QtWidgets.QWidget()

        self.resolutions = QtWidgets.QComboBox(self.tab)
        self.resolutions.setGeometry(QtCore.QRect(30, 60, 171, 21))
        self.resolutions.activated[str].connect(self.res_box_ev)

        self.difficulties = QtWidgets.QComboBox(self.tab)
        self.difficulties.setGeometry(QtCore.QRect(240, 60, 171, 21))
        self.difficulties.activated[str].connect(self.dif_box_ev)

        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(30, 40, 61, 16))

        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(240, 40, 61, 16))

        self.tabWidget.addTab(self.tab, "")
        self.play_b = QtWidgets.QPushButton(self)
        self.play_b.setGeometry(QtCore.QRect(310, 355, 80, 25))
        self.play_b.setDefault(True)
        self.play_b.clicked.connect(self.play)

        self.exit_b = QtWidgets.QPushButton(self)
        self.exit_b.setGeometry(QtCore.QRect(400, 355, 80, 25))
        self.exit_b.clicked.connect(self.exit_ev)

        self.initUI()
        self.retranslateUI()

        QtCore.QMetaObject.connectSlotsByName(self)

    def initUI(self):
        self.setFixedSize(500, 400)
        self.setWindowTitle('Game Config')
        self.setWindowIcon(QtGui.QIcon("Data\Settings.png"))

    def retranslateUI(self):
        res = app.desktop().screenGeometry()
        cur = self.con.cursor()
        ans = cur.execute("SELECT width, height from resols")

        for i in ans:
            self_height = res.height()
            if i[1] <= self_height:
                self.resolutions.addItem(f'{i[0]}x{i[1]}')
        resol = cur.execute("SELECT resolution from settings")
        for i in resol:
            self.resolutions.setCurrentText(i[0])

        self.difficulties.addItems(("Карапуз", "Легко", "Нормально",
                                    "Сложно", "Ты Бог?"))
        dif = cur.execute("SELECT last_dif from settings")
        for i in dif:
            self.difficulties.setCurrentIndex(int(i[0]))

        self.label.setText("Resolution")
        self.label_3.setText("Difficultly")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "Settings")
        self.play_b.setText("Play")
        self.exit_b.setText("Exit")

    def res_box_ev(self, val):
        cur = self.con.cursor()
        cur.execute(f"""UPDATE settings SET resolution = '{val}'""")
        self.con.commit()
        self.update()

    def dif_box_ev(self):
        cur = self.con.cursor()
        cur.execute(f"""UPDATE settings 
        SET last_dif = '{self.difficulties.currentIndex()}'""")
        self.con.commit()
        self.update()

    def play(self):
        self.hide()
        system('python game.py')
        self.exit_ev()

    def exit_ev(self):
        self.con.close()
        sys.exit()
