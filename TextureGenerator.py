#!/usr/bin/python

import sys, os, io
import array
import random
import numpy
from math import *
from PIL import Image

class TextureGenerator():
    """ class TextureGenerator():
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

    def fromimage(self, imagefile):
        try:
            image = Image.open(imagefile)
            imagesize = image.size
            print "image x,y %d,%d" % (imagesize[0], imagesize[1])
            pixels = image.load()
        except IOError:
            return False
        self.initialize(imagesize[0], imagesize[1])
        for i in range(imagesize[0]):
            for j in range(imagesize[1]):
                self.r_array[i][j] = pixels[i,j][0]
                self.g_array[i][j] = pixels[i,j][1]
                self.b_array[i][j] = pixels[i,j][2]
        return True

    def toimage(self, filename, fileformat="TGA"):
        #print "Creating %s" % filename
        if os.path.exists(filename):
            #print "Deleting old file!"
            os.remove(filename)
        f = open(filename, "wb")
        image = Image.new("RGB", (self.width, self.height))
        data = []
        for i in range(self.width):
            for j in range(self.height):
                r, g, b = self.data_to_rgb(i, j)
                data.append(b*256*256 + g*256 + r)
        #print len(data)
        image.putdata(data)
        image.save(filename, fileformat)

    def create_singlecolortexture(self, r, g, b, variance):
        for i in range(self.width):
            for j in range(self.height):
                var = random.randint(-variance/2, variance/2)
                _r = r + var
                _g = g + var
                _b = b + var
                self.rgb_to_data(i, j, _r, _g, _b)

#############################################################################

    def data_to_rgb(self, x, y):
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

    def rgb_to_data(self, x, y, r, g, b):
        self.r_array[x][y] = float(r)
        self.g_array[x][y] = float(g)
        self.b_array[x][y] = float(b)

#############################################################################

if __name__ == "__main__": # if run standalone
    texture = TextureGenerator(512, 512)

    texture.create_singlecolortexture(30,100,30,50)
    texture.toimage("./blender-export/generated_grass.png", "PNG")
    texture.create_singlecolortexture(90,83,73,50)
    texture.toimage("./blender-export/generated_stone.png", "PNG")
    texture.create_singlecolortexture(160,136,88,70)
    texture.toimage("./blender-export/generated_sand.png", "PNG")
