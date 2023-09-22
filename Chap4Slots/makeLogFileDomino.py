import RasterSlots as RS
import makeLogFileSlots as mLFS
import subprocess
import os.path
# =============== DATA ===============
NUMBER_OF_SHADES = 10
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]


# =============== CODE ===============
def getRawName(fileName):
    return "/home/arthur/Documents/L2/Stage/Chap4Slots/Raw/" + fileName + ".jpg"
def getCroppedName(fileName):
    return"/home/arthur/Documents/L2/Stage/Chap4Slots/Raw/" + fileName + "Cropped.png"
def getLpName(fileName):
    return "/home/arthur/Documents/L2/Stage/Chap4Slots/LPFiles/" + fileName + ".lp"
def getSolName(fileName):
    return "/home/arthur/Documents/L2/Stage/Chap4Slots/SolFiles/" + fileName + ".sol"
def getLogName(fileName):
    return "/home/arthur/Documents/L2/Stage/Chap4Slots/LogFiles/" + fileName + ".log"
def getSvgName(fileName):
    return "/home/arthur/Documents/L2/Stage/Chap4Slots/Results/" + fileName + ".svg"

def printDico(dico):
    for e in dico:
        print(e, ":", dico[e])

def removeKeyValueDuplicate(dico):
    tabKey = []
    for key in dico:
        if dico[key] in dico.keys() and dico[dico[key]] == key and dico[key] not in tabKey:
            tabKey.append(key)
    for key in tabKey : del dico[key]

def getAllSlots(solFileName: str):
    pairs = {}
    with open(solFileName) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    i,j,k,l = mLFS.get_i_j_k_l_from_var(var)
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

def get_contrast_m_n_i_j_k_l(m, n, i, j, k, l, gsMatrix):
    return (m - gsMatrix[i][j])**2 + (n - gsMatrix[k][l])**2

def get_cost_m_n_i_j_k_l(m, n, i, j, k, l, gsMatrix):
    return min((m - gsMatrix[i][j])**2 + (n - gsMatrix[k][l])**2, (n - gsMatrix[i][j])**2 + (m - gsMatrix[k][l])**2)

def strTotalCost(gsMatrix, allSlots: dict):
    res = ""

    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            for (i,j) in allSlots:
                k, l = allSlots[(i,j)]
                scalar = get_cost_m_n_i_j_k_l(m,n,i,j, k, l, gsMatrix)
                add = "+ " + str(scalar) + " X" + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
                res += add 
    return res[2:]

def strSlotsConstraints(i, j, k, l):
    # par slots, on a qu'une seule valeur possible de Domino
    res = ""
    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            add = " + X"  + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
            res += add
    res = res + " = 1"
    res = res[2:]
    return res

def strDominoConstraints(m , n, allSlots, numberOfSets):
    res = ""
    for (i,j) in allSlots:                
        k, l = allSlots[(i,j)]
        add = " + X" + "_" + str(m) + "_" + str(n) + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) 
        res += add
    res = res + " = " + str(numberOfSets)
    res = res[2:]
    return res

def createLPfile(fileName, imageName, blocksize, numberOfSets, allSlots):
    
    height = RS.getNbLines(imageName, blocksize)
    width = RS.getNbCollums(imageName, blocksize)
    gsMatrix = RS.image2matrix(imageName, blocksize, numberOfSets)

    print("blocksize :", blocksize)
    print("height : ", height)
    print("width : ", width)
    print("len(gsMatrix) : ", len(gsMatrix))
    print("len(gsMatrix[0]) : ", len(gsMatrix[0]))

    vars = decomposeExpr(strTotalCost(gsMatrix, allSlots))[0]

    # =============== MIN/MAX ===============
    
    write('minimize', fileName)
    totalCost = str2Expr(strTotalCost(gsMatrix, allSlots))
    write(totalCost, fileName)
    
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for m in range(NUMBER_OF_SHADES):
        for n in range(m, NUMBER_OF_SHADES):
            DominoConstraintMN = str2Expr(strDominoConstraints(m , n, allSlots, numberOfSets))
            write(DominoConstraintMN, fileName)

    for (i,j) in allSlots:
            k,l = allSlots[(i,j)]
            ConstraintSlot = str2Expr(strSlotsConstraints(i,j, k,l))
            write(ConstraintSlot, fileName)

    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        write(v, fileName)
        
    write("end", fileName)
     
    return None

def decomposeExpr(expr: str):
    noOp = expr                         # expression sans opérateur
    for op in lpMathSymbols:
        noOp = noOp.replace(op, " ")    
    noOp = noOp.split()         # tableau de var, coef et var_coef
    vars_coefs = {}            # Init du dico correspondant aux vars + coeff
    operators = expr             # opérateur : str == expr
    coefHolder = "1"    # tant qu'on ne connait pas le coef, on dit que c'est 1

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

        var = noOp[i][coefIndex:]    # On garde le reste
        if coef == "":               # s'il n'y a pas de coef:  alors soit "X1" avec facteur 1, soit "X1" avec coef dans coef holder 
            vars_coefs[var] = coefHolder

        elif var == "":              # s'il n'y a pas de variable: "8" => on le retiens pour plus tard (variable ou égalité)
            coefHolder = coef  
        else:                        # il y a coef et var : "8X1"
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

def write(addition: str, fileName):

    f = open(fileName, "a+")
    f.write(addition)
    f.write("\n")
    f.close()

def solFile2gSmatrix(solFile, image, blocksize, gsMatrix):
    height = RS.getNbLines(image, blocksize)
    width = RS.getNbCollums(image, blocksize)
    matrix = [[0 for i in range(width)] for j in range (height)]

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    m,n,i,j,k,l = get_m_n_i_j_k_l_from_var(var)
                    if get_contrast_m_n_i_j_k_l(m,n,i,j,k,l, gsMatrix) < get_contrast_m_n_i_j_k_l(n,m,i,j,k,l, gsMatrix):
                        # si m: (i,j), n: (k,l) moins couteux que n: (i,j), m: (k,l) 
                        matrix[i][j] = m
                        matrix[k][l] = n
                    else:
                        matrix[i][j] = n
                        matrix[k][l] = m
            cpt += 1 
    return matrix

def main(fileName, numberOfSets):
    rawName = getRawName(fileName)
    croppedName = getCroppedName(fileName)
    lpName =  getLpName(fileName)
    solName = getSolName(fileName)
    logName = getLogName(fileName)
    svgName = getSvgName(fileName)

    allSlots = getAllSlots(getSolName(fileName + "Slots"))

    RS.cropImage(rawName, numberOfSets)
    blocksize = RS.getBS(croppedName, numberOfSets)

    if os.path.isfile(lpName): os.remove(lpName)

    createLPfile(lpName, croppedName, blocksize, numberOfSets, allSlots)

    subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName])
    gsMatrix = RS.image2matrix(croppedName, blocksize, numberOfSets)
    m = solFile2gSmatrix(solName, croppedName, blocksize, gsMatrix)
    return RS.matrix2imageFromSvgTab(m, svgName, RS.tabDomino)


print ("______________________________")
# main("GOAT", 42)
# 
# print ("______________________________")
# main("nirvana", 42)
# 
# print ("______________________________")
# main("SOAD", 42)
# 

# RS.context2png( main("Marbrier", 30), "MarbrierDomino.png") # 1 min
# 

print ("______________________________")
