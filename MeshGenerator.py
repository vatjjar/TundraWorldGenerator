#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os, io
import random
import numpy
import math

import OgreXMLOutput

class MeshGenerator():
    """ class MeshGenerator(): A collection of procedural methods for
        creating mesh files with various content. Content is saved in Ogre .xml
        mesh format, and it is purposed to be post-processed with Ogre
        tools afterwards.
    """

    def __init__(self):
        """ MeshGenerator.__init__(width, height):
        """
        self.initialize()
        self.OgreXML = OgreXMLOutput.OgreXMLOutput()

    def initialize(self, vertices=1, faces=1, texcoords=1, normals=1):
        """ MeshGenerator.initialize():
        """
        self.a_vertices = numpy.zeros([vertices, 3], dtype=float)
        self.a_normals = numpy.zeros([normals, 3], dtype=float)
        self.a_faces = numpy.zeros([faces, 3], dtype=float)
        self.a_texcoords = numpy.zeros([texcoords, 2], dtype=float)
        self.intend = 0
        return True

#############################################################################
# Mesh textual output methods
#

    def printmessage(self, message):
        sys.stdout.write(message + "\n")

    def printerror(self, message):
        sys.stderr.write("ERROR: " + str(message) + "\n")

#############################################################################
# File I/O
#

    def toFile(self, filename, overwrite=False):
        self.OgreXML.startMesh()
        self.OgreXML.startSharedgeometry(len(self.a_vertices))
        self.OgreXML.startVertexbuffer(position=True, normal=True, texcoord=True)
        for i in range(len(self.a_vertices)):
            self.OgreXML.startVertex()
            self.OgreXML.outputPosition(self.a_vertices[i,0], self.a_vertices[i,1], self.a_vertices[i,2])
            self.OgreXML.outputNormal(self.a_normals[i,0], self.a_normals[i,1], self.a_normals[i,2])
            self.OgreXML.outputTexcoord(self.a_texcoords[i,0], self.a_texcoords[i,1])
            self.OgreXML.endVertex()
        self.OgreXML.endVertexbuffer()
        self.OgreXML.endSharedgeometry()
        self.OgreXML.endMesh()
        self.OgreXML.toFile(filename, overwrite)
        return True

#############################################################################
# Procedural primitive creators
#
# - Plane
# - Cube
#############################################################################

    def createPlane(self, LOD=1):
        """ MeshGenerator.createPlane(self, LOD): Create a plane mesh component
            - Method will create a plane mesh component in XZ-plane whose size is 1 times 1 units in
              coordinate system.
            - Level of detail will range number of faces in the plane from 2-50. LOD levels 1-5 are accepted
        """
        self.initialize(vertices=(LOD+1)*(LOD+1), faces=2*LOD*LOD, normals=(LOD+1)*(LOD+1), texcoords=(LOD+1)*(LOD+1))
        x_delta = 1.0 / LOD
        y_delta = 1.0 / LOD
        for x in range(LOD+1):
            for y in range(LOD+1):
                #print "Injecting vertex %d with data %f %f %f" % (x*(LOD+1)+y, -1+x*x_delta, 0, -1+y*y_delta)
                self.a_vertices[x*(LOD+1)+y, 0] = -0.5 + x*x_delta
                self.a_vertices[x*(LOD+1)+y, 1] = 0.0
                self.a_vertices[x*(LOD+1)+y, 2] = -0.5 + y*y_delta
                #print "Injecting normal %d with data %f %f %f" % (x*(LOD+1)+y, 0, -1, 0)
                self.a_normals[x*(LOD+1)+y, 0] =  0.0
                self.a_normals[x*(LOD+1)+y, 1] = -1.0
                self.a_normals[x*(LOD+1)+y, 2] =  0.0
                #print "Injecting texcoord %d with data %f %f" % (x*(LOD+1)+y, (x*x_delta)/2.0, (y*y_delta)/2.0)
                self.a_texcoords[x*(LOD+1)+y, 0] = 0.0 + x*x_delta
                self.a_texcoords[x*(LOD+1)+y, 1] = 0.0 + y*y_delta

    def createCube(self, LOD=1):
        self.initialize(vertices=8, faces=12, normals=8, texcoords=8)

############################################################################
# Transformation helpers, for procedural meshes
#
# - Translate
# - Rotate
# - MatrixMultiply
#############################################################################

    def rotate(self):
        return

    def translate(self):
        return

    def matrixMultiply(self):
        return

#############################################################################

if __name__ == "__main__": # if run standalone
    mesh = MeshGenerator()
    mesh.createPlane(LOD=5)
    mesh.toFile("plane.mesh.xml")
