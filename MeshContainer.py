#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os
import math

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
        def __init__(self, materialref="", operationtype="triangle_list"):
            self.vertexBuffer = MeshContainer.VertexBuffer()
            self.faces = []
            self.boneAssignments = MeshContainer.BoneAssignments()
            self.name = ""
            self.materialref = materialref
            self.operationtype = operationtype
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

        def rotate(self, angle, x, y, z):
            self.__message("Submesh: rotate %f around %f %f %f" % (angle, x, y, z))
            self.vertexBuffer.rotate(angle, x, y, z)

        def merge(self, submesh):
            self.__message("Submesh: merge")
            vOffset = len(self.vertexBuffer.vertices) / 3
            for i in submesh.faces:
                self.faces.append(i + vOffset)
            self.vertexBuffer.merge(submesh.vertexBuffer)

        def resetOrigin(self):
            pass

        def optimize(self, tolerance=0.01):
            self.__message("Submesh: optimize")
            d = {}
            #
            # First the eucleidean distance is checked whether we have overlapping vertices:
            #
            for i in range(len(self.vertexBuffer.vertices)/3):
                for j in range(i+1, len(self.vertexBuffer.vertices)/3):
                    a = self.vertexBuffer.vertices[3*i+0] - self.vertexBuffer.vertices[3*j+0]
                    b = self.vertexBuffer.vertices[3*i+1] - self.vertexBuffer.vertices[3*j+1]
                    c = self.vertexBuffer.vertices[3*i+2] - self.vertexBuffer.vertices[3*j+2]
                    eta = a*a + b*b + c*c
                    eta = math.sqrt(eta)
                    if eta < tolerance:
                        #print "eta %f %d %d" % (eta, i, j)
                        d[j] = i                                # Populate search-replce dict
            #
            # If search-replace dictionary is populated, then we have some elements removed
            #
            if len(d.items()) > 0:
                #
                # First the face index reordering ...
                #
                for i in range(len(self.faces)):
                    try:
                        #print "replace %d with %d" % (self.faces[i], d[self.faces[i]])
                        self.faces[i] = d[self.faces[i]]
                    except KeyError: pass
                #
                # ... and then reconstruction of the element lists after deletion
                #
                uniqueFaces = []
                for i in self.faces: # First gather a list of unique vertices (indicated by the faces)
                    if i not in uniqueFaces: uniqueFaces.append(i)
                newVertices      = []
                newNormals       = []
                newTexcoords     = []
                newDiffusecolors = []
                for i in uniqueFaces:
                    # Vertices
                    newVertices.append(self.vertexBuffer.vertices[i*3+0])
                    newVertices.append(self.vertexBuffer.vertices[i*3+1])
                    newVertices.append(self.vertexBuffer.vertices[i*3+2])
                    # Normals
                    try:
                        newNormals.append(self.vertexBuffer.normals[i*3+0])
                        newNormals.append(self.vertexBuffer.normals[i*3+1])
                        newNormals.append(self.vertexBuffer.normals[i*3+2])
                    except IndexError: pass
                    # Texcoords
                    try:
                        newTexcoords.append(self.vertexBuffer.texcoords[i*2+0])
                        newTexcoords.append(self.vertexBuffer.texcoords[i*2+1])
                    except IndexError: pass
                    # Diffuse colors
                    try:
                        newDiffusecolors.append(self.vertexBuffer.diffusecolors[i*3+0])
                        newDiffusecolors.append(self.vertexBuffer.diffusecolors[i*3+1])
                        newDiffusecolors.append(self.vertexBuffer.diffusecolors[i*3+2])
                    except IndexError: pass
                #print "Previous vertices %d, new vertices %d" % (len(self.vertexBuffer.vertices), len(newVertices))
                self.vertexBuffer.vertices      = newVertices
                self.vertexBuffer.normals       = newNormals
                self.vertexBuffer.texcoords     = newTexcoords
                self.vertexBuffer.diffusecolors = newDiffusecolors

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

        def rotate(self, angle, x, y, z):
            sinA = math.sin(angle * math.pi / 180.0)
            cosA = math.cos(angle * math.pi / 180.0)
            # Normalize rotation vector
            m = math.sqrt(x*x + y*y + z*z)
            x = x/m; y = y/m; z = z/m
            # Calc temp variables, for populating the rotation matrix
            xs = x*sinA; ys = y*sinA; zs = z*sinA
            ca = 1.0 - cosA
            # Populate rotation matrix
            mat = [ [x*x*ca+cosA,  x*y*ca-zs,    x*z*ca+ys,  ],
                    [x*y*ca+zs,    y*y*ca+cosA,  y*z*ca-xs,  ],
                    [x*z*ca-ys,    y*z*ca+xs,    z*z*ca+cosA ] ]
            #
            # Now rotate all vertices and normals
            #
            vr = [0.0, 0.0, 0.0]    # temporary vector
            for i in range(len(self.vertices)/3):
                for j in xrange(3):
                    vr[j] = mat[j][0]*self.vertices[i*3+0] + \
                            mat[j][1]*self.vertices[i*3+1] + \
                            mat[j][2]*self.vertices[i*3+2]
                self.vertices[i*3+0] = vr[0]
                self.vertices[i*3+1] = vr[1]
                self.vertices[i*3+2] = vr[2]
                for j in xrange(3):
                    vr[j] = mat[j][0]*self.normals[i*3+0] + \
                            mat[j][1]*self.normals[i*3+1] + \
                            mat[j][2]*self.normals[i*3+2]
                self.normals[i*3+0] = vr[0]
                self.normals[i*3+1] = vr[1]
                self.normals[i*3+2] = vr[2]

        def merge(self, vertexbuffer):
            self.__message("VertexBuffer: merge")
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
    def newSubmesh(self, materialref="", operationtype="triangle_list"):
        sm = MeshContainer.SubMesh(materialref=materialref, operationtype=operationtype)
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

    def rotate(self, angle, x, y, z):
        self.__message("Meshcontainer: rotate %f around %f %f %f" % (angle, x, y, z))
        for s in self.submeshes:
            s.rotate(angle, x, y, z)
        if self.sharedgeometry != None:
            self.sharedgeometry.rotate(angle, x, y, z)

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
        for m in self.submeshes:
            m.optimize(tolerance)

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
