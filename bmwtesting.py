#[bmw] some testing
"""
current status:
    creates pyqt window
    adds toolbar
    keyboard shortcut to quit
    mouse bindings to move box around
    dialog box popup (in commented code)
    box class (separate from another)
    movable boxes

todo:
    extend box object
    wires
    and the rest of the project

"""

import sys
from PyQt4 import QtGui, QtCore

class MainBox(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)

        self.resize(500, 500) #[bmw] window size
        self.setWindowTitle('PyQt Testing!') #[bmw] window title

        self.boxArea = BoxArea() #[bmw] declare boxarea (defined below) - will contain the boxes to move around
        self.setCentralWidget(self.boxArea) #[bmw] set boxarea as central widget - central widgets take up the rest of the space (after some space is taken up by toolbar, etc)

        #addNode = QtGui.QAction(QtGui.QIcon('lambda.png'), 'Add Node', self)
        addNode = QtGui.QAction('Add Node', self)
        addNode.setShortcut('Ctrl+Shift+N')
        addNode.setStatusTip('Add a new node')
        self.connect(addNode, QtCore.SIGNAL('triggered()'), self.boxArea.addNode)

        addInput = QtGui.QAction('Add Input', self)
        addInput.setStatusTip('Add an input to selected node')
        self.connect(addInput, QtCore.SIGNAL('triggered()'), self.boxArea.addInput)

        addOutput = QtGui.QAction('Add Output', self)
        addOutput.setStatusTip('Add an output to selected node')
        self.connect(addOutput, QtCore.SIGNAL('triggered()'), self.boxArea.addOutput)
        

        #exit = QtGui.QAction(QtGui.QIcon('x.png'), 'Exit', self) #[bmw] set exit action, assign an image to it
        exit = QtGui.QAction('Exit', self) #[bmw] set exit action, assign an image to it
        exit.setShortcut('Ctrl+Q') #[bmw] set keyboard shortcut (cmd q on osx)
        exit.setStatusTip('Exit application') #tooltip
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()')) #[bmw] binds exit's signal so that if it's triggered(), the application will close()

        self.statusBar().showMessage("Ready!") #[bmw] status bar message

        menubar = self.menuBar() #[bmw] grab menu bar pointer
        menuFile = menubar.addMenu('&File') #[bmw] add a new menu
        menuFile.addAction(exit) #[bmw] add exit to that menu

        menuNode = menubar.addMenu('&Node')
        menuNode.addAction(addNode)
        menuNode.addAction(addInput)
        menuNode.addAction(addOutput)
        

        toolbar = self.addToolBar('Toolbar') #[bmw] make a new toolbar
        toolbar.addAction(addNode) #[bmw] add exit to toolbar
        toolbar.addAction(addInput)
        toolbar.addAction(addOutput)
        #toolbar.addAction(exit) #[bmw] add exit to toolbar

        self.raise_() #[bmw] grab focus on creation

class HasNode(QtGui.QFrame):
    def __init__(self, parent=None):
        self.inputs = []
        self.outputs = []
        super(HasNode, self).__init__(parent)
        self.frameRect = QtCore.QRect()
        self.setFrameStyle(1)
        self.moving = False
        self.resizing = False
        self.clickedOffset = QtCore.QPoint()
        
        self.button = QtGui.QPushButton('Edit', self) #[bmw] dialog button creation
        self.button.setFocusPolicy(QtCore.Qt.NoFocus) #[bmw] sets focus policy
        self.connect(self.button, QtCore.SIGNAL('clicked()'), 
            self.showDialog) #[bmw] binds button to showDialog()
        self.setFocus() 
        self.text = QtGui.QLabel(self) #[bmw] creates lineedit "output"
        
        self.resize(120,75)
        self.setAutoFillBackground(True)
        self.setLineWidth(1)
        
        
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
        super(HasNode, self).resize(x,y)
        self.text.resize(x-20,y-40)
        self.button.move(x-70,y-30)

        yincr = 0
        for inp in self.inputs:
            inp.move(x-20,yincr)
            yincr = yincr + 30
            
        yincr = 0
        for outp in self.inputs:
            outp.move(0,yincr)
            yincr = yincr + 30

    def mouseReleaseEvent(self, event): #[bmw] handles mouse click releases
        if event.button() == QtCore.Qt.LeftButton and self.resizing:
            self.mouseMoveEvent(event)
            self.resizing = False #[bmw] so we know to not move anymore
        if event.button() == QtCore.Qt.LeftButton and self.moving: 
            self.mouseMoveEvent(event)
            self.moving = False #[bmw] so we know to not move anymore
            
    def showDialog(self): #[bmw] dialog box to edit input
        text, ok = QtGui.QInputDialog.getText(self, 'Input', 
            'Enter something:')
        if ok:
            self.text.setText(str(text))

    def reqFocus(self, node):
        self.parent().reqFocus(node) #[bmw] recurse until @ boxarea

    def reqMovingLink(self, link):
        self.parent().reqMovingLink(link)

    def setFocus(self):
        self.setLineWidth(2)
        
    def loseFocus(self):
        self.setLineWidth(1)

    def addInput(self):
        self.inputs.append(HasNodeInput(self))

    def remInput(self):
        self.inputs.pop()
        
    def addOutput(self):
        self.outputs.append(HasNodeOutput(self))

    def remOutput(self):
        self.outputs.pop()
            
class HasNodeIOVar(QtGui.QFrame):
    ioVarId = 0
    def __init__(self, parent=None):
        super(HasNodeIOVar, self).__init__(parent)
        self.text = QtGui.QLabel(self)
        self.resize(20,20)
        self.frameRect = QtCore.QRect()
        self.setFrameStyle(1)
        self.ioVarId = HasNodeIOVar.ioVarId
        HasNodeIOVar.ioVarId = HasNodeIOVar.ioVarId + 1
        
class HasNodeInput(HasNodeIOVar):
    def __init__(self, parent=None):
        super(HasNodeInput, self).__init__(parent)
    def mousePressEvent(self, event):
        self.parent().reqSinkMovingLink(self)
        
class HasNodeOutput(HasNodeIOVar):
    def __init__(self, parent=None):
        super(HasNodeOutput, self).__init__(parent)
    def mousePressEvent(self, event):
        self.parent().reqMovingLink(HasLink(self))
        

class HasLink(QtCore.QLine):
    linkId = 0
    def __init__(self, source = None, sink = None):
        super(HasLink,self).__init__()
        self.source = source
        self.sink = sink
        self.linkId = HasLink.linkId
        HasLink.linkId = HasLink.linkId + 1

    def updateLinks(self,reference):
        if self.source is not None:
            self.setP1(self.source.mapTo(reference,QtCore.QPoint(0,0)))
        if self.sink is not None:
            self.setP2(self.sink.pos())

class HasLinkList(dict): #is there a better way of doing htis? currently stores dictionary by id, but also dictionary by source and by sink
    def __init__(self):
        super(HasLinkList,self).__init__()
        self.sourceDict = {}
        self.sinkDict = {}
    def addLink(self,newLink):
        self[newLink.linkId] = newLink
        if newLink.source.ioVarId not in self.sourceDict:
            self.sourceDict[newLink.source.ioVarId] = []
        self.sourceDict[newLink.source.ioVarId].append(newLink)
        if newLink.sink.ioVarId not in self.sinkDict:
            self.sinkDict[newLink.sink.ioVarId] = []
        self.sinkDict[newLink.sink.ioVarId].append(newLink)
    def remLink(self,oldLink):
        sourceIOid = oldLink.source.ioVarId
        sinkIOid = oldLink.sink.ioVarId
        linkId = oldLink.linkId
        self.sourceDict.pop(sourceIOid)
        self.sinkDict.pop(sinkIOid)
        self.pop(linkId)
    def byLink(self):
        return self
    def bySource(self):
        return self.sourceDict
    def bySink(self):
        return self.sinkDict
    


class BoxArea(QtGui.QWidget): #[bmw] boxarea widget to contain our moving boxes and stuff
    def __init__(self, parent=None):
        super(BoxArea, self).__init__(parent)

        self.frames = [] #[bmw] list of frames (added to using addNode)
        self.curFocus = None

        self.linkList = HasLinkList()
        self.movingLink = None
        

    def addExistingNode(self, node):
        self.frames.append(node)
        
    def addNode(self): #[bmw] interface to outside to add a basic node of 30,100 at 0,0
        newNode = HasNode(self)
        self.addExistingNode(newNode)
        newNode.show()

    def addInput(self):
        if self.curFocus is not None:
            self.curFocus.addInput()
        else:
            self.parent().statusBar().showMessage("Cannot add input: no selected node!")
            
    def addOutput(self):
        if self.curFocus is not None:
            self.curFocus.addOutput()
        else:
            parent.statusBar().showMessage("Cannot add output: no selected node!")

    def reqFocus(self, node):
        if self.curFocus is not None:
            self.curFocus.loseFocus()
        node.setFocus()
        self.curFocus = node

    def reqMovingLink(self, link):
        self.movingLink = link

    def paintEvent(self, event):
        super(BoxArea, self).paintEvent(event)
        map(lambda x: x.updateLinks(), self.linkList)
        qp = QtGui.QPainter(self)
        qp.setPen(QtCore.Qt.black)
        for link in self.linkList:
            qp.drawLine(link)
        if self.movingLink is not None:
            self.movingLink.updateLinks(self)
            qp.drawLine(self.movingLink)
        self.update()
            
    def mouseMoveEvent(self, event): #[bmw] handles mouse movement
        if self.movingLink is not None:
            self.movingLink.setP2(event.pos())


# Every PyQt4 application must create an application object.
# The application object is located in the QtGui module.
a = QtGui.QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
# We provide the default constructor for QWidget. The default constructor has no parent.
# A widget with no parent is called a window. 
w = QtGui.QWidget()

qb = MainBox()
#qb = HasNode()
qb.show()

qb.boxArea.addNode()

sys.exit(a.exec_())  # Finally, we enter the mainloop of the application.
