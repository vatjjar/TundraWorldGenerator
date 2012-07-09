#!/usr/bin/python

import TerrainGenerator
import WorldGenerator
import MaterialGenerator
import TextureGenerator

prefix         = ""
avatar_prefix  = ""
env_prefix     = ""

def create_assets():
    print "Reading terrain from ASC file"
    t = TerrainGenerator.TerrainGenerator()
    t.fromFile("terrain.asc")
    t.adjustHeight(-300.0)
    t.toFile("./terrain.ntf", overwrite=True)
    print "Generating weightmap for the ASC terrain"
    t.toWeightmap("./terrainweight.png", fileformat="PNG", overwrite=True)
    print "Generating terrain material"
    m = MaterialGenerator.Material("terrain")
    m.createMaterial_4channelTerrain("terrain", "sand.png", "grass.png", "rock.png", "", "terrainweight.png")
    m.toFile("./terrain.material", overwrite=True)
    print "Generating terrain textures"
    t = TextureGenerator.TextureGenerator()
    t.createSingleColorTexture(30,100,30,50)
    t.toImage("./grass.png", "PNG", overwrite=True)
    t.createSingleColorTexture(90,83,73,50)
    t.toImage("./rock.png", "PNG", overwrite=True)
    t.createSingleColorTexture(160,136,88,70)
    t.toImage("./sand.png", "PNG", overwrite=True)

def create_world():
    t_width  = 16*((1500/16)+1)
    t_height = 16*((1500/16)+1)
    w = WorldGenerator.WorldGenerator()
    w.TXML.startScene()
    w.createEntity_Terrain(1, "terrain", transform="-304,0,-304,0,0,0,1,1,1",
                              width=t_width, height=t_height,
                              material=prefix+"terrain.material",
                              heightmap=prefix+"terrain.ntf")
    w.createEntity_SimpleSky(1, "SimpleSky",
                                texture = env_prefix+"rex_sky_front.dds;" + env_prefix+"rex_sky_back.dds;" + \
                                          env_prefix+"rex_sky_left.dds;" + env_prefix+"rex_sky_right.dds;" + \
                                          env_prefix+"rex_sky_top.dds;" + env_prefix+"rex_sky_bottom.dds")
    w.createEntity_Avatar(1, "AvatarApp",
                             avatar_prefix+"avatarapplication.js;"+ \
                             avatar_prefix+"simpleavatar.js;" + \
                             avatar_prefix+"exampleavataraddon.js")
    w.createEntity_Waterplane(1, "Waterplane", 608, 608, 0.0)
    w.TXML.endScene()
    w.toFile("./Terrain.txml", overwrite=True)

create_assets()
create_world()
