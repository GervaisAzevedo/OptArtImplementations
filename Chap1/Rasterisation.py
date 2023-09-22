import TruchetTiles as TT
from PIL import Image
import numpy as np
import cairo


def imageToMatrix(fileName, blockSize, precision = 2):
    image =  Image.open(fileName).convert('L')
    arrayIm = np.asarray(image)
    height = image.size[1]  // blockSize
    width = image.size[0]  // blockSize

    m = [[0 for i in range (width)] for j in range (height)]
    height
    for i in range (height):
        for j in range(width):
            mean = 0
            for k in range(blockSize):
                for l in range(blockSize):
                    mean = + arrayIm[blockSize*i + k][blockSize*j + l]
            m[i][j] = round(mean/blockSize*blockSize, precision)
    image.close()
    return m, height, width

# =============== CODE ===============


def roundUpMatrix( matrix , precision):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            matrix[i][j] = round(matrix[i][j]/255, precision)
    return matrix

def letter2Angle(letter):
    d = {'a' : 0, 'b' : 90, 'c' : 180, 'd' : 270}
    return d[letter]


def createTilesHolder(precision, _drawBezierFunc):
    minBrightArea = TT.getMinBrightArea(_drawBezierFunc)
    maxBrightArea = TT.getMaxBrightArea(_drawBezierFunc)
    
    lenTab = pow(10,precision) +1  # longueur max du tableau.
    lenTab = lenTab - int(round(minBrightArea, precision)*(pow(10,precision) ) ) +1
    lenTab = lenTab - int(round(1 - maxBrightArea, precision)*(pow(10,precision) ) ) +1
    lenTab = lenTab*4 # 4 orientation
    return [[ None for i in range(lenTab)] for i in range(4)]

def createBoschImageStrictTab(patternOrder, 
                              image, 
                              _drawBezierFunc,
                              blockSize = 3, 
                              precision = 2, 
                              resultFileName= "Result.svg"
                              ):

    minBrightArea = TT.getMinBrightArea(_drawBezierFunc)
    maxBrightArea = TT.getMaxBrightArea(_drawBezierFunc)

    x = imageToMatrix(image, blockSize, precision)
    matrixGrey = roundUpMatrix(x[0], precision)
    height = x[1]
    width = x[2] 
    patternDim = len(patternOrder)

    destination = cairo.SVGSurface(resultFileName,
                                    width*TT.WIDTH,
                                    height*TT.HEIGHT)
    cr = cairo.Context(destination)
    
    oldTiles = createTilesHolder(precision)
                        
    for i in range(height):
        for j in range(width):

            cr.move_to(0,0)

            rel_i = i % patternDim
            rel_j = j % patternDim
            letter = patternOrder[rel_i][rel_j]
            orientationInd = letter2Angle(letter)//90

            gS = matrixGrey[i][j]
            gSIndex = int(gS * pow(10,precision)) - int(round(minBrightArea,2)*pow(10,precision))

            if gS < minBrightArea and oldTiles[orientationInd][0] != None:
                tile = oldTiles[orientationInd][0]

            elif gS < minBrightArea :
                tile = TT.createTile(letter, gS, letter2Angle(letter), _drawBezierFunc= _drawBezierFunc )
                oldTiles[orientationInd][0] = tile

            elif gS > maxBrightArea and oldTiles[orientationInd][-1] != None:
                tile = oldTiles[orientationInd][-1]

            elif gS > maxBrightArea:
                tile = TT.createTile(letter, gS, letter2Angle(letter), _drawBezierFunc= _drawBezierFunc )
                oldTiles[orientationInd][-1] = tile

            elif oldTiles[orientationInd][gSIndex] is None:              
                tile = TT.createTile(letter, gS, letter2Angle(letter), _drawBezierFunc= _drawBezierFunc )
                oldTiles[orientationInd][gSIndex]  = tile

            else:
                tile = oldTiles[orientationInd][gSIndex]
                 
            cr.set_source_surface(tile.get_target(), j*TT.WIDTH, i*TT.HEIGHT)
            cr.paint()
    return cr

def createBoschImageEasyTab(patternOrder,
                            image, 
                            _drawBezierFunc,
                            blockSize = 3, 
                            precision = 2, 
                            resultFileName= "Result.svg"):

    x = imageToMatrix(image, blockSize, precision)
    matrixGrey = roundUpMatrix(x[0], precision)
    height = x[1]
    width = x[2] 
    patternDim = len(patternOrder)

    destination = cairo.SVGSurface(resultFileName, width*TT.WIDTH, height*TT.HEIGHT)
    cr = cairo.Context(destination)
    
    oldTiles = [[ None for i in range( pow(10,precision) +1)] for i in range(4)]
                        
    for i in range(height):
        for j in range(width):

            cr.move_to(0,0)

            rel_i = i % patternDim
            rel_j = j % patternDim
            letter = patternOrder[rel_i][rel_j]
            orientationInd = letter2Angle(letter)//90

            gS = matrixGrey[i][j]
            gSIndex = int(gS * pow(10,precision)) 

            if oldTiles[orientationInd][gSIndex] is None:
                tile = TT.createTile(letter, gS, letter2Angle(letter), _drawBezierFunc= _drawBezierFunc )
                oldTiles[orientationInd][gSIndex]  = tile

            else:
                tile = oldTiles[orientationInd][gSIndex]
                 
            cr.set_source_surface(tile.get_target(), j*TT.WIDTH, i*TT.HEIGHT)
            cr.paint()
    return cr



# =============== TEST ===============

"""

createBoschImageEasyTab( [['a','c'],['c','a']], "Lhasa.jpg", TT.drawBezier3P , precision=2, blockSize=8, resultFileName="3pLhasaBS8")
createBoschImageEasyTab( [['a','c'],['c','a']], "Lhasa.jpg", TT.drawBezierEPS , precision=2, blockSize=8, resultFileName="EpsLhasaBS8")

createBoschImageEasyTab( [['a','c'],['c','a']], "SOADhighquality.jpg", TT.drawBezierEPS, precision=3, blockSize=5, resultFileName="EpsPrec3BS5ACCA")
createBoschImageEasyTab( [
                ['b', 'd', 'd', 'b', 'd', 'd', 'a', 'a', 'c', 'a', 'a', 'c'],
                ['d', 'b', 'd', 'd', 'b', 'd', 'a', 'c', 'a', 'a', 'c', 'a'],
                ['d', 'd', 'b', 'd', 'd', 'b', 'c', 'a', 'a', 'c', 'a', 'a'],
                ['b', 'd', 'd', 'b', 'd', 'd', 'a', 'a', 'c', 'a', 'a', 'c'],
                ['d', 'b', 'd', 'd', 'b', 'd', 'a', 'c', 'a', 'a', 'c', 'a'],
                ['d', 'd', 'b', 'd', 'd', 'b', 'c', 'a', 'a', 'c', 'a', 'a'],
                ['c', 'c', 'a', 'c', 'c', 'a', 'd', 'b', 'b', 'd', 'b', 'b'],
                ['c', 'a', 'c', 'c', 'a', 'c', 'b', 'd', 'b', 'b', 'd', 'b'],
                ['a', 'c', 'c', 'a', 'c', 'c', 'b', 'b', 'd', 'b', 'b', 'd'],
                ['c', 'c', 'a', 'c', 'c', 'a', 'd', 'b', 'b', 'd', 'b', 'b'],
                ['c', 'a', 'c', 'c', 'a', 'c', 'b', 'd', 'b', 'b', 'd', 'b'],
                ['a', 'c', 'c', 'a', 'c', 'c', 'b', 'b', 'd', 'b', 'b', 'd']                  
                  ], 
                   "SOADhighquality.jpg",
                   TT.drawBezierEPS, precision=3, blockSize=5, resultFileName="EpsPrec3BS572")
"""

"""
createBoschImageEasyTab( [['a','c'],['c','a']], "David.jpg", blockSize=3, resultFileName="Easy.svg")


createBoschImageEasyTab( [
                ['b', 'd', 'd', 'b', 'd', 'd', 'a', 'a', 'c', 'a', 'a', 'c'],
                ['d', 'b', 'd', 'd', 'b', 'd', 'a', 'c', 'a', 'a', 'c', 'a'],
                ['d', 'd', 'b', 'd', 'd', 'b', 'c', 'a', 'a', 'c', 'a', 'a'],
                ['b', 'd', 'd', 'b', 'd', 'd', 'a', 'a', 'c', 'a', 'a', 'c'],
                ['d', 'b', 'd', 'd', 'b', 'd', 'a', 'c', 'a', 'a', 'c', 'a'],
                ['d', 'd', 'b', 'd', 'd', 'b', 'c', 'a', 'a', 'c', 'a', 'a'],
                ['c', 'c', 'a', 'c', 'c', 'a', 'd', 'b', 'b', 'd', 'b', 'b'],
                ['c', 'a', 'c', 'c', 'a', 'c', 'b', 'd', 'b', 'b', 'd', 'b'],
                ['a', 'c', 'c', 'a', 'c', 'c', 'b', 'b', 'd', 'b', 'b', 'd'],
                ['c', 'c', 'a', 'c', 'c', 'a', 'd', 'b', 'b', 'd', 'b', 'b'],
                ['c', 'a', 'c', 'c', 'a', 'c', 'b', 'd', 'b', 'b', 'd', 'b'],
                ['a', 'c', 'c', 'a', 'c', 'c', 'b', 'b', 'd', 'b', 'b', 'd']                  
                  ], "GOAT.jpg", TT.drawBezier3P,  blockSize=2, precision=4, resultFileName="GOAT3P.svg")
createBoschImageEasyTab( [
                ['b', 'd', 'd', 'b', 'd', 'd', 'a', 'a', 'c', 'a', 'a', 'c'],
                ['d', 'b', 'd', 'd', 'b', 'd', 'a', 'c', 'a', 'a', 'c', 'a'],
                ['d', 'd', 'b', 'd', 'd', 'b', 'c', 'a', 'a', 'c', 'a', 'a'],
                ['b', 'd', 'd', 'b', 'd', 'd', 'a', 'a', 'c', 'a', 'a', 'c'],
                ['d', 'b', 'd', 'd', 'b', 'd', 'a', 'c', 'a', 'a', 'c', 'a'],
                ['d', 'd', 'b', 'd', 'd', 'b', 'c', 'a', 'a', 'c', 'a', 'a'],
                ['c', 'c', 'a', 'c', 'c', 'a', 'd', 'b', 'b', 'd', 'b', 'b'],
                ['c', 'a', 'c', 'c', 'a', 'c', 'b', 'd', 'b', 'b', 'd', 'b'],
                ['a', 'c', 'c', 'a', 'c', 'c', 'b', 'b', 'd', 'b', 'b', 'd'],
                ['c', 'c', 'a', 'c', 'c', 'a', 'd', 'b', 'b', 'd', 'b', 'b'],
                ['c', 'a', 'c', 'c', 'a', 'c', 'b', 'd', 'b', 'b', 'd', 'b'],
                ['a', 'c', 'c', 'a', 'c', 'c', 'b', 'b', 'd', 'b', 'b', 'd']                  
                  ], "GOAT.jpg", TT.drawBezierEPS, blockSize=2,precision=4, resultFileName="GOATEPS.svg")

"""

# createBoschImageEasyTab( [['a','c'],['c','a']], "GreatDepression.jpg",TT.drawBezier3P, blockSize=15, precision=2, resultFileName="GreatDep15.svg")
