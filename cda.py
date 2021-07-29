import settings
import ntpath
import array,sys,time,os
import numpy as np
from collada import *


def loadCda(filename, ignore = False):
	"""	Process a collada file, True upon success, False on failure, scene stored in scene global """
	global success
	success = False
	#Opening the file is simple:
	if(os.path.exists(filename) == False): #Make sure the file exists
		return False
	
	#Collada has a large error system, these for development purposes may need to be ignored.
	ignore = []
	if ignore:
		ignore.extend([
			collada.DaeUnsupportedError, 
			collada.DaeBrokenRefError,
	])
	
	#Process Collada file
	global scene
	scene = Collada(filename, ignore=ignore)
	#Check for errors
	if scene.errors:
		print(*cdaModel.errors, sep='\n')
		return False
	
	#File has been processed successfully
	success = True
	return True
	
	#print(cdaModel.materials[0].effect.params[0].image.path)
	#print(cdaModel.materials[0].effect.diffuse.sampler.surface.image.path)
	#print(cdaModel.materials[0].effect.specular)
	
def bwmToCda(model, fileout):
	#Takes the bwm model dictionary and convert it to Collada and save the file
	
	fout = open(fileout, "w+")
	if(fout == False):
		return False #If the file failed to be opened, back out.
		
	#Process the model and build the Collada arrays, which are numpy based.
	
	
	#Clean up and end
	fout.close()
	return True

def cdaToBwm():
	#Make sure the collada file is set and isn't empty
	if(success == False):
		return False
	
	#Storage for bwm model
	bwmModel = {}
	
	#Process collada model and fill the model dictionary
	#	Vertices can be accessed through geometries[x].primitives[y].vertex[geometries[x].primitives[y].vertex_index][v]
	#	Could be prudent to create a function that grabs this information.
	#	A reference to the material is included in the primitive.
	#	Furthermore, one potential issue I will have to deal with at different types of privitives. The downloaded dae file contains lines.
	#Vertices must be added based on materials and meshes. The difficulty would exist in the meshes were the materials may not be organized properly
	
	
	
	
	#return model
	return bwmModel

def get_triangles(scene):
	"""
	A generator that pulls all the triangles out of the Collada scene.
	"""
	for geometry in scene.scene.objects('geometry'):
		for primitive in geometry.primitives():
			for triangle in primitive.triangles():
				yield triangle
