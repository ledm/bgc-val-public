#!/usr/bin/ipython

#
# Copyright 2015, Plymouth Marine Laboratory
#
# This file is part of the bgc-val library.
#
# bgc-val is free software: you can redistribute it and/or modify it
# under the terms of the Revised Berkeley Software Distribution (BSD) 3-clause license.

# bgc-val is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the revised BSD license for more details.
# You should have received a copy of the revised BSD license along with bgc-val.
# If not, see <http://opensource.org/licenses/BSD-3-Clause>.
#
# Address:
# Plymouth Marine Laboratory
# Prospect Place, The Hoe
# Plymouth, PL1 3DH, UK
#
# Email:
# ledm@pml.ac.uk
#
"""
.. module:: ConfigParser
   :platform: Unix
   :synopsis: Some tools to help with parsing the config files.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
import ConfigParser
import os
from glob import glob

from functions.stdfunctions import std_functions  
from bgcvaltools.tdicts import tdicts
    
    
def checkConfig(Config,debug=False):
	"""
	If it's a string, it opens it as a ConfigParser.
	"""
	if type(Config) == type('string'):
		if debug: print "Reading", Config
		Config1 = ConfigParser.ConfigParser()
		Config1.read(Config)
		Config = Config1
	return Config


def parseBooleanSection(Config,section='ActiveKeys'):
	"""
	This is for parsing a list of boolean swithces for the evaluation suite.
	"""
	Config = checkConfig(Config)

	if section not in Config.sections():
		assert "parseKeys:\tThis Config does not have an "+str(section)+" section"

	options = Config.options(section)	
	keys	= []
	for option in options:
		val = Config.getboolean(section, option)
		if val: keys.append(option)
	return keys

def linkActiveKeys(Config,):
	"""
	This looks at the Active keys and makes a dictionary of keys, where the dictionairy is:
	dict1[lowercase key taken from the ActiveKeys Section] = Section name
	"""
	
	Config = checkConfig(Config)

	activeKeys = parseBooleanSection(Config,section='ActiveKeys')
	sectionsdict = {sec.lower():sec for sec in Config.sections()}
	#dict1 = {}
	actives = []
		
	for key in activeKeys:
		#dict1[key] = sectionsdict[key.lower()]
		try:	actives.append(sectionsdict[key.lower()])
		except:
			raise AssertionError("configparser.py:\tThe \""+str(key)+"\" key in the activeKeys list does not have a corresponding [Section] in the config file.")
	return actives		
	#return dict1


def findReplaceFlags(Config, section, string):
	# Look for the important flags, then swap them in
	if string.find('$YEAR') >-1:
		yr = parseOptionOrDefault(Config, section, 'year')
		string = string.replace('$YEAR', str(yr))
	if string.find('$JOBID') >-1:
		yr = parseOptionOrDefault(Config, section, 'jobID')
		string = string.replace('$JOBID', str(yr))
	if string.find('$NAME') >-1:
		yr = parseOptionOrDefault(Config, section, 'name')
		string = string.replace('$NAME', str(yr))	
	if string.find('$MODEL') >-1:
		yr = parseOptionOrDefault(Config, section, 'model')
		string = string.replace('$MODEL', str(yr))

	if string.find('$BASEDIR_MODEL') >-1:
		yr = parseOptionOrDefault(Config, section, 'basedir_model')
		string = string.replace('$BASEDIR_MODEL', str(yr))
	if string.find('$BASEDIR_OBS') >-1:
		yr = parseOptionOrDefault(Config, section, 'basedir_obs')
		string = string.replace('$BASEDIR_OBS', str(yr))
						
	return string
	

def parseFilepath(Config,section, option,expecting1=True,optional=True):
	"""
	This is for parsing a file path, a list of filepaths (separated by spaces), or a wildcard filepath.
	"""
	Config = checkConfig(Config)
	
	# Load raw string from config
	filepath = parseOptionOrDefault(Config,section, option)
	
	#filepath = findReplaceFlags(Config, filepath)
	 
	outputFiles = []
	if len(filepath.split(' '))>1:
		for fn in filepath.split(' '):
			outputFiles.extend(glob(fn))
	else:	outputFiles.extend(glob(filepath))

	if len(filepath) >0 and len(outputFiles)==0:
		print "parseFilepath:\tfilepath:",filepath, "\n\t\toutputFiles:",outputFiles
		if not optional:
			raise AssertionError("parseFilepath:\tUnable to locate the requested file.")		
	
	if expecting1:
		if len(outputFiles) == 1: return outputFiles[0]
		if len(outputFiles) == 0 and optional: return ''
		raise AssertionError("parseFilepath:\tExpecting a single file, but found multiple files.")
		
	if optional and len(outputFiles) ==0:
		return ''
	
	return outputFiles

	
def parseList(Config,section,option):
	"""
	This tool loads an string from config file and returns it as a list.
	"""
	Config = checkConfig(Config)
	try:	list1 = Config.get(section, option)
	except: 
		print "No option ",option," in section: ",section
		return ''
		
	list1 = findReplaceFlags(Config,section, list1)	
	list1.replace(',', ' ')
	list1.replace('  ', ' ')
	list1.replace('\'', '')
	list1.replace('\"', '')	
	return list1.split(' ')


def parseFunction(Config,section,option):
	"""
	This tool loads a function from the list of accepted functions.
	or loads a customFunction from a specified file with the following format:
	relative/path/to/file.py:function
	"""
	Config = checkConfig(Config)
	try:	functionname = Config.get(section, option)
	except: 
		print "No option ",option," in section: ",section
		return ''
	if functionname in std_functions.keys():
		print "Standard Function Found:",functionname
		return std_functions[functionname]

	if functionname.find(':') > -1:		
		[functionFileName,functionname] = functionname.split(':')
		lst = functionFileName.replace('.py','').replace('/', '.').split('.')		
		modulename =  '.'.join(lst)
		
		print "parseFunction:\tAttempting to load the function:",functionname, "from the:",modulename
		mod = __import__(modulename, fromlist=[functionname,])
		func = getattr(mod, functionname)
		return func
	
	raise AssertionError("parseFunction:\tNot able to load the function. From custom functions, try using filepath(no .py):function in your config file.")		
		

						
def get_str(Config, section, option,debug=False):
	Config = checkConfig(Config)	
	try: return Config.get(section, option)
	except:
		if debug: print "Unable to load:",section, option
	return ''

def parseOptionOrDefault(Config,section,option,parsetype='',debug=True, optional=True):
	"""#####
	This tool lets you create a Defaults section, and set some fields as defaults.
	 	ie: model_lat is always nav_lat, unless other specified.
	"""
	Config = checkConfig(Config)	
	defaultSection = 'Global'
	
	if defaultSection not in Config.sections():
		raise AssertionError("parseOptionOrDefault:\tNo defaults provided.")		
		
	if parsetype in ['', 'string','str']:
		value   = findReplaceFlags(Config,section,get_str(Config, section, option))	
		default = findReplaceFlags(Config,section, get_str(Config, defaultSection, option))	
		
	if parsetype.lower() in ['list', ]:
		try:	default = parseList(Config,defaultSection,option)
		except: default = ''

		try:	value = parseList(Config,section,option)
		except: value = ''	

	if parsetype.lower() in ['int', ]:
		try:	default = Config.getint(defaultSection,option)
		except: default = ''

		try:	value = Config.getint(section,option)
		except: value = ''
		
	if parsetype.lower() in ['bool', 'boolean','TrueOrFalse']:
		try:	
			value = Config.getboolean(section,option)
			return value
		except:
			default = Config.getboolean(defaultSection,option)
			return 	default
				
	#####
	# Value overrides global default
	
	if len(value) >0 and value not in ['', ' ']: 
		return value

	#####
	# Otherwise return the default
	if len(default) >0 and default not in ['', ' ']: 
		if debug:	print "parseOptionOrDefault: section",section, "option:", option, "is empty", value, "using default:", 	default
		return default
	if debug:	print "parseOptionOrDefault: ",[section,option,parsetype],"section option and default are empty"
	
	if optional: return ''
	#####
	# Otherwise, this doesn't work.
	raise AssertionError("parseOptionOrDefault:\tNo option or default provided.\tsection: "+str(section)+"\toption: "+str(option))	
	
	

def parseCoordinates(Config,section,m_or_d='model'):
	"""
	This tool loads a coordinate dictionary from the config file.
	"""

	if m_or_d.lower() not in ['model','data']:
		raise AssertionError("parseCoordinates:\tExpecting model or data, but found: "+str(m_or_d))
	Config = checkConfig(Config)
	coords = {}
	coordnames = ['t','cal','z','lat','lon']
	for c in coordnames:
		coords[c] = parseOptionOrDefault(Config,section, m_or_d+'_'+c)
	if m_or_d=='data':
		td = parseOptionOrDefault(Config,section, m_or_d+'_tdict')
		coords['tdict'] = tdicts[td]
	return coords


def parseBoolean(Config, section, option, default= True):
	"""
	This tool parses a boolean, but returns the defult, if a boolean is not found. 
	"""
	try:	return Config.getboolean(section, option)
	except:	return default

def parseDetails(Config,section,m_or_d='model'):
	"""
	This tool creates a coordinate dictionary describing the evaluation details. 
	"""
	if m_or_d.lower() not in ['model','data']:
		raise AssertionError("parseDetails:\tExpecting model or data, but found: "+str(m_or_d))

	Config = checkConfig(Config)
	details = {}
	details['name'] 	= Config.get(section,'name')
	details['units'] 	= Config.get(section,'units')
	details['vars'] 	= parseList(Config,section,m_or_d+'_vars')
	details['convert'] 	= parseFunction(Config,section,m_or_d+'_convert')
	
	#####
	# Looking for kwargs to pass to convert:
	for option in Config.options(section):
		searchFor =  m_or_d+'_convert_'
		findstr = option.find(searchFor)
		if findstr==-1:	continue
		kwargkey = option[len(searchFor):]
		details[kwargkey] = Config.get(section,option)
	return details


class GlobalSectionParser:
  def __init__(self,
  		fn,
  		defaultSection = 'Global',
  		debug=True):
	if debug: 
		print "------------------------------------------------------------------"
		print "GlobalKeyParser:\tBeginning to call GlobalSectionParser for ", fn
	self.__cp__ = checkConfig(fn)    
	self.__fn__ = fn	

	self.jobID = self.__cp__.get(defaultSection, 'jobID')
	self.year  = self.__cp__.get(defaultSection, 'year')	
	self.model = self.__cp__.get(defaultSection, 'model')
		
	self.makeReport 	= parseBoolean(self.__cp__, defaultSection, 'makeReport',	default=True)	
	self.makeProfiles 	= parseBoolean(self.__cp__, defaultSection, 'makeProfiles',	default=True)	
	self.makeP2P 		= parseBoolean(self.__cp__, defaultSection, 'makeP2P',		default=True)	
	self.makeTS	 	= parseBoolean(self.__cp__, defaultSection, 'makeTS',		default=True)	
	self.clean 		= parseBoolean(self.__cp__, defaultSection, 'clean',		default=False)
		
	self.images_ts		= parseOptionOrDefault(self.__cp__, defaultSection, 'images_ts',  )
	self.images_pro 	= parseOptionOrDefault(self.__cp__, defaultSection, 'images_pro', )	
	self.images_p2p 	= parseOptionOrDefault(self.__cp__, defaultSection, 'images_p2p', )
	self.postproc_ts  	= parseOptionOrDefault(self.__cp__, defaultSection, 'postproc_ts',  )
	self.postproc_pro 	= parseOptionOrDefault(self.__cp__, defaultSection, 'postproc_prp', )
	self.postproc_p2p 	= parseOptionOrDefault(self.__cp__, defaultSection, 'postproc_p2p', )
	self.reportdir 		= parseOptionOrDefault(self.__cp__, defaultSection, 'reportdir', )
	self.gridFile 		= parseFilepath(self.__cp__, defaultSection, 'gridFile',  )#expecting1=True, optional=False)	
	self.modelgrid		= parseOptionOrDefault(self.__cp__, defaultSection, 'modelgrid')		
	self.ActiveKeys 	= linkActiveKeys(self.__cp__)
				
  def __print__(self):
	print "------------------------------------------------------------------"
	print "GlobalSectionParser."
	print "File:				", self.__fn__
	print "model:				", self.model	
	print "jobID:				", self.jobID
	print "year:				", self.year	
	print "makeTS:				", self.makeTS
	print "makeP2P:				", self.makeP2P
	print "makeProfiles:			", self.makeProfiles
	print "makeReport:			", self.makeReport
							
	print "timeseries image folder:		", self.images_ts
	print "P2P image folder:		", self.images_p2p	
	print "Profile image folder:		", self.images_pro	
	print "timeseries postprocessed files:	", self.postproc_ts
	print "Profile postprocessed files:	", self.postproc_pro	
	print "p2p postprocessed files:		", self.postproc_p2p

	print "grid File:			", self.gridFile	
	print "model grid:			", self.modelgrid
	print "ActiveKeys:			", self.ActiveKeys
	
	return''
  def __repr__(self): return self.__print__()
  def __str__( self): return self.__print__()				
  
  
  	
class AnalysisKeyParser:
  def __init__(self,fn,key,debug=True):
	self.__fn__ = fn
	if debug: 
		print "------------------------------------------------------------------"
		print "AnalysisKeyParser:\tBeginning to call AnalysisKeyParser for ", key
	self.__cp__ = checkConfig(fn)  

	section = key
	self.jobID		= parseOptionOrDefault(self.__cp__, section, 'jobID')
	self.year		= parseOptionOrDefault(self.__cp__, section, 'year')	

	self.clean		= parseOptionOrDefault(self.__cp__, section, 'clean',		parsetype='bool')
	self.makeProfiles 	= parseOptionOrDefault(self.__cp__, section, 'makeProfiles',	parsetype='bool')	
	self.makeP2P 		= parseOptionOrDefault(self.__cp__, section, 'makeP2P',		parsetype='bool')	
	self.makeTS	 	= parseOptionOrDefault(self.__cp__, section, 'makeTS',		parsetype='bool')
	
	self.name		= self.__cp__.get(section, 'name')	
	self.units		= self.__cp__.get(section, 'units')		
	self.dimensions		= self.__cp__.getint(section, 'dimensions')
		
	self.modelFiles_ts 	= parseFilepath(self.__cp__, section, 'modelFiles',expecting1=False, )#optional=False)
	self.modelFile_p2p 	= parseFilepath(self.__cp__, section, 'modelFile_p2p',expecting1=True,)# optional=True)	
	
	self.dataFile   	= parseFilepath(self.__cp__, section, 'dataFile',  expecting1=True, )#optional=False)
	self.gridFile 		= parseFilepath(self.__cp__, section, 'gridFile',  expecting1=True, optional=False)

	self.modelcoords	 = parseCoordinates(self.__cp__, section, 'model')
	self.datacoords 	 = parseCoordinates(self.__cp__, section, 'data' )

	self.modeldetails 	= parseDetails(self.__cp__, section, 'model')
	self.datadetails  	= parseDetails(self.__cp__, section, 'data' )
	
	self.datasource		= parseOptionOrDefault(self.__cp__, section, 'datasource')
	self.model		= parseOptionOrDefault(self.__cp__, section, 'model')	
	self.modelgrid		= parseOptionOrDefault(self.__cp__, section, 'modelgrid')	

	self.regions 		= parseOptionOrDefault(self.__cp__, section, 'regions',parsetype='list')
	self.layers 		= parseOptionOrDefault(self.__cp__, section, 'layers', parsetype='list')
		
	self.images_ts		= parseOptionOrDefault(self.__cp__, section, 'images_ts',  )
	self.images_pro 	= parseOptionOrDefault(self.__cp__, section, 'images_pro', )
	self.images_p2p 	= parseOptionOrDefault(self.__cp__, section, 'images_p2p', )	
	self.postproc_ts  	= parseOptionOrDefault(self.__cp__, section, 'postproc_ts',  )
	self.postproc_pro 	= parseOptionOrDefault(self.__cp__, section, 'postproc_pro', )	
	self.postproc_p2p 	= parseOptionOrDefault(self.__cp__, section, 'postproc_p2p', )
	self.reportdir 		= parseOptionOrDefault(self.__cp__, section, 'reportdir', )
	
	if debug: self.__print__()

  	
  	
  	
  
  def __print__(self):
	print "------------------------------------------------------------------"
	print "AnalysisKeyParser."
	print "File:		", self.__fn__
	print "jobID:		", self.jobID
	print "clean:		", self.clean
	print "makeProfiles:	", self.makeProfiles
	print "makeP2P:		", self.makeP2P
	print "makeTS:		", self.makeTS
					
	print "timeseries image folder:		", self.images_ts
	print "Profile image folder:		", self.images_pro
	print "P2P image folder:		", self.images_p2p		
	print "timeseries postprocessed files:	", self.postproc_ts
	print "profile postprocessed files:	", self.postproc_pro
	print "p2p postprocessed files:		", self.postproc_p2p

	print "year:		", self.year
	print "name:		", self.name
	print "units:		", self.units
	print "datasource:	", self.datasource
	print "model:		", self.model
	print "dimensions:	", self.dimensions
			
	print "model Files (ts):", self.modelFiles_ts
	print "model Files (p2p):", self.modelFile_p2p
	print "data File:	", self.dataFile
	
	print "grid File:	", self.gridFile	
	print "model grid:	", self.modelgrid
	
	print "model coords:	", self.modelcoords
	print "data coords:	", self.datacoords
	print "model details:	", self.modeldetails
	print "data details:	", self.datadetails

	print "regions:		", self.regions
	print "layers:		", self.layers
	return''
  def __repr__(self): return self.__print__()
  def __str__( self): return self.__print__()		
  		
#####
# TO DO:
# Figure out how to load custom functions.

	
#analysiskeys = parseBooleanSection(self.__cp__)







