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
        self.TXML = TXMLOutput.TXMLOutput()

    ###########################################################################
    # File I/O
    #
    def toFile(self, filename, overwrite=False):
        self.TXML.toFile(filename, overwrite)

    ###########################################################################
    # Internal attribute creation methods
    #
    def __pushAttributeDictionary(self, name, d, parameters):
        for attr, value in d.items():
            try: self.TXML.createAttribute(attr, parameters[attr])
            except KeyError:
                self.TXML.createAttribute(attr, d[attr])
            except TypeError:
                print "Error: (%s) Paramlist not a dictionary type." % name
                return
        self.__doubleCheckAttributes(name, d, parameters)

    def __doubleCheckAttributes(self, name, d, p):
        for attr, value in p.items():
            try: t = d[attr]
            except KeyError:
                print "Warning, (%s) requesting attribute %s which is not supported by component" % (name, attr)
            #if attr[0].lower() == attr[0]:
            #    print "Warning, (%s) attribute %s not capitalized. It should be: %s" % (name, attr, attr[0].upper()+attr[1:])

    ###########################################################################
    # Attribute creation, component and entity start and stop signals
    # - EC_RidigBody
    # - EC_Name
    # - EC_Placeable
    # - EC_Mesh
    # - EC_Light
    # - EC_Script
    # - EC_InputMapper
    # - EC_OgreCompositor
    # - EC_Material
    # - EC_Terrain
    # - EC_WaterPlane
    # - EC_EnvironmentLight
    # - EC_Sky
    # - EC_SkyX
    # - EC_HydraX
    #
    def createComponent_Rigidbody(self, sync, parameters={}):
        d = { "Mass"                            :"0",
              "Shape type"                      :"0",
              "Size"                            :"1.0 1.0 1.0",
              "Collision mesh ref"              :"",
              "Friction"                        :"0.5",
              "Restitution"                     :"0",
              "Linear damping"                  :"0",
              "Angular damping"                 :"0",
              "Linear factor"                   :"1.0 1.0 1.0",
              "Angular factor"                  :"1.0 1.0 1.0",
              "Kinematic"                       :"false",
              "Phantom"                         :"false",
              "Draw debug"                      :"false",
              "Linear velocity"                 :"0.0 0.0 0.0",
              "Angular velocity"                :"0.0 0.0 0.0",
              "Collision layer"                 :"-1",
              "Collision mask"                  :"-1" }
        self.TXML.startComponent("EC_RigidBody", str(sync))
        self.__pushAttributeDictionary("EC_RidigBody", d, parameters)
        self.TXML.endComponent()

    def createComponent_Name(self, sync, parameters={}):
        d = { "name"                            :"",
              "description"                     :"" }
        self.TXML.startComponent("EC_Name", str(sync))
        self.__pushAttributeDictionary("EC_Name", d, parameters)
        self.TXML.endComponent()

    def createComponent_Placeable(self, sync, parameters={}):
        d = { "Transform"                       :"0,0,0,0,0,0,1,1,1",
              "Show bounding box"               :"false",
              "Visible"                         :"true",
              "Selection layer"                 :"1",
              "Parent entity ref"               :"",
              "Parent bone name"                :"" }
        self.TXML.startComponent("EC_Placeable", str(sync))
        self.__pushAttributeDictionary("EC_Name", d, parameters)
        self.TXML.endComponent()

    def createComponent_Mesh(self, sync, parameters={}):
        d = { "Transform"                       :"0,0,0,0,0,0,1,1,1",
              "Mesh ref"                        :"",
              "Skeleton ref"                    :"",
              "Mesh materials"                  :"",
              "Draw distance"                   :"0",
              "Cast shadows"                    :"true" }
        self.TXML.startComponent("EC_Mesh", str(sync))
        self.__pushAttributeDictionary("EC_Mesh", d, parameters)
        self.TXML.endComponent()

    def createComponent_Light(self, sync, parameters={}):
        d = { "lighttype"                       :"",
              "diffuse color"                   :"1.0 1.0 1.0",
              "specular color"                  :"0.0 0.0 0.0",
              "cast shadows"                    :"false",
              "light range"                     :"25.0",
              "brightness"                      :"1.0",
              "constant atten"                  :"0.0",
              "linear atten"                    :"0.01",
              "quadratic atten"                 :"0.01",
              "light inner angle"               :"30.0",
              "lilght outer angle"              :"40.0" }
        self.TXML.startComponent("EC_Light", str(sync))
        self.__pushAttributeDictionary("EC_Light", d, parameters)
        self.TXML.endComponent()

    def createComponent_Script(self, sync, parameters={}):
        d = { "Script ref"                      :"",
              "Run on load"                     :"false",
              "Run mode"                        :"0",
              "Script application name"         :"",
              "Script class name"               :"" }
        self.TXML.startComponent("EC_Script", str(sync))
        self.__pushAttributeDictionary("EC_Script", d, parameters)
        self.TXML.endComponent()

    def createComponent_Inputmapper(self, sync, parameters={}):
        d = { "Input context name"              :"EC_InputMapper",
              "Input context priority"          :"90",
              "Take keyboard events over QT"    :"false",
              "Take mouse events over QT"       :"false",
              "Action execution type"           :"1",
              "Key modifiers enable"            :"true",
              "Enable actions"                  :"true",
              "Trigger on keyrepeats"           :"true",
              "Suppress used keybaord events"   :"false",
              "Suppress used mouse events"      :"false" }
        self.TXML.startComponent("EC_InputMapper", str(sync))
        self.__pushAttributeDictionary("EC_InputMapper", d, parameters)
        self.TXML.endComponent()

    def createComponent_Ogrecompositor(self, sync, parameters={}):
        d = { "Enabled"                         :"false",
              "Compositor ref"                  :"HDR",
              "Priority"                        :"-1",
              "Parameters"                      :"" }
        self.TXML.startComponent("EC_OgreCompositor", str(sync))
        self.__pushAttributeDictionary("EC_OgreCompositor", d, parameters)
        self.TXML.endComponent()

    def createComponent_Material(self, sync, parameters={}):
        d = { "Parameters"                      :"",
              "Output material"                 :"",
              "Input material"                  :"" }
        self.TXML.startComponent("EC_Material", str(sync))
        self.__pushAttributeDictionary("EC_Material", d, parameters)
        self.TXML.endComponent()

    def createComponent_Terrain(self, sync, parameters={}):
        d = { "Transform"                       :"0,0,0,0,0,0,1,1,1",
              "Grid Width"                      :"1",
              "Grid Height"                     :"1",
              "Material"                        :"local://RexTerrainPCF.material",
              "Heightmap"                       :"",
              "Tex. U scale"                    :"0.13",
              "Tex. V scale"                    :"0.13" }
        self.TXML.startComponent("EC_Terrain", str(sync))
        self.__pushAttributeDictionary("EC_Terrain", d, parameters)
        self.TXML.endComponent()

    def createComponent_Waterplane(self, sync, parameters={}):
        d = { "x-size"                          :"5000",
              "y-size"                          :"5000",
              "depth"                           :"20",
              "Position"                        :"0 0 0",
              "Rotation"                        :"1 0 0 0",
              "U factor"                        :"0.0002f",
              "V factor"                        :"0.0002f",
              "Segments in x"                   :"10",
              "Segments in y"                   :"10",
              "Material"                        :"Ocean",
              "Material ref"                    :"",
              "Fog color"                       :"0.2 0.4 0.35 1.0",
              "Fog start dist."                 :"100.0f",
              "Fog end dist."                   :"2000.0f",
              "Fog mode"                        :"3",
              "Fog exponential density"         :"0.001f" }
        self.TXML.startComponent("EC_WaterPlane", str(sync))
        self.__pushAttributeDictionary("EC_WaterPlane", d, parameters)
        self.TXML.endComponent()

    def createComponent_Environmentlight(self, sync, parameters={}):
        d = { "Sunlight color"                  :"0.63 0.63 0.63 1.0",
              "Ambient light color"             :"0.36 0.36 0.36 1.0",
              "Sunlight diffuse color"          :"0.93 0.93 0.93 1.0",
              "Sunlight direction vector"       :"-1.0 -1.0 -1.0",
              "Sunlight cast shadows"           :"true" }
        self.TXML.startComponent("EC_EnvironmentLight", str(sync))
        self.__pushAttributeDictionary("EC_EnvironmentLight", d, parameters)
        self.TXML.endComponent()

    def createComponent_Sky(self, sync, parameters={}):
        d = { "Material"                        :"RexSkyBox",
              "Texture"                         :"rex_sky_front.dds;rex_sky_back.dds;rex_sky_left.dds;rex_sky_right.dds;rex_sky_top.dds;rex_sky_bot.dds",
              "Distance"                        :"50",
              "Orientation"                     :"0.0 0.0 0.0 1.0",
              "Draw first"                      :"true" }
        self.TXML.startComponent("EC_Sky", str(sync))
        self.__pushAttributeDictionary("EC_Sky", d, parameters)
        self.TXML.endComponent()

    def createComponent_SkyX(self, sync, parameters={}):
        d = { "Cloud type"                      :"1",
              "Time multiplier"                 :"0.25",
              "Time [0-24]"                     :"16.978079",
              "Time sunrise [0-24]"             :"7.5",
              "Time sunset [0-24]"              :"20.5",
              "Cloud coverage [0-100]"          :"50",
              "Cloud average size [0-100]"      :"50",
              "Cloud height"                    :"100",
              "Moon phase [0-100]"              :"70.7420731",
              "Sun inner radius"                :"9.75",
              "Sun outer radius"                :"10.25",
              "Wind direction"                  :"0",
              "Wind speed"                      :"5" }
        self.TXML.startComponent("EC_SkyX", str(sync))
        self.__pushAttributeDictionary("EC_SkyX", d, parameters)
        self.TXML.endComponent()

    def createComponent_HydraX(self, sync, parameters={}):
        d = { "Config ref"                      :"HydraxDefault.hdx",
              "Visible"                         :"true",
              "Position"                        :"0.0 7.0 0.0" }
        self.TXML.startComponent("EC_Hydrax", str(sync))
        self.__pushAttributeDictionary("EC_Hydrax", d, parameters)
        self.TXML.endComponent()


    ###########################################################################
    # Dynamic component creation
    #
    def createComponent_Dynamiccomponent(self, name, variables):
        self.TXML.startComponent("EC_DynamicComponent", sync="1", name=name)
        for var in variables:
            self.TXML.createDynamicAttribute(var[0], var[1], var[2])
        self.TXML.endComponent()


    ###########################################################################
    # Entity creation macros. These macros create certain, often needed entities.
    # Parametrization is minimal, and if the defaults are not suitable for the
    # application requirement then use the component creation methods instead
    #
    # - Terrain
    # - Static mesh
    # - Water plane
    # - Simple Sky (Environmentlight + Sky)
    #
    def createEntity_Terrain(self, sync, name, transform="0,0,0,0,0,0,1,1,1", width=1, height=1, material="", heightmap=""):
        self.TXML.startEntity()
        self.createComponent_Name(sync, { "name":str(name) } )
        self.createComponent_Terrain(sync, {  "Grid Width"  :str(width),
                                              "Grid Height" :str(height),
                                              "Material"    :str(material),
                                              "Heightmap"   :str(heightmap) } )
        self.createComponent_Rigidbody(sync, { "Shape type" :"5" } )
        self.createComponent_Placeable(sync, { "Transform"  :str(transform) } )
        self.TXML.endEntity()

    def createEntity_Staticmesh(self, sync, name, transform="0,0,0,0,0,0,1,1,1", mesh="", material="", skeleton=""):
        self.TXML.startEntity()
        self.createComponent_Name(sync, { "name"            :str(name) } )
        self.createComponent_Mesh(sync, { "Mesh ref"        :str(mesh),
                                          "Skeleton ref"    :str(skeleton),
                                          "Mesh materials"  :str(material) } )
        self.createComponent_Placeable(sync, { "Transform"  :str(transform) } )
        self.createComponent_Rigidbody(sync, { "Shape type" :"4",
                                               "Collision mesh ref":str(mesh) } )
        self.TXML.endEntity()

    def createEntity_Waterplane(self, sync, name, width, height, level):
        self.TXML.startEntity()
        self.createComponent_Name(sync, { "name"            :str(name) } )
        self.createComponent_Placeable(sync, { "Transform"  :"0,0,%d,0,0,0,1,1,1"%level } )
        self.createComponent_Waterplane(sync, { "x-size"     :str(width),
                                                "y-size"     :str(height) } )
        self.TXML.endEntity()



    def createEntity_Avatar(self, sync, name, script):
        self.TXML.startEntity()
        self.createComponent_Name(sync, { "name"            :str(name) } )
        self.createComponent_Script(sync, { "Script ref"    :str(script),
                                            "Run on load"   :"true",
                                            "Script application name":"AvatarApp" } )
        self.TXML.endEntity()

    def createEntity_SimpleSky(self, sync, name):
        self.TXML.startEntity()
        self.createComponent_Name(sync, { "name":str(name) } )
        self.createComponent_Environmentlight(sync)
        self.createComponent_Sky(sync)
        self.TXML.endEntity()


###########################################################################
# Unit test case for demonstration of the WorldGenerator
#
if __name__ == "__main__": # if run standalone
    import MeshGenerator
    import MeshIO
    import MeshContainer
    import TerrainGenerator
    import TextureGenerator

    # By a default test case we shall run an embedded world generator script to create a simple
    # world with terrain and a few objects in it. Feel free to rewrite the generator using
    # world generator primitives, by yourself.
    world = WorldGenerator()
    terrain = TerrainGenerator.TerrainGenerator()
    texture = TextureGenerator.TextureGenerator()

    width = 32
    height = 32
    assetdir = "./resources/"

    world.TXML.startScene()

    print "Generating grass texture..."
    texture.createSingleColorTexture(30,100,30,50)
    texture.toImage("./resources/generated_grass.png", "PNG", overwrite=True)
    print "Generating stone texture..."
    texture.createSingleColorTexture(90,83,73,50)
    texture.toImage("./resources/generated_stone.png", "PNG", overwrite=True)
    print "Generating sand texture..."
    texture.createSingleColorTexture(160,136,88,70)
    texture.toImage("./resources/generated_sand.png", "PNG", overwrite=True)

    print "Generating a terrain..."
    terrain.fromDiamondsquare(width, 10, -5, -5, 10)
    terrain.rescale(-20, 50)
    terrain.saturate(-5)
    terrain.toWeightmap(assetdir + "terrainsurfacemap.png", overwrite=True)
    terrain.toFile(assetdir + "terrain.ntf", overwrite=True)

    world.createEntity_Terrain(1, "terrain", transform="%d,0,%d,0,0,0,1,1,1"%(-width*8, -height*8), width=width, height=height, material="terrainsample.material", heightmap="terrain.ntf")
    world.createEntity_Waterplane(1, "waterplane", width*world.cPatchSize, height*world.cPatchSize, -1)
    world.createEntity_Avatar(1, "AvatarApp", "avatarapplication.js;simpleavatar.js;exampleavataraddon.js")
    world.createEntity_SimpleSky(1, "SimpleSky")

    print ("Generating a group of meshes to the world...")
    mesh = MeshContainer.MeshContainer()
    meshgen = MeshGenerator.MeshGenerator(mesh)
    meshgen.createPlane(LOD=5)
    meshio = MeshIO.MeshIO(mesh)
    meshio.toFile(assetdir + "plane.mesh.xml", overwrite=True)

    for i in range(20):
        x = random.randint(0, width*world.cPatchSize)
        y = random.randint(0, height*world.cPatchSize)
        z = terrain.getHeight(x,y)
        x = x - width*world.cPatchSize/2
        y = y - height*world.cPatchSize/2
        if (z > 2.0) and (z < terrain.getMaxitem()/2.0):
            world.createEntity_Staticmesh(1, "Tree"+str(world.TXML.getCurrentEntityID()),
                                          mesh="plane.mesh",
                                          material="",
                                          transform="%f,%f,%f,0,0,0,1,1,1" % (y, x, z))

    world.TXML.endScene()
    world.toFile("./testworld.txml", overwrite=True)

