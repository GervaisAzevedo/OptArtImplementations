import RasterDomino as R
from PIL import Image
import subprocess
import os.path
import math
# =============== DATA ============Raster===
# =============== CODE ===============
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]
otherMathSymbols = ["/", "*", "^"]


def createLPfile(fileName, imageName, blocksize, numberOfSets, dominoPositioning):
    
    height = R.getNbLines(imageName, blocksize)
    width = R.getNbCollums(imageName, blocksize)
    gsMatrix = R.image2matrix(imageName, blocksize, numberOfSets)

    print("blocksize :", blocksize)
    print("height : ", height)
    print("width : ", width)
    print("len(gsMatrix) : ", len(gsMatrix))
    print("len(gsMatrix[0]) : ", len(gsMatrix[0]))
    # print("gsMatrix : ", gsMatrix)


    vars = decomposeExpr(R.strTotalCost(height, width, gsMatrix, dominoPositioning))[0]

    # =============== MIN/MAX ===============
    
    write('minimize', fileName)
    totalCost = str2Expr(R.strTotalCost(height, width, gsMatrix, dominoPositioning))
    write(totalCost, fileName)  
    # print(totalCost)
    #print("nb variables dans Total Cost :", len(vars))
    
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for m in range(R.NUMBER_OF_SHADES):
        for n in range(m, R.NUMBER_OF_SHADES):
            DominoConstraintMN = str2Expr(R.strDominoConstraints(m , n, height, width, numberOfSets))
            write(DominoConstraintMN, fileName)
            # print(DominoConstraintMN)
            #print("nb variables dans Domino Constraints m, n :", nbVars(DominoConstraintMN))

    for i in range(height):
        for j in range(width):
            ConstraintIJ = str2Expr(R.strSlotsConstraints(i,j, dominoPositioning))
            write(ConstraintIJ, fileName)
            #print(VerticalConstraintIJ)
            #print("nb variables dans Vertical Constraints i, j :", nbVars(VerticalConstraintIJ))
    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        write(v, fileName)
        
    write("end", fileName)
     
    return None

def get_m_n_i_j_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    m = coords[0]
    n = coords[1]
    i = coords[2]
    j = coords[3]
    if m > n :
        raise Exception("Le domino (",m,n,") est faux. Il faut: m <= n")
    return int(m),int(n),int(i),int(j)

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

        coef = ""           # store le coef
        coefIndex = 0       # l'indice du coef

        # tant qu'on reste dans le str et que ce n'est pas une lettre
        while coefIndex < len(noOp[i]) and not noOp[i][coefIndex].isalpha():
            coef += noOp[i][coefIndex]      # On l'ajoute comme coef
            coefIndex += 1
        var = noOp[i][coefIndex:]    # On garde le reste
        if coef == "":        # s'il n'y a pas de coef
            if i != 1:
                vars_coefs[var] = coefHolder
            else:
                vars_coefs[var] = "1"
        elif var == "":       # s'il n'y a pas de variable
            coefHolder = coef  
        else:                 # il y a coef et var 
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

def solFile2gSmatrix(solFile, image, blocksize , dominoPositioning ):
    height = R.getNbLines(image, blocksize)
    width = R.getNbCollums(image, blocksize)
    matrix = [[0 for i in range(width)] for j in range (height)]

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    m,n,i,j = get_m_n_i_j_from_var(var)
                    
                    if dominoPositioning == "vertical":
                            matrix[i][j] = m
                            matrix[i+1][j] = n
                    if dominoPositioning == "horizontal":
                        matrix[i][j] = m
                        matrix[i][j+1] = n
            cpt += 1 
    return matrix

def main(fileName, numberOfSets, dominoPositioning):
    
    rawName = "/home/arthur/Documents/L2/Stage/Chap4/Raw/" + fileName + ".jpg"
    croppedName = "/home/arthur/Documents/L2/Stage/Chap4/Raw/" + fileName + "Cropped.png"
    lpName = "/home/arthur/Documents/L2/Stage/Chap4/LPFiles/" + fileName + dominoPositioning + ".lp"
    solName = "/home/arthur/Documents/L2/Stage/Chap4/SolFiles/" + fileName + dominoPositioning + ".sol"
    logName = "/home/arthur/Documents/L2/Stage/Chap4/LogFiles/" + fileName + dominoPositioning + ".log"
    svgName = "/home/arthur/Documents/L2/Stage/Chap4/Results/" + fileName + dominoPositioning + ".svg"

    R.cropImage(rawName, numberOfSets)
    blocksize = R.getBS(croppedName, numberOfSets)

    if os.path.isfile(lpName): os.remove(lpName)

    createLPfile(lpName, croppedName, blocksize, numberOfSets, dominoPositioning)

    subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName])

    m = solFile2gSmatrix(solName, croppedName, blocksize, dominoPositioning)
    R.matrix2imageFromExistingSVG(m, svgName)

# =============== TEST ===============

# print ("______________________________")
# main("GOAT", 20, "vertical")
# print ("______________________________")
# main("nirvana", 20, "vertical")
# print ("______________________________")
# main("SOAD", 20, "vertical")
# print ("______________________________")

# print ("______________________________")
# main("GOAT", 8, "horizontal")
# print ("______________________________")
# main("nirvana", 4, "horizontal")
# print ("______________________________")
# main("SOAD", 4, "horizontal")
# print ("______________________________")

print ("______________________________")

# main("GreatDepression", 25, "horizontal") #12:32
# print ("______________________________")  #12:43
main("GreatDepression", 29, "vertical")     #12:46
print ("______________________________")    # 13:03


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

print ("Pour : 8X1 + 11/3 X2 + 15 X3 : ")
# print(decomposeExpr("8X1 + 11/3 X2 + 15 X3"))
print(str2Expr("8X1 + 11/3 X2 + 15 X3"))

print ("__________________________________________________ ")

print ("Pour : 8X1 + 11/3X2 + 15X3 +7 X4 <= 10 : ")
# print(decomposeExpr("8X1 + 11/3X2 + 15X3 +7 X4 <= 10"))
print(str2Expr("8X1 + 11/3X2 + 15X3 +7 X4 <= 10"))

print ("__________________________________________________ ")

print ("Pour : 8X1 +11/3X2+ 11 X3 = 10 : ")
# print(decomposeExpr("8X1 +11/3X2+ 11 X3 = 10 "))
print(str2Expr("8X1 +11/3X2+ 11 X3 = 10 "))
print ("__________________________________________________ ")

print ("Pour : 0 >= X1 <= 1 : ")
# print(decomposeExpr("0 >= X1 <= 1"))
print(str2Expr("0 >= X1 <= 1"))
print ("__________________________________________________ ")

#print( "Pour : ", R.strVerticalSlotsConstraints(0,0))
# print(decomposeExpr(R.strVerticalSlotsConstraints(0,0)))
print(str2Expr(R.strVerticalSlotsConstraints(0,0)))

print ("__________________________________________________ ")


#print( "Pour : ", R.strDominoConstraints(0,0, height, width, 5))
# print(decomposeExpr(R.strDominoConstraints(0,0)))
# print(str2Expr(R.strDominoConstraints(0, 0, 5, 5, 5)))


"""