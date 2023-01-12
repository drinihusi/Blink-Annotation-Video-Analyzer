from csv_writer import readList


class Blink:
    def __init__(self, start_frame):
        self.startFrame = start_frame
        self.endFrame = None
        self.isNew = True  # for verification mode to prevent removing old blinks by accident

    def end(self, end_frame):
        self.endFrame = end_frame


class BlinkList:

    def __init__(self):
        self.list = []
        self.removeConfirmed = False

    def startBlink(self, frame_num):
        if self.isBlink(frame_num):
            msg = "Blinks can't overlap!"
        elif len(self.list) == 0 or self.list[-1].endFrame is not None:
            b = Blink(frame_num)
            self.list.append(b)
            msg = 'Blink #' + str(self.length()) + ' STARTED at frame ' + str(frame_num)
        else:
            msg = 'End current blink first!'
        return msg

    def endBlink(self, frame_num):
        if len(self.list) != 0:
            if self.list[-1].endFrame is None:
                for blink in self.list:  # make sure blink doesn't completely surround another blink
                    if blink.endFrame is not None and self.list[-1].startFrame < blink.endFrame < frame_num:
                        return "Blinks can't overlap!"
            if self.isBlink(frame_num):
                msg = "Blinks can't overlap!"
            elif frame_num < self.list[-1].startFrame and self.list[-1].isNew:
                msg = "Blink end must be after blink start!"
            elif self.list[-1].endFrame is None:
                self.list[-1].end(frame_num)
                msg = 'Blink #' + str(self.length()) + ' ENDED at frame ' + str(frame_num)
            else:
                msg = 'Start a blink first!'
        else:
            msg = 'Start a blink first!'
        return msg

    def removeBlink(self, frame_number=None):
        if self.length() != 0:
            if frame_number is not None:
                # verification mode unmark
                for i, blink in enumerate(self.list):
                    if blink.startFrame <= frame_number <= blink.endFrame:
                        if not self.removeConfirmed:
                            msg = 'Press again to confirm removing this blink (Frame ' + str(blink.startFrame) + ' -> ' + str(blink.endFrame) + ')'
                            self.removeConfirmed = True
                        else:
                            msg = 'Blink from frame ' + str(blink.startFrame) + ' -> ' + str(blink.endFrame) + ' REMOVED'
                            self.list.pop(i)
                            self.removeConfirmed = False
                        break
            elif not self.list[-1].isNew:
                msg = 'No new blinks to remove!'

            else:
                rem = self.list.pop()  # if no frame number is given, just remove the last frame
                frame_number = self.length()+1
                msg = 'Blink #' + str(frame_number) + ' (starting at frame ' + str(rem.startFrame) + ') REMOVED'
        else:
            msg = 'Nothing to remove!'
        return msg

    def importFromCSV(self, file):
        frameList = readList(file)
        lookingFor = 1
        for i, frameValue in enumerate(frameList):
            if frameValue == lookingFor:

                if lookingFor == 1:
                    # start of blink
                    self.startBlink(i)
                    lookingFor = 0
                else:
                    # end of blink
                    self.endBlink(i-1)
                    self.list[-1].isNew = False
                    lookingFor = 1

    def isBlink(self, frame):
        for blink in self.list:
            if blink.endFrame is not None:
                if blink.startFrame <= frame <= blink.endFrame:
                    return True
        return False

    def sortList(self):
        # bubble sort algorithm to sort by start frames
        n = self.length()
        swapped = False
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if self.list[j].startFrame > self.list[j + 1].startFrame:
                    swapped = True
                    self.list[j], self.list[j + 1] = self.list[j + 1], self.list[j]

            if not swapped:
                return

    def length(self):
        return len(self.list)

    def getList(self):
        return self.list

    def printAllBlinks(self):
        print('ALL BLINKS (start -> end)')
        for blink in self.list:
            print(str(blink.startFrame) + ' -> ' + str(blink.endFrame))
        print(str(self.length()) + ' blinks total')
