#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os

#############################################################################
# MeshContainer class
# - Subclasses:
#   - SubMesh
#   - VertexBuffer
#   - BoneAssignments
#

class MeshContainer():
    ####
    # Submesh holds all ogre mesh data related to OgreSubmesh class
    #
    class SubMesh():
        def __init__(self):
            self.vertexBuffer = MeshContainer.VertexBuffer()
            self.faces = []
            self.boneAssignments = MeshContainer.BoneAssignments()
            self.name = ""
        def __message(self, msg):
            #print msg
            return

        def addFace(self, f_list):
            for f in f_list: self.faces.append(f)
        def addVertex(self, v_list):
            self.vertexBuffer.addVertex(v_list)
        def addNormal(self, n_list):
            self.vertexBuffer.addNormal(n_list)
        def addTexcoord(self, t_list):
            self.vertexBuffer.addTexcoord(t_list)
        def addDiffuseColor(self, c_list):
            self.vertexBuffer.addDiffuseColor(c_list)
        def addBoneAssignment(self, b_list):
            self.boneAssignments.addVertexBoneAssignment(b_list)
        def addName(self, name):
            self.name = name
        #
        # Manipulators
        #
        def translate(self, x, y, z):
            self.__message("Submesh: translate %f %f %f" % (x, y, z))
            self.vertexBuffer.translate(x, y, z)

        def merge(self, submesh):
            self.__message("Submesh: merge")
            vOffset = len(self.vertexBuffer.vertices) / 3
            for i in submesh.faces:
                self.faces.append(i + vOffset)
            self.vertexBuffer.merge(submesh.vertexBuffer)

        def optimize(self, tolerance=0.01):
            self.__message("Submesh: optimize")

    ####
    # Vertex buffer holds positions, normals and texcoords needed for rendering
    #
    class VertexBuffer():
        def __init__(self):
            self.vertices = []
            self.normals = []
            self.texcoords = []
            self.diffusecolors = []
        def __message(self, msg):
            #print msg
            return

        def addVertex(self, v_list):
            for v in v_list: self.vertices.append(v)
        def addNormal(self, n_list):
            for n in n_list: self.normals.append(n)
        def addTexcoord(self, t_list):
            for t in t_list: self.texcoords.append(t)
        def addDiffuseColor(self, c_list):
            for c in c_list.split(" "): self.diffusecolors.append(float(c))
        #
        # Manipulators
        #
        def translate(self, x, y, z):
            self.__message("VertexBuffer: translate %f %f %f" % (x, y, z))
            for i in range(len(self.vertices)/3):
                self.vertices[i*3+0] += x
                self.vertices[i*3+1] += y
                self.vertices[i*3+2] += z

        def merge(self, vertexbuffer):
            self.__message("VertexBuffer: merge")
            #vOffset = len(self.vertices) / 3
            for i in vertexbuffer.vertices:
                self.vertices.append(i)
            for i in vertexbuffer.normals:
                self.normals.append(i)
            for i in vertexbuffer.texcoords:
                self.texcoords.append(i)
            for i in vertexbuffer.diffusecolors:
                self.diffusecolors.append(i)

        def optimize(self, tolerance=0.01):
            self.__message("VertexBuffer: optimize")
            pass

    ####
    # Bone assignments are links between skeleton and mesh structure
    # TODO: bone assignments are not supported yet.
    #
    class BoneAssignments():
        def __init__(self):
            self.vertexBoneAssignments = []
        def addVertexBoneAssignment(self, b_list):
            for i in b_list: self.vertexBoneAssignments.append(i)

    ####
    # Basic MeshContainer API:
    # - __init__
    # - fromFile()
    # - toFile
    #
    def __init__(self):
        self.initialize()

    def __message(self, msg):
        #print msg
        return

    def initialize(self):
        self.submeshes = []
        self.sharedgeometry = None
        self.submeshnames = []
        self.skeletonlinks = None
        # State variables, either shared vertex buffer or submesh
        self.currententity = None

    #####
    # MeshContainer: Data attribute methods
    #
    def addVertex(self, v_list):
        try: self.currententity.addVertex(v_list)
        except AttributeError: pass
    def addNormal(self, n_list):
        try: self.currententity.addNormal(n_list)
        except AttributeError: pass
    def addTexcoord(self, t_list):
        try: self.currententity.addTexcoord(t_list)
        except AttributeError: pass
    def addDiffuseColor(self, c_list):
        try: self.currententity.addDiffuseColor(c_list)
        except AttributeError: pass
    def addFace(self, f_list):
        try: self.submeshes[-1].addFace(f_list)
        except IndexError: pass
    def addVertexBoneAssignment(self, b_list):
        try: self.submeshes[-1].addBoneAssignment(b_list)
        except IndexError: pass
    def addSkeletonLink(self):
        pass
    def addSubmeshName(self, name, index):
        try: self.submeshes[int(index)].addName(name)
        except IndexError: pass

    #####
    # MeshContainer: Data container methods
    # - newSubmesh
    # - newSharedGeometry
    # - newSubmeshName
    # - newSkeletonLink
    # - newBoneAssignment
    #
    def newSubmesh(self):
        sm = MeshContainer.SubMesh()
        self.submeshes.append(sm)
        self.currententity = sm
    def newSharedGeometry(self):
        self.sharedgeometry = MeshContainer.VertexBuffer()
        self.currententity = self.sharedgeometry
    def newSubmeshName(self, name):
        self.submeshname.append(name)
    def newSkeletonLink(self):
        pass
    def newBoneAssignment(self):
        pass

    #####
    # MeshContainer: Manipulators
    # - translate()
    # - merge()
    # - optimize()
    #
    def translate(self, x, y, z):
        self.__message("Meshcontainer: translate %f %f %f" % (x, y, z))
        for s in self.submeshes:
            s.translate(x, y, z)
        if self.sharedgeometry != None:
            self.sharedgeometry.translate(x, y, z)

    def merge(self, meshcontainer):
        """ merge() is a destructive merge operation of two meshcontainers. Target
            meshcontainer (self) is appended with the data in source meshcontainer.
            Note: This method only appends the data, and creates new submeshes on
            the fly, if needed. It also treats the sharedgeometry, if one is defined.
            However, it does not check for duplicates. If this is of the essence,
            then use optimize() method with a correct tolerance to shape the
            merged mesh further.
        """
        self.__message("Meshcontainer: merge")
        #
        # First submesh array merge ...
        #
        for i in range( max(len(self.submeshes), len(meshcontainer.submeshes)) ):
            try: sm1 = self.submeshes[i]
            except IndexError:
                self.newSubmesh()
                sm1 = self.submeshes[i]
            try: sm2 = meshcontainer.submeshes[i]
            except IndexError:
                break
            sm1.merge(sm2)
        #
        # ... and then shared geometry
        #
        if self.sharedgeometry == None:
            if meshcontainer.sharedgeometry != None:
                self.newSharedGeometry()
                self.sharedgeometry.merge(meshcontainer.sharedgeometry)
        else:
            if meshcontainer.sharedgeometry != None:
                self.sharedgeometry.merge(meshcontainer.sharedgeometry)

    def optimize(self, tolerance=0.01):
        self.__message("MeshContainer: optimize")
        pass

    #####
    # MeshContainer: debug
    #
    def printStatistics(self):
        self.__message("MeshContainer:")
        self.__message(" Shared vertices: %s" % (not self.sharedgeometry == None))
        if self.sharedgeometry != None:
            self.__message("  Vertices=%d, texcoords=%d, normal=%d" % (len(self.sharedgeometry.vertices)/3,
                                                              len(self.sharedgeometry.texcoords)/2,
                                                              len(self.sharedgeometry.normals)/3))
        self.__message(" Submeshes %d" % (len(self.submeshes)))
        for m in self.submeshes:
            self.__message("  Name = %s" % (m.name))
            self.__message("  Vertices=%d, faces=%d, normal=%d texcoords=%d, diffuse_colors=%d" % (len(m.vertexBuffer.vertices)/3,
                                                                       len(m.faces)/3,
                                                                       len(m.vertexBuffer.normals)/3,
                                                                       len(m.vertexBuffer.texcoords)/2,
                                                                       len(m.vertexBuffer.diffusecolors)/3))

###############################################################################
# Unit test case
#

if __name__ == "__main__":
    import getopt

    print "MeshContainer does not have unit test. Use MeshIO instead!"
    sys.exit(0)
