#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os

class TXMLOutput():
    """ class TXMLOutput(): I/O component for writing formatted TXML notation
    """
    def __init__(self):
        self.indent = 0
        self.entity_id = 1  # entity numbering must start from 1. Zero is invalid
        self.resetOutputXML()

#############################################################################
# TXML output methods
#

    def resetOutputXML(self):
        self.outputXMLbuffer = ""

    def outputXML(self, msg):
        indent_str = ""
        for i in range(self.indent):
            indent_str = indent_str + " "
        self.outputXMLbuffer += (indent_str + str(msg) + "\n")

    def toFile(self, filename, overwrite=False):
        if os.path.exists(filename):
            if overwrite == False:
                sys.stderr.write("TXMLOutput: ERROR: output file '%s' already exists!\n" % filename)
                return
            else:
                os.remove(filename)
        try: file = open(filename, "w")
        except IOError:
            sys.stderr.write("TXMLOutput: ERROR: Unable to open file '%s' for writing!" % filename)
            return
        file.write(self.outputXMLbuffer)
        file.close()

    def increaseIndent(self):
        self.indent += 1

    def decreaseIndent(self):
        if self.indent > 0: self.indent -= 1

#############################################################################
# TXML getters/setters
#

    def getCurrentEntityID(self):
        return self.entity_id

#############################################################################
# TXML scene level
#

    def startScene(self):
        self.outputXML("<!DOCTYPE Scene>\n<scene>")
        self.increaseIndent()

    def endScene(self):
        self.decreaseIndent()
        self.outputXML("</scene>")

#############################################################################
# TXML entity level
#

    def startEntity(self, sync="1"):
        self.outputXML("<entity id=\"%s\" sync=\"%s\">" % (self.entity_id, str(sync)))
        self.increaseIndent()

    def endEntity(self):
        self.decreaseIndent()
        self.outputXML("</entity>")
        self.entity_id = self.entity_id + 1

#############################################################################
# TXML component level
#

    def startComponent(self, component, sync, name=""):
        if name == "":
            self.outputXML("<component type=\"%s\" sync=\"%s\">" % (component, sync))
        else:
            self.outputXML("<component type=\"%s\" sync=\"%s\" name=\"%s\">" % (component, sync, name))
        self.increaseIndent()

    def endComponent(self):
        self.decreaseIndent()
        self.outputXML("</component>")

#############################################################################
# TXML attribute level
#

    def createAttribute(self, name, value):
        self.outputXML("<attribute value=\"%s\" name=\"%s\"/>" % (str(value), str(name)))

    def createDynamicAttribute(self, name, value, type):
        self.outputXML("<attribute name=\"%s\" value=\"%s\" type=\"%s\"/>" % (name, value, type))

#############################################################################
# TXML standalone unit test
#

if __name__ == "__main__": # if run standalone
    # The test case here will output a few components to stdout, which will
    # look like TXML output
    print "Generating test TXML"
    t = TXMLOutput()
    t.startScene()
    t.startEntity()
    t.startComponent("EC_Mesh", 1)
    t.createAttribute("TestATTR", "False")
    t.endComponent()
    t.endEntity()
    t.startEntity()
    t.startComponent("EC_Name", 1)
    t.createAttribute("Name", "Testing")
    t.endComponent()
    t.endEntity()
    t.endScene()
    print "Writing test output into ./resources/test.txml"
    t.toFile("./resources/test.txml", overwrite=True)
