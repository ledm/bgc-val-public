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
from functions import functions
import os
from glob import glob

   
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
	dict1 = {}
	for key in activeKeys:
		dict1[key] = sectionsdict[key.lower()]
	return dict1


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
				
	return string
	

def parseFilepath(Config,section, option,expecting1=True,):
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
		raise AssertionError("parseFilepath:\tUnable to locate the requested file.")		
	
	if expecting1:
		if len(outputFiles) == 1: return outputFiles[0]
		if len(outputFiles) == 0: return ''
		raise AssertionError("parseFilepath:\tExpecting a single file, but found multiple files.")
	return outputFiles

	
			

def parseList(Config,section,option):
	"""
	This tool loads an string from config file and returns it as a list.
	"""
	Config = checkConfig(Config)
	list1 = Config.get(section, option)
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
	/full/path/to/file.py
	"""
	Config = checkConfig(Config)
	functionname = Config.get(section, option)
	if functionname in functions.keys():
		print "Function Found:",functionname
		return functions[functionname]
	if os.path.exists(functionname):
		print "Function NOT Found:",functionname
		

						
#currrently working on getting findReplaceFlags to work, so that I can add $NAME to image directories.
def get_str(Config, section, option):
	Config = checkConfig(Config)	
	try: return Config.get(section, option)
	except:
		print "Unable to load:",section, option
	return ''

def parseOptionOrDefault(Config,section,option,parsetype='',debug=True, optional=False):
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
		#try:	
		#except: default = ''

		#try:	value = findReplaceFlags(Config,Config.get(section, option))
		#except: value = ''
		
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
	return details


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
	self.name		= self.__cp__.get(section, 'name')	
	self.units		= self.__cp__.get(section, 'units')		
	self.dimensions		= self.__cp__.getint(section, 'dimensions')
		
	self.modelFiles 	= parseFilepath(self.__cp__, section, 'modelFiles',expecting1=False)
	self.modelFile_p2p 	= parseFilepath(self.__cp__, section, 'modelFile_p2p',expecting1=True)	
	self.dataFile   	= parseFilepath(self.__cp__, section, 'dataFile',  expecting1=True)
	self.gridFile 		= parseFilepath(self.__cp__, section, 'gridFile',  expecting1=True)

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
	self.images_p2p 	= parseOptionOrDefault(self.__cp__, section, 'images_p2p', )
	self.postproc_ts  	= parseOptionOrDefault(self.__cp__, section, 'postproc_ts',  )
	self.postproc_p2p 	= parseOptionOrDefault(self.__cp__, section, 'postproc_p2p', )
	self.reportdir 		= parseOptionOrDefault(self.__cp__, section, 'reportdir', )
	
	if debug: self.__print__()

  	
  	
  	
  
  def __print__(self):
	print "------------------------------------------------------------------"
	print "AnalysisKeyParser."
	print "File:		", self.__fn__
	print "jobID:		", self.jobID
	
	print "timeseries image folder:		", self.images_ts
	print "P2P image folder:		", self.images_p2p	
	print "timeseries postprocessed files:	", self.postproc_ts
	print "p2p postprocessed files:		", self.postproc_p2p

	print "year:		", self.year
	print "name:		", self.name
	print "units:		", self.units
	print "datasource:	", self.datasource
	print "model:		", self.model
	print "dimensions:	", self.dimensions
			
	print "model Files:	", self.modelFiles
	print "model Files:	", self.modelFile_p2p
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







