import settings
import binaryReader as br
import numpy as np
import ntpath

class bwm():
	""" A Black and White Model class """
	def __init__(self, file, textures = settings.locations["Textures"]):
		self.filename = file
		self.name = ntpath.basename(file)

class bwMesh():
	""" A Black and White mesh """

# Material relevant classes: bwImage and bwMaterial
class bwImage():
	""" Stores a single texture file """
	def __init__(self,file,alignment="neut",type=None):
    	#Save file information
		self.path = file
		self.name = ntpath.basename(file)
		self.type = type
		self.alignment = alignment

		#Attempt to open the file, test for if the file can be found
		f = open(file,"r")
		self.found = False
		if(f != False):
			self.found = True
		f.close()

class bwMaterial():
	def __init__(self,diffuse=None,light=None,foliage=None,specular=None,fire=None,normal=None,type=None):
		self.diffuse = bwImage(diffuse,type="diffuse")
		self.diffuseGood, self.diffuseEvil = self.searchForAlignmentFiles(diffuse)
		self.light = bwImage(light,type="lightmap")
		self.lightGood, self.lightEvil = self.searchForAlignmentFiles(light,"light")
		self.foliage = bwImage(foliage,type="foliage")
		self.foliageGood, self.foliageEvil = self.searchForAlignmentFiles(foliage,"foliage")
		self.specular = bwImage(specular,type="specularmap")
		self.specularGood, self.specularEvil = self.searchForAlignmentFiles(specular,"specularmap")
		self.fire = bwImage(fire,type="fire")
		self.fireGood, self.fireEvil = self.searchForAlignmentFiles(fire,"fire")
		self.normal = bwImage(normal,type="normalmap")
		self.type = type

	def searchForAlignmentFiles(self,file,type="diffuse"):
		""" Takes a file and attempts to locate good and evil varients """
		#Get name of the file
		dir, name = ntpath.split(file)
		#Alignment is identified by the use of the terms: neut, good, and evil.
		#Other aspects of the file name includes t_<tribe>_<object>_<align>_<extension>
		#Some texture types have an extra item it:
		#	specular is spc
		#	lightmap is lightmap
		#	normal is nrm

		#Locating the needed files is quite simple, just replace "neut" with "good" or "evil"
		evilName = name.replace("neut","evil")
		goodName = name.replace("neut","good")

		#Check if they exist
		goodFile = dir + goodName
		evilFile = dir + evilName
		f = open(goodFile,"r")
		if(f != False):
			goodTexture = bwImage(goodFile,"good",type)
		else:
			goodTexture = None
		f.close()

		f = open(evilFile,"r")
		if(f != False):
			evilTexture = bwImage(evilFile,"good",type)
		else:
			evilTexture = None
		f.close()

		return goodTexture, evilTexture

#Lower level classes
class bwPoint():
	""" Single point in bw format (x,y,z) """
	def __int__(self,x,y,z):
		self.x = x
		self.y = y
		self.z = z

	def __init__(self,file):
		self.x = br.readFloat(file)
		self.y = br.readFloat(file)
		self.z = br.readFloat(file)

	def writePoint(self,file):
		br.writeFloat(file,self.x)
		br.writeFloat(file,self.y)
		br.writeFloat(file,self.z)

def main():
	m = bwm("diff.bwm")
	print(m)

if __name__ == '__main__':
	main()
