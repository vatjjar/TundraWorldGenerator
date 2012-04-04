#!/usr/bin/python
#
# Author: Jarkko Vatjus-Anttila <jvatjusanttila@gmail.com>
#
# For conditions of distribution and use, see copyright notice in license.txt
#

import os
import sys

##########################################################################
# Class MaterialContainer
#
class MaterialContainer():
    def __init__(self):
        self.reset()

    def reset(self):
        self.materials = []

    def addMaterial(self, material):
        self.materials.append(material)

    def getMaterials(self):
        return self.materials

    def toFile(self, filename, overwrite=False, append=True, LOD=5):
        for m in self.materials:
            m.toFile(filename, overwrite=overwrite, append=append, LOD=LOD)

    def fromFile(self, filename):
        self.reset()
        try: f = open(filename, "r")
        except IOError:
            print "MeshContainer: Error opening file %s" % filename
            return
        material = None
        lastObject = ""
        while 1:
            line = f.readline()
            if len(line) == 0: break
            l = line.strip().split(" ")
            try: key = l[0]
            except IOError: continue
            try: name = l[1].strip()
            except IndexError: name = ""

            if key == "material":
                material = Material(l[1])
                self.materials.append(material)
                lastObject = key
            elif key == "technique":
                material.addTechnique(name)
                lastObject = key
            elif key == "pass":
                material.addPass(name)
                lastObject = key
            elif key == "vertex_program_ref":
                material.addVertexprogram(name)
                lastObject = key
            elif key == "fragment_program_ref":
                material.addFragmentprogram(name)
                lastObject = key
            elif key == "texture_unit":
                material.addTextureunit(name)
                lastObject = key
            elif key == "{": pass
            elif key == "}":
                lastObject = ""
            elif key.startswith("//"): pass
            else:
                # regular parameters into last defined unit
                d = { key:" ".join(l[1:]) }
                if lastObject == "pass":
                    material.addPassParameters(d)
                elif lastObject == "material":
                    material.addMaterialParameters(d)
                elif lastObject == "technique":
                    material.addTechniqueParameters(d)
                elif lastObject == "texture_unit":
                    material.addTextureunitParameters(d)
                elif lastObject == "fragment_program_ref":
                    material.addFragmentprogramParameters(d)
                elif lastObject == "vertex_program_ref":
                    material.addVertexprogramParameters(d)

##########################################################################
# Class Material
#
class Material():
    def __init__(self, name):
        self.reset(name)

    def reset(self, name):
        self.name = name
        self.techniques = []
        self.currenttechnique = None
        self.indent = 0
        self.currentparams = {}
        self.lod1_params = [ ]
        self.lod2_params = [ ]
        self.lod3_params = [ ]
        self.lod4_params = [ ]
        self.lod5_params = [ "receive_shadows" ]
        self.all_params  = " ".join(self.lod1_params)
        self.all_params += (" " + " ".join(self.lod2_params))
        self.all_params += (" " + " ".join(self.lod3_params))
        self.all_params += (" " + " ".join(self.lod4_params))
        self.all_params += (" " + " ".join(self.lod5_params))

    ##########################################################################
    # Subclasses for the material definition
    # - Technique
    # - Pass
    # - TextureUnit
    # - Vertexshader
    # - Fragmentshader
    #
    class Technique():
        def __init__(self, parentmaterial, name=""):
            self.parentmaterial = parentmaterial
            self.passes = []
            self.currentpass = None
            self.name = name
            self.currentparams = {}
            self.lod1_params = [ ]
            self.lod2_params = [ ]
            self.lod3_params = [ ]
            self.lod4_params = [ ]
            self.lod5_params = [ ]
            self.all_params  = " ".join(self.lod1_params)
            self.all_params += (" " + " ".join(self.lod2_params))
            self.all_params += (" " + " ".join(self.lod3_params))
            self.all_params += (" " + " ".join(self.lod4_params))
            self.all_params += (" " + " ".join(self.lod5_params))

        def addPass(self, p):
            self.passes.append(p)
            self.currentpass = p

        def addPassParameters(self, d):
            self.currentpass.addPassParameters(d)

        def addTextureunit(self, t):
            self.currentpass.addTextureunit(t)

        def addTextureunitParameters(self, d):
            self.currentpass.addTextureunitParameters(d)

        def addVertexprogram(self, vp):
            self.currentpass.addVertexprogram(vp)

        def addVertexprogramParameters(self, d):
            self.currentpass.addVertexprogramParameters(d)

        def addFragmentprogram(self, fp):
            self.currentpass.addFragmentprogram(fp)

        def addFragmentprogramParameters(self, d):
            self.currentpass.addFragmentprogramParameters(d)

        def addTechniqueParameters(self, d):
            for key, value in d.items():
                if key == "": continue # Suppress cosmetic warning
                if key in self.all_params:
                    self.currentparams[key] = value
                else:
                    print "Warning: Trying to set param '%s' for current Technique, but it is not a valid parameter" % key

        ##########################################################################
        # Technique output methods
        #
        def startTechnique(self):
            self.parentmaterial.writeMaterialString("technique %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endTechnique(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputTechnique(self, LOD=5):
            valid = " ".join(self.lod1_params)
            if LOD >= 2: valid += (" " + " ".join(self.lod2_params))
            if LOD >= 3: valid += (" " + " ".join(self.lod3_params))
            if LOD >= 4: valid += (" " + " ".join(self.lod4_params))
            if LOD >= 5: valid += (" " + " ".join(self.lod5_params))
            for key, value in self.currentparams.items():
                if key in valid:
                    self.parentmaterial.writeMaterialString("%s %s" % (key, value))
            for p in self.passes:
                p.startPass()
                p.outputPass(LOD=LOD)
                p.endPass()

    ##########################################################################
    # Pass Subclass
    #
    class Pass():
        def __init__(self, parentmaterial, name=""):
            self.name = name
            self.parentmaterial = parentmaterial
            self.textureunits = []
            self.vertexprograms = []
            self.fragmentprograms = []
            self.currentparams = {}
            self.currenttextureunit = None
            self.currentvertexprogram = None
            self.currentfragmentprogram = None
            self.lod1_params = [ "ambient", "diffuse", "cull_hardware", "depth_check", "depth_func", "colour_write" ]
            self.lod2_params = [ "specular", "emissive", "polygon_mode", "shading", "alpha_to_coverage" ]
            self.lod3_params = [ "scene_blend", "depth_write", "transparent_sorting", "illumination_stage" ]
            self.lod4_params = [ "lighting", "alpha_rejection", "iteration", "scene_blend_op", "normalise_normals" ]
            self.lod5_params = [ "cull_software", "fog_override", "light_scissor", "light_clip_planes" ]
            self.all_params  = " ".join(self.lod1_params)
            self.all_params += (" " + " ".join(self.lod2_params))
            self.all_params += (" " + " ".join(self.lod3_params))
            self.all_params += (" " + " ".join(self.lod4_params))
            self.all_params += (" " + " ".join(self.lod5_params))

        def addPassParameters(self, d):
            for key, value in d.items():
                if key == "": continue # Suppress cosmetic warning
                if key in self.all_params:
                    self.currentparams[key] = value
                else:
                    print "Warning: Trying to set param '%s' for current Pass, but it is not a valid parameter" % key

        def addTextureunit(self, t_unit):
            self.textureunits.append(t_unit)
            self.currenttextureunit = t_unit

        def addTextureunitParameters(self, d):
            self.currenttextureunit.addTextureunitParameters(d)

        def addVertexprogram(self, vp):
            self.vertexprograms.append(vp)
            self.currentvertexprogram = vp

        def addVertexprogramParameters(self, d):
            self.currentvertexprogram.addVertexprogramParameters(d)

        def addFragmentprogram(self, fp):
            self.fragmentprograms.append(fp)
            self.currentfragmentprogram = fp

        def addFragmentprogramParameters(self, d):
            self.currentfragmentprogram.addFragmentprogramParameters(d)

        def startPass(self):
            self.parentmaterial.writeMaterialString("pass %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endPass(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputPass(self, LOD=5):
            valid = " ".join(self.lod1_params)
            if LOD >= 2: valid += (" " + " ".join(self.lod2_params))
            if LOD >= 3: valid += (" " + " ".join(self.lod3_params))
            if LOD >= 4: valid += (" " + " ".join(self.lod4_params))
            if LOD >= 5: valid += (" " + " ".join(self.lod5_params))
            for key, value in self.currentparams.items():
                if key in valid:
                    self.parentmaterial.writeMaterialString("%s %s" % (key, value))
            for vp in self.vertexprograms:
                vp.startVertexprogram()
                vp.outputVertexprogram(LOD=LOD)
                vp.endVertexprogram()
            for fp in self.fragmentprograms:
                fp.startFragmentprogram()
                fp.outputFragmentprogram(LOD=LOD)
                fp.endFragmentprogram()
            for t in self.textureunits:
                t.startTextureunit()
                t.outputTextureunit(LOD=LOD)
                t.endTextureunit()

    ##########################################################################
    # Vertexprogram Subclass
    #
    class Vertexprogram():
        def __init__(self, parentmaterial, name=""):
            self.name = name
            self.parentmaterial = parentmaterial
            self.currentparams = {}
            self.lod1_params = [ "param_named", "param_named_auto" ]
            self.lod2_params = [ ]
            self.lod3_params = [ ]
            self.lod4_params = [ ]
            self.lod5_params = [ ]
            self.all_params  = " ".join(self.lod1_params)
            self.all_params += (" " + " ".join(self.lod2_params))
            self.all_params += (" " + " ".join(self.lod3_params))
            self.all_params += (" " + " ".join(self.lod4_params))
            self.all_params += (" " + " ".join(self.lod5_params))

        def addVertexprogramParameters(self, d):
            for key, value in d.items():
                if key == "": continue # Suppress cosmetic warning
                if key in self.all_params:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Vertexprogram, but it is not a valid parameter" % key

        def startVertexprogram(self):
            self.parentmaterial.writeMaterialString("vertex_program_ref %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endVertexprogram(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputVertexprogram(self, LOD=5):
            valid = " ".join(self.lod1_params)
            if LOD >= 2: valid += (" " + " ".join(self.lod2_params))
            if LOD >= 3: valid += (" " + " ".join(self.lod3_params))
            if LOD >= 4: valid += (" " + " ".join(self.lod4_params))
            if LOD >= 5: valid += (" " + " ".join(self.lod5_params))
            for key, value in self.currentparams.items():
                if key in valid:
                    self.parentmaterial.writeMaterialString("%s %s" % (key, value))

    ##########################################################################
    # Fragmentprogram Subclass
    #
    class Fragmentprogram():
        def __init__(self, parentmaterial, name=""):
            self.name = name
            self.parentmaterial = parentmaterial
            self.currentparams = {}
            self.lod1_params = [ "param_named", "param_named_auto" ]
            self.lod2_params = [ ]
            self.lod3_params = [ ]
            self.lod4_params = [ ]
            self.lod5_params = [ ]
            self.all_params  = " ".join(self.lod1_params)
            self.all_params += (" " + " ".join(self.lod2_params))
            self.all_params += (" " + " ".join(self.lod3_params))
            self.all_params += (" " + " ".join(self.lod4_params))
            self.all_params += (" " + " ".join(self.lod5_params))

        def addFragmentprogramParameters(self, d):
            for key, value in d.items():
                if key == "": continue # Suppress cosmetic warning
                if key in self.all_params:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Fragmentprogram, but it is not a valid parameter" % key

        def startFragmentprogram(self):
            self.parentmaterial.writeMaterialString("fragment_program_ref %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endFragmentprogram(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputFragmentprogram(self, LOD=5):
            valid = " ".join(self.lod1_params)
            if LOD >= 2: valid += (" " + " ".join(self.lod2_params))
            if LOD >= 3: valid += (" " + " ".join(self.lod3_params))
            if LOD >= 4: valid += (" " + " ".join(self.lod4_params))
            if LOD >= 5: valid += (" " + " ".join(self.lod5_params))
            for key, value in self.currentparams.items():
                if key in valid:
                    self.parentmaterial.writeMaterialString("%s %s" % (key, value))

    ##########################################################################
    # Textureunit Subclass
    #
    class Textureunit():
        def __init__(self, parentmaterial, name=""):
            self.parentmaterial = parentmaterial
            self.name = name
            self.currentparams = {}
            self.lod1_params = [ "texture", "texture_alias", "content_type", "scale" ]
            self.lod2_params = [ "wave_xform", "colour_op", "tex_coord_set" ]
            self.lod3_params = [ "tex_address_mode", "filtering", "cubic_texture" ]
            self.lod4_params = [ "rotate_anim", "cubic_texture" ]
            self.lod5_params = [ "scroll_anim", "alpha_op_ex", "colour_op_ex", "env_map" ]
            self.all_params  = " ".join(self.lod1_params)
            self.all_params += (" " + " ".join(self.lod2_params))
            self.all_params += (" " + " ".join(self.lod3_params))
            self.all_params += (" " + " ".join(self.lod4_params))
            self.all_params += (" " + " ".join(self.lod5_params))

        def addTextureunitParameters(self, d):
            for key, value in d.items():
                if key == "": continue # Suppress cosmetic warning
                if key in self.all_params:
                    self.currentparams[key] = value
                else:
                    print "Trying to set param '%s' for current Texture_unit, but it is not a valid parameter" % key

        def startTextureunit(self):
            self.parentmaterial.writeMaterialString("texture_unit %s" % self.name)
            self.parentmaterial.writeMaterialString("{")
            self.parentmaterial.increaseIndent()

        def endTextureunit(self):
            self.parentmaterial.decreaseIndent()
            self.parentmaterial.writeMaterialString("}")

        def outputTextureunit(self, LOD=5):
            valid = " ".join(self.lod1_params)
            if LOD >= 2: valid += (" " + " ".join(self.lod2_params))
            if LOD >= 3: valid += (" " + " ".join(self.lod3_params))
            if LOD >= 4: valid += (" " + " ".join(self.lod4_params))
            if LOD >= 5: valid += (" " + " ".join(self.lod5_params))
            for key, value in self.currentparams.items():
                if key in valid:
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
    def toFile(self, filename, overwrite=False, append=False, LOD=5):
        if os.path.exists(filename):
            if overwrite == False and append == False:
                sys.stderr.write("MaterialGenerator: ERROR: output file '%s' already exists!\n" % filename)
                return
            elif overwrite == True:
                os.remove(filename)
        filemode = "w"
        if append == True: filemode = "a"
        try: self.file = open(filename, filemode)
        except IOError:
            sys.stderr.write("MaterialGenerator: ERROR: Unable to open file '%s' for writing!" % filename)
            return

        self.__startMaterial()
        valid = " ".join(self.lod1_params)
        if LOD >= 2: valid += (" " + " ".join(self.lod2_params))
        if LOD >= 3: valid += (" " + " ".join(self.lod3_params))
        if LOD >= 4: valid += (" " + " ".join(self.lod4_params))
        if LOD >= 5: valid += (" " + " ".join(self.lod5_params))
        for key, value in self.currentparams.items():
            if key in valid:
                self.writeMaterialString("%s %s" % (key, value))

        for t in self.techniques:
            t.startTechnique()
            t.outputTechnique(LOD=LOD)
            t.endTechnique()
        self.__endMaterial()
        self.file.close()

    def addMaterialParameters(self, d):
        for key, value in d.items():
            if key == "": continue # Suppress cosmetic warning
            if key in self.all_params:
                self.currentparams[key] = value
            else:
                print "Warning: Trying to set param '%s' for current Material, but it is not a valid parameter" % key

    def addTechnique(self, name=""):
        t = Material.Technique(self, name=name)
        self.techniques.append(t)
        self.currenttechnique = t

    def addTechniqueParameters(self, d={}):
        self.currenttechnique.addTechniqueParameters(d)

    def addPass(self, name=""):
        p = Material.Pass(self)
        self.currenttechnique.addPass(p)

    def addPassParameters(self, d={}):
        self.currenttechnique.addPassParameters(d)

    def addTextureunit(self, name=""):
        t = Material.Textureunit(self, name=name)
        self.currenttechnique.addTextureunit(t)

    def addTextureunitParameters(self, d={}):
        self.currenttechnique.addTextureunitParameters(d)

    def addVertexprogram(self, name=""):
        vp = Material.Vertexprogram(self, name=name)
        self.currenttechnique.addVertexprogram(vp)

    def addVertexprogramParameters(self, d={}):
        self.currenttechnique.addVertexprogramParameters(d)

    def addFragmentprogram(self, name=""):
        fp = Material.Fragmentprogram(self, name=name)
        self.currenttechnique.addFragmentprogram(fp)

    def addFragmentprogramParameters(self, d={}):
        self.currenttechnique.addFragmentprogramParameters(d)

    ##########################################################################
    # Material generator pre-defined macros for simple generation of certain
    # types of materials. Parameters in these macros are limited. If it seems
    # too restricting for you, then use the above API to generate more custom
    # materials
    #
    def createMaterial_Diffuseonly(self, name, diffusecolor="1.0 1.0 1.0"):
        self.reset(name)
        self.addTechnique()
        self.addPass()
        self.addPassParameters({"diffuse":diffusecolor})

    def createMaterial_Textureonly(self, name, texture, diffusecolor="1.0 1.0 1.0", ambientcolor="0.5 0.5 0.5"):
        self.reset(name)
        self.addTechnique()
        self.addPass()
        self.addPassParameters({"diffuse":diffusecolor, "ambient":ambientcolor})
        self.addTextureunit(texture)

    def createMaterial_4channelTerrain(self, name, t1, t2, t3, t4, weightmap):
        self.reset(name)
        self.addTechnique("TerrainPCF")
        self.addPass()
        self.addPassParameters({"ambient":"0.0 0.0 0.0 1.0"})
        self.addVertexprogram("Rex/TerrainPCFVS_weighted")
        self.addFragmentprogram("Rex/TerrainPCFFS_weighted")
        self.addTextureunit("weights")
        self.addTextureunitParameters({"texture_alias":"weights", "texture":weightmap})
        self.addTextureunit("detail0")
        self.addTextureunitParameters({"texture_alias":"detail0", "texture":t1})
        self.addTextureunit("detail1")
        self.addTextureunitParameters({"texture_alias":"detail1", "texture":t2})
        self.addTextureunit("detail2")
        self.addTextureunitParameters({"texture_alias":"detail2", "texture":t3})
        self.addTextureunit("detail3")
        self.addTextureunitParameters({"texture_alias":"detail3", "texture":t4})
        self.addTextureunit("shadowMap0")
        self.addTextureunitParameters({"texture_alias":"shadowMap0", "tex_address_mode":"clamp", "content_type":"shadow"})
        self.addTextureunit("shadowMap1")
        self.addTextureunitParameters({"texture_alias":"shadowMap1", "tex_address_mode":"clamp", "content_type":"shadow"})
        self.addTextureunit("shadowMap2")

##########################################################################
# Material unit testacase
#
if __name__ == "__main__":
    m = Material("testmaterial")
    m.addTechnique()
    m.addPass()
    m.addPassParameters({"ambient":"0.5 0.5 0.5", "diffuse":"1.0 1.0 1.0"})
    m.addTextureunit()
    m.addTextureunitParameters({"texture":"image.png", "scroll_anim":"0.1 0.0", "wave_xform":"scale sine 0.0 0.7 0.0 1.0"})
    m.addTextureunit()
    m.addTextureunitParameters({"texture":"wobbly.png", "rotate_anim":"0.25", "colour_op":"add"})
    m.toFile("./resources/testmaterial.material", overwrite=True)

    m.createMaterial_4channelTerrain("terrainsample", "weight.png", "t1.png", "t2.png", "t3.png", "t4.png")
    m.toFile("./resources/4channelterrainsample.material", overwrite=True)
    m.createMaterial_Diffuseonly("diffuse")
    m.toFile("./resources/diffuseonly.material", overwrite=True)
    m.createMaterial_Textureonly("textureonly", "tex.png")
    m.toFile("./resources/textureonly.material", overwrite=True)

    mc = MaterialContainer()
    mc.fromFile("./resources/terrainsample.material")
    mc.toFile("./resources/terrainsample2.material", overwrite=True, append=True, LOD=5)
    mc.fromFile("./resources/twinmaterial.material")
    mc.toFile("./resources/twinmaterial2.material", overwrite=False, append=True, LOD=5)
    print "Done"
