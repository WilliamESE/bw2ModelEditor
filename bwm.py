import array,sys,time,os
import re
import numpy as np
import struct
import ntpath

class bwm():	
	def __init__(self):
		self.m = {}
		
		
	def loadFromFile(self,filename):
		self.fln = filename
		self.f = open(self.fln, "rb")
		
		#--Header Section--
		#File identification
		fileId = self.readString(20)
		if(fileId != "LiOnHeAdMODEL"):
			return 0
		self.m["Id"] = fileId
		
		#27 byte gap
		self.f.seek(self.f.tell()+26)
		
		#File Size
		self.m["Size"] = self.readUInt32()
		#Magic Number
		self.m["MagicNum"] = self.readUInt32()
		if(self.m["MagicNum"] != 0x2B00B1E5):
			return 1
		
		#Model Type
		self.m["Type"] = self.readInt32()
		if((self.m["Type"] != 5)and(self.m["Type"] != 6)):
			return 2
		
		#Stride Position
		self.m["SdePos"] = self.readInt32()
		
		#Model Information
		self.m["Unknown1"] = self.readFloat() 		# This value is generally close to 0 - but cannot be 0 otherwise the game fails to display the model correctly. No other values cause any visible changes in the game
		self.m["Unknown2"] = self.readLHPoint() 	# A point on the model, purpose is unknown. Y value is generally zero, suggesting a point on the ground. When changed no visible changes could be observed. Mathimatically no connection with other points in the header could be found.
		self.m["BoxPoint1"] = self.readLHPoint()	# A corner of the object
		self.m["BoxPoint2"] = self.readLHPoint() 	# The opposite corner of the object
		self.m["Center"] = self.readLHPoint() 		# This point is generally close to zero, probably an offset for building center. Box values observed for gate houses would suggest this.
		
		self.m["Height"] = self.readFloat()			# Total height of the model
		self.m["Radius"] = self.readFloat()			# Radius of the model, used for path creation
		
		self.m["Unknown3"] = self.readFloat()		# Usually 1 or 2, rarely 0 - not tech level (gate houses are all 1 regardless of tech level)
		self.m["Volume"] = self.readFloat()
		
		#Model File Contents
		self.m["cntMaterials"] = self.readInt32()
		self.m["cntMeshs"] = self.readInt32()
		self.m["cntBones"] = self.readInt32()
		self.m["hasJoints"] = False
		if(self.m["cntBones"] != 0):
			self.m["hasJoints"] = True
		self.m["cntEntities"] = self.readInt32()
		self.m["cntUnknown1"] = self.readInt32()	# I suspect these have something to do with construction [verified false] - Matt commented "circle foot prints", which I have come to understand as incorrect through viewing the points in 3D modelling software
		self.m["cntUnknown2"] = self.readInt32()	#
		
		#Some unknown information
		self.m["UnknownF1"] = self.readFloat()		# Not a clue, attempted to set them all 0, which there were no observable changes in game
		self.m["UnknownF2"] = self.readFloat()
		self.m["UnknownF3"] = self.readFloat()
		self.m["UnknownF4"] = self.readFloat()
		self.m["Unknown4"] = self.readInt32()
		
		#Model Frame Info
		self.m["cntVerticies"] = self.readInt32()
		self.m["cntStrides"] = self.readInt32()
		self.m["Unknown5"] = self.readInt32()		# 120 (*((_DWORD *)v75[66] + 30) = 2;)
		self.m["cntIndices"] = self.readInt32()
		
		#--Header End--
		#--Material Definitions--
		self.m["Materials"] = []
		for x in range(self.m["cntMaterials"]):
			self.m["Materials"].append(self.readMaterialDefinition())
		
		#--Mesh Descriptions--
		self.m["Meshs"] = []
		for x in range(self.m["cntMeshs"]):
			self.m["Meshs"].append(self.readMeshDescription())
		
		for m in range(self.m["cntMeshs"]):
			self.m["Meshs"][m]["Materials"] = []
			for x in range(self.m["Meshs"][m]["cntMaterials"]):
				self.m["Meshs"][m]["Materials"].append(self.readMestMaterialReference())
				
		#Bones
		self.m["Bones"] = []
		for b in range(self.m["cntBones"]):
			self.m["Bones"].append(self.readBone())
		
		#Entities
		self.m["Entities"] = []
		for b in range(self.m["cntEntities"]):
			self.m["Entities"].append(self.readEntity())
		
		#Unknown1
		self.m["Un1"] = []
		for b in range(self.m["cntUnknown1"]):
			self.m["Un1"].append(self.readLHPoint())
		
		#Unknown2
		self.m["Un2"] = []
		for b in range(self.m["cntUnknown2"]):
			self.m["Un2"].append(self.readLHPoint())
		
		#We begin to get into some of the real unknowns here
		# There seems to be this unknown section section of data prior to the model data all of which are integers
		# The stride pointer points to the 21st integer
		self.m["VertexSize"] = self.readVertexSize()
		
		self.m["Stride"] = []
		print(self.f.tell())
		print(self.m["SdePos"])
		strLen = [23,34,34,34,34,34,34,34,34]
		for s in range(self.m["cntStrides"]):
			self.m["Stride"].append(self.readStride(strLen[s]))
		print(self.f.tell())
		#Verticies
		self.m["Vertices"] = []
		for x in range(self.m["cntVerticies"]):
			v = self.readVertex()
			self.m["Vertices"].append(v)
				
		if(self.m["hasJoints"] == True):
			self.m["Matrices"] = {}
			self.m["Matrices"]["Connection"] = []
			self.m["Matrices"]["Weight_0"] = []
			self.m["Matrices"]["Weight_1"] = []
			self.m["Matrices"]["Weight_2"] = []
			self.m["Matrices"]["Weight_3"] = []
			
			for x in range(0,self.m["cntVerticies"]):
				self.m["Matrices"]["Connection"].append(self.readJointConnections())
				
			for x in range(0,self.m["cntVerticies"]):
				self.m["Matrices"]["Weight_0"].append(self.readFloat())
			
			for x in range(0,self.m["cntVerticies"]):
				self.m["Matrices"]["Weight_1"].append(self.readFloat())
			
			for x in range(0,self.m["cntVerticies"]):
				self.m["Matrices"]["Weight_2"].append(self.readFloat())
			
			for x in range(0,self.m["cntVerticies"]):
				self.m["Matrices"]["Weight_3"].append(self.readFloat())
		
		print(self.f.tell())	
		#Indices
		self.m["Indices"] = []
		for x in range(self.m["cntIndices"]):
			val = self.readInt16()
			self.m["Indices"].append(val)
			
		print(self.f.tell())
		#Cleaves
		if(self.m["Type"] == 6):
			self.m["cntCleaves"] = self.readInt32()			
			self.m["Cleaves"] = []
			for x in range(self.m["cntCleaves"]):
				try:
					self.m["Cleaves"].append(self.readLHPoint())
				except:
					self.f.close()
					return 5
			
		self.f.close()
		return 3
	
	#-------------------Conversion and Saving-------------------	
	def savebwm(self):
		bw = open(self.fln, "wb+")
		
		self.writeString(bw,"LiOnHeAdMODEL")
		
		#Padding
		for x in range(27):
			self.writeUInt8(bw,0)
		
		#File size will be filled in later so place zero there for now
		flsize = bw.tell()
		self.writeUInt32(bw,0)
		
		#Magic number
		self.writeUInt32(bw,0x2B00B1E5)
		
		#Type - TODO: I've have to figure out how to differentiate the two types
		self.writeUInt32(bw,self.m["Type"])
		
		#Stride position
		flstride = bw.tell()
		self.writeUInt32(bw,0) #set to zero for now
		
		#Model details
		self.writeFloat(bw,self.m["Unknown1"])
		self.writeLHPoint(bw,self.m["Unknown2"])
		self.writeLHPoint(bw,self.m["BoxPoint1"])
		self.writeLHPoint(bw,self.m["BoxPoint2"])
		self.writeLHPoint(bw,self.m["Center"])
		
		self.writeFloat(bw,self.m["Height"])
		self.writeFloat(bw,self.m["Radius"])
		self.writeFloat(bw,self.m["Unknown3"])
		self.writeFloat(bw,self.m["Volume"])
		
		self.writeUInt32(bw,len(self.m["Materials"]))
		self.writeUInt32(bw,self.m["cntMeshs"])
		self.writeUInt32(bw,self.m["cntBones"])
		self.writeUInt32(bw,len(self.m["Entities"]))
		self.writeUInt32(bw,len(self.m["Un1"]))
		self.writeUInt32(bw,len(self.m["Un2"]))
		
		self.writeFloat(bw,self.m["UnknownF1"])
		self.writeFloat(bw,self.m["UnknownF2"])
		self.writeFloat(bw,self.m["UnknownF3"])
		self.writeFloat(bw,self.m["UnknownF4"])
		self.writeUInt32(bw,self.m["Unknown4"])
		
		self.writeUInt32(bw,self.m["cntVerticies"])
		self.writeUInt32(bw,self.m["cntStrides"])
		self.writeUInt32(bw,self.m["Unknown5"])
		self.writeUInt32(bw,self.m["cntIndices"])
		
		#Material Definitions
		for mat in self.m["Materials"]:
			self.writeMaterialDefinition(bw,mat)
			
		#--Mesh Descriptions--
		for mesh in self.m["Meshs"]:
			self.writeMeshDescription(bw,mesh)
		
		for mesh in self.m["Meshs"]:
			for mat in mesh["Materials"]:
				self.writeMestMaterialReference(bw,mat)
				
		#Bones
		for bone in self.m["Bones"]:
			self.writeBone(bw,bone)
		
		#Entities
		for ent in self.m["Entities"]:
			self.writeEntity(bw,ent)
		
		#Unknown1
		for unk in self.m["Un1"]:
			self.writeLHPoint(bw,unk)
		
		#Unknown2
		for unk in self.m["Un2"]:
			self.writeLHPoint(bw,unk)
		
		#Stride			
		self.writeVertexSize(bw,self.m["VertexSize"])
		
		#Unknown data
		for s in range(len(self.m["Stride"])):
			self.writeStride(bw,self.m["Stride"][s])
			
		hold = bw.tell() #Store the current location
		stLoca = hold - 56 #Update this number
		bw.seek(flstride) #Go to stride pointer
		self.writeUInt32(bw,stLoca)
		bw.seek(hold) #return to the stride unknown values
			
		#Verticies
		for vert in self.m["Vertices"]:
			self.writeVertex(bw,vert)
			
		if(self.m["hasJoints"] == True):			
			for x in range(0,self.m["cntVerticies"]):
				self.writeJointConnections(bw,self.m["Matrices"]["Connection"][x])
				
			for x in range(0,self.m["cntVerticies"]):
				self.writeFloat(bw,self.m["Matrices"]["Weight_0"][x])
			
			for x in range(0,self.m["cntVerticies"]):
				self.writeFloat(bw,self.m["Matrices"]["Weight_1"][x])
			
			for x in range(0,self.m["cntVerticies"]):
				self.writeFloat(bw,self.m["Matrices"]["Weight_2"][x])
			
			for x in range(0,self.m["cntVerticies"]):
				self.writeFloat(bw,self.m["Matrices"]["Weight_3"][x])
			
		#Indices
		for ind in self.m["Indices"]:
			self.writeUInt16(bw,ind)
			
		#Cleaves
		if(self.m["Type"] == 6):
			self.writeUInt32(bw,self.m["cntCleaves"])
			for cle in self.m["Cleaves"]:
				self.writeLHPoint(bw,cle)
				
		filesize = bw.tell() - 44
		bw.seek(flsize)
		self.writeUInt32(bw,filesize)
		
		bw.close()
		print("Saved")
		
	#--------------------General Editing Functions--------------------
	def getEntities(self):
		return self.m["Entities"]
	
	def addEntity(self,entity):
		self.m["Entities"].append(entity)
		self.m["cntEntities"] += 1
	
	def removeEntity(self, index):
		del self.m["Entities"][index]
		self.m["cntEntities"] -= 1
		
	#-------------------High level reading functions-------------------
	def readMaterialDefinition(self):
		#A list of strings each is 64 bytes maximum
		#	Thus the reading will have to read in a string then jump to the next one.
		#	64 - len(string)
		#Items: DiffuseMap, LightMap, FoliageMap, SpecularMap, FireMap, NormalMap, Type
		material = {}
		material["DiffuseMap"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["DiffuseMap"])))
		material["LightMap"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["LightMap"])))
		material["FoliageMap"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["FoliageMap"])))
		material["SpecularMap"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["SpecularMap"])))
		material["FireMap"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["FireMap"])))
		material["NormalMap"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["NormalMap"])))
		material["Type"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(material["Type"])))
		
		return material
		
	def writeMaterialDefinition(self,f,mat):
		self.writeString(f,mat["DiffuseMap"])
		f.seek(f.tell()+(64-len(mat["DiffuseMap"])))
		self.writeString(f,mat["LightMap"])
		f.seek(f.tell()+(64-len(mat["LightMap"])))
		self.writeString(f,mat["FoliageMap"])
		f.seek(f.tell()+(64-len(mat["FoliageMap"])))
		self.writeString(f,mat["SpecularMap"])
		f.seek(f.tell()+(64-len(mat["SpecularMap"])))
		self.writeString(f,mat["FireMap"])
		f.seek(f.tell()+(64-len(mat["FireMap"])))
		self.writeString(f,mat["NormalMap"])
		f.seek(f.tell()+(64-len(mat["NormalMap"])))
		self.writeString(f,mat["Type"])
		f.seek(f.tell()+(64-len(mat["Type"])))
		
		
	def readMeshDescription(self):
		mesh = {}
		mesh["cntFaces"] = self.readInt32()
		mesh["offIndices"] = self.readInt32()
		
		mesh["cntIndices"] = self.readInt32()
		mesh["offVertices"] = self.readInt32()	# or Cleaves - These only appear in version 6 and always has the same amount of vertices
		mesh["cntVertices"] = self.readInt32()	# or Cleaves
		
		#List of points
		mesh["Points"] = []
		for x in range(9):
			mesh["Points"].append(self.readLHPoint())
			
		#More info
		mesh["Unknown1"] = self.readUInt32()
		mesh["Volume"] = self.readFloat()
		mesh["cntMaterials"] = self.readUInt32()
		mesh["Unknown3"] = self.readUInt32()
		mesh["Unknown4"] = self.readUInt32() # In the granery the values are 1,1,1,2,2,2,3,3,3,4,4,4 [Some sort of ID system]
		
		#Name
		mesh["Name"] = self.readString(64)
		self.f.seek(self.f.tell()+(63-len(mesh["Name"])))
		
		#Unknowns
		mesh["Unknown5"] = self.readInt32()
		mesh["Unknown6"] = self.readInt32()
		
		return mesh
		
	def writeMeshDescription(self,f,mesh):
		#Initial Data
		self.writeUInt32(f,mesh["cntFaces"])
		self.writeUInt32(f,mesh["offIndices"])
		self.writeUInt32(f,mesh["cntIndices"])
		self.writeUInt32(f,mesh["offVertices"])
		self.writeUInt32(f,mesh["cntVertices"])
		#Points
		for pnt in mesh["Points"]:
			self.writeLHPoint(f,pnt)
			
		#Data
		self.writeUInt32(f,mesh["Unknown1"])
		self.writeFloat(f,mesh["Volume"])
		self.writeUInt32(f,mesh["cntMaterials"])
		self.writeUInt32(f,mesh["Unknown3"])
		self.writeUInt32(f,mesh["Unknown4"])
		#Name
		self.writeString(f,mesh["Name"])
		f.seek(f.tell()+(64-len(mesh["Name"])))
		#Last set
		self.writeUInt32(f,mesh["Unknown5"])
		self.writeUInt32(f,mesh["Unknown6"])
			
		
	def readMestMaterialReference(self):
		ref = {}
		ref["MaterialRef"] = self.readInt32()
		ref["offIndices"] = self.readInt32()
		ref["cntIndices"] = self.readInt32()
		ref["offVertex"] = self.readInt32()
		ref["cntVertex"] = self.readInt32()
		ref["offFaces"] = self.readInt32()
		ref["cntFaces"] = self.readInt32()
		ref["Unknown"] = self.readInt32()	#Appears to be the same across models decreasing across the material references, from 331535 -> 3855 / 3854 -> 15 -> 5 (These values are the only ones observed acorss several model files)
		return ref
		
	def writeMestMaterialReference(self,f,ref):
		self.writeUInt32(f,ref["MaterialRef"])
		self.writeUInt32(f,ref["offIndices"])
		self.writeUInt32(f,ref["cntIndices"])
		self.writeUInt32(f,ref["offVertex"])
		self.writeUInt32(f,ref["cntVertex"])
		self.writeUInt32(f,ref["offFaces"])
		self.writeUInt32(f,ref["cntFaces"])
		self.writeUInt32(f,ref["Unknown"])
	
	def readBone(self):
		bone = {}
		bone["P1"] = self.readLHPoint() #Rotation?
		bone["P2"] = self.readLHPoint() #Translation?
		bone["P3"] = self.readLHPoint() #Scale?
		bone["Position"] = self.readLHPoint() #Position
		return bone
		
	def writeBone(self,f,bone):
		self.writeLHPoint(f,bone["P1"])
		self.writeLHPoint(f,bone["P2"])
		self.writeLHPoint(f,bone["P3"])
		self.writeLHPoint(f,bone["Position"])
		
	def readJointConnections(self):
		conn = []
		conn.append(self.readInt8())
		conn.append(self.readInt8())
		conn.append(self.readInt8())
		conn.append(self.readInt8())
		return conn
		
	def writeJointConnections(self,f,conn):
		self.writeInt8(f,conn[0])
		self.writeInt8(f,conn[1])
		self.writeInt8(f,conn[2])
		self.writeInt8(f,conn[3])
		
	def readEntity(self):
		ent = {}
		ent["Unknown1"] = self.readLHPoint()
		ent["Unknown2"] = self.readLHPoint()
		ent["Unknown3"] = self.readLHPoint()
		ent["Position"] = self.readLHPoint()
		ent["Name"] = self.readString(256)
		self.f.seek(self.f.tell()+(255-len(ent["Name"])))
		
		return ent
		
	def writeEntity(self,f,ent):
		self.writeLHPoint(f,ent["Unknown1"])
		self.writeLHPoint(f,ent["Unknown2"])
		self.writeLHPoint(f,ent["Unknown3"])
		self.writeLHPoint(f,ent["Position"])
		self.writeString(f,ent["Name"])
		f.seek(f.tell()+(256-len(ent["Name"])))
	
	def readVertex(self):
		vertex = {}
		for sz in self.m["VertexSize"]["Items"]:
			if(sz["Enabled"]):
				if((sz["Type"] == "Position") or (sz["Type"] == "Normal")):
					vertex[sz["Type"]] = self.readLHPoint()
				elif(sz["Type"] == "UV"):
					vertex['U'] = self.readFloat()
					vertex['V'] = self.readFloat()
				else: #Unknown
					if(sz["Value"] == 0):
						vertex[sz["Type"]] = self.readFloat()
					elif(sz["Value"] == 1):
						vertex[sz["Type"]] = []
						vertex[sz["Type"]].append(self.readFloat())
						vertex[sz["Type"]].append(self.readFloat())
					elif(sz["Value"] == 2):
						vertex[sz["Type"]] = self.readLHPoint()
		return vertex
		
	def writeVertex(self,f,vertex):
		for sz in self.m["VertexSize"]["Items"]:
			if(sz["Enabled"]):
				if((sz["Type"] == "Position") or (sz["Type"] == "Normal")):
					self.writeLHPoint(f,vertex[sz["Type"]])
				elif(sz["Type"] == "UV"):
					self.writeFloat(f,vertex["U"])
					self.writeFloat(f,vertex["V"])
				else: #Unknown
					if(sz["Value"] == 0):
						self.readFloat()
					elif(sz["Value"] == 1):
						self.writeFloat(f,vertex[sz["Type"]][0])
						self.writeFloat(f,vertex[sz["Type"]][1])
					elif(sz["Value"] == 2):
						self.writeLHPoint(f,vertex[sz["Type"]])
	
	def readVertexSize(self):
		vertexSize = {}
		item_Lookup = ["Position","Normal","UV","Unknown1","Unknown2"]
		sizelookup = [4,8,12,4,1]
		totalsize = 0
		
		vertexSize["count"] = self.readUInt32()
		vertexSize["Items"] = []
		for x in range(5):
			val = {}
			val["Id"] = self.readUInt32()
			val["Value"] = self.readUInt32()
			val["Type"] = item_Lookup[x]
			if(x >= vertexSize["count"]):
				val["Value"] = 0
				val["Enabled"] = False
			else:
				totalsize += sizelookup[val["Value"]]
				val["Enabled"] = True
				
			vertexSize["Items"].append(val)
		
		vertexSize["TotalSize"] = totalsize
		return vertexSize
		
	def writeVertexSize(self,f,stride):	
		self.writeUInt32(f,stride["count"])
		for sz in stride["Items"]:
			self.writeUInt32(f,sz["Id"])
			self.writeUInt32(f,sz["Value"])
			
	def readStride(self,length):
		st = []
		for i in range(length):
			st.append(self.readInt32())
		return st
		
	def writeStride(self,f,st):
		for i in st:
			self.writeInt32(f,i)
		return st
			
	#Reading a single point
	def readLHPoint(self):
		pt = {}
		pt['X'] = self.readFloat()
		pt['Y'] = self.readFloat()
		pt['Z'] = self.readFloat()
		return pt
	
	#Writing a single point
	def writeLHPoint(self,f,val):
		self.writeFloat(f,val['X'])
		self.writeFloat(f,val['Y'])
		self.writeFloat(f,val['Z'])
	
	# Low level reading functions: int32, float, and string [until null is reached, null not included in returned string]
	def readInt32(self):
		return struct.unpack('<i', self.f.read(4))[0]
	def readUInt32(self):
		return struct.unpack('<I', self.f.read(4))[0]
	#Read int16
	def readInt16(self):
		return struct.unpack('<h', self.f.read(2))[0]
	def readUInt16(self):
		return struct.unpack('<H', self.f.read(2))[0]
	#Read int8	
	def readInt8(self):
		return struct.unpack('<b', self.f.read(1))[0]
	def readUInt8(self):
		return struct.unpack('<B', self.f.read(1))[0]
	#Read float (4 bytes)
	def readFloat(self):
		return struct.unpack('<f', self.f.read(4))[0]
		
	def readString(self,mxRead):
		mystr = ''
		c = ' '
		cnt = 0
		while ((c[0] != 0)and(cnt<mxRead)):
			c = struct.unpack('c', self.f.read(1))[0]
			if(c[0] != 0):
				b = c[0].to_bytes(1, sys.byteorder)
				mystr += b.decode('utf-8', 'backslashreplace')

			cnt+=1
		return mystr
		
	# Low level writing functions:
	def writeInt32(self,f,val):
		f.write(struct.pack('<i',val))
		
	def writeUInt32(self,f,val):
		f.write(struct.pack('<I',val))
	#Write int16	
	def writeInt16(self,f,val):
		f.write(struct.pack('<h',val))
		
	def writeUInt16(self,f,val):
		f.write(struct.pack('<H',val))
	#Write int8
	def writeInt8(self,f,val):
		f.write(struct.pack('<b',val))
		
	def writeUInt8(self,f,val):
		f.write(struct.pack('<B',val))
	#Write float (4 bytes)
	def writeFloat(self,f,val):
		f.write(struct.pack('<f',val))
	#Write String
	def writeString(self,f,val):
		for c in val:
			f.write(struct.pack('<c',bytes(c,'utf-8')))
		
#numpy data type
#	'<': little endian
#	'>': big endian
#	Variable Type
#	'b': Boolean
#	'i': integer
#	'u': unsigned integer
#	'f': float
#	'c': complex-floating point
#	'm': timedelta
#	'M': Datetime
#	'O': Python Object
#	'S','a': (byte-) String
#	'U': Unicode
#	'V': Raw Data
#	Number of Bytes
#		Following the variable type a number is used to intidate the number of bytes to read
#	Example
#		'<i4': Little endian 32bit integer
