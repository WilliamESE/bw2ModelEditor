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

class jointsEditor():
	def __init__(self, root, p3d):
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
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

	def loadPoints(self,joints):
		self.jnt = joints
		self.Tframes = []
		self.Jframes = []
		self.inputs = []
		
		ary = ["P1","P2","P3","Position"]
		jcnt = 0
		for p in joints:
			jItems = {}
			jFrame = Frame(self.frame, bd=1, relief=FLAT)
			cnt = 0
			
			tframes = Frame(jFrame, bd=1, relief=FLAT)
		
			titlelbl = Label(tframes,text="Joint {0}".format(jcnt))
			titlelbl.config(font=("Times New Roman", 14))
			titlelbl.pack(side=LEFT, padx=2, pady=2)
			
			tframes.pack(side=TOP, fill=X)
			
			self.Tframes.append(tframes)
			
			for i in range(4):
				jnt_frm = Frame(jFrame, bd=1, relief=FLAT)
				
				btxt = Label(jnt_frm,text="Point {0}".format(cnt))
				btxt.pack(side=LEFT, padx=2, pady=2)
				
				#Point Editor
				pnt_entryX = Entry(jnt_frm, width = 6)
				pnt_entryX.insert(0, round(p[ary[i]]["X"],3))
				pnt_entryX.pack(side=LEFT)
				pnt_entryX.bind("<Button-1>", lambda e, o = pnt_entryX: self.focus_me(e,o))
				pnt_entryY = Entry(jnt_frm, width = 6)
				pnt_entryY.insert(0, round(p[ary[i]]["Y"],3))
				pnt_entryY.pack(side=LEFT)
				pnt_entryY.bind("<Button-1>", lambda e, o = pnt_entryY: self.focus_me(e,o))
				pnt_entryZ = Entry(jnt_frm, width = 6)
				pnt_entryZ.insert(0, round(p[ary[i]]["Z"],3))
				pnt_entryZ.pack(side=LEFT)
				pnt_entryZ.bind("<Button-1>", lambda e, o = pnt_entryZ: self.focus_me(e,o))
				
				jnt_frm.pack(side=TOP, fill=X)
				
				frm = {"Frame": jnt_frm, "entX": pnt_entryX, "entY": pnt_entryY, "entZ": pnt_entryZ, "Index": cnt}
				jItems[ary[i]] = frm
				cnt+=1
			
			
			self.inputs.append(jItems)			
			jFrame.pack(side=TOP, fill=X)
			self.Jframes.append(jFrame)
			jcnt += 1
			
	def savePoints(self):
		cnt = 0
		for j in self.inputs:
			self.jnt[cnt]["P1"]["X"] = float(j["P1"]["entX"].get())
			self.jnt[cnt]["P1"]["Y"] = float(j["P1"]["entY"].get())
			self.jnt[cnt]["P1"]["Z"] = float(j["P1"]["entZ"].get())
			
			self.jnt[cnt]["P2"]["X"] = float(j["P2"]["entX"].get())
			self.jnt[cnt]["P2"]["Y"] = float(j["P2"]["entY"].get())
			self.jnt[cnt]["P2"]["Z"] = float(j["P2"]["entZ"].get())
			
			self.jnt[cnt]["P3"]["X"] = float(j["P3"]["entX"].get())
			self.jnt[cnt]["P3"]["Y"] = float(j["P3"]["entY"].get())
			self.jnt[cnt]["P3"]["Z"] = float(j["P3"]["entZ"].get())
			
			self.jnt[cnt]["Position"]["X"] = float(j["Position"]["entX"].get())
			self.jnt[cnt]["Position"]["Y"] = float(j["Position"]["entY"].get())
			self.jnt[cnt]["Position"]["Z"] = float(j["Position"]["entZ"].get())
			cnt += 1
		
	def focus_me(self,e,o):
		o.focus_force()
