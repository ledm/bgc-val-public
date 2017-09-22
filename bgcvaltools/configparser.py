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
from itertools import product

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
	# Look for the important flags, then swap them in.
	flags = ['year', 'jobid','name','model','basedir_model','basedir_obs']
	for flag in flags:
		lookingFor = '$'+flag.upper()
		if string.find(lookingFor) ==-1:continue
		fl = parseOptionOrDefault(Config, section, flag.lower())
		string = string.replace(lookingFor, str(fl))		
	return string	

def findReplaceFlag(string, flag, value):
	"""
	Looking for $FLAG in the string. 
	If found, we replace $FLAG with value
	"""
	lookingFor = '$'+flag.upper()
	if string.find(lookingFor) ==-1: return string
	string = string.replace(lookingFor, value)		
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

	
def parseList(Config,section,option,findreplace=True):
	"""
	This tool loads an string from config file and returns it as a list.
	"""
	Config = checkConfig(Config)
	try:	list1 = Config.get(section, option)
	except: 
		print "No option ",option," in section: ",section
		return ''
		
	if findreplace:
		list1 = findReplaceFlags(Config,section, list1)	
	list1 = list1.replace('\t', ' ')
	list1 = list1.replace(',', ' ')
	list1 = list1.replace('  ', ' ')
	list1 = list1.replace('\'', '')
	list1 = list1.replace('\"', '')	
	while list1.count('  ')>0: 
		list1 = list1.replace('  ', ' ')
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

def parseOptionOrDefault(Config,section,option,parsetype='',debug=True, optional=True,findreplace=True):
	"""#####
	This tool lets you create a Defaults section, and set some fields as defaults.
	 	ie: model_lat is always nav_lat, unless other specified.
	"""
	Config = checkConfig(Config)	
	defaultSection = 'Global'
	
	if defaultSection not in Config.sections():
		raise AssertionError("parseOptionOrDefault:\tNo defaults provided.")		
		
	if parsetype in ['', 'string','str']:
		if findreplace:
			value   = findReplaceFlags(Config,section,get_str(Config, section, option))
			default = findReplaceFlags(Config,section, get_str(Config, defaultSection, option))
		else:	
			value   = get_str(Config, section, option)
			default = get_str(Config, defaultSection, option)
		
	if parsetype.lower() in ['list', ]:
		try:	default = parseList(Config,defaultSection,option,findreplace=findreplace)
		except: default = ''

		try:	value = parseList(Config,section,option,findreplace=findreplace)
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
  	if not fn:
  		raise AssertionError("GlobalSectionParser:\t Did not get a config filename: \""+fn+"\"")
	if debug:
		print "------------------------------------------------------------------"
		print "GlobalKeyParser:\tBeginning to call GlobalSectionParser for ", fn
	self.__cp__ = checkConfig(fn)
	self.__fn__ = fn

	self.ActiveKeys 	= linkActiveKeys(self.__cp__)
	self.jobIDs 		= parseList(self.__cp__, defaultSection, 'jobIDs'  )
	self.years  		= parseList(self.__cp__, defaultSection, 'years'   )
	self.models 		= parseList(self.__cp__, defaultSection, 'models'  )
	self.scenarios 		= parseList(self.__cp__, defaultSection, 'scenario')

	self.makeReport 	= parseBoolean(self.__cp__, defaultSection, 'makeReport',	default=True)	
	self.makeComp 		= parseBoolean(self.__cp__, defaultSection, 'makeComp',		default=True)
	self.clean 		= parseBoolean(self.__cp__, defaultSection, 'clean',		default=False)

	self.basedir_model	= self.parseFilepath( 'basedir_model', 	expecting1=True, optional=True,)
	self.basedir_obs	= self.parseFilepath( 'basedir_obs', 	expecting1=True, optional=True,)	
			
	self.reportdir 		= self.parseFilepath( 'reportdir', 	expecting1=True, optional=True, outputDir=True)
	self.images_comp	= self.parseFilepath( 'images_comp', 	expecting1=True, optional=True, outputDir=True)	
	

	self.modelgrid		= parseOptionOrDefault(self.__cp__, defaultSection, 'modelgrid')	
	self.gridFile 		= self.parseFilepath('gridFile',  	expecting1=True, optional=False)
					
	self.AnalysisKeyParser = {}	
	for (m,j,y,s,k) in product(self.models,self.jobIDs, self.years, self.scenarios,self.ActiveKeys):
		self.AnalysisKeyParser[(m,j,y,s,k)] = AnalysisKeyParser(fn,model = m,	jobID = j, year  = y, scenario=s, key = k,)

				
  def __print__(self):
	print "------------------------------------------------------------------"
	print "GlobalSectionParser."
	print "File:				", self.__fn__
	print "ActiveKeys:			", self.ActiveKeys		
	print "models:				", self.models	
	print "jobIDs:				", self.jobIDs
	print "years:				", self.years	
	print "scenarios:			", self.scenarios	
	print "makeReport:			", self.makeReport
	print "makeComp:			", self.makeComp	
	print "reportdir:			", self.reportdir							
	print "images_comp:			", self.images_comp								
	print "model grid:                      ", self.modelgrid
	print "gridFile:                        ", self.gridFile	
	return''
  def __repr__(self): return self.__print__()
  def __str__( self): return self.__print__()				
  
  def parseFilepath(self, option,expecting1=True,optional=True,outputDir=False):
	"""
	This is for parsing a file path, a list of filepaths (separated by spaces), or a wildcard filepath.
	The expecting1 flag is a switch to check for a single file as an output. 
	If a single file is expected, and 
	"""
	self.__cp__ = checkConfig(self.__cp__)
	
	# Load raw string from config1
	filepath = parseOptionOrDefault(self.__cp__, 'Global', option,findreplace=False)

	#####
	# Replace all the $FLAGS in the path.
	filepath = findReplaceFlag(filepath, 	'models', 	'_'.join(self.models))	
	filepath = findReplaceFlag(filepath, 	'jobIDs', 	'_'.join(self.jobIDs))	
	filepath = findReplaceFlag(filepath, 	'years', 	'_'.join(self.years))	
	filepath = findReplaceFlag(filepath, 	'scenarios', 	'_'.join(self.scenarios))
	try:	filepath = findReplaceFlag(filepath, 	'basedir_model',	 self.basedir_model)
	except: pass
	try:	filepath = findReplaceFlag(filepath, 	'basedir_obs',	 	self.basedir_obs)
	except: pass	
	
	if filepath.find('$')>-1:
		raise AssertionError("GlobalSectionParser:\tparseFilepath:\t"+str(option)+"\tUnable to replace all the $PATH KEYS. "+\
		"\n\t\tAvailable options are: $MODELS, $JOBIDS, $YEARS, $SCENARIOS, (in that order)."+\
		"\n\t\tAfter replacing $FLAGS, Filepath was:"+str(filepath))		
		

	#####
	# Expecting an output directory, which may not exist yet.
	if outputDir: return filepath
	
	outputFiles = []
	#####
	# Looking for files which have to exist already
	if len(filepath.split(' '))>1:
		for fn in filepath.split(' '):
			outputFiles.extend(glob(fn))
	else:	outputFiles.extend(glob(filepath))

	if len(filepath) >0 and len(outputFiles)==0:
		print "GlobalSectionParser:\tparseFilepath:\tfilepath:",filepath, "\n\t\toutputFiles:",outputFiles
		if not optional:
			raise AssertionError("GlobalSectionParser:\tparseFilepath:\tUnable to locate the file: "+str(filepath))		
	
	if expecting1:
		if len(outputFiles) == 1: return outputFiles[0]
		if len(outputFiles) == 0 and optional: return ''
		raise AssertionError("parseFilepath:\tExpecting a single file, but found multiple files.")
		
	if optional and len(outputFiles) ==0:
		return ''
	
	return outputFiles 	
  	
  	
  	
  	

  
  	
class AnalysisKeyParser:
  def __init__(self,fn,
  		model = '',
  		jobID = '',
  		year  = '',
  		scenario='',
  		key   = '',
  		debug=True):
	self.__fn__ = fn
	if debug: 
		print "------------------------------------------------------------------"
		print "AnalysisKeyParser:\tBeginning to call AnalysisKeyParser for ", key
	self.__cp__ = checkConfig(fn)  

	self.section 	= key
	self.model 	= model
	self.jobID 	= jobID
	self.year	= year
	self.scenario 	= scenario
	self.key 	= key

	self.akp_id 	= 	(self.model,self.jobID,self.year,self.scenario,self.key)
	#self.jobID		= parseOptionOrDefault(self.__cp__, section, 'jobID')
	#self.year		= parseOptionOrDefault(self.__cp__, section, 'year')	
	#self.model		= parseOptionOrDefault(self.__cp__, section, 'model')	

	self.name		= self.__cp__.get(self.section, 'name')	
	self.units		= self.__cp__.get(self.section, 'units')		
	self.dimensions		= self.__cp__.getint(self.section, 'dimensions')
		
	self.clean		= parseOptionOrDefault(self.__cp__, self.section, 'clean',		parsetype='bool')
	self.makeProfiles 	= parseOptionOrDefault(self.__cp__, self.section, 'makeProfiles',	parsetype='bool')	
	self.makeP2P 		= parseOptionOrDefault(self.__cp__, self.section, 'makeP2P',		parsetype='bool')	
	self.makeTS	 	= parseOptionOrDefault(self.__cp__, self.section, 'makeTS',		parsetype='bool')
	

	self.modelcoords	 = parseCoordinates(self.__cp__, self.section, 'model')
	self.datacoords 	 = parseCoordinates(self.__cp__, self.section, 'data' )
	self.modeldetails 	= parseDetails(self.__cp__, self.section, 'model')
	self.datadetails  	= parseDetails(self.__cp__, self.section, 'data' )
	
	self.datasource		= parseOptionOrDefault(self.__cp__, self.section, 'datasource')
	self.modelgrid		= parseOptionOrDefault(self.__cp__, self.section, 'modelgrid')	

	self.regions 		= parseOptionOrDefault(self.__cp__, self.section, 'regions',parsetype='list')
	self.layers 		= parseOptionOrDefault(self.__cp__, self.section, 'layers', parsetype='list')

	self.basedir_model	= self.parseFilepath('basedir_model', 	expecting1=True, optional=True,)			
	self.basedir_obs	= self.parseFilepath('basedir_obs', 	expecting1=True, optional=True,)				
	
	self.modelFiles_ts 	= self.parseFilepath('modelFiles',	expecting1=False,optional=True )  #optional=False)
	self.modelFile_p2p 	= self.parseFilepath('modelFile_p2p',	expecting1=True, optional=True ) # optional=True)	
	
	self.dataFile   	= self.parseFilepath('dataFile',  	expecting1=True, optional=True ) #optional=False)
	self.gridFile 		= self.parseFilepath('gridFile',  	expecting1=True, optional=False)
	

	self.images_ts		= self.parseFilepath( 'images_ts',  	expecting1=True, optional=True, outputDir=True)
	self.images_pro 	= self.parseFilepath( 'images_pro', 	expecting1=True, optional=True, outputDir=True)
	self.images_p2p 	= self.parseFilepath( 'images_p2p', 	expecting1=True, optional=True, outputDir=True)	
	self.postproc_ts  	= self.parseFilepath( 'postproc_ts', 	expecting1=True, optional=True, outputDir=True )
	self.postproc_pro 	= self.parseFilepath( 'postproc_pro', 	expecting1=True, optional=True, outputDir=True)	
	self.postproc_p2p 	= self.parseFilepath( 'postproc_p2p', 	expecting1=True, optional=True, outputDir=True)

			
	if debug: self.__print__()

  def parseFilepath(self, option,expecting1=True,optional=True,outputDir=False):
	"""
	This is for parsing a file path, a list of filepaths (separated by spaces), or a wildcard filepath.
	The expecting1 flag is a switch to check for a single file as an output. 
	If a single file is expected, and 
	"""
	self.__cp__ = checkConfig(self.__cp__)
	
	# Load raw string from config1
	filepath = parseOptionOrDefault(self.__cp__, self.section, option,findreplace=False)

	#####
	# Replace all the $FLAGS in the path.
	filepath = findReplaceFlag(filepath, 	'model', 	self.model)	
	filepath = findReplaceFlag(filepath, 	'jobID', 	self.jobID)	
	filepath = findReplaceFlag(filepath, 	'year', 	self.year)	
	filepath = findReplaceFlag(filepath, 	'scenario', 	self.scenario)	
	filepath = findReplaceFlag(filepath, 	'key', 		self.key)			
	filepath = findReplaceFlag(filepath, 	'name',		self.name)				
	try:	filepath = findReplaceFlag(filepath, 	'basedir_model',self.basedir_model)					
	except:	pass
	try:	filepath = findReplaceFlag(filepath, 	'basedir_obs', self.basedir_obs)					
	except:	pass	
	if filepath.find('$')>-1:
		raise AssertionError("parseFilepath:\t"+str(option)+"\tUnable to replace all the $PATH KEYS. "+\
		"\n\t\tAvailable options are: $MODEL, $JOBID, $YEAR, $SCENARIO, $KEY, $NAME (in that order)."+\
		"\n\t\tAfter replacing $FLAGS, Filepath was:"+str(filepath))		
		
	outputFiles = []

	#####
	# Expecting an output directory, which may not exist yet.
	if outputDir: return filepath

	#####
	# Looking for files which have to exist already
	if len(filepath.split(' '))>1:
		for fn in filepath.split(' '):
			outputFiles.extend(glob(fn))
	else:	outputFiles.extend(glob(filepath))

	if len(filepath) >0 and len(outputFiles)==0:
		print "parseFilepath:\tfilepath:",filepath, "\n\t\toutputFiles:",outputFiles
		if not optional:
			raise AssertionError("parseFilepath:\tUnable to locate the requested file: "+str(filepath))		
	
	if expecting1:
		if len(outputFiles) == 1: return outputFiles[0]
		if len(outputFiles) == 0 and optional: return ''
		raise AssertionError("parseFilepath:\tExpecting a single file, but found multiple files:"+str(outputFiles))
		
	if optional and len(outputFiles) ==0:
		return ''
	
	return outputFiles 	
  	
  	
  
  def __print__(self):
	print "------------------------------------------------------------------"
	print "AnalysisKeyParser."
	print "File:		", self.__fn__
	print "model:		", self.model
	print "jobID:		", self.jobID
	print "year:		", self.year
	print "scenario:	", self.scenario	
	print "name:		", self.name
		
	print "units:		", self.units
	print "datasource:	", self.datasource
	print "dimensions:	", self.dimensions

	print "clean:		", self.clean
	print "makeProfiles:	", self.makeProfiles
	print "makeP2P:		", self.makeP2P
	print "makeTS:		", self.makeTS
					
								
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
	
	print "timeseries image folder:		", self.images_ts
	print "Profile image folder:		", self.images_pro
	print "P2P image folder:		", self.images_p2p		
	print "timeseries postprocessed files:	", self.postproc_ts
	print "profile postprocessed files:	", self.postproc_pro
	print "p2p postprocessed files:		", self.postproc_p2p
		
	return''
  def __repr__(self): return self.__print__()
  def __str__( self): return self.__print__()		
  		
#####
# TO DO:
# Figure out how to load custom functions.

	
#analysiskeys = parseBooleanSection(self.__cp__)







