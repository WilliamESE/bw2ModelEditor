#import binaryReader as br
import numpy as np
import ntpath

import bwModel
import bwMaterial

class bwMesh:
	"""  """
	def __init__(self):
		"""  """

class bwMeshInteraction:
    def __init__(self, points = []):
        self.points = points

    def getPoint(self, x):
        return self.points[x]

    def setPoint(self, x, point):
        self.point[x] = point

class bwMaterialRef:
	def __init__(self,ref = None,sIndices = None,indices = None,sVertices = None,vertices = None,sFaces = None,faces = None,unknown = None):
		self.materialRef = ref
		self.material = None
		self.indexStart = sIndices
		self.indexCount = indices
		self.vertexStart = sVertices
		self.vertexCount = vertices
		self.faceStart = sFaces
		self.faceCount = faces
		self.unknown = unknown

	@property
	def material(self):
		return self.material
	@material.setter
	def material(self,material = None):
		self.material = material

	def readMaterialRef(self, file):
		self.materialRef = br.readUInt32(file)
		self.indexStart = br.readUInt32(file)
		self.indexCount = br.readUInt32(file)
		self.vertexStart = br.readUInt32(file)
		self.vertexCount = br.readUInt32(file)
		self.faceStart = br.readUInt32(file)
		self.faceCount = br.readUInt32(file)
		self.unknown = br.readUInt32(file)

	def writeMaterialRef(self,file):
		br.writeUInt32(file,self.materialRef)
		br.writeUInt32(file,self.indexStart)
		br.writeUInt32(file,self.indexCount)
		br.writeUInt32(file,self.vertexStart)
		br.writeUInt32(file,self.vertexCount)
		br.writeUInt32(file,self.faceStart)
		br.writeUInt32(file,self.faceCount)
		br.writeUInt32(file,self.unknown)