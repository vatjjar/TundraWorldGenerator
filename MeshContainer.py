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

    ####
    # Vertex buffer holds positions, normals and texcoords needed for rendering
    #
    class VertexBuffer():
        def __init__(self):
            self.vertices = []
            self.normals = []
            self.texcoords = []
            self.diffusecolors = []
        def addVertex(self, v_list):
            for v in v_list: self.vertices.append(v)
        def addNormal(self, n_list):
            for n in n_list: self.normals.append(n)
        def addTexcoord(self, t_list):
            for t in t_list: self.texcoords.append(t)
        def addDiffuseColor(self, c_list):
            for c in c_list.split(" "): self.diffusecolors.append(float(c))

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
    # MeshContainer: debug
    #
    def printStatistics(self):
        print "MeshContainer:"
        print " Shared vertices: %s" % (not self.sharedgeometry == None)
        if self.sharedgeometry != None:
            print "  Vertices=%d, texcoords=%d, normal=%d" % (len(self.sharedgeometry.vertices)/3,
                                                              len(self.sharedgeometry.texcoords)/2,
                                                              len(self.sharedgeometry.normals)/3)
        print " Submeshes %d" % (len(self.submeshes))
        for m in self.submeshes:
            print "  Name = %s" % (m.name)
            print "  Vertices=%d, faces=%d, normal=%d texcoords=%d, diffuse_colors=%d" % (len(m.vertexBuffer.vertices)/3,
                                                                       len(m.faces)/3,
                                                                       len(m.vertexBuffer.normals)/3,
                                                                       len(m.vertexBuffer.texcoords)/2,
                                                                       len(m.vertexBuffer.diffusecolors)/3)

###############################################################################
# Unit test case
#

if __name__ == "__main__":
    import getopt

    print "MeshContainer does not have unit test. Use MeshIO instead!"
    sys.exit(0)
