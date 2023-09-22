import Raster as R
from PIL import Image
import subprocess
import os.path

# =============== DATA ===============
# =============== CODE ===============
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]
otherMathSymbols = ["/", "*", "^"]

def getBS(fileImage):
    im = Image.open(fileImage)
    width = im.size[0]
    height = im.size[1]
    potential_bs = []
    for i in range(2,30):
        
        size = ((width // i) * (height // i)) / R.NUMBER_OF_SVG
        eps = 0.001
        if int(size) - eps <= size and size <= int(size) + eps:
            potential_bs.append(int(i))
    print(potential_bs)
    bs = input("wich blocksize would you like ? ")
    return int(bs)

def createLPfile(fileName, image, blocksize):
    imageCropped = image[:image.find('.')] + "Cropped.png"

    print(imageCropped)
    R.cropImage(image, blocksize)

    height = R.getHeight(imageCropped, blocksize)
    width = R.getWidth(imageCropped, blocksize)

    print("number of cartoons to be used each: ", R.numberOfUsesPerSVG(width, height))

    gsMatrix = R.image2matrix(imageCropped, blocksize)

    vars = decomposeExpr(R.strTotalCost(height, width, gsMatrix))[0]
    # =============== MIN/MAX ===============
    
    write('minimize', fileName)
    write(str2Expr(R.strTotalCost(height, width, gsMatrix)), fileName)  
    
    # =============== RESTRICTIONS ===============

    write("subject to", fileName)

    for c in range(R.NUMBER_OF_SVG):
        write(str2Expr(R.strTypeCConstraints(c, height, width)), fileName)

    for i in range(height):
        for j in range(width):
            write(str2Expr(R.strBlockConstraints(i,j)), fileName)


    # =============== BOUNDS ===============
    
    write("binary", fileName)
    for v in vars:
        write(v, fileName)
        
    write("end", fileName)
     
    print("number of vars: ", len(vars))
    return None

def get_c_i_j_from_var(var: str):
    coords = var[2:]
    coords = coords.replace("_"," ")
    coords = coords.split()
    c = coords[0]
    i = coords[1]
    j = coords[2]
    return int(c),int(i),int(j)

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

def solFile2gSmatrix(solFile, image, blocksize):
    height = R.getHeight(image, blocksize)
    width = R.getWidth(image, blocksize)
    matrix = [[0 for i in range(width)] for j in range (height)]

    with open(solFile) as f:
        cpt = 0
        for line in f:
            if cpt != 0:
                var, value = line.split() 
                if value == "1":
                    c,i,j = get_c_i_j_from_var(var)
                    matrix[i][j] = c
            cpt += 1 
    
    return matrix

def boolNumberCartoons(matrix):
    cartoonTab = [0 for i in range(R.NUMBER_OF_SVG)]
    height = len(matrix)
    width = len(matrix[0])
    for i in range(height):
        for j in range(width):
            cartoonTab[matrix[i][j]] += 1
    
    flag = True
    for i in range(R.NUMBER_OF_SVG-1):
        flag = flag and cartoonTab[i] == cartoonTab[i+1]
    print(cartoonTab)
    return flag

def main(fileName):

    rawName = "/home/arthur/Documents/L2/Stage/Chap3/Raw/" + fileName + ".jpg"
    lpName = "/home/arthur/Documents/L2/Stage/Chap3/LPFiles/" + fileName + ".lp"
    solName = "/home/arthur/Documents/L2/Stage/Chap3/SolFiles/" + fileName + ".sol"
    logName = "/home/arthur/Documents/L2/Stage/Chap3/LogFiles/" + fileName + ".log"
    svgName = "/home/arthur/Documents/L2/Stage/Chap3/results/" + fileName + ".svg"

    blocksize = getBS(rawName)

    if os.path.isfile(lpName): os.remove(lpName)

    createLPfile(lpName, rawName, blocksize)

    subprocess.run(["gurobi_cl", "Resultfile=" + solName , "Logfile=" + logName, " Method=0", lpName])

    m = solFile2gSmatrix(solName, rawName, blocksize)
    R.matrix2imageFromExistingSVG(m, svgName)

# =============== TEST ===============

# print ("______________________________")
# main("GOAT")
# print ("______________________________")
# main("nirvana")
# print ("______________________________")
# main("SOAD")
# print ("______________________________")

# print ("______________________________")
# main("GreatDepression")


"""
print ("_______________________ TEST _______________________ ")

blocksize = getBS("GOAT.jpg")
R.cropImage("GOAT.jpg", blocksize)
height = R.getHeight("GOATCropped.png", blocksize)
width = R.getWidth("GOATCropped.png", blocksize)

print("width =", width )
print("height =", height )
print("blocksize =", blocksize )

print ("__________________________________________________ ")

m = [[(i+coefIndex)/10 for i in range (3)] for coefIndex in range (3)]
print (m)
print(R.strTotalCost(3, 3, m))
print(str2Expr(R.strTotalCost(3, 3, m)))  

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

print( "Pour : ", R.strBlockConstraints(0,0))
# print(decomposeExpr(R.strBlockConstraints(0,0)))
print(str2Expr(R.strBlockConstraints(0,0)))

print ("__________________________________________________ ")


print( "Pour : ", R.strTypeCConstraints(0, height, width))
print(decomposeExpr(R.strBlockConstraints(0,0)))
print(str2Expr(R.strTypeCConstraints(0, height, width)))


"""