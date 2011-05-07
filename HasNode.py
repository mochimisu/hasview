import sys
from PyQt4 import QtGui, QtCore

import HasSyn

class NodeAreaViewer(QtGui.QGraphicsView):
    def resizeEvent(self, event):
        self.scene().mainContainer.resizeFrame(event.size().width(), event.size().height())
        super(NodeAreaViewer, self).resizeEvent(event)

class NodeArea(QtGui.QGraphicsScene):
    """Container for Nodes. Used for the main window's central widget."""
    def __init__(self, parent=None):
        """Create a NodeArea
        NodeArea is a GraphicsScene that contains all our nodes and connectors.

        """
        super(NodeArea, self).__init__(parent)

        self.viewer = QtGui.QGraphicsView(self)
        self.mainContainer = MainNode() #maincontainer breaks the dragging bezier by mouse, but it is also broken for nested nodes, so we should fix that issues instead of not using a container node
        self.addItem(self.mainContainer)
        self.mainContainer.resizeFrame(self.width(), self.height())


    def addNodeByClass(self, nodeType):
        """Adds a GraphicsItem to our scene and gives it focus"""
        if self.focusItem() and self.focusItem().canHoldStuff:
            #Apparently when called with a non-None parent, it adds itself to the scene...
            node = nodeType(self.focusItem())
        else:
            node = nodeType(self.mainContainer)
            self.addItem(node)
            self.setFocusItem(node)

    def addNode(self):
        """[bmw] interface to outside to add a basic node."""
        self.addNodeByClass(BaseNode)

    def addHasScriptNode(self):
        """A HasScriptNode will be added and given focus
        HasScriptNode supports input / output links

        """
        self.addNodeByClass(HasScriptNode)

    def addConstantNode(self):
        """better way to do this than to make 1000 functions?"""
        self.addNodeByClass(ConstantNode)

    def addNamedFunctionNode(self):
        """better way to do this than to make 1000 functions?"""
        self.addNodeByClass(NamedFunctionNode)

    def addContainerNode(self):
        self.addNodeByClass(ContainerNode)

    def addSplittableContainerNode(self):
        self.addNodeByClass(SplittableContainerNode)

    def addInput(self):
        """[bmw] adds an input box to the node with focus."""
        if self.focusItem():
            self.focusItem().addInput()
        else:
            self.viewer.parent().statusBar().showMessage("Cannot add input: no selected node!")

    def addOutput(self):
        """[bmw] adds an output box to the node with focus"""
        if self.focusItem():
            self.focusItem().addOutput()
        else:
            self.viewer.parent().statusBar().showMessage("Cannot add output: no selected node!")

    def addSplit(self):
        """to add splits to a splittable window"""
        if self.focusItem():
            if isinstance(self.focusItem(), SplittableContainerNode):
                self.focusItem().addSplit()
            else:
                self.viewer.parent().statusBar().showMessage("Cannot add split: Node not splittable!")
        else:
            self.viewer.parent().statusBar().showMessage("Cannot add split: no selected node!")

    def serializeCurrent(self):
        """serializes currently selected node"""
        if self.focusItem():
            #TODO: move this somewhere else (i put this here just to make it show for now)
            msgBox = QtGui.QMessageBox()
            #monospace font
            monoFont = QtGui.QFont("Monospace")
            monoFont.setStyleHint(QtGui.QFont.TypeWriter)
            msgBox.setFont(monoFont)
            serializedList = self.focusItem().serialize()
            outputText = ""
            if len(serializedList) > 0:
                outputText = str(reduce(lambda x,y: x.toHaskell() + "\n" + y.toHaskell(),serializedList))
            else:
                resolved = self.focusItem().resolve()
                if len(resolved) > 0:
                    for resolution in resolved:
                        outputText += resolution.toHaskell()  
            msgBox.setText(outputText)
            #quick hackery to use setDetails for a copy-able compiled thing
            msgBox.setDetailedText(outputText)
            msgBox.exec_()
        else:
            self.viewer.parent().statusBar().showMessage("Cannot serialize: no selected node!")

    def comp(self): #basically a serialization of the main node
        msgBox = QtGui.QMessageBox()
        monoFont = QtGui.QFont("Monospace")
        monoFont.setStyleHint(QtGui.QFont.TypeWriter)
        msgBox.setFont(monoFont)
        serializedTopNodes = []
        
        nodes = filter(lambda child: isinstance(child, BaseNode), self.mainContainer.childItems())
        serialized = self.mainContainer.serialize()[0] #main can only have 1 serialiaztion
        if serialized is not None:
            outputText = serialized.toHaskell()
            msgBox.setText(outputText)
            msgBox.setDetailedText(outputText)
        msgBox.exec_()
        

    def mouseMoveEvent(self, event):
        """mouse movement of node area. super() call allows to drag boxes around, and the rest allows to display lines after an iovar was selected """
        if HasNodeIOVar.current_line is not None:
            if HasNodeIOVar.current_line.sink is None:
                HasNodeIOVar.current_line.sinkLoc = event.scenePos()
            elif HasNodeIOVar.current_line.source is None:
                HasNodeIOVar.current_line.sourceLoc = event.scenePos()

        super(NodeArea, self).mouseMoveEvent(event)
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape and HasNodeIOVar.current_line is not None: #i think we need ==? not sure
            if HasNodeIOVar.current_line.source is not None:
                HasNodeIOVar.current_line.source.links.remove(HasNodeIOVar.current_line)
            if HasNodeIOVar.current_line.sink is not None:
                HasNodeIOVar.current_line.sink.links.remove(HasNodeIOVar.current_line)
            #sometimes segfaults and i dont know why
            HasNodeIOVar.current_line.scene().removeItem(HasNodeIOVar.current_line)
            HasNodeIOVar.current_line = None
        else:
            super(NodeArea, self).keyPressEvent(event)

def setup_default_flags(item,
                        flags = QtGui.QGraphicsItem.ItemIsMovable    | \
                                QtGui.QGraphicsItem.ItemIsSelectable | \
                                QtGui.QGraphicsItem.ItemIsFocusable):
    """Make item (or items) have attributes from flags. By default items are focusable, selectable and movable."""
    if type(item) is list:
        for i in item:
            setup_default_flags(i)
    else:
        item.setFlags(flags)

class HasLine(QtGui.QGraphicsPathItem):
    idCounter = 0
    def __init__(self, source=None, sink=None, parent=None):
        self.source = source
        self.sink = sink

        self.sourceLoc = QtCore.QPointF(0,0)
        self.sinkLoc = QtCore.QPointF(0,0)

        self.cubicPath = QtGui.QPainterPath()
        super(HasLine, self).__init__(self.cubicPath, parent)
        self.name = "l" + str(HasLine.idCounter)
        HasLine.idCounter += 1

    def setSource(self, source):
        self.source = source
        source.links.append(self)
        self.updateLinks()

    def setSink(self, sink):
        self.sink = sink
        sink.links.append(self)
        self.updateLinks()
    
    def updateLinks(self):
        if self.source is not None:
            self.sourceLoc = self.source.mapToScene(self.source.rect().center())
        if self.sink is not None:
            self.sinkLoc = self.sink.mapToScene(self.sink.rect().center())
            
        self.cubicPath = QtGui.QPainterPath(self.sourceLoc)
        self.cubicPath.cubicTo(self.sourceLoc + QtCore.QPointF(100,000),
                               self.sinkLoc + QtCore.QPointF(-100,-100),
                               self.sinkLoc)
        self.setPath(self.cubicPath)
        self.update()



    def setSourceLoc(self, sourceLoc):
        self.sourceLoc = sourceLoc
        self.updateLinks()

    def setSinkLoc(self, sinkLoc):
        self.sinkLoc = sinkLoc
        self.updateLinks()

    def paint(self, qp, option, widget=None):
        self.updateLinks()
        super(HasLine, self).paint(qp, option, widget)


class BaseNode(QtGui.QGraphicsItemGroup):
    idCounter = 0
    intermediateIdCounter = 0
    """Basic Node -- a node can have inputs and outputs, and contains items."""
    def __init__(self, parent=None):
        super(BaseNode, self).__init__(parent)

        self.inputs = []  #[bmw] lists to contain inputs and outputs
        self.outputs = []
        self.canHoldStuff = False #[bmw] to say that it cant hold nodes

        setup_default_flags(self)

        self.setHandlesChildEvents(False)  # we need this to ensure that group components are still interactable

        self.frameRect = QtGui.QGraphicsRectItem()
        newRect = QtCore.QRectF(self.x(), self.y(), 200, 200)
        self.frameRect.setRect(newRect)
        self.addToGroup(self.frameRect)
        
        
        #startPos = QtCore.QPointF(0,0)

        #self.resizeFrame(200,200, startPos.x(), startPos.y())  #default size

        # if we want syntax highlighting for Haskell Nodes s/QLabel/QTextEdit
        # and subclass QSyntaxHighlighter
        self.name = "n" + str(BaseNode.idCounter)
        BaseNode.idCounter += 1

        self.isResizing = False
        self.clickedOffset = QtCore.QPointF()
        
        self.setAcceptHoverEvents(True)

    def addInput(self):
        new_input = HasNodeInput(len(self.inputs), parent=self)
        self.inputs.append(new_input)

    def addOutput(self):
        new_output = HasNodeOutput(len(self.outputs), parent=self)
        self.outputs.append(new_output)

    def serialize(self):
        """Serialization is the list of function definition/instantiation"""
        return [None]

    def resolve(self):
        """Resolution is the actual function call"""

        firstInputVar = self.inputs[0].name
        firstOutputVar = self.outputs[0].name
        return [HasSyn.Resolution(HasSyn.VarList([firstInputVar]),firstOutputVar)]
    
    def mousePressEvent(self, event):
        super(BaseNode, self).mousePressEvent(event)
        localMousePos = self.mapToItem(self.frameRect,event.pos())

        if event.button() == QtCore.Qt.LeftButton and (localMousePos.x() > (self.frameRect.rect().width()-20)) and (localMousePos.y() > (self.frameRect.rect().height()-20)): #check for 10px by 10px box on bottom right (better to not hardcode?)
            self.isResizing = True
            self.clickedOffset = QtCore.QPointF(self.frameRect.rect().width() - localMousePos.x(), self.frameRect.rect().height() - localMousePos.y())

        

    def mouseReleaseEvent(self, event):
        super(BaseNode, self).mouseReleaseEvent(event)
        self.isResizing = False
        

    def focusInEvent(self, event):
        super(BaseNode, self).focusInEvent(event)

    def focusOutEvent(self, event):
        super(BaseNode, self).focusOutEvent(event)
    
    def paint(self, qp, opt, widget):
        newPen = QtGui.QPen(qp.pen())
        newPen.setWidth(3)
        qp.setPen(newPen)
        super(BaseNode, self).paint(qp,opt,widget)    

    def resizeFrame(self, width, height, posx=0, posy=0):
        temp = self.frameRect
        self.frameRect.setRect(posx, posy, width, height)
        #quick hacky way to make it update itself.. how do you actually make it update?
        self.removeFromGroup(temp)
        self.addToGroup(temp)
        map(lambda iovar: iovar.update(), self.inputs)
        map(lambda iovar: iovar.update(), self.outputs)

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.isResizing:
            btmRtPt = self.mapToItem(self.frameRect,event.pos())# + self.clickedOffset
            if(btmRtPt.x() > 10 and btmRtPt.y() > 10): #make sure box is >10px in every dimension
                #self.prepareGeometryChange()
                #self.frameRect.setRect(self.frameRect.x(), self.frameRect.y(), btmRtPt.x(), btmRtPt.y())
                self.resizeFrame(btmRtPt.x(), btmRtPt.y())
        else:
            super(BaseNode, self).mouseMoveEvent(event)

    def rename(self, name):
        self.name = name



class ContainerNode(BaseNode):
    def __init__(self, parent=None):
        self.inputTunnel = []
        self.outputTunnel = []
        super(ContainerNode, self).__init__(parent)
        self.canHoldStuff = True

    
    def addInput(self):
        outerInput = HasNodeInput(len(self.inputTunnel), parent=self)
        innerInput = HasNodeInputInner(len(self.inputTunnel), parent=self)
        self.inputTunnel.append(ContainerIOVar(innerInput, outerInput))
        self.inputs.append(outerInput)

    def addOutput(self):
        outerOutput = HasNodeOutput(len(self.outputTunnel), parent=self)
        innerOutput = HasNodeOutputInner(len(self.outputTunnel), parent=self)
        self.outputTunnel.append(ContainerIOVar(innerOutput, outerOutput))
        self.outputs.append(outerOutput)

    def resolve(self):
        #returns list of (list of bindings, resolution for binding)
        #calling of the function: out = foo in
        outVars = HasSyn.VarList()
        inVars = HasSyn.VarList()

        #grab names of outer output links
        for outp in self.outputTunnel:
            links = outp.outer.links
            for link in links:
                outVars.addVar(link.name)

        #and grab names of outer input links
        for inp in self.inputTunnel:
            links = inp.outer.links
            for link in links:
                inVars.addVar(link.name)

        #and construct the string of the haskell equivalent
        functionCall = self.name + " "
        functionCall += inVars.toHaskellSpace() 
        
        return [HasSyn.Resolution(outVars, functionCall)]
    
    def serialize(self): 
        #go backwards from outputs
        inVars = HasSyn.VarList()
        outVars = HasSyn.VarList()
        resolutions = {}
        body = HasSyn.SerializationBody()

        #find inputs
        inVars.extendList(map(lambda inTun: inTun.inner.name, self.inputTunnel))

        #add link name resolution from inputs (multiple wires from input)
        for inp in map(lambda inTun: inTun.inner, self.inputTunnel):
            for link in inp.links:
                resolutions[link.name] = HasSyn.Resolution(HasSyn.VarList([link.name]), inp.name)
        
        #find outputs and resolutions
        for out in self.outputTunnel:
            curLink = out.inner.links[0] #current link connected to output node
            outVars.addVar(curLink.name) #we want this to be one of our tuple'd haskell function outputs
            resolutions.update(self.resolveUntilInput(curLink.source)) #recursively call link until it is at an input
    
        #serializations of children
        childrenNodes = filter(lambda x: isinstance(x,BaseNode), self.childItems())
        for child in childrenNodes:
            serializedList= child.serialize()
            for serialized in serializedList:
                if serialized is not None:
                    binding = serialized.name + " " + serialized.args.toHaskellSpace()
                    resolutions[binding] = HasSyn.Resolution(HasSyn.VarList([binding]), serialized.body.toHaskell(len(binding) + 3))
        

        body.addLets(resolutions.values())
        body.addIns(outVars)

        return [HasSyn.Serialization(self.name, inVars, body)]

    def resolveUntilInput(self, sourceVar):
        #recursion from link until input link, using source output IOVar
        
        #if sourceVar.name in map(lambda inp: inp.inner.name, self.inputTunnel):
        if sourceVar.parentItem() is self:
            return {}
        else:

            curNode = sourceVar.parentItem()
            curDict = {}

            for output in curNode.outputs:
                for link in output.links:
                    resolved= curNode.resolve()
                    for resolution in resolved:
                        curDict[resolution.varList.toHaskellParen()] = resolution
            for inp in curNode.inputs:
                for link in inp.links:
                    curDict.update(self.resolveUntilInput(link.source))

            return curDict

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            newName, ok = QtGui.QInputDialog.getText(None, 'Set New Name For ' + str(self.name), 'Enter New Name')
            if ok:
                self.rename(newName)
        else:
            super(ContainerNode, self).mousePressEvent(event)

    def resizeFrame(self, width, height, posx = 0, posy = 0):
        super(ContainerNode, self).resizeFrame(width, height, posx, posy)
        #update inners beacuse the outers are taken care of by super
        map(lambda tunnel: tunnel.inner.update(), self.inputTunnel)
        map(lambda tunnel: tunnel.inner.update(), self.outputTunnel)

    def paint(self, qp, option, widget=None):
        super(ContainerNode, self).paint(qp, option, widget)
        curFont = qp.font()
        curFont.setBold(True)
        qp.setFont(curFont)
        qp.drawText(self.frameRect.pos() + QtCore.QPointF(25,15), QtCore.QString(self.name))

#allows for multiple definitions of a single function, preserving order in serialization
class SplittableContainerNode(ContainerNode):
    def __init__(self, parent=None):
        super(SplittableContainerNode, self).__init__(parent)
        self.resizeFrame(300,300)
        self.splitWindows = []
        self.addSplit()

    def addInput(self):
        outerInput = HasNodeInput(len(self.inputTunnel), parent=self)
        container = SplittableContainerIOVar(None, outerInput)
        for split in self.splitWindows:
            container.addInner(split.addInputFromSplitter(outerInput))
        self.inputTunnel.append(container)
        self.inputs.append(outerInput)

    def addOutput(self):
        outerOutput = HasNodeOutput(len(self.outputTunnel), parent=self)
        container = SplittableContainerIOVar(None, outerOutput)
        for split in self.splitWindows:
            container.addInner(split.addOutputFromSplitter(outerOutput))
        self.outputTunnel.append(container)
        self.outputs.append(outerOutput)

    def addSplit(self):
        newSplit = SplitWindowContainerNode(self, self.name)
        self.splitWindows.append(newSplit)
        for inp in self.inputTunnel:
            inp.addInner(newSplit.addInputFromSplitter(inp.outer))
        for out in self.outputTunnel:
            out.addInner(newSplit.addOutputFromSplitter(out.outer))

    def serialize(self):
        serializedListsWithPos = map(lambda split: (split.pos(), split.serialize()), self.splitWindows)
        #better way to flatten?
        serializedFlattenedWithPos = []
        for posSplit in serializedListsWithPos:
            for serialization in posSplit[1]:
                serializedFlattenedWithPos.append((posSplit[0], serialization))
        sortedWithPos = sorted(serializedFlattenedWithPos, key=lambda posSplit: posSplit[0].y())
        serializedList = map(lambda posSplit: posSplit[1], sortedWithPos)
        return serializedList

    def rename(self, name):
        super(SplittableContainerNode, self).rename(name)
        map(lambda split: split.renameFromParent(name), self.splitWindows)

#contained by SplittableContainerNode
#io tunnels is controlled by parent
class SplitWindowContainerNode(ContainerNode):
    def __init__(self, parent=None, name=None):
        super(SplitWindowContainerNode, self).__init__(parent)
        self.resizeFrame(100,100)
        if name is not None:
            self.name = name

    def addInputFromSplitter(self, outerInput):
        innerInput = HasNodeInputInner(len(self.inputTunnel), parent=self)
        self.inputTunnel.append(ContainerIOVar(innerInput, outerInput))
        return innerInput

    def addOutputFromSplitter(self, outerOutput):
        innerOutput = HasNodeOutputInner(len(self.outputTunnel), parent=self)
        self.outputTunnel.append(ContainerIOVar(innerOutput, outerOutput))
        return innerOutput

    def addInput(self):
        self.parentItem().addInput()

    def addOutput(self):
        self.parentItem().addOutput()

    def renameFromParent(self, name):
        super(SplitWindowContainerNode, self).rename(name)

    def rename(self, name):
        self.parentItem().rename(name)

#quick hacky to get print statement in there
class MainNode(ContainerNode):
    #cannot add input or output
    def __init__(self, parent=None):
        super(MainNode, self).__init__(parent)
        super(MainNode, self).addOutput()
        self.name = "main"

    def addInput(self):
        None
    def addOutput(self):
        None
    def serialize(self):
        serialized = super(MainNode, self).serialize()
        serialized[0].body.setInFunction("print") #main node can not have multiple serializations
        return serialized
    def mouseMoveEvent(self, event):
        return None

class HasScriptNode(ContainerNode):
    """Haskell Script Node -- contains haskell code, the equivalent of MathScript nodes in LabView."""
    def __init__(self, parent=None):
        super(HasScriptNode, self).__init__(parent)
        self.canHoldStuff = False

        self.text = QtGui.QGraphicsTextItem("Enter Text Here")
        text_flags = QtCore.Qt.TextEditorInteraction
        self.text.setTextInteractionFlags(text_flags)
        self.text.moveBy(25,20)
        self.text.setTextWidth(150) #default
        self.addToGroup(self.text)

        # syntax highlighting is fun! Have some for breakfast.
        highlighter = HasHighlighter(self.text.document())

        setup_default_flags(self)

    def serialize(self):
        inVars = HasSyn.VarList(map(lambda inTun: inTun.inner.name, self.inputTunnel))
        body = HasSyn.SerializationBody()
        body.setHaskell(self.text.toPlainText())
        return [HasSyn.Serialization(self.name, inVars, body)]
    
    def resizeFrame(self, width, height, posx=0, posy=0):
        super(HasScriptNode, self).resizeFrame(width, height, posx, posy)
        self.text.setTextWidth(width-50)

class ConstantNode(BaseNode):
    """Constant value used as an output only"""
    def __init__(self, parent=None):
        super(ConstantNode, self).__init__(parent)


        self.resizeFrame(75,30)

        #self.removeFromGroup(self.frameRect)
        #self.frameRect.setRect(QtCore.QRectF(0, 0, 125, 25))
        #self.addToGroup(self.frameRect)

        self.text = QtGui.QGraphicsTextItem("Constant")
        text_flags = QtCore.Qt.TextEditorInteraction
        self.text.setTextInteractionFlags(text_flags)
        self.addToGroup(self.text)
        
        setup_default_flags(self)

        self.addOutput()
    
    def resolve(self): #ex: 2 (is this same thing as namedfunction with no input?)
        resolutions = []
        for output in self.outputs:
            for link in output.links:
                resolutions.append(HasSyn.Resolution(HasSyn.VarList([link.name]),
                                                     self.text.toPlainText()))
        return resolutions

class NamedFunctionNode(BaseNode):
    """Named function"""
    def __init__(self, parent=None):
        super(NamedFunctionNode, self).__init__(parent)

        self.removeFromGroup(self.frameRect)
        self.frameRect.setRect(QtCore.QRectF(self.x(), self.y(), 125, 25))
        self.addToGroup(self.frameRect)

        self.text = QtGui.QGraphicsTextItem("Function Name")
        text_flags = QtCore.Qt.TextEditorInteraction
        self.text.setTextInteractionFlags(text_flags)
        self.addToGroup(self.text)
        
        setup_default_flags(self)

        self.addOutput()

    def resolve(self): #ex: foo a b

        funcCall = "(" + self.text.toPlainText() + " " + \
                   reduce(lambda x,y: x + " " + y,
                          map(lambda inp: inp.links[0].name,
                              self.inputs),
                          "") + \
                    ")"
        """
        outVars = HasSyn.VarList()
        for output in self.outputs:
            for link in output.links:
                outVars.addVar(link.name)
        return [HasSyn.Resolution(outVars,funcCall)]
        """
        resolutions = []
        for output in self.outputs:
            for link in output.links:
                resolutions.append(HasSyn.Resolution(HasSyn.VarList([link.name]), funcCall))
        return resolutions


class HasTextNode(QtGui.QGraphicsTextItem):
    """Wrapper around QGraphicsTextItem. Will be edited to have syntax highlighting."""
    def __init__(self, parent=None):
        super(HasTextNode, self).__init__(parent)

    def addInput(self):
        return self.parentItem().addInput()

    def addOutput(self):
        return self.parentItem().addOutput()


class HasNodeIOVar(QtGui.QGraphicsRectItem):
    """Basic IO box for nodes."""
    current_line = None
    idCounter = 0

    def __init__(self, parent=None):
        super(HasNodeIOVar, self).__init__(parent)
        setup_default_flags(self,
                            flags = QtGui.QGraphicsItem.ItemIsSelectable | \
                                    QtGui.QGraphicsItem.ItemIsFocusable)
        self.links = []
        self.name = "x"+str(HasNodeIOVar.idCounter)
        HasNodeIOVar.idCounter = HasNodeIOVar.idCounter + 1

    def updateRelativePos(self):
        return None

    def update(self):
        self.updateRelativePos()
        super(HasNodeIOVar, self).update()

    def addInput(self):
        return self.parentItem().addInput()

    def addOutput(self):
        return self.parentItem().addOutput()

    def paint(self, qp, option, widget=None):
        super(HasNodeIOVar, self).paint(qp, option, widget)
        qp.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, QtCore.QString(self.name))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            newName, ok = QtGui.QInputDialog.getText(None, 'Set New Name For ' + str(self.name), 'Enter New Name')
            if ok:
                self.name = newName
        else:
            super(HasNodeIOVar, self).mousePressEvent(event)

class HasNodeInput(HasNodeIOVar):
    """Input box for nodes -- will be placed on the left of a node"""
    def __init__(self, num_prev_inputs, parent=None):
        super(HasNodeInput, self).__init__(parent)
        self.localCounter = num_prev_inputs
        self.update()
    
    def updateRelativePos(self):
        cornerPos = self.parentItem().frameRect.pos()
        self.setRect(-20 + cornerPos.x(),                   # place on left side
                    20 * self.localCounter + cornerPos.y(),  # account for earlier inputs
                    20,                    # 20x20 is a reasonable box size
                    20)

    def mouseDoubleClickEvent(self, event):
        if HasNodeIOVar.current_line is not None:
            if HasNodeIOVar.current_line.sink is None:
                HasNodeIOVar.current_line.setSink(self)
                HasNodeIOVar.current_line = None
        else:
            HasNodeIOVar.current_line = HasLine()
            HasNodeIOVar.current_line.setSink(self)
            self.scene().addItem(HasNodeIOVar.current_line)


class HasNodeOutput(HasNodeIOVar):
    """Output box for nodes."""
    def __init__(self, num_prev_outputs, parent=None):
        super(HasNodeOutput, self).__init__(parent)
        self.localCounter = num_prev_outputs
        self.update()
    
    def updateRelativePos(self):
        cornerPos = self.parentItem().frameRect.pos() + QtCore.QPointF(self.parentItem().frameRect.rect().width(), 0)
        #cornerPos = self.parentItem().frameRect.rect().topRight()
        self.setRect(cornerPos.x(),   # find the right index to use [haha]
                     20 * self.localCounter + cornerPos.y(),                             # account for earlier inputs
                     20,
                     20)


    def mouseDoubleClickEvent(self, event):
        if HasNodeIOVar.current_line is not None:
            if HasNodeIOVar.current_line.source is None:
                HasNodeIOVar.current_line.setSource(self)
                HasNodeIOVar.current_line = None
        else:
            HasNodeIOVar.current_line = HasLine()
            HasNodeIOVar.current_line.setSource(self)
            self.scene().addItem(HasNodeIOVar.current_line)

class HasNodeInputInner(HasNodeOutput):
    def __init__(self, num_prev_inputs, parent=None):
        super(HasNodeInputInner, self).__init__(num_prev_inputs, parent)

    def updateRelativePos(self):
        cornerPos = self.parentItem().frameRect.pos()
        self.setRect(cornerPos.x(),
                     20 * self.localCounter +  + cornerPos.y(),
                     20,                    
                     20)

class HasNodeOutputInner(HasNodeInput):
    def __init__(self, num_prev_outputs, parent=None):
        super(HasNodeOutputInner, self).__init__(num_prev_outputs, parent)

    def updateRelativePos(self):
        cornerPos = self.parentItem().frameRect.pos() + QtCore.QPointF(self.parentItem().frameRect.rect().width(), 0)

        self.setRect(cornerPos.x()-20,
                     20 * self.localCounter + cornerPos.y(),
                     20,
                     20)

class ContainerIOVar: 
    #contains both container "input" and "output": makes a tunnel
    def __init__(self, inner, outer):
        self.inner = inner
        self.outer = outer

class SplittableContainerIOVar:
    def __init__(self, inners, outer):
        if inners is None:
            self.inners = []
        else:
            self.inners = inners
        self.outer = outer

    def addInner(self, iovar):
        self.inners.append(iovar)
    

class HasHighlighter(QtGui.QSyntaxHighlighter):
    """Defining syntax highlighting schemas for Haskell"""
    def __init__(self, parent):
        super(HasHighlighter, self).__init__(parent)

    def highlightBlock(self, text):
        """This function, called on each change to its parent textItem, will do syntax highlighting.

        To add a new highlighting rule, add a pattern_map entry with a QRegExp key,
        and a QTextCharFormat value.

        """
        pattern_map = {}

        typedef_highlight = QtGui.QTextCharFormat()
        typedef_highlight.setForeground(QtCore.Qt.red)
        typedef_pattern = QtCore.QString("::(?!:)")
        typedef_expression = QtCore.QRegExp(typedef_pattern)
        pattern_map[typedef_expression] = typedef_highlight

        comment_highlight = QtGui.QTextCharFormat()
        comment_highlight.setForeground(QtGui.QColor(18, 73, 74))  # using colors from syntax-highlight
        comment_pattern = QtCore.QString("\\-\\-.*")
        comment_expression = QtCore.QRegExp(comment_pattern)
        pattern_map[comment_expression] = comment_highlight

        punctuation_highlight = QtGui.QTextCharFormat()
        punctuation_highlight.setForeground(QtCore.Qt.darkRed)
        punctuation_pattern = QtCore.QString("[\\[|\\]|\\(|\\)|=|\\,|(\\->)]")
        punctuation_expression = QtCore.QRegExp(punctuation_pattern)
        pattern_map[punctuation_expression] = punctuation_highlight

        # Note that the documentation for how to do this at
        # http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qsyntaxhighlighter.html#highlightBlock
        # is _very_ wrong. exp.matchedLength() only works if used in conjunction with indexIn().
        for exp, pattern in pattern_map.items():
            index = exp.indexIn(text)
            while index >= 0:
                length = exp.matchedLength()
                self.setFormat(index, length, pattern)
                index = exp.indexIn(text, index + length)
