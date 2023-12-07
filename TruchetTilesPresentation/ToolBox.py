import cairo
import math
import os.path

PIXEL_SIZE = 50 

def context2png(context, pngName):
    context.get_target().write_to_png(pngName)
    
def deg2rad(angle):
    return angle * math.pi/180.0
def letter2Angle(letter):
    d = {'a' : 0, 'b' : 90, 'c' : 180, 'd' : 270}
    return d[letter]

def createDirectory(dirName):
    parentPath = os.getcwd()
    path = os.path.join(parentPath, dirName)
    if not os.path.isdir(path):
        os.mkdir(path)   
def createAllDirectories():
    createDirectory("Raw")    
    createDirectory("Results")    
    createDirectory("Tiles")    
    createDirectory("Patterns")    

    
def getRawName(fileName):
    path = os.getcwd()
    return path + "/Raw/" + fileName + ".png"
def getPatternName(fileName):
    path = os.getcwd()
    return path + "/Patterns/" + fileName + ".svg"
def get_SVG_TileName(fileName):
    path = os.getcwd()
    return path + "/Tiles/" + fileName + ".svg"
def get_PNG_TileName(fileName):
    path = os.getcwd()
    return path + "/Tiles/" + fileName + ".png"
def get_SVG_ResultName(fileName):
    path = os.getcwd()
    return path + "/Results/" + fileName + ".svg"
def get_PNG_ResultName(fileName):
    path = os.getcwd()
    return path + "/Results/" + fileName + ".png"