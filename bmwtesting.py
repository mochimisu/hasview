#[bmw] some testing
"""
current status:
    creates pyqt window
    adds toolbar
    keyboard shortcut to quit
    mouse bindings to move box around
    dialog box popup

todo:
    create class for boxes (and unify dialog, text output, frame, etc)
    make box class movable
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

        exit = QtGui.QAction(QtGui.QIcon('lambda.png'), 'Exit', self) #[bmw] set exit action, assign an image to it
        exit.setShortcut('Ctrl+Q') #[bmw] set keyboard shortcut (cmd q on osx)
        exit.setStatusTip('Exit application') #tooltip
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()')) #[bmw] binds exit's signal so that if it's triggered(), the application will close()

        self.statusBar().showMessage("asdf") #[bmw] status bar message

        menubar = self.menuBar() #[bmw] grab menu bar pointer
        file = menubar.addMenu('&File') #[bmw] add a new menu
        file.addAction(exit) #[bmw] add exit to that menu

        toolbar = self.addToolBar('Exit') #[bmw] make a new toolbar
        toolbar.addAction(exit) #[bmw] add exit to toolbar


class BoxArea(QtGui.QWidget): #[bmw] boxarea widget to contain our moving boxes and stuff
    def __init__(self, parent=None):
        super(BoxArea, self).__init__(parent)

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

    def paintEvent(self, e): #[bmw] some lingering code to show how to draw a box outline
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine))
        qp.drawRect(10, 195, 90, 60)
        qp.end()


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
        self.label.move(newPos)
        self.button.move(newPos - QtCore.QPoint(100,0)) #[bmw] offset (QPoint has arithmetic operators)

    def showDialog(self): #[bmw] dialog box to edit input
        text, ok = QtGui.QInputDialog.getText(self, 'Input', 
            'Enter something:')

        if ok:
            self.label.setText(str(text))


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
