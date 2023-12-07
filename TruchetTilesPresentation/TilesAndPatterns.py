import cairo
import math
import ToolBox as TB


# =============== CODE ===============

# =============== BEGIN : MATH ===============
    
def getMinBrightArea():
    return 1/6 # MINIMUM_BRIGHT_AREA_3P

def getMaxBrightArea():
    return 5/6 #MAXIMUM_BRIGHT_AREA_3P

def optimalCurveParam(grayScale):
    if grayScale < getMinBrightArea():
        return 1      
    if grayScale > getMaxBrightArea():
        return 0
    else:
        return 5/4 - 3/2*grayScale 
# =============== END : MATH ===============

# =============== BEGIN : DRAWINGS ===============

def drawBezier(cr, grayScale):

    cr.scale(TB.PIXEL_SIZE,TB.PIXEL_SIZE)
    cr.set_line_width(0.2)        
    a = optimalCurveParam(grayScale)

    # Background
    cr.set_source_rgb(1,1,1)  # White
    cr.rectangle(0, 0, TB.PIXEL_SIZE, TB.PIXEL_SIZE)
    cr.fill()
    
    cr.set_source_rgb(0, 0, 0) # BLack
    
    # Curve 
    cr.move_to(0, 0)
    cr.curve_to(a, 1 - a, a, 1 - a, 1, 1)
    cr.line_to(0, 1)
    cr.line_to(0,0)
    cr.close_path()
    cr.fill()

    return cr
# =============== END : DRAWINGS ===============

# =============== BEGIN : TILES/PATTERN CREATION/MANIPULATION ===============

def rotateTile(tile, angle):
    tile.move_to(TB.PIXEL_SIZE/2, TB.PIXEL_SIZE/2)
    tile.translate(TB.PIXEL_SIZE/2, TB.PIXEL_SIZE/2)
    tile.rotate(TB.deg2rad(angle))
    tile.translate(-TB.PIXEL_SIZE/2, -TB.PIXEL_SIZE/2)
    return tile
     
def createTile(tileName, grayScale, angle):
    # output: cairo.Context
    resultFileName = TB.get_SVG_TileName(tileName )
    surface = cairo.SVGSurface(resultFileName, TB.PIXEL_SIZE, TB.PIXEL_SIZE)
    cr = cairo.Context(surface)
    return drawBezier(rotateTile(cr, angle), grayScale)

def makeGrayTile(i):    
    resultFileName = TB.get_SVG_TileName("GrayTile_" + str(i) )
    destination = cairo.SVGSurface(resultFileName, TB.PIXEL_SIZE, TB.PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(i,i,i)
    cr.rectangle(0,0,TB.PIXEL_SIZE, TB.PIXEL_SIZE)
    cr.fill()
    return cr

def createPattern(patternName, order, grayScaleOrder ):
    # input : patternName: name for the svg file
    #         order : matrix of letter from 'a' to 'd' describing the pattern  
    # output: cairo.Context
    patternName = TB.getPatternName(patternName)
    height = len(order)
    width = len(order[0])

    destination = cairo.SVGSurface(patternName, width*TB.PIXEL_SIZE, height*TB.PIXEL_SIZE)
    cr = cairo.Context(destination)

    # Background
    cr.set_source_rgb(1,1,1)  # White
    cr.rectangle(0, 0, width*TB.PIXEL_SIZE, height*TB.PIXEL_SIZE)
    cr.fill()

    for i in range(height):
        for j in range(width):
            cr.move_to(0,0)
            
            letter = order[i][j]
            if type(grayScaleOrder) == float:
                gS = grayScaleOrder
            else:
                gS = grayScaleOrder[i][j]
            tile = createTile(letter, gS, TB.letter2Angle(letter))

            cr.set_source_surface(tile.get_target(), j*TB.PIXEL_SIZE, i*TB.PIXEL_SIZE)
            cr.paint()
            
    return cr
# =============== BEGIN : TILES/PATTERN CREATION/MANIPULATION ===============


# =============== TEST ===============
"""
createTile("a.svg", 0.7, 0)
 
TB.context2png(createPattern("ACCA3p", [['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]]), "ACCA3p.png")
TB.context2png(createPattern("ACCAEps",[['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]]), "ACCAEps.png")
TB.context2png(createPattern("CAAC3p", [['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]]), "CAAC3p.png")
TB.context2png(createPattern("CAACEps",[['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]]), "CAACEps.png")
TB.context2png(createPattern("CAAC", [['c','a'],['a','c']], 0.5), "CAAC.png")
TB.context2png(createPattern("72", 
              [
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
                  0.5, drawBezier), "72.png")
"""

# TB.context2png(createPattern("Ds", [['d' for i in range (10)]], [[i / 10 for i in range (10)]], drawBezierEPS), "Ds1.png")
# for i in range (10) :
#     print(optimalCurveParam(i/10, drawBezier))


# TB.context2png(createPattern("Ds", [['d']], [[0.3]], drawBezierEPS), "d03.png")
# print(optimalCurveParam(3/10, drawBezier))
# print("MaxBrightArea:" , (7.65 - getMaxBrightArea(drawBezierEPS) * 6))
# print("MinBrightArea:" , getMinBrightArea(drawBezierEPS))
# TB.context2png(createPattern("Ds", [['d']], [[0.36]], drawBezierEPS), "Ds.png")

createTile("a", 0.7, 0)
 
createPattern("ACCA3p", [['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]])
createPattern("CAAC3p", [['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]])
createPattern("CAAC", [['c','a'],['a','c']], 0.5)
createPattern("72", 
              [
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
                  0.8)