#!/usr/bin/python
# WorldGenerator.py <width> <height>
# defaults:
#  - width  10
#  - height 10

import random
from TerrainGenerator import *

class WorldGenerator():
    """ class WorldGenerator():
        - A baseclass for creating 3D worlds based on realXtend project entity component
          model.
    """

    def __init__(self):
        self.indent = 0
        self.id = 1
        self.cPatchSize = 16
        self.cPatchSize = 16
        self.terrain = TerrainGenerator()

    ### Output methods, for writing txml ###

    def output(self, string):
        """ WorldGenerator.output(string):
            - Takes a null terminated string as input and writes it into the output stream.
              the current implementation writes directly to stdout, and the purpose is to
              allow redirection of the output in shell to what ever target.
            - It is assumed that the input string is already formatted for output.
            - This method also does automatic intention if the txml output, which is
              controlled via self.increase_indent() and self.decrease_indent() methods.
            Return value: None
        """
        self.indent_str = ""
        for i in range(self.indent):
            self.indent_str = self.indent_str + " "
        sys.stdout.write(self.indent_str + str(string) + "\n")

    def increase_indent(self):
        self.indent = self.indent + 1

    def decrease_indent(self):
        self.indent = self.indent - 1
        if self.indent < 0:
            self.indent = 0

    def message(self, string):
        sys.stderr.write(string + "\n")

    ### Attribute creation, component and entity start and stop signals

    def start_scene(self):
        self.output("<!DOCTYPE Scene>\n<scene>")
        self.increase_indent()

    def end_scene(self):
        self.decrease_indent()
        self.output("</scene>")

    def start_component(self, component, sync):
        self.output("<component type=\"" + str(component) + "\" sync=\"" + str(sync) + "\">")
        self.increase_indent()

    def end_component(self):
        self.decrease_indent()
        self.output("</component>")

    def start_entity(self):
        self.output("<entity id=\"" + str(self.id) + "\">")
        self.increase_indent()

    def end_entity(self):
        self.decrease_indent()
        self.output("</entity>")
        self.id = self.id + 1

    def create_attribute(self, name, value):
        self.output("<attribute value=\"" + str(value) + "\" name=\"" + str(name) + "\"/>")

    def create_component_rigidbody(self, reference, mass, shapetype, collision):
        self.start_component("EC_RigidBody", "1")
        self.create_attribute("Mass", str(mass))
        self.create_attribute("Shape type", str(shapetype))
        if collision != "": c_str = str(reference) + str(collision)
        else: c_str = ""
        self.create_attribute("Collision mesh ref", c_str)
        self.create_attribute("Friction", "0.5")
        self.create_attribute("Restitution", "0")
        self.create_attribute("Linear damping", "0")
        self.create_attribute("Angular damping", "0")
        self.create_attribute("Linear factor", "1 1 1")
        self.create_attribute("Angular factor", "1 1 1")
        self.create_attribute("Phantom", "false")
        self.create_attribute("Draw Debug", "false")
        self.create_attribute("Linear velocity", "0 0 0")
        self.create_attribute("Angular velocity", "0 0 0")
        self.end_component()

    def create_component_name(self, name, description, userdefined):
        self.start_component("EC_Name", "1")
        self.create_attribute("name", str(name))
        self.create_attribute("description", str(description))
        self.create_attribute("user-defined", str(userdefined))
        self.end_component()

    def create_component_placeable(self, transform):
        self.start_component("EC_Placeable", "1")
        self.create_attribute("Position", "0 0 0")
        self.create_attribute("Scale", "0 0 0")
        self.create_attribute("Transform", str(transform))
        self.create_attribute("Show bounding box", "false")
        self.create_attribute("Visible", "true")
        self.end_component()

    ### Logical components for the world

    def insert_materials(self, reference, materials):
        #self.message("Inserting %d materials with reference %s" % (len(materials), reference))
        m_str = ""
        for i in range(len(materials)):
            m_str = m_str + str(reference) + materials[i]
            if i != len(materials)-1: m_str = m_str + ";"
        return m_str

    def create_static_mesh(self, name, mesh, reference, materials, center_x, center_y, center_z=0.0):
        self.start_entity()
        # Mesh component
        self.start_component("EC_Mesh", "1")
        self.create_attribute("Transform", "0,0,0,90,0,180,1,1,1")
        self.create_attribute("Mesh ref", str(reference) + str(mesh))
        self.create_attribute("Skeleton ref", "")
        self.create_attribute("Mesh materials", self.insert_materials(reference, materials))
        self.create_attribute("Draw distance", "0")
        self.create_attribute("Cast shadows", "true")
        self.end_component()
        # Name -component
        self.create_component_name(str(name), "", "false")
        # Placeable -component
        self.start_component("EC_Placeable", "1")
        self.create_attribute("Position", "0 0 0")
        self.create_attribute("Scale", "0 0 0")
        self.create_attribute("Transform", str(center_x)+","+str(center_y)+","+str(center_z)+",0,0,180,1,1,1")
        self.create_attribute("Show bounding box", "false")
        self.create_attribute("Visible", "true")
        self.end_component()
        # Rigidbody -component
        self.create_component_rigidbody(reference, "1", "4", mesh)
        self.end_entity()

    def create_terrain(self, reference, materials, heightmap, collision, width, height):
        self.start_entity()
        self.create_component_name("terrain"+str(self.id), "", "false")
        self.start_component("EC_Terrain", "1")
        self.create_attribute("Transform", "-"+str(width*8)+",-"+str(height*8)+",0,0,0,0,1,1,1")
        self.create_attribute("Grid Width", str(width))
        self.create_attribute("Grid Height", str(height))
        self.create_attribute("Tex. U scale", "0.129999995")
        self.create_attribute("Tex. V scale", "0.129999995")
        self.create_attribute("Material", self.insert_materials(reference, materials))
        self.create_attribute("Texture 0", "")
        self.create_attribute("Texture 1", "")
        self.create_attribute("Texture 2", "")
        self.create_attribute("Texture 3", "")
        self.create_attribute("Texture 4", "")
        self.create_attribute("Heightmap", str(reference) + str(heightmap))
        self.end_component()
        self.create_component_rigidbody(reference, "0", "5", collision)
        self.end_entity()

    def create_avatar(self, reference, script):
        self.start_entity()
        self.start_component("EC_Script", "1")
        self.create_attribute("Type", "js")
        self.create_attribute("Run on load", "true")
        self.create_attribute("Script ref", str(reference) + str(script))
        self.end_component()
        self.create_component_name("AvatarScript"+str(self.id), "", "false")
        self.end_entity()

    def create_waterplane(self, width, height, level):
        self.start_entity()
        self.create_component_name("WaterPlane"+str(self.id), "", "false")
        self.create_component_placeable("0,0,"+str(level)+",0,0,0,1,1,1")
        self.start_component("EC_WaterPlane", "1")
        self.create_attribute("x-size", str(width))
        self.create_attribute("y-size", str(height))
        self.create_attribute("depth", "20")
        self.create_attribute("Position", "0 0 0")
        self.create_attribute("Rotation", "1 0 0 0")
        self.create_attribute("U factor", "0.00199999995")
        self.create_attribute("V factor", "0.00199999995")
        self.create_attribute("Segments in x", "10")
        self.create_attribute("Segments in y", "10")
        self.create_attribute("Material", "Ocean")
        self.create_attribute("Material ref", "")
        self.create_attribute("Fog color", "0.2 0.4, 0.35")
        self.create_attribute("Fog start dist.", "100")
        self.create_attribute("Fog end dist.", "2000")
        self.create_attribute("Fog mode", "3")
        self.end_component()
        self.end_entity()

    ### High level world generation itself

    def generateworld(self, width, height):
        self.start_scene()

        self.message("Generating terrain...")
        self.create_terrain("local://", ("terrainweighted2.material",), "terrain.ntf", "", width, height)
        self.terrain.fromdiamondsquare(width, 10, -5, -5, 10)
        self.terrain.apply_rescale(-20, 50)
        self.terrain.apply_saturate(-5)
        self.terrain.create_weightmap("./blender-export/terrain.tga")
        self.terrain.tofile("./blender-export/terrain.ntf")

        self.create_waterplane(width*self.cPatchSize, height*self.cPatchSize, -1)
        self.create_avatar("local://", "avatarapplication.js")

        self.message("Generating forest...")
        for i in range(300):
            x = random.randint(0, width*self.cPatchSize)
            y = random.randint(0, height*self.cPatchSize)
            z = self.terrain.get_height(x,y)
            x = x - width*self.cPatchSize/2
            y = y - height*self.cPatchSize/2
            if (z > 2.0) and (z < self.terrain.get_maxitem()/2.0):
                self.create_static_mesh("Tree"+str(self.id),
                                        "sassa_asimina_g.mesh",
                                        "local://",
                                        ("m_sassafaras_leaves.material", "m_asimina_bark.material", "m_asimina_leaves.material"),
                                        y, x, z)
                #print "creaeting in %d %d %d" % (x, y, z)

        self.end_scene()

###

if __name__ == "__main__": # if run standalone
    world = WorldGenerator()
    world.generateworld(32, 32)
