from tkinter import *
import tkinter.font
import tkinter.messagebox
from  tkinter.scrolledtext import *
from tkinter import ttk
from PIL import Image, ImageTk
import array,sys,time,os
import numpy as np
import bwm
import obj
from functools import partial

class basicEditor():
	def __init__(self, root):
		self.canvas = Canvas(root)
		self.frame = Frame(self.canvas,width=300)
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
		
	def emptyData(self):
		for i in range(len(self.set_frames)):
			self.set_frames[i][0].destroy()
			self.set_frames[i][1].destroy()

	def loadInformation(self,model,tp,e):
		self.type = tp
		if(tp == 1):
			self.load_bwm_info(model,e)
		else:
			self.load_obj_info(model)
		
	def load_bwm_info(self,model,e):
		self.set_frames = []
		settingOptions = [{
			"Title": "Base Information",
			"Settings": [
				{"Name":"Unk 1:","Type": "Number","Index": "Unknown1","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Pnt:","Type": "Point","Index": "Unknown2","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Box1:","Type": "Point","Index": "BoxPoint1","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Box2:","Type": "Point","Index": "BoxPoint2","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Cent:","Type": "Point","Index": "Center","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Height:","Type": "Number","Index": "Height","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Radius:","Type": "Number","Index": "Radius","Width": 6,"dataType": "f", "WidthText": 6},
				{"Name":"Unk:","Type": "Number","Index": "Unknown3","Width": 6,"dataType": "i", "WidthText": 6},
				{"Name":"Volume:","Type": "Number","Index": "Volume","Width": 7,"dataType": "f", "WidthText": 6}
			]
		},{
			"Title": "Unknown Values",
			"Settings": [
				{"Name":"Unk 1:","Type": "Number","Index": "UnknownF1","Width": 7,"dataType": "f", "WidthText": 7},
				{"Name":"Unk 2:","Type": "Number","Index": "UnknownF2","Width": 7,"dataType": "f", "WidthText": 7},
				{"Name":"Unk 3:","Type": "Number","Index": "UnknownF3","Width": 7,"dataType": "f", "WidthText": 7},
				{"Name":"Unk 4:","Type": "Number","Index": "UnknownF4","Width": 7,"dataType": "f", "WidthText": 7},
				{"Name":"Unk 5:","Type": "Number","Index": "Unknown4","Width": 7,"dataType": "i", "WidthText": 7},
			]	
		},{
			"Title": "Model Information",
			"Settings": [
				{"Text":"# of Materials: %d" % model.m["cntMaterials"],"Type": "Info"},
				{"Text":"# of Meshes: %d" % model.m["cntMeshs"],"Type": "Info"},
				{"Text":"# of Bones: %d" % model.m["cntBones"],"Type": "Info"},
				{"Text":"# of Entities: %d" % model.m["cntEntities"],"Type": "Info"},
				{"Text":"# of Unknown1: %d" % model.m["cntUnknown1"],"Type": "Info"},
				{"Text":"# of Unknown2: %d" % model.m["cntUnknown2"],"Type": "Info"},
				{"Text":"# of Verticies: %d" % model.m["cntVerticies"],"Type": "Info"},
				{"Text":"# of Strides: %d" % model.m["cntStrides"],"Type": "Info"},
				{"Text":"Unknown5: %d" % model.m["Unknown5"],"Type": "Info"},
				{"Text":"# of Indices: %d" % model.m["cntIndices"],"Type": "Info"},
			]
		}]
		#{
		#	"Title": "Sride Information",
		#	"Settings": [
		#		{"Name":"Unk 1:","Type": "SNumber","Index": 0,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 2:","Type": "SNumber","Index": 1,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 3:","Type": "SNumber","Index": 2,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 4:","Type": "SNumber","Index": 3,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 5:","Type": "SNumber","Index": 4,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 6:","Type": "SNumber","Index": 5,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 7:","Type": "SNumber","Index": 6,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 8:","Type": "SNumber","Index": 7,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 9:","Type": "SNumber","Index": 8,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 10:","Type": "SNumber","Index": 9,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 11:","Type": "SNumber","Index": 10,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 12:","Type": "SNumber","Index": 11,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 13:","Type": "SNumber","Index": 12,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 14:","Type": "SNumber","Index": 13,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 15:","Type": "SNumber","Index": 14,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 16:","Type": "SNumber","Index": 15,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 17:","Type": "SNumber","Index": 16,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 18:","Type": "SNumber","Index": 17,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 19:","Type": "SNumber","Index": 18,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 20:","Type": "SNumber","Index": 19,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 21:","Type": "SNumber","Index": 20,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 22:","Type": "SNumber","Index": 21,"Width": 12,"dataType": "i", "WidthText": 7},
		#		{"Name":"Unk 23:","Type": "SNumber","Index": 22,"Width": 12,"dataType": "i", "WidthText": 7},
		#	]
		#}]
		self.settings = []
		for setGroup in settingOptions:
			setGroup_frm = Frame(self.frame, bd=1, relief=FLAT)
			sTitle_lbl = Label(setGroup_frm,text=setGroup["Title"])
			sTitle_lbl.config(font=("Times New Roman", 14))
			sTitle_lbl.pack(side=LEFT)
			setGroup_frm.pack(side=TOP, fill=X)
			
			settings_frm = Frame(self.frame, bd=1, relief=FLAT)
			for s in setGroup["Settings"]:
				set_frm = Frame(settings_frm, bd=1, relief=FLAT)
				
				if(s["Type"] != "Info"):
					setg = {}
					setg["Name"] = s["Index"]
					setg["Type"] = s["Type"]
					setg["dataType"] = s["dataType"]
					set_lbl = Label(set_frm,text=s["Name"],width=s["WidthText"],anchor="w")
					set_lbl.pack(side=LEFT)
				
				if(s["Type"] == "Number"):
					set_entry = Entry(set_frm, width = s["Width"])
					if(s["dataType"] == "f"):
						set_entry.insert(0, round(model.m[s["Index"]],3))
					elif(s["dataType"] == "i"):
						set_entry.insert(0, round(model.m[s["Index"]]))
					set_entry.pack(side=LEFT)
					setg["Entry"] = set_entry
					setg["Entry"].bind("<Button-1>", lambda e, o = setg["Entry"]: self.focus_me(e,o))
				elif(s["Type"] == "Point"):
					set_entryX = Entry(set_frm, width = s["Width"])
					set_entryX.insert(0, round(model.m[s["Index"]]["X"],3))
					set_entryX.pack(side=LEFT)
					set_entryY = Entry(set_frm, width = s["Width"])
					set_entryY.insert(0, round(model.m[s["Index"]]["Y"],3))
					set_entryY.pack(side=LEFT)
					set_entryZ = Entry(set_frm, width = s["Width"])
					set_entryZ.insert(0, round(model.m[s["Index"]]["Z"],3))
					set_entryZ.pack(side=LEFT)
					setg["EntryX"] = set_entryX
					setg["EntryY"] = set_entryY
					setg["EntryZ"] = set_entryZ
					setg["EntryX"].bind("<Button-1>", lambda e, o = setg["EntryX"]: self.focus_me(e,o))
					setg["EntryY"].bind("<Button-1>", lambda e, o = setg["EntryY"]: self.focus_me(e,o))
					setg["EntryZ"].bind("<Button-1>", lambda e, o = setg["EntryZ"]: self.focus_me(e,o))
				elif(s["Type"] == "Info"):
					set_Infolbl = Label(set_frm,text = s["Text"])
					set_Infolbl.pack(side=LEFT)
				elif((s["Type"] == "SNumber") and (e != 4) and (e != 6)):
					set_entry = Entry(set_frm, width = s["Width"])
					if(s["dataType"] == "i"):
						set_entry.insert(0, round(model.m["Stride"]["Unknowns"][s["Index"]]))
					set_entry.pack(side=LEFT)
					setg["Entry"] = set_entry
					setg["Entry"].bind("<Button-1>", lambda e, o = setg["Entry"]: self.focus_me(e,o))
				
				if(s["Type"] != "Info"):
					self.settings.append(setg)
				set_frm.pack(side=TOP, fill=X)
				self.set_frames.append([setGroup_frm, settings_frm])
			settings_frm.pack(side=TOP, fill=X)
	
	def save_bwm_info(self,model):
		for s in self.settings:
			if(s["Type"] == "Number"):
				if(s["dataType"] == "f"):
					model.m[s["Name"]] = float(s["Entry"].get())
				elif(s["dataType"] == "i"):
					model.m[s["Name"]] = int(s["Entry"].get())
			elif(s["Type"] == "Point"):
				model.m[s["Name"]]["X"] = float(s["EntryX"].get())
				model.m[s["Name"]]["Y"] = float(s["EntryY"].get())
				model.m[s["Name"]]["Z"] = float(s["EntryZ"].get())
			elif(s["Type"] == "SNumber"):
				if(s["dataType"] == "i"):
					model.m["Stride"]["Unknowns"][s["Name"]] = int(s["Entry"].get())
		
	def load_obj_info(self,model):
		for mh in model["Meshes"]:
			setMesh_frm = Frame(self.frame, bd=1, relief=FLAT)
			sTitle_lbl = Label(setMesh_frm,text="Mesh: {0}".format(mh["Name"]))
			sTitle_lbl.config(font=("Times New Roman", 14))
			sTitle_lbl.pack(side=LEFT)
			setMesh_frm.pack(side=TOP, fill=X)
			
			mhVert_frm = Frame(self.frame, bd=1, relief=FLAT)
			mhVert_Infolbl = Label(mhVert_frm,text = "Vertices: {0}".format(len(mh["v"])))
			mhVert_Infolbl.pack(side=LEFT)
			mhVert_frm.pack(side=TOP, fill=X, padx=10)
			
			mhNors_frm = Frame(self.frame, bd=1, relief=FLAT)
			mhNors_Infolbl = Label(mhNors_frm,text = "Normals: {0}".format(len(mh["n"])))
			mhNors_Infolbl.pack(side=LEFT)
			mhNors_frm.pack(side=TOP, fill=X, padx=10)
			
			mhUV_frm = Frame(self.frame, bd=1, relief=FLAT)
			mhUV_Infolbl = Label(mhUV_frm,text = "Textures: {0}".format(len(mh["uv"])))
			mhUV_Infolbl.pack(side=LEFT)
			mhUV_frm.pack(side=TOP, fill=X, padx=10)
			
			setMt_frm = Frame(self.frame, bd=1, relief=FLAT)
			sTitle_lbl = Label(setMt_frm,text="Materials ({0})".format(len(mh["Materials"])))
			sTitle_lbl.config(font=("Times New Roman", 12))
			sTitle_lbl.pack(side=LEFT)
			setMt_frm.pack(side=TOP, fill=X, padx=10)
			
			for idx, mt in mh["Materials"].items():
				setMt_frm = Frame(self.frame, bd=1, relief=FLAT)
				sTitle_lbl = Label(setMt_frm,text="{0}:   {1} Faces".format(mt["Name"],len(mt["Faces"])))
				sTitle_lbl.config(font=("Times New Roman", 10))
				sTitle_lbl.pack(side=LEFT)
				setMt_frm.pack(side=TOP, fill=X, padx=20)
	
	def focus_me(self,e,o):
		o.focus_force()