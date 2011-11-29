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

    def initialize(self, vertices=3, faces=1, texcoords=3, normals=1):
        """ MeshGenerator.initialize():
        """
        self.n_vertices = vertices;
        self.n_faces = faces;
        self.n_texcoords = texcoords;
        self.n_normals = normals
        self.a_vertices = numpy.zeros([vertices, 3], dtype=float)
        self.a_normals = numpy.zeros([normals, 3], dtype=float)
        self.a_faces = numpy.zeros([faces, 3], dtype=int)
        self.a_texcoords = numpy.zeros([texcoords, 2], dtype=float)
        self.intend = 0
        return True

#############################################################################
# Mesh textual and file I/O methods
#

    def printmessage(self, message):
        sys.stdout.write(message + "\n")

    def printerror(self, message):
        sys.stderr.write("ERROR: " + str(message) + "\n")

    def tryFileOpen(self, filename, overwrite=False):
        if os.path.exists(filename):
            if overwrite == False:
                raise IOError
            else:
                os.remove(filename)
        file = open(filename, "w")
        return file

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
        self.OgreXML.startSubMeshes()
        self.OgreXML.startSubMesh("test.material", True)
        self.OgreXML.startFaces(len(self.a_faces))
        for i in range(len(self.a_faces)):
            self.OgreXML.outputFace(self.a_faces[i,0], self.a_faces[i,1], self.a_faces[i,2])
        self.OgreXML.endFaces()
        self.OgreXML.endSubMesh()
        self.OgreXML.endSubMeshes()
        self.OgreXML.endMesh()
        self.OgreXML.toFile(filename, overwrite)
        return True

    def toTextFile(self, filename, overwrite=False):
        """ MeshGenerator->toTextFile(filename, overwrite=False): Output mesh into textual (simple) files
            - toTextFile() method outputs generated gemoetry into a bunch of textual files, which
              can be read in a simplified fashion, line-by-line, by scripts and simple test programs
            - filename with extensions: ".faces", ".vertices", ".normals", ".texcoords" are provided
        """

        # Faces:
        try: file = self.tryFileOpen(filename+".faces", overwrite)
        except IOError:
            sys.stderr.write("ERROR: Unable to open '%s'\n" % (filename+".faces"))
            return
        output = ""
        for i in range(self.n_faces):
            output += ("%d\n" % (self.a_faces[i, 0]))
            output += ("%d\n" % (self.a_faces[i, 1]))
            output += ("%d\n" % (self.a_faces[i, 2]))
        file.write(output)
        file.close()

        # Vertices:
        try: file = self.tryFileOpen(filename+".vertices", overwrite)
        except IOError:
            sys.stderr.write("ERROR: Unable to open '%s'\n" % (filename+".vertices"))
            return
        output = ""
        for i in range(self.n_vertices):
            output += ("%f\n" % (self.a_vertices[i, 0]))
            output += ("%f\n" % (self.a_vertices[i, 1]))
            output += ("%f\n" % (self.a_vertices[i, 2]))
        file.write(output)
        file.close()

        # Normals:
        try: file = self.tryFileOpen(filename+".normals", overwrite)
        except IOError:
            sys.stderr.write("ERROR: Unable to open '%s'\n" % (filename+".normals"))
            return
        output = ""
        for i in range(self.n_normals):
            output += ("%f\n" % (self.a_normals[i, 0]))
            output += ("%f\n" % (self.a_normals[i, 1]))
            output += ("%f\n" % (self.a_normals[i, 2]))
        file.write(output)
        file.close()

        # Texcoords:
        try: file = self.tryFileOpen(filename+".texcoords", overwrite)
        except IOError:
            sys.stderr.write("ERROR: Unable to open '%s'\n" % (filename+".texcoords"))
            return
        output = ""
        for i in range(self.n_texcoords):
            output += ("%f\n" % (self.a_texcoords[i, 0]))
            output += ("%f\n" % (self.a_texcoords[i, 1]))
        file.write(output)
        file.close()

#############################################################################
# Procedural primitive creators
#
# - Plane
# - Cube
#############################################################################

    def createPlane(self, LOD=1):
        """ MeshGenerator.createPlane(self, LOD): Create a plane mesh component
            - Method will create a plane mesh component in XZ-plane whose size is 1 times 1 units in
              coordinate system and which is centered to origin.
            - Level of detail will range number of faces in the plane from 2-50. LOD levels 1-5 are accepted
        """
        self.initialize(vertices=(LOD+1)*(LOD+1), faces=2*LOD*LOD, normals=(LOD+1)*(LOD+1), texcoords=(LOD+1)*(LOD+1))
        x_delta = 1.0 / LOD
        y_delta = 1.0 / LOD
        #
        # First we create vertices, normals and texcoords
        #
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
        #
        # And according to above, we create faces
        #
        for x in range(LOD):
            for y in range(LOD):
                #print "Injecting face %d with vertices %d %d %d" % ((2*(x*LOD+y)), 0     + y+x*(LOD+1), 1     + y+x*(LOD+1), LOD+2 + y+x*(LOD+1))
                self.a_faces[2*(x*LOD+y), 0]   = 0     + y+x*(LOD+1)
                self.a_faces[2*(x*LOD+y), 1]   = 1     + y+x*(LOD+1)
                self.a_faces[2*(x*LOD+y), 2]   = LOD+2 + y+x*(LOD+1)
                #print "Injecting face %d with vertices %d %d %d" % ((2*(x*LOD+y)+1), 0     + y+x*(LOD+1),LOD+2 + y+x*(LOD+1),LOD+1   + y+x*(LOD+1))
                self.a_faces[2*(x*LOD+y)+1, 0] = 0     + y+x*(LOD+1)
                self.a_faces[2*(x*LOD+y)+1, 1] = LOD+2 + y+x*(LOD+1)
                self.a_faces[2*(x*LOD+y)+1, 2] = LOD+1 + y+x*(LOD+1)

    def createCube(self, LOD=1):
        self.initialize(vertices=8, faces=12, normals=8, texcoords=8)

############################################################################
# Transformation helpers, for procedural meshes
#
# - Rotate
# - Translate
# - Scale
# - MatrixMultiply
#############################################################################

    def rotate(self):
        return

    def translate(self, x=0.0, y=0.0, z=0.0):
        for i in range(self.n_vertices):
            self.a_vertices[i, 0] = self.a_vertices[i,0] + float(x)
            self.a_vertices[i, 1] = self.a_vertices[i,1] + float(y)
            self.a_vertices[i, 2] = self.a_vertices[i,2] + float(z)

    def scale(self, x=1.0, y=1.0, z=1.0):
        for i in range(self.n_vertices):
            self.a_vertices[i, 0] = self.a_vertices[i,0] * float(x)
            self.a_vertices[i, 1] = self.a_vertices[i,1] * float(y)
            self.a_vertices[i, 2] = self.a_vertices[i,2] * float(z)

    def matrixMultiply(self, m):
        for i in range(self.n_vertices):
            for j in range(3):
                self.a_vertices[i,0] = m[j,0]*self.a_vertices[0,0] + \
                                       m[j,1]*self.a_vertices[0,1] + \
                                       m[j,2]*self.a_vertices[0,2]

#############################################################################

if __name__ == "__main__": # if run standalone
    mesh = MeshGenerator()
    mesh.createPlane(LOD=5)
    mesh.toFile("Plane.mesh.xml", overwrite=True)
    mesh.toTextFile("Plane", overwrite=True)
