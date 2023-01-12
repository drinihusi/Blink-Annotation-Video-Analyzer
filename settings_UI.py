from PyQt5.QtWidgets import *
from ui_classes import *
from yaml_editor import *


class SettingsDialog(QDialog):
    def __init__(self) -> None:
        super(SettingsDialog, self).__init__(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.saveFlags = []

        self.setWindowTitle("Settings")
        iconPath = resource_path("HSL-logo.png")
        self.setWindowIcon(QtGui.QIcon(iconPath))
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(900, 200)  # w, h

        self.outputPathSelector = LabelFieldPair('Output Folder:', yaml_read('Output Path'))
        self.outputPathSelector.field.setReadOnly(True)
        self.selectFolderBtn = QPushButton('Select Folder')
        self.selectFolderBtn.setMinimumWidth(120)
        self.selectFolderBtn.clicked.connect(self.selectOutputFolder)
        self.outputPathWidget = HorizontalWidget([self.outputPathSelector, self.selectFolderBtn])
        self.errorLabel = QLabel('')
        self.errorLabel.setAlignment(Qt.AlignHCenter)

        self.cancelBtn = QPushButton('Cancel')
        self.cancelBtn.clicked.connect(self.cancel)
        self.saveBtn = QPushButton('Save')
        self.saveBtn.clicked.connect(self.save)
        self.bottomBtnWidget = HorizontalWidget([self.cancelBtn, self.saveBtn], hCentered=True)

        self.mainWidget = VerticalWidget([self.outputPathWidget, 'stretch', self.errorLabel, self.bottomBtnWidget])
        self.mainLayout = self.mainWidget.getLayout()
        self.setLayout(self.mainLayout)

    def selectOutputFolder(self):
        oldPath = yaml_read("Output Path")
        newPath = QFileDialog.getExistingDirectory(None, 'Select New Output Location:', oldPath, QFileDialog.ShowDirsOnly)

        if newPath == oldPath or newPath == "":
            self.errorLabel.setText('No new path selected')
        else:
            self.outputPathSelector.field.setText(newPath)
            self.saveFlags.append('Output Path')
            self.resetErrorLabel()

    def resetErrorLabel(self):
        self.errorLabel.setText('')

    def cancel(self):
        self.close()

    def save(self):
        if 'Output Path' in self.saveFlags:
            # save filePath
            print('saved')
            newPath = self.outputPathSelector.field.text()
            yaml_write("Output Path", newPath)
        self.close()

    def closeEvent(self, event):
        pass

