import csv
from blinks import *


def saveList(list, filename, delim, frame_count):
    
    isBlinking = False
    breakFlag = False

    with open(filename, 'w', newline='') as csvFile:
        listWriter = csv.writer(csvFile, delimiter=delim)
        
        blink_index = 0
        blinkValue = 0
        ended = False
        for i in range(frame_count):
            if blink_index < len(list):
                if list[blink_index].startFrame == i:
                    blinkValue = 1
                if list[blink_index].endFrame == i:
                    ended = True
                    blink_index += 1
            listWriter.writerow([i, blinkValue])
            if ended:
                blinkValue = 0
                ended = False


def readList(file):
    arr = []
    with open(file) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            arr.append(int(row[1]))
    return arr
