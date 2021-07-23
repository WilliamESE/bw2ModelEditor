#This file contains all the global information that independent editors may need to know
#	Images (Icons) for buttons
#	File locations
from appdirs import *
import array,sys,time,os
import configparser
import ntpath
import posixpath

def init():
	ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) #Get root directory
	
	#Icon files
	global icons
	icons = {}
	icons["Edit"] = ROOT_DIR + '\\Images\\Icons\\editIcon.png'
	icons["Show"] = ROOT_DIR + '\\Images\\Icons\\Showing.png'
	icons["Hide"] = ROOT_DIR + '\\Images\\Icons\\Hidden.png'
	icons["Add"] = ROOT_DIR + '\\Images\\Icons\\addIcon.png'
	icons["Delete"] = ROOT_DIR + '\\Images\\Icons\\deleteIcon.png'
	icons["Save"] = ROOT_DIR + '\\Images\\Icons\\saveIcon.png'
	icons["Convert"] = ROOT_DIR + '\\Images\\Icons\\convertIcon.png'
	
	#Location information, read from the configuration file
	global locations
	locations = {}
	
	global appName
	global appAuthor
	appName = "BW2ModellingTools"
	appAuthor = "Bill"
	
	locations["ConfigFolder"] = user_config_dir(appName,appAuthor)
	if(os.path.exists(locations["ConfigFolder"]) == False):
		os.makedirs(locations["ConfigFolder"])
	
	#Check for config file
	locations["Config"] = locations["ConfigFolder"] + "\config.ini"
	if(os.path.exists(locations["Config"]) == False):
		default = configparser.ConfigParser()
		
		default.add_section('general')
		default.set('general', 'bwLocation', "C:\\Program Files (x86)\\Lionhead Studios\\Black & White 2")
		
		with open(locations["Config"], 'w') as configfile:
			default.write(configfile)
	
	#Read in configuration file
	global config		
	config = configparser.ConfigParser()
	config.read(locations["Config"])
	general = config["general"]
	
	#Identify Black and White 2 directory information:
	locations["Self"] = ROOT_DIR
	updateBWRoot(general["bwLocation"])

#Calculate Black and White 2 related file locations
def updateBWRoot(loca):
	locations["Root"] = loca #Black and white 2 root directory
	#Models and textures
	locations["Models"] = locations["Root"] + "\\Data\\Art\\models"
	locations["Textures"] = locations["Root"] + "\\Data\\Art\\textures"
	
	#Convert to linux path information. For some reason the people behind Panda3D (The 3D engine) decided their code would only work with linux pathing.
	#	So that is why this is here.
	locations["Textures_Linux"] = locations["Textures"].replace(ntpath.sep, posixpath.sep)
	locations["Textures_Linux"] = locations["Textures_Linux"].replace("C:","/c")
	
#Save the config information
def saveConfig():
	config_file = configparser.ConfigParser()
		
	config_file.add_section('general')
	config_file.set('general', 'bwLocation', locations["Root"])
	
	with open(locations["Config"], 'w') as configfile:
		config_file.write(configfile)
