#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import os

##########################################################################
# Class Material
#
class Material():
    def __init__(self, name):
        self.name = name
        self.techniques = []
        self.currenttechnique = None
        self.indent = 0

    ##########################################################################
    # Subclasses for the material definition
    # - Technique
    # - Pass
    # - TextureUnit
    #
    class Technique():
        def __init__(self, parentmaterial):
            self.parentmaterial = parentmaterial
            self.passes = []
            self.currentpass = None

        def addPass(self, p):
            self.passes.append(p)
            self.currentpass = p

        def addPassParameters(self, d):
            self.currentpass.addPassParameters(d)

        def addTextureunit(self, t):
            self.currentpass.addTextureunit(t)

        def addTextureunitParameters(self, d):
            self.currentpass.addTextureunitParameters(d)

        ##########################################################################
        # Technique output methods
        #
        def startTechnique(self):
            self.parentmaterial.writeMaterialString("technique")
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endTechnique(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputTechnique(self):
            for p in self.passes:
                p.startPass()
                p.outputPass()
                p.endPass()

    ##########################################################################
    # Pass Subclass
    #
    class Pass():
        def __init__(self, parentmaterial):
            self.parentmaterial = parentmaterial
            self.textureunits = []
            self.currentparams = {}

        def addPassParameters(self, d):
            valid = [ "ambient", "diffuse" ]
            for key, value in d.items():
                if key in valid:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Pass, but it is not a valid parameter" % key

        def addTextureunit(self, t_unit):
            self.textureunits.append(t_unit)
            self.currenttextureunit = t_unit

        def addTextureunitParameters(self, d):
            self.currenttextureunit.addTextureunitParameters(d)

        def startPass(self):
            self.parentmaterial.writeMaterialString("pass")
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endPass(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputPass(self):
            for key, value in self.currentparams.items():
                self.parentmaterial.writeMaterialString("%s %s" % (key, value))
            for t in self.textureunits:
                t.startTextureunit()
                t.outputTextureunit()
                t.endTextureunit()

    ##########################################################################
    # Textureunit Subclass
    #
    class Textureunit():
        def __init__(self, parentmaterial, name):
            self.parentmaterial = parentmaterial
            self.name = name
            self.currentparams = {}

        def addTextureunitParameters(self, d):
            valid = [ "wave_xform", "scroll_anim", "rotate_anim", "colour_op" ]
            for key, value in d.items():
                if key in valid:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Texture_unit, but it is not a valid parameter" % key

        def startTextureunit(self):
            self.parentmaterial.writeMaterialString("texture_unit")
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endTextureunit(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputTextureunit(self):
            self.parentmaterial.writeMaterialString("texture %s" % self.name)
            for key, value in self.currentparams.items():
                self.parentmaterial.writeMaterialString("%s %s" % (key, value))

    ##########################################################################
    # Material class private methods
    #
    def __startMaterial(self):
        self.writeMaterialString("material %s" % self.name)
        self.writeMaterialString("{")
        self.increaseIndent()

    def __endMaterial(self):
        self.decreaseIndent()
        self.writeMaterialString("}")

    def writeMaterialString(self, string):
        s = ""
        for i in range(self.indent): s += "   "
        self.file.write(s + string + "\n")

    def increaseIndent(self):
        self.indent += 1

    def decreaseIndent(self):
        self.indent -= 1

    ##########################################################################
    # Material generator API
    #
    def toFile(self, filename, overwrite=False):
        if os.path.exists(filename):
            if overwrite == False:
                sys.stderr.write("MaterialGenerator: ERROR: output file '%s' already exists!\n" % filename)
                return
            else:
                os.remove(filename)
        try: self.file = open(filename, "w")
        except IOError:
            sys.stderr.write("MaterialGenerator: ERROR: Unable to open file '%s' for writing!" % filename)
            return
        self.__startMaterial()
        for t in self.techniques:
            t.startTechnique()
            t.outputTechnique()
            t.endTechnique()
        self.__endMaterial()
        self.file.close()

    def addTechnique(self):
        t = Material.Technique(self)
        self.techniques.append(t)
        self.currenttechnique = t

    def addPass(self):
        p = Material.Pass(self)
        self.currenttechnique.addPass(p)

    def addPassParameters(self, d={}):
        self.currenttechnique.addPassParameters(d)

    def addTextureunit(self, name):
        t = Material.Textureunit(self, name)
        self.currenttechnique.addTextureunit(t)

    def addTextureunitParameters(self, d={}):
        self.currenttechnique.addTextureunitParameters(d)

    ##########################################################################
    # Material generator pre-defined macros for simple generation of certain
    # types of materials. Parameters in these macros are limited. If it seems
    # too restricting for you, then use the above API to generate more custom
    # materials
    #
    def createMaterial_Diffuseonly(self, name, diffusecolor="1.0 1.0 1.0"):
        self.reset()
        self.name = name
        m.addTechnique()
        m.addPass()
        m.addPassParameters({"diffuse":diffusecolor})

    def createMaterial_Textureonly(self, name, texture, diffusecolor="1.0 1.0 1.0", ambientcolor="0.5 0.5 0.5"):
        self.reset()
        self.name = name
        m.addTechnique()
        m.addPass()
        m.addPassParameters({"diffuse":diffusecolor, "ambient":ambientcolor})
        m.addTextureunit(texture)

##########################################################################
# Matrial unit testacse
#
if __name__ == "__main__":
    m = Material("testmaterial")
    m.addTechnique()
    m.addPass()
    m.addPassParameters({"ambient":"0.5 0.5 0.5", "diffuse":"1.0 1.0 1.0"})
    m.addTextureunit("image.png")
    m.addTextureunitParameters({"scroll_anim":"0.1 0.0", "wave_xform":"scale sine 0.0 0.7 0.0 1.0"})
    m.addTextureunit("wobbly.png")
    m.addTextureunitParameters({"rotate_anim":"0.25", "colour_op":"add"})
    m.toFile("./resources/testmaterial.material", overwrite=True)
    print "Done"
