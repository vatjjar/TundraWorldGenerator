#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os, io
import random
import math

import MeshContainer
import MeshIO

class MeshGenerator():
    """ class MeshGenerator(): A collection of procedural methods for
        creating mesh files with various content.
    """

    def __init__(self, meshcontainer, sharedgeometry=False):
        """ MeshGenerator.__init__(meshcontainer, sharedgeometry):
        """
        self.meshcontainer = meshcontainer
        self.sharedgeometry = sharedgeometry

#############################################################################
# Procedural primitive creators
#
# - Plane
# - Cube
# - Cylinder
# - Sphere
#############################################################################

    #########################################################################
    # Plane
    # - Creates a planar mesh
    #
    def createPlane(self, LOD=1, materialref=""):
        """ MeshGenerator.createPlane(self, LOD): Create a plane mesh component
            - Method will create a plane mesh component in XZ-plane whose size is 1 times 1 units in
              coordinate system and which is centered to origin.
        """
        self.meshcontainer.initialize()
        if self.sharedgeometry == True:
            self.meshcontainer.newSharedGeometry()
        else:
            self.meshcontainer.newSubmesh(materialref=materialref)     # The plane is pushed into single submesh

        x_delta = 1.0 / LOD
        z_delta = 1.0 / LOD
        #
        # First we create vertices, normals and texcoords
        #
        for x in range(LOD+1):
            for z in range(LOD+1):
                self.meshcontainer.addVertex([-0.5 + x*x_delta, 0.0, -0.5 + z*z_delta])
                self.meshcontainer.addNormal([0.0, 1.0, 0.0])
                self.meshcontainer.addTexcoord([x*x_delta, z*z_delta], 0)
        #
        # And according to above, we create the faces
        #
        if self.sharedgeometry == True:
            self.meshcontainer.newSubmesh(materialref=materialref)
        for x in range(LOD):
            for z in range(LOD):
                self.meshcontainer.addFace([z+x*(LOD+1), 1+z+x*(LOD+1), LOD+2+z+x*(LOD+1)])
                self.meshcontainer.addFace([z+x*(LOD+1), LOD+2+z+x*(LOD+1), LOD+1+z+x*(LOD+1)])

    #########################################################################
    # Cube
    # - Constructs a cubic mesh from 6 planar meshes. Does the merge with
    #   meshcontainer provided translation tools
    #
    def createCube(self, LOD=1):
        self.meshcontainer.initialize()
        self.meshcontainer.newSubmesh()
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
        mesh.rotate(180, 1, 0, 0)
        mesh.translate(0.0, -0.5, 0.0)
        self.meshcontainer.merge(mesh)
        # Cube Face 3
        mesh.translate(0.0, 0.5, 0.0)
        mesh.rotate(90, 1, 0, 0)
        mesh.translate(0.0, 0.0, -0.5)
        self.meshcontainer.merge(mesh)
        # Cube Face 4
        mesh.translate(0.0, 0.0, 0.5)
        mesh.rotate(90, 0, 1, 0)
        mesh.translate(-0.5, 0.0, 0.0)
        self.meshcontainer.merge(mesh)
        # Cube Face 5
        mesh.translate(0.5,  0.0, 0.0)
        mesh.rotate(90, 0, 1, 0)
        mesh.translate(0.0, 0.0, 0.5)
        self.meshcontainer.merge(mesh)
        # Cube Face 6
        mesh.translate(0.0, 0.0, -0.5)
        mesh.rotate(90, 0, 1, 0)
        mesh.translate(0.5, 0.0, 0.0)
        self.meshcontainer.merge(mesh)

    #########################################################################
    # Cylinder
    # - Constructs a cylinder with experimental support for callbacks
    #
    def createCylinder(self, slices=2, LOD=1, minH=0.0, maxH=1.0, callback=None):
        nR = 5+LOD
        rDelta = 2.0*math.pi/nR
        hDelta = (maxH-minH)/(slices-1)
        print "MeshGenerator::createCylinder slices=%d, nR=%d, rDelta=%f, hDelta=%f" % (slices, nR, rDelta, hDelta)

        self.meshcontainer.initialize()
        if self.sharedgeometry == True:
            self.meshcontainer.newSharedGeometry()
        else:
            self.meshcontainer.newSubmesh()     # The cylinder is pushed into single submesh

        for i in xrange(slices):                # Vertical slices
            for j in xrange(nR):                # Circular slices
                if callback == None:
                    r = 0.5
                else:
                    r = callback(i*hDelta, j*rDelta)
                self.meshcontainer.addVertex([r*math.sin(j*rDelta), minH+i*hDelta, r*math.cos(j*rDelta)])
                self.meshcontainer.addNormal([0.0, -1.0, 0.0]) # This is bogus, for the time being
                self.meshcontainer.addTexcoord([j*1.0/(nR-1), i*hDelta], 0)

        if self.sharedgeometry == True:
            self.meshcontainer.newSubmesh()

        for i in xrange(slices-1):
            for j in xrange(nR-1):
                self.meshcontainer.addFace([i*nR+j, (i+1)*nR+j+1, (i+1)*nR+j])
                self.meshcontainer.addFace([i*nR+j, i*nR+j+1, (i+1)*nR+j+1])
            self.meshcontainer.addFace([i*nR+j+1, (i+1)*nR+0, (i+1)*nR+j+1])
            self.meshcontainer.addFace([i*nR+j+1, i*nR+0, (i+1)*nR+0])

        # Surface normal re-calculation should be here once the faces have been set ...


    #########################################################################
    # Sphere
    # - Constructs a Sphere primitive
    #
    def createSphere(self, LOD=1):
        nR = 5+LOD
        slices = LOD+1
        hDelta = 2.0/slices

        self.meshcontainer.initialize()
        if self.sharedgeometry == True:
            self.meshcontainer.newSharedGeometry()
        else:
            self.meshcontainer.newSubmesh()     # The sphere is pushed into single submesh

        for i in xrange(slices+1):          # Vertical slices
            r = math.sqrt(1.0-(-1.0+i*hDelta)*(-1.0+i*hDelta))
            for j in xrange(nR):            # Circular slices
                a = j*2*math.pi/(nR-1)      # Current circle angle
                self.meshcontainer.addVertex([r*math.sin(a), -1.0+i*hDelta, r*math.cos(a)])
                self.meshcontainer.addNormal([0.0, -1.0, 0.0]) # This is bogus
                self.meshcontainer.addTexcoord([j*1.0/(nR-1), i*hDelta], 0)

        if self.sharedgeometry == True:
            self.meshcontainer.newSubmesh()

        for i in xrange(slices):
            for j in xrange(nR-1):
                self.meshcontainer.addFace([i*nR+j, (i+1)*nR+j,   (i+1)*nR+j+1])
                self.meshcontainer.addFace([i*nR+j, (i+1)*nR+j+1, i*nR+j+1])

#############################################################################

if __name__ == "__main__": # if run standalone
    mesh = MeshContainer.MeshContainer()
    meshgen = MeshGenerator(mesh, sharedgeometry=True)
    meshgen.createPlane(LOD=1)
    #meshgen.createCube(LOD=1)
    #meshgen.createCylinder(0.25, 0.75, LOD=10, end1=True, end2=True)
    #meshgen.createSphere(LOD=15)
    meshio = MeshIO.MeshIO(mesh)
    meshio.toFile("./Plane.mesh.xml", overwrite=True)

