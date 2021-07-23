import settings
from tkinter import *
import tkinter.font
import tkinter.messagebox
from  tkinter.scrolledtext import *
from tkinter import ttk
from PIL import Image, ImageTk as pil
import array,sys,time,os
import numpy as np
import bwm
from functools import partial

class unkPointEditor():
	def __init__(self, root, p3d):
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
		self.points = {}
		self.frames = {}
		self.shAll = {}
		self.shState = {}
		self.vbtn = {}
		self.vEnt = {}
		self.p3d = p3d
		
		self.showicon = pil.PhotoImage(file=settings.icons["Show"])
		self.hideicon = pil.PhotoImage(file=settings.icons["Hide"])
		
		#Points list display
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

	def loadPoints(self,title,pnts):
		self.points[title] = pnts
		self.frames[title] = {}
		self.vbtn[title] = []
		self.vEnt[title] = []
		deleteicon = pil.PhotoImage(file=settings.icons["Delete"])
		
		self.frames[title]["title"] = Frame(self.frame, bd=1, relief=FLAT)
		
		titlelbl = Label(self.frames[title]["title"],text=title)
		titlelbl.config(font=("Times New Roman", 14))
		titlelbl.pack(side=LEFT, padx=2, pady=2)
		
		#Show all Button
		self.shAll[title] = Button(self.frames[title]["title"], width=20, height=20, relief=FLAT, image=self.hideicon, command = partial(self.toggleAll, title))
		self.shAll[title].image = self.hideicon
		self.shAll[title].pack(side=RIGHT, padx=2, pady=2)
		self.shState[title] = 0
		
		eaicon = pil.PhotoImage(file=settings.icons["Add"])
		self.ebtnadd = Button(self.frames[title]["title"], width=20, height=20, relief=FLAT, image=eaicon, command = partial(self.addPoint, title))
		self.ebtnadd.image = eaicon
		self.ebtnadd.pack(side=RIGHT, padx=2, pady=2)
		
		self.frames[title]["title"].pack(side=TOP, fill=X)
		
		self.frames[title]["Pnts"] = []
		cnt = 0
		for p in pnts:
			pntFrame = Frame(self.frame, bd=1, relief=FLAT)
			
			btxt = Label(pntFrame,text="Point {0}".format(cnt))
			btxt.pack(side=LEFT, padx=2, pady=2)
			
			#Point Editor
			pnt_entryX = Entry(pntFrame, width = 6)
			pnt_entryX.insert(0, round(p["X"],3))
			pnt_entryX.pack(side=LEFT)
			pnt_entryX.bind("<Button-1>", lambda e, o = pnt_entryX: self.focus_me(e,o))
			pnt_entryY = Entry(pntFrame, width = 6)
			pnt_entryY.insert(0, round(p["Y"],3))
			pnt_entryY.pack(side=LEFT)
			pnt_entryY.bind("<Button-1>", lambda e, o = pnt_entryY: self.focus_me(e,o))
			pnt_entryZ = Entry(pntFrame, width = 6)
			pnt_entryZ.insert(0, round(p["Z"],3))
			pnt_entryZ.pack(side=LEFT)
			pnt_entryZ.bind("<Button-1>", lambda e, o = pnt_entryZ: self.focus_me(e,o))
			
			vbtn = Button(pntFrame, width=20, height=20, relief=FLAT, image=self.hideicon, command = partial(self.toggleView, title, cnt))
			vbtn.image = self.hideicon
			vbtn.pack(side=RIGHT, padx=2, pady=2)
			
			self.vbtn[title].append(vbtn)
			self.vEnt[title].append(0)
			
			dbtn = Button(pntFrame, width=20, height=20, relief=FLAT, image=deleteicon, command = partial(self.removePoint, title, cnt))
			dbtn.image = deleteicon
			dbtn.pack(side=RIGHT, padx=2, pady=2)
			
			pntFrame.pack(side=TOP, fill=X)
			frm = {"Frame": pntFrame, "entX": pnt_entryX, "entY": pnt_entryY, "entZ": pnt_entryZ, "Index": cnt}
			self.frames[title]["Pnts"].append(frm)
			cnt+=1
	
	def toggleAll(self,t):
		if (self.shState[t] == 0):
			for e in range(len(self.points[t])):
				if(self.vEnt[t][e] == 0):
					self.toggleView(t,e)
			self.shState[t] = 1
			self.shAll[t].configure(image = self.showicon)
			self.shAll[t].image = self.showicon
		else:
			for e in range(len(self.points[t])):
				if(self.vEnt[t][e] == 1):
					self.toggleView(t,e)
			self.shState[t] = 0
			self.shAll[t].configure(image = self.hideicon)
			self.shAll[t].image = self.hideicon
	
	def toggleView(self, title, index):
		if(self.vEnt[title][index] == 0):
			self.vEnt[title][index] = 1
			self.p3d.showPoint(title,index)
			self.vbtn[title][index].configure(image = self.showicon)
			self.vbtn[title][index].image = self.showicon
		else:
			self.vEnt[title][index] = 0
			self.p3d.hidePoint(title,index)
			self.vbtn[title][index].configure(image = self.hideicon)
			self.vbtn[title][index].image = self.hideicon
	
	def reloadPoints(self):
		for name, t in self.frames.items():
			t["title"].destroy()
			for f in t["Pnts"]:
				f["Frame"].destroy()
		for name, t in self.frames.items():
			self.loadPoints(name,self.points[name])
			
	def emptyData(self):
		for name, t in self.frames.items():
			t["title"].destroy()
			for f in t["Pnts"]:
				f["Frame"].destroy()
		for name, t in self.frames.items():
			del self.points[name]
	
	def removePoint(self,title,index):
		del self.points[title][index]
		self.reloadPoints()
		
	def addPoint(self,title):
		self.points[title].append({"X": 0, "Y": 0, "Z": 0})
		self.reloadPoints()
		
	def savePoints(self):
		for name, t in self.frames.items():
			for f in t["Pnts"]:
				self.points[name][f["Index"]]["X"] = float(f["entX"].get())
				self.points[name][f["Index"]]["Y"] = float(f["entY"].get())
				self.points[name][f["Index"]]["Z"] = float(f["entZ"].get())
	
	def focus_me(self,e,o):
		o.focus_force()
