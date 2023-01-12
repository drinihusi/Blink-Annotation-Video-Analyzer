from PyQt5.QtWidgets import *
from ui_classes import *


class InstructionsDialog(QDialog):
    def __init__(self) -> None:
        super(InstructionsDialog, self).__init__(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Instructions")
        iconPath = resource_path("HSL-logo.png")
        self.setWindowIcon(QtGui.QIcon(iconPath))
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(800, 500)  # w, h

        self.mainText = QTextEdit()
        with open(resource_path('README.md')) as f:
            text = f.read()
        self.mainText.setMarkdown(text)
        self.mainText.setReadOnly(True)

        self.mainWidget = VerticalWidget([self.mainText])
        self.mainLayout = self.mainWidget.getLayout()
        self.setLayout(self.mainLayout)

    def closeEvent(self, event):
        pass

