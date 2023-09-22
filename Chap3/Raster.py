from PIL import Image
import numpy as np
import math as math
import cairo
import random as rd

# =============== DATA ===============

PIXEL_SIZE = 10
NUMBER_OF_SVG = 10
BLOCKSIZE = 10


# =============== CODE ===============


    
def create(i):
    resultFileName = str(i) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(i/10,i/10,i/10)

    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    return cr

def makeTile(i):
    i = 10-i
    resultFileName = str(1) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(1,1,1)
    cr.set_line_width(0.025)
    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    cr.set_source_rgb(0,0,0)

    cr.scale(PIXEL_SIZE, PIXEL_SIZE)

    for k in range(i):

        a = rd.random()
        b = rd.random()

        x = rd.random()*a
        y = rd.random()*b
        cr.curve_to(0.5, 0, x, y, a, b)
        x = rd.random()
        y = rd.random()
        cr.curve_to(a,b, x, y, 0.5, 1)
        cr.stroke()

        a = rd.random()
        b = rd.random()

        x = rd.random()*a
        y = rd.random()*b
        cr.curve_to(0, 0.5, x, y, a,b)
        x = rd.random()
        y = rd.random()
        cr.curve_to(a,b, x, y, 1, 0.5)
        cr.stroke()

    return cr

tabImage = [create(i) for i in range (NUMBER_OF_SVG)]
# tabImage = [makeTile(i) for i in range (NUMBER_OF_SVG)]


# =============== RASTERIZE ===============

def cropImage(input, blocksize):
    output = input[:input.rfind('.')] + "Cropped.png"
    print("_____________________ input:     ", input)
    im = Image.open(input)
    width, height = im.size
    decHeight = height - (height % blocksize)
    decWidth = width - (width % blocksize)
    im1 = im.crop((0, 0, decWidth, decHeight))
    im1 = im1.save(output)
    return im1


def context2png(context, pngName):
    context.get_target().write_to_png(pngName)

def image2matrix(fileName, blocksize):
    fileNameCropped = fileName[:fileName.rfind('.')] + "Cropped.png"
    fileName = fileName[:fileName.rfind('.')] + ".png"

    print("_____________________ fNCropped: ", fileNameCropped)
    print("_____________________ fileName:  ", fileName)

    cropImage(fileName, blocksize)

    image = Image.open(fileNameCropped).convert('L')


    arrayIm = np.asarray(image)
    height = getHeight(fileName, blocksize)
    width = getWidth(fileName, blocksize)

    m = [[0 for j in range (width)] for i in range (height)]
    
    for i in range (height):
        for j in range(width):
            sum = 0

            for k in range(blocksize):
                for l in range(blocksize):
                    sum += arrayIm[blocksize*i + k][blocksize*j + l]/255
            m[i][j] = math.floor((NUMBER_OF_SVG-1) * sum / (blocksize*blocksize))
    image.close()
    return m

def getHeight(image, blocksize):
    # Height in mega pixel
    im = Image.open(image)
    height = im.size[1]
    height = height // blocksize
    return height

def getWidth(image, blocksize):
    # Height in mega pixel
    im = Image.open(image)
    width = im.size[0]
    width = width // blocksize
    return width

def matrix2imageFromGSMatrix(image, blocksize, resultFileName= "Chap3.svg"):

    x = image2matrix(image, blocksize)
    m = x
    height = len(x)
    width = len(x[0] )
    
    destination = cairo.SVGSurface(resultFileName, width*PIXEL_SIZE, height*PIXEL_SIZE)
    cr = cairo.Context(destination)
                   
    for i in range(height):
        for j in range(width):

            cr.move_to(0,0)
            gS = m[i][j]
            cr.set_source_rgb(gS, gS, gS)  # White
            cr.rectangle(j*PIXEL_SIZE, i*PIXEL_SIZE,PIXEL_SIZE,PIXEL_SIZE)
            cr.fill()

            cr.set_source_rgb(1,0.5,0)  # White
            cr.set_line_width(0.04)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(40)
            cr.move_to( j*PIXEL_SIZE + 12, i*PIXEL_SIZE + 40 )
            cr.show_text(str(math.floor(gS*10)))
            cr.fill()
    return cr

def matrix2imageFromExistingSVG(matrix, resultFileName= "Chap3.svg"):
    height = len(matrix)
    width =  len(matrix[0])
    
    destination = cairo.SVGSurface(resultFileName, width*PIXEL_SIZE, height*PIXEL_SIZE)
    cr = cairo.Context(destination)

    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0,width*PIXEL_SIZE, height*PIXEL_SIZE)
    cr.fill()

                   
    for i in range(height):
        for j in range(width):            
            gSindex = matrix[i][j]
            pixel = tabImage[gSindex]
            
            """
            # show grayScale Numbers
            cr.set_source_rgb(1,0.5,0)  # White
            cr.set_line_width(0.04)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(10)
            cr.move_to( j*PIXEL_SIZE , i*PIXEL_SIZE )
            cr.show_text(str(gSindex))
            cr.fill()
"""
            cr.set_source_surface(pixel.get_target(), j*PIXEL_SIZE, i*PIXEL_SIZE)
            cr.paint()
            
            
            
    return cr

# =============== LINEAR PROBLEM ===============

def numberOfUsesPerSVG(width, height):
    res = height*width / NUMBER_OF_SVG
    return int(res)

def strTotalCost( height, width, gsMatrix):
    res = ""
    for c in range(NUMBER_OF_SVG):
        for i in range(height):
            for j in range(width):
                gSindex = gsMatrix[i][j]
                scalar = pow(c-gSindex, 2)
                add = "+ " + str(scalar) + " X" + "_"+ str(c) + "_" + str(i) + "_" + str(j) 
                res += add
    return res[2:]

def strBlockConstraints(i, j):
    res = ""
    for c in range(NUMBER_OF_SVG):
        add = " + X" + "_" + str(c) + "_" + str(i) + "_" + str(j) 
        res += add
    res = res[2:]
    res = res + " = 1"
    return res

def strTypeCConstraints(c, height, width):
    res = ""
    for i in range(height):
        for j in range(width):
            add = " + X" + "_" + str(c) + "_" + str(i) + "_" + str(j) 
            res += add
    return res[2:] + " = " + str(numberOfUsesPerSVG( width, height))


# =============== TEST ===============

# marbrierMatrix = getSVGIndexMatrix("/home/arthur/Documents/L2/Stage/Chap3/Raw/Marbrier.jpg", 20)
# context2png(matrix2imageFromExistingSVG(marbrierMatrix, "RasterMarbrier.svg"),"MarbrierRaster.jpg")


# depMatrix = image2matrix("/home/arthur/Documents/L2/Stage/Chap3/Raw/GreatDepression.jpg", 15)
# context2png(matrix2imageFromExistingSVG(depMatrix, "GreatDepressionRaster.svg"),"GreatDepressionRaster.jpg")

depMatrix = image2matrix("/home/arthur/Documents/L2/Stage/Chap3/Raw/nirvana.jpg", 15)
context2png(matrix2imageFromExistingSVG(depMatrix, "nirvana.svg"),"nirvana.jpg")
