from PIL import Image
import numpy as np
import math as math
import cairo
import random as rd
import itertools as iter

# =============== DATA ===============

PIXEL_SIZE = 10
DOMINO_SET_SIZE = 55
NUMBER_OF_SHADES = 10


# =============== CODE ===============
def printDico(dico):
    for e in dico:
        print(e, ":", dico[e])

def isPrime(n):
    if n < 2:
        return False
    d = 2
    while d**2 <= n:
        if n % d == 0:
            return False
        d = d + 1
    return True
tabIsPrime = [ i for i in range(55*5) if isPrime(i)]

def getDominoName(x,y):
    return(min(x,y), max(x,y))

def getRatio(height, width):
    return height/width

def getPrimeFactors(n):
    factors = []
    f = 2
    stop = n 
    while f <= stop**2:
        while n % f == 0 and f in tabIsPrime:
            n = n // f
            factors.append(f)
        f = f + 1
    return factors
    
def getComplementary(list, subList):
    res = []
    temp = subList.copy()

    for e in list:
        if e not in temp:
            res.append(e)
        else: 
            temp.remove(e)

    return res

def multiProduct(list):
    res = 1
    for e in list:
        res = res * e
    return res

def getPossibleDimensions(n: int):
    dim = {}
    n = n * DOMINO_SET_SIZE * 2
    factors = getPrimeFactors(n)
    
    h_factors = []
    w_factors = []
    pairing = {}

    for i in range (len(factors)+1):
        h_factors += iter.combinations(factors, i)

    for i in range(len(h_factors)):
        h_factors[i] = list(h_factors[i])
        w_factors.append(getComplementary(factors, h_factors[i]))
        
        h_factors[i] = multiProduct(h_factors[i])
        w_factors[i] = multiProduct(w_factors[i])
        pairing[h_factors[i]] = w_factors[i]
    
    return pairing

def getClosestDimensions(height, width, options):
    idealRatio = height/width    # convert to a ratio
    optimalPossibleRatio = math.inf
    optHW = (math.inf, math.inf)   
    for possHeight in options:
        possWidth = options[possHeight]
        possRatio = possHeight/possWidth
        if (possRatio - idealRatio) ** 2 < (optimalPossibleRatio - idealRatio) ** 2:
            optimalPossibleRatio = possRatio
            
            if (height - possHeight) ** 2 < (height - possWidth) ** 2:
                optHW = (possHeight, possWidth)
            else:
                optHW = (possWidth, possHeight)
    return optHW

# =============== RASTERIZE ===============

def cropImage(originalFileName, numberOfSets):

    outputName = originalFileName[:originalFileName.find('.')] + "Cropped.png"

    im = Image.open(originalFileName)
    width, height = im.size
    blocksize = getBS(originalFileName, numberOfSets)
    wantedDimensions = getClosestDimensions(height, width, getPossibleDimensions(numberOfSets))   # height, width
    wantedHeight, wantedWidth  = wantedDimensions


    heightOffset = (height - wantedHeight * blocksize) // 2
    widthOffset = (width - wantedWidth * blocksize) // 2
    decHeight = height - (height - wantedHeight * blocksize)
    decWidth = width - (width - wantedWidth * blocksize) 

    im1 = im.crop(( widthOffset, heightOffset , decWidth + widthOffset , decHeight + heightOffset))
    im1 = im1.save(outputName)
    return im1

def getBS(imageName: str, numberOfSets: int):
    image = Image.open(imageName)

    width, height = image.size    
    
    wantedDimensions = getClosestDimensions(height, width, getPossibleDimensions(numberOfSets))   # height, width
    wantedHeight, wantedWidth = wantedDimensions

    # print("getBS(",numberOfSets,") : wantedHeight,= ", wantedHeight)
    # print("            : wantedWidth,= ", wantedWidth)
    # print("height//wantedHeight :", height//wantedHeight)
    # print("width//wantedWidth :", width//wantedWidth)
    
    return height//wantedHeight

def makeTile(n):
    resultFileName = str(n) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(0.2 , 0.2 , 0.2)
    cr.set_line_width(0.025)
    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    cr.set_source_rgb(1,1,1)

    cr.scale(PIXEL_SIZE, PIXEL_SIZE)
    
    if n % 2 == 1 :     # i est imapir
        cr.arc(0.5, 0.5, 0.075, 0, 2 * math.pi)
        cr.close_path()
        cr.fill()
        n = n - 1       # i est maitenant pair

    if n == 8:
        cr.arc(0.5, 0.8, 0.075, 0, 2 * math.pi)
        cr.arc(0.5, 0.2, 0.075, 0, 2 * math.pi)
        cr.close_path()
        cr.fill()
        n = 6

    if n == 6:
        cr.arc(0.8, 0.5, 0.075, 0, 2 * math.pi)
        cr.arc(0.2, 0.5, 0.075, 0, 2 * math.pi)
        cr.close_path()
        cr.fill()
        n = 4
    
    if n == 4:
        cr.arc(0.2, 0.2, 0.075, 0, 2 * math.pi)
        cr.arc(0.8, 0.8, 0.075, 0, 2 * math.pi)
        cr.close_path()
        cr.fill()
        n = 2

    if n == 2 :
        cr.arc(0.2, 0.8, 0.075, 0, 2 * math.pi)
        cr.arc(0.8, 0.2, 0.075, 0, 2 * math.pi)
        cr.close_path()
        cr.fill()

    return cr
tabImage = [makeTile(i) for i in range(10)]

"""
def create(i):
    resultFileName = str(i) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(i/10,i/10,i/10)

    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    return cr
tabImage = [create(i) for i in range(10)]
"""
def context2png(context, pngName):
    context.get_target().write_to_png(pngName)

def image2matrix(fileName, blocksize, numberOfSets):
    fileName = fileName[:fileName.find('.')] + ".png"

    image =  Image.open(fileName).convert('L')
    width, height = image.size

    wantedDimensions = getClosestDimensions(height, width, getPossibleDimensions(numberOfSets))   # height, width
    wantedHeight, wantedWidth = wantedDimensions
    arrayIm = np.asarray(image)    

    m = [[0 for j in range (wantedWidth)] for i in range (wantedHeight)]

    
    for i in range (wantedHeight):
        for j in range(wantedWidth):
            sum = 0

            for k in range(blocksize):
                for l in range(blocksize):
                    sum += arrayIm[blocksize*i + k][blocksize*j + l]/255
            m[i][j] = math.floor((NUMBER_OF_SHADES-1) * sum/((blocksize**2)))
    image.close()
    return m


def matrix2imageFromExistingSVG(matrix, resultFileName):
    height = len(matrix)
    width =  len(matrix[0])
    
    destination = cairo.SVGSurface(resultFileName, width*PIXEL_SIZE, height*PIXEL_SIZE)
    cr = cairo.Context(destination)
                   
    for i in range(height):
        for j in range(width):            
            gSindex = matrix[i][j]
            pixel = tabImage[gSindex]
            
            cr.set_source_surface(pixel.get_target(), j*PIXEL_SIZE, i*PIXEL_SIZE)
            cr.paint()
            
    return cr

def getNbLines(imageName, blocksize):
    im = Image.open(imageName)
    width, height = im.size    
    return height//blocksize

def getNbCollums(imageName, blocksize):
    im = Image.open(imageName)
    width, height = im.size    
    return width//blocksize

# =============== LINEAR PROBLEM ===============

def cost_m_n_i_j_o(m,n,i,j, orientation, gsMatrix, dominoPositioning):
    if (dominoPositioning == "vertical" and i%2 == 0) :
        if i+1 >= len(gsMatrix):
            raise Exception("i+1 out of Bounds:", i+1, " > ", len(gsMatrix))
        if orientation == 0:
            return (m - gsMatrix[i][j])**2 + (n - gsMatrix[i+1][j])**2
        else :
            return (n - gsMatrix[i][j])**2 + (m - gsMatrix[i+1][j])**2

    if (dominoPositioning == "horizontal" and j%2 == 0):
        if j+1 >= len(gsMatrix[0]):
            raise Exception("j+1 out of Bounds:", j+1, " > ", len(gsMatrix[0]))
        if orientation == 0:
            return (m - gsMatrix[i][j])**2 + (n - gsMatrix[i][j+1])**2
        else :
            return (n - gsMatrix[i][j])**2 + (m - gsMatrix[i][j+1])**2

    return 0

def strTotalCost( height, width, gsMatrix, dominoPositioning):
    res = ""
    for orientation in range(2):
        for m in range(NUMBER_OF_SHADES):
            for n in range(m, NUMBER_OF_SHADES):
                for i in range(height):
                    for j in range(width):
                        scalar = cost_m_n_i_j_o(m,n,i,j, orientation , gsMatrix, dominoPositioning)
                        if orientation == 0:
                            add = "+ " + str(scalar) + " X" + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) 
                        else :
                            add = "+ " + str(scalar) + " X" + "_" + str(n) + "_" + str(m) + "_" + str(i) + "_" + str(j) 
                        res += add 
    return res[2:]

def strSlotsConstraints(i, j, dominoPositioning):
    res = ""
    if (dominoPositioning == "vertical" and i%2 == 0) or (dominoPositioning == "horizontal" and j%2 == 0):
        scalar = 1
    else : 
        scalar = 0
    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            add = " + " + str(scalar) + " X"  + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) 
            res += add
    res = res[2:]
    res = res + " = " + str(scalar) 
    
    return res

def strDominoConstraints(m , n, height, width, numberOfSets):
    res = ""
    for i in range(height):
        for j in range(width):
            add = " + X" + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) 
            res += add
    res = res[2:]
    res = res + " = " + str(numberOfSets)
    return res

# =============== TEST ===============

# print(getPrimeFactors(5)) 
# printDico(getPossibleDimensions(5))
# print(getClosestDimensions(550,500, getPossibleDimensions(5)))


# cropImage("/home/arthur/Documents/L2/Stage/Chap4/Raw/GOAT.jpg",3)
# bs = getBS("/home/arthur/Documents/L2/Stage/Chap4/Raw/GOATCropped.png", 3)
# matrix2imageFromExistingSVG(image2matrix("/home/arthur/Documents/L2/Stage/Chap4/Raw/GOATCropped.png", bs, 3), "/home/arthur/Documents/L2/Stage/Chap4/Results/GOATTest.svg")

# cropImage("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOAD.jpg",5)
# bs = getBS("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOADCropped.png", 5)
# matrix2imageFromExistingSVG(image2matrix("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOADCropped.png", bs, 5), "/home/arthur/Documents/L2/Stage/Chap4/Results/SOAD5sets.svg")
# 
# cropImage("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOAD.jpg",7)
# bs = getBS("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOADCropped.png", 7)
# matrix2imageFromExistingSVG(image2matrix("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOADCropped.png", bs, 7), "/home/arthur/Documents/L2/Stage/Chap4/Results/SOAD7sets.svg")

# cropImage("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOAD.jpg",15)
# bs = getBS("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOADCropped.png", 15)
# matrix2imageFromExistingSVG(image2matrix("/home/arthur/Documents/L2/Stage/Chap4/Raw/SOADCropped.png", bs, 15), "/home/arthur/Documents/L2/Stage/Chap4/Results/SOAD7sets.svg")