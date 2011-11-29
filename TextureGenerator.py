#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import sys, os, io
import random
import numpy
import math

from PIL import Image

class TextureGenerator():
    """ class TextureGenerator(): A collection of procedural methods for
        creating texture files with various content.
        Uses Python Imaging Library for image I/O
    """

    def __init__(self, width=256, height=256):
        """ TextureGenerator.__init__(width, height):
        """
        self.initialize(width, height)

    def initialize(self, width=256, height=256):
        """ TextureGenerator.initialize(width, height):
        """
        self.width = width
        self.height = height
        self.r_array = numpy.zeros([width,height], dtype=float)
        self.g_array = numpy.zeros([width,height], dtype=float)
        self.b_array = numpy.zeros([width,height], dtype=float)
        return True

#############################################################################
# Texture textual output methods
#

    def printmessage(self, message):
        sys.stdout.write(message + "\n")

    def printerror(self, message):
        sys.stderr.write("ERROR: " + str(message) + "\n")

#############################################################################
# Image I/O
#

    def fromImage(self, imagefile):
        """ TextureGenerator.fromImage(self, imagefile):
        """
        try: image = Image.open(imagefile)
        except IOError:
            self.printerror("File "+str(filename)+" open failed. Aborting");
            return False

        imagesize = image.size
        self.printmessage("image x,y %d,%d" % (imagesize[0], imagesize[1]))

        pixels = image.load()
        self.initialize(imagesize[0], imagesize[1])
        for i in range(imagesize[0]):
            for j in range(imagesize[1]):
                self.r_array[i][j] = pixels[i,j][0]
                self.g_array[i][j] = pixels[i,j][1]
                self.b_array[i][j] = pixels[i,j][2]
        return True

    def toImage(self, filename, fileformat="TGA", overwrite=False):
        """ TextureGenerator.toImage(self, filename, fileformat="TGA", overwrite=False):
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

        image = Image.new("RGB", (self.width, self.height))
        data = []
        for i in range(self.width):
            for j in range(self.height):
                r, g, b = self.__data_to_rgb(i, j)
                data.append(b*256*256 + g*256 + r)

        image.putdata(data)
        image.save(filename, fileformat)
        return True

    def createSingleColorTexture(self, r, g, b, variance):
        """ TextureGenerator.createSingleColorTexture(self, r, g, b, variance):
        """
        for i in range(self.width):
            for j in range(self.height):
                var = random.randint(-variance/2, variance/2)
                _r = r + var
                _g = g + var
                _b = b + var
                self.__rgb_to_data(i, j, _r, _g, _b)

#############################################################################
# Internal methods, primarily for testing for the time being
#
    def __data_to_rgb(self, x, y):
        r = int(self.r_array[x][y])
        if r < 0:   r = 0
        if r > 255: r = 255
        g = int(self.g_array[x][y])
        if g < 0:   g = 0
        if g > 255: g = 255
        b = int(self.b_array[x][y])
        if b < 0:   b = 0
        if b > 255: b = 255
        return r, g, b

    def __rgb_to_data(self, x, y, r, g, b):
        self.r_array[x][y] = float(r)
        self.g_array[x][y] = float(g)
        self.b_array[x][y] = float(b)

#############################################################################
# Standalone test case
#

if __name__ == "__main__": # if run standalone
    texture = TextureGenerator(128, 128)

    print "Generating grass texture..."
    texture.createSingleColorTexture(30,100,30,50)
    texture.toImage("./resources/generated_grass.png", "PNG", overwrite=True)
    print "Generating stone texture..."
    texture.createSingleColorTexture(90,83,73,50)
    texture.toImage("./resources/generated_stone.png", "PNG", overwrite=True)
    print "Generating sand texture..."
    texture.createSingleColorTexture(160,136,88,70)
    texture.toImage("./resources/generated_sand.png", "PNG", overwrite=True)
