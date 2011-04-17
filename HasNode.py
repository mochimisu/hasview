import sys
from PyQt4 import QtGui, QtCore

"""
Container for Nodes. Used for the main window's central widget.
"""
class NodeArea(QtGui.QWidget): #[bmw] boxarea widget to contain our moving boxes and stuff
    def __init__(self, parent=None):
        super(NodeArea, self).__init__(parent)

        self.frames = [] #[bmw] list of frames (added to using addNode)
        self.curFocus = None #[bmw] pointer for current focused/clicked node (for adding input/output boxes)

        self.linkList = HasLinkList() #[bmw] holds links
        self.movingLink = None #[bmw] pointer for temporary sink-less link (when user is connecting stuff)
        self.setMouseTracking(True) #[bmw] allows to track mouse without clicking
        

    def addExistingNode(self, node): #[bmw] Adds an existing node to the NodeArea
        self.frames.append(node)
        
    def addNode(self): #[bmw] interface to outside to add a basic node
        newNode = BaseNode(self)
        self.addExistingNode(newNode)
        newNode.show()

    def addInput(self): #[bmw] adds an input box to the currently selected node
        if self.curFocus is not None:
            self.curFocus.addInput()
        else:
            self.parent().statusBar().showMessage("Cannot add input: no selected node!")
            
    def addOutput(self): #[bmw] adds an output box to the currently selected node
        if self.curFocus is not None:
            self.curFocus.addOutput()
        else:
            self.parent().statusBar().showMessage("Cannot add output: no selected node!")

    def reqFocus(self, node): #[bmw] request focus for node to be the one in focu
        if self.curFocus is not None:
            self.curFocus.loseFocus()
        node.setFocus()
        self.curFocus = node

    def reqMovingLink(self, link): #[bmw] request link to be used as the moving link
        #TODO: be able to move sink or source
        self.movingLink = link
        self.movingLink.sink = None
        
    def reqSinkMovingLink(self, node): #[bmw] "sinks" the moving link
        if self.movingLink is not None:
            self.movingLink.sink = node
            self.linkList.addLink(self.movingLink)
            self.movingLink = None
        else:
            self.parent().statusBar().showMessage("Cannot sink connection: no current connection!")

    def paintEvent(self, event): #[bmw] because HasLinks extend QLine, they need to be explicitly drawn
        super(NodeArea, self).paintEvent(event)
        qp = QtGui.QPainter(self)
        qp.setPen(QtCore.Qt.black)
        for link in self.linkList.itervalues():
            link.updateLinks(self) #[bmw] JIT update link positions to make the boxes touch
            qp.drawLine(link)
        if self.movingLink is not None: #[bmw] draw moving link
            self.movingLink.updateLinks(self)
            qp.drawLine(self.movingLink)
        self.update() #[bmw] signal to refresh buffer
            
    def mouseMoveEvent(self, event): #[bmw] handles mouse movement
        if self.movingLink is not None:
            self.movingLink.setP2(event.pos()) #[bmw] set sink of moving link


"""
Basic Node
"""
class BaseNode(QtGui.QFrame):
    def __init__(self, parent=None):
        self.inputs = [] #[bmw] lists to contain inputs and outputs
        self.outputs = []
        super(BaseNode, self).__init__(parent)
        self.frameRect = QtCore.QRect() #[bmw] create our containing rectangle
        self.setFrameStyle(1) 
        self.moving = False #[bmw] default value for moving var (if we're being dragged or not)
        self.resizing = False #[bmw] " for resizing var (if we're being resized or not)
        self.clickedOffset = QtCore.QPoint() #[bmw] maintain 2D vector offset (so can click anywhere in box and move relative to that position)
        
        self.button = QtGui.QPushButton('Edit', self) #[bmw] dialog button creation
        self.button.setFocusPolicy(QtCore.Qt.NoFocus) #[bmw] sets focus policy
        self.connect(self.button, QtCore.SIGNAL('clicked()'), 
            self.showDialog) #[bmw] binds button to showDialog()
        self.setFocus() 
        self.text = QtGui.QLabel(self) #[bmw] creates lineedit "output"
        
        self.resize(120,75) #[bmw] default size
        self.setAutoFillBackground(True) #[bmw] don't want to see through the background
        self.setLineWidth(1) #[bmw] unfocused line width

        
        
    def mousePressEvent(self, event): #[bmw] mousepress listener: only handles clicks and not releases
        self.clickedOffset = event.pos()

        if event.button() == QtCore.Qt.LeftButton and (self.clickedOffset.x() > self.width()-10) and (self.clickedOffset.y() > self.height()-10): #check for 10px by 10px box on bottom right (better to not hardcode?)
            self.resizing = True
            self.clickedOffset = QtCore.QPoint(self.width() - self.clickedOffset.x(), self.height() - self.clickedOffset.y())
        elif event.button() == QtCore.Qt.LeftButton: #moving the box
            self.moving = True #[bmw] so we know that we clicked
            
        self.parent().reqFocus(self) #[bmw] inform parent that this box should grab focus (is there a pyqt focus class that does the same hting? i looked quickly and didn't think they were the same -- but are they?)
        
    def mouseMoveEvent(self, event): #[bmw] handles mouse movement
        if (event.buttons() & QtCore.Qt.LeftButton) and self.moving: #[bmw] only move @ left button & moving bool is on
            self.move(self.pos()+event.pos()-self.clickedOffset)
        elif (event.buttons() & QtCore.Qt.LeftButton) and self.resizing: #[bmw] only resize @ left button & resizing bool is on
            btmRtPt = event.pos() + self.clickedOffset;
            if(btmRtPt.x() > 10 and btmRtPt.y() > 10): #[bmw] make sure box is >10px in every dimension
                self.resize(btmRtPt.x(),btmRtPt.y())

    def resize(self, x, y): #[bmw] overloading resize to move text and button to relative positions (hardcoded pos; bad?)
        super(BaseNode, self).resize(x,y)
        self.text.resize(x-20,y-40)
        self.button.move(x-70,y-30)

        yincr = 0 #[bmw] space inputs and outputs. TODO: dynamically?
        for inp in self.inputs:
            inp.move(x-20,yincr)
            yincr = yincr + 30
            
        yincr = 0
        for outp in self.outputs:
            outp.move(0,yincr)
            yincr = yincr + 30

    def mouseReleaseEvent(self, event): #[bmw] handles mouse click releases
        if event.button() == QtCore.Qt.LeftButton and self.resizing:
            self.mouseMoveEvent(event) #[bmw] one last update
            self.resizing = False #[bmw] so we know to not resize anymore
        if event.button() == QtCore.Qt.LeftButton and self.moving: 
            self.mouseMoveEvent(event)
            self.moving = False #[bmw] so we know to not move anymore
            
    def showDialog(self): #[bmw] dialog box to edit input
        text, ok = QtGui.QInputDialog.getText(self, 'Input', 
            'Enter something:')
        if ok:
            self.text.setText(str(text))

    def reqFocus(self, node): #[bmw] child node requested focus from us; we don't deal with that, but NodeArea does
        self.parent().reqFocus(node) #[bmw] recurse until @ nodearea

    def reqMovingLink(self, link): #[bmw] link was request to be moving here; we should deal with this later when we have nested nodes
        self.parent().reqMovingLink(link)
        
    def reqSinkMovingLink(self, link): #[bmw] moving link was requested to be sink'd
        self.parent().reqSinkMovingLink(link)

    def setFocus(self): #[bmw] set focus by increasing border
        self.setLineWidth(2)
        
    def loseFocus(self): #[bmw] lose focus by decreasing border
        self.setLineWidth(1)
        
    def addInput(self): #[bmw] add input box
        newInput = HasNodeInput(self)
        self.inputs.append(newInput)
        newInput.show()
        self.resize(self.width(),self.height())

    def remInput(self): #[bmw] remove input box. TODO: find better way
        self.inputs.pop()
        
    def addOutput(self): #[bmw] add output box
        newOutput = HasNodeOutput(self)
        self.outputs.append(newOutput)
        newOutput.show()
        self.resize(self.width(),self.height())

    def remOutput(self): #[bmw] remove output box. same issue as remInput
        self.outputs.pop()


"""
Basic IO box for nodes
"""
class HasNodeIOVar(QtGui.QFrame):
    ioVarId = 0 #[bmw] class var link ID to be used as index in HasLinkList
    def __init__(self, parent=None):
        super(HasNodeIOVar, self).__init__(parent)
        self.text = QtGui.QLabel(self)
        self.resize(20,20) #[bmw] default size
        self.frameRect = QtCore.QRect()
        self.setFrameStyle(1)
        self.ioVarId = HasNodeIOVar.ioVarId
        HasNodeIOVar.ioVarId = HasNodeIOVar.ioVarId + 1
"""
Input box for nodes
"""
class HasNodeInput(HasNodeIOVar):
    def __init__(self, parent=None):
        super(HasNodeInput, self).__init__(parent)
    def mousePressEvent(self, event): #[bmw] on click, request to sink the link
        self.parent().reqSinkMovingLink(self)
        
"""
Output box for nodes
"""
class HasNodeOutput(HasNodeIOVar):
    def __init__(self, parent=None):
        super(HasNodeOutput, self).__init__(parent)
    def mousePressEvent(self, event):
        tempLink = HasLink(self) #[bmw] create a new temporary link and request it to be the moving link
        self.parent().reqMovingLink(tempLink)
        
"""
Link between nodes. Needs to be explicitly drawn. How to make clickable?
"""
class HasLink(QtCore.QLine):
    linkId = 0 #[bmw] link id used to let dictionary be indexable
    def __init__(self, source = None, sink = None):
        super(HasLink,self).__init__()
        self.source = source #[bmw] contains information of bound source and sink
        self.sink = sink
        self.linkId = HasLink.linkId
        HasLink.linkId = HasLink.linkId + 1

    def updateLinks(self,reference): #[bmw] update positions of local P1 and P2 to the actual locations in reference's coord system. TODO: possibly move reference somewhere else?
        if self.source is not None:
            self.setP1(self.source.mapTo(reference,QtCore.QPoint(0,0)))
        if self.sink is not None:
            self.setP2(self.sink.mapTo(reference,QtCore.QPoint(0,0)))

"""
Dictionary structure for containing the links.
3 representations
HasLinkList.byLink() gives a dictionary indexed by link ID
HasLinkList.bySource() gives a dictionary indexed by source ID
HasLinkList.bySink() gives a dictionary indexed by sink ID
"""
class HasLinkList(dict): #is there a better way of doing htis? currently stores dictionary by id, but also dictionary by source and by sink
    def __init__(self):
        super(HasLinkList,self).__init__()
        self.sourceDict = {} #[bmw] maintain separate dictionaries by source and by sink
        self.sinkDict = {}
    def addLink(self,newLink): #[bmw] add a link, must maintain all 3 dicts
        self[newLink.linkId] = newLink
        if newLink.source.ioVarId not in self.sourceDict:
            self.sourceDict[newLink.source.ioVarId] = []
        self.sourceDict[newLink.source.ioVarId].append(newLink)
        if newLink.sink.ioVarId not in self.sinkDict:
            self.sinkDict[newLink.sink.ioVarId] = []
        self.sinkDict[newLink.sink.ioVarId].append(newLink)
    def remLink(self,oldLink): #[bmw] remove a link, must maintain all 3 dicts
        sourceIOid = oldLink.source.ioVarId
        sinkIOid = oldLink.sink.ioVarId
        linkId = oldLink.linkId
        self.sourceDict.pop(sourceIOid)
        self.sinkDict.pop(sinkIOid)
        self.pop(linkId)
    def byLink(self): #[bmw] access different tables (but all have same information, just indexed differently)
        return self
    def bySource(self):
        return self.sourceDict
    def bySink(self):
        return self.sinkDict
    
