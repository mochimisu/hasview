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

        addNode = QtGui.QAction(QtGui.QIcon('lambda.png'), 'Add Node', self)
        addNode.setShortcut('Ctrl+Shift+N')
        addNode.setStatusTip('Add a new node')
        self.connect(addNode, QtCore.SIGNAL('triggered()'), self.boxArea.addNode)

        exit = QtGui.QAction(QtGui.QIcon('x.png'), 'Exit', self) #[bmw] set exit action, assign an image to it
        exit.setShortcut('Ctrl+Q') #[bmw] set keyboard shortcut (cmd q on osx)
        exit.setStatusTip('Exit application') #tooltip
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()')) #[bmw] binds exit's signal so that if it's triggered(), the application will close()

        self.statusBar().showMessage("asdf") #[bmw] status bar message

        menubar = self.menuBar() #[bmw] grab menu bar pointer
        file = menubar.addMenu('&File') #[bmw] add a new menu
        file.addAction(addNode)
        file.addAction(exit) #[bmw] add exit to that menu

        toolbar = self.addToolBar('Toolbar') #[bmw] make a new toolbar
        toolbar.addAction(addNode) #[bmw] add exit to toolbar
        toolbar.addAction(exit) #[bmw] add exit to toolbar

class HasNode(QtGui.QFrame):
    def __init__(self, parent=None):
        super(HasNode, self).__init__(parent)
        self.frameRect = QtCore.QRect()
        self.setFrameStyle(1)
        self.moving = False
        self.resizing = False
        self.clickedOffset = QtCore.QPoint()
        
    def mousePressEvent(self, event): #[bmw] mousepress listener: only handles clicks and not releases
        self.clickedOffset = event.pos()

        if event.button() == QtCore.Qt.LeftButton and (self.clickedOffset.x() > self.width()-10) and (self.clickedOffset.y() > self.height()-10):
            self.resizing = True
            self.clickedOffset = QtCore.QPoint(self.width() - self.clickedOffset.x(), self.height() - self.clickedOffset.y())
        elif event.button() == QtCore.Qt.LeftButton: #moving the box
            self.moving = True #[bmw] so we know that we clicked
        
    def mouseMoveEvent(self, event): #[bmw] handles mouse movement
        if (event.buttons() & QtCore.Qt.LeftButton) and self.moving: #[bmw] only move when left butotn is clicked and click bool is on (redundant possibly?)
            self.move(self.pos()+event.pos()-self.clickedOffset)
        elif (event.buttons() & QtCore.Qt.LeftButton) and self.resizing:
            btmRtPt = event.pos() + self.clickedOffset;
            self.resize(btmRtPt.x(),btmRtPt.y())

    def mouseReleaseEvent(self, event): #[bmw] handles mouse click releases
        if event.button() == QtCore.Qt.LeftButton and self.resizing:
            self.mouseMoveEvent(event)
            self.resizing = False #[bmw] so we know to not move anymore
        if event.button() == QtCore.Qt.LeftButton and self.moving: 
            self.mouseMoveEvent(event)
            self.moving = False #[bmw] so we know to not move anymore


class BoxArea(QtGui.QWidget): #[bmw] boxarea widget to contain our moving boxes and stuff
    def __init__(self, parent=None):
        super(BoxArea, self).__init__(parent)

        self.frames = []
        
        #self.frame = HasNode(self)
        #self.frame.show()

    def addExistingNode(self, node):
        self.frames.append(node)
    def addNode(self):
        newNode = HasNode(self)
        self.addExistingNode(newNode)
        newNode.show()


"""
        #[bmw] set initial vars
        self.clicked = False

        self.button = QtGui.QPushButton('Edit', self) #[bmw] dialog button creation
        self.button.setFocusPolicy(QtCore.Qt.NoFocus) #[bmw] sets focus policy
        self.button.move(20, 20) #[bmw] initial pos
        self.connect(self.button, QtCore.SIGNAL('clicked()'), 
            self.showDialog) #[bmw] binds button to showDialog()
        self.setFocus() 

        self.label = QtGui.QLineEdit(self) #[bmw] creates lineedit "output"
        self.label.move(120, 20) #[bmw] initial pos
        """

        
"""

    def mousePressEvent(self, event): #[bmw] mousepress listener: only handles clicks and not releases
        if event.button() == QtCore.Qt.LeftButton: #[bmw] only care about left button
            self.clicked = True #[bmw] so we know that we clicked

    def mouseMoveEvent(self, event): #[bmw] handles mouse movement
        if (event.buttons() & QtCore.Qt.LeftButton) and self.clicked: #[bmw] only move when left butotn is clicked and click bool is on (redundant possibly?)
            self.moveThingTo(event.pos()) 

    def mouseReleaseEvent(self, event): #[bmw] handles mouse click releases
        if event.button() == QtCore.Qt.LeftButton and self.clicked: #[bmw] same as mousemove
            self.moveThingTo(event.pos()) #[bmw] same as mousemove
            self.clicked = False #[bmw] so we know to not move anymore

    def moveThingTo(self, newPos): #[bmw] actual moving
        self.frame.move(newPos)
        #self.label.move(newPos)
        #self.button.move(newPos - QtCore.QPoint(100,0)) #[bmw] offset (QPoint has arithmetic operators)

    def showDialog(self): #[bmw] dialog box to edit input
        text, ok = QtGui.QInputDialog.getText(self, 'Input', 
            'Enter something:')

        if ok:
            self.label.setText(str(text))
        """


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
