#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os
import xml.sax

#############################################################################
# MeshContainer class, and its sub/friend classes
#

####
# Submesh holds all ogre mesh data related to OgreSubmesh class

class SubMesh():
    def __init__(self):
        self.vertexBuffer = VertexBuffer()
        self.faces = []
        self.boneAssignments = BoneAssignments()
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
# Bone assignments are links between skeleton and mesh structure
# TODO: bone assignments are not supported yet.

class BoneAssignments():
    def __init__(self):
        self.vertexBoneAssignments = []
    def addVertexBoneAssignment(self, b_list):
        for i in b_list: self.vertexBoneAssignments.append(i)

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
        for c in c_list: self.diffusecolors.append(c)

####
# Vertex buffer holds positions, normals and texcoords needed for rendering
#

class MeshContainer():
    def __init__(self):
        self.submeshes = []
        self.sharedgeometry = None
        self.submeshnames = []
        self.skeletonlinks = None
        # State variables, either shared vertex buffer or submesh
        self.currententity = None

    def fromFile(self, localfile, mimetype):
        if mimetype == "model/mesh" or localfile.endswith(".mesh"):
            ml = OgreMeshImport(self)
            ml.fromFile(localfile)
        elif mimetype == "model/x-ogremesh" or localfile.endswith(".xml"):
            ml = OgreXMLImport(self)
            ml.fromFile(localfile)
        elif mimetype == "model/vtk" or localfile.endswith(".vtk"):
            ml = VTKMeshImport(self)
            ml.fromFile(localfile)
        else:
            print "Unknown mimetype %s" % item.mimetype

    def toFile(self, localfile, overwrite=False):
        if os.path.exists(localfile):
            if overwrite == False:
                print "Output file %s already exists, abort" % localfile
                return
            try: os.unlink(localfile)
            except IOError:
                print "Cannot overwrite file %s. Abort!" % localfile
                return
        if localfile.endswith(".xml"):
            ml = OgreXMLImport(self)
            ml.toFile(localfile)
        elif localfile.endswith(".vtk"):
            ml = VTKMeshImport(self)
            ml.toFile(localfile)
        elif localfile.endswith(".mesh"):
            ml = OgreMeshImport(self)
            ml.toFile(localfile)

    #####
    # MeshContainer: Data attribute additions
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
    # MeshContainer: New container instances
    #
    def newSubmesh(self):
        sm = SubMesh()
        self.submeshes.append(sm)
        self.currententity = sm
    def newSharedGeometry(self):
        self.sharedgeometry = VertexBuffer()
        self.currententity = self.sharedgeometry
    def newSubmeshName(self, name):
        self.submeshname.append(name)
    def newSkeletonLink(self):
        pass
    def newBoneAssignment(self):
        pass

    #####
    # MeshContainer: Statistics for debug
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

#############################################################################
# OgreXMLImport class
#

class OgreXMLImport():
    """ OgreXMLImport() is able to eat Ogre XML input and fill in the provided
        MeshContainer class for further use.
    """
    def __init__(self, meshcontainer):
        self.meshcontainer = meshcontainer

    ###
    # OgreXMLImport: I/O
    #
    def fromFile(self, localfile):
        p = xml.sax.make_parser()
        ogreparser = OgreXMLImport.XMLParser()
        ogreparser.setMeshContainer(self.meshcontainer)
        p.setContentHandler(ogreparser)
        p.parse(localfile)

    def toFile(self, localfile, overwrite=False):
        mesh = self.OgreXMLExport(localfile, overwrite)
        mesh.startMesh()
        if self.meshcontainer.sharedgeometry != None:
            print "Fixme, sharedvertice export TBD"
            pass                            # Todo: add sharedgeometry suppot
        if len(self.meshcontainer.submeshes) > 0:
            mesh.startSubmeshes()
            for m in self.meshcontainer.submeshes:
                longIndices = False
                if len(m.vertexBuffer.vertices) > 32765: longIndices = True
                mesh.startSubmesh("", False, longIndices, "triangle_list")

                mesh.startFaces(len(m.faces)/3)
                for i in [m.faces[x:x+3] for x in xrange(0, len(m.faces), 3)]:
                    mesh.outputFace(i[0], i[1], i[2])
                mesh.endFaces()

                mesh.startGeometry(len(m.vertexBuffer.vertices)/3)
                vVector = [m.vertexBuffer.vertices[x:x+3]  for x in xrange(0, len(m.vertexBuffer.vertices), 3)]
                nVector = [m.vertexBuffer.normals[x:x+3]   for x in xrange(0, len(m.vertexBuffer.normals), 3)]
                tVector = [m.vertexBuffer.texcoords[x:x+2] for x in xrange(0, len(m.vertexBuffer.texcoords), 2)]
                cVector = [m.vertexBuffer.diffusecolors[x:x+3]    for x in xrange(0, len(m.vertexBuffer.diffusecolors), 3)]
                mesh.startVertexbuffer((len(vVector) != 0), (len(nVector) != 0), (len(tVector) != 0), (len(cVector) != 0))

                counter = 0
                while counter < len(m.vertexBuffer.vertices)/3:
                    mesh.startVertex()
                    mesh.outputPosition(vVector[counter][0], vVector[counter][1], vVector[counter][2])
                    if len(nVector) > 0:
                        mesh.outputNormal(nVector[counter][0], nVector[counter][1], nVector[counter][2])
                    if len(nVector) > 0:
                        mesh.outputTexcoord(tVector[counter][0], tVector[counter][1])
                    if len(cVector) > 0:
                        mesh.outputDiffuseColor(cVector[counter][0], cVector[counter][1], cVector[counter][2])
                    mesh.endVertex()
                    counter += 1

                mesh.endVertexbuffer()
                mesh.endGeometry()
                mesh.endSubmesh()
            mesh.endSubmeshes()
        mesh.endMesh()
        mesh.closeOutputXML()

    ###
    # OgreXMLImport: tools
    #
    def printStatistics(self):
        self.meshcontainer.printStatistics()

    ###
    # OgreXMLImport: XMLParser: XML parser class for OgreXML fileformat:
    #
    class XMLParser(xml.sax.ContentHandler):
        def setMeshContainer(self, container):
            self.mc = container

        ###
        # Start element methods:
        #
        def __start_mesh(self, attributes):
            pass
        def __start_submeshes(self, attributes):
            pass
        def __start_submesh(self, attributes):
            self.mc.newSubmesh()
        def __start_sharedgeometry(self, attributes):
            self.mc.newSharedGeometry()
        def __start_faces(self, attributes):
            pass
        def __start_face(self, attributes):
            self.mc.addFace([attributes.getValueByQName("v1"),
                             attributes.getValueByQName("v2"),
                             attributes.getValueByQName("v3")])
        def __start_geometry(self, attributes):
            pass
        def __start_vertexbuffer(self, attributes):
            pass
        def __start_position(self, attributes):
            self.mc.addVertex([attributes.getValueByQName("x"),
                               attributes.getValueByQName("y"),
                               attributes.getValueByQName("z")])
        def __start_normal(self, attributes):
            self.mc.addNormal([attributes.getValueByQName("x"),
                               attributes.getValueByQName("y"),
                               attributes.getValueByQName("z")])
        def __start_texcoord(self, attributes):
            self.mc.addTexcoord([attributes.getValueByQName("u"),
                                 attributes.getValueByQName("v")])
        def __start_diffusecolor(self, attributes):
            self.mc.addDiffuseColor(attributes.getValueByQName("value"))
        def __start_boneassignments(self, attributes):
            self.mc.newBoneAssignments()
        def __start_vertexboneassignment(self, attributes):
            self.mc.addVertexBoneAssignment([])
        def __start_skeletonlink(self, attributes):
            self.mc.addSkeletonLink()
        def __start_submeshnames(self, attributes):
            pass
        def __start_submeshname(self, attributes):
            self.mc.addSubmeshName(attributes.getValueByQName("name"),
                                   attributes.getValueByQName("index"))

        ###
        # End element methods:
        #
        def __end_mesh(self):
            pass
        def __end_submeshes(self):
            pass
        def __end_submesh(self):
            pass
        def __end_sharedgeometry(self):
            pass
        def __end_faces(self):
            pass
        def __end_face(self):
            pass
        def __end_geometry(self):
            pass
        def __end_vertexbuffer(self):
            pass
        def __end_position(self):
            pass
        def __end_normal(self):
            pass
        def __end_texcoord(self):
            pass
        def __end_diffusecolor(self):
            pass
        def __end_boneassignments(self):
            pass
        def __end_vertexboneassignment(self):
            pass
        def __end_skeletonlink(self):
            pass
        def __end_submeshnames(self):
            pass
        def __end_submeshname(self):
            pass

        def startElement(self, tag, attributes):
            if tag == "mesh":                 return self.__start_mesh(attributes)
            if tag == "submeshes":            return self.__start_submeshes(attributes)
            if tag == "submesh":              return self.__start_submesh(attributes)
            if tag == "sharedgeometry":       return self.__start_sharedgeometry(attributes)
            if tag == "faces":                return self.__start_faces(attributes)
            if tag == "face":                 return self.__start_face(attributes)
            if tag == "geometry":             return self.__start_geometry(attributes)
            if tag == "vertexbuffer":         return self.__start_vertexbuffer(attributes)
            if tag == "position":             return self.__start_position(attributes)
            if tag == "normal":               return self.__start_normal(attributes)
            if tag == "texcoord":             return self.__start_texcoord(attributes)
            if tag == "colour_diffuse":       return self.__start_diffusecolor(attributes)
            if tag == "boneassignmenst":      return self.__start_boneassignments(attributes)
            if tag == "vertexboneassignment": return self.__start_vertexboneassignment(attributes)
            if tag == "skeletonlink":         return self.__start_skeletonlink(attributes)
            if tag == "submeshnames":         return self.__start_submeshnames(attributes)
            if tag == "submeshname":          return self.__start_submeshname(attributes)

        def endElement(self, tag):
            if tag == "mesh":                 return self.__end_mesh()
            if tag == "submeshes":            return self.__end_submeshes()
            if tag == "submesh":              return self.__end_submesh()
            if tag == "sharedgeometry":       return self.__end_sharedgeometry()
            if tag == "faces":                return self.__end_faces()
            if tag == "face":                 return self.__end_face()
            if tag == "geometry":             return self.__end_geometry()
            if tag == "vertexbuffer":         return self.__end_vertexbuffer()
            if tag == "position":             return self.__end_position()
            if tag == "normal":               return self.__end_normal()
            if tag == "texcoord":             return self.__end_texcoord()
            if tag == "colour_diffuse":       return self.__end_diffusecolor()
            if tag == "boneassignmenst":      return self.__end_boneassignments()
            if tag == "vertexboneassignment": return self.__end_vertexboneassignment()
            if tag == "skeletonlink":         return self.__end_skeletonlink()
            if tag == "submeshnames":         return self.__end_submeshnames()
            if tag == "submeshname":          return self.__end_submeshname()

    ###
    # OgreXMLImport: OgreXMLExport: Ogre XML output class:
    #
    class OgreXMLExport():
        """ class OgreXMLExport(): I/O component for writing formatted OgreXML notation
            - Primarily used by MeshGenerator for producing Ogre compliant XML mesh
              notation.
            - All XML requests are pushed into buffer, and once toFile method is called
              the contents are flushes to the desired output file.
        """
        def __init__(self, localfile=None, overwrite=False):
            self.indent = 0
            self.outputXMLFile = None
            self.openOutputXML(localfile, overwrite)

        #############################################################################
        # OgreXMLExport: File I/O and internals
        #
        def openOutputXML(self, localfile, overwrite):
            if os.path.exists(localfile):
                if overwrite == False:
                    print ("OgreXMLExport: ERROR: output file '%s' already exists!\n" % filename)
                    return
                else:
                    os.unlink(localfile)
            try: self.outputXMLFile = open(localfile, "w")
            except IOError:
                print ("OgreXMLExport: ERROR: Unable to open file '%s' for writing!" % filename)
                self.outputXMLFile = None

        def closeOutputXML(self):
            self.outputXMLFile.close()
            self.outputXMLFile = None

        def __outputXML(self, msg):
            if self.outputXMLFile == None:
                return
            indent_str = ""
            for i in range(self.indent):
                indent_str = indent_str + " "
            self.outputXMLFile.write((indent_str + str(msg) + "\n"))

        def __increaseIndent(self):
            self.indent += 1

        def __decreaseIndent(self):
            if self.indent > 0: self.indent -= 1

        #############################################################################
        # OgreXMLExport: Ogre XML output methods
        #
        def startMesh(self):
            self.__outputXML("<mesh>")
            self.__increaseIndent()

        def endMesh(self):
            self.__decreaseIndent()
            self.__outputXML("</mesh>")

        def startVertexbuffer(self, position=True, normal=True, texcoord=True, diffusecolor=False, tex_dimensions=2):
            s_out = ""
            if normal == True:   s_out += "normals=\"true\" "
            if position == True: s_out += "positions=\"true\" "
            if texcoord == True:
                s_out += "texture_coords=\"true\""
                s_out += "tex_coord_dimensions=\"%d\"" % tex_dimensions
            if diffusecolor == True:
                s_out += "colours_diffuse=\"true\""
            self.__outputXML("<vertexbuffer %s>" % s_out)
            self.__increaseIndent()

        def endVertexbuffer(self):
            self.__decreaseIndent()
            self.__outputXML("</vertexbuffer>")

        def startSharedgeometry(self, vertices):
            self.__outputXML("<sharedgeometry vertexcount=\"" + str(vertices) + "\">")
            self.__increaseIndent()

        def endSharedgeometry(self):
            self.__decreaseIndent()
            self.__outputXML("</sharedgeometry>")

        def startVertex(self):
            self.__outputXML("<vertex>")
            self.__increaseIndent()

        def endVertex(self):
            self.__decreaseIndent()
            self.__outputXML("</vertex>")

        def startSubmeshes(self):
            self.__outputXML("<submeshes>")
            self.__increaseIndent()

        def endSubmeshes(self):
            self.__decreaseIndent()
            self.__outputXML("</submeshes>")

        def startSubmesh(self, material, sharedvertices, longindices, operationtype):
            s_out = "material=\"%s\" " % material
            s_out += "usesharedvertices=\"%s\" " % sharedvertices
            s_out += "use32bitindexes=\"%s\" " % longindices
            s_out += "operationtype=\"%s\"" % operationtype
            self.__outputXML("<submesh %s>" % s_out)
            self.__increaseIndent()

        def endSubmesh(self):
            self.__decreaseIndent()
            self.__outputXML("</submesh>")

        def startFaces(self, faces):
            self.__outputXML("<faces count=\""+str(faces)+"\">")
            self.__increaseIndent()

        def endFaces(self):
            self.__decreaseIndent()
            self.__outputXML("</faces>")

        def startGeometry(self, vertices):
            self.__outputXML("<geometry count=\""+str(vertices)+"\">")
            self.__increaseIndent()

        def endGeometry(self):
            self.__decreaseIndent()
            self.__outputXML("</geometry>")

        def outputPosition(self, x, y, z):
            self.__outputXML("<position x=\""+str(x)+"\" y=\""+str(y)+"\" z=\""+str(z)+"\"/>")

        def outputNormal(self, x, y, z):
            self.__outputXML("<normal x=\""+str(x)+"\" y=\""+str(y)+"\" z=\""+str(z)+"\"/>")

        def outputTexcoord(self, u, v):
            self.__outputXML("<texcoord u=\""+str(u)+"\" v=\""+str(v)+"\"/>")

        def outputFace(self, v1, v2, v3):
            self.__outputXML("<face v1=\""+str(v1)+"\" v2=\""+str(v2)+"\" v3=\""+str(v3)+"\"/>")

        def outputDiffuseColor(self, r, g, b):
            self.__outputXML("<colour_diffuse value=\"%f %f %f\" />" % (r, g, b))

#############################################################################
# OgreMeshImport class - for importing binary ogre meshes
#

class OgreMeshImport():
    """ OgreMeshImport() is able to eat binary Ogre mesh input and fill in the provided
        MeshContainer class for further use.
        OgreMeshImport wraps the binary through OgreXMLConverter. If such tool does
        not exist in the system path, the class will fail with IOError
        - This is a harsh hack to handle binary meshes, but it will be sufficient since
          using of the binary meshes is not the priority for this tool.
        - Binary exporter will not be written.
    """
    def __init__(self, meshcontainer):
        self.meshcontainer = meshcontainer

    ###
    # OgreMeshImport I/O
    #
    def fromFile(self, localfile):
        import subprocess
        rc = subprocess.call(["OgreXMLConverter", "-q", localfile, "/tmp/tempogremesh.mesh.xml"])
        if rc != 0: raise IOError
        ml = OgreXMLImport(self.meshcontainer)
        ml.fromFile("/tmp/tempogremesh.mesh.xml")

    def toFile(self, localfile):
        print "Exporting of binary Ogre mesh not supported"

    ###
    # OgreMeshImport stats, for debugging
    #
    def printStatistics(self):
        self.meshcontainer.printStatistics()

#############################################################################
# VTKMeshImport class - for importing VTK point clouds
#

class VTKMeshImport():
    """ VTKMeshImport() is able to eat ASCII VTK fileformat, which contains point cloud
        data and index offsets into polygons.
    """
    def __init__(self, meshcontainer):
        self.meshcontainer = meshcontainer

    ###
    # OgreMeshImport I/O
    #
    def fromFile(self, localfile):
        """ Import from the .vtk file. exceptions are passed through and expected to be caught
            elsewhere.
        """
        f = open(localfile)
        while True:
            line = f.readline()
            if line.find("POINTS") != -1:
                self.meshcontainer.newSubmesh()
                nPoints = int(line.split()[1])
                for index in range(nPoints):
                    vector = f.readline().split(" ")
                    self.meshcontainer.addVertex([float(vector[0]), float(vector[1]), float(vector[2])])
                #print "%d vertices read" % nPoints
            if line.find("POLYGONS") != -1:
                nPolygons = int(line.split()[1])
                for index in range(nPolygons):
                    vector = f.readline().split(" ")
                    self.meshcontainer.addFace([int(vector[1]), int(vector[2]), int(vector[3])])
                #print "%d vertices read" % nPoints
            if line.find("COLOR_SCALARS") != -1:
                # at this point we already know nPoints
                #nPolygons = int(line.split()[1])
                for index in range(nPoints):
                    vector = f.readline().split(" ")
                    self.meshcontainer.addDiffuseColor([float(vector[0]), float(vector[1]), float(vector[2])])
                print "%d colours read" % nPoints

            if line == "": break
            #print line.strip()

    def toFile(self, localfile):
        print "Exporting of VTK ASCII fileformat is not supported"

    ###
    # VTKMeshImport stats, for debugging
    #
    def printStatistics(self):
        self.meshcontainer.printStatistics()

###############################################################################
# Unit test case
# - the test case implements input from any supported mesh container and
#

if __name__ == "__main__":
    import getopt

    def usage():
        print "OgreMeshImport -i <input> [-o <outputfile>]"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:",
            ["input=", "output="])
    except getopt.GetoptError, err:
        usage()
        sys.exit(0)

    input = None
    output = None
    for o, a in opts:
        if o in ("-i", "--input"):
            input = str(a)
        if o in ("-o", "--output"):
            output = str(a)

    if input == None:
        print "No input given. Abort!"
        usage()
        sys.exit(0)

    try:
        mesh = MeshContainer()
        mesh.fromFile(input, None)
        mesh.printStatistics()
        if output != None:
            mesh.toFile(output, overwrite=True)
    except IOError:
        print "Error parsing the input file!"
    except OSError:
        print "OSError, check OgreXMLConverter"
