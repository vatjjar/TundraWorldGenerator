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
            self.min_x_index        = -1
            self.max_x_index        = -1
            self.min_y_index        = -1
            self.max_y_index        = -1
            self.min_z_index        = -1
            self.max_z_index        = -1
            self.min_x              =  1000000.0
            self.max_x              = -1000000.0
            self.min_y              =  1000000.0
            self.max_y              = -1000000.0
            self.min_z              =  1000000.0
            self.max_z              = -1000000.0
            # Statistic arrays for edgecollapse
            self.edgeCosts          = None
            self.uniqueEdges        = []

        def __message(self, msg):
            print msg
            return

        def addFace(self, f_list):
            for f in f_list: self.faces.append(f)
        def addVertex(self, v_list):
            self.vertexBuffer.addVertex(v_list)
        def addNormal(self, n_list):
            self.vertexBuffer.addNormal(n_list)
        def addTexcoord(self, t_list, bank):
            self.vertexBuffer.addTexcoord(t_list, bank)
        def addDiffuseColor(self, c_list):
            self.vertexBuffer.addDiffuseColor(c_list)
        def addBoneAssignment(self, b_list):
            self.boneAssignments.addVertexBoneAssignment(b_list)
        def addName(self, name):
            self.name = name
        def setTexcoordDimensions(self, t_bank, t_dim):
            self.vertexBuffer.setTexcoordDimensions(t_bank, t_dim)
        def setMaterial(self, materialref):
            self.materialref = materialref

        #
        # Manipulators
        #
        def translate(self, x, y, z):
            self.__message("Submesh: translate %f %f %f" % (x, y, z))
            self.vertexBuffer.translate(x, y, z)

        def rotate(self, angle, x, y, z):
            self.__message("Submesh: rotate %f around %f %f %f" % (angle, x, y, z))
            self.vertexBuffer.rotate(angle, x, y, z)

        def scale(self, x, y, z):
            self.__message("Submesh: scale %f %f %f" % (x, y, z))
            self.vertexBuffer.scale(x, y, z)

        def merge(self, submesh, shared_vertices=-1):
            self.__message("Submesh: merge")
            vOffset = shared_vertices
            if shared_vertices == -1:
                vOffset = len(self.vertexBuffer.vertices) / 3
            for i in submesh.faces:
                self.faces.append(i + vOffset)
            self.vertexBuffer.merge(submesh.vertexBuffer)

        def resetOrigin(self):
            pass

        def buildAABBMesh(self, meshcontainer, sg=None):
            self.__message("Submesh: buildAABBMesh")
            vb = self.vertexBuffer
            if sg != None: vb = sg

            meshcontainer.setTexcoordDimensions(0, vb.texcoordDimensions[0])
            meshcontainer.setTexcoordDimensions(1, vb.texcoordDimensions[1])
            meshcontainer.setMaterial(self.materialref)

            self.__findSubmeshMinMax(sg)
            self.__debugSubmeshMinMax(sg)
            for x in [vb.vertices[3*self.min_x_index+0], vb.vertices[3*self.max_x_index+0]]:
                for y in [vb.vertices[3*self.min_y_index+1], vb.vertices[3*self.max_y_index+1]]:
                    for z in [vb.vertices[3*self.max_z_index+2], vb.vertices[3*self.min_z_index+2]]:
                        vi = self.__findClosestVertex(sg, x, y, z)
                        meshcontainer.addVertex(vb.vertices[3*vi:3*vi+3])
                        try: meshcontainer.addNormal(vb.normals[3*vi:3*vi+3])
                        except IndexError: pass
                        try: meshcontainer.addTexcoord(vb.texcoords[vb.texcoordDimensions[0]*vi:vb.texcoordDimensions[0]*vi+vb.texcoordDimensions[0]], 0)
                        except IndexError: pass
                        try: meshcontainer.addTexcoord(vb.texcoords_1[vb.texcoordDimensions[1]*vi:vb.texcoordDimensions[1]*vi+vb.texcoordDimensions[1]], 1)
                        except IndexError: pass
                        try: meshcontainer.addDiffuseColor(vb.diffusecolors[3*vi:3*vi+3])
                        except IndexError: pass
            for f in [ [0,2,3], [0,3,1], [1,3,7], [1,7,5], [5,7,6], [5,6,4], [4,6,2], [4,2,0], [2,6,7], [2,7,3], [5,1,0], [5,0,4] ]:
                meshcontainer.addFace(f)

        def prepareCollapse(self, sg):
            """ prepareCollapse(sg): prepareCollapse prepares some internal datastructures for
                edge collapse algorithm. Primarily vertex reference counts and number of
                unique edges in the mesh are needed. These values need to be calculated from
                the original data, before it is being altered. Hence, the application needs
                to perform this activity before calling actual edge collapse.
                This method should not be called directly, but instead through the MeshContainer
                wrapper method. It will take care of the calling conventions.
            """
            import Queue
            self.__message("Submesh: prepareCollapse()")
            vb = self.vertexBuffer
            if sg != None: vb = sg
            #
            # First, vertex refcounts are updated for active vertex buffer
            #
            vb.setupStatistics()
            for f in self.faces:
                vb.vRefCounts[f] += 1
            self.__message("Submesh: prepareCollapse, updated vertex refs for %d faces" % (len(self.faces)/3))
            #
            # Second, a list of unique edges are built.
            #
            self.uniqueEdges = []               # Previous data is destroyed
            self.edgeCosts   = None
            self.temp_d = {}
            for i in range(len(self.faces)/3):
                f = self.faces[3*i:3*i+3]
                f.sort()
                self.__addUniqueEdge(f[0], f[1])
                self.__addUniqueEdge(f[1], f[2])
                self.__addUniqueEdge(f[2], f[0])
            self.__message("Submesh, prepareCollapse: Added %d unique edges out of %d faces and %d vertices" % \
                            (len(self.uniqueEdges), len(self.faces)/3, len(vb.vertices)/3))
            #
            # Third, sort all individual edges into priority queue based on their length.
            # Cost method for the edge collapse can vary, but for this implementation we
            # use edge length. Shortest edges are collapsed first.
            #
            index = 0
            self.edgeQueue = Queue.PriorityQueue()
            for e in self.uniqueEdges:
                v1 = vb.vertices[3*e[0]:3*e[0]+3]   # We do not need sqrt() in length, since due to its linearity
                v2 = vb.vertices[3*e[1]:3*e[1]+3]   # it does not change the order of edges. Hence, squared length is enough.
                l = (v2[0]-v1[0])*(v2[0]-v1[0]) + (v2[1]-v1[1])*(v2[1]-v1[1]) + (v2[2]-v1[2])*(v2[2]-v1[2])
                self.edgeQueue.put((l, index))
                index += 1

        def collapseEdges(self, sg, percentage=0.80, amount=None, d={}):
            import Queue
            """ Submesh.collapseEdges(sg, percentage, amount, d): collapseEdges() method will start
                collapsing the edges of the given submesh. Edge collapse is performed in the order
                which is indicated by the priority queue, prepared by prepareCollapse() method.
                Shortest edge is collapsed first. During a single collapse operation, the method
                is to remove one edge, and other one of its vertices and then adjust the remaining
                faces to correspond the situation. Vertex ref counts are used when deciding which vertex
                to collapse. The one with higher number of references will be removed. It could be
                other way around as well, but having only a few references for a vertex, it votes it
                being a hard edge. It is beneficial to keep hard edges, since losing them will break
                the overall original geometry of the mesh.
            """
            self.__message("Submesh: collapseEdges(percentage=%f, amount=%s)" % (percentage, str(amount)))
            vb = self.vertexBuffer
            if sg != None: vb = sg
            #
            # First, start removing edges in priority order and at the same time update
            # a search-replace dictionary for next phase for optimization of the face list.
            # The dictionary is used later to reorder remaining faces.
            #
            target = amount
            if amount == None:
                target = int(len(self.uniqueEdges)*percentage)
            self.__message("Submesh, collapseEdges: Targeting to remove %d edges out of %d" % (target, len(self.uniqueEdges)))

            print "d start %d" % len(d)

            counter = 0
            while counter < target:
                try: edge = self.edgeQueue.get(block=False)
                except Queue.Empty: break
                e = self.uniqueEdges[edge[1]]
                if vb.vRefCounts[e[0]] < vb.vRefCounts[e[1]]:   # v1 will be kept, v2 will be removed
                    v1 = e[0]; v2 = e[1]                        # Order is decided based on vertex refcounts.
                else:
                    v1 = e[1]; v2 = e[0]

                #self.__message("Trying edge %d-%d, (vrefs %d-%d)" % (v1, v2, vb.vRefCounts[v1], vb.vRefCounts[v2]))
                try: v1 = d[v1]
                except KeyError: pass   # to the root vertex.
                try: t = d[v2]
                except KeyError:
                    d[v2] = v1              # Replacement indices are accepted into dict, only if they are new
                    if v1 == 2881:
                        print "Collapsing %d into %d" % (v2, v1)
                    #self.__message("Collapsing edge #%d: %d-%d, (vrefs %d-%d)" % (counter, v1, v2, vb.vRefCounts[v1], vb.vRefCounts[v2]))
                    for (a, b) in d.items():
                        if b == v2:
                            d[a] = v1
                            #self.__message("Translating collapse of %d from %d to %d" % (a, b, v1))
                counter += 1

            self.__message("%d entries added into collapse buffer" % len(d))

            #
            # After edge collapse, the remaing faces are reordered. There are three types of faces now:
            #  1) Those, which are ok, and are reformed by the collapse
            #  2) Those, which are ok, but nearly zero in surface area (i.e. all three vertices in the same line)
            #  3) Those, which have 1-2 missing vertices due to collapse.
            # Faces in categories 2 and 3 are dropped from the list.
            #
            new_faces = []
            m = 0
            for f in range(len(self.faces)/3):
                #print "face", f, self.faces[3*f+0], self.faces[3*f+1], self.faces[3*f+2]
                try: self.faces[3*f+0] = d[self.faces[3*f+0]]; m+=1   # Re-order indices based on the collected
                except KeyError: pass                           # dictionary
                try: self.faces[3*f+1] = d[self.faces[3*f+1]]; m+=1
                except KeyError: pass
                try: self.faces[3*f+2] = d[self.faces[3*f+2]]; m+=1
                except KeyError: pass
                # Case 3) missing vertices?
                #print "    ", f, self.faces[3*f+0], self.faces[3*f+1], self.faces[3*f+2]
                if self.faces[3*f+0] == self.faces[3*f+1] or \
                   self.faces[3*f+0] == self.faces[3*f+2] or \
                   self.faces[3*f+1] == self.faces[3*f+2]:
                    continue
                #print "face", f, 3*f+0, 3*f+1, 3*f+2, self.faces[3*f+0], self.faces[3*f+1], self.faces[3*f+2]
                # and case 2) face exists, but is nearly void. It is calculated via face edge dot product
                if 0:
                    vec1 = [ (vb.vertices[3*self.faces[3*f+1]+0] - vb.vertices[3*self.faces[3*f+0]+0]), \
                             (vb.vertices[3*self.faces[3*f+1]+1] - vb.vertices[3*self.faces[3*f+0]+1]), \
                             (vb.vertices[3*self.faces[3*f+1]+2] - vb.vertices[3*self.faces[3*f+0]+2]) ]
                    vec2 = [ (vb.vertices[3*self.faces[3*f+2]+0] - vb.vertices[3*self.faces[3*f+1]+0]), \
                             (vb.vertices[3*self.faces[3*f+2]+1] - vb.vertices[3*self.faces[3*f+1]+1]), \
                             (vb.vertices[3*self.faces[3*f+2]+2] - vb.vertices[3*self.faces[3*f+1]+2]) ]
                    dot = abs(abs(vec1[0]*vec2[0] + vec1[1]*vec2[1] + vec1[2]*vec2[2])-1)
                    if dot < 0.01:
                        self.__message("Face edge dot product (%f) value less than 0.01, ignoring face!" % (dot))
                        continue
                self.__addUniqueFace(self.faces[3*f:3*f+3], new_faces)
            # Finally, replace the old face list with the collapsed one
            print "d end %d" % len(d)
            self.faces = new_faces

        def collapseVertexbuffer(self, sg, offset, rdict, va, na, ta1, ta2, ca):
            """ Submesh.collapseVertexbuffer(sg, offset, rdict, va, na, ta1, ta2, ca): After statistics are
                calculated and edges are collapsed with collapseEdges(), there are a list of unreferenced
                and collapsed vertices, due to face removal operation. These vertices are collected and dropped
                from the list. Likewise, the indexing of the faces is recalculated afterwards.
                The case of sharedgeometry is a problematic once, since a single submesh cannot be collapsed
                without having knowledge about the others ones. That is why this method takes vectors of
                temporary data. Those vectors are updated directly to the submesh, if sharedgeometry does not
                exist. Otherwise they are held back, and applied collectively at the higher level, in meshcontainer.
            """
            self.__message("Submesh: collapseVertexbuffer()")
            vb = self.vertexBuffer
            if sg != None: vb = sg

            #print "rdict start: %d" % len(rdict)

            start = offset
            for i in range(len(self.faces)):
                t = self.faces[i]
                try:
                    self.faces[i] = rdict[self.faces[i]]        # vertex already copied into vectors -> skip
                    #print "skipping vertex %d" % self.faces[i]
                    continue
                except KeyError:
                    rdict[self.faces[i]] = offset               # Take new vertex into the list
                if (len(vb.vertices     [3*self.faces[i]:3*self.faces[i]+3]) == 0):
                    print "something went wrong! i %d, f %d (old=%d)" % (i, self.faces[i], t)
                va  += vb.vertices     [3*self.faces[i]:3*self.faces[i]+3]  # and append the data
                na  += vb.normals      [3*self.faces[i]:3*self.faces[i]+3]
                ca  += vb.diffusecolors[vb.diffusecolorDimensions*self.faces[i]:vb.diffusecolorDimensions*self.faces[i]+vb.diffusecolorDimensions]
                ta1 += vb.texcoords    [vb.texcoordDimensions[0]*self.faces[i]:vb.texcoordDimensions[0]*self.faces[i]+vb.texcoordDimensions[0]]
                ta2 += vb.texcoords_1  [vb.texcoordDimensions[1]*self.faces[i]:vb.texcoordDimensions[1]*self.faces[i]+vb.texcoordDimensions[1]]
                self.faces[i] = offset
                #if self.faces[i] > 1000 and self.faces[i] < 1010:
                #    print "adding vertex %d as index %d" % (self.faces[i], offset)
                offset += 1
            print "v start %d v end %d\n" % (len(vb.vertices)/3, offset-start-1)
            if sg == None:
                vb.vertices      = va                           # if noshared geometry, the ordered data can be
                vb.normals       = na                           # applied directly into this submesh
                vb.texcoords     = ta1
                vb.texcoords_1   = ta2
                vb.diffusecolors = ca

            #print "rdict end: %d" % len(rdict)
            return offset

        def recalculateNormals(self, sg=None):
            #
            # realculateNormals() loops through the submesh facelist, calculated surface normal for each of them
            # and once that is complete, then loop through all vertices and calculate vertex normals based on
            # all neighboring faces' surface normals.
            #
            print "Submesh: recalculateNormals"

            fVector = [self.faces[x:x+3]                     for x in xrange(0, len(self.faces),                 3)]
            if sg == None:
                self.vertexBuffer.normals = [0.0] * len(self.vertexBuffer.vertices) # local normal buffers are reset here
                nVector = [self.vertexBuffer.normals[x:x+3]  for x in xrange(0, len(self.vertexBuffer.normals),  3)]
                vVector = [self.vertexBuffer.vertices[x:x+3] for x in xrange(0, len(self.vertexBuffer.vertices), 3)]
            else:
                nVector = [sg.normals[x:x+3]                 for x in xrange(0, len(sg.normals),                 3)]
                vVector = [sg.vertices[x:x+3]                for x in xrange(0, len(sg.vertices),                3)]
            nFaceVector = []

            # First, we loop through faces, and calculate their normals
            # and normalize them while we are at it.
            #
            for f in fVector:
                #print f[0], f[1], f[2]
                #print "%f-%f, %f-%f, %f-%f = %f %f %f" % (vVector[f[1]][0],vVector[f[0]][0], vVector[f[1]][1],vVector[f[0]][1], vVector[f[1]][2],vVector[f[0]][2], vVector[f[1]][0]-vVector[f[0]][0], vVector[f[1]][1]-vVector[f[0]][1], vVector[f[1]][2]-vVector[f[0]][2])
                v1 = [ vVector[f[1]][0]-vVector[f[0]][0], vVector[f[1]][1]-vVector[f[0]][1], vVector[f[1]][2]-vVector[f[0]][2] ]
                v2 = [ vVector[f[2]][0]-vVector[f[0]][0], vVector[f[2]][1]-vVector[f[0]][1], vVector[f[2]][2]-vVector[f[0]][2] ]
                #print vVector[f[0]], vVector[f[1]], vVector[f[2]]
                #print v1, v2
                n = []
                n.append( (v1[1]*v2[2]-v1[2]*v2[1]))
                n.append(-(v1[0]*v2[2]-v1[2]*v2[0]))
                n.append( (v1[0]*v2[1]-v1[1]*v2[0]))
                l = math.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2])
                #if l == 0: n[0] = 0.0; n[1] = 1.0; n[2] = 0.0
                #else:
                n[0] /= l
                n[1] /= l
                n[2] /= l
                #print n
                #print "---"
                nFaceVector.append(n)

            #print nVector
            #print nFaceVector
            #
            for v in range(len(vVector)):                   # Second, loop through vertices, and calculate vertex normals
                indices = []                                # based on neighbour face surface normals. Vertex normal is an average
                fIndex = 0                                  # of its neighboring face surface normals, normalized.
                for f in fVector:                           # ... loop through all faces
                    if v in f: indices.append(fIndex)       # ... if vertex index is among face indices, append to neighbor list
                    fIndex += 1
                #print indices
                if len(indices) == 0: continue              # ... this case indicated a dead vertex
                for i in indices:                           # ... loop through all neighbor faces
                    #print i, fVector[i], nFaceVector[i]
                    nVector[v][0] += nFaceVector[i][0]      # ... calcualte cumulative sum for normal vector
                    nVector[v][1] += nFaceVector[i][1]      # ... and at the same time write it to normal buffer
                    nVector[v][2] += nFaceVector[i][2]
                l = math.sqrt(nVector[v][0]*nVector[v][0] + nVector[v][1]*nVector[v][1] + nVector[v][2]*nVector[v][2])
                nVector[v][0] /= l
                nVector[v][1] /= l
                nVector[v][2] /= l
                #print nVector[v]
                #print "---"

            #                                                ... Copy results into corresponding vertex buffer..
            if sg == None:
                self.vertexBuffer.normals = []
                for normal in nVector:
                    for n in normal: self.vertexBuffer.normals.append(n)
            else:
                sg.normals = []
                for normal in nVector:
                    for n in normal: sg.normals.append(n)
            #print nVector

        def removeDeadFaces(self, sg=None):
            #
            # removeDeadFaces() loops through submesh faces, and looks for faces which have one of following:
            #   - face indices are not unique
            #   - face vertices pointed by the face indices are not unique
            # all matched faces are considered dead, and are removed from the facelist
            #
            print "Submesh: removeDeadFaces()"

            fVector = [self.faces[x:x+3]                     for x in xrange(0, len(self.faces),                 3)]
            if sg == None:
                vVector = [self.vertexBuffer.vertices[x:x+3] for x in xrange(0, len(self.vertexBuffer.vertices), 3)]
            else:
                vVector = [sg.vertices[x:x+3]                for x in xrange(0, len(sg.vertices),                3)]
            newFaceList = []
            #
            # loop through the facelist
            #
            for f in fVector:
                if f[0] == f[1]: continue
                if f[0] == f[2]: continue
                if f[1] == f[2]: continue
                if vVector[f[0]] == vVector[f[1]]: continue
                if vVector[f[0]] == vVector[f[2]]: continue
                if vVector[f[1]] == vVector[f[2]]: continue
                for face in f: newFaceList.append(face)
            print "Dropped %d out of %d faces" % (len(fVector)-len(newFaceList)/3, len(fVector))
            self.faces = newFaceList

        ### Submesh private: ###########################################################################

        def __addUniqueEdge(self, a, b):
            try:
                t = self.temp_d[a]
                if not b in t:
                    self.uniqueEdges.append((a, b))
                    t.append(b)
                    self.temp_d[a] = t
            except KeyError:
                self.temp_d[a] = [b]
            #if (a, b) not in self.uniqueEdges:
            #    self.uniqueEdges.append((a, b))

        def __addUniqueFace(self, f, new_faces):
            for i in range(len(new_faces)/3):
                if self.faces[3*i+0] == f[0] and self.faces[3*i+1] == f[1] and self.faces[3*i+2] == f[2]:
                    return
            new_faces += f

        def __findClosestVertex(self, sg, x, y, z):
            self.__message("Submesh: __findClosestVertex(%f, %f, %f)" % (x, y, z))
            vb = self.vertexBuffer
            if sg != None: vb = sg
            min_distance = 1000000.0
            index        = -1
            counter      = 0
            vVector      = [vb.vertices[_x:_x+3] for _x in xrange(0, len(vb.vertices), 3)]
            for v in vVector:
                distance = (x-v[0])*(x-v[0]) + (y-v[1])*(y-v[1]) + (z-v[2])*(z-v[2])
                if distance < min_distance:
                    min_distance = distance
                    index = counter
                counter += 1
            self.__message("Submesh: Closest vertex at index %d, request: %f %f %f, candidate: %f %f %f, eta: %f" % \
                (index, x, y, z, vVector[index][0], vVector[index][1], vVector[index][2], \
                 math.sqrt((x-vVector[index][0])*(x-vVector[index][0]) + (y-vVector[index][1])*(y-vVector[index][1]) + (z-vVector[index][2])*(z-vVector[index][2]))))
            return index

        def __findSubmeshMinMax(self, sg):
            self.__message("Submesh: __findSubmeshMinMax()")
            vb = self.vertexBuffer
            if sg != None: vb = sg
            self.__message("Looping through %d faces" % len(self.faces))
            for f in self.faces:
                if vb.vertices[3*f+0] < self.min_x: self.min_x = vb.vertices[3*f+0]; self.min_x_index = f
                if vb.vertices[3*f+0] > self.max_x: self.max_x = vb.vertices[3*f+0]; self.max_x_index = f
                if vb.vertices[3*f+1] < self.min_y: self.min_y = vb.vertices[3*f+1]; self.min_y_index = f
                if vb.vertices[3*f+1] > self.max_y: self.max_y = vb.vertices[3*f+1]; self.max_y_index = f
                if vb.vertices[3*f+2] < self.min_z: self.min_z = vb.vertices[3*f+2]; self.min_z_index = f
                if vb.vertices[3*f+2] > self.max_z: self.max_z = vb.vertices[3*f+2]; self.max_z_index = f

        def __debugSubmeshMinMax(self, sg):
            vb = self.vertexBuffer
            if sg != None: vb = sg
            self.__message("Submesh: debugMinMax()")
            self.__message(" x: %d %d y: %d %d z: %d %d" % (self.min_x_index, self.max_x_index, \
                                                            self.min_y_index, self.max_y_index, \
                                                            self.min_z_index, self.max_z_index))
            self.__message(" x: %f %f y: %f %f z: %f %f" % (vb.vertices[3*self.min_x_index+0], vb.vertices[3*self.max_x_index+0], \
                                                            vb.vertices[3*self.min_y_index+1], vb.vertices[3*self.max_y_index+1], \
                                                            vb.vertices[3*self.min_z_index+2], vb.vertices[3*self.max_z_index+2]))

    ##############################################################################
    # Vertex buffer holds positions, normals and texcoords needed for rendering
    #
    class VertexBuffer():
        def __init__(self):
            self.reset()
        def reset(self):
            self.vertices           = []
            self.normals            = []
            self.texcoords          = []    # There is actually up to eight of texcoords banks
            self.texcoords_1        = []    # Only two supported for testing, for now
            self.diffusecolors      = []
            self.diffusecolorDimensions = 3
            self.texcoordDimensions = [2,2] # Default dimensions for the texcoord banks
            self.resetMinMax()
        def resetMinMax(self):
            self.min_x              =  100000.0           # Min, max statistics are updated on the go
            self.max_x              = -100000.0          # when vertices are fed into the buffers
            self.min_y              =  100000.0           # and they are used by 3D voxel texture
            self.max_y              = -100000.0          # calculations
            self.min_z              =  100000.0
            self.max_z              = -100000.0
            self.min_x_index        = -1
            self.max_x_index        = -1
            self.min_y_index        = -1
            self.max_y_index        = -1
            self.min_z_index        = -1
            self.max_z_index        = -1
            self.scaleF             = 0.0
            # Params for edge collapsing
            self.vRefCounts         = None                  # each vertex has a counter how many times
                                                            # it has been referenced from face array
        def __message(self, msg):
            print msg
            return
        def debugMinMax(self):
            return
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
        def setDiffusecolorDimensions(self, c_dim):
            #self.__message("Setting diffusecolor dimension to %d" % c_dim)
            self.diffusecolorDimensions = c_dim;

        ##############################################################################
        # Vertexbuffer content adaptation:
        #   - addVertex()
        #   - addNormal()
        #   - addTexcoord()
        #   - addDiffuseColor()
        #
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
                self.__message("Warning: texcoord dimensions for bank %d do not match expectation. Got %d, expected %d" % (bank, len(t_list), self.texcoordDimensions[bank]))
            if bank == 0:
                for t in t_list: self.texcoords.append(t)
            if bank == 1:
                for t in t_list: self.texcoords_1.append(t)
        def addDiffuseColor(self, c_list):
            colorComponents = c_list.split(" ")
            self.setDiffusecolorDimensions(len(colorComponents))
            for c in colorComponents:
                self.diffusecolors.append(float(c))

        ##############################################################################
        # Vertexbuffer manipulators:
        #   - translate()
        #   - rotate()
        #   - scale()
        #   - merge()
        #
        def translate(self, x, y, z):
            self.__message("VertexBuffer: translate %f %f %f" % (x, y, z))
            for i in range(len(self.vertices)/3):
                self.vertices[i*3+0] += x
                self.vertices[i*3+1] += y
                self.vertices[i*3+2] += z

        def rotate(self, angle, x, y, z):
            self.__message("VertexBuffer: rotate angle %f, %f %f %f" % (angle, x, y, z))
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

        def scale(self, x, y, z):
            self.__message("VertexBuffer: scale %f %f %f" % (x, y, z))
            for i in range(len(self.vertices)/3):
                self.vertices[3*i+0] = x * self.vertices[3*i+0]
                self.vertices[3*i+1] = y * self.vertices[3*i+1]
                self.vertices[3*i+2] = z * self.vertices[3*i+2]

        def merge(self, vertexbuffer):
            self.__message("VertexBuffer: merge")
            for i in vertexbuffer.vertices:
                self.vertices.append(i)
            for i in vertexbuffer.normals:
                self.normals.append(i)
            for i in vertexbuffer.texcoords:
                self.texcoords.append(i)
            for i in vertexbuffer.texcoords_1:
                self.texcoords_1.append(i)
            for i in vertexbuffer.diffusecolors:
                self.diffusecolors.append(i)

        def setupStatistics(self):
            self.__message("VertexBuffer: setupStatistics()")
            if self.vRefCounts == None or len(self.vRefCounts) != len(self.vertices):
                self.vRefCounts = [0] * len(self.vertices)
                #self.__message("Setup a ref array for vertices of size %d" % len(self.vRefCounts))
            #else:
                #self.__message("Vertex ref counts already setup")

        ##############################################################################
        # Experimental. a method to build a 3D texture out from point cloud
        # position and color data.
        #
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
            self.scaleF *= 1.001
            self.create3DTexcoords()
            cubicR = numpy.zeros((size, size, size), dtype=numpy.float32)
            cubicG = numpy.zeros((size, size, size), dtype=numpy.float32)
            cubicB = numpy.zeros((size, size, size), dtype=numpy.float32)
            cubicN = numpy.zeros((size, size, size), dtype=numpy.int32)
            vVector = [self.vertices[x:x+3]      for x in xrange(0, len(self.vertices), 3)]
            cVector = [self.diffusecolors[x:x+self.diffusecolorDimensions] for x in xrange(0, len(self.diffusecolors), self.diffusecolorDimensions)]
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

    ##############################################################################
    # Bone assignments are links between skeleton and mesh structure
    # TODO: bone assignments are not supported yet.
    #
    class BoneAssignments():
        def __init__(self):
            self.vertexBoneAssignments = []
        def addVertexBoneAssignment(self, b_list):
            for i in b_list: self.vertexBoneAssignments.append(i)

    ##############################################################################
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
        #
        self.edgeStatisticsCalculated = False

    ##############################################################################
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
        #if self.sharedgeometry != None:                     # increase vertex refs, once feeding the face indices
        #    self.sharedgeometry.addVertexReferences(f_list)
        #else:
        #    self.submeshes[-1].addVertexReferences(f_list)
    def addVertexBoneAssignment(self, b_list):
        try: self.submeshes[-1].addBoneAssignment(b_list)
        except IndexError: pass
    def addSkeletonLink(self):
        pass
    def addSubmeshName(self, name, index):
        try: self.submeshes[int(index)].addName(name)
        except IndexError: pass
    def setTexcoordDimensions(self, t_index, t_dim):
        self.currentEntity.setTexcoordDimensions(t_index, t_dim)
    def setMaterial(self, materialref):
        self.currentEntity.setMaterial(materialref)

    ##############################################################################
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

    ##############################################################################
    # MeshContainer: Manipulators
    # - translate()
    # - rotate()
    # - scale()
    # - merge()
    # - buildAABBMesh()
    # - edgeCollapse()
    # - toSharedgeometry()
    # - collapseSimilars()
    # - recalculateNormals()
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

    def scale(self, x, y, z):
        self.__message("Meshcontainer: scale factor %f %f %f" % (x, y, z))
        for s in self.submeshes:
            s.scale(x, y, z)
        if self.sharedgeometry != None:
            self.sharedgeometry.scale(x, y, z)

    def merge(self, meshcontainer, append=False):
        """ merge() is a destructive merge operation of two meshcontainers. Target
            meshcontainer (self) is merged with the data in the source meshcontainer.
            Note: This method only merges the data, and creates new submeshes on
            the fly, if needed. It also treats the sharedgeometry, if one is defined.
            However, it does not check for vertex duplicates.
        """
        self.__message("Meshcontainer: merge")
        #
        # Merge is refused, if meshcontainers are mixing shared and non-sharedgeometry
        #
        if (self.sharedgeometry == None and meshcontainer.sharedgeometry != None) or \
           (self.sharedgeometry != None and meshcontainer.sharedgeometry == None):
            self.__message("Meshcontainer: Error merging meshes which mismatch sharedgeometry")
            return -1

        shared_vertices = -1
        if self.sharedgeometry != None:
            shared_vertices = len(self.sharedgeometry.vertices)/3
        #
        # First submesh array merge ...
        #
        if append == False:
            for i in range( max(len(self.submeshes), len(meshcontainer.submeshes)) ):
                try: sm1 = self.submeshes[i]
                except IndexError:
                    self.newSubmesh()
                    sm1 = self.submeshes[i]
                try: sm2 = meshcontainer.submeshes[i]
                except IndexError:
                    break
                sm1.merge(sm2, shared_vertices)
                if shared_vertices != -1:
                    shared_vertices += len(sm2.vertexBuffer.vertices)/3

        elif append == True:
            for i in range(len(meshcontainer.submeshes)):
                self.newSubmesh(meshcontainer.submeshes[i].materialref)
                sm1 = self.submeshes[-1]            # meshcontainer submeshes always go to the end of the list
                sm2 = meshcontainer.submeshes[i]
                sm1.merge(sm2, shared_vertices)     # Merge agaist empty submesh in the end of the list == append
                if shared_vertices != -1:
                    shared_vertices += len(sm2.vertexBuffer.vertices)/3
        #
        # ... and then shared geometry, if any
        #
        if meshcontainer.sharedgeometry != None:
            self.sharedgeometry.merge(meshcontainer.sharedgeometry)

    def replaceGeometry(self, meshcontainer):
        self.__message("MeshContainer: replaceGeometry")
        if self.sharedGeometry != None:
            self.sharedGeometry.replaceGeometry(meshcontainer.sharedGeometry)
        for i in range(len(meshcontainer.submeshes)):
            m.replaceGeometry(self.submeshes[i], meshcontainer.submeshesi[i])

    def buildAABBMesh(self):
        self.__message("MeshContainer: buildAABBMesh")
        mesh2 = MeshContainer()
        for m in self.submeshes:
            mesh2.newSubmesh()
            m.buildAABBMesh(mesh2, self.sharedgeometry)
        # Make a replacement
        self.submeshes      = mesh2.submeshes
        self.sharedgeometry = mesh2.sharedgeometry
        self.submeshnames   = mesh2.submeshnames
        self.skeletonlinks  = mesh2.skeletonlinks
        self.currentEntity  = mesh2.currentEntity
        #mesh2.printStatistics()

    def edgeCollapse(self, percentage=0.50, amount=None):
        self.__message("MeshContainer: edgeCollapse(percentage=%f, amount=%s)" % (percentage, str(amount)))
        # First, if there is no statistical analysis for the current mesh
        # we need to build one
        for m in self.submeshes:
            m.prepareCollapse(self.sharedgeometry)
        # Loop through all submeshes (and collect search-replace dict)
        #d = {}
        #for m in self.submeshes:
        #    m.collapseEdges(self.sharedgeometry, percentage, amount, d)

        if self.sharedgeometry != None:
            n_vert = []
            n_norm = []
            n_tex1 = []
            n_tex2 = []
            n_diff = []
            rdict  = {}
            offset = 0
            d = {}
            for m in self.submeshes:
                m.collapseEdges(self.sharedgeometry, percentage, amount, d)
            for m in self.submeshes:
                offset = m.collapseVertexbuffer(self.sharedgeometry, offset, rdict, n_vert, n_norm, n_tex1, n_tex2, n_diff)
            self.sharedgeometry.vertices      = n_vert
            self.sharedgeometry.normals       = n_norm
            self.sharedgeometry.texcoords     = n_tex1
            self.sharedgeometry.texcoords_1   = n_tex2
            self.sharedgeometry.diffusecolors = n_diff
        else:
            for m in self.submeshes:
                m.collapseEdges(None, percentage, amount, {})
                m.collapseVertexbuffer(None, 0, {}, [], [], [], [], [])

    def toSharedgeometry(self): # This method transforms a mesh into sharedgeometry structure, if it is not already
        self.__message("MeshContainer: toSharedgeometry()")
        if self.sharedgeometry != None:
            return # If this container is already based on SG, do nothing then
        self.sharedgeometry = MeshContainer.VertexBuffer()
        self.currentEntity = self.sharedgeometry
        faceOffset = 0
        for m in self.submeshes:
            self.sharedgeometry.merge(m.vertexBuffer)
            for i in range(len(m.faces)):
                m.faces[i] += faceOffset;
            faceOffset += len(m.vertexBuffer.vertices)/3
            m.vertexBuffer.reset()

    def collapseSimilars(self): # This method collapses all submeshesh into one, which share the same materialref
        self.__message("MeshContainer: collapseSimilars()")
        try:
            for i in range(len(self.submeshes)):
                temp = self.submeshes[i] # Trigger an artificial IndexError, if vector has already run out due to collapsing
                deleteList = []
                for j in range(i+1, len(self.submeshes)):
                    if self.submeshes[i].materialref == self.submeshes[j].materialref:
                        #self.__message("Collapsing submesh %d into %d, materialref = %s" % (j, i,  self.submeshes[i].materialref))
                        self.submeshes[i].merge(self.submeshes[j])
                        deleteList.append(j)
                deleteList.reverse()
                for d in deleteList: del self.submeshes[d]
        except IndexError:
            #self.__message("Done collapsing")
            pass

    #
    # This method discards the current normals stored in the mesh, and recalculates them all based on
    # neighboring face surface vertices
    #
    def recalculateNormals(self):
        self.__message("Meshcontainer: recalculateNormals()")
        if self.sharedgeometry != None:
            # if this is a mesh with shared geometry, the normal array needs to be
            # initialized at this point. the calculator itself will replace the zero
            # placeholders then when ascending the vertex array
            self.sharedgeometry.normals = [0.0] * len(self.sharedgeometry.vertices)
        # loop through all submeshes
        for s in self.submeshes:
            s.recalculateNormals(self.sharedgeometry)
        #if self.sharedgeometry != None: print self.sharedgeometry.normals
        #else: print self.submeshes[0].vertexBuffer.normals

    #
    # This method removes all dead (zero sized, orphan etc) faces from the mesh
    #
    def removeDeadFaces(self):
        self.__message("Meshcontainer: removeDeadFaces()")
        for s in self.submeshes:
            s.removeDeadFaces(self.sharedgeometry)

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
            try: self.__message("   Vertices=%d" % (len(m.vertexBuffer.vertices)/3))
            except IndexError: pass
            try: self.__message("   Faces=%d" % (len(m.faces)/3))
            except IndexError: pass
            try: self.__message("   Normals=%d" % (len(m.vertexBuffer.normals)/3))
            except IndexError: pass
            try: self.__message("   Diffuse colors=%d" % (len(m.vertexBuffer.diffusecolors)/m.vertexBuffer.diffusecolorDimensions))
            except IndexError: pass
            try: self.__message("   Texcoords 0 bank=%d, dimensions=%d" % (len(m.vertexBuffer.texcoords)/m.vertexBuffer.texcoordDimensions[0], m.vertexBuffer.texcoordDimensions[0]))
            except IndexError: pass
            try: self.__message("   Texcoords 1 bank=%d, dimensions=%d" % (len(m.vertexBuffer.texcoords_1)/m.vertexBuffer.texcoordDimensions[1], m.vertexBuffer.texcoordDimensions[1]))
            except IndexError: pass
            index += 1

###############################################################################
# Unit test case
#

if __name__ == "__main__":
    import getopt
    import MeshGenerator
    import MeshIO

    # Load all template meshes
    baseMesh = MeshContainer()
    meshIO = MeshIO.MeshIO(baseMesh)
    birchMesh = MeshContainer()
    meshIO_birch = MeshIO.MeshIO(birchMesh)
    meshIO_birch.fromFile("../TundraWorldGenerator/Applications/syote/resources/birch.mesh.xml", "model/x-ogremesh")
    pineMesh = MeshContainer()
    meshIO_pine = MeshIO.MeshIO(pineMesh)
    meshIO_pine.fromFile("../TundraWorldGenerator/Applications/syote/resources/pine.mesh.xml", "model/x-ogremesh")
    spruceMesh = MeshContainer()
    meshIO_spruce = MeshIO.MeshIO(spruceMesh)
    meshIO_spruce.fromFile("../TundraWorldGenerator/Applications/syote/resources/spruce.mesh.xml", "model/x-ogremesh")
    # Transform all into sharedgeometry models
    baseMesh.toSharedgeometry()
    birchMesh.toSharedgeometry()
    pineMesh.toSharedgeometry()
    spruceMesh.toSharedgeometry()
    # spill meshes all over the baseMesh
    for i in range(10):
        baseMesh.merge(birchMesh, append=True)
        baseMesh.merge(pineMesh, append=True)
        baseMesh.merge(spruceMesh, append=True)
    print "Mesh structure before:"
    baseMesh.printStatistics()
    baseMesh.collapseSimilars()
    print "Mesh structure after:"
    baseMesh.printStatistics()
    meshIO.toFile("testmesh.mesh.xml", overwrite=True)
    sys.exit(0)

    mesh = MeshContainer()
    m = MeshGenerator.MeshGenerator(mesh, sharedgeometry=True)
    m.createPlane(LOD=2)
    mesh2 = MeshContainer()
    m2 = MeshGenerator.MeshGenerator(mesh2, sharedgeometry=True)
    m2.createPlane(LOD=2)
    mesh2.translate(10, 0, 0)
    mesh.merge(mesh2, append=True)
    meshio = MeshIO.MeshIO(mesh)
    meshio.toFile("./plane.mesh.xml", overwrite=True)

    #mesh.scale(5, 5, 5)
    #mesh.translate(2.5, 0, 0)
    #mesh.printStatistics()
    mesh.edgeCollapse(amount=8)

    meshio = MeshIO.MeshIO(mesh)
    meshio.toFile("./mangledmesh.mesh.xml", overwrite=True)
