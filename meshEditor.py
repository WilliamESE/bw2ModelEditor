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

class meshEditor():
	def __init__(self, root):
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
		#Entities: Tool bar
		#self.toolbar = Frame(root, bd=1, relief=FLAT)
		##Add Button
		#eaicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\addIcon.png')
		#self.ebtnadd = Button(self.toolbar, width=20, height=20, relief=FLAT, image=eaicon, command = lambda: self.addMaterial())
		#self.ebtnadd.image = eaicon
		#self.ebtnadd.pack(side=LEFT, padx=2, pady=2)
		#
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
		
	def matscrollFunt2(self, event):
		canvas_width = event.width
		self.matcanvas.itemconfig(self.matcanvasframe, width = canvas_width)

	def matscrollFunt(self,event):
		self.matcanvas.configure(scrollregion=self.matcanvas.bbox("all"))
		
	def loadMeshes(self, meshes):
		self.meshList = meshes
		#Pre-processing
		editicon = PhotoImage(file=self.ROOT_DIR + '\\Images\\Icons\\editIcon.png')
		deleteicon = PhotoImage(file=self.ROOT_DIR + '\\Images\\Icons\\deleteIcon.png')
		
		#Loop through entities
		self.meshFrames = []
		cnt = 0
		for mesh in meshes:
			#Create Frame
			if((cnt % 2) == 0):
				meshFrm = Frame(self.frame, bd=1, relief=FLAT)
			else:
				meshFrm = Frame(self.frame, bd=1, relief=FLAT, bg="light blue")
			
			#Text Name
			if((cnt % 2) == 0):
				btxt = Label(meshFrm,text=mesh["Name"])
			else:
				btxt = Label(meshFrm,text=mesh["Name"], bg="light blue")
			btxt.pack(side=LEFT, padx=2, pady=2)
			
			##Delete Button
			#if((cnt % 2) == 0):
			#	dbtn = Button(meshFrm, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removeMesh, cnt))
			#else:
			#	dbtn = Button(meshFrm, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removeMesh, cnt), bg="light blue")
			#dbtn.image = deleteicon
			#dbtn.pack(side=RIGHT, padx=2, pady=2)
			
			#Edit Button
			if((cnt % 2) == 0):
				ebtn = Button(meshFrm, width=20, height=20, relief=FLAT, image=editicon, command = partial(self.editMesh_init, cnt))
			else:
				ebtn = Button(meshFrm, width=20, height=20, relief=FLAT, image=editicon, command = partial(self.editMesh_init, cnt), bg="light blue")
			ebtn.image = editicon
			ebtn.pack(side=RIGHT, padx=2, pady=2)
			
			#Pack
			meshFrm.pack(side=TOP, fill=X)
			self.meshFrames.append(meshFrm)
			cnt += 1
	
	def reloadMeshes(self):
		#Delete frames
		for x in range(0, len(self.meshFrames)):
			self.meshFrames[x].destroy()
		#Reload the list
		self.loadMeshes(self.meshList)
		
	def emptyData(self):
		for x in range(0, len(self.meshFrames)):
			self.meshFrames[x].destroy()
		del self.meshList
	
	def removeMesh(self,index):
		del self.meshList[index]
		
	def editMesh_init(self,index):
		self.editor = index
		self.openEditor(self.meshList[index])
	
	#Saving
	def saveMesh(self):
		idx = self.editor
		#Loop through the settings
		for s in self.mshItems:
			if(s["Item"] == "Mesh"):
				if(s["Index"] == "Name"):
					self.meshList[idx][s["Index"]] = s["Entry"].get()
				elif(s["Index"] == "Volume"):
					self.meshList[idx][s["Index"]] = float(s["Entry"].get())
				else:
					self.meshList[idx][s["Index"]] = int(s["Entry"].get())
			elif(s["Item"] == "Mat"):
				#These are all ints
				#	["Materials"][Material index]["Setting"]
				self.meshList[idx]["Materials"][s["Number"]][s["Index"]] = int(s["Entry"].get())
			elif(s["Item"] == "pnt"):
				self.meshList[idx]["Points"][s["Number"]]["X"] = float(s["EntryX"].get())
				self.meshList[idx]["Points"][s["Number"]]["Y"] = float(s["EntryY"].get())
				self.meshList[idx]["Points"][s["Number"]]["Z"] = float(s["EntryZ"].get())
		self.reloadMeshes()
		self.Mesheditor.destroy()
		
	def cancelMeshEdit(self):
		self.Mesheditor.destroy()
		
	#Window
	def openEditor(self,mesh):
		#There are three sections, the first is the direct settings involved in the mesh; second is the material references; and third is the interaction information.
		self.mshItems = []
		mshNames = ["Name","Face Count","Ind Offset","Ind Count","Ver Offset","Ver Count","Unk 1","Volume","Unk 3","Unk 4","Unk 5","Unk 6"]
		mshElements = ["Name","cntFaces","offIndices","cntIndices","offVertices","cntVertices","Unknown1","Volume","Unknown3","Unknown4","Unknown5","Unknown6"]
		
		self.Mesheditor = Tk()
		self.Mesheditor.wm_title("Mesh Editor")
		self.Mesheditor.geometry("%dx%d+0+0" % (600, 350))
		
		mshSettings = Frame(self.Mesheditor, bd=1, relief=FLAT)
		
		set_1frm = Frame(mshSettings, bd=1, relief=FLAT, width=200)
		
		matTools = Frame(set_1frm, bd=1, relief=FLAT, width=200)
		mTitle_lbl = Label(matTools,text="Mesh Properties",anchor="w")
		mTitle_lbl.config(font=("Times New Roman", 14))
		mTitle_lbl.pack(side=LEFT)
		matTools.pack(side=TOP, fill=X)
		
		for cnt in range(0, len(mshNames)):
			mshfrm = Frame(set_1frm, bd=1, relief=FLAT)
			
			mshlbl = Label(mshfrm,text=mshNames[cnt], anchor="e", width=9)
			mshlbl.pack(side=LEFT)
			mshEntr =  Entry(mshfrm, width = 15)
			mshEntr.insert(0, mesh[mshElements[cnt]])
			mshEntr.pack(side=LEFT)
			
			mshfrm.pack(side=TOP, fill=X)
			
			items = {}
			items["Item"] = "Mesh"
			items["Index"] = mshElements[cnt]
			items["Entry"] = mshEntr
			
			self.mshItems.append(items)
		
		set_1frm.pack(side=LEFT, fill=Y, padx=2, pady=2)
		
		#Material section
		set_2frm = Frame(mshSettings, bd=1, relief=GROOVE, width=200)
		
		
		self.matcanvas = Canvas(set_2frm, width=200)
		self.matframe = Frame(self.matcanvas,bg='white', width=200)
		self.matscroll = Scrollbar(set_2frm, orient="vertical", command=self.matcanvas.yview, width=20)
		self.matcanvas.config(yscrollcommand=self.matscroll.set)
		
		self.matscroll.pack(side=RIGHT, fill=Y)
		self.matcanvas.pack(side=LEFT, fill=BOTH, expand=True)
		self.matcanvasframe = self.matcanvas.create_window((0, 0),window=self.matframe,anchor="nw")
		self.matframe.bind("<Configure>",self.matscrollFunt)
		self.matcanvas.bind("<Configure>",self.matscrollFunt2)
		
		matNames = ["REF","Ind offset","Ind count","Ver offset","Ver count","Face offset","Face count","Unk"]
		matElements = ["MaterialRef","offIndices","cntIndices","offVertex","cntVertex","offFaces","cntFaces","Unknown"]
		cnt = 0
		for mat in mesh["Materials"]:
			mshmatfrm = Frame(self.matframe, bd=1, relief=FLAT)
			
			matTools = Frame(mshmatfrm, bd=1, relief=FLAT)
			mTitle_lbl = Label(matTools,text="Material: %d" % cnt)
			mTitle_lbl.config(font=("Times New Roman", 14))
			mTitle_lbl.pack(side=LEFT)
			matTools.pack(side=TOP, fill=X)
			
			for ele in range(0, len(matNames)):
				mat_ele_frm = Frame(mshmatfrm, bd=1, relief=FLAT)
				
				matlbl = Label(mat_ele_frm,text=matNames[ele], anchor="e", width=8)
				matlbl.pack(side=LEFT)
				matEntr =  Entry(mat_ele_frm, width = 22)
				matEntr.insert(0, mat[matElements[ele]])
				matEntr.pack(side=LEFT)
				
				mat_ele_frm.pack(side=TOP, fill=X)
				
				items = {}
				items["Item"] = "Mat"
				items["Number"] = cnt
				items["Index"] = matElements[ele]
				items["Entry"] = matEntr
				
				self.mshItems.append(items)
				
			cnt+=1
			mshmatfrm.pack(side=TOP, fill=X)
			
		set_2frm.pack(side=LEFT,fill=Y)
		
		set_3frm = Frame(mshSettings, bd=1, relief=FLAT, width=200)
		mTitle_lbl = Label(set_3frm,text="Interaction Information",anchor="w")
		mTitle_lbl.config(font=("Times New Roman", 14))
		mTitle_lbl.pack(side=TOP)
		#Interaction information
		cnt = 0
		pntnames = ["Point 1","Point 2","Point 3","Point 4","Point 5","Point 6","Point 7","Point 8","Point 9"]
		for pnt in mesh["Points"]:
			pnt_ele_frm = Frame(set_3frm, bd=1, relief=FLAT)
			
			pnt_lbl = Label(pnt_ele_frm,text=pntnames[cnt],width=6,anchor="w")
			pnt_lbl.pack(side=LEFT)
			
			pnt_entryX = Entry(pnt_ele_frm, width = 6)
			pnt_entryX.insert(0, round(pnt["X"],3))
			pnt_entryX.pack(side=LEFT)
			pnt_entryY = Entry(pnt_ele_frm, width = 6)
			pnt_entryY.insert(0, round(pnt["Y"],3))
			pnt_entryY.pack(side=LEFT)
			pnt_entryZ = Entry(pnt_ele_frm, width = 6)
			pnt_entryZ.insert(0, round(pnt["Z"],3))
			pnt_entryZ.pack(side=LEFT)
			
			pnt_ele_frm.pack(side=TOP, fill=X)
			
			items = {}
			items["Item"] = "pnt"
			items["Number"] = cnt
			items["EntryX"] = pnt_entryX
			items["EntryY"] = pnt_entryY
			items["EntryZ"] = pnt_entryZ
			cnt+=1
			
			self.mshItems.append(items)
			
		set_3frm.pack(side=LEFT,fill=Y)
		
		mshSettings.pack(side=TOP,fill=X)
		#Buttons
		mshFrmBTN = Frame(self.Mesheditor, bd=1, relief=FLAT)
		end_Save = Button(mshFrmBTN, text="Save", command = lambda: self.saveMesh())
		end_Save.pack(side=RIGHT)
		ent_Can = Button(mshFrmBTN, text="Cancel", command = lambda: self.cancelMeshEdit())
		ent_Can.pack(side=RIGHT)
		mshFrmBTN.pack(side=BOTTOM, fill=X)
		
		self.Mesheditor.mainloop()
