#!/usr/bin/python

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
    def addVertex(self, v_list):
        for v in v_list: self.vertices.append(v)
    def addNormal(self, n_list):
        for n in n_list: self.normals.append(n)
    def addTexcoord(self, t_list):
        for t in t_list: self.texcoords.append(t)

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
            print "  Vertices=%d, faces=%d, normal=%d texcoords=%d" % (len(m.vertexBuffer.vertices)/3,
                                                                       len(m.faces)/3,
                                                                       len(m.vertexBuffer.normals)/3,
                                                                       len(m.vertexBuffer.texcoords)/2)

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

    def toFile(self, localfile):
        f = open(localfile, "w")            # at this point, no exception checking. We'll let them to passthrough
        f.write("<mesh>\n")
        if self.meshcontainer.sharedgeometry != None:
            print "Fixme, sharedvertice export TBD"
            pass                            # Todo: add sharedgeometry suppot
        if len(self.meshcontainer.submeshes) > 0:
            f.write("<submeshes>\n")
            for mesh in self.meshcontainer.submeshes:
                longIndices = False
                if len(mesh.vertexBuffer.vertices) > 32765: longIndices = True
                f.write("<submesh material=\"%s\" usesharedvertices=\"%s\" use32bitindices=\"%s\" operation_type=\"%s\">\n" %
                        ("", False, longIndices, "triangle_list"))

                f.write("<faces count=\"%d\">\n" % (len(mesh.faces)/3))
                for i in [mesh.faces[x:x+3] for x in xrange(0, len(mesh.faces), 3)]:
                    f.write("<face v1=\"%d\" v2=\"%d\" v3=\"%d\"/>\n" % (i[0], i[1], i[2]))
                f.write("</faces>\n");

                f.write("<geometry vertexcount=\"%d\">\n" % (len(mesh.vertexBuffer.vertices)/3))
                vVector = [mesh.vertexBuffer.vertices[x:x+3] for x in xrange(0, len(mesh.vertexBuffer.vertices), 3)]
                nVector = [mesh.vertexBuffer.normals[x:x+3] for x in xrange(0, len(mesh.vertexBuffer.normals), 3)]
                tVector = [mesh.vertexBuffer.texcoords[x:x+2] for x in xrange(0, len(mesh.vertexBuffer.texcoords), 2)]
                f.write("<vertexbuffer positions=\"%s\" normals=\"%s\" texture_coords=\"%d\" texture_coord_dimensions=\"2\">\n" %
                        ((len(vVector) != 0), (len(nVector) != 0), (len(tVector) != 0)))

                counter = 0
                while counter < len(mesh.vertexBuffer.vertices)/3:
                    f.write("<vertex>\n")
                    f.write("<position x=\"%f\" y=\"%f\" z=\"%f\"/>\n"  % (vVector[counter][0], vVector[counter][1], vVector[counter][2]))
                    if len(nVector) > 0:
                        f.write("<normal x=\"%f\" y=\"%f\" z=\"%f\"/>\n"    % (nVector[counter][0], nVector[counter][1], nVector[counter][2]))
                    if len(nVector) > 0:
                        f.write("<texcoord u=\"%f\" v=\"%f\"/>\n"           % (tVector[counter][0], tVector[counter][1]))
                    f.write("</vertex>\n")
                    counter += 1

                f.write("</vertexbuffer>\n")
                f.write("</geometry>\n")
                f.write("</submesh>\n")
            f.write("</submeshes>\n")
        f.write("</mesh>\n")
        f.close()

    ###
    # OgreXMLImport: tools
    #
    def printStatistics(self):
        self.meshcontainer.printStatistics()

    ###
    # OgreXMLImport: XML parser class for OgreXML fileformat:
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
            if tag == "boneassignmenst":      return self.__end_boneassignments()
            if tag == "vertexboneassignment": return self.__end_vertexboneassignment()
            if tag == "skeletonlink":         return self.__end_skeletonlink()
            if tag == "submeshnames":         return self.__end_submeshnames()
            if tag == "submeshname":          return self.__end_submeshname()

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
