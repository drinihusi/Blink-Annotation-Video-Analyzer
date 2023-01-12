# Blink Video Analyzer for Ground Truth Data Collection

This program can be used to play back videos taken during DRT testing in order to mark the timing and duration of participants' blinks. It includes 2 modes: one to go through the video normally and mark the blinks, and one to play back the video again to verify that the first reviewer did not miss any blinks or mark any that shouldn't have been marked.

## Controls
Everything can be controlled either using the keyboard shortcuts below or clicking the buttons on the screen.


| Function                |          Key          |
|-------------------------|:---------------------:|
| **Play/Pause**          |       Space Bar       |
| **Forward/Back One Frame** | Left/Right Arrow Keys |
| **Mark Start of Blink** |           1           |
| **Mark End of Blink**   |           2           |
| **Remove Last Marked Blink** |           3           |
| **Unmark Current Blink** (verification mode only) |           4           |

## Determining Start and End of Blinks
The **start** of a blink should be marked on the first frame where the participant's eyes start to close.

The **end** of a blink should be marked on the first frame where the participant's eyes stop opening.

## Blink Recording Mode
In this mode, the user can play back the video at normal speed and/or go forward and back one frame at a time. The most efficient process is to:
1. Play through the video until you see a blink, then pause the video
2. Go back one frame at a time to mark the exact start frame
3. Go forward one frame at a time to mark the end frame
4. Resume playing at normal speed until you see another blink

After going through the full video clip, clicking **Save and Finish** will save all the marked blinks to a CSV file and return the program back to the main menu where another clip can be selected. Clicking **Change Video** will allow another clip to be selected, but will NOT save any marked blinks.

## Verification Mode
In this mode, the user can select a CSV and video file for a clip that has already been analyzed in order to verify the accuracy of the ground truth data and correct any mistakes made by the first reviewer. Based on the selected CSV file, the word "BLINK" will be displayed on the frame for all blinks marked by the first reviewer. The most efficient process is to:
1. Play through the video, ensuring that the word "BLINK" is shown every time the participant blinks and is not shown when they are not blinking. (being a few frames off is ok, since the exact frames where a blink starts and ends is subjective)
2. If a blink was missed during the first analysis, you can add it in by marking the start and end frame normally.
3. If any blinks were marked that should not have been, they can be removed by pressing '4' on the keyboard or clicking the 'Unmark Current Blink' button. This process requires a confirmation to avoid accidentally removing blinks.

After going through the full clip, clicking **Save and Finish** will save the CSV file with any changes to the marked blinks made.

## File Saving
CSV files are saved to the user's Appdata folder by default on Windows or home folder on Linux, and can be viewed by clicking **File > Open Output Folder**. 
This output folder can be changed by clicking **File > Settings** and selecting a new path.
