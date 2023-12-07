import TilesAndPatterns as TT
import ToolBox as TB
from PIL import Image
import numpy as np
import cairo

# =============== DATA ===============

BLOCKSIZE = 10

# =============== CODE ===============

def matrix2imageFromExistingPNG(INT_GS_matrix, resultFileName):
    height = len(INT_GS_matrix)
    width =  len(INT_GS_matrix[0])
    
    destination = cairo.SVGSurface(resultFileName, width*TB.PIXEL_SIZE, height*TB.PIXEL_SIZE)
    cr = cairo.Context(destination)

    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0,width*TB.PIXEL_SIZE, height*TB.PIXEL_SIZE)
    cr.fill()              
    for i in range(height):
        for j in range(width):            
            gSindex = INT_GS_matrix[i][j]
            pixel = cairo.create(TB.get_PNG_TileName(str(gSindex)))
            
            cr.set_source_surface(pixel.get_target(), j*TB.PIXEL_SIZE, i*TB.PIXEL_SIZE)
            cr.paint()
                  
    return cr

def imageToGSMatrix(fileName, blockSize, precision = 2):
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
                    mean = mean + arrayIm[blockSize*i + k][blockSize*j + l]
            m[i][j] = round(mean/(blockSize*blockSize), precision)
    image.close()
    return m 

# =============== CODE ===============

def roundUpMatrix( matrix , precision):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            matrix[i][j] = round(matrix[i][j]/255, precision)            
    return matrix

def createBoschImageEasyTab(patternOrder,
                            imageName, 
                            blockSize = 3, 
                            precision = 2, 
                            resultFileName= TB.get_SVG_ResultName("Result")):

    TB.createAllDirectories()
    imageName = TB.getRawName(imageName)
    
    x = imageToGSMatrix(imageName, blockSize, precision)
    matrixGrey = roundUpMatrix(x, precision)
    height = len(matrixGrey)
    width = len(matrixGrey[0])
    patternDim = len(patternOrder)
    
    destination = cairo.SVGSurface(resultFileName, width*TB.PIXEL_SIZE, height*TB.PIXEL_SIZE)
    cr = cairo.Context(destination)

    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0,width*TB.PIXEL_SIZE, height*TB.PIXEL_SIZE)
    cr.fill()
    
    oldTiles = [[ None for i in range( pow(10,precision) +1)] for i in range(4)]
                        
    for i in range(height):
        for j in range(width):

            cr.move_to(0,0)

            rel_i = i % patternDim
            rel_j = j % patternDim
            letter = patternOrder[rel_i][rel_j]
            orientationInd = TB.letter2Angle(letter)//90

            gS = matrixGrey[i][j]
            gSIndex = int(gS * pow(10,precision)) 

            if oldTiles[orientationInd][gSIndex] is None:
                tile = TT.createTile(letter, gS, TB.letter2Angle(letter))
                oldTiles[orientationInd][gSIndex]  = tile

            else:
                tile = oldTiles[orientationInd][gSIndex]
                 
            cr.set_source_surface(tile.get_target(), j*TB.PIXEL_SIZE, i*TB.PIXEL_SIZE)
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

# createBoschImageEasyTab( [['a','c'],['c','a']], "nirvana.jpg",TT.drawBezier3P, blockSize=10, precision=2, resultFileName="Lhasa10.svg")

createBoschImageEasyTab( [['a','c'],['c','a']], 
    "nirvana",
    blockSize=10,
    precision=2)

