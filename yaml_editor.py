from platform import platform
import yaml
import os
import io
from shutil import copyfile, copytree, rmtree
import platform

plat = platform.system()
if plat == "Windows":
    filePath = os.path.join(os.path.expanduser("~"), "Appdata", "Roaming", "HMS Lab Video Analyzer")
else:
    filePath = os.path.join(os.path.expanduser("~"), ".HMS-Lab-Video-Analyzer")

if not os.path.isdir(filePath):
    os.mkdir(filePath)
filePath = os.path.join(filePath, "config")
if not os.path.isdir(filePath):
    os.mkdir(filePath)

fileNames = ["config"]


def yaml_read(key, key2=''):
    global filePath
    returnVal = ""
    # check key to see which file to write it to
    fileName = os.path.join(filePath, chooseFile(key))

    try:
        with open(fileName, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

            # try to use second key
            if key2 != "":
                returnVal = data_loaded[key][key2]
            else:
                returnVal = data_loaded[key]

    except:
        updateConfigFiles()
        with open(fileName, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        if key2 != "":
            returnVal = data_loaded[key][key2]
        else:
            returnVal = data_loaded[key]

    return returnVal


# function to write a value to a YAML file
def yaml_write(key, dataToWrite="", key2=""):
    global filePath

    # check key to see which file to write it to
    fileName = os.path.join(filePath, chooseFile(key))

    with open(fileName, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    if key2 != "":
        data_loaded[key][key2] = dataToWrite
    else:
        data_loaded[key] = dataToWrite

    with io.open(fileName, 'w', encoding='utf8') as outfile:
        yaml.dump(data_loaded, outfile, default_flow_style=False, allow_unicode=False, sort_keys=False)


def chooseFile(key) -> str:
    return "config.yml"


def updateConfigFiles():
    # create new config files and then copy old settings back into new files
    global fileNames

    # make .old files
    fileNamesTemp = fileNames

    for index, file in enumerate(fileNamesTemp):
        fileNamesTemp[index] = os.path.join(filePath, file + '.yml')

    for file in fileNamesTemp:
        copyfile(file, file + ".old")

    # regenerate new files
    createConfigFiles(forced=True)

    # open old files and write their values into new files (for some reason the method of getting keys is different in both cases)
    for file in fileNamesTemp:
        with open(file + ".old", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            keyList = data_loaded.keys

            for key in keyList():
                if not isinstance(data_loaded[key], dict):  # single value keys
                    yaml_write(key, data_loaded[key])
                else:  # nested keys
                    for nestedKey in list(data_loaded[key].keys()):
                        yaml_write(key, data_loaded[key][nestedKey], nestedKey)

        os.remove(file + ".old")


def createConfigFiles(forced=False):
    # make sure all config files exist and create and write to them if they do not
    fileName = os.path.join(filePath, "config.yml")
    if not os.path.isfile(fileName) or forced:
        data = {
            'Video Select Path': filePath,
            'Output Path': os.path.join(os.path.dirname(filePath), 'Output')
        }
        with io.open(fileName, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)


def getConfigPath():
    return filePath

