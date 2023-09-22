import math 
import numpy as np
from PIL import Image
import subprocess
import os.path
import cairo
import itertools as iter



# ============================== DATA ==============================

PIXEL_SIZE = 100
NUMBER_OF_SHADES = 10
DOMINO_SET_SIZE = 55
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]

# ============================== CODE ==============================

# =============== ENVIRONNEMENT MANAGING ===============

def createDirectory(dirName):
    parentPath = os.getcwd()
    path = os.path.join(parentPath, dirName)
    if not os.path.isdir(path):
        os.mkdir(path)
def createAllDirectories():
    createDirectory("Raw")    
    createDirectory("LPFiles")    
    createDirectory("SolFiles") 
    createDirectory("LogFiles")    
    createDirectory("Results")    

# =============== BASIC FUNCTIONS ===============
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

def productOverList(list):
    res = 1
    for e in list:
        res = res * e
    return res

def removeKeyValueDuplicate(dico):
    tabKey = []
    for key in dico:
        if dico[key] in dico.keys() and dico[dico[key]] == key and dico[key] not in tabKey:
            tabKey.append(key)
    for key in tabKey : del dico[key]

# =============== GETS ===============

def getRawName(fileName):
    path = os.getcwd()
    return path + "/Raw/" + fileName + ".jpg"
def getCroppedName(fileName):
    path = os.getcwd()
    return path + "/Raw/" + fileName + "Cropped.jpg"
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
        
        h_factors[i] = productOverList(h_factors[i])
        w_factors[i] = productOverList(w_factors[i])
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

def getBS(imageName: str, numberOfSets: int):
    image = Image.open(imageName)

    width, height = image.size    
    
    wantedDimensions = getClosestDimensions(height, width, getPossibleDimensions(numberOfSets))   # height, width
    wantedHeight, wantedWidth = wantedDimensions   
    return height//wantedHeight

def getNbLines(imageName, blocksize):
    im = Image.open(imageName)
    width, height = im.size    
    return height//blocksize

def getNbCollums(imageName, blocksize):
    im = Image.open(imageName)
    width, height = im.size    
    return width//blocksize

def getAllSlots(solFileName: str):
    pairs = {}
    with open(solFileName) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    i,j,k,l = get_i_j_k_l_from_var(var)
                    pairs[(i,j)] = (k,l)
            cpt += 1 
    removeKeyValueDuplicate(pairs)
    return pairs

def get_m_n_i_j_k_l_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    m = coords[0]
    n = coords[1]
    i = coords[2]
    j = coords[3]
    k = coords[4]
    l = coords[5]
    return int(m), int(n), int(i), int(j), int(k), int(l)

def get_i_j_k_l_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    i = coords[0]
    j = coords[1]
    k = coords[2]
    l = coords[3]
    return int(i),int(j),int(k),int(l)

def get_cost_m_n_i_j_k_l(m, n, i, j, k, l, gsMatrix):
    return (m - gsMatrix[i][j])**2 + (n - gsMatrix[k][l])**2

# =============== RASTERIZATION ===============

def cropImage(originalFileName, numberOfSets):

    outputName = originalFileName[:originalFileName.find('.')] + "Cropped.jpg"

    im =  Image.open(originalFileName).convert('RGB')
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

def image2matrix(fileName, blocksize, numberOfSets):
    fileName = fileName[:fileName.find('.')] + ".jpg"

    image =  Image.open(fileName).convert('RGB')
    
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

# =============== DRAWINGS ===============

def addContext(cr1,cr2, matrix, resultFileName):
    height = len(matrix)
    width = len(matrix[0])
    
    destination = cairo.SVGSurface(resultFileName + "Together", width*PIXEL_SIZE, height*PIXEL_SIZE)
    resCr = cairo.Context(destination)
    resCr.set_source_surface(cr1.get_target(), 0,0)
    resCr.paint()
    resCr.set_source_surface(cr2.get_target(), 0,0)
    resCr.paint()
    return resCr
 
def makeDomino(n):
    path = "/home/arthur/Documents/L2/Stage/Tiles/"
    resultFileName = path + str(n) + ".svg"
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
tabDomino = [makeDomino(i) for i in range(10)]

def makeGrayPixel(n):
    path = "/home/arthur/Documents/L2/Stage/Tiles/"
    resultFileName = path + str(n) + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_source_rgb(n/10,n/10,n/10)

    cr.rectangle(0,0,PIXEL_SIZE, PIXEL_SIZE)
    cr.fill()

    return cr

def makeSlot(dominoStatus):     
    path = "/home/arthur/Documents/L2/Stage/Tiles/"
    resultFileName = path + dominoStatus + ".svg"
    destination = cairo.SVGSurface(resultFileName, PIXEL_SIZE, PIXEL_SIZE)
    cr = cairo.Context(destination)
    cr.set_line_width(0.025)
    cr.set_source_rgb(0.5,0.5,0.5)

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

# =============== LINEAR PROBLEM ===============
# ======= BASICS =======
def isWhiteCell(i,j):
    return (i%2 == 0 and j%2 == 0) or (i%2 == 1 and j%2 == 1)

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
    
# ======= EQUATIONS FOR SLOTS =======

def get_contrast_i_j_dP(i,j,k,l, gsMatrix):
    return (gsMatrix[i][j] - gsMatrix[k][l])**2

def strTotalCostSlots( height, width, gsMatrix):
    res = ""
    for i in range(height):
        for j in range(width):
            i_j_adjacent = getAdjacent(i,j,height,width)
            for (k,l) in i_j_adjacent:
                scalar = get_contrast_i_j_dP(i,j, k,l, gsMatrix)
                add = "+ " + str(scalar) + " X_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
                res += add 
    return res[2:]

def strSlotsAdjacentConstraints(i, j, height, width):
    res = ""
    for (k,l) in getAdjacent(i,j,height,width):
        add = "+ X_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
        res += add  
    res += " = 1"  
    return res[2:]

def strSlotsPhysicalConstraints(i, j, k,l):
    res = "X_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l)
    res += " - X_" + str(k) + "_" + str(l) + "_" + str(i) + "_" + str(j) 
    res += " = 0"
    return res

# ======= EQUATIONS FOR DOMINO PLACEMENT =======

def strTotalCostDomino(gsMatrix, allSlots: dict):
    res = ""

    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            for (i,j) in allSlots:
                k, l = allSlots[(i,j)]
                scalar = get_cost_m_n_i_j_k_l(m,n,i,j, k, l, gsMatrix)
                add = "+ " + str(scalar) + " X" + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
                res += add 
    return res[2:]

def strDominoPerSlotsConstraints(i, j, k, l):
    # par slots, on a qu'une seule valeur possible de Domino
    res = ""
    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            add = " + X"  + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
            res += add
    res = res + " = 1"
    res = res[2:]
    return res

def strDominoSetsConstraints(m, n, allSlots, numberOfSets):
    res = ""
    for (i,j) in allSlots:                
        k, l = allSlots[(i,j)]
        add = " + X" + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
        res += add
    res = res + " = " + str(numberOfSets)
    res = res[2:]
    return res

# =============== FILE CREATION ===============

def write(addition: str, fileName):
    f = open(fileName, "a+")
    f.write(addition)
    f.write("\n")
    f.close()

def decomposeExpr(expr: str):
    noOp = expr                             # expression sans opérateur
    for op in lpMathSymbols:
        noOp = noOp.replace(op, " ")    
    noOp = noOp.split()                     # tableau de var, coef et var_coef
    vars_coefs = {}                         # Init du dico correspondant aux vars + coeff
    operators = expr                        # opérateur : str == expr
    coefHolder = "1"                        # tant qu'on ne connait pas le coef, on dit que c'est 1

    for i in range(len(noOp)):
        operators = operators.replace(noOp[i]," ",1)    # on enlève les vars+coeff
        noOp[i] = noOp[i].replace(" ", "")
        # noOp[i] ressemblera à : 8X1 ou 8 ou X1

        coef = ""          # store le coef
        coefIndex = 0      # l'indice du coef

        # tant qu'on reste dans le str et que ce n'est pas une lettre
        while coefIndex < len(noOp[i]) and not noOp[i][coefIndex].isalpha():
            coef += noOp[i][coefIndex]      # On l'ajoute comme coef
            coefIndex += 1                  # On note sa fin

        var = noOp[i][coefIndex:]   # On garde le reste
        if coef == "":              # s'il n'y a pas de coef:  alors soit "X1" avec facteur 1, soit "X1" avec coef dans coef holder 
            vars_coefs[var] = coefHolder

        elif var == "":             # s'il n'y a pas de variable: "8" => on le retiens pour plus tard (variable ou égalité)
            coefHolder = coef  
        else:                       # il y a coef et var : "8X1"
            vars_coefs[var] = coef
            coefHolder = "1"
    operators = operators.split()
    return vars_coefs, operators, coefHolder

def str2Expr(expr: str):
    vars_coefs, operators, coefHolder = decomposeExpr(expr)
    res = ""
    if operators[0] == "=" or operators[0] == "<=" or operators[0] == ">=":
        res +=  expr[0] + " " + operators[0] + " " 
        cpt = 1
        for var in vars_coefs.keys():
            coef = vars_coefs[var]
            if coef == "1":
                res +=  " " + var + " " + operators[cpt] 
            else :
                res +=  " " + coef + " " + var + " " + operators[cpt] 
            cpt += 1
        res += " " + coefHolder
        return res

    else : 
        cpt = 0 
        for var in vars_coefs.keys():
            coef = vars_coefs[var]
            if cpt == 0:
                if coef == "1":
                    res += var
                else :
                    res += coef + " " + var
            else:
                if coef == "1":
                    res += " " + operators[cpt-1] + " " + var
                else:
                    res += " " + operators[cpt-1] + " " + coef + " " + var
            cpt += 1

    if operators[-1] == "=" or operators[-1] == "<=" or operators[-1] == ">=":
        res += " " + operators[-1] + " " + coefHolder
    return res

def createLPfileDominoPlacement(fileName, gsMatrix, numberOfSets, allSlots):
   
    vars = decomposeExpr(strTotalCostDomino(gsMatrix, allSlots))[0]

    # =============== MIN/MAX ===============
    
    write('minimize', fileName)
    totalCost = str2Expr(strTotalCostDomino(gsMatrix, allSlots))
    write(totalCost, fileName)
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            DominoConstraintMN = str2Expr(strDominoSetsConstraints(m , n, allSlots, numberOfSets))
            write(DominoConstraintMN, fileName)

    for (i,j) in allSlots:
            k,l = allSlots[(i,j)]
            ConstraintSlot = str2Expr(strDominoPerSlotsConstraints(i,j, k,l))
            write(ConstraintSlot, fileName)

    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        write(v, fileName)
        
    write("end", fileName)
     
    return None

def createLPfileSlotsArrangement(fileName, imageName, blocksize, numberOfSets):
    
    height = getNbLines(imageName, blocksize)
    width = getNbCollums(imageName, blocksize)
    gsMatrix = image2matrix(imageName, blocksize, numberOfSets)

    print("blocksize :", blocksize)
    print("height : ", height)
    print("width : ", width)
    print("len(gsMatrix) : ", len(gsMatrix))
    print("len(gsMatrix[0]) : ", len(gsMatrix[0]))

    vars = decomposeExpr(strTotalCostSlots(height, width, gsMatrix))[0]
    # =============== MIN/MAX ===============
    
    write('maximize', fileName)
    totalCost = str2Expr(strTotalCostSlots(height, width, gsMatrix))
    write(totalCost, fileName)  
    #print("nb variables dans Total Cost :", len(vars))
    
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for i in range(height):
        for j in range(width):
                slotsConstraints = str2Expr(strSlotsAdjacentConstraints(i,j,height, width))
                write(slotsConstraints, fileName)
    
    for i in range(height):
        for j in range(width):
                for (k,l) in getAdjacent(i,j,height, width):
                    physicalConstraints = strSlotsPhysicalConstraints(i,j,k,l)
                    write(physicalConstraints, fileName)

        
        


    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        write(v, fileName)
        
    write("end", fileName)
     
    return None

# =============== MAIN ===============

def solFileDomino2Matrix(solFile, image, blocksize, gsMatrix):
    height = getNbLines(image, blocksize)
    width = getNbCollums(image, blocksize)
    matrix = [[0 for i in range(width)] for j in range (height)]

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    m,n,i,j,k,l = get_m_n_i_j_k_l_from_var(var)
                    if get_cost_m_n_i_j_k_l(m,n,i,j,k,l, gsMatrix) < get_cost_m_n_i_j_k_l(n,m,i,j,k,l, gsMatrix):
                        # si m: (i,j), n: (k,l) moins couteux que n: (i,j), m: (k,l) 
                        matrix[i][j] = m
                        matrix[k][l] = n
                    else:
                        matrix[i][j] = n
                        matrix[k][l] = m
            cpt += 1 
    return matrix

def solFileSlots2Matrix(solFile, image, blocksize ):
    height = getNbLines(image, blocksize)
    width = getNbCollums(image, blocksize)
    matrix = [[0 for i in range(width)] for j in range (height)]

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    i,j,k,l = get_i_j_k_l_from_var(var)
                    i_j_pos = dp_and_i_j_pos(i,j,k,l)
                    matrix[i][j] = i_j_pos
                    matrix[k][l] = getContraryPos(i_j_pos)
            cpt += 1 
    return matrix

def main(fileName, numberOfSets):
    createAllDirectories()

    rawName = getRawName(fileName)
    croppedName = getCroppedName(fileName)
    lpNameSlots =  getLpName(fileName + "Slots")
    solNameSlots = getSolName(fileName + "Slots")
    logNameSlots = getLogName(fileName + "Slots")
    svgNameSlots = getSvgName(fileName + "Slots")
    lpNameDomino =  getLpName(fileName + "Domino")
    solNameDomino = getSolName(fileName + "Domino")
    logNameDomino = getLogName(fileName + "Domino")
    svgNameDomino = getSvgName(fileName + "Domino")

    # === Slots Creation ===
    cropImage(rawName, numberOfSets)
    blocksize = getBS(croppedName, numberOfSets)
    gsMatrix = image2matrix(croppedName, blocksize, numberOfSets)

    if os.path.isfile(lpNameSlots): os.remove(lpNameSlots)

    createLPfileSlotsArrangement(lpNameSlots, croppedName, blocksize, numberOfSets)

    subprocess.run(["gurobi_cl", "Resultfile=" + solNameSlots , "Logfile=" + logNameSlots, " Method=0", lpNameSlots])

    m = solFileSlots2Matrix(solNameSlots, croppedName, blocksize)
    pictureOfSlotsArrangment = matrix2imageFromSvgTab(m, svgNameSlots, tabSlots)

    # === Domino Creation ===

    allSlots = getAllSlots(getSolName(fileName + "Slots"))

    cropImage(rawName, numberOfSets)
    blocksize = getBS(croppedName, numberOfSets)

    if os.path.isfile(lpNameDomino): os.remove(lpNameDomino)

    createLPfileDominoPlacement(lpNameDomino, gsMatrix, numberOfSets, allSlots)

    subprocess.run(["gurobi_cl", "Resultfile=" + solNameDomino , "Logfile=" + logNameDomino, " Method=0", lpNameDomino])
    gsMatrix = image2matrix(croppedName, blocksize, numberOfSets)
    m = solFileDomino2Matrix(solNameDomino, croppedName, blocksize, gsMatrix)
    pictureOfDominoArrangment = matrix2imageFromSvgTab(m, svgNameDomino, tabDomino)

    return addContext(pictureOfDominoArrangment, pictureOfSlotsArrangment, gsMatrix, svgNameDomino )


# ============================== TEST ==============================

# main("GOAT", 17)