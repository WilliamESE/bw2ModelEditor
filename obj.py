import array,sys,time,os
import re
import numpy as np
import struct
import pywavefront
import math
import ntpath

class obj():
	#def __init__(self):
	#	self.m = {}
		
	def loadFromFile(self, filename):
		#self.m = pywavefront.Wavefront(filename,create_materials=True,collect_faces=True)
		
		fdir, fname = ntpath.split(filename)
		
		meshes = []
		mh = {"Name": "None", "Id": 0, "v": [], "n": [], "uv": [], "vp": [], "Materials": {}}
		mh["Format"] = {"v": 3,"n": 3,"uv": 2,"tp": 0}
		mh["Updated"] = {"v": False,"n": False,"uv": False,"tp": False}
		mhcnt = 1
		lcnt = 0
		mt = ""
		with open(filename) as fl:
			for line in fl:
				cont = line.split(" ")
				#cont[-1] = cont[-1][:-1]
				elecnt = len(cont)
				if(cont[0] == "mtllib"): #Material file
					mtl = self.loadmtlFile(fdir,cont[1][:-1])
				elif(cont[0] == "o"): #Object [Meshes]
					if(mhcnt > 1):
						meshes.append(mh)
					mh = {"Name": cont[1][:-1], "Id": mhcnt, "v": [], "n": [], "uv": [], "vp": [], "Materials": {}}
					mh["Format"] = {"v": 3,"n": 3,"uv": 2,"tp": 0}
					mh["Updated"] = {"v": False,"n": False,"uv": False,"tp": False}
					mhcnt += 1
				elif(cont[0] == "v"): #Vertex
					if(mh["Updated"]["v"] == False):
						mh["Format"]["v"] = elecnt - 1
						mh["Updated"]["v"] = True
					mh["v"].append({"X": float(cont[1]),"Y": float(cont[2]),"Z": float(cont[3])})
				elif(cont[0] == "vn"): #Normal
					if(mh["Updated"]["n"] == False):
						mh["Format"]["n"] = elecnt - 1
						mh["Updated"]["n"] = True
					mh["n"].append({"X": float(cont[1]),"Y": float(cont[2]),"Z": float(cont[3])})
				elif(cont[0] == "vt"): #texture coorinates (u [,v,w])
					if(mh["Updated"]["uv"] == False):
						mh["Format"]["uv"] = elecnt - 1
						mh["Updated"]["uv"] = True
					uv_s = {}
					uv_s["U"] = float(cont[1])
					if(elecnt > 2):
						uv_s["V"] = float(cont[2])
					if(elecnt > 3):
						uv_s["W"] = float(cont[3])
					mh["uv"].append(uv_s)
				elif(cont[0] == "vp"): #Parameter space vertices ( u [,v] [,w] )
					if(mh["Updated"]["vp"] == False):
						mh["Format"]["vp"] = elecnt - 1
						mh["Updated"]["vp"] = True
					vp_s = {}
					vp_s["U"] = float(cont[1])
					if(elecnt > 2):
						vp_s["V"] = float(cont[2])
					if(elecnt > 3):
						vp_s["W"] = float(cont[3])
					mh["vp"].append(vp_s)
				elif(cont[0] == "usemtl"):
					mt = cont[1][:-1]
					mh["Materials"][mt] = {"Name": mt, "Faces": [], "Updated": False, "Type": 0}
				elif(cont[0] == "f"): #Faces [0] v1 v2 v3; [1] v1/vt1 v2/vt2 v3/vt3; [2] v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3; [3] v1//vn1 v2//vn2 v3//vn3
					if(mh["Materials"][mt]["Updated"] == False):
						#I must first determine the format
						#	Separated by a ' ' I would get one of the following: v1; v1/vt2; v1/vt1/vn1; v1//vn1
						#	The '/' will allow me to distiguesh between them (1) has none, (2) has 1, (3) and (4) have 2; the latter ones can be differentaited by looking for '//'
						faceT = cont[1].split(" ")
						slcnt = faceT[0].count("/")
						if(slcnt == 1):
							mh["Materials"][mt]["Type"] = 1
						elif(slcnt == 2):
							if (faceT[0].find("//") == -1):
								mh["Materials"][mt]["Type"] = 2
							else:
								mh["Materials"][mt]["Type"] = 3
						mh["Materials"][mt]["Updated"] = True
					#End if type check
					face = []
					x = 0
					for x in range(1, len(cont)):
						if(x == (len(cont) - 1)):
							cont[x] = cont[x][:-1]
						vertex = {"id": cont[x],"v": -1, "uv": -1, "n": -1}
						if(mh["Materials"][mt]["Type"] == 0):
							vertex["v"] = int(cont[x]) - 1
						elif(mh["Materials"][mt]["Type"] == 1):
							values = cont[x].split("/")
							vertex["v"] = int(values[0]) - 1
							vertex["uv"] = int(values[1]) - 1
						elif(mh["Materials"][mt]["Type"] == 2):
							values = cont[x].split("/")
							vertex["v"] = int(values[0]) - 1
							vertex["uv"] = int(values[1]) - 1
							vertex["n"] = int(values[2]) - 1
						elif(mh["Materials"][mt]["Type"] == 3):
							values = cont[x].split("//")
							vertex["v"] = int(values[0]) - 1
							vertex["n"] = int(values[1]) - 1
						face.append(vertex)
					mh["Materials"][mt]["Faces"].append(face)
			lcnt += 1
		
		fl.close()
		meshes.append(mh)
		#Construct the final model output
		self.m = {}
		self.m["Meshes"] = meshes
		self.m["Materials"] = mtl
		return self.m
	
	def loadmtlFile(self,filelocation,name):
		mtl = []
		cnt = 0
		cm = {}
		with open(filelocation + "/" + name) as mfl:
			for line in mfl:
				cont = line.split(" ")
				elecnt = len(cont)
				if(cont[0] == "newmtl"):
					if(cnt != 0):
						mtl.append(cm)
					cm = {"Name": cont[1][:-1],"Id": cnt}
					cnt += 1
				elif(cont[0] == "Ns"):
					cm["SpecularWeight"] = float(cont[1][:-1])
				elif(cont[0] == "Ka"):
					cm["Ambient"] = [float(cont[1]), float(cont[2]), float(cont[3][:-1])]
				elif(cont[0] == "Kd"):
					cm["Diffuse"] = [float(cont[1]), float(cont[2]), float(cont[3][:-1])]
				elif(cont[0] == "Ks"):
					cm["Specular"] = [float(cont[1]), float(cont[2]), float(cont[3][:-1])]
				elif(cont[0] == "Ke"):
					cm["Emissive"] = [float(cont[1]), float(cont[2]), float(cont[3][:-1])]
				elif(cont[0] == "Ni"):
					cm["OpticalDensity"] = float(cont[1][:-1])
				elif(cont[0] == "d"):
					cm["Transparent"] = float(cont[1][:-1])
				elif(cont[0] == "Tr"):
					cm["Transparent"] = 1.0 - float(cont[1][:-1])
				elif(cont[0] == "illum"):
					cm["Illumination"] = int(cont[1][:-1])
				elif(cont[0] == "map_Kd"):
					cm["DiffuseTexture"] = cont[1][:-1]
				#else:
				#	isMap = cont[0].find("map")
				#	if(isMap != -1):
						#Texture
		mtl.append(cm)
		mfl.close()
		return mtl
	
	#generateBWM - Process the wavefront and develop a bwm object structure
	#	Basic Model details - box, front, center, height, raduis, volume.
	#	Vertices Convertor - Generate the bwm version of verices from the obj, also indices is best delt with here
	#							Collect (position, normal, uv); remove repeatitive vertices; constuct indices.
	def calculate_ModelInfo(self):
		#We have in the wavefront self.m.vertices, which can be processed to locate the corner points
		pA = {"X":self.m["Meshes"][0]["v"][0]["X"],"Y":self.m["Meshes"][0]["v"][0]["Y"],"Z":self.m["Meshes"][0]["v"][0]["Z"]}
		pB = {"X":self.m["Meshes"][0]["v"][0]["X"],"Y":self.m["Meshes"][0]["v"][0]["Y"],"Z":self.m["Meshes"][0]["v"][0]["Z"]}
		for mh in self.m["Meshes"]:
			for v in mh["v"]:
				if(v["X"] > pA["X"]):
					pA["X"] = v["X"]
				if(v["X"] < pB["X"]):
					pB["X"] = v["X"]
					
				if(v["Y"] > pA["Y"]):
					pA["Y"] = v["Y"]
				if(v["Y"] < pB["Y"]):
					pB["Y"] = v["Y"]	
					
				if(v["Z"] > pA["Z"]):
					pA["Z"] = v["Z"]
				if(v["Z"] < pB["X"]):
					pB["Z"] = v["Z"]
				
		h = pA["Y"] - pB["Y"]
		r = round(math.sqrt(((pA["X"] - pB["X"])*(pA["X"] - pB["X"]))+((pA["Z"] - pB["Z"])*(pA["Z"] - pB["Z"]))) / 2, 3)
		pF = {"X":0,"Y":0,"Z":pA["Z"]}
		volume = (pA["X"] - pB["X"]) * (pA["Z"] - pB["Z"]) * h #Overly simlified calculation
		
		mod_info = {}
		mod_info["Front"] = pF
		mod_info["Box1"] = pA
		mod_info["Box2"] = pB
		mod_info["Radius"] = r
		mod_info["Height"] = h
		mod_info["Volume"] = volume
		return mod_info
		
	def convertToBWM(self):
		bwm = {}
		info = self.calculate_ModelInfo()
		
		bwm["Type"] = 5
		bwm["Unknown1"] = 0.0
		bwm["Unknown2"] = info["Front"]
		bwm["BoxPoint1"] = info["Box1"]
		bwm["BoxPoint2"] = info["Box2"]
		bwm["Center"] = {"X": 0, "Y": 0, "Z": 0}
		bwm["Height"] = info["Height"]
		bwm["Volume"] = info["Volume"]
		bwm["Radius"] = info["Radius"]
		bwm["Unknown3"] = 2
		
		#Unknown information
		bwm["UnknownF1"] = 0
		bwm["UnknownF2"] = 0
		bwm["UnknownF3"] = 0
		bwm["UnknownF4"] = bwm["Unknown2"]["Z"]
		bwm["Unknown4"] = 0
		
		#Model contents
		bwm["Bones"] = []
		bwm["cntBones"] = 0
		
		bwm["Entities"] = []
		bwm["cntEntities"] = 0
		
		bwm["Un1"] = []
		bwm["cntUnknown1"] = 0
		
		bwm["Un2"] = []
		bwm["cntUnknown2"] = 0
		
		#Materials
		bwm["Materials"] = []
		matrefs = {}
		for mat in self.m["Materials"]:
			matrefs[mat["Name"]] = mat["Id"]
			#DiffuseMap, LightMap, FoliageMap, SpecularMap, FireMap, NormalMap, Type
			material = {"DiffuseMap": "", "LightMap": "", "FoliageMap": "", "SpecularMap": "", "FireMap": "", "NormalMap": "", "Type": "baseplate"}
			bwm["Materials"].append(material)
		bwm["cntMaterials"] = len(self.m["Materials"])
		
		bwm["Meshs"] = []
		bwm["cntMeshs"] = len(self.m["Meshes"])
		
		#Vertices and indices
		# For each mesh there is an array of faces, this can be used for the vertices
		#	I can construct the array of vertex objects, relying on the key "id" for later sorting
		
		bwm["Vertices"] = []
		bwm["Indices"] = []
		
		icnt = 0 #index count
		vcnt = 0 #vertex count
		fcnt = 0 #face count
		mhcnt = 0
		for mh in self.m["Meshes"]:
			bw_mesh = {} #cntFaces, offIndices, cntIndices, offVertices, cntVertices, [Points] * 9, Unknown1 = 1, Volume, cntMaterials, [Unknown3], [Unknown4], Name, Unknown5 = 0, Unknown6 = 0
			#Basic mesh details
			bw_mesh["offIndices"] = icnt
			bw_mesh["offVertices"] = vcnt
			bw_mesh["Volume"] = 0
			bw_mesh["cntMaterials"] = len(mh["Materials"])
			bw_mesh["Name"] = mh["Name"]
			if(bw_mesh["Name"] == None):
				bw_mesh["Name"] = "box%d" % (mhcnt+1)
			
			bw_mesh["Points"] = []
			pnts = [[-1,0,0],[0,0,-1],[0,-1,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
			for x in range(9):
				p = {"X": pnts[x][0], "Y": pnts[x][1], "Z": pnts[x][2]}
				bw_mesh["Points"].append(p)
			
			bw_mesh["Unknown1"] = 1
			bw_mesh["Unknown3"] = 0
			bw_mesh["Unknown4"] = 1
			bw_mesh["Unknown5"] = 0
			bw_mesh["Unknown6"] = 0
			
			#Materials
			bw_mesh["Materials"] = []
			for nm, mt in mh["Materials"].items():
				bw_mat = {} #MaterialRef, offIndices, cntIndices, offVertex, cntVertex, offFaces, cntFaces, Unknown = 15
				#Materials in the wavefront will have a .name item which is the key in the m.material dictionary; this will have to be used to indicate what the material ref is
				#	Prior to this section (under materials) I constructed a matrefs dictionary, which the keys are the material's name and value is the reference number
				bw_mat["MaterialRef"] = matrefs[mt["Name"]]
				
				bw_mat["offIndices"] = icnt
				bw_mat["offVertex"] = vcnt
				bw_mat["offFaces"] = fcnt
				
				bw_mat["Unknown"] = 15
				
				#Reference Array
				#f = {
				#	id = "v1/vt1/n1"
				#	v
				#	n
				#	vt
				# }
				vREF = {}
				vRcnt = 0
				fScnt = 0
				for f in mt["Faces"]:
					for x in range(3): #Each face contains 3 vertices
						if(f[x]["id"] in vREF):
							#Access face information and save index as specified in vREF
							bwm["Indices"].append(vREF[f[x]["id"]]["Index"])
							icnt+=1
						else:
							vREF[f[x]["id"]] = {"Order": vRcnt, "Index": vcnt}
							vRcnt += 1	
							#Save original vertex and append new index
							v = {"id": vcnt}
							if(mh["Format"]["v"] == 3):
								#if(f[x]["v"] > len(mh["v"])):
									v["Position"] = {"X": mh["v"][f[x]["v"]]["X"],"Y": mh["v"][f[x]["v"]]["Y"],"Z": mh["v"][f[x]["v"]]["Z"]}
								#else:
								#	print("Fatal Error: Vertex out of range %d" % f[x]["v"])
								#	return 0
							if(mh["Format"]["n"] == 3):
								#if(f[x]["n"] > len(mh["n"])):
									v["Normal"] = {"X": mh["n"][f[x]["n"]]["X"],"Y": mh["n"][f[x]["n"]]["Y"],"Z": mh["n"][f[x]["n"]]["Z"]}
								#else:
								#	print("Fatal Error: Normal out of range %d" % f[x]["n"])
								#	return 0
							if(mh["Format"]["uv"] > 1):
								#if(f[x]["uv"] > len(mh["uv"])):	
									v["U"] = mh["uv"][f[x]["uv"]]["U"]
									v["V"] = mh["uv"][f[x]["uv"]]["V"] * -1
								#else:
								#	print("Fatal Error: UV out of range %d" % f[x]["uv"])
								#	return 0
							if(mh["Format"]["uv"] > 2):
								v["W"] = mh["uv"][f[x]["uv"]]["W"]
								
							bwm["Vertices"].append(v)
							bwm["Indices"].append(vcnt)
							icnt+=1
							vcnt+=1
					fcnt += 1			
					fScnt += 1	
				#End of material face loop
				
				bw_mat["cntIndices"] = icnt - bw_mat["offIndices"]
				bw_mat["cntVertex"] = vcnt - bw_mat["offVertex"]
				bw_mat["cntFaces"] = fcnt - bw_mat["offFaces"]
				
				bw_mesh["Materials"].append(bw_mat)
			#End of material reference
			
			bw_mesh["cntFaces"] = fcnt
			bw_mesh["cntIndices"] = icnt - bw_mesh["offIndices"]
			bw_mesh["cntVertices"] = vcnt - bw_mesh["offVertices"]
			bwm["Meshs"].append(bw_mesh)
			mhcnt += 1
			
		#End of mesh loop
		#Clean up and final steps
		bwm["Vertices"].sort(key=self.getvertKey)
		bwm["cntVerticies"] = vcnt
		bwm["cntIndices"] = icnt
		bwm["cntStrides"] = 1
		bwm["Unknown5"] = 2
		
		#Stride
		bwm["Stride"] = []
		s = []
		ary = [0,0,1244040,0,1244840,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		for x in range(23):
			s.append(ary[x])
		bwm["Stride"].append(s)
		
		#Vertex Size
		bwm["VertexSize"] = {}
		bwm["VertexSize"]["Items"] = []
		#count, Items: {Id,Value}
		ary = [[0,2],[1,2],[2,1],[0,0],[0,0]]
		for v in ary:
			bwm["VertexSize"]["Items"].append({"Id":v[0],"Value":v[1]})
		bwm["VertexSize"]["count"] = 3
		
		bwm["VertexSize"]["Items"][0]["Enabled"] = True
		bwm["VertexSize"]["Items"][0]["Type"] = "Position"
		bwm["VertexSize"]["Items"][1]["Enabled"] = True
		bwm["VertexSize"]["Items"][1]["Type"] = "Normal"
		bwm["VertexSize"]["Items"][2]["Enabled"] = True
		bwm["VertexSize"]["Items"][2]["Type"] = "UV"
		bwm["VertexSize"]["Items"][3]["Enabled"] = False
		bwm["VertexSize"]["Items"][3]["Type"] = "Unknown1"
		bwm["VertexSize"]["Items"][4]["Enabled"] = False
		bwm["VertexSize"]["Items"][4]["Type"] = "Unknown2"
		
		return bwm
		
	def getvertKey(self, obj):
		return obj["id"]
		
#Wavefont object class
#	Root
#		vertices
#		mesh_list
#			materials
#				vertex_format - Can contain: T2F, C3F, N3F and V3F may appear in this string
#									T = uv[w]
#									C = Cleaves
#									N = Normal
#									V = Position
#				vertices - see the vertex_format
#				faces
#				diffuse
#				ambient
#				texture
			
#OBJ file info:
#	Each line of code in an obj file begins will an identifier:
#		v 	=> geometric vertices (x,y,z[,w]) [w defaults to 1.0]
#		vt 	=> texture coorinates (u [,v,w]) these will vary between 0 and 1. v, w are optional and default to 0.
#		vn	=> vertex normals in (x,y,z), they may or may not be unit vectors
#		vp	=> Parameter space vertices ( u [,v] [,w] )
#		f	=> polygonal face element. 4 format are available, each line will contain 3 or more elements
#			1. v1 v2 v3
#			2. v1/vt1 v2/vt2 v3/vt3
#			3. v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3
#			4. v1//vn1 v2//vn2 v3//vn3
#		l	=> line element (v1 v2 v3 v4 ...)
#	Materials
#		These are stored in external mtl files
#		The following command is used to name this material files: 
#			mtllib [external mtl filename]
#		The file then indicates what material to use with this command:
#			usemtl [material name]
#		Named objects and polygon groups are specified using:
#			o [object name]
#			g [group name]
#		There is also smoothing groups indicated with [Probably won't do much with this]
#			s 1
#				....
#				s off
#	Lines that begin with #are comments in the model file and should be ignored

#mtl file info:
#	A comment line begins with #
#	A material is defined with
#		newmtl [name]
#	Ambient color
#		ka [R G B]
#	Diffuse
#		kd [R G B]
#	Specular color
#		Ks [R G B]
#		Weighted with Ns
#			Ns [Value]
#	Transparent
#		d [0-1.0 (where 1.0 is fully opaque)
#		Others use
#		Tr [0-1.0 (the opposate of d)]
#	Optical density (index of refraction):
#		Ni [Value]
#	Illumination models
#		illum [Type]
#		Types:
#			0. Color on and Ambient off
#			1. Color on and Ambient on
#			2. Highlight on
#			3. Reflection on and Ray trace on
#			4. Transparency: Glass on, Reflection: Ray trace on
#			5. Reflection: Fresnel on and Ray trace on
#			6. Transparency: Refraction on, Reflection: Fresnel off and Ray trace on
#			7. Transparency: Refraction on, Reflection: Fresnel on and Ray trace on
#			8. Reflection on and Ray trace off
#			9. Transparency: Glass on, Reflection: Ray trace off
#			10. Casts shadows onto invisible surfaces
#	Finally the texture map, not necessary but are simply a list of texture files contained within this material
#		Textures may also have options:
#			-blendu on | off                       # set horizontal texture blending (default on)
#			-blendv on | off                       # set vertical texture blending (default on)
#			-boost float_value                     # boost mip-map sharpness
#			-mm base_value gain_value              # modify texture map values (default 0 1)
#			                                       #     base_value = brightness, gain_value = contrast
#			-o u [v [w]]                           # Origin offset             (default 0 0 0)
#			-s u [v [w]]                           # Scale                     (default 1 1 1)
#			-t u [v [w]]                           # Turbulence                (default 0 0 0)
#			-texres resolution                     # texture resolution to create
#			-clamp on | off                        # only render texels in the clamped 0-1 range (default off)
#			                                       #   When unclamped, textures are repeated across a surface,
#			                                       #   when clamped, only texels which fall within the 0-1
#			                                       #   range are rendered.
#			-bm mult_value                         # bump multiplier (for bump maps only)
#			
#			-imfchan r | g | b | m | l | z         # specifies which channel of the file is used to 
#			                                       # create a scalar or bump texture. r:red, g:green,
#			                                       # b:blue, m:matte, l:luminance, z:z-depth.. 
#			                                       # (the default for bump is 'l' and for decal is 'm')
