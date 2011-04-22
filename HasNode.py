import sys
from PyQt4 import QtGui, QtCore


class NodeArea(QtGui.QGraphicsScene):
    """Container for Nodes. Used for the main window's central widget."""
    def __init__(self, parent=None):
        """Create a NodeArea
        NodeArea is a GraphicsScene that contains all our nodes and connectors.

        """
        super(NodeArea, self).__init__(parent)

        self.viewer = QtGui.QGraphicsView(self)

    def addExistingNode(self, node):
        """Adds a GraphicsItem to our scene and gives it focus"""
        self.addItem(node)
        self.setFocusItem(node)

    def addNode(self):
        """[bmw] interface to outside to add a basic node."""
        newNode = BaseNode(self)
        self.addExistingNode(newNode)

    def addHasScriptNode(self):
        """A HasScriptNode will be added and given focus
        HasScriptNode supports input / output links

        """
        newNode = HasScriptNode(self)
        self.addExistingNode(newNode)

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


def reassign_p1(line_ref, new_p1):
    """Update the first point of line -- a GraphicsLineItem"""
    line = line_ref.line()
    line.setP1(new_p1)
    line_ref.setLine(line)


def reassign_p2(line_ref, new_p2):
    """Update the second point of line -- a GraphicsLineItem"""
    line = line_ref.line()
    line.setP2(new_p2)
    line_ref.setLine(line)


class HasLine(QtGui.QGraphicsLineItem):
    """HasLine -- a line from a source to a sink that resizes itself."""
    def __init__(self, line, parent=None):
        super(HasLine, self).__init__(line, parent)
        self.source = None
        self.sink = None

    def setSource(self, source):
        self.source = source

    def setSink(self, sink):
        self.sink = sink

    def paint(self, painter, option, widget=None):
        """Ensure that the line is still accurate. If not: redraw appropriately."""
        if self.sink is not None and not self.sink.rect().contains(self.sink.mapFromScene(self.line().p2())):
            reassign_p2(self,
                        self.sink.mapToScene(self.sink.rect().center()))

        if self.source is not None and not self.source.rect().contains(self.source.mapFromScene(self.line().p1())):
            reassign_p1(self,
                        self.source.mapToScene(self.source.rect().center()))

        super(HasLine, self).paint(painter, option, widget)


class BaseNode(QtGui.QGraphicsItemGroup):
    """Basic Node -- a node can have inputs and outputs, and contains items."""
    def __init__(self, parent=None):
        super(BaseNode, self).__init__(parent)

        self.inputs = []  #[bmw] lists to contain inputs and outputs
        self.outputs = []

        setup_default_flags(self)

        self.setHandlesChildEvents(False)  # we need this to ensure that group components are still interactable

        # if we want syntax highlighting for Haskell Nodes s/QLabel/QTextEdit
        # and subclass QSyntaxHighlighter

    def addInput(self):
        new_input = HasNodeInput(len(self.inputs), parent=self)
        self.inputs.append(new_input)

    def addOutput(self):
        new_output = HasNodeOutput(len(self.outputs), parent=self)
        self.outputs.append(new_output)


class HasScriptNode(BaseNode):
    """Haskell Script Node -- contains haskell code, the equivalent of MathScript nodes in LabView."""
    def __init__(self, parent=None):
        super(HasScriptNode, self).__init__()

        rect = QtGui.QGraphicsRectItem()
        rect.setRect(QtCore.QRectF(self.x(), self.y(), 200, 200))  #[bmw] default size
        self.addToGroup(rect)

        text = HasTextNode("Enter Text Here")
        text_flags = QtCore.Qt.TextEditorInteraction
        text.setTextInteractionFlags(text_flags)
        self.addToGroup(text)

        setup_default_flags(self)


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

    def __init__(self, parent=None):
        super(HasNodeIOVar, self).__init__(parent)
        setup_default_flags(self,
                            flags = QtGui.QGraphicsItem.ItemIsSelectable | \
                                    QtGui.QGraphicsItem.ItemIsFocusable)

    def addInput(self):
        return self.parentItem().addInput()

    def addOutput(self):
        return self.parentItem().addOutput()


class HasNodeInput(HasNodeIOVar):
    """Input box for nodes -- will be placed on the left of a node"""
    def __init__(self, num_prev_inputs, parent=None):
        super(HasNodeInput, self).__init__(parent)
        self.setRect(-20,                   # place on left side
                     20 * num_prev_inputs,  # account for earlier inputs
                     20,                    # 20x20 is a reasonable box size
                     20)

    def mouseDoubleClickEvent(self, event):
        HasNodeIOVar.current_line = HasLine(QtCore.QLineF(self.mapToScene(self.rect().center()),
                                                          self.mapToScene(self.rect().center())))
        HasNodeIOVar.current_line.setSource(self)
        self.scene().addItem(HasNodeIOVar.current_line)

    def keyPressEvent(self, event):
        if event.key() is QtCore.Qt.Key_Escape:
            HasNodeIOVar.current_line = None


class HasNodeOutput(HasNodeIOVar):
    """Output box for nodes."""
    def __init__(self, num_prev_outputs, parent=None):
        super(HasNodeOutput, self).__init__(parent)
        self.setRect(self.parentItem().boundingRect().topRight().x(),   # find the right index to use [haha]
                     20 * num_prev_outputs,                             # account for earlier inputs
                     20,
                     20)

    def mouseDoubleClickEvent(self, event):
        if HasNodeIOVar.current_line is not None:
            reassign_p2(HasNodeIOVar.current_line,
                        self.mapToScene(self.rect().center()))
            HasNodeIOVar.current_line.setSink(self)
        HasNodeIOVar.current_line = None
