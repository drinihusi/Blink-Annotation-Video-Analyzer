import cv2
import time
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap


class VideoStreamer(QThread):
    change_pixmap_signal = pyqtSignal(QPixmap, int)

    def __init__(self, file, main_window_object, frame_buffer_size):
        super().__init__()
        # setup
        self.videoFile = file
        self.frameBufferSize = frame_buffer_size
        self.cap = cv2.VideoCapture(file)
        self.mainWindow = main_window_object
        self.frameRate = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.totalFrames/self.frameRate
        self._run_flag = True
        self.frame = None
        self.fps = None
        self.elapsedTime = None
        self.currentFrameNum = None
        self.qtImg = None

        # timing setup
        self.desiredDelay = 1 / self.frameRate
        self.sleepTime = self.desiredDelay
        self.prevFrameTime = time.time()
        self.newFrameTime = time.time() + self.desiredDelay
        self.elapsedTimes = []
        for i in range(self.frameBufferSize):
            self.elapsedTimes.append((1 / self.frameRate))
        self.avgFrameDelay = sum(self.elapsedTimes) / len(self.elapsedTimes)

    def startPlayback(self, start_frame=0):
        self.currentFrameNum = start_frame
        self.start()

    def run(self):
        print('Starting from frame ' + str(self.currentFrameNum))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrameNum)

        """MAIN LOOP"""
        while self._run_flag:
            # time stuff
            self.prevFrameTime = self.newFrameTime
            self.newFrameTime = time.time()
            self.elapsedTime = self.newFrameTime - self.prevFrameTime
            if self.elapsedTime < 0.5:  # don't add longer times from pausing
                self.elapsedTimes.append(self.elapsedTime)
                self.elapsedTimes.pop(0)
            self.fps = str(1 / self.avgFrameDelay)

            # frame processing
            ret, self.frame = self.cap.read()
            if ret:
                self.processAndDisplayFrame()
                self.currentFrameNum += 1

                # sleep until next cycle
                self.avgFrameDelay = sum(self.elapsedTimes) / len(self.elapsedTimes)
                self.sleepTime = self.desiredDelay - self.avgFrameDelay if self.desiredDelay - self.avgFrameDelay > 0 else 0
                time.sleep(self.sleepTime)
            else:
                self.stop()

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.mainWindow.videoPlaybackLabel.width(), self.mainWindow.videoPlaybackLabel.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

    def getSingleFrame(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrameNum)
        ret, self.frame = self.cap.read()
        if ret:
            self.processAndDisplayFrame()

    def processAndDisplayFrame(self):
        # self.frame = cv2.resize(self.frame, (853, 480))
        cv2.putText(self.frame, str(self.currentFrameNum), (7, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2, cv2.LINE_AA)
        if self.mainWindow.mode == 1 and self.mainWindow.blinkFramesList.isBlink(self.currentFrameNum):
            cv2.putText(self.frame, 'BLINK', (700, 1000), cv2.FONT_HERSHEY_SIMPLEX, 7, (255, 255, 0), 9, cv2.LINE_AA)
        self.qtImg = self.convert_cv_qt(self.frame)

        # pass image back to GUI thread
        self.change_pixmap_signal.emit(self.qtImg, self.currentFrameNum)




