#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys
import random

import TXMLOutput

class WorldGenerator():
    """ class WorldGenerator():
        - A baseclass for creating 3D worlds based on realXtend project entity component
          model.
    """

    def __init__(self):
        self.cPatchSize = 16
        self.cPatchSize = 16
        self.terrain = TerrainGenerator.TerrainGenerator()
        self.TXML = TXMLOutput.TXMLOutput()

    ### Error logging to stderr ###

    def message(self, string):
        sys.stderr.write(string + "\n")

    def toFile(self, filename, overwrite=False):
        self.TXML.toFile(filename, overwrite)

    ### Attribute creation, component and entity start and stop signals

    def create_component_rigidbody(self, reference, mass, shapetype, collision):
        self.TXML.startComponent("EC_RigidBody", "1")
        self.TXML.createAttribute("Mass", str(mass))
        self.TXML.createAttribute("Shape type", str(shapetype))
        if collision != "": c_str = str(reference) + str(collision)
        else: c_str = ""
        self.TXML.createAttribute("Collision mesh ref", c_str)
        self.TXML.createAttribute("Friction", "0.5")
        self.TXML.createAttribute("Restitution", "0")
        self.TXML.createAttribute("Linear damping", "0")
        self.TXML.createAttribute("Angular damping", "0")
        self.TXML.createAttribute("Linear factor", "1 1 1")
        self.TXML.createAttribute("Angular factor", "1 1 1")
        self.TXML.createAttribute("Phantom", "false")
        self.TXML.createAttribute("Draw Debug", "false")
        self.TXML.createAttribute("Linear velocity", "0 0 0")
        self.TXML.createAttribute("Angular velocity", "0 0 0")
        self.TXML.endComponent()

    def create_component_name(self, name, description, userdefined):
        self.TXML.startComponent("EC_Name", "1")
        self.TXML.createAttribute("name", str(name))
        self.TXML.createAttribute("description", str(description))
        self.TXML.createAttribute("user-defined", str(userdefined))
        self.TXML.endComponent()

    def create_component_placeable(self, transform):
        self.TXML.startComponent("EC_Placeable", "1")
        self.TXML.createAttribute("Position", "0 0 0")
        self.TXML.createAttribute("Scale", "0 0 0")
        self.TXML.createAttribute("Transform", str(transform))
        self.TXML.createAttribute("Show bounding box", "false")
        self.TXML.createAttribute("Visible", "true")
        self.TXML.endComponent()

    ### Logical components for the world

    def insert_materials(self, reference, materials):
        #self.message("Inserting %d materials with reference %s" % (len(materials), reference))
        m_str = ""
        for i in range(len(materials)):
            m_str = m_str + str(reference) + materials[i]
            if i != len(materials)-1: m_str = m_str + ";"
        return m_str

    def create_static_mesh(self, name, mesh, reference, materials, center_x, center_y, center_z=0.0):
        self.TXML.startEntity()
        # Mesh component
        self.TXML.startComponent("EC_Mesh", "1")
        self.TXML.createAttribute("Transform", "0,0,0,90,0,180,1,1,1")
        self.TXML.createAttribute("Mesh ref", str(reference) + str(mesh))
        self.TXML.createAttribute("Skeleton ref", "")
        self.TXML.createAttribute("Mesh materials", self.insert_materials(reference, materials))
        self.TXML.createAttribute("Draw distance", "0")
        self.TXML.createAttribute("Cast shadows", "true")
        self.TXML.endComponent()
        # Name -component
        self.create_component_name(str(name), "", "false")
        # Placeable -component
        self.TXML.startComponent("EC_Placeable", "1")
        self.TXML.createAttribute("Position", "0 0 0")
        self.TXML.createAttribute("Scale", "0 0 0")
        self.TXML.createAttribute("Transform", str(center_x)+","+str(center_y)+","+str(center_z)+",0,0,180,1,1,1")
        self.TXML.createAttribute("Show bounding box", "false")
        self.TXML.createAttribute("Visible", "true")
        self.TXML.endComponent()
        # Rigidbody -component
        #self.create_component_rigidbody(reference, "1", "4", mesh)
        self.TXML.endEntity()

    def create_terrain(self, reference, materials, heightmap, collision, width, height):
        self.TXML.startEntity()
        self.create_component_name("terrain"+str(self.TXML.getCurrentEntityID()), "", "false")
        self.TXML.startComponent("EC_Terrain", "1")
        self.TXML.createAttribute("Transform", "-"+str(width*8)+",-"+str(height*8)+",0,0,0,0,1,1,1")
        self.TXML.createAttribute("Grid Width", str(width))
        self.TXML.createAttribute("Grid Height", str(height))
        self.TXML.createAttribute("Tex. U scale", "0.129999995")
        self.TXML.createAttribute("Tex. V scale", "0.129999995")
        self.TXML.createAttribute("Material", self.insert_materials(reference, materials))
        self.TXML.createAttribute("Texture 0", "")
        self.TXML.createAttribute("Texture 1", "")
        self.TXML.createAttribute("Texture 2", "")
        self.TXML.createAttribute("Texture 3", "")
        self.TXML.createAttribute("Texture 4", "")
        self.TXML.createAttribute("Heightmap", str(reference) + str(heightmap))
        self.TXML.endComponent()
        self.create_component_rigidbody(reference, "0", "5", collision)
        self.TXML.endEntity()

    def create_avatar(self, reference, script):
        self.TXML.startEntity()
        self.TXML.startComponent("EC_Script", "1")
        self.TXML.createAttribute("Type", "js")
        self.TXML.createAttribute("Run on load", "true")
        self.TXML.createAttribute("Script ref", str(reference) + str(script))
        self.TXML.endComponent()
        self.create_component_name("AvatarScript"+str(self.TXML.getCurrentEntityID()), "", "false")
        self.TXML.endEntity()

    def create_waterplane(self, width, height, level):
        self.TXML.startEntity()
        self.create_component_name("WaterPlane"+str(self.TXML.getCurrentEntityID()), "", "false")
        self.create_component_placeable("0,0,"+str(level)+",0,0,0,1,1,1")
        self.TXML.startComponent("EC_WaterPlane", "1")
        self.TXML.createAttribute("x-size", str(width))
        self.TXML.createAttribute("y-size", str(height))
        self.TXML.createAttribute("depth", "20")
        self.TXML.createAttribute("Position", "0 0 0")
        self.TXML.createAttribute("Rotation", "1 0 0 0")
        self.TXML.createAttribute("U factor", "0.00199999995")
        self.TXML.createAttribute("V factor", "0.00199999995")
        self.TXML.createAttribute("Segments in x", "10")
        self.TXML.createAttribute("Segments in y", "10")
        self.TXML.createAttribute("Material", "Ocean")
        self.TXML.createAttribute("Material ref", "")
        self.TXML.createAttribute("Fog color", "0.2 0.4, 0.35")
        self.TXML.createAttribute("Fog start dist.", "100")
        self.TXML.createAttribute("Fog end dist.", "2000")
        self.TXML.createAttribute("Fog mode", "3")
        self.TXML.endComponent()
        self.TXML.endEntity()

###

if __name__ == "__main__": # if run standalone
    import MeshGenerator
    import TerrainGenerator

    # By a default test case we shall run an embedded world generator script to create a simple
    # world with terrain and a few objects in it. Feel free to rewrite the generator using
    # world generator primitives, by yourself.
    world = WorldGenerator()
    mesh = MeshGenerator.MeshGenerator()
    terrain = TerrainGenerator.TerrainGenerator()

    width = 32
    height = 32
    assetdir = "./resources/"

    world.TXML.startScene()

    print "Generating a terrain..."
    terrain.fromDiamondsquare(width, 10, -5, -5, 10)
    terrain.rescale(-20, 50)
    terrain.saturate(-5)
    terrain.toWeightmap(assetdir + "terrain.tga", overwrite=True)
    terrain.toFile(assetdir + "terrain.ntf", overwrite=True)

    world.create_terrain("local://", ("terrainweighted2.material",), "terrain.ntf", "", width, height)
    world.create_waterplane(width*world.cPatchSize, height*world.cPatchSize, -1)
    world.create_avatar("local://", "avatarapplication.js")

    world.message("Generating a group of meshes to the world...")
    mesh.createPlane()
    mesh.toFile(assetdir + "plane.mesh.xml", overwrite=True)
    for i in range(20):
        x = random.randint(0, width*world.cPatchSize)
        y = random.randint(0, height*world.cPatchSize)
        z = terrain.getHeight(x,y)
        x = x - width*world.cPatchSize/2
        y = y - height*world.cPatchSize/2
        if (z > 2.0) and (z < terrain.getMaxitem()/2.0):
            world.create_static_mesh("Tree"+str(world.TXML.getCurrentEntityID()),
                                     "plane.mesh",
                                     "local://",
                                     (),
                                     y, x, z)
        #print "creaeting in %d %d %d" % (x, y, z)

    world.TXML.endScene()
    world.toFile("./testworld.txml", overwrite=True)
