import cairo
import math

# =============== DATA ===============
EPS = 0.01
WIDTH = 50
HEIGHT = 50
d = {'a' : 0, 'b' : 90, 'c' : 180, 'd' : 270}

# =============== CODE ===============


def context2png(context, pngName):
    context.get_target().write_to_png(pngName)


def getMinBrightArea(_drawBezierFunc):
    if _drawBezierFunc == drawBezierEPS: return (( (8/3) * EPS + (7/3)) ** 2 - (1519/288) + (145/6) * EPS ** 3 - (62/9) * EPS ** 2 - (182/9)  * EPS) / 8 # MINIMUM_BRIGHT_AREA_EPS
    if _drawBezierFunc == drawBezier3P: return 1/6 # MINIMUM_BRIGHT_AREA_3P

def getMaxBrightArea(_drawBezierFunc):
    if _drawBezierFunc == drawBezierEPS: return (( (8/3) * EPS + 1 + (7/3)) ** 2 - (1519/288) + (145/6) * EPS ** 3 - (62/9) * EPS ** 2 - (182/9)  * EPS) / 8 # MAXIMUM_BRIGHT_AREA_EPS
    if _drawBezierFunc == drawBezier3P: return 5/6 #MAXIMUM_BRIGHT_AREA_3P

def context2png(context, pngName):
    context.get_target().write_to_png(pngName)

def optimalCurveParam(grayScale, _drawBezierFunc):
    if grayScale < getMinBrightArea(_drawBezierFunc):
        return 1      
    if grayScale > getMaxBrightArea(_drawBezierFunc):
        return 0
    else:
        if _drawBezierFunc == drawBezier3P:
            return 5/4 - 3/2*grayScale 
        if _drawBezierFunc == drawBezierEPS: 
            return 1- (math.sqrt( 8*grayScale + (1519/288) - (145/6) * (EPS)**3 + (62/9) * (EPS)**2 + (182/9) * (EPS)) - (8/3) * (EPS) - (7/3) )
   
def drawBezier3P(cr, grayScale):

    cr.scale(WIDTH, HEIGHT)
    cr.set_line_width(0.2)        
    a = optimalCurveParam(grayScale, drawBezier3P)

    # Background
    cr.set_source_rgb(1,1,1)  # White
    cr.rectangle(0, 0, WIDTH, HEIGHT)
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

def BezierCurveEPS(t,a):
    r1 =(6*a - 3)*t**4 +(-12*a + 8*EPS + 4)*t**3 + (6*a-12*EPS)*t**2 + 4*EPS*t
    r2 =(3 - 6*a)*t**4 +(12*a + 8*EPS -8)*t**3 + (6-6*a-12*EPS)*t**2 + 4*EPS*t

    return(r1, r2) 

def drawBezierEPS(cr, grayScale):

    cr.scale(WIDTH, HEIGHT)
    cr.set_line_width(0.2)        
    a = optimalCurveParam(grayScale, drawBezierEPS)

    # Background
    cr.set_source_rgb(1,1,1)  # White
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()
    
    cr.set_source_rgb(0, 0, 0) # BLack
    
    # Curve 
    t = 0
    points = []
    while t < 1:
        x,y = BezierCurveEPS(t,a)[0], BezierCurveEPS(t,a)[1]
        points.append((x , y))
        t += 0.1
    
    cr.move_to(0,0)
    for p in points[1:]:
        cr.line_to(p[0],p[1])
    cr.line_to(0, 1)
    cr.line_to(0,0)
    cr.close_path()
    cr.fill()

    return cr

def rotateTile(tile, angle):
    tile.move_to(WIDTH/2, HEIGHT/2)
    tile.translate(WIDTH/2, HEIGHT/2)
    tile.rotate(deg2rad(angle))
    tile.translate(-WIDTH/2, -HEIGHT/2)
    return tile

def deg2rad(angle):
    return angle * math.pi/180.0
     
def createTile(tileName, grayScale, angle, _drawBezierFunc = BezierCurveEPS):
    # output: cairo.Context
    surface = cairo.SVGSurface(tileName, WIDTH, HEIGHT)
    cr = cairo.Context(surface)
    return _drawBezierFunc(rotateTile(cr, angle), grayScale)

def createPattern(patternName, order, grayScaleOrder, _drawBezierFunc ):
    # input : patternName: name for the svg file
    #         order : matrix of letter from 'a' to 'd' describing the pattern  
    # output: cairo.Context
    height = len(order)
    width = len(order[0])

    destination = cairo.SVGSurface(patternName, width*WIDTH, height*HEIGHT)
    cr = cairo.Context(destination)

    # Background
    cr.set_source_rgb(1,1,1)  # White
    cr.rectangle(0, 0, width*WIDTH, height*HEIGHT)
    cr.fill()

    for i in range(height):
        for j in range(width):
            cr.move_to(0,0)
            
            letter = order[i][j]
            if type(grayScaleOrder) == float:
                gS = grayScaleOrder
            else:
                gS = grayScaleOrder[i][j]
            tile = createTile(letter, gS, d[letter], _drawBezierFunc )

            cr.set_source_surface(tile.get_target(), j*WIDTH, i*HEIGHT)
            cr.paint()
            
    return cr

# =============== TEST ===============
"""
createTile("a.svg", 0.7, 0)
 
context2png(createPattern("ACCA3p", [['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]], drawBezier3P), "ACCA3p.png")
context2png(createPattern("ACCAEps",[['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]], drawBezierEPS), "ACCAEps.png")
context2png(createPattern("CAAC3p", [['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]], drawBezier3P), "CAAC3p.png")
context2png(createPattern("CAACEps",[['c','a'],['a','c']], [[0.8,0.6],[0.2,0.4]], drawBezierEPS), "CAACEps.png")
context2png(createPattern("CAAC", [['c','a'],['a','c']], 0.5, drawBezier3P), "CAAC.png")
context2png(createPattern("72", 
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
                  0.5, drawBezier3P), "72.png")
"""

# context2png(createPattern("Ds", [['d' for i in range (10)]], [[i / 10 for i in range (10)]], drawBezierEPS), "Ds1.png")
# for i in range (10) :
#     print(optimalCurveParam(i/10, drawBezier3P))


# context2png(createPattern("Ds", [['d']], [[0.3]], drawBezierEPS), "d03.png")
# print(optimalCurveParam(3/10, drawBezier3P))
# print("MaxBrightArea:" , (7.65 - getMaxBrightArea(drawBezierEPS) * 6))
# print("MinBrightArea:" , getMinBrightArea(drawBezierEPS))
# context2png(createPattern("Ds", [['d']], [[0.36]], drawBezierEPS), "Ds.png")
