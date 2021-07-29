####################################################################################################
# Program: Black & White 2 Modeler
# Purpose: Provide the user an interface with which to convert and edit Black & White 2 model files
# Author: Bill
# Date: 
# Version: 1
####################################################################################################
#Program uses Tkinter for user interface
import settings
from tkinter import *
import tkinter.font
import tkinter.filedialog as tkFileDialog
from tkinter import messagebox
import array,sys,time,os
import ntpath
import SculptingHud #Model editor

#Other folders need to be added to the path: sys.path.append('Location')
#	Then files in that location can be imported

class Form1(Frame):
	global root,canv
	def __init__(self, parent=None, **kw):
		Frame.__init__(self, parent, kw)
		self.op = False
		self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
	
	def makeWidgets(self):
		#Construct Menu System
		self.menubar = Menu(root)
		filemenu = Menu(self.menubar, tearoff=0)
		filemenu.add_command(label="Open",command=self.fileLoad)
		filemenu.add_command(label="Save")
		filemenu.add_separator()
		filemenu.add_command(label="Exit",command=root.destroy)
		self.menubar.add_cascade(label="File",menu=filemenu)

		helpmenu = Menu(self.menubar, tearoff=0)
		helpmenu.add_command(label="Help Index")
		helpmenu.add_command(label="About...")
		self.menubar.add_cascade(label="Help",menu=helpmenu)
		root.config(menu=self.menubar)
		
	def _update(self):
		update_flag = False # Nothing to update on the screen at this time.
		self._timer = self.after(1000, self._update) # do this all again 1 second from now.
		
	def fileLoad(self):
		# Use Dialog Box to locate a svg files
		filenm = tkFileDialog.askopenfilename(initialdir = self.ROOT_DIR,filetypes = (("BW Models","*.bwm"),("Object Files","*.obj"),("COLLADA","*.dae"),("all files","*.*")))
		if not filenm: return
		self.loadModel(filenm)
			
	def loadModel(self,filename):
		self.filenm = filename
		dirpart, filepart = ntpath.split(filename) # get the directory part into dirpart and the file name into filepart
		exts = filepart.split('.') # parts based on . to find the extension.  Actual extension will be exts[len(exts)-1]
		ext = exts[len(exts)-1]
		if(ext == "bwm")or(ext == "obj")or(ext == "dae"):
			if(self.op == True):
				self.scuplter.loadFile(self.filenm)
			else:
				self.scuplter = SculptingHud.bwSculpting(root,self.filenm)
			self.op = True
		else:
			return False
		
def main():
	global root,Frm1
	
	args = sys.argv[1:] #Get main arguments
	#Initialize settings
	settings.init()
	

	root = Tk()

	root.geometry("%dx%d+0+0" % (800, 480))
	root.wm_title("Bw2 Model Editor")

	root.update() # this is needed to obtain actual screen measurements 
		
	Frm1 = Form1(root)
	Frm1.makeWidgets() # Make sure Setup runs before makeWidgets
	Frm1.pack(side=TOP)

	root.update() # this is needed to obtain actual screen measurements 
	Frm1._update() # Activate the 1 second process.
	
	#The only argument (at least for now) should be a model
	if(len(args) > 0):
		modelName = args[0]
		#Frm1.loadModel(modelName)

	root.mainloop()
    
if __name__ == '__main__':
    main()
