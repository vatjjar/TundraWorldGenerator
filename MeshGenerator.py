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

import MeshContainer
import MeshIO

class MeshGenerator():
    """ class MeshGenerator(): A collection of procedural methods for
        creating mesh files with various content.
    """

    def __init__(self, meshcontainer):
        """ MeshGenerator.__init__(width, height):
        """
        self.meshcontainer = meshcontainer

#############################################################################
# Procedural primitive creators
#
# - Plane
# - Cube
#############################################################################

    #########################################################################
    # Plane
    # - Creates a planar mesh
    #
    def createPlane(self, LOD=1):
        """ MeshGenerator.createPlane(self, LOD): Create a plane mesh component
            - Method will create a plane mesh component in XZ-plane whose size is 1 times 1 units in
              coordinate system and which is centered to origin.
            - Level of detail will range number of faces in the plane from 2-50.
        """
        self.meshcontainer.initialize()
        self.meshcontainer.newSubmesh()     # The plane is pushed into single submesh
        x_delta = 1.0 / LOD
        y_delta = 1.0 / LOD
        #
        # First we create vertices, normals and texcoords
        #
        for x in range(LOD+1):
            for y in range(LOD+1):
                self.meshcontainer.addVertex([-0.5 + x*x_delta, 0.0, -0.5 + y*y_delta])
                self.meshcontainer.addNormal([0.0, -1.0, 0.0])
                self.meshcontainer.addTexcoord([x*x_delta, y*y_delta])
        #
        # And according to above, we create faces
        #
        for x in range(LOD):
            for y in range(LOD):
                self.meshcontainer.addFace([y+x*(LOD+1), 1+y+x*(LOD+1), LOD+2+y+x*(LOD+1)])
                self.meshcontainer.addFace([y+x*(LOD+1), LOD+2+y+x*(LOD+1), LOD+1+y+x*(LOD+1)])

    #########################################################################
    # Cube
    # - Constructs a cubic mesh from 6 planar meshes. Does the merge with
    #   meshcontainer provided translation tools
    #
    def createCube(self, LOD=1):
        self.meshcontainer.initialize()
        #
        # Temporary mesh container for plane mesh (single side of a cube)
        #
        mesh = MeshContainer.MeshContainer()
        meshgen = MeshGenerator(mesh)
        meshgen.createPlane(LOD)
        # Cube Face 1
        mesh.translate(0.0, 0.5, 0.0)
        self.meshcontainer.merge(mesh)
        # Cube Face 2
        mesh.translate(0.0, -0.5, 0.0)
        mesh.rotate(90, 0, 0, 1)
        mesh.translate(-0.5, 0.0, 0.0)
        self.meshcontainer.merge(mesh)
        # Cube Face 3
        mesh.translate(0.5, 0.0, 0.0)
        mesh.rotate(90, 0, 0, 1)
        mesh.translate(0.0, -0.5, 0.0)
        self.meshcontainer.merge(mesh)
        # Cube Face 4
        mesh.translate(0.0,  0.5, 0.0)
        mesh.rotate(90, 0, 0, 1)
        mesh.translate(0.5, 0.0, 0.0)
        self.meshcontainer.merge(mesh)
        # Cube Face 5
        mesh.translate(-0.5,  0.0, 0.0)
        mesh.rotate(90, 0, 1, 0)
        mesh.translate(0.0, 0.0, -0.5)
        self.meshcontainer.merge(mesh)
        # Cube Face 6
        mesh.translate(0.0, 0.0, 0.5)
        mesh.rotate(180, 0, 1, 0)
        mesh.translate(0.0, 0.0, 0.5)
        self.meshcontainer.merge(mesh)
        # finally optimize the results
        #self.meshcontainer.optimize(tolerance=0.1)

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
    mesh = MeshContainer.MeshContainer()
    meshgen = MeshGenerator(mesh)
    meshgen.createCube(LOD=10)
    meshio = MeshIO.MeshIO(mesh)
    meshio.toFile("./Plane.mesh.xml", overwrite=True)

