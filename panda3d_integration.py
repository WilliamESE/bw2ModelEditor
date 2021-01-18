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
		
		self.mousedown1 = False
		self.wheelChanged = False
		self.distance = 94
		self.S_t = 0
		self.S_b = 0
		self.S_mx = 0
		self.S_my = 0
		self.theta = 31.67
		self.beta = 0
		self.sensitivityMouse = 50
		self.sensitivityWheel = 5
		self.base.accept('mouse1', self.mousedown)
		self.base.accept('mouse1-up', self.mouseup)
		self.base.accept('wheel_up', self.wheeldown)
		self.base.accept('wheel_down', self.wheelup)
		self.base.taskMgr.add(self.objectRotation, "RotateObject")
		
		self.frame.bind("<Configure>",self.resized)
	
	def mousedown(self):
		self.mousedown1 = True
		self.S_t = self.theta
		self.S_b = self.beta
		
		self.S_mx = self.base.mouseWatcherNode.getMouseX()
		self.S_my = self.base.mouseWatcherNode.getMouseY()
		
	def mouseup(self):
		self.mousedown1 = False
		
	def wheeldown(self):
		self.wheelChanged = True
		self.distance -= self.sensitivityWheel
		self.S_t = self.theta
		self.S_b = self.beta
		
		self.S_mx = self.base.mouseWatcherNode.getMouseX()
		self.S_my = self.base.mouseWatcherNode.getMouseY()
		
	def wheelup(self):
		self.wheelChanged = True
		self.distance += self.sensitivityWheel
		self.S_t = self.theta
		self.S_b = self.beta
		
		self.S_mx = self.base.mouseWatcherNode.getMouseX()
		self.S_my = self.base.mouseWatcherNode.getMouseY()
	
	def objectRotation(self, task):
		if((self.mousedown1 == True) or (self.wheelChanged == True)):
			C_mx = self.base.mouseWatcherNode.getMouseX() #A value between -1 and 1, where 0 is the center. Negative to the left, positive to the right
			C_my = self.base.mouseWatcherNode.getMouseY()
			
			self.theta = self.S_t + ((self.S_mx - C_mx) * self.sensitivityMouse)
			self.beta = self.S_b + ((self.S_my - C_my) * self.sensitivityMouse)
			
			self.theta = self.theta - (360 * floor(self.theta / 360))
			
			self.setCamPos(self.theta, self.beta, self.distance)
			
			self.base.camera.lookAt(self.o_x,self.o_y,self.o_z)
			self.base.camera.setR(90)
			if((self.theta < 0) and (self.theta > -180)):
				self.base.camera.setR(-90)
			if(self.theta > 180):
				self.base.camera.setR(-90)
			
			self.wheelChanged = False
			
		return task.again
	
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
		
	def displayBWM(self,model):
		#Loop through the meshes and insert the vertices associated with that mesh (This is a node)
		#	Render the node and apply the texture
		#	The issue is that the I'll have to integate the indices properly for each mesh as well
		#Actually each mesh has a set of materials, those materials would be the "node" so to speak, however I wonder if there is ever any overlap
		t2 = False
		t3 = False
		fmt = GeomVertexArrayFormat()
		fmt.addColumn("vertex",3,Geom.NTFloat32,Geom.CPoint)
		fmt.addColumn("normal",3,Geom.NTFloat32,Geom.CNormal)
		fmt.addColumn("texcoord",2,Geom.NTFloat32,Geom.CTexcoord)
		if(t2 == True):
			fmt.addColumn("texcoord2",2,Geom.NTFloat32,Geom.CTexcoord)
		if(t3 == True):
			fmt.addColumn("texcoord3",2,Geom.NTFloat32,Geom.CTexcoord)
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
		texcoord = GeomVertexWriter(self.vnode, 'texcoord')
		if(t2 == True):
			texcoord2 = GeomVertexWriter(self.vnode, 'texcoord2')
		if(t3 == True):
			texcoord3 = GeomVertexWriter(self.vnode, 'texcoord3')
		
		#Mat0: 6634
		#Mat1: 6634 -> 7531
		cnt=0
		for vtx in range(0,model.m["cntVerticies"]):
			p = model.m["Vertices"][vtx]["Position"]
			n = model.m["Vertices"][vtx]["Normal"]
			v = model.m["Vertices"][vtx]["V"]
			u = model.m["Vertices"][vtx]["U"]
			#if(cnt < 7538):
			#	if("Unknown1" in model.m["Vertices"][vtx]):
			#		print("{0}: U2 {1}, V2 {2}; U3 {3}, V3 {4}".format(cnt,round(model.m["Vertices"][vtx]["Unknown1"][0],3),round(model.m["Vertices"][vtx]["Unknown1"][1],3),round(model.m["Vertices"][vtx]["Unknown2"][0],3),round(model.m["Vertices"][vtx]["Unknown2"][1],3)))
			
			vertices.addData3f(p["X"],p["Y"],p["Z"])
			normals.addData3f(n["X"],n["Y"],n["Z"])
			texcoord.addData2(u, -v)
			cnt+=1
		
		
		cnt=0
		cntm = 0
		matTex = []
		for mh in model.m["Meshs"]:
			#if(model.m["cntMeshs"] > 1):
			#	if(cntm == (model.m["cntMeshs"] - 1)):
			#		break
			for mt in mh["Materials"]:				
				nm = mh["Name"] + "_" + str(mt["MaterialRef"])
				#Collect faces
				ptv = GeomTriangles(Geom.UHStatic)
				for i in range(mt["offIndices"],mt["offIndices"] + mt["cntIndices"],3):
					ptv.addVertices(model.m["Indices"][i],model.m["Indices"][i+1],model.m["Indices"][i+2])
				
				geom = Geom(self.vnode)
				geom.addPrimitive(ptv)
				nodes.addGeom(geom)
				
				if(model.m["Materials"][mt["MaterialRef"]]["DiffuseMap"] == ""):
					txLoc2 = txLoc + "/t_courtyardground.dds"
				else:
					txLoc2 = txLoc + "/" + model.m["Materials"][mt["MaterialRef"]]["DiffuseMap"]
				tex = loader.loadTexture(txLoc2)
				ts = TextureStage(nm)
				ts.setMode(TextureStage.MModulate)
				txa = TextureAttrib.make()
				txa = txa.addOnStage(ts, tex)
				matTex.append(txa)
				#self.nodePath.setTexture(tex)
			cntm+=1
		for n in range(nodes.getNumGeoms()):
			if(matTex[n] == None):
				continue
			tx = matTex[n]
			newRenderState = nodes.getGeomState(n).addAttrib(tx,1)
			nodes.setGeomState(n, newRenderState)
		
		self.nodePath = render.attachNewNode(nodes) #setRenderModeWireframe
		self.nodePath.setTransparency(TransparencyAttrib.M_alpha)
		self.nodePath.setTextureOff(0)
		#self.nodePath.setRenderModeWireframe()
		self.base.camera.reparentTo(self.nodePath)
		
		self.base.disableMouse() # if you leave mouse mode enabled camera position will be governed by Panda mouse control
		
		self.o_x = (model.m["BoxPoint1"]["X"] + model.m["BoxPoint2"]["X"]) / 2
		self.o_y = (model.m["BoxPoint1"]["Y"] + model.m["BoxPoint2"]["Y"]) / 2
		self.o_z = (model.m["BoxPoint1"]["Z"] + model.m["BoxPoint2"]["Z"]) / 2
		
		x = 80
		y = 50
		z = 0
		#self.base.camera.setPos(x, y, z)
		self.setCamPos(31.67,0,94)
		self.base.camera.lookAt(self.o_x,self.o_y,self.o_z)
		self.base.camera.setR(90)
		#self.lookat(self.o_x,self.o_y,self.o_z,x,y,z)
		#self.base.camera.lookat(self.cubeNodePath)
		
		self.drawEntities(model.m["Entities"])
		self.points = {}
		self.drawPoints("Unknowns 1",model.m["Un1"],0,0,1,True)
		self.drawPoints("Unknowns 2",model.m["Un2"],0,1,1,True)
		#self.drawPoints("Interaction",model.m["Meshs"][0]["Points"],1,1,0,False)
		
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
			ls.setThickness(5)
		
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
		
	def setCamPos(self, ang1, ang2, dist):
		
		r_aRound = radians(ang2)
		r_aUp = radians(ang1)
		
		x = self.o_x + dist * sin(r_aUp) * cos(r_aRound)#* cos(r_aRound)
		y = self.o_y + dist * sin(r_aUp) * sin(r_aRound)#* sin(r_aRound) * sin(r_aUp)
		z = self.o_z + dist * cos(r_aUp) #* sin(r_aRound) * cos(r_aUp)
		
		self.base.camera.setPos(x, y, z)	
	
	def destroyModel(self):
		self.nodePath.removeNode()
		self.vnode.clearRows()

























