import settings
from tkinter import *
import numpy as np
import os
from datetime import date
import ntpath

from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from panda3d.core import WindowProperties
from math import *
from direct.task import Task

class TkinterGuiClass(ttk.Frame):
    
	def __init__(self, parent, args_):
		# Start ShowBase, but don't open a Panda window yet
		self.base = ShowBase(windowType='none')

		# Start Tkinter integration, get the root window handle
		ConfigVariableBool('disable-message-loop', False).value = True
		self.base.startTk()
		
		self.frame = parent
		self.frame.update()
		self.frame.update_idletasks() 
		id = self.frame.winfo_id()
		width = self.frame.winfo_width()
		height = self.frame.winfo_height()
		
		props = WindowProperties()
		props.setParentWindow(id)
		props.setOrigin(0, 0)
		props.setSize(width, height)

		self.base.win = self.base.makeDefaultPipe()
		self.base.openDefaultWindow(props=props)
		
		self.frame.bind("<Configure>",self.resized)
	
	def resized(self,event):
		self.frame.update()
		self.frame.update_idletasks() 
		w = self.frame.winfo_width()
		h = self.frame.winfo_height()
		
		props = WindowProperties()
		props.setOrigin(0, 0)
		props.setSize(w, h) 
		
		#if self.base.win is not None:
		self.base.win.requestProperties(props)
		
	def getBase(self):
		return self.base

class p3dClass():
	bw2Root = "/c/Program Files (x86)/Lionhead Studios/Black & White 2/"
	bw2RootWin = "C:\\Program Files (x86)\\Lionhead Studios\\Black & White 2\\Data\\Art\\textures"
	bw2Textures = bw2Root+"/Data/Art/textures"
	
	class bw2TextureClass():
		def __init__(self,name,material):
			#Each material will have 7 pieces of information:
			#	Diffuse map - the main texture connected to the base texture coords
			self.Diffuse = {}
			self.Diffuse["Main"] = material["DiffuseMap"]
			if(self.Diffuse["Main"] == ""):
				self.Diffuse["Main"] = "t_courtyardground.dds"
			self.locateFile(self.Diffuse)
			#	Light map - uses the base texture coords
			self.Light = {}
			self.Light["Main"] = material["LightMap"]
			self.locateFile(self.Light)
			#	Growth map - secondary texture (in all models view to this point, it has been related to foliage)
			self.growth = {}
			self.growth["Main"] = material["FoliageMap"]
			self.locateFile(self.growth)
			#	Specular map - uses the base texture coords
			self.specular = {}
			self.specular["Main"] = material["SpecularMap"]
			self.locateFile(self.specular)
			#	Animation map - secondary texture (in all models view to this point, it has been related to fire -- likely fire animation textures)
			self.animation = {}
			self.animation["Main"] = material["FireMap"]
			self.locateFile(self.animation)
			#	Normal map - uses the base texture coords
			self.normal = {}
			self.normal["Main"] = material["NormalMap"]
			self.locateFile(self.normal)
			#	Type - what type of material this is: _glossy_, _tree_
			self.type = material["Type"]
			
			#Texture arrays for panda3D
			self.stages = [] #These are the slots in which a single texture can be loaded
			self.texAttrib = TextureAttrib.make()#Storage for multiple texture stages which can be applied to a geomtery node
			
			self.defineStage(name,"diffuse","base",self.Diffuse)
			self.defineStage(name,"light","growth",self.Light)
			#self.defineStage(name,"growth","growth",self.growth)
			self.defineStage(name,"specular","base",self.specular)
			#self.defineStage(name,"animation","animation",self.animation)
			self.defineStage(name,"normal","base",self.normal)
					
			#Texture order
			#The following function call can be used to specify the order in which the textures will appear
			#<texturestage>.setSort(#) #The default is 0
			#<texturestage>.setPriority() #Sets which texture is of the most importance
			
			#Texture transforms would likely have to be used for the flame textures. But must be done through the nodepath
			#<nodepath>.setTextureOffset(<texturestage>, uoffset, voffset)
			#<nodepath>.setTextureScale(<texturestage>, uScale, vScale)
			#<nodepath>.setTextureRotate(<texturestage>, degrees)
			
			#The mode maybe be useful for spectual and normal maps and the like...
			#plants and veins could be best as decal
			#spectual could be glossy
			#normal is (nicely named) a normal map mode
			
		def defineStage(self,name,ty,coord,item):
			if((coord != "base") and (coord != "growth") and (coord != "animation")):
				return False
			
			#Main first, check to make sure it is defined and was found
			if(item["hasMain"] == True):
				filename = settings.locations["Textures_Linux"] + "/" + item["Main"]
				texture = loader.loadTexture(filename)
				
				stg = TextureStage(name+ty+"Main")
				stg.setTexcoordName(coord)
				if((ty == "diffuse")):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "normal"):
					stg.setMode(TextureStage.MNormal)
				elif(ty == "light"):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "animation"):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "specular"):
					stg.setMode(TextureStage.MGloss)
				self.texAttrib = self.texAttrib.addOnStage(stg, texture)
			
			#Evil
			if(item["hasEvil"] == True):
				filename = settings.locations["Textures_Linux"] + "/" + item["Evil"]
				texture = loader.loadTexture(filename)
				
				stg = TextureStage(name+ty+"Evil")
				stg.setTexcoordName(coord)
				if((ty == "diffuse")):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "light"):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "animation"):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "normal"):
					stg.setMode(TextureStage.MNormal)
				elif(ty == "specular"):
					stg.setMode(TextureStage.MGloss)
				#self.texAttrib = self.texAttrib.addOnStage(stg, texture)
				
			#Good
			if(item["hasGood"] == True):
				filename = settings.locations["Textures_Linux"] + "/" + item["Good"]
				texture = loader.loadTexture(filename)
				
				stg = TextureStage(name+ty+"Good")
				stg.setTexcoordName(coord)
				if((ty == "diffuse")):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "light"):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "animation"):
					stg.setMode(TextureStage.MModulate)
				elif(ty == "normal"):
					stg.setMode(TextureStage.MNormal)
				elif(ty == "specular"):
					stg.setMode(TextureStage.MGloss)
				#self.texAttrib = self.texAttrib.addOnStage(stg, texture)
			
		def locateFile(self,item):
			item["hasMain"] = False
			item["hasEvil"] = False
			item["hasGood"] = False
			
			if(item["Main"] == ""):
				return False
				
			filename = settings.locations["Textures"] + "\\" + item["Main"]
			if(os.path.exists(filename) == True):
				item["hasMain"] = True
				#We have the file, so that's good
				#	We'll have to check for alignment files that go alone with this		
				if("neut" in item["Main"]):
					#Texture files for which exist alternate alignments follow the structure:
					#	t_<tribe>_<object>_<align>_<extension>
					#Some texture types have an extra item it:
					#	specular is spc
					#	lightmap is lightmap
					#	normal is nrm
					evilName = item["Main"].replace("neut","evil")
					goodName = item["Main"].replace("neut","good")
					
					evilLoca = settings.locations["Textures"] + "\\" + evilName
					goodLoca = settings.locations["Textures"] + "\\" + goodName
					if(os.path.exists(evilLoca) == True):
						item["Evil"] = evilName
						item["hasEvil"] = True
					if(os.path.exists(goodLoca) == True):
						item["Good"] = goodName
						item["hasGood"] = True	
				return True
			return False
			
		def getAttrib(self):
			return self.texAttrib
			
	
	def __init__(self, base, model):
		self.base = base
		self.model = model
		#Determine the type of model we are working with
		#if(not ("MagicNum" in model)):
		
		#else:
		#Interprate file name
		full_location = model.fln #Get full name from the model
		directory, filename = ntpath.split(full_location) #Split the file name from the directory
		exts = filename.split('.bwm') #Remove the extension
		self.filename = exts[0] #Save this value in a global
		
		self.loadBWM(model.m,self.filename)
		
	def loadBWM(self,model,name):
		#Analyzing vertex information:
		texcoord2 = False
		texcoord3 = False
		
		geomfmt = GeomVertexArrayFormat()
		geomfmt.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)
		geomfmt.addColumn("normal",3,Geom.NTFloat32,Geom.CNormal)
		geomfmt.addColumn("texcoord.base",2,Geom.NTFloat32,Geom.CTexcoord)
		if(model["VertexSize"]["Items"][3]["Enabled"] == True):
			geomfmt.addColumn("texcoord.growth",2,Geom.NTFloat32,Geom.CTexcoord)
			texcoord2 = True
		if(model["VertexSize"]["Items"][4]["Enabled"] == True):
			geomfmt.addColumn("texcoord.animation",2,Geom.NTFloat32,Geom.CTexcoord)
			texcoord3 = True
		
		#Create new vertex format
		gVerfmt = GeomVertexFormat()
		gVerfmt.addArray(geomfmt)
		gVerfmt = GeomVertexFormat.registerFormat(gVerfmt)
		
		#Create panda3D vertex object, it is in this that all the vertices will be stored
		self.geomDataAry = GeomVertexData(name, gVerfmt, Geom.UHStatic)
		#Define writers
		wvertices = GeomVertexWriter(self.geomDataAry, 'vertex')
		wnormals = GeomVertexWriter(self.geomDataAry, 'normal')
		wtexcoord = GeomVertexWriter(self.geomDataAry, 'texcoord.base')
		if(texcoord2 == True):
			wtexcoord2 = GeomVertexWriter(self.geomDataAry, 'texcoord.growth')
		if(texcoord3 == True):
			wtexcoord3 = GeomVertexWriter(self.geomDataAry, 'texcoord.animation')
		
		#Fill vertex data array
		for vtx in range(0,model["cntVerticies"]):
			#Read vertex information from model
			p = model["Vertices"][vtx]["Position"]
			n = model["Vertices"][vtx]["Normal"]
			v = model["Vertices"][vtx]["V"]
			u = model["Vertices"][vtx]["U"]
			if(texcoord2 == True):
				v2 = model["Vertices"][vtx]["Unknown1"][0]
				u2 = model["Vertices"][vtx]["Unknown1"][1]
			if(texcoord3 == True):
				v3 = model["Vertices"][vtx]["Unknown2"][0]
				u3 = model["Vertices"][vtx]["Unknown2"][1]
			
			#Store them in the vertex data array
			wvertices.addData3f(p["X"],p["Y"],p["Z"])
			wnormals.addData3f(n["X"],n["Y"],n["Z"])
			wtexcoord.addData2(u, -v) #bwm files, the v coord is flipped, hence the reason for the negative
			if(texcoord2 == True):
				wtexcoord2.addData2(v2, -u2)
			if(texcoord3 == True):
				wtexcoord3.addData2(v3, -u3)
			
		#Pre-material processing
		#	Here the plan is to loop through the materials, locate the textures and determine how they should be loaded.
		materialDefs = []
		for mat in model["Materials"]:
			materialDefs.append(self.bw2TextureClass(name,mat))
		
		#Now that the vertices have been transfered into the data array.
		# The next step is to go through each mesh and its subsequent materials
		# and build the geometry nodes.
		
		#Create instance of panda geometry node
		geometry = GeomNode(name)
		
		indPos = 0 #Keeps track of the index position
		faces = []
		refs = []
		for mesh in model["Meshs"]:
			if(mesh["Unknown4"] != 1):
				break
			for material in mesh["Materials"]:
				#This name will be used to identify the geom later
				geomName = mesh["Name"] + "_" + str(material["MaterialRef"])
				
				#Create triangles for this material
				face = GeomTriangles(Geom.UHStatic)
				indPos = material["offIndices"]
				for i in range(indPos,indPos + material["cntIndices"],3):
					try:		
						face.addVertices(model["Indices"][i],model["Indices"][i+1],model["Indices"][i+2])
					except:
						print(i)
						return 0
				
				indPos = i
				materialGeom = Geom(self.geomDataAry)
				materialGeom.addPrimitive(face)
				geometry.addGeom(materialGeom)
				refs.append(material["MaterialRef"])
		
		#Apply textures
		for n in range(geometry.getNumGeoms()):
			textures = materialDefs[refs[n]].getAttrib()
			newRenderState = geometry.getGeomState(n).addAttrib(textures,1)
			geometry.setGeomState(n, newRenderState)
			
		self.nodePath = render.attachNewNode(geometry) #setRenderModeWireframe
		self.nodePath.setTransparency(TransparencyAttrib.M_alpha)
		self.nodePath.setTextureOff(0)
		#self.nodePath.setRenderModeWireframe()
		
		self.base.disableMouse() # if you leave mouse mode enabled camera position will be governed by Panda mouse control
		
		self.base.useDrive()
		self.base.useTrackball()
		
		self.base.trackball.node().setPos(0, model["Radius"]+20, 0)
		self.base.trackball.node().setP(120)
		
		self.drawEntities(model["Entities"])
		
		self.points = {}
		self.drawPoints("Unknowns 1",model["Un1"],0,0,1,True)
		self.drawPoints("Unknowns 2",model["Un2"],0,1,1,True)
		
	def displayBWM(self,model):
		#Loop through the meshes and insert the vertices associated with that mesh (This is a node)
		#	Render the node and apply the texture
		#	The issue is that the I'll have to integate the indices properly for each mesh as well
		#Actually each mesh has a set of materials, those materials would be the "node" so to speak, however I wonder if there is ever any overlap
		t2 = True #False
		t3 = True #False
		fmt = GeomVertexArrayFormat()
		fmt.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)
		fmt.addColumn("normal",3,Geom.NTFloat32,Geom.CNormal)
		fmt.addColumn("texcoord.base",2,Geom.NTFloat32,Geom.CTexcoord)
		if(t2 == True):
			fmt.addColumn("texcoord.plants",2,Geom.NTFloat32,Geom.CTexcoord)
		if(t3 == True):
			fmt.addColumn("texcoord.fire",2,Geom.NTFloat32,Geom.CTexcoord)
		gfmt = GeomVertexFormat()
		gfmt.addArray(fmt)
		gfmt = GeomVertexFormat.registerFormat(gfmt)
		#Model information:
		flname = model.fln
		#The problem is accessing / finding the textures. It is probably best to assume for the time being they exist solely in the bw2 directory and that it's subsequent location is also in the default location
		txLoc = "/c/Program Files (x86)/Lionhead Studios/Black & White 2/Data/Art/textures"
		
		#Loop through the model's meshes and materials collecting all the needed information
		txrs = []
		nodes = GeomNode("Objectname")
		#geometry = GeomVertexData("Obj", fmt, Geom.UHStatic)
		
		#geometry.setNumRows(model.m["cntVerticies"])
		
		nm = "Objectname"
		self.vnode = GeomVertexData(nm, gfmt, Geom.UHStatic)
		
		#Set the number of vertices
		self.vnode.setNumRows(model.m["cntVerticies"])
		
		#Collect vertices
		vertices = GeomVertexWriter(self.vnode, 'vertex')
		normals = GeomVertexWriter(self.vnode, 'normal')
		texcoord = GeomVertexWriter(self.vnode, 'texcoord.base')
		if(t2 == True):
			texcoord2 = GeomVertexWriter(self.vnode, 'texcoord.plants')
		if(t3 == True):
			texcoord3 = GeomVertexWriter(self.vnode, 'texcoord.fire')
		
		#Mat0: 6634
		#Mat1: 6634 -> 7531
		cnt=0
		pnts = []
		vpnts = []
		for vtx in range(0,model.m["cntVerticies"]):
			p = model.m["Vertices"][vtx]["Position"]
			n = model.m["Vertices"][vtx]["Normal"]
			v = model.m["Vertices"][vtx]["V"]
			u = model.m["Vertices"][vtx]["U"]
			#v2 = model.m["Vertices"][vtx]["Unknown1"][0]
			#u2 = model.m["Vertices"][vtx]["Unknown1"][1]
			#v3 = model.m["Vertices"][vtx]["Unknown2"][0]
			#u3 = model.m["Vertices"][vtx]["Unknown2"][1]
			vpnts.append(p)
			#if(cnt < 7538):
			#	if("Unknown1" in model.m["Vertices"][vtx]):
			#		print("{0}: U2 {1}, V2 {2}; U3 {3}, V3 {4}".format(cnt,round(model.m["Vertices"][vtx]["Unknown1"][0],3),round(model.m["Vertices"][vtx]["Unknown1"][1],3),round(model.m["Vertices"][vtx]["Unknown2"][0],3),round(model.m["Vertices"][vtx]["Unknown2"][1],3)))
			
			vertices.addData3f(p["X"],p["Y"],p["Z"])
			normals.addData3f(n["X"],n["Y"],n["Z"])
			texcoord.addData2(u, -v)
			#texcoord2.addData2(u2, -v2)
			#texcoord3.addData2(u3, -v3)
			cnt+=1
		
		
		cnt=0
		cntm = 0
		indPos = 0
		matTex = []
		for mh in model.m["Meshs"]:
			#if(model.m["cntMeshs"] > 1):
			#	if(cntm == (model.m["cntMeshs"] - 1)):
			#		break
			for mt in mh["Materials"]:
				nm = mh["Name"] + "_" + str(mt["MaterialRef"])
				#Collect faces
				ptv = GeomTriangles(Geom.UHStatic)
				for i in range(indPos,indPos + mt["cntIndices"],3):
					try:
						#if(cntm == (model.m["cntMeshs"] - 1)):
						#	print("{0},{1},{2}".format(model.m["Indices"][i],model.m["Indices"][i+1],model.m["Indices"][i+2]))
						inpnt = []
						inpnt.append(model.m["Vertices"][model.m["Indices"][i]]["Position"])
						inpnt.append(model.m["Vertices"][model.m["Indices"][i+1]]["Position"])
						inpnt.append(model.m["Vertices"][model.m["Indices"][i+2]]["Position"])
						pnts.append(inpnt)
						ptv.addVertices(model.m["Indices"][i],model.m["Indices"][i+1],model.m["Indices"][i+2])
						indPos += 3
					except:
						print(i)
						#return
				
				geom = Geom(self.vnode)
				geom.addPrimitive(ptv)
				nodes.addGeom(geom)
				
				#default texture, which is completely transparent
				textLocation = txLoc + "/t_courtyardground.dds"
				if(model.m["Materials"][mt["MaterialRef"]]["DiffuseMap"] != ""):
					textLocation = txLoc + "/" + model.m["Materials"][mt["MaterialRef"]]["DiffuseMap"]
				#load texture
				texture = loader.loadTexture(textLocation)
				if(texture != False): #if a texture is not found, don't do this part
					#TextureStage: a slot to hold a single texture
					ts = TextureStage(nm) #nm = mesh[Name]_material[Name]
					
					#Texture order
					#The following function call can be used to specify the order in which the textures will appear
					#<texturestage>.setSort(#) #The default is 0
					#<texturestage>.setPriority() #Sets which texture is of the most importance
					
					#Texture transforms would likely have to be used for the flame textures. But must be done through the nodepath
					#<nodepath>.setTextureOffset(<texturestage>, uoffset, voffset)
					#<nodepath>.setTextureScale(<texturestage>, uScale, vScale)
					#<nodepath>.setTextureRotate(<texturestage>, degrees)
					
					ts.setTexcoordName("base")
					
					#The mode maybe be useful for spectual and normal maps and the like...
					#plants and veins could be best as decal
					#spectual could be glossy
					#normal is (nicely named) a normal map mode
					ts.setMode(TextureStage.MModulate)
					txa = TextureAttrib.make()
					txa = txa.addOnStage(ts, texture)
					matTex.append(txa)
					#self.nodePath.setTexture(tex)
			cntm+=1
		for n in range(nodes.getNumGeoms()):
			if((matTex[n] == None) or (matTex[n] == False)):
				continue
			tx = matTex[n]
			newRenderState = nodes.getGeomState(n).addAttrib(tx,1)
			nodes.setGeomState(n, newRenderState)
		
		self.nodePath = render.attachNewNode(nodes) #setRenderModeWireframe
		self.nodePath.setTransparency(TransparencyAttrib.M_alpha)
		self.nodePath.setTextureOff(0)
		#self.nodePath.setRenderModeWireframe()
		
		self.base.disableMouse() # if you leave mouse mode enabled camera position will be governed by Panda mouse control
		
		self.base.useDrive()
		self.base.useTrackball()
		
		self.base.trackball.node().setPos(0, model.m["Radius"]+20, 0)
		self.base.trackball.node().setP(120)
		
		
		self.drawEntities(model.m["Entities"])
		self.points = {}
		self.drawPoints("Unknowns 1",model.m["Un1"],0,0,1,True)
		self.drawPoints("Unknowns 2",model.m["Un2"],0,1,1,True)
		#self.drawPoints("Interactions",model.m["Meshs"][0]["Points"],1,0,0,False)
		#self.drawPoints("Vertices",vpnts,1,1,0,False)
		#pnts = []
		#cnt = 0
		#for vtx in range(2014,2030):
		#	pnts.append(model.m["Vertices"][vtx]["Position"])
		#	print("{0}: {1},{2},{3}".format(2014+cnt,model.m["Vertices"][vtx]["Position"]["X"],model.m["Vertices"][vtx]["Position"]["Y"],model.m["Vertices"][vtx]["Position"]["Z"]))
		#	cnt+=1
		#cnt = 0
		#for face in pnts:
		#	self.drawPoints("Face{0}".format(cnt),face,1,1,0,True)
		#	cnt+=1
		#self.showPoint("Face0",0)
		#self.showPoint("Face0",1)
		#self.showPoint("Face0",2)
		self.fc = 0
		
	def drawEntities(self,ents):
		#Entities
		self.EntAry = []
		cnt = 0
		for e in ents:
			ls = LineSegs()
			ls.setThickness(5)
		
			ls.setColor(0.0, 1.0, 0.0, 1.0)
			ls.moveTo(e["Position"]["X"], e["Position"]["Y"], e["Position"]["Z"])
			ls.drawTo(e["Position"]["X"], e["Position"]["Y"]+1, e["Position"]["Z"])
			
			node = ls.create()
			self.EntAry.append(render.attachNewNode(node))
			self.EntAry[-1].hide()
			
	def loopThroughFaces(self):
		self.hidePoint("Face{0}".format(self.fc),0)
		self.hidePoint("Face{0}".format(self.fc),1)
		self.hidePoint("Face{0}".format(self.fc),2)
		self.fc += 1
		print(self.fc)
		if(("Face{0}".format(self.fc)) in self.points):
			self.showPoint("Face{0}".format(self.fc),0)
			self.showPoint("Face{0}".format(self.fc),1)
			self.showPoint("Face{0}".format(self.fc),2)
		else:
			self.fc = 0
			self.showPoint("Face0",0)
			self.showPoint("Face0",1)
			self.showPoint("Face0",2)
		
	
	def showEntity(self,index):
		if(index < len(self.EntAry)):
			self.EntAry[index].show()
		return
	
	def hideEntity(self,index):
		if(index < len(self.EntAry)):
			self.EntAry[index].hide()
		return
		
	def drawPoints(self,title,points,r,g,b,hd):
		self.points[title] = []
		for pnt in points:
			ls = LineSegs()
			ls.setThickness(3)
			ls.setColor(r, g, b, 1.0)
			ls.moveTo(pnt["X"], pnt["Y"], pnt["Z"])
			ls.drawTo(pnt["X"], pnt["Y"]+0.5, pnt["Z"])
			
			node = ls.create()
			self.points[title].append(render.attachNewNode(node))
			if(hd == True):
				self.points[title][-1].hide()
			
	def showPoint(self,title,index):
		if(title in self.points):
			if(index < len(self.points[title])):
				self.points[title][index].show()
		return
	
	def hidePoint(self,title,index):
		if(title in self.points):
			if(index < len(self.points[title])):
				self.points[title][index].hide()
		return
	
	def destroyModel(self):
		self.nodePath.removeNode()
		self.geomDataAry.clearRows()

























