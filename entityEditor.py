import settings
from tkinter import *
import tkinter.font
import tkinter.messagebox
from  tkinter.scrolledtext import *
from tkinter import ttk
from tkinter import simpledialog
from PIL import Image, ImageTk as pil
import array,sys,time,os
import numpy as np
import bwm
from functools import partial

class entityEditor():
	def __init__(self, root):
		self.root = root
		self.vEnt = []
		#Entities: Tool bar
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
		self.toolbar = Frame(root, bd=1, relief=FLAT)
		
		self.showicon = pil.PhotoImage(file=settings.icons["Show"])
		self.hideicon = pil.PhotoImage(file=settings.icons["Hide"])
		
		#Add Button
		eaicon = pil.PhotoImage(file=settings.icons["Add"])
		self.ebtnadd = Button(self.toolbar, width=20, height=20, relief=FLAT, image=eaicon, command = lambda: self.bwmInitEntity_Add())
		self.ebtnadd.image = eaicon
		self.ebtnadd.pack(side=LEFT, padx=2, pady=2)
		
		#Show all Button
		self.shAll = Button(self.toolbar, width=20, height=20, relief=FLAT, image=self.hideicon, command = self.toggleAll)
		self.shAll.image = self.hideicon
		self.shAll.pack(side=LEFT, padx=2, pady=2)
		self.shState = 0
		
		self.toolbar.pack(side=TOP, fill=X)
		
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

	def loadEntities(self,entlist,p3d):
		self.entityList = entlist
		self.p3d = p3d
		#Pre-processing
		editicon = pil.PhotoImage(file=settings.icons["Edit"])
		deleteicon = pil.PhotoImage(file=settings.icons["Delete"])
		
		#Loop through entities
		self.entityFrames = []
		self.vbtn = []
		cnt = 0
		for ent in entlist:
			#Create Frame
			entFrame = Frame(self.frame, bd=1, relief=FLAT)
			
			#Text Name
			btxt = Label(entFrame,text=ent["Name"])
			btxt.pack(side=LEFT, padx=2, pady=2)
			
			#Edit Button
			if(not (cnt in self.vEnt)):
				self.vEnt.append(0)
				
			if(self.vEnt[cnt] == 1):
				vbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=self.showicon, command = partial(self.toggleEntity, cnt))
				vbtn.image = self.showicon
			else:
				vbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=self.hideicon, command = partial(self.toggleEntity, cnt))
				vbtn.image = self.hideicon
				
			vbtn.pack(side=RIGHT, padx=2, pady=2)
			self.vbtn.append(vbtn)
			
			#Delete Button
			dbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removeEntity, cnt))
			dbtn.image = deleteicon
			dbtn.pack(side=RIGHT, padx=2, pady=2)
			
			#Edit Button
			ebtn = Button(entFrame, width=20, height=20, relief=FLAT, image=editicon, command = partial(self.editEntity_init, cnt))
			ebtn.image = editicon
			ebtn.pack(side=RIGHT, padx=2, pady=2)
			
			#Colours
			if((cnt % 2) != 0):
				entFrame.config(bg="light blue")
				btxt.config(bg="light blue")
				vbtn.config(bg="light blue")
				dbtn.config(bg="light blue")
				ebtn.config(bg="light blue")
				
			#Pack
			entFrame.pack(side=TOP, fill=X)
			self.entityFrames.append(entFrame)
			cnt += 1
	
	def toggleAll(self):
		if (self.shState == 0):
			for e in range(len(self.entityList)):
				if(self.vEnt[e] == 0):
					self.toggleEntity(e)
			self.shState = 1
			self.shAll.configure(image = self.showicon)
			self.shAll.image = self.showicon
		else:
			for e in range(len(self.entityList)):
				if(self.vEnt[e] == 1):
					self.toggleEntity(e)
			self.shState = 0
			self.shAll.configure(image = self.hideicon)
			self.shAll.image = self.hideicon
	
	def toggleEntity(self, index):
		if(self.vEnt[index] == 0):
			self.vEnt[index] = 1
			self.p3d.showEntity(index)
			self.vbtn[index].configure(image = self.showicon)
			self.vbtn[index].image = self.showicon
		else:
			self.vEnt[index] = 0
			self.p3d.hideEntity(index)
			self.vbtn[index].configure(image = self.hideicon)
			self.vbtn[index].image = self.hideicon
			
	def reloadEntities(self):
		#Delete frames
		for x in range(0, len(self.entityFrames)):
			self.entityFrames[x].destroy()
		self.loadEntities(self.entityList,self.p3d)
		
	def emptyData(self):
		#Delete frames
		for x in range(0, len(self.entityFrames)):
			self.entityFrames[x].destroy()
		del self.entityList
	
	#**Remove Entity**
	def removeEntity(self,index):
		del self.entityList[index]
		self.reloadEntities()
		
	#**Edit functions**
	def editEntity_init(self, index):
		entResult = self.itemDialog(self.root, self.entityList[index])
		if(entResult.state == "Okay"):
			self.entityList[index] = entResult.entry
			self.reloadEntities()
		
	def bwmInitEntity_Add(self):
		#Initialize an empty entity
		enty = {}
		enty["Name"] = "bws_ep_door"
		enty["Position"] = {}
		enty["Position"]["X"] = 0.1
		enty["Position"]["Y"] = 0
		enty["Position"]["Z"] = 0.1
		enty["Unknown1"] = {}
		enty["Unknown1"]["X"] = -1
		enty["Unknown1"]["Y"] = 0
		enty["Unknown1"]["Z"] = 0
		enty["Unknown2"] = {}
		enty["Unknown2"]["X"] = 0
		enty["Unknown2"]["Y"] = 0
		enty["Unknown2"]["Z"] = -1
		enty["Unknown3"] = {}
		enty["Unknown3"]["X"] = 0
		enty["Unknown3"]["Y"] = 1
		enty["Unknown3"]["Z"] = 0
		
		#Open dialog box
		entResult = self.itemDialog(self.root, enty)
		if(entResult.state == "Okay"):
			self.entityList.append(entResult.entry)
			self.reloadEntities()
		
	class itemDialog(simpledialog.Dialog):
		def __init__(self, parent, entry):
			self.entry = entry
			self.state = "Cancel"
			super().__init__(parent, "Entity Editor")
			
		def body(self, frame):
			#Name editor
			nameFrame = Frame(frame, bd=1, relief=FLAT)
			
			lbl_name = Label(nameFrame,text="Name:")
			lbl_name.pack(side=LEFT, padx=2, pady=2)
			self.ent_name = Entry(nameFrame, width = 28)
			self.ent_name.insert(0, self.entry["Name"])
			self.ent_name.pack(side=LEFT, padx=2, pady=2)
			
			nameFrame.pack(side=TOP, fill=X)
			
			#location
			positionFrame = Frame(frame, bd=1, relief=FLAT)
			
			ent_poslbl1 = Label(positionFrame,text="Pos: X")
			ent_poslbl1.pack(side=LEFT, padx=2, pady=2)
			self.ent_posX = Entry(positionFrame, width = 6)
			self.ent_posX.insert(0, round(self.entry["Position"]["X"],3))
			self.ent_posX.pack(side=LEFT, padx=2, pady=2)
			ent_poslbl2 = Label(positionFrame,text="Y")
			ent_poslbl2.pack(side=LEFT, padx=2, pady=2)
			self.ent_posY = Entry(positionFrame, width = 6)
			self.ent_posY.insert(0, round(self.entry["Position"]["Y"],3))
			self.ent_posY.pack(side=LEFT, padx=2, pady=2)
			ent_poslbl3 = Label(positionFrame,text="Z")
			ent_poslbl3.pack(side=LEFT, padx=2, pady=2)
			self.ent_posZ = Entry(positionFrame, width = 6)
			self.ent_posZ.insert(0, round(self.entry["Position"]["Z"],3))
			self.ent_posZ.pack(side=LEFT, padx=2, pady=2)
			
			positionFrame.pack(side=TOP, fill=X)
			
			#Unknown 1
			unknown1Frame = Frame(frame, bd=1, relief=FLAT)
			
			ent_U1lbl1 = Label(unknown1Frame,text="Un1: X")
			ent_U1lbl1.pack(side=LEFT, padx=2, pady=2)
			self.ent_U1X = Entry(unknown1Frame, width = 6)
			self.ent_U1X.insert(0, round(self.entry["Unknown1"]["X"],3))
			self.ent_U1X.pack(side=LEFT, padx=2, pady=2)
			ent_U1lbl2 = Label(unknown1Frame,text="Y")
			ent_U1lbl2.pack(side=LEFT, padx=2, pady=2)
			self.ent_U1Y = Entry(unknown1Frame, width = 6)
			self.ent_U1Y.insert(0, round(self.entry["Unknown1"]["Y"],3))
			self.ent_U1Y.pack(side=LEFT, padx=2, pady=2)
			ent_U1lbl3 = Label(unknown1Frame,text="Z")
			ent_U1lbl3.pack(side=LEFT, padx=2, pady=2)
			self.ent_U1Z = Entry(unknown1Frame, width = 6)
			self.ent_U1Z.insert(0, round(self.entry["Unknown1"]["Z"],3))
			self.ent_U1Z.pack(side=LEFT, padx=2, pady=2)
			
			unknown1Frame.pack(side=TOP, fill=X)
			
			#Unknown 2
			unknown2Frame = Frame(frame, bd=1, relief=FLAT)
			
			ent_U2lbl1 = Label(unknown2Frame,text="Un2: X")
			ent_U2lbl1.pack(side=LEFT, padx=2, pady=2)
			self.ent_U2X = Entry(unknown2Frame, width = 6)
			self.ent_U2X.insert(0, round(self.entry["Unknown2"]["X"],3))
			self.ent_U2X.pack(side=LEFT, padx=2, pady=2)
			ent_U2lbl2 = Label(unknown2Frame,text="Y")
			ent_U2lbl2.pack(side=LEFT, padx=2, pady=2)
			self.ent_U2Y = Entry(unknown2Frame, width = 6)
			self.ent_U2Y.insert(0, round(self.entry["Unknown2"]["Y"],3))
			self.ent_U2Y.pack(side=LEFT, padx=2, pady=2)
			ent_U2lbl3 = Label(unknown2Frame,text="Z")
			ent_U2lbl3.pack(side=LEFT, padx=2, pady=2)
			self.ent_U2Z = Entry(unknown2Frame, width = 6)
			self.ent_U2Z.insert(0, round(self.entry["Unknown2"]["Z"],3))
			self.ent_U2Z.pack(side=LEFT, padx=2, pady=2)
			
			unknown2Frame.pack(side=TOP, fill=X)
			
			#Unknown 3
			unknown3Frame = Frame(frame, bd=1, relief=FLAT)
			
			ent_U3lbl1 = Label(unknown3Frame,text="Un3: X")
			ent_U3lbl1.pack(side=LEFT, padx=2, pady=2)
			self.ent_U3X = Entry(unknown3Frame, width = 6)
			self.ent_U3X.insert(0, round(self.entry["Unknown3"]["X"],3))
			self.ent_U3X.pack(side=LEFT, padx=2, pady=2)
			ent_U3lbl2 = Label(unknown3Frame,text="Y")
			ent_U3lbl2.pack(side=LEFT, padx=2, pady=2)
			self.ent_U3Y = Entry(unknown3Frame, width = 6)
			self.ent_U3Y.insert(0, round(self.entry["Unknown3"]["Y"],3))
			self.ent_U3Y.pack(side=LEFT, padx=2, pady=2)
			ent_U3lbl3 = Label(unknown3Frame,text="Z")
			ent_U3lbl3.pack(side=LEFT, padx=2, pady=2)
			self.ent_U3Z = Entry(unknown3Frame, width = 6)
			self.ent_U3Z.insert(0, round(self.entry["Unknown3"]["Z"],3))
			self.ent_U3Z.pack(side=LEFT, padx=2, pady=2)
			
			unknown3Frame.pack(side=TOP, fill=X)
			
			return frame
			
		def ok_pressed(self):
			# print("ok")
			self.entry["Name"] = self.ent_name.get()
			self.entry["Position"]["X"] = float(self.ent_posX.get())
			self.entry["Position"]["Y"] = float(self.ent_posY.get())
			self.entry["Position"]["Z"] = float(self.ent_posZ.get())
			
			self.entry["Unknown1"]["X"] = float(self.ent_U1X.get())
			self.entry["Unknown1"]["Y"] = float(self.ent_U1Y.get())
			self.entry["Unknown1"]["Z"] = float(self.ent_U1Z.get())
			
			self.entry["Unknown2"]["X"] = float(self.ent_U2X.get())
			self.entry["Unknown2"]["Y"] = float(self.ent_U2Y.get())
			self.entry["Unknown2"]["Z"] = float(self.ent_U2Z.get())
			
			self.entry["Unknown3"]["X"] = float(self.ent_U3X.get())
			self.entry["Unknown3"]["Y"] = float(self.ent_U3Y.get())
			self.entry["Unknown3"]["Z"] = float(self.ent_U3Z.get())
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
		
