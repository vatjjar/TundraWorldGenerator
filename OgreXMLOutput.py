#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys
import os

class OgreXMLOutput():
    """ class OgreXMLOutput(): I/O component for writing formatted OgreXML notation
        - Primarily used by MeshGenerator for producing Ogre compliant XML mesh
          notation.
        - All XML requests are pushed into buffer, and once toFile method is called
          the contents are flushes to the desired output file.
    """
    def __init__(self):
        self.indent = 0
        self.entity_id = 0
        self.resetOutputXML()

#############################################################################
# Ogre XML output methods
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
                sys.stderr.write("OgreXML: ERROR: output file '%s' already exists!\n" % filename)
            else:
                os.remove(filename)
        try: file = open(filename, "w")
        except IOError:
            sys.stderr.write("OgreXML: ERROR: Unable to open file '%s' for writing!" % filename)
            return
        file.write(self.outputXMLbuffer)
        file.close()

    def increaseIndent(self):
        self.indent += 1

    def decreaseIndent(self):
        if self.indent > 0: self.indent -= 1

#############################################################################
#
#

    def startMesh(self):
        self.outputXML("<mesh>")
        self.increaseIndent()

    def endMesh(self):
        self.decreaseIndent()
        self.outputXML("</mesh>")

    def startVertexbuffer(self, position=True, normal=True, texcoord=True):
        s_out = ""
        if normal == True:   s_out += "normals=\"true\" "
        if position == True: s_out += "positions=\"true\" "
        if texcoord == True: s_out += "texture_coords=\"true\""
        self.outputXML("<vertexbuffer %s>" % s_out)
        #normals=\""+str(normal)+"\" positions=\""+str(position)+"\" texture_coords=\""+str(1)+"\">")
        self.increaseIndent()

    def endVertexbuffer(self):
        self.decreaseIndent()
        self.outputXML("</vertexbuffer>")

    def startSharedgeometry(self, vertices):
        self.outputXML("<sharedgeometry vertexcount=\"" + str(vertices) + "\">")
        self.increaseIndent()

    def endSharedgeometry(self):
        self.decreaseIndent()
        self.outputXML("</sharedgeometry>")

    def startVertex(self):
        self.outputXML("<vertex>")
        self.increaseIndent()

    def endVertex(self):
        self.decreaseIndent()
        self.outputXML("</vertex>")

    def outputPosition(self, x, y, z):
        self.outputXML("<position x=\""+str(x)+"\" y=\""+str(y)+"\" z=\""+str(z)+"\"/>")

    def outputNormal(self, x, y, z):
        self.outputXML("<normal x=\""+str(x)+"\" y=\""+str(y)+"\" z=\""+str(z)+"\"/>")

    def outputTexcoord(self, u, v):
        self.outputXML("<texcoord u=\""+str(u)+"\" v=\""+str(v)+"\"/>")

#############################################################################
# Test case:
#

if __name__ == "__main__": # if run standalone
    # The test case here will output a few components to stdout, which will
    # look like OgreXML output
    t = OgreXMLOutput()
    t.startMesh()
    t.startSharedgeometry(10)
    t.startVertexbuffer(position=True, normal=True, texcoord=True)
    for i in range(10):
        t.startVertex()
        t.outputPosition(i*1, i*2, i*3)
        t.outputNormal(i*3, i*4, i*5)
        t.outputTexcoord(i*6, i*7)
        t.endVertex()
    t.endVertexbuffer()
    t.endSharedgeometry()
    t.endMesh()
    t.toFile("./test.mesh.xml", overwrite=True)
