#!/usr/bin/python

####
# usage example
#
#    tree = TreeGenerator.TreeGenerator(generatedFolder, resourcesFolder, terrainSlice, tileWidth, verScale, horScale, 
#                                       "spruce.mesh.xml", "pine.mesh.xml", "birch.mesh.xml",
#                                       "spruce.material", "pine.material", "birch.material")
#    tree.createForest(w)
# 
# 
####
import WorldGenerator
import TerrainGenerator
import random
from PIL import Image
import MeshContainer
import MeshIO
import subprocess
import datetime


class TreeGenerator():

    def __init__(self, outputFolder, inputFolder, terrainSlice, tileWidth, verScale, horScale, 
                     tree1, tree2, tree3, 
                     treetex1, treetex2, treetex3, 
                     treeMinHeight=None, treeMaxHeight=None, groupWidth = None, treesInGroup = None):
        
        self.outputFolder = outputFolder
        self.inputFolder = inputFolder
        
        # string tuple containing the names of the tiles
        self.terrainSlice = terrainSlice
        # int containing the width of a tile
        self.tileWidth = tileWidth
        #scaling factors
        self.verScale = verScale
        self.horScale = horScale
        
        #treetypes
        self.tree1 = tree1
        self.tree2 = tree2
        self.tree3 = tree3
        self.treetex1 = treetex1
        self.treetex2 = treetex2
        self.treetex3 = treetex3
             
        # min height where trees can appear
        self.treeMinHeight = treeMinHeight
        # max, beyond this point there will be no trees
        self.treeMaxHeight = treeMaxHeight
        #width of the forest tiles
        self.groupWidth = groupWidth
        #max abount of trees allowed in a group
        self.treesInGroup = treesInGroup
        
        #default values
        if treeMinHeight == None:
            self.treeMinHeight = 2
        if treeMaxHeight == None:
            self.treeMaxHeight = 200
        if groupWidth == None:
            self.groupWidth = 50
        if treesInGroup == None:
            self.treesInGroup = 1000
        self.subSlice = tileWidth / self.groupWidth
    
    
    def createForest(self, w):
        start = datetime.datetime.now()
        print "Started: " + str(start)
        print "Generating trees..."
        
        for tile, tileName in enumerate(self.terrainSlice):
            #read height data from generated .ntf files
            inputFile = self.outputFolder + tileName + ".ntf"
            t = TerrainGenerator.TerrainGenerator()
            t.fromFile(inputFile)
            
            coordGeneral = self.generateCoordGrid(t, tile)
            vegCoord = []
            vegCoord = self.vegMapToCoord(tileName)
            
            self.createForestPatch(t, w, coordGeneral, tile, tileName, vegCoord)
            
        stop = datetime.datetime.now()
        print "Stopped: " + str(stop)
        print "Runtime: " + str(stop - start)

    #generate a grid of coordinates
    def generateCoordGrid(self, t, tile):
        coord = []
        sliceWidth = self.tileWidth / self.subSlice
        
        for i in range(self.subSlice): #x
            for j in range(self.subSlice): #y
                x = i * sliceWidth
                z = j * sliceWidth
                #offset coordinates to tile vegmap, designated zone in a different location
                x, z = self.locationOffset(tile, x, z, 1)
                
                # coordinates flipped from 3d to 2d x,y,z -> z,x  
                y = t.getHeight(z,x)
                coord.append([x, y*self.verScale, z])
        
        coord.sort()
        return coord
    
    
    def locationOffset(self, tile, x, y, mode = 0):
        #placement correction, generated trees to their own slice
        if mode == 0:
            if tile == 0:
                x = x
                y = y
            elif tile == 1:
                x = x - self.tileWidth
                y = y
            elif tile == 2:
                x = x - self.tileWidth
                y = y - self.tileWidth
            elif tile == 3:
                x = x
                y = y - self.tileWidth
            x = x * self.horScale
            y = y * self.horScale 
        #offset for heightcheck
        if mode == 1:
            if tile == 0:
                x = x
                y = y
            elif tile == 1:
                x = self.tileWidth - x
                y = y
            elif tile == 2:
                x = self.tileWidth - x
                y = self.tileWidth - y
            elif tile == 3:
                x = x
                y = self.tileWidth - y
        return x, y
    
    
    #vegmap to coord
    def vegMapToCoord(self, tileName):
        coord = []
        im = Image.open(self.inputFolder + tileName + "vegetationMap.png")
        
        if not 'transparency' in im.info:
            im = im.convert('RGBA')
        
        pix = im.load()
        
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                pixel = pix[x,y]
                coord.append([[x,y],pixel])
        return coord
    
    
    def getGroupDensity(self, tileName, x, y):
        im = Image.open(self.inputFolder + tileName + "densityMap.png")
        pix = im.load()
        pixel = pix[x,y]
        #convert to opposite, because black is considered 0 and we want black to be dense(255)
        return 255-pixel
    
    
    def createForestPatch(self, t, w, coord, tile, tileName, vegCoord):
        entityCount = 0
        for j, e in enumerate(coord):
            x = coord[j][0]
            y = coord[j][1]
            z = coord[j][2]
            
            if (y >= self.treeMinHeight and y <= self.treeMaxHeight):
                #creates forest-like treegroup tiles, if group has more than 1 tree
                group, name = self.createDynamicGroup(t, tileName, x, z, j, vegCoord, self.treesInGroup)
                
                #make sure a group was created
                if group: 
                    # y = 0 because createdynmesh aligns itself with 0 + height currently
                    self.addEntity(w, tile, tileName, "dynamicMesh", x, 0, z, name)
                    entityCount = entityCount + 1
                    
        print "Added " + str(entityCount) + " entities to " + tileName
        
    #Outputs entities to txml
    def addEntity(self, w, tile, tileName, type, x, y, z, meshName=""):
        #offset the entity coordinates to match the tile it should be on, adjust to scale
        x, z = self.locationOffset(tile, x, z)
        
        #preconfigured entity types
        if (type == "dynamicMesh"):
            name = type + meshName
            mesh = self.outputFolder + meshName + "dynamicGroup.mesh"
            material = self.treetex1 + ";" + self.treetex2 + ";" + self.treetex3
            modelAdjustment = 0
        
        elif (type == "single"):
            name = type + meshName
            mesh = self.tree1
            material = self.treetex1
            modelAdjustment = 0
            
        w.createEntity_Staticmesh(1, name, mesh=mesh,
                                    material=self.inputFolder + material,
                                    transform="%f,%f,%f,0,0,0,1,1,1" % (x, y+modelAdjustment, z))

    #Adds trees in the defined area and specifies their type
    def createDynamicGroup(self, t, tileName, x, z, groupId, vegCoord, entityAmount):
        name = tileName + str(groupId)
        print "Generating treegroup: " + name
        coord = []
        treeamount = 0
        
        #get density from group middle coord
        pixel = self.getGroupDensity(tileName,x,z)
        amount = float(entityAmount) * (float(pixel) / float(255))
        
        for j in range(int(amount)):
            _x = random.randint(-self.groupWidth/2, self.groupWidth/2)
            _z = random.randint(-self.groupWidth/2, self.groupWidth/2)
            adjustedX = _x+x
            adjustedZ = _z+z
            
            #make sure created object fits inside a tiles parameters, (otherwise we'll have floating trees)
            if (0 <= adjustedX <= self.tileWidth and 0 <= adjustedZ <= self.tileWidth):
                
                # only add trees if over red in vegmap
                # figure out the index where we want to check for trees
                i = adjustedX + adjustedZ * (self.tileWidth+8)
                
                # [index][x,y](R, G, B, a)
                if vegCoord[i][0] == [adjustedX, adjustedZ]:
                
                    #do nothing while on green or when opacity is 0
                    if not vegCoord[i][1][3] == 0:
                        if not (vegCoord[i][1][0] == 0 and 
                                vegCoord[i][1][1] == 255 and 
                                vegCoord[i][1][2] == 0):
                            y = t.getHeight(adjustedZ,adjustedX)
                            
                            #check list incase coords were generated below the minimum height for trees
                            if (y >= self.treeMinHeight and y <= self.treeMaxHeight):
                                #add to coord to be generated later
                                coord.append([[_x, y*self.verScale, _z], vegCoord[i][1]])
                                treeamount = treeamount+1
                                
        #amount of trees generated for testing purposes added to the groups name
        name = name +"_"+ str(int(treeamount))
        
        if len(coord) > 1:
            #create mesh
            self.createDynamicMesh(name, coord)
            return True, name
        else:
            #print "... No group needed for " + name + ", skipping"
            return False, name
    
    #creates .mesh.xml from createDynamicGroup
    def createDynamicMesh(self, name, coord):
        start = datetime.datetime.now()
        input = self.inputFolder + self.tree1
        output = self.outputFolder + name + "dynamicGroup.mesh.xml"
        
        mesh = MeshContainer.MeshContainer()
        meshio = MeshIO.MeshIO(mesh)
        #get base mesh from file, also adds a tree at 0,0
        meshio.fromFile(input, "model/x-ogremesh")
        mesh.toSharedgeometry()

        for i, e in enumerate(coord):
            #treetype from rgb
            input2 = self.chooseTreeType(coord, i)
            
            mesh2 = MeshContainer.MeshContainer()
            meshio2 = MeshIO.MeshIO(mesh2)
            meshio2.fromFile(input2, "model/x-ogremesh")
            mesh2.toSharedgeometry()
            
            x = coord[i][0][0] * self.horScale
            y = coord[i][0][1]
            z = coord[i][0][2] * self.horScale
            
            mesh2.translate(x, y, z)
            #mesh.rotate(0,0,0,0) # rotate
            #mesh.scale(2,2,2) # scale
            #add last object to the meshcontainer
            mesh.merge(mesh2, append=True)
        
        #output
        mesh.collapseSimilars()
        meshio.toFile(output, overwrite=True)
        # from .mesh.xml to .mesh
        self.compileDynamicMesh(output)
        
        stop = datetime.datetime.now()
        print "createDynamicMesh " + name + " Runtime: " + str(stop - start)
    
    
    def chooseTreeType(self, coord, i):
        trees = (self.tree1, self.tree2, self.tree3)
        #probability for each tree from rgb vegmap
        r = coord[i][1][0]
        g = coord[i][1][1]
        b = coord[i][1][2]
        #print "%i, %i, %i" % (r, g, b)
        type = [r / float(255), g / float(255), b / float(255)]
        
        weights = []
        for i, e in enumerate(type):
            if e != 0:
                weights.append(type[i])
                
        # weighted change for each type from the rgb values 255 = 100% change, 
        # r g b 255,255,255 = trees[0], because red 100%
        rnd = random.random() * sum(weights)
        for i, e in enumerate(weights):
            rnd -= e
            if rnd < 0:
                return self.inputFolder + trees[i]
    
    
    def compileDynamicMesh(self, input):
        compiler = "OgreXMLConverter.exe  -q "
        subprocess.Popen(compiler + input, shell=True)
        
        