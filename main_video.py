import ctypes
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import QtCore
from video_playback import VideoStreamer
from ui_classes import *
from yaml_editor import *
from blinks import *
import platform
from csv_writer import *
from instructions_UI import InstructionsDialog
from settings_UI import SettingsDialog

'''
BUILD COMMAND:
pyinstaller main_video.py --name="Video Analyzer" --icon="assets\hslab_logo.ico" --noconsole --onedir --onefile --add-data "assets\;." --add-data "README.md;."
'''


class MainWindow(QMainWindow):

    def __init__(self, w, h):
        super(MainWindow, self).__init__()
        createConfigFiles()

        self.playbackThread = None
        self.playing = False
        self.wasPlaying = False
        self.videoFilePath = None
        self.csvFilePath = None
        self.mode = None
        if platform.system() == "Windows":
            self.width = w
            self.height = h
        else:
            self.width = 1920
            self.height = 1080
        self.blinkFramesList = BlinkList()
        self.setWindowTitle("HMS Blink Data Ground Truth Collection")
        iconPath = resource_path("HSL-logo.png")
        self.setWindowIcon(QtGui.QIcon(iconPath))

        # # to make taskbar icon display
        if platform.system() == "Windows":
            myappid = 'com.hmslab.videoanalyzer'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # mode/file selector
        self.modeSelectLabel = TitleLabel('Select a Mode:', 16)
        self.primaryModeLabel = TitleLabel('Blink Recording Mode', 14)
        self.videoSelectBtn = QPushButton('Select a Video File')
        self.videoSelectBtn.clicked.connect(self.selectVideo)
        self.videoSelectBtn.setMinimumWidth(180)
        self.primaryModeWidget = VerticalWidget([self.primaryModeLabel, 'stretch', self.videoSelectBtn, 'stretch'], hCentered=True)
        self.primaryModeFrame = QFrame()
        self.primaryModeFrame.setLayout(self.primaryModeWidget.getLayout())
        self.primaryModeFrame.setFrameShape(QFrame.Box)
        self.primaryModeFrame.setMinimumWidth(250)
        self.primaryModeFrame.setMaximumHeight(int(self.height/5))

        self.verifyModeLabel = TitleLabel('Verify Blinks Mode', 14)
        self.modeSelectionInfoLabel = QLabel('')
        self.csvSelectBtn = QPushButton('Select a CSV File')
        self.csvSelectBtn.clicked.connect(lambda: self.selectVideoAndCSV('csv'))
        self.csvSelectBtn.setMinimumWidth(180)
        self.andLabel = QLabel('and')
        self.videoSelectBtn2 = QPushButton('Select a Video File')
        self.videoSelectBtn2.clicked.connect(lambda: self.selectVideoAndCSV('video'))
        self.videoSelectBtn2.setMinimumWidth(180)
        self.verifyModeWidget = VerticalWidget([self.verifyModeLabel, 'stretch', self.csvSelectBtn, self.andLabel, self.videoSelectBtn2, 'stretch'], hCentered=True)
        self.verifyModeFrame = QFrame()
        self.verifyModeFrame.setLayout((self.verifyModeWidget.getLayout()))
        self.verifyModeFrame.setFrameShape(QFrame.Box)
        self.verifyModeFrame.setMinimumWidth(250)
        self.verifyModeFrame.setMaximumHeight(int(self.height/5))

        self.bothModesWidget = HorizontalWidget([self.primaryModeFrame, self.verifyModeFrame])

        self.videoSelectWidget = VerticalWidget(['stretch', self.modeSelectLabel, self.bothModesWidget, self.modeSelectionInfoLabel, 'stretch'], hCentered=True)

        # create the label that holds the image
        self.videoPlaybackLabel = QLabel()

        # video progress slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.timeLabel = QLabel('0:00/0:00')
        self.frameLabel = QLabel('Frame 0/0')
        self.sliderInfoWidget = HorizontalWidget([self.timeLabel, 'stretch', self.frameLabel])
        self.sliderWidget = VerticalWidget(['stretch', self.slider, self.sliderInfoWidget])
        self.sliderWidget.setFixedHeight(100)

        # control buttons
        self.playBtn = QPushButton('>')
        self.playBtn.clicked.connect(self.resumeVideo)
        self.pauseBtn = QPushButton('||')
        self.pauseBtn.clicked.connect(lambda: self.pauseVideo(True))
        self.fwdBtn = QPushButton('-->')
        self.fwdBtn.clicked.connect(self.frameForward)
        self.backBtn = QPushButton('<--')
        self.backBtn.clicked.connect(self.frameBack)

        self.changeVideoBtn = QPushButton('Return to Menu')
        self.changeVideoBtn.setMinimumWidth(150)
        self.changeVideoBtn.clicked.connect(self.backToMenu)

        self.saveButton = QPushButton('Save and Finish')
        self.saveButton.clicked.connect(self.saveAndFinish)
        self.saveButton.setMinimumWidth(200)

        self.btnWidget = HorizontalWidget([self.changeVideoBtn, 'stretch', self.backBtn, self.pauseBtn, self.playBtn, self.fwdBtn, 'stretch', self.saveButton])
        self.btnWidget.setMaximumHeight(150)

        self.leftPanel = VerticalWidget([self.videoPlaybackLabel, self.sliderWidget, self.btnWidget])

        self.console = QLabelConsole(20)

        # blink marking buttons
        self.startBlinkButton = QPushButton('Mark Blink Start (1)')
        self.startBlinkButton.clicked.connect(lambda: self .markBlink('start'))
        self.endBlinkButton = QPushButton('Mark Blink End (2)')
        self.endBlinkButton.clicked.connect(lambda: self.markBlink('end'))
        self.undoBlinkButton = QPushButton('Remove Last Blink (3)')
        self.undoBlinkButton.clicked.connect(lambda: self.markBlink('undo'))
        self.unmarkBlinkButton = QPushButton('Unmark Current Blink (4)')
        self.unmarkBlinkButton.clicked.connect(lambda: self.markBlink('remove'))

        self.markButtonWidget = VerticalWidget([HorizontalWidget([self.startBlinkButton, self.endBlinkButton]), HorizontalWidget([self.undoBlinkButton, self.unmarkBlinkButton])])
        self.markButtonWidget.setFixedHeight(180)
        self.rightPanel = VerticalWidget([self.console, self.markButtonWidget])

        self.videoPlaybackWidget = HorizontalWidget([self.leftPanel, self.rightPanel])
        self.stackWidget = QStackedWidget()
        self.stackWidget.addWidget(self.videoSelectWidget)
        self.stackWidget.addWidget(self.videoPlaybackWidget)
        self.stackWidget.currentChanged.connect(self.stackWidgetChanged)
        self.setCentralWidget(self.stackWidget)
        self.setChildrenFocusPolicy(QtCore.Qt.NoFocus)

        # Sizing
        h = int(self.height - self.sliderWidget.height() - self.btnWidget.height() - 30)
        self.videoPlaybackLabel.setFixedHeight(h)
        w = int(h * (16/9))
        self.videoPlaybackLabel.setFixedWidth(w)
        self.console.setFixedWidth(self.width - w - 50)

        # MENU BAR
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')

        self.instructionsAct = QAction('View Instructions', self)
        self.instructionsAct.triggered.connect(self.openInstructions)
        self.menuBar.addAction(self.instructionsAct)

        self.settingsAct = QAction('Settings', self)
        self.settingsAct.triggered.connect(self.openSettings)
        self.fileMenu.addAction(self.settingsAct)

        self.openFolderAct = QAction('Open Output Folder', self)
        self.openFolderAct.triggered.connect(self.openOutputFolder)
        self.fileMenu.addAction(self.openFolderAct)

    def startVideoPlayback(self, frame_number=0):
        # create the video playback thread
        self.playbackThread = VideoStreamer(self.videoFilePath, main_window_object=self, frame_buffer_size=10 * 60)
        self.playbackThread.change_pixmap_signal.connect(self.update_image)
        self.playbackThread.startPlayback(frame_number)
        self.slider.setTickInterval(1)
        self.slider.setMaximum(int(self.playbackThread.duration))
        self.updatePlayingState(True)

    def pauseVideo(self, from_btn=False):
        self.playbackThread.stop()
        if from_btn: self.playbackThread.currentFrameNum -= 1
        self.updatePlayingState(False)

    def resumeVideo(self):
        startFrame = self.playbackThread.currentFrameNum
        self.startVideoPlayback(startFrame)
        self.updatePlayingState(True)

    def frameBack(self):
        self.pauseVideo()
        self.playbackThread.currentFrameNum -= 1
        self.playbackThread.getSingleFrame()

    def frameForward(self):
        self.pauseVideo()
        self.playbackThread.currentFrameNum += 1
        self.playbackThread.getSingleFrame()
        self.resetConfirmation()

    def updatePlayingState(self, new_state):
        self.playing = new_state
        self.playBtn.setEnabled(not new_state)
        self.pauseBtn.setEnabled(new_state)
        self.resetConfirmation()

    def saveAndFinish(self):
        self.pauseVideo()
        try:
            if self.blinkFramesList.list[-1].endFrame is not None:
                outputPath = yaml_read('Output Path')

                # create filename from original video name
                fileName = self.videoFilePath.split("/")[-1].split(".")
                fileName.pop()
                fileName = '.'.join(fileName)
                fileName += '_Ground_Truth'
                if self.mode == 1:
                    fileName += '_Verified'
                    outputPath = os.path.join(outputPath, 'Verified Annotations')
                else:
                    outputPath = os.path.join(outputPath, 'Primary Annotations')
                if not os.path.isdir(outputPath):
                    os.mkdir(outputPath)

                fileName += '.csv'

                self.blinkFramesList.sortList()
                saveList(self.blinkFramesList.list, os.path.join(outputPath, fileName), ',', self.playbackThread.totalFrames)
                self.stackWidget.setCurrentIndex(0)
                self.modeSelectionInfoLabel.setText('CSV file saved!')

            else:
                self.console.log('Please end current blink before saving!')

        except:
            self.console.log('Failed to save CSV! Verify output path and try again')

    def backToMenu(self):
        self.pauseVideo()
        self.stackWidget.setCurrentIndex(0)
        
    def selectVideo(self):
        if self.playing: self.pauseVideo()
        p = yaml_read("Video Select Path")
        if not os.path.exists(yaml_read("Video Select Path")):
            p = getConfigPath()
        fileName = QFileDialog.getOpenFileName(None, 'Select a Video File:', p,
                                               "Video Files (*.mp4 *.m4a *.mov *.wmv *.flv *.mkv *.avi)")[0]
        if fileName != "":
            self.videoFilePath = fileName
            yaml_write("Video Select Path", os.path.dirname(fileName))  # remember where video was selected from
            self.mode = 0       # primary mode
            self.stackWidget.setCurrentIndex(1)
            self.startVideoPlayback(0)
            self.frameForward()
        else:
            self.modeSelectionInfoLabel.setText('No video file selected!')

    def selectVideoAndCSV(self, file_type):
        if file_type == 'csv':
            p = os.path.join(yaml_read("Output Path"), 'Primary Annotations')
            if not os.path.exists(p):
                os.mkdir(p)
            fileName = QFileDialog.getOpenFileName(None, 'Select a CSV File:', p, "CSV Files (*.csv)")[0]

            if fileName != "":
                self.csvFilePath = fileName
                self.modeSelectionInfoLabel.setText(self.csvFilePath.split("/")[-1] + ' selected!')
            else:
                self.modeSelectionInfoLabel.setText('No CSV file selected!')

        if file_type == 'video':
            if self.csvFilePath is None:
                self.modeSelectionInfoLabel.setText('Select a CSV file first!')
            else:
                p = yaml_read("Video Select Path")
                if not os.path.exists(yaml_read("Video Select Path")):
                    p = getConfigPath()
                fileName = QFileDialog.getOpenFileName(None, 'Select a Video File:', p,
                                                       "Video Files (*.mp4 *.m4a *.mov *.wmv *.flv *.mkv *.avi)")[0]
                if fileName != "":
                    self.videoFilePath = fileName
                    self.startVideoPlayback(0)

                    # make sure video and CSV match
                    if sum(1 for row in open(self.csvFilePath)) == self.playbackThread.totalFrames:
                        yaml_write("Video Select Path", os.path.dirname(fileName))  # remember where video was selected from
                        self.mode = 1  # verify mode
                        self.stackWidget.setCurrentIndex(1)
                        self.blinkFramesList.importFromCSV(self.csvFilePath)
                        self.console.log(str(self.blinkFramesList.length()) + ' blinks found in CSV')
                        self.frameForward()
                    else:
                        self.modeSelectionInfoLabel.setText("CSV and video files don't match!")
                        self.videoFilePath = None
                        self.pauseVideo()
                else:
                    self.modeSelectionInfoLabel.setText('No video file selected!')

    def markBlink(self, blink_type):
        if blink_type == 'start':
            self.resetConfirmation()
            msg = self.blinkFramesList.startBlink(self.playbackThread.currentFrameNum)

        elif blink_type == 'end':
            self.resetConfirmation()
            msg = self.blinkFramesList.endBlink(self.playbackThread.currentFrameNum)

        elif blink_type == 'undo':
            self.resetConfirmation()
            msg = self.blinkFramesList.removeBlink()

        elif blink_type == 'remove':
            # for verification mode only, pass an index to the remove function to unmark a blink that is already marked
            msg = self.blinkFramesList.removeBlink(self.playbackThread.currentFrameNum)
            if 'REMOVED' in msg:  # to clear blink text
                self.frameForward()
                self.frameBack()

        self.console.log(msg)

    def stackWidgetChanged(self):
        if self.stackWidget.currentIndex() == 0:    # returning to menu
            self.videoFilePath = None
            self.csvFilePath = None
            self.blinkFramesList = BlinkList()
        else:   # opening player
            self.console.clear()
            if self.mode == 0:
                self.unmarkBlinkButton.setEnabled(False)
            else:
                self.unmarkBlinkButton.setEnabled(True)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key_Space:
            if self.playing: self.pauseVideo(True)
            else: self.resumeVideo()
        elif key == Qt.Key_Left:
            self.frameBack()
        elif key == Qt.Key_Right:
            self.frameForward()
        elif key == Qt.Key_1:
            self.markBlink('start')
        elif key == Qt.Key_2:
            self.markBlink('end')
        elif key == Qt.Key_3:
            self.markBlink('undo')
        elif key == Qt.Key_4 and self.mode == 1:
            self.markBlink('remove')
        elif key == Qt.Key_0: # testing only
            self.blinkFramesList.sortList()
            self.blinkFramesList.printAllBlinks()

    def setChildrenFocusPolicy(self, policy):
        # this function is needed to override default arrow key behaviour
        def recursiveSetChildFocusPolicy(parentQWidget):
            for childQWidget in parentQWidget.findChildren(QWidget):
                childQWidget.setFocusPolicy(policy)
                recursiveSetChildFocusPolicy(childQWidget)

        recursiveSetChildFocusPolicy(self)

    def closeEvent(self, event):
        try:
            self.playbackThread.stop()
            self.playbackThread.cap.release()
            cv2.destroyAllWindows()
            event.accept()
        except: pass

    def update_image(self, img, frameNum):
        # update time info
        m, s = divmod((frameNum / self.playbackThread.frameRate), 60)
        m = str(int(m))
        s = str(int(s))
        m = '0' + m if int(m) < 9 else m
        s = '0' + s if int(s) < 9 else s
        tmin, tsec = divmod(self.playbackThread.duration, 60)
        tmin = str(int(tmin))
        tsec = str(int(tsec))
        tmin = '0' + tmin if int(tmin) < 9 else tmin
        tsec = '0' + tsec if int(tsec) < 9 else tsec

        self.timeLabel.setText(m + ':' + s + '/' + tmin + ':' + tsec)
        self.frameLabel.setText('Frame ' + str(frameNum) + '/' + str(self.playbackThread.totalFrames))
        self.slider.setSliderPosition(int(frameNum/self.playbackThread.frameRate))
        self.videoPlaybackLabel.setPixmap(img)

    def openSettings(self):
        self.settingsDialog = SettingsDialog()
        status = self.settingsDialog.exec()

    def openInstructions(self):
        self.instructionsDialog = InstructionsDialog()
        status = self.instructionsDialog.exec()

    def openOutputFolder(self):
        path = yaml_read("Output Path")
        if not os.path.isdir(path):
            os.mkdir(path)

        os.startfile(path)

    def resetConfirmation(self):
        self.blinkFramesList.removeConfirmed = False

    def shutdown(self):
        # self.saveAndFinish()
        pass

def main():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    app.setFont(QFont('Calibri', 12))
    window = MainWindow(screen.availableGeometry().width(), screen.availableGeometry().height())
    window.showMaximized()
    e_code = app.exec_()
    window.shutdown()
    sys.exit(e_code)


if __name__ == '__main__':
    main()
