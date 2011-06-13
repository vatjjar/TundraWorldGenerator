#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os, io
import array
import random
import numpy
from math import *
from PIL import Image

class TerrainGenerator():
    """ class TerrainGenerator():
        - TerrainGenerator is a general purpose NTF file generator which can output files
          suitable for Tundra Terrain importer. The class can open existing NTF files for
          modification, as well as write NTF files for Tundra usage. Internally the data
          is presented as 2-dimensional float array.
        - Optionally content of the terrain can be read from an image file. Image file
          can be of anything that Python Imaging Library supports. Image is treated as
          heightmap based on pixel color and the information is used to directly feed
          height information into float matrix.
        - Dependencies are Python Imaging Library (PIL), array module and NumPy
    """

    def __init__(self, width=16, height=16):
        """ TerrainGenerator.__init__(width, height):
            - Initializes the class and makes reservation for the terrain table.
            - cPatchSize is fixed to 16, as the same hardcoding is used within Tundra. This
              script works with other patch sizes as well, but resulted output is no longer
              supported by Tundra. Hence, it is recommended to leave the value fixed.
            Return value: None
        """
        self.cPatchSize = 16
        self.initialize(width, height)

    def initialize(self, width=16, height=16):
        """ TerrainGenerator.initialize(width, height):
            - Makes memory allocation for the terrain table. Default size for the table is
              16x16. The units correspond to terrain patches, which are 16x16 floats in size.
              Hence, the default terrain size will be 256*256 units in tundra world.
            - Note that +1 is added to each dimension in the table. This is because of the
              diamondsquare terrain generator, which requires one additional row and column
              in the table. Maybe a proper initialization to allocate extra space ONLY
              when diamondsquare would be in use, but at the moment this will do.
              Return value: True
        """
        self.width = width
        self.height = height
        self.minitem = 0
        self.maxitem = 0
        self.maxvalid = False
        self.minvalid = False
        self.d_array = numpy.zeros([width*self.cPatchSize+1,height*self.cPatchSize+1], dtype=float)
        return True

#############################################################################
# Terrain file manipulators
#

    def fromfile(self, filename):
        """ TerrainGenerator.fromfile(filename)
            - Loads a terrain definition from NTF file into internal table. File can then be further
              processed, with TerrainGenerator internal methods, or directly manipulating
              self.d_array table.
              Return value: True if file input succeeded, otherwise False
        """
        if not os.path.exists(filename):
            print "File open failed!"
            return False
        f = open(filename, "rb")
        size_buf = array.array("I")
        size_buf.fromfile(f, 2)
        l = size_buf.tolist()
        self.initialize(l[0], l[1])
        for i in range(self.width):
            for j in range(self.height):
                d_buf = array.array("f")
                d_buf.fromfile(f, self.cPatchSize*self.cPatchSize)
                l = d_buf.tolist()
                for x in range(self.cPatchSize):
                    for y in range(self.cPatchSize):
                        self.d_array[i*self.cPatchSize+x][j*self.cPatchSize+y] = l[x*self.cPatchSize+y]
        f.close()
        self.minvalid = False
        self.maxvalid = False
        return True

    def tofile(self, filename):
        """ TerrainGenerator.tofiles(filename):
            - tofile() writes the current terrain vector into file in a local filesystem. What ever is at the moment
              written in internal data table, is written to the file.
            - output file format is NTF, which is directly loadable by Tundra.
            Return value: True if generator succeeded, otherwise False
        """
        if os.path.exists(filename):
            os.remove(filename)
        f = open(filename, "wb")
        s_buf = array.array("I")
        s_buf.fromlist([self.width, self.height])
        s_buf.tofile(f)
        for i in range(self.width):
            for j in range(self.height):
                d_patch = []
                for x in range(self.cPatchSize):
                    for y in range(self.cPatchSize):
                        d_patch.append(self.d_array[i*self.cPatchSize+x][j*self.cPatchSize+y])
                d_buf = array.array("f")
                d_buf.fromlist(d_patch)
                d_buf.tofile(f)
        f.close()
        return True

    def fromimage(self, imagefile):
        """ TerrainGenerator.fromimage(imagefile)
            - fromimage() takes an image file as an input, opens it with PIL, scales the content to match
              requested terrain size, and then uses the image as a height map to create the terrain
            - R, G and B values for each pixels are averaged and used as a height for each individual
              node in the terrain.
            Return value: True if file input succeeded, otherwise False
        """
        try:
            image = Image.open(imagefile)
            image2 = image.resize((self.width*self.cPatchSize, self.height*self.cPatchSize), Image.ANTIALIAS)
            pixels = image2.load()
        except IOError:
            return False
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                self.d_array[i][j] = (pixels[i,j][0] + pixels[i,j][1] + pixels[i,j][2]) / 3.0
        self.minvalid = False
        self.maxvalid = False
        return True

#############################################################################
# Terrain algorithms generator
#

    def fromdiamondsquare(self, size, seed1, seed2, seed3, seed4):
        """ TerrainGenerator.fromdiamondsquare(size, seed1, seed2, seed3, seed4)
            - fromdiamondsquare() implements an algorithm which can be used to create simple
              fractal based terrains. The algorithm is described in detail in:
              http://www.gameprogrammer.com/fractal.html
            - The algorithm will require a square shaped vector for storage space. Another
              requirement for the vector is that its dimensions need to be power of two. The
              size of the terrain is at the moment limited to maximum of 128
            - seed[1-4] values are initial float corner values for the terrain and act as a seed
              for the generator.
            Return value: True if generator succeeded, otherwise False
        """
        sizeispoweroftwo = False
        for i in (1, 2, 4, 8, 16, 32, 64, 128):
            if size == i:
                sizeispoweroftwo = True
                break
        if sizeispoweroftwo == False:
            print "Size is not a power of Two or exceed 128"
            return False
        self.initialize(size, size)
        w = size*self.cPatchSize
        h = w
        self.d_array[0][0] = float(seed1)
        self.d_array[w][0] = float(seed2)
        self.d_array[0][h] = float(seed3)
        self.d_array[w][h] = float(seed4)
        #print "%d %d %d %d" % (self.d_array[0][0], self.d_array[w][0], self.d_array[0][h], self.d_array[w][h])
        divider = 1
        randrange = 32
        while divider < w:
            blocksize = w/divider
            for i in range(divider):
                for j in range(divider):
                    # Square phase:
                    value =         self.d_array[(i+0)*blocksize][(j+0)*blocksize]
                    value = value + self.d_array[(i+1)*blocksize][(j+0)*blocksize]
                    value = value + self.d_array[(i+0)*blocksize][(j+1)*blocksize]
                    value = value + self.d_array[(i+1)*blocksize][(j+1)*blocksize]
                    value = value / 4.0 + float(random.randint(-randrange, randrange))
                    self.d_array[i*blocksize+blocksize/2][j*blocksize+blocksize/2] = value
                    # Diamond phase:
                    value =         self.d_array[(i+0)*blocksize][(j+0)*blocksize]
                    value = value + self.d_array[(i+1)*blocksize][(j+0)*blocksize]
                    value = value / 2.0 + float(random.randint(-randrange, randrange))
                    self.d_array[i*blocksize+blocksize/2][j*blocksize] = value
                    value =         self.d_array[(i+0)*blocksize][(j+0)*blocksize]
                    value = value + self.d_array[(i+0)*blocksize][(j+1)*blocksize]
                    value = value / 2.0 + float(random.randint(-randrange, randrange))
                    self.d_array[i*blocksize][j*blocksize+blocksize/2] = value
                    value =         self.d_array[(i+0)*blocksize][(j+1)*blocksize]
                    value = value + self.d_array[(i+1)*blocksize][(j+1)*blocksize]
                    value = value / 2.0 + float(random.randint(-randrange, randrange))
                    self.d_array[i*blocksize+blocksize/2][j*blocksize+blocksize] = value
                    value =         self.d_array[(i+1)*blocksize][(j+0)*blocksize]
                    value = value + self.d_array[(i+1)*blocksize][(j+1)*blocksize]
                    value = value / 2.0 + float(random.randint(-randrange, randrange))
                    self.d_array[i*blocksize+blocksize][j*blocksize+blocksize/2] = value
            divider = divider * 2
            randrange = randrange / 2
        self.minvalid = False
        self.maxvalid = False
        return True

#############################################################################
# Terrain shape manipulator algorithms
#

    def rescale(self, minlimit, maxlimit):
        """ TerrainGenerator.rescale(minlimit, maxlimit)
            - rescale() operation runs through the current terrain vector and rescales all values between
              parameters given for the method. The algorithm does a simple linear scaling for terrain to
              force it into certain numerical range.
            Return value: True always
        """
        minitem = self.get_minitem()
        maxitem = self.get_maxitem()
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                self.d_array[i][j] = (self.d_array[i][j]-minitem) * (maxlimit-minlimit)/(maxitem-minitem) + minlimit
        self.minitem = minlimit
        self.maxitem = maxlimit
        self.minvalid = True
        self.maxvalid = True
        return True

    def quantize(self, level=16):
        """ TerrainGenerator.quantize(level)
            - quantize() algorithm quantizes the currently generated terrain to number of levels defined by the
              input parameter. Currenly implemented algorithms are generating continuous terrains, but sometimes
              there is a need to split the data into levels, i.e. quantize it.
            - Input parameter level tells into how many levels the current terrain need to be quantized.
            Return value: True always
        """
        minitem = self.get_minitem()
        maxitem = self.get_maxitem()
        threshold = (maxitem-minitem)/level
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                self.d_array[i][j] = value = floor((self.d_array[i][j]-minitem)/threshold) * threshold + minitem
        return True

    def saturate(self, level):
        """ TerrainGenerator.saturate(level)
            - saturate() methods does either negative of positive saturation for the currently generated terrain.
              If a negative level is passed as input then all negative values are saturated . If the input is
              positive then all positive numbers are saturated.
            Return value: True always
        """
        if level > 0: # positive saturation
            for i in range(self.width*self.cPatchSize):
                for j in range(self.height*self.cPatchSize):
                    if self.d_array[i][j] > level:
                        self.d_array[i][j] = level
            self.maxitem = level
            self.maxvalid = True
        else:
            for i in range(self.width*self.cPatchSize):
                for j in range(self.height*self.cPatchSize):
                    if self.d_array[i][j] < level:
                        self.d_array[i][j] = level
            self.minitem = level
            self.minvalid = True
        return True

#############################################################################
# Terrain helper methods
#

    def get_minitem(self):
        """ TerrainGenerator.get_minitem()
            - get_minitem() is a helper method which will seek the current minimum value from
              the terrain vector. Its purpose is to act as a helper method for the actual algorithms
            - the actual value is cached and invalidated when seen fit. This is to speed up
              algorithms which take a heavy use of this method.
            Return value: float representing the minvalue of the current terrain vector
        """
        if self.minvalid == True:
            return self.minitem
        self.minitem = 10000
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                if self.d_array[i][j] < self.minitem:
                    self.minitem = self.d_array[i][j]
        self.minvalid = True
        return self.minitem

    def get_maxitem(self):
        """ TerrainGenerator.get_maxitem()
            - get_maxitem() is a helper method which will seek the current maximum value from
              the terrain vector. Its purpose is to act as a helper method for the actual algorithms
            - the actual value is cached and invalidated when seen fit. This is to speed up
              algorithms which take a heavy use of this method.
            Return value: float representing the maxvalue of the current terrain vector
        """
        if self.maxvalid == True:
            return self.maxitem
        self.maxitem = -10000
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                if self.d_array[i][j] > self.maxitem:
                    self.maxitem = self.d_array[i][j]
        self.maxvalid = True
        return self.maxitem

    def get_height(self, x, y):
        """ TerrainGenerator.get_height(x, y)
            - get_height() returns the current height value from requested node.
            - input taken as x,y coordinate pair to the 2-dimensional terrain vector.
            Return value: True if successful, otherwise False
        """
        return self.d_array[x][y]

    def height_to_rgb(self, maxitem, height):
        """ TerrainGenerator.height_to_rgb(maxitem, height)
            - height_to_rgb() translates given height value into RGB value with certain thresholds
            - the implementation of this method is merely a test without proper intelligence. Only
              purpose primarily is to test mapping of terrain shape into terrain surface textures.
            - will be rewritten soon..
            Return value: translated R, G and B values
        """
        if height < 0.5: # Sand brown
            return 0, 0, 255
        elif height < float(random.randint(maxitem/2-2, maxitem/2+2)): # grass
            return 0, 255, 0
        else: # gray rocks
            return 255, 0, 0

    def create_weightmap(self, filename, fileformat="TGA"):
        """ TerrainGenerator.create_weightmap(filename, fileformat)
            - create_weightmap() takes the current input terrain vector and creates a texture
              representing the surface texturing.
            - the algorithm runs through the vector and translates height values into RGB values
              where each RGB value acts as an input for the final terrain shader renderer.
            Return value: True always
        """
        if os.path.exists(filename):
            os.remove(filename)
        f = open(filename, "wb")
        image = Image.new("RGB", (self.width*self.cPatchSize, self.height*self.cPatchSize))
        data = []
        maxitem = self.get_maxitem()
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                r, g, b = self.height_to_rgb(maxitem, self.d_array[i][j])
                data.append(r*256*256 + g*256 + b)
        image.putdata(data)
        image.save(filename, fileformat)
        return True

#############################################################################

if __name__ == "__main__": # if run standalone
    # If run standalone, we will run a bunch of test cases

    terrain = TerrainGenerator(16, 16)

    print "Running input/output test"
    terrain.fromfile("./resources/terrain.ntf")
    terrain.tofile("./resources/terrain2.ntf")

    print "Running terrain-from-image with rescaling test"
    terrain.fromimage("./resources/map.png")
    terrain.rescale(-20, 50)
    terrain.quantize(8)
    terrain.tofile("./resources/terrain3.ntf")

    print "Running diamond-square with rescale & saturate + generating weightmap"
    terrain.fromdiamondsquare(32, 10, -5, -5, 10)
    terrain.rescale(-20, 50)
    terrain.saturate(-5)
    terrain.tofile("./resources/terrain4.ntf")
    terrain.create_weightmap("./resources/terrainweights.tga")

    print "Done!"