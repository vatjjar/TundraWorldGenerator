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
            self.vertexBuffer       = MeshContainer.VertexBuffer()
            self.faces              = []
            self.boneAssignments    = MeshContainer.BoneAssignments()
            self.name               = ""
            self.materialref        = materialref
            self.operationtype      = operationtype
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
            self.vertices           = []
            self.normals            = []
            self.texcoords          = []    # There is actually up to eight of texcoords
            self.texcoords_1        = []    # Only two supported for testing
            self.diffusecolors      = []
            self.texcoordDimensions = [2, 2]
            self.resetMinMax()
        def resetMinMax(self):
            self.min_x = 100000.0
            self.max_x = -100000.0
            self.min_y = 100000.0
            self.max_y = -100000.0
            self.min_z = 100000.0
            self.max_z = -100000.0
            self.min_x_index = -1
            self.max_x_index = -1
            self.min_y_index = -1
            self.max_y_index = -1
            self.min_z_index = -1
            self.max_z_index = -1
            self.scaleF = 0.0
        def __message(self, msg):
            #print msg
            return
        def debugMinMax(self):
            print "---"
            print "Mesh min-max values:"
            print self.min_x, self.max_x, self.min_y, self.max_y, self.min_z, self.max_z
            print "Mesh min-max differences:"
            print self.max_x-self.min_x, self.max_y-self.min_y, self.max_z-self.min_z
            print "Scale factor:"
            print self.scaleF
            print "Mesh min-max indices:"
            print self.min_x_index, self.max_x_index, self.min_y_index, self.max_y_index, self.min_z_index, self.max_z_index
            print "---"
        def setTexcoordDimensions(self, t_array, t_dim):
            try:   self.texcoordDimensions[t_array] = t_dim
            except IndexError: pass

        def addVertex(self, v_list):    # Assume v_list is a three dimensional vertex definition
            for v in v_list: self.vertices.append(v)
            # Min, max values are updated as they are fed
            # into the array
            if v_list[0] < self.min_x: self.min_x = v_list[0]; self.min_x_index = len(self.vertices)/3-1
            if v_list[0] > self.max_x: self.max_x = v_list[0]; self.max_x_index = len(self.vertices)/3-1
            if v_list[1] < self.min_y: self.min_y = v_list[1]; self.min_y_index = len(self.vertices)/3-1
            if v_list[1] > self.max_y: self.max_y = v_list[1]; self.max_y_index = len(self.vertices)/3-1
            if v_list[2] < self.min_z: self.min_z = v_list[2]; self.min_z_index = len(self.vertices)/3-1
            if v_list[2] > self.max_z: self.max_z = v_list[2]; self.max_z_index = len(self.vertices)/3-1
            self.scaleF = max(self.max_x-self.min_x, max(self.max_y-self.min_y, self.max_z-self.min_z))
        def addNormal(self, n_list):
            for n in n_list: self.normals.append(n)
        def addTexcoord(self, t_list, bank):
            if len(t_list) != self.texcoordDimensions[bank]:
                self.__message("Warning: texcoord dimensions do not match expectation. Expected %d, got %d" % (len(t_list), self.texcoordDimensions[bank]))
            if bank == 0:
                for t in t_list: self.texcoords.append(t)
            if bank == 1:
                for t in t_list: self.texcoords_1.append(t)
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

        ###
        # Experimental. a method to build a 3D texture out from point cloud
        # position and color data. Also
        #
        def calcVertexMinMax(self):
            self.resetMinMax()
            vVector = [self.vertices[x:x+3]      for x in xrange(0, len(self.vertices), 3)]
            for i in range(len(vVector)):
                if vVector[i][0] < min_x: min_x = vVector[i][0]
                if vVector[i][0] > max_x: max_x = vVector[i][0]
                if vVector[i][1] < min_y: min_y = vVector[i][1]
                if vVector[i][1] > max_y: max_y = vVector[i][1]
                if vVector[i][2] < min_z: min_z = vVector[i][2]
                if vVector[i][2] > max_z: max_z = vVector[i][2]
            self.scaleF = max(self.max_x-self.min_x, max(self.max_y-self.min_y, self.max_z-self.min_z))

        def create3DTexcoords(self):
            vVector = [self.vertices[x:x+3] for x in xrange(0, len(self.vertices), 3)]
            self.texcoords = []
            self.setTexcoordDimensions(0, 3)
            for i in range(len(vVector)):
                self.texcoords.append((vVector[i][0] - self.min_x)/self.scaleF)     # vertex scaled into 0..1 cubic volume
                self.texcoords.append((vVector[i][1] - self.min_y)/self.scaleF)     # shall act as 3D tex coord
                self.texcoords.append((vVector[i][2] - self.min_z)/self.scaleF)

        def build3DTexture(self, size=32, filename="tex3d.bin"):
            import numpy
            #self.calcVertexMinMax()
            self.scaleF *= 1.001
            self.create3DTexcoords()
            cubicR = numpy.zeros((size, size, size), dtype=numpy.float32)
            cubicG = numpy.zeros((size, size, size), dtype=numpy.float32)
            cubicB = numpy.zeros((size, size, size), dtype=numpy.float32)
            cubicN = numpy.zeros((size, size, size), dtype=numpy.int32)
            vVector = [self.vertices[x:x+3]      for x in xrange(0, len(self.vertices), 3)]
            cVector = [self.diffusecolors[x:x+3] for x in xrange(0, len(self.diffusecolors), 3)]
            for i in range(len(vVector)):
                x = int(size*(vVector[i][0] - self.min_x)/self.scaleF)     # x, y, z will range in [0..size]
                y = int(size*(vVector[i][1] - self.min_y)/self.scaleF)
                z = int(size*(vVector[i][2] - self.min_z)/self.scaleF)
                #print x, y, z
                cubicR[x][y][z] += cVector[i][0]
                cubicG[x][y][z] += cVector[i][1]
                cubicB[x][y][z] += cVector[i][2]
                cubicN[x][y][z] += 1
            count = 0
            for x in range(size):               # Cumulating colors are averaged
                for y in range(size):
                    for z in range(size):
                        #print cubicN[x][y][z]
                        if cubicN[x][y][z] == 0: continue   # Division by zero exception does not pass with numpy
                        else: count += 1
                        #try: cubicR[x][y][z] /= cubicN[x][y][z]
                        #except ZeroDivisionError: pass
                        cubicR[x][y][z] /= cubicN[x][y][z]
                        cubicG[x][y][z] /= cubicN[x][y][z]
                        cubicB[x][y][z] /= cubicN[x][y][z]
                        #print cubicR[x][y][z], cubicG[x][y][z], cubicB[x][y][z]
            #print count
            # And now flush the binary to a file
            import array
            f = open(filename, "wb")
            buf = array.array("I")
            buf.fromlist([size, size, size])
            buf.tofile(f)                   # Write header. tex dimensions x, y, z
            buf = array.array("f")
            d_buf = []
            for z in range(size):
                for y in range(size):
                    for x in range(size):
                        d_buf.append(cubicR[x][y][z])
                        d_buf.append(cubicG[x][y][z])
                        d_buf.append(cubicB[x][y][z])
                        d_buf.append(1.0)
            buf.fromlist(d_buf)
            buf.tofile(f)
            f.close()

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
        print msg
        return

    def initialize(self):
        self.submeshes = []
        self.sharedgeometry = None
        self.submeshnames = []
        self.skeletonlinks = None
        # State variables, either shared vertex buffer or a submesh
        self.currentEntity = None

    #####
    # MeshContainer: Data attribute methods
    #
    def addVertex(self, v_list):
        try: self.currentEntity.addVertex(v_list)
        except AttributeError: pass
    def addNormal(self, n_list):
        try: self.currentEntity.addNormal(n_list)
        except AttributeError: pass
    def addTexcoord(self, t_list, bank):
        try: self.currentEntity.addTexcoord(t_list, bank)
        except AttributeError: pass
    def addDiffuseColor(self, c_list):
        try: self.currentEntity.addDiffuseColor(c_list)
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
    def setTexcoordDimensions(self, t_index, t_dim):
        try: self.currentEntity.setTexcoordDimensions(t_index, t_dim)
        except AttributeError: pass

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
        self.currentEntity = sm
    def newSharedGeometry(self):
        self.sharedgeometry = MeshContainer.VertexBuffer()
        self.currentEntity = self.sharedgeometry
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
            if (len(self.sharedgeometry.vertices) != 0):
                self.__message("  Vertices=%d" % (len(self.sharedgeometry.vertices)/3))
            if (len(self.sharedgeometry.normals) != 0):
                self.__message("  Normals=%d" % (len(self.sharedgeometry.normals)/3))
            if (len(self.sharedgeometry.texcoords) != 0):
                self.__message("   Texcoords 0 bank=%d, dimensions=%d" % (len(self.sharedgeometry.texcoords)/self.sharedgeometry.texcoordDimensions[0], self.sharedgeometry.texcoordDimensions[0]))
            if (len(self.sharedgeometry.texcoords_1) != 0):
                self.__message("   Texcoords 1 bank=%d, dimensions=%d" % (len(self.sharedgeometry.texcoords_1)/self.sharedgeometry.texcoordDimensions[1], self.sharedgeometry.texcoordDimensions[1]))

        index = 0
        self.__message(" Submeshes %d" % (len(self.submeshes)))
        for m in self.submeshes:
            self.__message("  Index %d" % index)
            self.__message("   Name = %s" % m.name)
            self.__message("   Material ref = %s" % m.materialref)
            if (len(m.vertexBuffer.vertices) != 0):
                self.__message("   Vertices=%d" % (len(m.vertexBuffer.vertices)/3))
            if (len(m.faces) != 0):
                self.__message("   Faces=%d" % (len(m.faces)/3))
            if (len(m.vertexBuffer.normals) != 0):
                self.__message("   Normals=%d" % (len(m.vertexBuffer.normals)/3))
            if (len(m.vertexBuffer.diffusecolors) != 0):
                self.__message("   Diffuse colors=%d" % (len(m.vertexBuffer.diffusecolors)/3))
            if (len(m.vertexBuffer.texcoords) != 0):
                self.__message("   Texcoords 0 bank=%d, dimensions=%d" % (len(m.vertexBuffer.texcoords)/m.vertexBuffer.texcoordDimensions[0], m.vertexBuffer.texcoordDimensions[0]))
            if (len(m.vertexBuffer.texcoords_1) != 0):
                self.__message("   Texcoords 1 bank=%d, dimensions=%d" % (len(m.vertexBuffer.texcoords_1)/m.vertexBuffer.texcoordDimensions[1], m.vertexBuffer.texcoordDimensions[1]))

###############################################################################
# Unit test case
#

if __name__ == "__main__":
    import getopt

    print "MeshContainer does not have unit test. Use MeshIO instead!"
    sys.exit(0)
