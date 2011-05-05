import sys
import re

class HaskellSynthesizer():
    def toHaskell(self, curSpaces=0):
        return self.__str__(curSpaces)
    def __str__(self, curSpaces=0):
        return (" "*curspaces + super(HaskellSynthesizer,self).__str())


class VarList(HaskellSynthesizer):
    #something weird with python's default args here...
    def __init__(self, initVars=None):
        if initVars is None:
            self.varList = []
        else:
            self.varList = initVars

    def addVar(self, var):
        self.varList.append(var)

    def extend(self, varLs):
        self.varList.extend(varLs.varList)

    def extendList(self, listOfVars):
        self.varList.extend(listOfVars)

    def isEmpty(self):
        return len(self.varList) == 0

    def toHaskellParen(self, curSpaces=0):
        return self.toHaskell(curSpaces)
    def toHaskellSpace(self, curSpaces=0):
        return (" " * curSpaces) + reduce(lambda x,y: x + " " + y, self.varList, "") 
    def __str__(self, curSpaces=0):
        if len(self.varList) > 1:
            return (" " * curSpaces) + "(" + reduce(lambda x,y: x + ", " + y, self.varList, "") + ")"
        elif len(self.varList) == 1:
            return (" " * curSpaces) + self.varList[0]
        else:
            return (" " * curSpaces)

class Resolution(HaskellSynthesizer):
    def __init__(self, varList = None, binding = ""):
        if varList is None:
            self.varList = VarList()
        else:
            self.varList = varList
        self.binding = binding
    def __str__(self, curSpaces=0):
        spacedBinding = str(self.binding)
        spacer = re.compile("\n")        
        spacer.sub("\n"+ " "*curSpaces, spacedBinding)


        return (" " * curSpaces) + self.varList.toHaskellParen() + " = " + spacedBinding

class SerializationBody(HaskellSynthesizer):
    def __init__(self):
        self.letResolutions = []
        self.inVariables = VarList()
        self.whereResolutions = []
        self.haskell = ""

    def addSingleLet(self, resolution):
        self.letResolutions.append(resolution)
    def addSingleIn(self, variable):
        self.varList.variables.addVar(variable)
    def addsingleWhere(self, resolution):
        self.letResolutions.append(resolution)

    def addLets(self, resolutions):
        self.letResolutions.extend(resolutions)
    def addIns(self, varList):
        self.inVariables.extend(varList)
    def addWheres(self, resolutions):
        self.whereResolutions.extend(resolutions)
    
    def setHaskell(self, haskellString):
        self.haskell = haskellString

    def toHaskell(self, curSpaces=0, indentFirst=False):
        return self.__str__(curSpaces,indentFirst)

    def __str__(self, curSpaces=0, indentFirst=True):
        outputStr = ""
        if indentFirst:
            outputstr += " " * curSpaces
        if self.haskell != "":
            spacer = re.compile("\n")
            spacedHaskell = str(self.haskell)

            spacer.sub("\n"+ " "*curSpaces, spacedHaskell)
            outputStr += spacedHaskell
        else:
            if len(self.letResolutions) > 0:
                letSpaces = curSpaces + 4
                outputStr += "let "
                first = True
                for resolution in self.letResolutions:
                    if first:
                        outputStr += resolution.toHaskell()
                    else:
                        outputStr += resolution.toHaskell(letSpaces)
                    outputStr += "\n"
                outputStr += (" "*curSpaces)
            if not self.inVariables.isEmpty():
                outputStr += "in " + self.inVariables.toHaskellParen()
            if len(self.whereResolutions) > 0:
                whereSpaces = curSpaces + 6
                outputStr += "where "
                first = True
                for resolution in self.whereResolutions:
                    if first:
                        outputStr += resolution.toHaskell()
                    else:
                        outputStr += resolution.toHaskell(whereSpaces)
                    outputStr += "\n"
                outputStr += "\n" + (" "*curSpaces)
        return outputStr

class Serialization(HaskellSynthesizer):
    def __init__(self, name="", args=VarList(), body=SerializationBody()):
        self.name = name
        if args is None:
            self.args = VarList()
        else:
            self.args = args
        if body is None:
            self.body = SerializationBody()
        else:
            self.body = body
    def __str__(self, curSpaces=0):
        outputStr = ""
        outputStr += self.name + " "
        if not self.args.isEmpty():
            outputStr += self.args.toHaskellSpace() + " "
        outputStr += "= "
        curSpaces = len(outputStr)
        outputStr += self.body.toHaskell(curSpaces,False)
        return outputStr
