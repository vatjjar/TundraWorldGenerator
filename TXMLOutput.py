#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys

class TXMLOutput():
    """ class TXMLOutput(): I/O component for writing formatted TXML notation
    """
    def __init__(self):
        self.indent = 0
        self.entity_id = 0

    def output(self, string):
        self.indent_str = ""
        for i in range(self.indent):
            self.indent_str = self.indent_str + " "
        sys.stdout.write(self.indent_str + str(string) + "\n")

    def increase_indent(self):
        self.indent = self.indent + 1

    def decrease_indent(self):
        self.indent = self.indent - 1
        if self.indent < 0: self.indent = 0

    ### Scene level

    def startScene(self):
        self.output("<!DOCTYPE Scene>\n<scene>")
        self.increase_indent()

    def endScene(self):
        self.decrease_indent()
        self.output("</scene>")

    ### Entity level

    def startEntity(self):
        self.output("<entity id=\"" + str(self.entity_id) + "\">")
        self.increase_indent()

    def endEntity(self):
        self.decrease_indent()
        self.output("</entity>")
        self.entity_id = self.entity_id + 1

    ### Component level

    def startComponent(self, component, sync):
        self.output("<component type=\"" + str(component) + "\" sync=\"" + str(sync) + "\">")
        self.increase_indent()

    def endComponent(self):
        self.decrease_indent()
        self.output("</component>")

    ### Attribute level

    def createAttribute(self, name, value):
        self.output("<attribute value=\"" + str(value) + "\" name=\"" + str(name) + "\"/>")

if __name__ == "__main__": # if run standalone
    # The test case here will output a few components to stdout, which will
    # look like TXML output
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

