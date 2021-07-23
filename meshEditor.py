from tkinter import *
import tkinter.font
import tkinter.messagebox
import settings
from  tkinter.scrolledtext import *
from tkinter import ttk
from PIL import Image, ImageTk as pil
import array,sys,time,os
import numpy as np
import bwm
from functools import partial

class meshEditor():
	def __init__(self, root):
		self.root = root
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
		#Entities: Tool bar
		#self.toolbar = Frame(root, bd=1, relief=FLAT)
		##Add Button
		#eaicon = pil.PhotoImage(file=settings.icons["Add"])
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
		editicon = pil.PhotoImage(file=settings.icons["Edit"])
		deleteicon = pil.PhotoImage(file=settings.icons["Delete"])
		
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
		meshResult = self.itemDialog(self.root, self.meshList[index])
		if(meshResult.state == "Okay"):
			self.meshList[index] = meshResult.mesh
			self.reloadMeshes()
		
	class itemDialog(simpledialog.Dialog):
		def __init__(self, parent, mesh):
			self.mesh = mesh
			self.state = "Cancel"
			self.mshItems = []
			super().__init__(parent, "Mesh Editor")
			
		def body(self, frame):
			#Data information in a nicely organized array to make this more streamlined
			mshNames = ["Name","Face Count","Ind Offset","Ind Count","Ver Offset","Ver Count","Unk 1","Volume","Unk 3","Unk 4","Unk 5","Unk 6"]
			mshElements = ["Name","cntFaces","offIndices","cntIndices","offVertices","cntVertices","Unknown1","Volume","Unknown3","Unknown4","Unknown5","Unknown6"]
			
			#Section 1 is the mesh's general properties		
			meshS1_frm = Frame(frame, bd=1, relief=FLAT, width=200)
			
			#Title
			s1Title_frm = Frame(meshS1_frm, bd=1, relief=FLAT, width=200)
			s1Title = Label(s1Title_frm,text="Mesh Properties",anchor="w")
			s1Title.config(font=("Times New Roman", 14))
			s1Title.pack(side=LEFT)
			s1Title_frm.pack(side=TOP, fill=X)
			
			#Settigns
			for cnt in range(0, len(mshNames)):
				setfrm = Frame(meshS1_frm, bd=1, relief=FLAT)
				
				setlbl = Label(setfrm,text=mshNames[cnt], anchor="e", width=9)
				setlbl.pack(side=LEFT)
				setEntry =  Entry(setfrm, width = 15)
				val = self.mesh[mshElements[cnt]]
				if(mshElements[cnt] == "Volume"):
					val = round(self.mesh[mshElements[cnt]],3)
				setEntry.insert(0, val)
				setEntry.pack(side=LEFT)
				
				setfrm.pack(side=TOP, fill=X)
				
				#This array is to keep all the elements packed together to make saving the data easier later.
				items = {}
				items["Item"] = "Mesh"
				items["Index"] = mshElements[cnt]
				items["Entry"] = setEntry
				self.mshItems.append(items)
			
			meshS1_frm.pack(side=LEFT, fill=Y, padx=2, pady=2)
			
			#Section 2: List of materials
			meshS2_frm = Frame(frame, bd=1, relief=GROOVE, width=200)
			
			#Setup Canvas for scrolling capablities:
			self.matcanvas = Canvas(meshS2_frm, width=200)
			self.matframe = Frame(self.matcanvas,bg='white', width=200)
			self.matscroll = Scrollbar(meshS2_frm, orient="vertical", command=self.matcanvas.yview, width=20)
			self.matcanvas.config(yscrollcommand=self.matscroll.set)
			
			self.matscroll.pack(side=RIGHT, fill=Y)
			self.matcanvas.pack(side=LEFT, fill=BOTH, expand=True)
			self.matcanvasframe = self.matcanvas.create_window((0, 0),window=self.matframe,anchor="nw")
			self.matframe.bind("<Configure>",self.matScrollFunt)
			self.matcanvas.bind("<Configure>",self.matScrollFunt2)
			
			#Load material references
			matNames = ["REF","Ind offset","Ind count","Ver offset","Ver count","Face offset","Face count","Unk"]
			matElements = ["MaterialRef","offIndices","cntIndices","offVertex","cntVertex","offFaces","cntFaces","Unknown"]
			cnt = 0
			for mat in self.mesh["Materials"]:
				mshmatfrm = Frame(self.matframe, bd=1, relief=FLAT)
				
				#Material identifier
				matTools = Frame(mshmatfrm, bd=1, relief=FLAT)
				mTitle_lbl = Label(matTools,text="Material: %d" % cnt)
				mTitle_lbl.config(font=("Times New Roman", 14))
				mTitle_lbl.pack(side=LEFT)
				matTools.pack(side=TOP, fill=X)
				
				#Settings
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
				
			meshS2_frm.pack(side=LEFT,fill=Y)
			
			#Setions 3: Interaction variables
			meshS3_frm = Frame(frame, bd=1, relief=FLAT, width=200)
			
			#Title
			mTitle_lbl = Label(meshS3_frm,text="Interaction Information",anchor="w")
			mTitle_lbl.config(font=("Times New Roman", 14))
			mTitle_lbl.pack(side=TOP)
			
			#Settings
			cnt = 0
			pntnames = ["Point 1","Point 2","Point 3","Point 4","Point 5","Point 6","Point 7","Point 8","Point 9"]
			for pnt in self.mesh["Points"]:
				pnt_ele_frm = Frame(meshS3_frm, bd=1, relief=FLAT)
				
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
			
			meshS3_frm.pack(side=LEFT,fill=Y)
			
			return frame
		
		def matScrollFunt2(self, event):
			canvas_width = event.width
			self.matcanvas.itemconfig(self.matcanvasframe, width = canvas_width)

		def matScrollFunt(self,event):
			self.matcanvas.configure(scrollregion=self.matcanvas.bbox("all"))
			
		def ok_pressed(self):
			# print("ok")
			#Loop through the settings
			for s in self.mshItems:
				if(s["Item"] == "Mesh"):
					if(s["Index"] == "Name"):
						self.mesh[s["Index"]] = s["Entry"].get()
					elif(s["Index"] == "Volume"):
						self.mesh[s["Index"]] = float(s["Entry"].get())
					else:
						self.mesh[s["Index"]] = int(s["Entry"].get())
				elif(s["Item"] == "Mat"):
					self.mesh["Materials"][s["Number"]][s["Index"]] = int(s["Entry"].get())
				elif(s["Item"] == "pnt"):
					self.mesh["Points"][s["Number"]]["X"] = float(s["EntryX"].get())
					self.mesh["Points"][s["Number"]]["Y"] = float(s["EntryY"].get())
					self.mesh["Points"][s["Number"]]["Z"] = float(s["EntryZ"].get())
			self.state = "Okay"
			self.destroy()

		def cancel_pressed(self):
			# print("cancel")
			self.state = "Cancel"
			self.destroy()

		def buttonbox(self):
			self.ok_button = Button(self, text='OK', width=7, command=self.ok_pressed)
			self.ok_button.pack(side="right")
			cancel_button = Button(self, text='Cancel', width=7, command=self.cancel_pressed)
			cancel_button.pack(side="right")
			self.bind("<Return>", lambda event: self.ok_pressed())
			self.bind("<Escape>", lambda event: self.cancel_pressed())
