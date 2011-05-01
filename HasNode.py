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

    def addConstantNode(self):
        """better way to do this than to make 1000 functions?"""
        newNode = ConstantNode(self)
        self.addExistingNode(newNode)

    def addNamedFunctionNode(self):
        """better way to do this than to make 1000 functions?"""
        newNode = NamedFunctionNode(self)
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

    def serializeCurrent(self):
        """serializes currently selected node"""
        if self.focusItem():
            print self.focusItem().serialize()
        else:
            self.viewer.parent().statusBar().showMessage("Cannot compile: no selected node!")

    def mouseMoveEvent(self, event):
        """mouse movement of node area. super() call allows to drag boxes around, and the rest allows to display lines after an iovar was selected """
        super(NodeArea, self).mouseMoveEvent(event)
        if HasNodeIOVar.current_line is not None:
            if HasNodeIOVar.current_line.sink is None:
                reassign_p2(HasNodeIOVar.current_line,
                            event.scenePos())
            if HasNodeIOVar.current_line.source is None:
                reassign_p1(HasNodeIOVar.current_line,
                            event.scenePos())

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
        self.cubicPath = QtGui.QPainterPath()

    def setSource(self, source):
        self.source = source
        #TODO: check for previous source/sink and remove if reassigned
        source.links.append(self)

    def setSink(self, sink):
        self.sink = sink
        sink.links.append(self)

    def paint(self, painter, option, widget=None):
        """Ensure that the line is still accurate. If not: redraw appropriately."""
        if self.sink is not None and not self.sink.rect().center() == (self.sink.mapFromScene(self.line().p2())):
            reassign_p2(self,
                        self.sink.mapToScene(self.sink.rect().center()))

        if self.source is not None and not self.source.rect().center() == (self.source.mapFromScene(self.line().p1())):
            reassign_p1(self,
                        self.source.mapToScene(self.source.rect().center()))

        self.updateCubic()
        painter.setPen(QtCore.Qt.black)
        painter.drawPath(self.cubicPath)
#super(HasLine, self).paint(painter, option, widget)

    def updateCubic(self): #i think theres a better way to do this....
        self.cubicPath = QtGui.QPainterPath(self.line().p1())
        self.cubicPath.cubicTo(self.line().p1() + QtCore.QPointF(100,100),self.line().p2() + QtCore.QPointF(-100,-100),self.line().p2())
    
    def boundingRect(self):
        return self.cubicPath.boundingRect()


class BaseNode(QtGui.QGraphicsItemGroup):
    """Basic Node -- a node can have inputs and outputs, and contains items."""
    def __init__(self, parent=None):
        super(BaseNode, self).__init__(parent)

        self.inputs = []  #[bmw] lists to contain inputs and outputs
        self.outputs = []

        setup_default_flags(self)

        self.setHandlesChildEvents(False)  # we need this to ensure that group components are still interactable

        self.frameRect = QtGui.QGraphicsRectItem()
        self.frameRect.setRect(QtCore.QRectF(self.x(), self.y(), 200, 200))  #default size
        #self.boundingRect = rect
        self.addToGroup(self.frameRect)

        # if we want syntax highlighting for Haskell Nodes s/QLabel/QTextEdit
        # and subclass QSyntaxHighlighter

    def addInput(self):
        new_input = HasNodeInput(len(self.inputs), parent=self)
        self.inputs.append(new_input)

    def addOutput(self):
        new_output = HasNodeOutput(len(self.outputs), parent=self)
        self.outputs.append(new_output)

    def serialize(self): #take inputs as list of arguments in order
        #inputs should only have one connecting source [check for this?]

        #default actuion is to just use the first input as output (no checks yet, just trying to get method down)
        firstInputVar = self.inputs[0].name
        firstOutputVar = self.outputs[0].name
        return firstOutputVar + " = " + firstInputVar
        

class HasScriptNode(BaseNode):
    """Haskell Script Node -- contains haskell code, the equivalent of MathScript nodes in LabView."""
    def __init__(self, parent=None):
        super(HasScriptNode, self).__init__()

        text = QtGui.QGraphicsTextItem("Enter Text Here")
        text_flags = QtCore.Qt.TextEditorInteraction
        text.setTextInteractionFlags(text_flags)
        self.addToGroup(text)

        # syntax highlighting is fun! Have some for breakfast.
        highlighter = HasHighlighter(text.document())

        setup_default_flags(self)

class ConstantNode(BaseNode):
    """Constant value used as an output only"""
    def __init__(self, parent=None):
        super(ConstantNode, self).__init__()

        self.removeFromGroup(self.frameRect)
        self.frameRect.setRect(QtCore.QRectF(self.x(), self.y(), 125, 25))
        self.addToGroup(self.frameRect)

        self.text = QtGui.QGraphicsTextItem("Constant")
        text_flags = QtCore.Qt.TextEditorInteraction
        self.text.setTextInteractionFlags(text_flags)
        self.addToGroup(self.text)
        
        setup_default_flags(self)

        self.addOutput()
    
    def serialize(self): #ex: 2 (is this same thing as namedfunction with no input?)
        return self.text.toPlainText()

class NamedFunctionNode(BaseNode):
    """Named function"""
    def __init__(self, parent=None):
        super(NamedFunctionNode, self).__init__()

        self.removeFromGroup(self.frameRect)
        self.frameRect.setRect(QtCore.QRectF(self.x(), self.y(), 125, 25))
        self.addToGroup(self.frameRect)

        self.text = QtGui.QGraphicsTextItem("Function Name")
        text_flags = QtCore.Qt.TextEditorInteraction
        self.text.setTextInteractionFlags(text_flags)
        self.addToGroup(self.text)
        
        setup_default_flags(self)

        self.addOutput()

    def serialize(self): #ex: foo a b
        outputString = ""
        funcCall = self.text.toPlainText()
        for inp in self.inputs:
            outputString += inp.name + " = " + inp.links[0].source.parentItem().serialize() + "\n"
            funcCall += " " + inp.name
        outputString += funcCall
        return outputString

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
        if HasNodeIOVar.current_line is not None:
            if HasNodeIOVar.current_line.sink is None:
                reassign_p1(HasNodeIOVar.current_line,
                            self.mapToScene(self.rect().center()))
                HasNodeIOVar.current_line.setSink(self)
                HasNodeIOVar.current_line = None
        else:
            HasNodeIOVar.current_line = HasLine(QtCore.QLineF(self.mapToScene(self.rect().center()),
                                                          self.mapToScene(self.rect().center())))
            HasNodeIOVar.current_line.setSink(self)
            self.scene().addItem(HasNodeIOVar.current_line)


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
            if HasNodeIOVar.current_line.source is None:
                reassign_p2(HasNodeIOVar.current_line,
                            self.mapToScene(self.rect().center()))
                HasNodeIOVar.current_line.setSource(self)
                HasNodeIOVar.current_line = None
        else:
            HasNodeIOVar.current_line = HasLine(QtCore.QLineF(self.mapToScene(self.rect().center()),
                                                              self.mapToScene(self.rect().center())))
            HasNodeIOVar.current_line.setSource(self)
            self.scene().addItem(HasNodeIOVar.current_line)


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
