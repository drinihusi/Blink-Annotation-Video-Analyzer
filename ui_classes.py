from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QLineEdit, QFrame, QAction, QActionGroup, QPlainTextEdit, QSplashScreen
import os
import sys


class VerticalWidget(QWidget):
    def __init__(self, childWidgets, vCentered=False, hCentered=False):
        super(VerticalWidget, self).__init__()

        self.layout = QVBoxLayout()

        for widget in childWidgets:
            if widget == "stretch":
                self.layout.addStretch()
            else:
                if hCentered:
                    self.layout.addWidget(widget, alignment=Qt.AlignHCenter)
                else:
                    self.layout.addWidget(widget)
        
        if vCentered:
            self.layout.setAlignment(Qt.AlignCenter)
        
        self.setLayout(self.layout)
    
    def getLayout(self):
        return self.layout


class HorizontalWidget(QWidget):
    def __init__(self, childWidgets, vCentered=False, hCentered=False):
        super(HorizontalWidget, self).__init__()

        self.layout = QHBoxLayout()

        for widget in childWidgets:
            if widget == "stretch":
                self.layout.addStretch()
            else:
                if vCentered:
                    self.layout.addWidget(widget, alignment=Qt.AlignVCenter)
                else:
                    self.layout.addWidget(widget)
        
        if hCentered:
            self.layout.setAlignment(Qt.AlignCenter)
        
        self.setLayout(self.layout)
    
    def getLayout(self):
        return self.layout


class QLabelConsole(QFrame):
    def __init__(self, rows, minWidth=550):
        super(QLabelConsole, self).__init__()

        self.labelList = []
        for i in range(rows):
            self.labelList.append(QLabel(''))
        
        vw = VerticalWidget(self.labelList)

        layout = vw.getLayout()

        self.setLayout(layout)
        self.setFrameShape(QFrame.Box)
        self.setMinimumWidth(minWidth)

        self.cursorPos = 0
        self.length = rows
    
    def log(self, text):

        print(text)
        
        # if console isn't full
        if self.cursorPos < self.length:
            self.labelList[self.cursorPos].setText(str(text))
            self.labelList[self.cursorPos].setStyleSheet("font-weight: bold")
            self.labelList[self.cursorPos-1].setStyleSheet("font-weight: normal")
            self.cursorPos += 1
        
        # if console is full
        else:
            for i in range(self.length-1):
                self.labelList[i].setText(self.labelList[i+1].text())
                self.labelList[i].setStyleSheet("font-weight: normal")
            self.labelList[-1].setText(str(text))
            self.labelList[-1].setStyleSheet("font-weight: bold")
    
    def clear(self):
        for i in range(self.length):
            self.labelList[i].setText("")
        self.cursorPos = 0


class IndexedButton(QPushButton):
    def __init__(self, text, id, width=0, icon=''):
        super(IndexedButton, self).__init__()
        
        self.id = id
        self.setText(text)
        if width != 0: self.setFixedWidth(width)
        if icon != '': 
            if isinstance(icon, str):
                self.setIcon(QtGui.QIcon(resource_path(icon)))
            else:
                self.setIcon(icon)


class LabelFieldPair(QWidget):
    def __init__(self, labelText, fieldText='', minFWidth=0, maxFWidth=0, minLWidth=0, maxLWidth=0, fieldEnabled=True, vCentered=False, hCentered=False):
        super(LabelFieldPair, self).__init__()

        self.label = QLabel(labelText)
        self.field = QLineEdit(fieldText)

        self.field.setEnabled(fieldEnabled)
        
        if minFWidth != 0:
            self.field.setMinimumWidth(minFWidth)
        if maxFWidth != 0:
            self.field.setMaximumWidth(maxFWidth)
        if minLWidth != 0:
            self.label.setMinimumWidth(minLWidth)
        if maxLWidth != 0:
            self.label.setMaximumWidth(maxLWidth)

        hWidget = HorizontalWidget([self.label, self.field], vCentered, hCentered)
        self.setLayout(hWidget.getLayout())


class LoginWidget(QWidget):

    def __init__(self, labelText):
        super (LoginWidget, self).__init__()

        self.label = QLabel('Log in to hawkbit credential manager:')
        self.usernameForm = LabelFieldPair('Username:', minFWidth=280)
        self.passwordForm = LabelFieldPair('Password:', minFWidth=280)
        self.passwordForm.field.setEchoMode(QLineEdit.Password)
        self.button = QPushButton('Login')
        self.button.setMinimumWidth(150)
        self.errorLabel = QLabel()
        self.errorLabel.setContentsMargins(11, 20, 11, 11)

        w = VerticalWidget([self.label, self.usernameForm, self.passwordForm, self.button, self.errorLabel], vCentered=True, hCentered=True)  
        self.setLayout(w.getLayout())         


# class for title fonts
class TitleLabel(QLabel):
    def __init__(self, text, size):
        super(TitleLabel, self).__init__()
        self.font = QtGui.QFont('calibri')
        self.setStyleSheet("font-weight: bold")
        self.font.setPointSize(size)
        self.setFont(self.font)
        self.setText(text)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        if relative_path == 'README.md':
            base_path = ''
        else:
            base_path = os.path.abspath(r".\assets")

    return os.path.join(base_path, relative_path)