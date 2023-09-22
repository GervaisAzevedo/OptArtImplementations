import RasterSlots as R
import subprocess
import os.path
# =============== DATA ============
# =============== CODE ===============
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]
otherMathSymbols = ["/", "*", "^"]


def createLPfile(fileName, imageName, blocksize, numberOfSets):
    
    height = R.getNbLines(imageName, blocksize)
    width = R.getNbCollums(imageName, blocksize)
    gsMatrix = R.image2matrix(imageName, blocksize, numberOfSets)

    print("blocksize :", blocksize)
    print("height : ", height)
    print("width : ", width)
    print("len(gsMatrix) : ", len(gsMatrix))
    print("len(gsMatrix[0]) : ", len(gsMatrix[0]))

    vars = decomposeExpr(R.strTotalCost(height, width, gsMatrix))[0]
    # =============== MIN/MAX ===============
    
    write('maximize', fileName)
    totalCost = str2Expr(R.strTotalCost(height, width, gsMatrix))
    write(totalCost, fileName)  
    #print("nb variables dans Total Cost :", len(vars))
    
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for i in range(height):
        for j in range(width):
                slotsConstraints = str2Expr(R.strSlotsConstraints(i,j,height, width))
                write(slotsConstraints, fileName)
    
    for i in range(height):
        for j in range(width):
                for (k,l) in R.getAdjacent(i,j,height, width):
                    physicalConstraints = R.strPhysicalConstraints(i,j,k,l)
                    write(physicalConstraints, fileName)

        
        


    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        write(v, fileName)
        
    write("end", fileName)
     
    return None

def get_i_j_k_l_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    i = coords[0]
    j = coords[1]
    k = coords[2]
    l = coords[3]
    return int(i),int(j),int(k),int(l)

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

def nbVars(expr :str):
    return len(decomposeExpr(expr)[0])

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

def solFile2matrix(solFile, image, blocksize ):
    height = R.getNbLines(image, blocksize)
    width = R.getNbCollums(image, blocksize)
    matrix = [[0 for i in range(width)] for j in range (height)]

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    i,j,k,l = get_i_j_k_l_from_var(var)
                    i_j_pos = R.dp_and_i_j_pos(i,j,k,l)
                    matrix[i][j] = i_j_pos
                    matrix[k][l] = R.getContraryPos(i_j_pos)
            cpt += 1 
    return matrix

def main(fileName, numberOfSets):  
    rawName = "/home/arthur/Documents/L2/Stage/Chap4Slots/Raw/" + fileName + ".jpg"
    croppedName = "/home/arthur/Documents/L2/Stage/Chap4Slots/Raw/" + fileName + "Cropped.png"
    lpName = "/home/arthur/Documents/L2/Stage/Chap4Slots/LPFiles/" + fileName + "Slots.lp"
    solName = "/home/arthur/Documents/L2/Stage/Chap4Slots/SolFiles/" + fileName + "Slots.sol"
    logName = "/home/arthur/Documents/L2/Stage/Chap4Slots/LogFiles/" + fileName + "Slots.log"
    svgName = "/home/arthur/Documents/L2/Stage/Chap4Slots/Results/" + fileName + "Slots.svg"

    R.cropImage(rawName, numberOfSets)
    blocksize = R.getBS(croppedName, numberOfSets)

    if os.path.isfile(lpName): os.remove(lpName)

    createLPfile(lpName, croppedName, blocksize, numberOfSets)

    subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName])

    m = solFile2matrix(solName, croppedName, blocksize)
    return R.matrix2imageFromSvgTab(m, svgName, R.tabSlots)

# =============== TEST ===============


# print ("______________________________")
# main("GOAT", 42)
# 
# print ("______________________________")
# main("nirvana", 42)
# 
# print ("______________________________")
# main("SOAD", 42)
# 
# print ("______________________________")

# print ("______________________________")
# R.context2png( main("Marbrier", 30), "MarbrierSlots.png") # moins de 10 sec
# print ("______________________________")


"""


print ("_______________________ TEST _______________________ ")

blocksize = R.getBS("./Raw/GOAT.jpg", 5)
R.cropImage("./Raw/GOAT.jpg", 5)
height = R.getNbLines("./Raw/GOATCropped.png", blocksize)
width = R.getNbCollums("./Raw/GOATCropped.png", blocksize)

print("width =", width )
print("height =", height )
print("blocksize =", blocksize )

print ("__________________________________________________ ")

m = [[(i+coefIndex)/10 for i in range (4)] for coefIndex in range (4)]
print (m)
vars = decomposeExpr(R.strTotalCost(4, 4, m, "vertical"))[0]
R.printDico(vars)
print()
print(str2Expr(R.strTotalCost(4, 4, m, "vertical")))  

print ("__________________________________________________ ")

print ("Pour :  0 X1 + 11/3 X2 + 1 X3 : ")
print(decomposeExpr("0 X1 + 11/3 X2 + 1 X3"))
print(str2Expr("0 X1 + 11/3 X2 + 1 X3"))

print ("__________________________________________________ ")

print ("Pour : 8X1 + 11/3X2 + 15X3 +7 X4 <= 10 : ")
print(decomposeExpr("8X1 + 11/3X2 + 15X3 +7 X4 <= 10"))
print(str2Expr("8X1 + 11/3X2 + 15X3 +7 X4 <= 10"))

print ("__________________________________________________ ")

print ("Pour : 8X1 +11/3X2+ 11 X3 = 10 : ")
print(decomposeExpr("8X1 +11/3X2+ 11 X3 = 10 "))
print(str2Expr("8X1 +11/3X2+ 11 X3 = 10 "))
print ("__________________________________________________ ")

print ("Pour : 0 >= X1 <= 1 : ")
print(decomposeExpr("0 >= X1 <= 1"))
print(str2Expr("0 >= X1 <= 1"))
print ("__________________________________________________ ")

print(str2Expr("0 >= X1 <= 1"))
print ("__________________________________________________ ")

"""