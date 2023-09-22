import math 
import numpy as np
from PIL import Image
import subprocess
import os.path
import cairo
import random as rd


# ============================== DATA ==============================
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]

# ============================== CODE ==============================
def printDico(dico):
    for e in dico:
        print(e, ":", dico[e])

def tupleSet2sortedTupleList(tupleSet: set):
    res = list(tupleSet)
    return sorted(res)

# =============== ENVIRONNEMENT MANAGING ===============ojccv

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

# =============== GETS ===============

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

def get_a_b_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    a = coords[0]
    b = coords[1]
    return int(a), int(b)
def get_cost_a_b(a,b):
    return int(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2))
def get_a_form_coords(x,y, graphCoords):
    for e in graphCoords:
        if (x,y) == e:
            return e
        else:
            raise Exception("Coords not here.")

def get_connected_vertices(middle, graphMatrix):
    if middle >= len(graphMatrix):
        raise Exception ("Vertice not in graph")
    
    before = 0    
    while graphMatrix[middle][before] == 0 and before < len(graphMatrix[0]):
        before += 1
    
    if before >= len(graphMatrix[0]):
        raise Exception ("No connected Vertices")

     
    after = before + 1 
    while graphMatrix[middle][after] == 0 and after < len(graphMatrix[0]):
        after += 1

    if after >= len(graphMatrix[0]):
        raise Exception ("Only one connected vertex:,", middle ," to ", before)
    
    return before, after
def get_previous_vertice(vertex, graphMatrix):
    return get_connected_vertices(vertex, graphMatrix)[0]
def get_following_vertice(vertex, graphMatrix):
    return get_connected_vertices(vertex, graphMatrix)[1]

def get_subtour(start, graphMatrix):
    previous, next = get_connected_vertices(start, graphMatrix)
    if previous == next and next == 0:
        return []
    
    current = next
    res = [start]
    while current != start:
        res.append(current)
        before, after = get_connected_vertices(current, graphMatrix)
        if after in res:
            current = before
        else:
            current = after
        if len(res) > len(graphMatrix):
            raise Exception("End point never found")
    return res
def get_all_subtours(graphMatrix):
    hasToBeSeen = [i for i in range(len(graphMatrix))]
    subtoursTab = []
    while len(hasToBeSeen) > 0:
        subtour = get_subtour(hasToBeSeen[0], graphMatrix)
        subtoursTab.append(subtour)
        hasToBeSeen = [i for i in hasToBeSeen if i not in subtour]
    return subtoursTab

# =============== RASTERIZATION ===============
def cropImage(input, blocksize):
    output = input[:input.find('.')] + "Cropped.png"
    
    im = Image.open(input)
    width, height = im.size
    decHeight = height - (height % blocksize)
    decWidth = width - (width % blocksize)
    im1 = im.crop((0, 0, decWidth, decHeight))
    im1 = im1.save(output)
    return im1
    
def image2matrix(fileName, blocksize):
    fileName = fileName[:fileName.find('.')] + ".jpg"

    image =  Image.open(fileName).convert('RGB')
    
    image =  Image.open(fileName).convert('L')
    width, height = image.size
    width = width//blocksize
    height = height//blocksize

    arrayIm = np.asarray(image)    

    m = [[0 for j in range (width)] for i in range (height)]
    
    cpt = 0
    for i in range (height):    
        for j in range(width):
            mean = 0
            for k in range(blocksize):
                for l in range(blocksize):
                    mean = mean + (arrayIm[blocksize*i + k][blocksize*j + l])
            # m[i][j] = 10 - math.floor(mean/(255*(blocksize**2)) * 10)
            m[i][j] = 3 - int((mean/(255*(blocksize**2)) * 10)//3)
            cpt += m[i][j]

    image.close()
    print("There is ", cpt, "Points.")
    return m


def graphCoordsAndMatrixFromImage(imageName, blocksize):
    
    dotsDensityMatrix = image2matrix(imageName, blocksize)
    height = len(dotsDensityMatrix) 
    width = len(dotsDensityMatrix[0]) 

    res = set()
    for i in range(height):
        for j in range(width):

            for k in range(dotsDensityMatrix[i][j]):  
                # on choisit k x et k y au hazard dans un pixel et
                # on les déplace dans l'image afin de coller au pixel
                # i j
                x = int(rd.random() * blocksize + j * blocksize)
                y = int(rd.random() * blocksize + i * blocksize)
                res.add((x,y))
    res = tupleSet2sortedTupleList(res)
    
    matrix = [ [0 for i in range(len(res))] for j in range(len(res))]
    for i in range(len(res)):
        for j in range(len(res)):
            matrix[i][j] = get_cost_a_b(res[i], res[j])

    return res, matrix

# =============== DRAWINGS ===============

def showPointsOnly(resultFileName,imageName, blocksize):
    
    graphCoords, graphMatrix = graphCoordsAndMatrixFromImage(imageName, blocksize)

    image =  Image.open(imageName).convert('L')
    width, height = image.size
    destination = cairo.SVGSurface(resultFileName, width, height)
    cr = cairo.Context(destination)
    
    cr.set_line_width(3)
    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0, width, height)
    cr.fill()

    cr.set_source_rgb(1,0,0)
    for i in range(len(graphCoords)):
            (x,y) = graphCoords[i]
            cr.move_to(x,y)
            cr.rectangle(x -1.5, y -1.5,3,3)
            cr.fill()
    return cr

def context2png(context, fileName):
    context.get_target().write_to_png(fileName + ".png")

def graph2Context(resultFileName, graphMatrix, graphCoords, height, width):    
    destination = cairo.SVGSurface(resultFileName, width, height)
    cr = cairo.Context(destination)
    
    cr.set_line_width(3)
    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0, width, height)
    cr.fill()

    cr.set_source_rgb(0,0,0)
    for i in range(len(graphMatrix)):
        for j in range(len(graphMatrix[0])):
            if graphMatrix[i][j] != 0:
                (x1,y1) = graphCoords[i]
                (x2,y2) = graphCoords[j]
                cr.move_to(x1, y1)
                cr.line_to(x2,y2)      
    cr.stroke()
    return cr

def addContext(cr1,cr2, matrix, resultFileName, height, width):
    height = len(matrix)
    width = len(matrix[0])
    
    destination = cairo.SVGSurface(resultFileName + "Together", width, height)
    resCr = cairo.Context(destination)
    resCr.set_source_surface(cr1.get_target(), 0,0)
    resCr.paint()
    resCr.set_source_surface(cr2.get_target(), 0,0)
    resCr.paint()
    return resCr
 
# =============== LINEAR PROBLEM ===============

def strTotalCostDistance(graphMatrix):
    res = ""
    for i in range(len(graphMatrix)):
        for j in range(len(graphMatrix[0])):
            if i != j :
                add = "+ " + strVar([i,j], graphMatrix[i][j]) 
                res += add 
    return res[2:]

def strVertexConstraintsExt(graphMatrix, indexA):
    res = ""
    for i in range(len(graphMatrix)):
        if i != indexA:
            add = " + " + strVar([i, indexA])  
            res += add 
    res = res + " = 2"
    return res[2:]

def strLinksConstraints(i,j):
    res = ""
    res = strVar([i,j]) + " - " + strVar([j,i]) + " = 0"
    return res

def strSubtourConstraints(graphMatrix, subtour):
    hasToBeSeen = [i for i in range(len(graphMatrix)) if i not in subtour]
    res = ""
    for a in subtour:
        for b in hasToBeSeen:
            add = " + " + strVar([a, b])  
            res += add 
    res = res + " >= 2"
    return res[2:]

# =============== FILE CREATION ===============
def strVar(indexes: list, scalar = 1):
    res = str(scalar) + " X"
    for e in indexes:
        res += "_" + str(e) 
    return res

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

def createLPfileGraph(fileName, graphCoords, graphMatrix, allSubtours = [[]]):
    # graph ici correspond a un ensemble de point sans transiitions
    # il deviendra un graphe avec toutes les transtition possible sauf boucle
    # states correspond a une liste de tuple ordonné dans l'ordre alphabetique
    vars = decomposeExpr(strTotalCostDistance(graphMatrix))[0]

    # =============== MIN/MAX ===============
    
    write('minimize', fileName)
    totalCost = str2Expr(strTotalCostDistance(graphMatrix))
    write(totalCost, fileName)
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for i in range(len(graphCoords)):
        
        vertexConstraintExt = strVertexConstraintsExt(graphMatrix, i)
        write(vertexConstraintExt, fileName)

    for i in range(len(graphCoords)):
        for j in range(len(graphCoords)):
            if i != j :
                LinksConstraints = strLinksConstraints(i,j)
                write(LinksConstraints, fileName)
    
    if len(allSubtours) != 1:
        for subtour in allSubtours:
            SubTourConstraint = strSubtourConstraints(graphMatrix, subtour)
            write(SubTourConstraint, fileName)


    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        a,b = get_a_b_from_var(v)
        if a == b:
            raise Exception("a == b")
        write(v, fileName)
        
    write("end", fileName)
     
    return None

# =============== MAIN ===============

def solFile2Graph(solFile, graphMatrix):
    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value != "1":
                    a, b  = get_a_b_from_var(var)
                    graphMatrix[a][b] = 0
            cpt += 1 
    return graphMatrix

def main(fileName, graphCoords, graphMatrix, height, width):
    createAllDirectories()
    allSubTours = [[]]
    cpt = 0
    numberOfSubTours = 0

    while numberOfSubTours != 1 and cpt < 10:
        lpName =  getLpName(fileName  + "_" + str(cpt))
        solName = getSolName(fileName + "_" + str(cpt))
        logName = getLogName(fileName + "_" + str(cpt))
        svgName = getSvgName(fileName + "_" + str(cpt))
        
        copyOfGraphMatrix = [row[:] for row in graphMatrix]

        if os.path.isfile(lpName): os.remove(lpName)
        createLPfileGraph(lpName, graphCoords, copyOfGraphMatrix, allSubTours)
        subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName ])

        resultGraph = solFile2Graph(solName, copyOfGraphMatrix)
        if allSubTours == [[]]: allSubTours = get_all_subtours(resultGraph)

        drawing = graph2Context(svgName, resultGraph, graphCoords, height, width)
        for subTour in get_all_subtours(resultGraph):
            allSubTours.append(subTour)
            
        numberOfSubTours = len(get_all_subtours(resultGraph)) 
        cpt += 1
        
    return drawing

def mainImage(fileName, blocksize):
    createAllDirectories()

    graphCoords, graphMatrix =  graphCoordsAndMatrixFromImage(getRawName(fileName), blocksize)
    height = len(graphMatrix)  
    width = len(graphMatrix[0])  
    allSubTours = [[]]
    cpt = 0
    numberOfSubTours = 0
    
    while numberOfSubTours != 1 and cpt < 50:
        lpName =  getLpName(fileName  + "_" + str(cpt))
        solName = getSolName(fileName + "_" + str(cpt))
        logName = getLogName(fileName + "_" + str(cpt))
        svgName = getSvgName(fileName + "_" + str(cpt))
        
        copyOfGraphMatrix = [row[:] for row in graphMatrix]

        if os.path.isfile(lpName): os.remove(lpName)
        createLPfileGraph(lpName, graphCoords, copyOfGraphMatrix, allSubTours)
        subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName ])

        resultGraph = solFile2Graph(solName, copyOfGraphMatrix)
        if allSubTours == [[]]: allSubTours = get_all_subtours(resultGraph)

        drawing = graph2Context(svgName, resultGraph, graphCoords, height, width)
        for subTour in get_all_subtours(resultGraph):
            allSubTours.append(subTour)
            
        numberOfSubTours = len(get_all_subtours(resultGraph)) 
        cpt += 1
    return drawing

# ============================== TEST ==============================

# print(createGraphWithRandomPoints(100,100, 10))
# print(makeAllTransition(createGraphWithRandomPoints(100,100, 10)))
# print(G.removeNullDistance(makeAllTransition(createGraphWithRandomPoints(100,100, 10))))


# main("Test", graphCoords, graphMatrix, 500, 500)

# showPointsOnly("Results/Skull.svg", "Raw/Skull.jpg" , 14)
# mainImage("Skull", 14)

# print(image2matrix("Raw/Skull.jpg", 10))
# il y a 2229 points. Lancé le 6 Juillet à 17 h 45
# graphCoords, graphMatrix =  graphCoordsAndMatrixFromImage(getRawName("Eye"), 10)
# print(graphCoords)
# print(graphMatrix)
"""
# print(graphMatrix)

def print_coords_list(list):
    for e in list:
        print(graphCoords[e])
        
subTour0 = get_subtour(0, graphMatrix)
print(subTour0)
print_coords_list(subTour0)

allSubTours = get_all_subtours(graphMatrix)
n = 0
for list in allSubTours:
    print(list)
    n += len(list)
    print_coords_list(list)

print("There is :", len(allSubTours)," subtours.")
print("There is :", n," vertices.")

# print(tupleSet2tupleList({ (0,1), (1,1), (8,1), (1,8), (2,1), (0,2), (0,0), (7,8), (1,7)}))
print(image2matrix("Raw/SOAD.jpg", 5))

"""

# print(image2matrix("Raw/Skull.jpg", 10))
