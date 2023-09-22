import numpy as np
from PIL import Image
import random as rd
import os.path
import cairo
import math
import ContinuousLine as C

# =============== GETS ===============
def printDico(dico):
    for e in dico:
        print(e, ":", dico[e])

def getRawName(fileName):
    path = os.getcwd()
    return path + "/Raw/" + fileName + ".jpg"
def getLpName(fileName):
    path = os.getcwd()
    return path + "/LPFiles/" + fileName + ".lp"
def getSolName(fileName):
    path = os.getcwd()
    return path + "/SolFiles/" + fileName + ".sol"
def getLogName(fileName): 
    path = os.getcwd()
    return path + "/LogFiles/" + fileName + ".log"
def getSvgName(fileName):
    path = os.getcwd()
    return path + "/Results/" + fileName + ".svg"

def getSumGrayScales(gsMatrix):
    sum = 0
    for i in range(len(gsMatrix)):
        for j in range(len(gsMatrix[0])):
            sum += gsMatrix[i][j]
    return sum

def getDistance(a0Coords: tuple, a1Coords: tuple):
    (x0, y0) = a0Coords
    (x1, y1) = a1Coords    
    return math.sqrt((x0-x1)**2 + (y0-y1)**2 )

def getCoords(dotsDict: dict, dotName: str):
    return dotsDict[dotName][0]
def getTBCounter(dotsDict: dict, dotName: str):
    return dotsDict[dotName][1]
def getOnlyCoords(dotsDict: dict):
    res = []
    for dot in dotsDict:
        res.append(dotsDict[dot][0])
    return res

def getClosest(dotsDict, tBCoords):
    closestName = "a0"
    closestCoords = getCoords(dotsDict, closestName)

    min = getDistance(closestCoords, tBCoords)
    
    for dot in dotsDict:
        currCoords = getCoords(dotsDict, dot)
        dist = getDistance(tBCoords, currCoords)
        if dist < min:
            min = dist
            closestName = dot
    return closestName

def getHitProba(gSValue, gsSum):
    return (255 - gSValue)/gsSum

def getRandomPosition(blocksize, i, j):
    x = int(rd.random() * blocksize + j * blocksize)
    y = int(rd.random() * blocksize + i * blocksize)
    return (x,y)

def getTractorBeamCoords(gsMatrix, gsSum, blocksize):
    height = len(gsMatrix) 
    width = len(gsMatrix[0]) 
    experienceProba = 1
    toReachProba = 0
    while experienceProba > toReachProba: 
        i = rd.randint(0,height-1)
        j = rd.randint(0,width-1)
        toReachProba = getHitProba(gsMatrix[i][j], gsSum)
        experienceProba = rd.random()
        (x,y) = getRandomPosition(blocksize, i, j)
    return (x,y)

def getRethrownDotsDict(gsMatrix, gsSum, blocksize, dotsDict):
    tBCoords = getTractorBeamCoords(gsMatrix, gsSum, blocksize)
    closest = getClosest(dotsDict, tBCoords)
    while getTBCounter(dotsDict, closest) > 120:
        tBCoords = getTractorBeamCoords(gsMatrix, gsSum, blocksize)
        closest = getClosest(dotsDict, tBCoords)
    updateDotPosition(dotsDict, closest, tBCoords)
    return dotsDict

def isHit(gsMatrix, coords, gsSum):
    (i,j) = coords
    toReachProba = getHitProba(gsMatrix[i][j], gsSum)
    experienceProba = rd.random()
    return experienceProba < toReachProba

# =============== RASTERIZATION ===============

def image2matrix(rawName, blocksize):
    image =  Image.open(rawName).convert('RGB')
    image =  Image.open(rawName).convert('L')

    width, height = image.size
    width = width//blocksize
    height = height//blocksize
    arrayIm = np.asarray(image)   
    matrix = [[0 for j in range (width)] for i in range (height)]

    for i in range (height):    
        for j in range(width):
            mean = 0
            for k in range(blocksize):
                for l in range(blocksize):
                    mean = mean + (arrayIm[blocksize*i + k][blocksize*j + l])
            mean = int(mean / (blocksize**2))
            matrix[i][j] = mean

    image.close()
    
    return matrix

# =============== DART THROWING ===============

def createPointsDictionnary(wantedNumberOfDots):
    d = {}
    # d[ai] = [coords, number of times the point i has been the target of the tractor beam]
    for i in range(wantedNumberOfDots):
        dotName = "a" + str(i)
        d[dotName] = [(0,0), -1]

    return d

def updateDotPosition(dotsDict, dotName, newPos):
    tBCounter = getTBCounter(dotsDict, dotName)
    if tBCounter == -1:
        # on initialise le dico
        dotsDict[dotName] = [newPos, tBCounter+1]
    else:
        oldPos = getCoords(dotsDict, dotName)
        x = int(1/(tBCounter+1) * newPos[0] + tBCounter/(tBCounter+1) * oldPos[0])
        y = int(1/(tBCounter+1) * newPos[1] + tBCounter/(tBCounter+1) * oldPos[1])
        dotsDict[dotName] = [(x,y), tBCounter+1]

def dartThrowDots(gsMatrix, gsSum, blocksize, wantedNumberOfDots):
    height = len(gsMatrix) 
    width = len(gsMatrix[0]) 
    
    dotsDict = createPointsDictionnary(wantedNumberOfDots)

    currentNumberOfDots = 0
    while currentNumberOfDots < wantedNumberOfDots:
        i = rd.randint(0,height-1)
        j = rd.randint(0,width-1)
        if isHit(gsMatrix, (i,j), gsSum):
            (x,y) = getRandomPosition(blocksize, i, j)
            updateDotPosition(dotsDict, "a"+ str(currentNumberOfDots), (x,y))
            currentNumberOfDots += 1
    return dotsDict

def dartThrowAfterOneUpdate(imageName, blocksize, wantedNumberOfDots):
    rawName = getRawName(imageName)
    dotName = getSvgName(imageName + "Dart")
    resName = getSvgName(imageName + "Res")

    gsMatrix = image2matrix(rawName,blocksize)
    gsSum = getSumGrayScales(gsMatrix)

    dotsDict = dartThrowDots(gsMatrix, gsSum, blocksize, wantedNumberOfDots)

    dotsDict = getRethrownDotsDict(gsMatrix, gsSum, blocksize, dotsDict)

    finalContex = createDotsContext(dotName, imageName, dotsDict, (1,0,0))

    return addContext([finalContex], resName, imageName)

def dartThrowAfterNumbersOfTB(imageName, blocksize, wantedNumberOfDots, numberOfTb):
    rawName = getRawName(imageName)
    dotName = getSvgName(imageName + "Dart")
    updateName = getSvgName(imageName + "Upd")
    resName = getSvgName(imageName + "Res")

    gsMatrix = image2matrix(rawName,blocksize)
    gsSum = getSumGrayScales(gsMatrix)

    dotsDict = dartThrowDots(gsMatrix, gsSum, blocksize, wantedNumberOfDots)
    dartsContex = createDotsContext(dotName, imageName, dotsDict, (0, 1, 0))
    
    for i in range(numberOfTb):
        dotsDict = getRethrownDotsDict(gsMatrix, gsSum, blocksize, dotsDict)

    finalContex = createDotsContext(updateName, imageName, dotsDict, (1, 0, 0))
    #printDico(dotsDict)
    addContext([dartsContex, finalContex], resName, imageName)
    addContext([finalContex], updateName, imageName)
    addContext([dartsContex], dotName, imageName)

    return dotsDict

def distanceMatrix(dotsDict):
    matrix = [ [0 for i in range(len(dotsDict))] for j in range(len(dotsDict))]
    for i in range(len(dotsDict)):
        for j in range(len(dotsDict)):
            a_i = getCoords(dotsDict, "a" + str(i))
            a_j = getCoords(dotsDict, "a" + str(j))
            matrix[i][j] = getDistance(a_i, a_j)
    return matrix

def dotDicts2TupleList(dotsDict):
    res = []
    for dot in dotsDict:
        res.append(getCoords(dotsDict, dot))
    return res

def main(fileName, blocksize, numberOfPoints, numberOfTB, additionName = ""):
    C.createAllDirectories()

    graphCoords = dartThrowAfterNumbersOfTB(fileName, blocksize, numberOfPoints, numberOfTB)
    
    graphMatrix =  distanceMatrix(graphCoords)
    graphCoords = dotDicts2TupleList(graphCoords)
    image =  Image.open(getRawName(fileName)).convert('L')
    width, height = image.size
    allSubTours = [[]]
    cpt = 0
    numberOfSubTours = 0
    
    while numberOfSubTours != 1:
        lpName =  getLpName(fileName + additionName + "_" + str(cpt))
        solName = getSolName(fileName + additionName + "_" + str(cpt))
        logName = getLogName(fileName + additionName + "_" + str(cpt))
        svgName = getSvgName(fileName + additionName + "_" + str(cpt))
        
        copyOfGraphMatrix = [row[:] for row in graphMatrix]

        if os.path.isfile(lpName): os.remove(lpName)
        C.createLPfileGraph(lpName, graphCoords, copyOfGraphMatrix, allSubTours)
        C.subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName ])

        resultGraph = C.solFile2Graph(solName, copyOfGraphMatrix)
        if allSubTours == [[]]: allSubTours = C.get_all_subtours(resultGraph)

        drawing = C.graph2Context(svgName, resultGraph, graphCoords, height, width)
        for subTour in C.get_all_subtours(resultGraph):
            allSubTours.append(subTour)
            
        numberOfSubTours = len(C.get_all_subtours(resultGraph)) 
        cpt += 1
        print("_________________________________")
    return drawing
# ============================== DRAW ==============================

def createDotsContext(resultFileName, imageName, dotsDict, color):
    rawName = getRawName(imageName)

    image =  Image.open(rawName).convert('L')
    width, height = image.size
    destination = cairo.SVGSurface(resultFileName, width, height)
    cr = cairo.Context(destination)
    
    cr.set_source_rgba(color[0],color[1],color[2], 0.5)

    if type(dotsDict) == tuple:
        (x,y) = dotsDict
        cr.move_to(x,y)
        cr.rectangle(x -5.5, y -5.5,5,5)
        cr.fill()
    else:
        coords = getOnlyCoords(dotsDict)
        for i in range(len(coords)):
            (x,y) = coords[i]
            cr.move_to(x,y)
            cr.rectangle(x -2.5, y -2.5,5,5)
            cr.fill()
    
    return cr

def context2png(context, fileName):
    context.get_target().write_to_png(fileName + ".png")

def addContext(crTab, resultFileName, imageName):
    rawName = getRawName(imageName)
    
    image =  Image.open(rawName).convert('L')
    width, height = image.size

    destination = cairo.SVGSurface(resultFileName, width, height)
    resCr = cairo.Context(destination)

    resCr.set_source_rgb(1,1,1)
    resCr.rectangle(0,0, width, height)
    resCr.fill()

    for cr in crTab:
        resCr.set_source_surface(cr.get_target(), 0,0)
        resCr.paint()
    return resCr
 

# ============================== TEST ==============================

# dotsSkull = dartThrowDots("Raw/Skull.jpg", 10, 500)
#  print(image2matrix(skullGSMatrix)
# print(getSumGrayScales(skullGSMatrix))

# both = dartThrowAndTractorBeamTargetDots("Skull", 10, 500)

# dartThrowAfterNumbersOfTB("Skull", 10, 500, 10000)
# dartThrowAfterOneUpdate("Skull", 10, 500)

# main("Skull", 10, 800, 50000, "July13")
# main("Marbrier", 10, 4000, 65000, "essai") # 14:48 fin 17:00. Killed
main("Brassens", 5, 1300, 80000, "essai") # 11:06


