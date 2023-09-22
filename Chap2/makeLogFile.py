# =============== DATA ===============
# =============== CODE ===============
lpMathSymbols = ["+", "-", "=", "<=", "<", ">", ">="]
otherMathSymbols = ["/", "*", "^"]

def main(fileName):

    # =============== MIN/MAX ===============

    minimizeOrMaximize = input('Minimize Or Maximize ? ')
    expr = input('Enter the expression you want to process :')

    writeMinimizeOrMaximize(minimizeOrMaximize, expr, fileName)     
    

    # =============== RESTRICTIONS ===============

    subject_to = []     
    stopFlag = 1      
    new_restriction = ''
    while stopFlag != 0:
        stopFlag = int(input("Would you like to add a restriction ?"))
        if stopFlag != 0:
            new_restriction = input("Enter a restriction equation: ")
            subject_to.append(new_restriction)
            
    writeSubjectTo(subject_to, fileName)

    # =============== BOUNDS ===============

    allPositiveFlag = int(input("If you'd simply like all of your variables to be positive, please enter '0'."))
    if allPositiveFlag == 0 :
        writePositiveBounds(getVars(expr), fileName)
    else: 
        bounds = []     
        stopFlag = 1      
        new_bound = ''
        while stopFlag != 0:
            stopFlag = int(input("Would you like to add a new bound? Enter 0 if you don't: "))
            if stopFlag != 0:
                new_bound = input("Enter a new bound: ")
                subject_to.append(new_bound)
        writeBounds(bounds, fileName)
    

    # =============== INTEGERS ===============

    integersFlag = int(input("Do you want all your variables to be integers? Enter 0 if you do: "))
    if integersFlag == 0:
        writeAllIntegers(getVars(expr), fileName)

    write("end", fileName)
     
    return None

def decomposeExpr(expr: str):
    noOp = expr
    for op in lpMathSymbols:
        noOp = noOp.replace(op, " ")
    noOp = noOp.split()

    vars = []
    scalars = []
    operators = expr

    for e in noOp:
        operators = operators.replace(e," ",1)

        curr = "" 
        j = 0
        while j < len(e) and not e[j].isalpha():
            curr += e[j]
            j += 1
        e = e[j:]
        if not curr == "":
            scalars.append(curr)
        if not e == "":
            vars.append(e)
    
    operators = operators.split()
    return scalars, vars, operators 

def getScalars(expr: str):
    return decomposeExpr(expr)[0]
def getVars(expr: str):
    return decomposeExpr(expr)[1]
def getOperators(expr: str):
    return decomposeExpr(expr)[2]

def str2Expr(expr: str):
    t = decomposeExpr(expr)
    
    scalars = getScalars(expr)
    vars = getVars(expr)
    operators = getOperators(expr)
    res = ""
    for i in range (len(scalars)):
        res += scalars[i] + " "
        if i < len(vars) :
            if vars[i] != "":
                res += vars[i] + " "
            else:
                res += " "
        if i < len(operators) :
            if operators[i] != "":
                res += operators[i] + " "
            else:
                res += " "
    
    
    return res

def write(addition: str, fileName):
    f = open(fileName, "a+")
    f.write(addition)
    f.write("\n")
    f.close()

def writeMinimizeOrMaximize(minimizeOrMaximize: str, expr: str, fileName):
    carac = ""
    if minimizeOrMaximize == 'minimize' or 'minimise' or 'min' : carac = 'minimize'
    if minimizeOrMaximize == 'maximize' or 'maximise' or 'max' : carac = 'maximize'
        
    write(carac, fileName)
    write(str2Expr(expr), fileName)

def writeSubjectTo(expressions: list[str], fileName):
    write("subject to", fileName)
    for expr in expressions:
        write(str2Expr(expr), fileName)

def writePositiveBounds(vars, fileName):
    write("bounds", fileName)
    for v in vars:
        write ("0 <= " + v, fileName)

def writeBounds(expressions: list[str], fileName):
    write("bounds", fileName)
    for expr in expressions:
        write(str2Expr(expr), fileName)

def writeAllIntegers(vars: list[str], fileName):
    write("integers", fileName)
    for v in vars:
        write(v, fileName)

# =============== TEST ===============

main("./lpFiles/pythoonLego.lp")
# print(decomposeExpr("8X1 + 11/3 X2 + 15 X3"))