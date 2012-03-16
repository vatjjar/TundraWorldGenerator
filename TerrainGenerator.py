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
# Terrain textual output methods
#

    def printmessage(self, message):
        sys.stdout.write(message + "\n")

    def printerror(self, message):
        sys.stderr.write("ERROR: " + str(message) + "\n")

#############################################################################
# Terrain file manipulators
#

    def fromFile(self, filename):
        if filename.endswith(".ntf"):
            return self.__fromNTFFile(filename)
        if filename.endswith(".asc"):
            return self.__fromASCFile(filename)
        return False

    def __fromNTFFile(self, filename):
        """ TerrainGenerator.__fromNTFFile(filename)
            - Loads a terrain definition from NTF file into internal table. File can then be further
              processed, with TerrainGenerator internal methods, or directly manipulating
              self.d_array table.
              Return value: True if file input succeeded, otherwise False
        """
        try: f = open(filename, "rb")
        except IOError: self.printerror("Requested file " + str(filename) + " does not exist."); return False

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

    def __fromASCFile(self, filename):
        """ TerrainGenerator.__fromASCFile(filename)
              Return value: True if file input succeeded, otherwise False
        """
        try: f = open(filename, "r")
        except IOError: self.printerror("Requested file %s does not exist." % filename); return False

        # first read the header
        line = f.readline()
        cols = int(line.split(" ")[-1].strip())
        line = f.readline()
        rows = int(line.split(" ")[-1].strip())
        f.readline()
        f.readline()
        f.readline()
        line = f.readline()
        novalue = float(line.split(" ")[-1].strip())

        if rows != cols:
            print "Warning: Importing ASCII data which is not square shaped!"

        # Setup the terrain
        self.initialize(((rows/self.cPatchSize)+1), ((cols/self.cPatchSize)+1))

        # Then loop through the file
        currentRow = 0
        currentCol = 0
        while 1:
            line = f.readline()
            if len(line) == 0: break
            t = line.split(" ")
            #print len(t)
            for c in range(len(t)-1):               # Last mark is linefeed, that is why -1
                value = float(t[c])
                if value == novalue: value = 0.0    # Zero for non-defined values
                self.d_array[currentRow][currentCol] = value
                currentRow += 1
                if currentRow == cols:
                    currentRow = 0
                    currentCol += 1
                    if currentCol == rows:
                        break                       # End of table reached
        return True

    def toFile(self, filename, overwrite=False):
        """ TerrainGenerator.toFile(filename):
            - tofile() writes the current terrain vector into file in a local filesystem. What ever is at the moment
              written in internal data table, is written to the file.
            - output file format is NTF, which is directly loadable by Tundra.
            Return value: True if generator succeeded, otherwise False
        """
        if os.path.exists(filename):
            if overwrite == False:
                self.printerror("Requested output file " + str(filename) + " already exists. Aborting.")
                return False
            os.remove(filename)
        try: f = open(filename, "wb")
        except IOError:
            self.printerror("Failed to open file " + str(filename) + ". Aborting!")
            return False

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

    def fromSurfaceImage(self, imagefile):
        """ TerrainGenerator.fromSurfaceImage(imagefile)
            - fromimage() takes an image file as an input, opens it with PIL, scales the content to match
              requested terrain size, and then uses the image as a height map to create the terrain
            - R, G and B values for each pixels are averaged and used as a height for each individual
              node in the terrain. The values are used directly, i.e. from zero to 255.
            Return value: True if file input succeeded, otherwise False
        """
        try: image = Image.open(imagefile)
        except IOError:
            self.printerror("File input from " + str(imagefile) + " failed. Aborting!")
            return False

        image2 = image.resize((self.width*self.cPatchSize, self.height*self.cPatchSize), Image.ANTIALIAS)
        pixels = image2.load()
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                self.d_array[i][j] = (pixels[i,j][0] + pixels[i,j][1] + pixels[i,j][2]) / 3.0
        self.minvalid = False
        self.maxvalid = False
        return True

    def toSurfaceImage(self, filename, fileformat="PNG", overwrite=False):
        """ TerrainGenerator.toSurfaceImage(imagefile)
            - toSurfaceMap() outputs the currently generated terrain into an RGB picture containing
              normalized height of each node in the terrain. Single pixel corresponds to single
              height value and is stored in grayscale RGB value. Height values are normalized to
              range of 0-255 before storing to gain maximum dynamics for the terrain.
            - RGB may be an overkill. Maybe single value grayscale image would be more elegant way
              to store the information
            Return value: True if file input succeeded, otherwise False
        """
        if os.path.exists(filename):
            if overwrite == False:
                self.printerror("Requested output file " + str(filename) + " already exists. Aborting.")
                return False
            os.remove(filename)

        image = Image.new("RGB", (self.width*self.cPatchSize, self.height*self.cPatchSize))

        data = []
        minitem = self.getMinitem()
        maxitem = self.getMaxitem()
        scalefactor = 255.0 / (maxitem - minitem)
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                # Here we need j,i orientation because PIL pixel orientation differs from our
                # internal presentation
                value = (self.d_array[j][i] - minitem) * scalefactor
                ivalue = int(value)
                data.append(ivalue*256*256 + ivalue*256 + ivalue)
        image.putdata(data)
        try: image.save(filename, fileformat)
        except IOError:
            self.printerror("toWeightmap() image save failed to " +str(filename)+ ". IOError.")
            return False
        return True

    def toWeightmap(self, filename, fileformat="TGA", overwrite=False):
        """ TerrainGenerator.toWeightmap(filename, fileformat)
            - toWeightmap() takes the current input terrain vector and creates a texture
              representing the surface texturing.
            - the algorithm runs through the vector and translates height values into RGB values
              where each RGB value acts as an input for the final terrain shader renderer.
            Return value: True always
        """
        if os.path.exists(filename):
            if overwrite == False:
                self.printerror("Requested output file " + str(filename) + " already exists. Aborting.")
                return False
            os.remove(filename)

        image = Image.new("RGB", (self.width*self.cPatchSize, self.height*self.cPatchSize))
        data = []
        maxitem = self.getMaxitem()
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                r, g, b = self.height_to_rgb(self.d_array[i][j], limit1=0.5, limit2=maxitem/2, variance=2)
                data.append(r*256*256 + g*256 + b)
        image.putdata(data)
        try: image.save(filename, fileformat)
        except IOError:
            self.printerror("toWeightmap() image save failed to " +str(filename)+ ". IOError.")
            return False
        return True

#############################################################################
# Terrain algorithms generator
#

    def fromDiamondsquare(self, size, seed1, seed2, seed3, seed4):
        """ TerrainGenerator.fromDiamondsquare(size, seed1, seed2, seed3, seed4)
            - fromdiamondsquare() implements an algorithm which can be used to create simple
              fractal based terrains. The algorithm is described in detail in:
              http://www.gameprogrammer.com/fractal.html
            - The algorithm will require a square shaped vector for storage space. Another
              requirement for the vector is that its dimensions need to be a power of two. The
              size of the terrain is at the moment limited to maximum of 128
            - seed[1-4] values are initial float corner values for the terrain and act as a seed
              for the generator.
            Return value: True if generator succeeded, otherwise False
        """
        if False == self.__sizeIsPowerOfTwo(size):
            return False;

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

    def fromEnvelope(self, size, envelope):
        """ TerrainGenerator.fromEnvelope(size, envelope)
            - fromEnvelope() method loops through the desired terrain array of floats
              and calls the envelope function for each node in the terrain soil to solve
              the particular height value.
            - Current X and Y coordinates are passed as a parameter to the envelope function
              which can then be used by what ever algorithm to determine the height value
            - Both envelope params are floats and it is assumed that the envelope returns
              a float, which is used directly-
            - input params for the envelope are mapped to [-1, 1] for both X and Y directions
              hence the envelope can assume all input X,Y pairs to fall into this area.
            Return value: True if generator succeeded, otherwise False
        """
        if False == self.__sizeIsPowerOfTwo(size):
            return False;

        self.initialize(size, size)
        w = size*self.cPatchSize
        h = w

        for i in range(h):
            for j in range(w):
                self.d_array[j][i] = envelope(float(2.0*i/(h-1)-1.0), float(2.0*j/(h-1)-1.0))
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
        minitem = self.getMinitem()
        maxitem = self.getMaxitem()
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                self.d_array[i][j] = (self.d_array[i][j]-minitem) * (maxlimit-minlimit)/(maxitem-minitem) + minlimit
        self.minitem = minlimit
        self.maxitem = maxlimit
        self.minvalid = True
        self.maxvalid = True
        return True

    def adjustHeight(self, delta):
        for i in range(self.width*self.cPatchSize):
            for j in range(self.height*self.cPatchSize):
                self.d_array[i][j] += delta

    def quantize(self, level=16):
        """ TerrainGenerator.quantize(level)
            - quantize() algorithm quantizes the currently generated terrain to number of levels defined by the
              input parameter. Currenly implemented algorithms are generating continuous terrains, but sometimes
              there is a need to split the data into levels, i.e. quantize it.
            - Input parameter level tells into how many levels the current terrain need to be quantized.
            Return value: True always
        """
        minitem = self.getMinitem()
        maxitem = self.getMaxitem()
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

    def __sizeIsPowerOfTwo(self, size):
        sizeispoweroftwo = False
        for i in (1, 2, 4, 8, 16, 32, 64, 128):
            if size == i: return True
        if sizeispoweroftwo == False:
            self.printerror("Size is not a power of Two or exceed 128")
            return False

    def getMinitem(self):
        """ TerrainGenerator.getMinitem()
            - getMinitem() is a helper method which will seek the current minimum value from
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

    def getMaxitem(self):
        """ TerrainGenerator.getMaxitem()
            - getMaxitem() is a helper method which will seek the current maximum value from
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

    def getHeight(self, x, y):
        """ TerrainGenerator.getHeight(x, y)
            - getHeight() returns the current height value from requested node.
            - input taken as x,y coordinate pair to the 2-dimensional terrain vector.
            Return value: True if successful, otherwise False
        """
        return self.d_array[x][y]

    def height_to_rgb(self, height, limit1=0.5, limit2=35.0, variance=2):
        """ TerrainGenerator.height_to_rgb(maxitem, height)
            - height_to_rgb() translates given height value into RGB value with certain thresholds
            - the implementation of this method is merely a test without proper intelligence. Only
              purpose primarily is to test mapping of terrain shape into terrain surface textures.
            - will be rewritten soon..
            Return value: translated R, G and B values
        """
        if height < float(random.randint(int(limit1-variance), int(limit1+variance))):
            return 0, 0, 255
        elif height < float(random.randint(int(limit2-variance), int(limit2+variance))):
            return 0, 255, 0
        else:
            return 255, 0, 0

#############################################################################

if __name__ == "__main__":
    # If run standalone, we will run a bunch of test cases

    terrain = TerrainGenerator(16,16)

    print "Running input/output test"
    terrain.fromFile("./resources/terrain.ntf")
    terrain.toFile("./resources/terrain2.ntf", overwrite=True)

    print "Running terrain-from-image with rescaling test"
    terrain.fromSurfaceImage("./resources/map.png")
    terrain.rescale(-20, 50)
    terrain.quantize(8)
    terrain.toFile("./resources/terrain3.ntf", overwrite=True)
    terrain.toSurfaceImage("./resources/terrainsurfaceimage.png", fileformat="PNG", overwrite=True)

    print "Running diamond-square with rescale & saturate + generating weightmap"
    terrain.fromDiamondsquare(2, 10, -5, -5, 10)
    terrain.rescale(-20, 50)
    terrain.saturate(-5)
    terrain.toFile("./resources/terrain4.ntf", overwrite=True)
    terrain.toWeightmap("./resources/terrainweights.tga", fileformat="TGA", overwrite=True)

    print "Done!"
