from PIL import Image
import numpy as np
import math as math
import cairo
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
    return height//wantedHeight

def makeDomino(n):
    resultFileName = str(n) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(0 , 0 , 0)
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
tabDomino = [makeDomino(i) for i in range(10)]

def makeGrayPixel(i):
    resultFileName = str(i) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(i/10,i/10,i/10)

    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    return cr
tabGrayPixel = [makeGrayPixel(i) for i in range(11)]


def makeSlot(dominoStatus):
        
    resultFileName = dominoStatus + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(1,1,1,)
    cr.set_line_width(0.2)
    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    cr.set_source_rgb(1,0,0)

    cr.scale(PIXEL_SIZE, PIXEL_SIZE)
    
    if dominoStatus == "haut":
        cr.move_to(0,1)
        cr.line_to(0,0)
        cr.line_to(1,0)
        cr.line_to(1,1)
        cr.stroke()

    elif dominoStatus == "bas":
        cr.move_to(0,0)
        cr.line_to(0,1)
        cr.line_to(1,1)
        cr.line_to(1,0)
        cr.stroke()

    elif dominoStatus == "left":
        cr.move_to(1,0)
        cr.line_to(0,0)
        cr.line_to(0,1)
        cr.line_to(1,1)
        cr.stroke()
        
    elif dominoStatus == "right":
        cr.move_to(0,0)
        cr.line_to(1,0)
        cr.line_to(1,1)
        cr.line_to(0,1)
        cr.stroke()
    else: 
        raise Exception ("makeTile issue")
    return cr

tabSlots = {("haut"): makeSlot("haut"),
            ("bas") :  makeSlot("bas"),
            ("left") :  makeSlot("left"),
            ("right") : makeSlot("right"),
            0 : makeGrayPixel(0)}

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
            mean = 0
            for k in range(blocksize):
                for l in range(blocksize):
                    mean = mean + (arrayIm[blocksize*i + k][blocksize*j + l])
            m[i][j] = math.floor(mean/(255*(blocksize**2)) * 10)
    image.close()
    return m

def matrix2imageFromSvgTab(matrix, resultFileName, svgTab):
    height = len(matrix)
    width =  len(matrix[0])
    
    destination = cairo.SVGSurface(resultFileName, width*PIXEL_SIZE, height*PIXEL_SIZE)
    cr = cairo.Context(destination)
                   
    for i in range(height):
        for j in range(width):            
            index = matrix[i][j]
            pixel = svgTab[index]
            
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

def isAdjacent(i,j,k,l):
    return ((i-k) ** 2 == 1 and j == l) or ((j-l) ** 2 == 1 and i == k)

def getAdjacent(i,j, height, width):
    tabCoord = []
    if i > 0 :
       tabCoord.append((i-1,j))
    if i+1 < height:
        tabCoord.append((i+1,j))
    if j > 0 :
       tabCoord.append((i,j-1))
    if j+1 < width:
        tabCoord.append((i,j+1))
    return tabCoord

def getDominoPos(i,j,k,l):
    if isAdjacent(i,j,k,l):
        if (k - i)**2 == 1:
            return "vertical"
        if (l - j)**2 == 1:
            return "horizontal"
    raise Exception("Not Adjacent")

def isStartingPoint(i,j,k,l):
    # starting point if (i,j) is to the left or higher
    if i < k or j < l:
        return True
    
def dp_and_i_j_pos(i,j,k,l):
    dP = getDominoPos(i,j,k,l)
    if dP == "vertical":
        if isStartingPoint(i,j,k,l):
            return "haut"
        else:
            return "bas"
    else:
        if isStartingPoint(i,j,k,l):
            return "left"
        else:
            return "right"

def getContraryPos(pos : str):
    if pos == "haut":
        return "bas"
    if pos == "bas":
        return "haut"
    if pos == "left":
        return "right"
    else:
        return "left"
    
def contrast_i_j_dP(i,j,k,l, gsMatrix):
    return (gsMatrix[i][j] - gsMatrix[k][l])**2

def strTotalCost( height, width, gsMatrix):
    res = ""
    for i in range(height):
        for j in range(width):
            i_j_adjacent = getAdjacent(i,j,height,width)
            for (k,l) in i_j_adjacent:
                scalar = contrast_i_j_dP(i,j, k,l, gsMatrix)
                add = "+ " + str(scalar) + " X_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
                res += add 
    return res[2:]

def strSlotsConstraints(i, j, height, width):
    res = ""
    for (k,l) in getAdjacent(i,j,height,width):
        add = "+ X_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
        res += add  
    res += " = 1"  
    return res[2:]

def strPhysicalConstraints(i, j, k,l):
    res = "X_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l)
    res += " - X_" + str(k) + "_" + str(l) + "_" + str(i) + "_" + str(j) 
    res += " = 0"
    return res

# =============== TEST ===============

# print(getPrimeFactors(5)) 
# printDico(getPossibleDimensions(5))
# print(getClosestDimensions(550,500, getPossibleDimensions(5)))


# cropImage("/home/arthur/Documents/L2/Stage/Chap4/Raw/GOAT.jpg",7)
# bs = getBS("/home/arthur/Documents/L2/Stage/Chap4/Raw/GOATCropped.png", 7)
# context2png(matrix2imageFromSvgTab(image2matrix("/home/arthur/Documents/L2/Stage/Chap4/Raw/GOATCropped.png", bs, 7), "/home/arthur/Documents/L2/Stage/Chap4/Results/GOATTest.svg", tabGrayPixel), "TEst.png")

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

