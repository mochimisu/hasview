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
    wires

todo:
    extend box object
    nested nodes
    and the rest of the project

"""

import sys
from PyQt4 import QtGui, QtCore
import HasNode

class MainBox(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)

        self.resize(500, 500) #[bmw] window size
        self.setWindowTitle('PyQt Testing!') #[bmw] window title

        #self.nodeArea = HasNode.NodeArea() #[bmw] declare area for nodes to move around
        
        self.nodeArea = HasNode.NodeArea() # this is the QGraphicsView for the entire node structure.

        self.setCentralWidget(self.nodeArea.viewer) #[bmw] set boxarea as central widget - central widgets take up the rest of the space (after some space is taken up by toolbar, etc)

        addHasScriptNode = QtGui.QAction('Add Haskell Script Node', self)
        addHasScriptNode.setShortcut('Ctrl+Shift+N')
        addHasScriptNode.setStatusTip('Add a new Haskell Script node')
        self.connect(addHasScriptNode, QtCore.SIGNAL('triggered()'), self.nodeArea.addHasScriptNode)

        addConstantNode = QtGui.QAction('Add Constant Node', self)
        addConstantNode.setStatusTip('Add a new Constant Script node')
        self.connect(addConstantNode, QtCore.SIGNAL('triggered()'), self.nodeArea.addConstantNode)

        addNamedFunctionNode = QtGui.QAction('Add Named Function Node', self)
        addNamedFunctionNode.setStatusTip('Add a new Named Function node')
        self.connect(addNamedFunctionNode, QtCore.SIGNAL('triggered()'), self.nodeArea.addNamedFunctionNode)

        addInput = QtGui.QAction('Add Input', self)
        addInput.setStatusTip('Add an input to selected node')
        self.connect(addInput, QtCore.SIGNAL('triggered()'), self.nodeArea.addInput)

        addOutput = QtGui.QAction('Add Output', self)
        addOutput.setStatusTip('Add an output to selected node')
        self.connect(addOutput, QtCore.SIGNAL('triggered()'), self.nodeArea.addOutput)

        comp = QtGui.QAction('"Compile"', self)
        comp.setStatusTip('Show equivalent Haskell code for selected node')
        self.connect(comp, QtCore.SIGNAL('triggered()'), self.nodeArea.serializeCurrent)

        #exit = QtGui.QAction(QtGui.QIcon('x.png'), 'Exit', self) #[bmw] set exit action, assign an image to it
        exit = QtGui.QAction('Exit', self) #[bmw] set exit action, assign an image to it
        exit.setShortcut('Ctrl+Q') #[bmw] set keyboard shortcut (cmd q on osx)
        exit.setStatusTip('Exit application') #tooltip
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()')) #[bmw] binds exit's signal so that if it's triggered(), the application will close()

        self.statusBar().showMessage("Ready!") #[bmw] status bar message

        menubar = self.menuBar() #[bmw] grab menu bar pointer
        menuFile = menubar.addMenu('&File') #[bmw] add a new menu
        menuFile.addAction(exit) #[bmw] add exit to that menu

        addNodeMenu = menubar.addMenu('&Add Node')
        addNodeMenu.addAction(addHasScriptNode)
        addNodeMenu.addAction(addConstantNode)
        addNodeMenu.addAction(addNamedFunctionNode)

        modifyNodeMenu = menubar.addMenu('&Modify Node')
        modifyNodeMenu.addAction(addInput)
        modifyNodeMenu.addAction(addOutput)

        runNodeMenu = menubar.addMenu('&Run Node')
        runNodeMenu.addAction(comp)
        

        toolbar = self.addToolBar('Toolbar') #[bmw] make a new toolbar
        #toolbar.addAction(addHasScriptNode)
        #toolbar.addAction(addConstantNode)
        toolbar.addAction(addInput)
        toolbar.addAction(addOutput)
        toolbar.addAction(comp)

        self.raise_() #[bmw] grab focus on creation



# Every PyQt4 application must create an application object.
# The application object is located in the QtGui module.
a = QtGui.QApplication(sys.argv)

qb = MainBox()
qb.show()

sys.exit(a.exec_())  # Finally, we enter the mainloop of the application.
