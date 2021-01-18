from tkinter import *
import tkinter.font
import tkinter.filedialog as tkFileDialog
from tkinter import messagebox
from  tkinter.scrolledtext import *
from tkinter import ttk
from PIL import Image, ImageTk
import array,sys,time,os
import numpy as np
import ntpath
import bwm
import obj
import basicEditor
import entityEditor
import materialEditor
import meshEditor
import unkPointEditor
from functools import partial
from pprint import pprint

import panda3d_integration


class bwSculpting():
	def __init__(self,root, filename):
		self.root = root
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
		self.m_defined = 0
		
		#Interprate file name
		self.fname = filename
		self.f_dir, self.f_name = ntpath.split(filename)
		exts = self.f_name.split('.')
		self.f_ext = exts[len(exts)-1]
		
		#Process the file
		if(self.f_ext == "bwm"):
			rtn = self.bwmInit(root, filename)
		elif(self.f_ext == "obj"):
			self.objInit(root, filename)
			
	def loadFile(self,filename):
		self.m_defined = 0
		
		#Interprate file name
		self.fname = filename
		self.f_dir, self.f_name = ntpath.split(filename)
		exts = self.f_name.split('.')
		self.f_ext = exts[len(exts)-1]
		
		#Process the file
		if(self.f_ext == "bwm"):
			del self.model #Remove the current model
			self.model = bwm.bwm() #Create new bwm object
			
			self.Err = 0
			rtn = self.model.loadFromFile(filename) #Reads the file returns either errors codes or success
			
			if(rtn < 3):
				return 1 #Failure in header information
			elif(rtn != 3):
				self.Err = rtn #Record whichever error this is, we shall continue anyways
			
			#3D View
			#Empty scene
			self.p3d.destroyModel()
			#Create new
			self.p3d.displayBWM(self.model)	
				
			#Load side panel information
			self.entityEdit.emptyData()
			self.entityEdit.loadEntities(self.model.m["Entities"],self.p3d)
			self.materialsEdit.emptyData()
			self.materialsEdit.loadMaterials(self.model.m["Materials"])
			self.meshesEdit.emptyData()
			self.meshesEdit.loadMeshes(self.model.m["Meshs"])
			self.unkPointEdit.emptyData()
			self.unkPointEdit.loadPoints("Unknowns 1",self.model.m["Un1"])
			self.unkPointEdit.loadPoints("Unknowns 2",self.model.m["Un2"])
			self.basicEdit.emptyData()
			self.basicEdit.loadInformation(self.model,1,self.Err)
			
		
		
	def bwmInit(self, root, filename):
		#Black and White Model file
		self.model = bwm.bwm()#Create new bwm object
		rtn = 3 #Assume success
		self.Err = 0
		rtn = self.model.loadFromFile(filename)#Reads the file returns either errors codes or success
		
		if(rtn < 3):
			return 1 #Failure in header information
		elif(rtn != 3):
			self.Err = rtn #Record whichever error this is, we shall continue anyways
		
		#Establish Sculpting widget container
		self.frm = Frame(root)
		self.frm.pack(fill=BOTH, expand=1)
		
		#Toolbar: Open, Save, ?
		self.tools = Frame(self.frm, bd=1, relief=FLAT)
		#Save Button
		sicon = PhotoImage(file=self.ROOT_DIR + '\\Images\\Icons\\saveIcon.png')
		self.btnSave = Button(self.tools, image=sicon, width=20, height=20, relief=FLAT, command = lambda: self.saveModel())
		self.btnSave.image = sicon
		if(self.Err != 0):
			self.btnSave["state"] = DISABLED
		self.btnSave.pack(side=LEFT, padx=2, pady=2)
		
		#Tool bar
		cicon = PhotoImage(file=self.ROOT_DIR + '\\Images\\Icons\\convertIcon.png')
		self.btnConvert = Button(self.tools, image=cicon, width=20, height=20, relief=FLAT, command= lambda: self.fileDialog("convert"))
		if(self.Err != 0):
			self.btnConvert["state"] = DISABLED
		self.btnConvert.image = cicon
		self.btnConvert.pack(side=LEFT, padx=2, pady=2)
		self.tools.pack(side=TOP, fill=X)
		
		#Side panel: Display information about the model
		#	Alignment, Meshs, Materials, Entities, Paths, etc...
		self.sidebar = Frame(self.frm, bg='white', width=300)
		self.sidebar.pack(side=LEFT, fill=Y)
		
		#Side panel tabs
		self.sideParent = ttk.Notebook(self.sidebar, width=300)
		self.sideTabModel = Frame(self.sideParent)
		self.sideTabEntities = Frame(self.sideParent)
		self.sideTabMesh = Frame(self.sideParent)
		self.sideTabMaterial = Frame(self.sideParent)
		self.sideTabUnk1 = Frame(self.sideParent)
		self.sideTabBones = Frame(self.sideParent)
		
		self.sideParent.add(self.sideTabModel,text="Model")
		self.sideParent.add(self.sideTabEntities,text="Entities")
		self.sideParent.add(self.sideTabMaterial,text="Materials")
		self.sideParent.add(self.sideTabMesh,text="Meshes")
		self.sideParent.add(self.sideTabUnk1,text="Unk1s")
		self.sideParent.add(self.sideTabBones,text="Bones")
		
		self.sideParent.pack(side=LEFT, fill='both')
		
		self.sideReSize = Frame(self.frm, bg='lightgray', width=5, cursor="sb_h_double_arrow")
		self.sideReSize.pack(side=LEFT, fill=Y)
		self.pnlResize = False
		self.sideReSize.bind("<Button-1>", self.panelResizeSet)
		self.sideReSize.bind("<B1-Motion>", self.panelResize) 
		self.sideReSize.bind("<ButtonRelease-1>", self.panelResizeRel)
		
		#Open GL frame
		self.gphFrm = Frame(self.frm)
		self.gphFrm.pack(side=RIGHT, fill=BOTH, expand=1)
		#self.gph = glController(self.gphFrm)
		
		self.p3d = panda3d_integration.TkinterGuiClass(self.gphFrm, ())
		self.p3d.displayBWM(self.model)
		
		self.basicEdit = basicEditor.basicEditor(self.sideTabModel)
		self.entityEdit = entityEditor.entityEditor(self.sideTabEntities)
		self.materialsEdit = materialEditor.materialEditor(self.sideTabMaterial)
		self.meshesEdit = meshEditor.meshEditor(self.sideTabMesh)
		self.unkPointEdit = unkPointEditor.unkPointEditor(self.sideTabUnk1,self.p3d)
		
		#Load information
		self.entityEdit.loadEntities(self.model.m["Entities"],self.p3d)
		self.materialsEdit.loadMaterials(self.model.m["Materials"])
		self.meshesEdit.loadMeshes(self.model.m["Meshs"])
		self.unkPointEdit.loadPoints("Unknowns 1",self.model.m["Un1"])
		self.unkPointEdit.loadPoints("Unknowns 2",self.model.m["Un2"])
		self.basicEdit.loadInformation(self.model,1,self.Err)
		
		
		self.m_defined = 1
		return self.Err
		
	def objInit(self, root, filename):
		#Standard obj file format
		self.obj = obj.obj()
		self.Err = 0
		try:
			self.model = self.obj.loadFromFile(filename)
		except Exception as e:
			messagebox.showerror(title="Error", message=e)
			return 0
		
		#Establish Sculpting widget container
		self.frm = Frame(root)
		self.frm.pack(fill=BOTH, expand=1)
		
		#Toolbar: Convertor
		self.tools = Frame(self.frm, bd=1, relief=FLAT)
		
		#Tool bar
		cicon = PhotoImage(file=self.ROOT_DIR + '\\Images\\Icons\\convertIcon.png')
		self.btnConvert = Button(self.tools, image=cicon, width=20, height=20, relief=FLAT, command= lambda: self.fileDialog("convert"))
		if(self.Err != 0):
			self.btnConvert["state"] = DISABLED
		self.btnConvert.image = cicon
		self.btnConvert.pack(side=LEFT, padx=2, pady=2)
		self.tools.pack(side=TOP, fill=X)
		
		#Side panel: Display information about the model
		#	Alignment, Meshs, Materials, Entities, Paths, etc...
		self.sidebar = Frame(self.frm, bg='white', width=300)
		self.sidebar.pack(side=LEFT, fill=Y)
		
		#Side panel tabs
		self.sideParent = ttk.Notebook(self.sidebar, width=300)
		self.sideTabModel = Frame(self.sideParent)
		
		self.sideParent.add(self.sideTabModel,text="Model")
		
		self.sideParent.pack(side=LEFT, fill='both')
		
		self.sideReSize = Frame(self.frm, bg='lightgray', width=5, cursor="sb_h_double_arrow")
		self.sideReSize.pack(side=LEFT, fill=Y)
		self.pnlResize = False
		self.sideReSize.bind("<Button-1>", self.panelResizeSet)
		self.sideReSize.bind("<B1-Motion>", self.panelResize) 
		self.sideReSize.bind("<ButtonRelease-1>", self.panelResizeRel)
		
		self.basicEdit = basicEditor.basicEditor(self.sideTabModel)
		self.basicEdit.loadInformation(self.model,2,self.Err)
		
		#Open GL frame
		#self.gphFrm = Frame(self.frm)
		#self.gphFrm.pack(side=RIGHT, fill=BOTH, expand=1)
		#self.gph = glController(self.gphFrm)
		#testlbl = Label(self.sidebar, text="Test").pack(side="left", expand=1)
			
		
		self.m_defined = 2
		return 1
		
	#--------------------Opening Files--------------------
	def fileDialog(self,tp):
		#Open file dialog
		if(tp == "model"):
			fname = tkFileDialog.askopenfilename(initialdir = self.ROOT_DIR,filetypes = (("BW Models","*.bwm"),("Object Models","*.obj"),("all files","*.*")))
		elif(tp == "convert"):
			fname = tkFileDialog.asksaveasfilename(initialdir = self.ROOT_DIR,filetypes=[("BW Models", '*.bwm')])
		if not fname: return
		
		if(tp == "model"):
			self.fileOpen(fname)
		elif(tp == "convert"):
			self.convertObjToBwm(fname)
	
	def convertObjToBwm(self,filename):
		#check to make sure the obj model is defined
		if(self.m_defined != 2):
			return
		b = bwm.bwm()#Create new bwm object
		b.m = self.obj.convertToBWM()
		if(b.m != 0):
			fdir, fname = ntpath.split(filename)
			if(fname.find(".bwm") != -1):
				name, exts = fname.split('.')
			else:
				name = fname
			b.fln = fdir + "/" + name + ".bwm"
			
			b.savebwm()
		else:
			print("Conversion Failed")
	
	#----------------------Saving Files----------------------
	def saveModel(self):
		if(self.m_defined == 1):
			self.basicEdit.save_bwm_info(self.model)
			self.materialsEdit.saveMaterials()
			self.unkPointEdit.savePoints()
			self.model.savebwm()
		return
	
	#------------Resizing side panel functionality------------
	def panelResizeSet(self,event):
		self.pnlResize = True
	
	def panelResize(self,event):
		if(self.pnlResize):
			abs_coord_x = self.root.winfo_pointerx() - self.root.winfo_rootx()
			if(abs_coord_x > 0):
				self.sidebar.config(width=abs_coord_x)
				self.sideParent.config(width=abs_coord_x)
	
	def panelResizeRel(self,event):
		self.pnlResize = False

#class glController():
#	def __init__(self,root):
#		self.root = root
#		
#		self.gph = AppOgl(root,width=320,height=200)
#		
#		self.gph.pack(fill=BOTH, expand=1)
#		self.gph.animate = 1
#		self.gph.after(20, self.gph.printContext)
#		self.gph.mainloop()
#
#class AppOgl(OpenGLFrame):
#
#	def initgl(self):
#		"""Initalize gl states when the frame is created"""
#		GL.glViewport(0, 0, self.width, self.height)
#		GL.glClearColor(0.0, 0.0, 0.0, 0.0)    
#		self.start = time.time()
#		self.nframes = 0
#
#	def redraw(self):
#		"""Render a single frame"""
#		GL.glClear(GL.GL_COLOR_BUFFER_BIT)
#		tm = time.time() - self.start
#		self.nframes += 1
