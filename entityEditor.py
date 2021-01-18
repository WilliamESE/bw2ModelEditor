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

class entityEditor():
	def __init__(self, root):
		#Entities: Tool bar
		self.toolbar = Frame(root, bd=1, relief=FLAT)
		
		self.showicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\Showing.png')
		self.hideicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\Hidden.png')
		
		#Add Button
		eaicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\addIcon.png')
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
		editicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\editIcon.png')
		deleteicon = PhotoImage(file='C:\\Users\\William\\Documents\\BW\\BW2Models\\python\\Images\\deleteIcon.png')
		
		#Loop through entities
		self.entityFrames = []
		self.vbtn = []
		self.vEnt = []
		cnt = 0
		for ent in entlist:
			#Create Frame
			if((cnt % 2) == 0):
				entFrame = Frame(self.frame, bd=1, relief=FLAT)
			else:
				entFrame = Frame(self.frame, bd=1, relief=FLAT, bg="light blue")
			
			#Text Name
			if((cnt % 2) == 0):
				btxt = Label(entFrame,text=ent["Name"])
			else:
				btxt = Label(entFrame,text=ent["Name"], bg="light blue")
			btxt.pack(side=LEFT, padx=2, pady=2)
			
			#Edit Button
			if((cnt % 2) == 0):
				vbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=self.hideicon, command = partial(self.toggleEntity, cnt))
			else:
				vbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=self.hideicon, command = partial(self.toggleEntity, cnt), bg="light blue")
			vbtn.image = self.hideicon
			vbtn.pack(side=RIGHT, padx=2, pady=2)
			
			self.vbtn.append(vbtn)
			self.vEnt.append(0)
			
			#Delete Button
			if((cnt % 2) == 0):
				dbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removeEntity, cnt))
			else:
				dbtn = Button(entFrame, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removeEntity, cnt), bg="light blue")
			dbtn.image = deleteicon
			dbtn.pack(side=RIGHT, padx=2, pady=2)
			
			#Edit Button
			if((cnt % 2) == 0):
				ebtn = Button(entFrame, width=20, height=20, relief=FLAT, image=editicon, command = partial(self.editEntity_init, cnt))
			else:
				ebtn = Button(entFrame, width=20, height=20, relief=FLAT, image=editicon, command = partial(self.editEntity_init, cnt), bg="light blue")
			ebtn.image = editicon
			ebtn.pack(side=RIGHT, padx=2, pady=2)
			
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
	
	#**Init functions**
	def editEntity_init(self, index):
		self.openEditor(self.entityList[index],1,index)
		
	def bwmInitEntity_Add(self):
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
		
		self.openEditor(enty,0,0)
	
	#**Saving**
	def editEntity(self, index):
		self.entityList[index]["Name"] = self.ent_nameEntered.get()
		self.entityList[index]["Position"]["X"] = float(self.ent_posX.get())
		self.entityList[index]["Position"]["Y"] = float(self.ent_posY.get())
		self.entityList[index]["Position"]["Z"] = float(self.ent_posZ.get())
		
		self.entityList[index]["Unknown1"]["X"] = float(self.ent_U1X.get())
		self.entityList[index]["Unknown1"]["Y"] = float(self.ent_U1Y.get())
		self.entityList[index]["Unknown1"]["Z"] = float(self.ent_U1Z.get())
		
		self.entityList[index]["Unknown2"]["X"] = float(self.ent_U2X.get())
		self.entityList[index]["Unknown2"]["Y"] = float(self.ent_U2Y.get())
		self.entityList[index]["Unknown2"]["Z"] = float(self.ent_U2Z.get())
		
		self.entityList[index]["Unknown3"]["X"] = float(self.ent_U3X.get())
		self.entityList[index]["Unknown3"]["Y"] = float(self.ent_U3Y.get())
		self.entityList[index]["Unknown3"]["Z"] = float(self.ent_U3Z.get())
		
		self.Enteditor.destroy()
		self.reloadEntities()
		
	def addEntity(self):
		ent = {}
		ent["Name"] = self.ent_nameEntered.get()
		ent["Position"] = {}
		ent["Position"]["X"] = float(self.ent_posX.get())
		ent["Position"]["Y"] = float(self.ent_posY.get())
		ent["Position"]["Z"] = float(self.ent_posZ.get())
		
		ent["Unknown1"] = {}
		ent["Unknown1"]["X"] = float(self.ent_U1X.get())
		ent["Unknown1"]["Y"] = float(self.ent_U1Y.get())
		ent["Unknown1"]["Z"] = float(self.ent_U1Z.get())
		
		ent["Unknown2"] = {}
		ent["Unknown2"]["X"] = float(self.ent_U2X.get())
		ent["Unknown2"]["Y"] = float(self.ent_U2Y.get())
		ent["Unknown2"]["Z"] = float(self.ent_U2Z.get())
		
		ent["Unknown3"] = {}
		ent["Unknown3"]["X"] = float(self.ent_U3X.get())
		ent["Unknown3"]["Y"] = float(self.ent_U3Y.get())
		ent["Unknown3"]["Z"] = float(self.ent_U3Z.get())
		
		self.entityList.append(ent)
		self.Enteditor.destroy()
		self.reloadEntities()
	
	def cancelEntity(self):
		self.Enteditor.destroy()
	
	#**Editor**
	def openEditor(self,enty,edit,index):
		self.Enteditor = Tk()
		self.Enteditor.wm_title("Entity Editor")
		self.Enteditor.geometry("%dx%d+0+0" % (225, 150))
		
		#Name editor
		self.ent_namelbl = Label(self.Enteditor,text="Name:")
		self.ent_namelbl.place(x=5,y=5)
		self.ent_nameEntered = Entry(self.Enteditor, width = 28)
		self.ent_nameEntered.insert(0, enty["Name"])
		self.ent_nameEntered.place(x=45,y=6)
		
		#location
		ent_poslbl1 = Label(self.Enteditor,text="Pos: X")
		ent_poslbl1.place(x=5,y=30)
		self.ent_posX = Entry(self.Enteditor, width = 6)
		self.ent_posX.insert(0, round(enty["Position"]["X"],3))
		self.ent_posX.place(x=45,y=31)
		ent_poslbl2 = Label(self.Enteditor,text="Y")
		ent_poslbl2.place(x=90,y=30)
		self.ent_posY = Entry(self.Enteditor, width = 6)
		self.ent_posY.insert(0, round(enty["Position"]["Y"],3))
		self.ent_posY.place(x=105,y=31)
		ent_poslbl3 = Label(self.Enteditor,text="Z")
		ent_poslbl3.place(x=150,y=30)
		self.ent_posZ = Entry(self.Enteditor, width = 6)
		self.ent_posZ.insert(0, round(enty["Position"]["Z"],3))
		self.ent_posZ.place(x=165,y=31)
		
		#Unknown 1
		ent_U1lbl1 = Label(self.Enteditor,text="Un1: X")
		ent_U1lbl1.place(x=5,y=50)
		self.ent_U1X = Entry(self.Enteditor, width = 6)
		self.ent_U1X.insert(0, round(enty["Unknown1"]["X"],3))
		self.ent_U1X.place(x=45,y=51)
		ent_U1lbl2 = Label(self.Enteditor,text="Y")
		ent_U1lbl2.place(x=90,y=50)
		self.ent_U1Y = Entry(self.Enteditor, width = 6)
		self.ent_U1Y.insert(0, round(enty["Unknown1"]["Y"],3))
		self.ent_U1Y.place(x=105,y=51)
		ent_U1lbl3 = Label(self.Enteditor,text="Z")
		ent_U1lbl3.place(x=150,y=50)
		self.ent_U1Z = Entry(self.Enteditor, width = 6)
		self.ent_U1Z.insert(0, round(enty["Unknown1"]["Z"],3))
		self.ent_U1Z.place(x=165,y=51)
		
		#Unknown 2
		ent_U2lbl1 = Label(self.Enteditor,text="Un2: X")
		ent_U2lbl1.place(x=5,y=70)
		self.ent_U2X = Entry(self.Enteditor, width = 6)
		self.ent_U2X.insert(0, round(enty["Unknown2"]["X"],3))
		self.ent_U2X.place(x=45,y=71)
		ent_U2lbl2 = Label(self.Enteditor,text="Y")
		ent_U2lbl2.place(x=90,y=70)
		self.ent_U2Y = Entry(self.Enteditor, width = 6)
		self.ent_U2Y.insert(0, round(enty["Unknown2"]["Y"],3))
		self.ent_U2Y.place(x=105,y=71)
		ent_U2lbl3 = Label(self.Enteditor,text="Z")
		ent_U2lbl3.place(x=150,y=70)
		self.ent_U2Z = Entry(self.Enteditor, width = 6)
		self.ent_U2Z.insert(0, round(enty["Unknown2"]["Z"],3))
		self.ent_U2Z.place(x=165,y=71)
		
		#Unknown 3
		ent_U3lbl1 = Label(self.Enteditor,text="Un3: X")
		ent_U3lbl1.place(x=5,y=90)
		self.ent_U3X = Entry(self.Enteditor, width = 6)
		self.ent_U3X.insert(0, round(enty["Unknown3"]["X"],3))
		self.ent_U3X.place(x=45,y=91)
		ent_U3lbl2 = Label(self.Enteditor,text="Y")
		ent_U3lbl2.place(x=90,y=90)
		self.ent_U3Y = Entry(self.Enteditor, width = 6)
		self.ent_U3Y.insert(0, round(enty["Unknown3"]["Y"],3))
		self.ent_U3Y.place(x=105,y=91)
		ent_U3lbl3 = Label(self.Enteditor,text="Z")
		ent_U3lbl3.place(x=150,y=90)
		self.ent_U3Z = Entry(self.Enteditor, width = 6)
		self.ent_U3Z.insert(0, round(enty["Unknown3"]["Z"],3))
		self.ent_U3Z.place(x=165,y=91)
		
		#Add Button
		ent_Can = Button(self.Enteditor, text="Cancel", command = lambda: self.cancelEntity())
		ent_Can.place(x=120,y=120)
		if(edit == 1):
			end_Save = Button(self.Enteditor, text="Save", command = partial(self.editEntity, index))
		else:
			end_Save = Button(self.Enteditor, text="Save", command = lambda: self.addEntity())
		end_Save.place(x=180,y=120)
		
		self.Enteditor.mainloop()
		
