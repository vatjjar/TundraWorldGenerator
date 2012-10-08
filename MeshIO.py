#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os
import xml.sax
import MeshContainer

#############################################################################
# Mesh IO classes for manipulation for inport, export of the mesh data
# All classes defined in this file work through the MeshContainer class.
#
# Implemented classes:
#  - MeshIO                 - Helper wrapper for basic IO functionality
#  - OgreXMLImport          - Private class for Ogre XML importing
#  - OgreXMLExport          - Private class for Ogre XML exporting
#  - OgreMeshImport         - Private class for Ogre binary mesh import
#  - VTKImport              - Private class for VTK ASCII mesh import
#

class MeshIO():
    def __init__(self, meshcontainer):
        self.meshcontainer = meshcontainer
        pass

    def fromFile(self, localfile, mimetype):
        if mimetype == "model/mesh" or localfile.endswith(".mesh"):
            ml = OgreMeshImport(self.meshcontainer)
            ml.fromFile(localfile)
        elif mimetype == "model/x-ogremesh" or localfile.endswith(".xml"):
            ml = OgreXMLImport(self.meshcontainer)
            ml.fromFile(localfile)
        elif mimetype == "model/vtk" or localfile.endswith(".vtk"):
            ml = VTKMeshImport(self.meshcontainer)
            ml.fromFile(localfile)
        else:
            print "Unknown mimetype %s. Import Aborted!" % item.mimetype

    def toFile(self, localfile, overwrite=False, positions=True, normals=True, texcoords0=True, texcoords1=True, diffusecolors=True):
        if os.path.exists(localfile):
            if overwrite == False:
                print "Output file %s already exists, abort" % localfile
                return
            try: os.unlink(localfile)
            except IOError:
                print "Cannot overwrite file %s. Abort!" % localfile
                return
        if localfile.endswith(".xml"):
            ml = OgreXMLExport(self.meshcontainer, localfile, overwrite)
            ml.toFile(localfile, positions=positions, normals=normals, texcoords0=texcoords0, texcoords1=texcoords1, diffusecolors=diffusecolors)
        else:
            print "Unknown file ending '%s'. Abort!" % localfile[-4:]

    def build3DTextures(self, prefix="3dtex%d.bin", overwrite=False):
        count = 0
        for m in self.meshcontainer.submeshes:
            filename = prefix % count
            count += 1
            m.vertexBuffer.build3DTexture(size=32, filename=filename)

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

    ###
    # OgreXMLImport: XMLParser: XML parser class for OgreXML fileformat:
    #
    class XMLParser(xml.sax.ContentHandler):
        def setMeshContainer(self, container):
            self.mc = container
            self.texcoordBank = 0

        ###
        # Start element methods:
        #
        def __start_mesh(self, attributes):
            pass
        def __start_submeshes(self, attributes):
            pass
        def __start_submesh(self, attributes):
            materialref = ""
            operationtype = "triangle_list"
            try: materialref = attributes.getValueByQName("material")
            except KeyError: materialref = ""
            try: operationtype = attributes.getValueByQName("operationtype")
            except KeyError: operationtype = "triangle_list"
            self.mc.newSubmesh(materialref, operationtype)
        def __start_sharedgeometry(self, attributes):
            self.mc.newSharedGeometry()
        def __start_faces(self, attributes):
            pass
        def __start_face(self, attributes):
            self.mc.addFace([int(attributes.getValueByQName("v1")),
                             int(attributes.getValueByQName("v2")),
                             int(attributes.getValueByQName("v3"))])
        def __start_geometry(self, attributes):
            pass
        def __start_vertex(self, attributes):
            self.texcoordBank = 0
        def __start_vertexbuffer(self, attributes):
            for i in range(8):
                try:
                    value = attributes.getValueByQName("texture_coord_dimensions_%d" % i)
                except KeyError:
                    break
                if value == "float2":
                    self.mc.setTexcoordDimensions(i, 2)
                if value == "float3":
                    self.mc.setTexcoordDimensions(i, 3)
                if value == "float4":
                    self.mc.setTexcoordDimensions(i, 4)
        def __start_position(self, attributes):
            self.mc.addVertex([float(attributes.getValueByQName("x")),
                               float(attributes.getValueByQName("y")),
                               float(attributes.getValueByQName("z"))])
        def __start_normal(self, attributes):
            self.mc.addNormal([float(attributes.getValueByQName("x")),
                               float(attributes.getValueByQName("y")),
                               float(attributes.getValueByQName("z"))])
        def __start_texcoord(self, attributes):
            names = ["u", "v", "w", "x"]
            coords = []
            for a in names:
                try:
                    coords.append(float(attributes.getValueByQName(a)))
                except KeyError:
                    break
            self.mc.addTexcoord(coords, self.texcoordBank)
            self.texcoordBank += 1
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
            if tag == "vertex":               return self.__start_vertex(attributes)
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
    # OgreXMLImport: debug
    #
    def printStatistics(self):
        self.meshcontainer.printStatistics()

#############################################################################
# OgreXMLExport: Ogre XML output class
#
class OgreXMLExport():
    """ class OgreXMLExport(): I/O component for writing formatted OgreXML notation
        - Primarily used by MeshGenerator for producing Ogre compliant XML mesh
          notation.
        - All XML requests are pushed into buffer, and once toFile method is called
          the contents are flushes to the desired output file.
    """
    def __init__(self, meshcontainer, localfile, overwrite=False):
        self.indent = 0
        self.outputXMLFile = None
        self.meshcontainer = meshcontainer
        self.openOutputXML(localfile, overwrite)

    def toFile(self, localfile, positions=True, normals=True, texcoords0=True, texcoords1=True, diffusecolors=True):
        self.startMesh()
        if self.meshcontainer.sharedgeometry != None:
            self.startSharedgeometry(len(self.meshcontainer.sharedgeometry.vertices)/3)
            self.__outputVertexbuffer(self.meshcontainer.sharedgeometry, positions, normals, texcoords0, texcoords1, diffusecolors)
            self.endSharedgeometry()

        if len(self.meshcontainer.submeshes) > 0:
            self.startSubmeshes()
            for m in self.meshcontainer.submeshes:
                longIndices = False
                if len(m.vertexBuffer.vertices) > 32765: longIndices = True
                self.startSubmesh(m.materialref, (self.meshcontainer.sharedgeometry!=None), longIndices, m.operationtype)

                self.startFaces(len(m.faces)/3)
                for i in [m.faces[x:x+3] for x in xrange(0, len(m.faces), 3)]:
                    self.outputFace(i[0], i[1], i[2])
                self.endFaces()

                if (len(m.vertexBuffer.vertices) > 0):
                    self.startGeometry(len(m.vertexBuffer.vertices)/3)
                    self.__outputVertexbuffer(m.vertexBuffer, positions, normals, texcoords0, texcoords1, diffusecolors)
                    self.endGeometry()

                self.endSubmesh()
            self.endSubmeshes()
        self.endMesh()
        self.closeOutputXML()

    def __outputVertexbuffer(self, vb, positions=True, normals=True, texcoords0=True, texcoords1=False, diffusecolors=True):
        vb.debugMinMax()
        tdim0 = vb.texcoordDimensions[0]
        tdim1 = vb.texcoordDimensions[1]
        cDim  = vb.diffusecolorDimensions;
        vVector  = [vb.vertices[x:x+3]           for x in xrange(0, len(vb.vertices), 3)]
        nVector  = [vb.normals[x:x+3]            for x in xrange(0, len(vb.normals), 3)]
        tVector0 = [vb.texcoords[x:x+tdim0]      for x in xrange(0, len(vb.texcoords), tdim0)]
        tVector1 = [vb.texcoords_1[x:x+tdim1]    for x in xrange(0, len(vb.texcoords_1), tdim1)]
        cVector  = [vb.diffusecolors[x:x+cDim]   for x in xrange(0, len(vb.diffusecolors), cDim)]
        self.startVertexbuffer(((len(vVector) != 0)&positions),
                               ((len(nVector) != 0)&normals),
                               ((len(tVector0) != 0)&texcoords0),
                               ((len(tVector1) != 0)&texcoords1),
                               ((len(cVector) != 0)&diffusecolors),
                               tex0_dimensions = tdim0,
                               tex1_dimensions = tdim1)
        #print "Tex bank 0: ", tdim0, texcoords0, len(tVector0)
        #print "Tex bank 1: ", tdim1, texcoords1, len(tVector1)

        counter = 0
        while counter < len(vb.vertices)/3:
            self.startVertex()
            self.outputPosition(vVector[counter][0], vVector[counter][1], vVector[counter][2])
            if len(nVector) > 0 and normals:
                self.outputNormal(nVector[counter][0], nVector[counter][1], nVector[counter][2])
            if len(tVector0) > 0 and texcoords0:
                self.outputTexcoord(tVector0[counter])
            if len(tVector1) > 0 and texcoords1:
                self.outputTexcoord(tVector1[counter])
            if len(cVector) > 0 and diffusecolors:
                if cDim == 3:
                    self.outputDiffuseColor(cVector[counter][0], cVector[counter][1], cVector[counter][2])
                else: # cDim == 4
                    self.outputDiffuseColor(cVector[counter][0], cVector[counter][1], cVector[counter][2], cVector[counter][3])
            self.endVertex()
            counter += 1
        self.endVertexbuffer()

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
        self.indent += 4

    def __decreaseIndent(self):
        if self.indent > 0: self.indent -= 4

    #############################################################################
    # OgreXMLExport: Ogre XML output methods
    #
    def startMesh(self):
        self.__outputXML("<mesh>")
        self.__increaseIndent()

    def endMesh(self):
        self.__decreaseIndent()
        self.__outputXML("</mesh>")

    def startVertexbuffer(self, position=True, normal=True, texcoord0=True, texcoord1=False, diffusecolor=False, tex0_dimensions=2, tex1_dimensions=2):
        s_out = ""
        t_count = 0
        if normal == True:   s_out += "normals=\"true\" "
        if position == True: s_out += "positions=\"true\" "
        if texcoord0 == True:
            s_out += "texture_coord_dimensions_0=\"float%d\" " % tex0_dimensions
            t_count += 1
        if texcoord1 == True:
            s_out += "texture_coord_dimensions_1=\"float%d\" " % tex1_dimensions
            t_count += 1
        if t_count > 0:
            s_out += ("texture_coords=\"%d\" " % t_count)
        if diffusecolor == True:
            s_out += "colours_diffuse=\"true\" "
        self.__outputXML("<vertexbuffer %s>" % s_out)
        self.__increaseIndent()

    def endVertexbuffer(self):
        self.__decreaseIndent()
        self.__outputXML("</vertexbuffer>")

    def startSharedgeometry(self, vertices):
        self.__outputXML("<sharedgeometry vertexcount=\"%d\">" % vertices)
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

    def startSubmesh(self, material, sharedvertices, longindices=False, operationtype="triangle_list"):
        s_out = "material=\"%s\" " % material
        s_out += "usesharedvertices=\"%s\" " % str(sharedvertices).lower()
        s_out += "use32bitindexes=\"%s\" " % str(longindices).lower()
        s_out += "operationtype=\"%s\"" % operationtype
        self.__outputXML("<submesh %s>" % s_out)
        self.__increaseIndent()

    def endSubmesh(self):
        self.__decreaseIndent()
        self.__outputXML("</submesh>")

    def startFaces(self, faces):
        self.__outputXML("<faces count=\"%d\">" % faces)
        self.__increaseIndent()

    def endFaces(self):
        self.__decreaseIndent()
        self.__outputXML("</faces>")

    def startGeometry(self, vertices):
        self.__outputXML("<geometry vertexcount=\"%d\">" %vertices)
        self.__increaseIndent()

    def endGeometry(self):
        self.__decreaseIndent()
        self.__outputXML("</geometry>")

    def outputPosition(self, x, y, z):
        self.__outputXML("<position x=\"%1.6f\" y=\"%1.6f\" z=\"%1.6f\"/>" % (x, y, z))

    def outputNormal(self, x, y, z):
        self.__outputXML("<normal x=\"%1.6f\" y=\"%1.6f\" z=\"%1.6f\"/>" % (x, y, z))

    def outputTexcoord(self, l_items):
        names = ["u", "v", "w", "x"]
        s_out = "<texcoord "
        for v in range(len(l_items)):
            s_out += ("%s=\"%f\" "%(names[v],l_items[v]))
        s_out += "/>"
        self.__outputXML(s_out)

    def outputFace(self, v1, v2, v3):
        self.__outputXML("<face v1=\"%d\" v2=\"%d\" v3=\"%d\"/>" % (v1, v2, v3))

    def outputDiffuseColor(self, r, g, b, a=None):
        if a == None:
            self.__outputXML("<colour_diffuse value=\"%1.6f %1.6f %1.6f\" />" % (r, g, b))
            return
        self.__outputXML("<colour_diffuse value=\"%1.6f %1.6f %1.6f %1.6f\" />" % (r, g, b, a))

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
            if line.find("POLYGONS") != -1:
                nPolygons = int(line.split()[1])
                for index in range(nPolygons):
                    vector = f.readline().split(" ")
                    self.meshcontainer.addFace([int(vector[1]), int(vector[2]), int(vector[3])])
            if line.find("COLOR_SCALARS") != -1:
                # at this point we already know nPoints
                for index in range(nPoints):
                    vector = f.readline().split(" ")
                    self.meshcontainer.addDiffuseColor([float(vector[0]), float(vector[1]), float(vector[2])])
                print "%d colours read" % nPoints

            if line == "": break
            #print line.strip()

    ###
    # VTKMeshImport stats, for debugging
    #
    def printStatistics(self):
        self.meshcontainer.printStatistics()

###############################################################################
# Unit test case
# - the test case implements input from any supported mesh container and
#   output to any supported export format

if __name__ == "__main__":
    import getopt

    def usage():
        print "MeshIO -i <input> [-o <outputfile>]"

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
        mesh = MeshContainer.MeshContainer()
        meshio = MeshIO(mesh)
        meshio.fromFile(input, None)
        mesh.printStatistics()
        mesh.buildAABBMesh()
        if output != None:
            print "Trying output write to %s" % output
            #meshio.build3DTextures(prefix="3dtex%03d.bin", overwrite=True)
            meshio.toFile(output, overwrite=True)
    except IOError:
        print "Error parsing the input file!"
    except OSError:
        print "OSError, check OgreXMLConverter installation?"
