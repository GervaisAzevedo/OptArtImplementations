import math 
import numpy as np
from PIL import Image
import subprocess
import os.path
import cairo
from GraphClass import Graph as G
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
    
# print(tupleSet2tupleList({ (0,1), (1,1), (8,1), (1,8), (2,1), (0,2), (0,0), (7,8), (1,7)}))

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


def get_x1_y1_x2_y2_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    x1 = coords[0]
    y1 = coords[1]
    x2 = coords[2]
    y2 = coords[3]
    return int(x1), int(y1), int(x2), int(y2)

def get_cost_x1_y1_x2_y2(x1,y1,x2,y2):
    return int(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))


# =============== RASTERIZATION ===============

def image2matrix(fileName, blocksize):
    fileName = fileName[:fileName.find('.')] + ".jpg"

    image =  Image.open(fileName).convert('RGB')
    
    image =  Image.open(fileName).convert('L')
    width, height = image.size

    arrayIm = np.asarray(image)    

    m = [[0 for j in range (width)] for i in range (height)]
    
    for i in range (height):    
        for j in range(width):
            mean = 0
            for k in range(blocksize):
                for l in range(blocksize):
                    mean = mean + (arrayIm[blocksize*i + k][blocksize*j + l])
            m[i][j] = math.floor(mean/(255*(blocksize**2)) * 10)
    image.close()
    return m

# =============== DRAWINGS ===============

def context2png(context, pngName):
    context.get_target().write_to_png(pngName)

def createGraphWithRandomPoints(height, width, numberOfPoints):
    res = set()
    for i in range(numberOfPoints):  
        x = int(rd.random() * height )
        y = int(rd.random() * width)
        res.add((x,y))

    A = G(res, {})
    return A

def makeAllTransition(graph):
    states = G.get_states(graph)
    for (x1,y1) in states:
        for (x2,y2) in states:
            if (x1,y1) != (x2,y2):
                G.add_transition(graph, (x1,y1),get_cost_x1_y1_x2_y2(x1,y1,x2,y2), (x2,y2))
    return graph

def graph2Context(resultFileName, graph: G, height, width):
    
    destination = cairo.SVGSurface(resultFileName, width, height)
    cr = cairo.Context(destination)
    
    cr.set_line_width(3)
    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0,height, width)
    cr.fill()

    trans = graph.trans
    
    cr.set_source_rgb(1,0,0)
    for (x,y) in graph.states:
        cr.move_to(x, y)
        cr.rectangle(x -2.5, y -2.5,5,5)
        cr.fill()

    cr.set_source_rgba(0,0,0, 0.3)
    for (x1, y1) in trans:

        # targets = G.compute_next(graph,{(x1,y1)}) 
        # for (x2, y2) in targets:
        if (x1, y1) in trans:
            for presence in trans[(x1,y1)]:
                if presence in trans[(x1,y1)]:
                    for (x2,y2) in trans[(x1,y1)][presence]: 
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
 
 
"""
def graph2Context(resultFileName, graph: G, height, width):
    makeAllTransition(graph)
    destination = cairo.SVGSurface(resultFileName, width, height)
    cr = cairo.Context(destination)
    
    cr.set_line_width(3)
    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0,height, width)
    cr.fill()

    trans = graph.trans
    
    cr.set_source_rgb(1,0,0)
    for (x,y) in graph.states:
        cr.move_to(x, y)
        cr.rectangle(x -2.5, y -2.5,5,5)
        cr.fill()

    cr.set_source_rgba(0,0,0, 0.3)
    for (x1, y1) in trans:
        cr.move_to(x1, y1)

        for label in trans[(x1,y1)]:
            for (x2, y2) in trans[(x1,y1)][label]:
                    cr.line_to(x2,y2)
    cr.stroke()

    return cr

"""

# =============== LINEAR PROBLEM ===============

def strTotalCostDistance(graph: G):
    res = ""
    trans = graph.trans
    for (x1, y1) in trans:
        if (x1, y1) in trans:
            for cost in trans[(x1,y1)]:
                if cost in trans[(x1,y1)]:
                    for (x2,y2) in trans[(x1,y1)][cost]:
                        add = "+ " + strVar([x1, y1, x2, y2], cost) 
                        res += add 
    return res[2:]

def strVertexConstraintsExt(graph: G, x1, y1):
    res = ""
    states = graph.states
    for (x2, y2) in states:
        if (x1,y1) != (x2,y2):
            add = " + " + strVar([x1, y1, x2, y2])  
            res += add 
    res = res + " = 2"
    return res[2:]

def strLinksConstraints(graph: G, x1, y1, x2, y2):
    res = ""
    res = strVar([x1, y1, x2, y2]) + " - " + strVar([x2, y2, x1, y1]) + " = 0"
    return res

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

def createLPfileGraph(fileName, graph: G):
    # graph ici correspond a un ensemble de point sans transiitions
    # il deviendra un graphe avec toutes les transtition possible sauf boucle
    # states correspond a une liste de tuple ordonné dans l'ordre alphabetique
    
    makeAllTransition(graph)
    G.removeNullDistance(graph)
    vars = decomposeExpr(strTotalCostDistance(graph))[0]

    # =============== MIN/MAX ===============
    
    write('minimize', fileName)
    totalCost = str2Expr(strTotalCostDistance(graph))
    write(totalCost, fileName)
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for (x1,y1) in G.get_states(graph):
        vertexConstraintExt = strVertexConstraintsExt(graph, x1,y1)
        write(vertexConstraintExt, fileName)

    for (x1,y1) in G.get_states(graph):
        for (x2,y2) in G.get_states(graph):
            if (x1,y1) != (x2,y2):
                LinksConstraints = strLinksConstraints(graph, x1,y1, x2,y2)
                write(LinksConstraints, fileName)


    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        x1, y1, x2, y2 = get_x1_y1_x2_y2_from_var(v)
        if x1 == x2 and y1 == y2:
            raise Exception("(x1,y1) == (x2,y2)")
        write(v, fileName)
        
    write("end", fileName)
     
    return None

# =============== MAIN ===============

def solFile2Graph(solFile):
    graph = G(set(), {})

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    x1,y1,x2,y2 = get_x1_y1_x2_y2_from_var(var)
                    if (x1,y1) not in graph.states:
                        G.add_state(graph, (x1, y1))
                    if (x2,y2) not in graph.states:
                        G.add_state(graph, (x2, y2))
                    G.add_transition(graph, (x1, y1), 1 ,(x2, y2))
            cpt += 1 
    return graph


def main(fileName, height, width, numberOfPoints):
    createAllDirectories()

    rawName = getRawName(fileName)
    lpName =  getLpName(fileName )
    solName = getSolName(fileName)
    logName = getLogName(fileName)
    svgName = getSvgName(fileName)

    # === graph Creation ===
    graph = createGraphWithRandomPoints(height, width, numberOfPoints)

    if os.path.isfile(lpName): os.remove(lpName)

    createLPfileGraph(lpName, graph)

    subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName ])

    resultGraph = solFile2Graph(solName)
    drawing = graph2Context(svgName, resultGraph, height, width)
    print(resultGraph)
    return drawing


# ============================== TEST ==============================

# print(createGraphWithRandomPoints(100,100, 10))
# print(makeAllTransition(createGraphWithRandomPoints(100,100, 10)))
# print(G.removeNullDistance(makeAllTransition(createGraphWithRandomPoints(100,100, 10))))

# main("Test", 500, 500, 50)
# main("Test", 500, 500, 100)
main("Test", 500, 500, 1000)
