from tkinter import *
import tkinter.font
import tkinter.messagebox
from  tkinter.scrolledtext import *
from tkinter import ttk
from PIL import Image, ImageTk
import array,sys,time,os
import numpy as np
import bwm
from functools import partial

class materialEditor():
	def __init__(self, root):
		#Entities: Tool bar
		#self.toolbar = Frame(root, bd=1, relief=FLAT)
		#Add Button
		#eaicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\addIcon.png')
		#self.ebtnadd = Button(self.toolbar, width=20, height=20, relief=FLAT, image=eaicon, command = lambda: self.addMaterial())
		#self.ebtnadd.image = eaicon
		#self.ebtnadd.pack(side=LEFT, padx=2, pady=2)
		
		#self.toolbar.pack(side=TOP, fill=X)
		
		#Entity list display
		self.canvas = Canvas(root)
		self.frame = Frame(self.canvas,width=300,bg='white')
		self.scroll = Scrollbar(root, orient="vertical", width=20, command=self.canvas.yview)
		self.canvas.config(yscrollcommand=self.scroll.set)
		
		self.scroll.pack(side=RIGHT, fill=Y)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
		self.canvasframe = self.canvas.create_window((0, 0),window=self.frame,anchor="nw")
		self.frame.bind("<Configure>",self.scrollFunt)
		self.canvas.bind("<Configure>",self.scrollFunt2)

	def scrollFunt2(self, event):
		canvas_width = event.width
		self.canvas.itemconfig(self.canvasframe, width = canvas_width)

	def scrollFunt(self,event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
	
	def loadMaterials(self, mats):
		self.matList = mats
		
		deleteicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\deleteIcon.png')
		
		self.entriesMats = []
		self.matFrames = []
		cnt = 0
		for m in mats:
			entry = []
			#Create Frame
			matFrame = Frame(self.frame, bd=1, relief=RIDGE)
			
			matTools = Frame(matFrame, bd=1, relief=FLAT)
			mat_lbl_0 = Label(matTools,text="Material %d" % (cnt))
			mat_lbl_0.config(font=("Times New Roman", 14))
			mat_lbl_0.pack(side=LEFT)
			#mbtnDel = Button(matTools, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removeMaterial,cnt))
			#mbtnDel.image = deleteicon
			#mbtnDel.pack(side=RIGHT, padx=2, pady=2)
			matTools.pack(side=TOP, fill=X)
			
			#Each material has 7 string
			mat1Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_1 = Label(mat1Frame,text="Diffuse Map", anchor="e", width=10)
			mat_lbl_1.pack(side=LEFT)
			mat_diff = Entry(mat1Frame, width = 30)
			mat_diff.insert(0, m["DiffuseMap"])
			mat_diff.pack(side=LEFT)
			
			mat1Frame.pack(side=TOP, fill=X)
			mat2Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_2 = Label(mat2Frame,text="Light Map", anchor="e", width=10)
			mat_lbl_2.pack(side=LEFT)
			mat_light = Entry(mat2Frame, width = 30)
			mat_light.insert(0, m["LightMap"])
			mat_light.pack(side=LEFT)
			
			mat2Frame.pack(side=TOP, fill=X)
			mat3Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_3 = Label(mat3Frame,text="Foliage Map", anchor="e", width=10)
			mat_lbl_3.pack(side=LEFT)
			mat_fol = Entry(mat3Frame, width = 30)
			mat_fol.insert(0, m["FoliageMap"])
			mat_fol.pack(side=LEFT)
			
			mat3Frame.pack(side=TOP, fill=X)
			mat4Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_4 = Label(mat4Frame,text="Specular Map", anchor="e", width=10)
			mat_lbl_4.pack(side=LEFT)
			mat_spec = Entry(mat4Frame, width = 30)
			mat_spec.insert(0, m["SpecularMap"])
			mat_spec.pack(side=LEFT)
			
			mat4Frame.pack(side=TOP, fill=X)
			mat5Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_5 = Label(mat5Frame,text="Fire Map", anchor="e", width=10)
			mat_lbl_5.pack(side=LEFT)
			mat_fire = Entry(mat5Frame, width = 30)
			mat_fire.insert(0, m["FireMap"])
			mat_fire.pack(side=LEFT)
			
			mat5Frame.pack(side=TOP, fill=X)
			mat6Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_6 = Label(mat6Frame,text="Normal Map", anchor="e", width=10)
			mat_lbl_6.pack(side=LEFT)
			mat_norm = Entry(mat6Frame, width = 30)
			mat_norm.insert(0, m["NormalMap"])
			mat_norm.pack(side=LEFT)
			
			mat6Frame.pack(side=TOP, fill=X)
			mat7Frame = Frame(matFrame, bd=1, relief=FLAT)
			
			mat_lbl_7 = Label(mat7Frame,text="Type", anchor="e", width=10)
			mat_lbl_7.pack(side=LEFT)
			mat_type = Entry(mat7Frame, width = 30)
			mat_type.insert(0, m["Type"])
			mat_type.pack(side=LEFT)
			
			mat7Frame.pack(side=TOP, fill=X)
			matFrame.pack(side=TOP, fill=X)
			
			mat_diff.bind("<Button-1>", lambda e, o = mat_diff: self.focus_me(e,o))
			entry.append(mat_diff)
			mat_light.bind("<Button-1>", lambda e, o = mat_light: self.focus_me(e,o))
			entry.append(mat_light)
			mat_fol.bind("<Button-1>", lambda e, o = mat_fol: self.focus_me(e,o))
			entry.append(mat_fol)
			mat_spec.bind("<Button-1>", lambda e, o = mat_spec: self.focus_me(e,o))
			entry.append(mat_spec)
			mat_fire.bind("<Button-1>", lambda e, o = mat_fire: self.focus_me(e,o))
			entry.append(mat_fire)
			mat_norm.bind("<Button-1>", lambda e, o = mat_norm: self.focus_me(e,o))
			entry.append(mat_norm)
			mat_type.bind("<Button-1>", lambda e, o = mat_type: self.focus_me(e,o))
			entry.append(mat_type)
			self.entriesMats.append(entry)
			
			self.matFrames.append(matFrame)
			
			cnt += 1
			
	def addMaterial(self):
		mat = {}
		mat["DiffuseMap"] = ""
		mat["LightMap"] = ""
		mat["FoliageMap"] = ""
		mat["SpecularMap"] = ""
		mat["FireMap"] = ""
		mat["NormalMap"] = ""
		mat["Type"] = ""
		
		self.matList.append(mat)
		self.reloadMaterials()
		
	def removeMaterial(self,index):
		del self.matList[index]
		self.reloadMaterials()

	def saveMaterials(self):
		cnt = 0
		for m in self.entriesMats:
			self.matList[cnt]["DiffuseMap"] = m[0].get()
			self.matList[cnt]["LightMap"] = m[1].get()
			self.matList[cnt]["FoliageMap"] = m[2].get()
			self.matList[cnt]["SpecularMap"] = m[3].get()
			self.matList[cnt]["FireMap"] = m[4].get()
			self.matList[cnt]["NormalMap"] = m[5].get()
			self.matList[cnt]["Type"] = m[6].get()
			
			cnt += 1
		#return self.matList
			
	def reloadMaterials(self):
		#Delete frames
		for x in range(0, len(self.matFrames)):
			self.matFrames[x].destroy()
		self.loadMaterials(self.matList)
		
	def emptyData(self):
		#Delete frames
		for x in range(0, len(self.matFrames)):
			self.matFrames[x].destroy()
		del self.matList
	
	def focus_me(self,e,o):
		o.focus_force()
