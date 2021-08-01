import settings
import binaryReader as br
import numpy as np
import ntpath

import bwMaterial

class bwm:
	""" A Black and White Model class """

	geometries = property( lambda s: s.funct1, lambda s,v: s.funct2(v), doc="""A list of :class:`collada.geometry.Geometry` objects. Can also be indexed by id""" )
	
	def __init__(self, file, textures = ""): #settings.locations["Textures"]
		self.filename = file
		self.name = ntpath.basename(file)

	def funct1(self):
		return self.filename

	def funct2(self,file):
		self.filename = file

class bwMesh:
	""" A Black and White mesh """
	#def __init__(self,file,textures):

class bwMeshMaterial:	
	""" A mesh reference to a material """
	def __init__(self,ref,sIndices,indices,sVertices,vertices,sFaces,faces,unknown):
		self.material = ref
		self.indexStart = sIndices
		self.indexCount = indices
		self.vertexStart = sVertices
		self.vertexCount = vertices
		self.faceStart = sFaces
		self.faceCount = faces
		self.unknown = unknown
	
	#def addFaces():

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
	settings.init()
	m = bwm("diff.bwm")
	print(m)

if __name__ == '__main__':
	main()
