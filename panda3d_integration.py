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
			self.texAttrib_Evil = TextureAttrib.make()#Storage for multiple texture stages which can be applied to a geomtery node
			self.texAttrib_Good = TextureAttrib.make()#Storage for multiple texture stages which can be applied to a geomtery node
			
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
				self.texAttrib_Evil = self.texAttrib.addOnStage(stg, texture)
				
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
				self.texAttrib_Good = self.texAttrib.addOnStage(stg, texture)
			
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
				continue
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
		
		#Export data to a file for use later...
		loc = settings.locations["ConfigFolder"] + "\\Models\\" + name
		if(os.path.exists(loc) == False):
			os.makedirs(loc)
		
		self.nodePath = render.attachNewNode(geometry) #setRenderModeWireframe
		self.nodePath.setTransparency(TransparencyAttrib.M_alpha)
		self.nodePath.setTextureOff(0)
		#self.nodePath.setRenderModeWireframe()
		
		#Generate model file
		fl = loc+"\\"+name+".bam"
		if(os.path.exists(fl) == False):
			f = open(fl,"w+")
			f.close()
		self.nodePath.writeBamFile(settings.convertToLinux(fl))
		#Copy textures over to that location
		
		self.base.disableMouse() # if you leave mouse mode enabled camera position will be governed by Panda mouse control
		
		self.base.useDrive()
		self.base.useTrackball()
		
		self.base.trackball.node().setPos(0, model["Radius"]+20, 0)
		self.base.trackball.node().setP(120)
		
		self.drawEntities(model["Entities"])
		
		self.points = {}
		self.drawPoints("Unknowns 1",model["Un1"],0,0,1,True)
		self.drawPoints("Unknowns 2",model["Un2"],0,1,1,True)
		
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

























