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

        self.nodeArea = HasNode.NodeArea() #[bmw] declare area for nodes to move around
        
        self.setCentralWidget(self.nodeArea) #[bmw] set boxarea as central widget - central widgets take up the rest of the space (after some space is taken up by toolbar, etc)

        #addNode = QtGui.QAction(QtGui.QIcon('lambda.png'), 'Add Node', self)
        addNode = QtGui.QAction('Add Node', self)
        addNode.setShortcut('Ctrl+Shift+N')
        addNode.setStatusTip('Add a new node')
        self.connect(addNode, QtCore.SIGNAL('triggered()'), self.nodeArea.addNode)

        addInput = QtGui.QAction('Add Input', self)
        addInput.setStatusTip('Add an input to selected node')
        self.connect(addInput, QtCore.SIGNAL('triggered()'), self.nodeArea.addInput)

        addOutput = QtGui.QAction('Add Output', self)
        addOutput.setStatusTip('Add an output to selected node')
        self.connect(addOutput, QtCore.SIGNAL('triggered()'), self.nodeArea.addOutput)
        

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



# Every PyQt4 application must create an application object.
# The application object is located in the QtGui module.
a = QtGui.QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
# We provide the default constructor for QWidget. The default constructor has no parent.
# A widget with no parent is called a window. 
w = QtGui.QWidget()

qb = MainBox()
qb.show()

sys.exit(a.exec_())  # Finally, we enter the mainloop of the application.
