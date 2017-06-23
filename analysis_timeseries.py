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
.. module:: analysis_timeseries
   :platform: Unix
   :synopsis: A script to produce analysis for time series.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

#####
# Load Standard Python modules:
from sys import argv,exit
from os.path import exists
from calendar import month_name
from socket import gethostname
from glob import glob
from scipy.interpolate import interp1d
import numpy as np
import os,sys
from getpass import getuser

#####
# Load specific local code:
import UKESMpython as ukp
from timeseries import timeseriesAnalysis
from timeseries import profileAnalysis
from timeseries import timeseriesTools as tst

from bgcvaltools.mergeMonthlyFiles import mergeMonthlyFiles
from bgcvaltools.AOU import AOU
from bgcvaltools.dataset import dataset

#####
# User defined set of paths pointing towards the datasets.
import paths



#####
# Biogeochemistry keys
bgcKeys = []
if True:
	bgcKeys.append('N')                        # WOA Nitrate
	bgcKeys.append('Si')                       # WOA Siliate
	bgcKeys.append('O2')                       # WOA Oxygen
	bgcKeys.append('Alk')                      # Glodap Alkalinity
	bgcKeys.append('DIC')                      # Globap tCO2
	bgcKeys.append('AirSeaFlux')               # Air Sea Flux
	bgcKeys.append('TotalAirSeaFluxCO2')       # Total global air sea flux
	bgcKeys.append('IntPP_OSU')                # OSU Integrated primpary production
	bgcKeys.append('PP_OSU')                   # OSU Integrated primpary production
	bgcKeys.append('LocalExportRatio')         # Export ratio (no data)
	bgcKeys.append('GlobalExportRatio')        # Export ratio (no data)
	bgcKeys.append('TotalOMZVolume')           # Total Oxygen Minimum zone Volume
	bgcKeys.append('OMZThickness')             # Oxygen Minimum Zone Thickness
	bgcKeys.append('OMZMeanDepth')             # Oxygen Minimum Zone mean depth
	bgcKeys.append('AOU')                      # Apparent Oxygen Usage                         
	bgcKeys.append('Iron')                     # Iron
	bgcKeys.append('Dust')                     # Dust
	bgcKeys.append('TotalDust')                # Total Dust
	bgcKeys.append('DiaFrac')                  # Diatom Fraction
        bgcKeys.append('DTC')                      # Detrital carbon
        bgcKeys.append('CHL')                      # Total Chlorophyll        
        bgcKeys.append('DMS_ARAN')                      # Total Chlorophyll        


bgcKeysDict = {i:n for i,n in enumerate(bgcKeys)}

#####
# Physical keys
physKeys = []
if True:
	physKeys.append('T')                        	# WOA Temperature
	physKeys.append('GlobalMeanTemperature')    	# Global Mean Temperature
	physKeys.append('GlobalMeanSalinity')    	# Global Mean Salinity
	physKeys.append('IcelessMeanSST')    		# Global Mean Surface Temperature with no ice	
	physKeys.append('S')                        	# WOA Salinity
	physKeys.append('MLD')				# iFERMER Mixed Layer Depth 
	#physKeys.append('MaxMonthlyMLD')            	# MLD Monthly max           
	      			
	physKeys.append('TotalIceArea')			# work in progress
	physKeys.append('NorthernTotalIceArea')		# work in progress
	physKeys.append('SouthernTotalIceArea')		# work in progress
	physKeys.append('TotalIceExtent')		# work in progress
	physKeys.append('NorthernTotalIceExtent')	# work in progress
	physKeys.append('SouthernTotalIceExtent')	# work in progress
	
	physKeys.append('DrakePassageTransport')	# DrakePassageTransport
	physKeys.append('AMOC_32S')                 	# AMOC 32S
	physKeys.append('AMOC_26N')                 	# AMOC 26N
        physKeys.append('AMOC_26N_nomexico')            # AMOC 26N
	physKeys.append('ADRC_26N')                 	# ADRC 26N                        	                
	physKeys.append('ZonalCurrent')             	# Zonal Veloctity
	physKeys.append('MeridionalCurrent')        	# Meridional Veloctity
	physKeys.append('VerticalCurrent')          	# Vertical Veloctity
#	physKeys.append('WindStress')               	# Wind Stress                        	

	physKeys.append('sowaflup')			# Net Upward Water Flux 
#	physKeys.append('sohefldo')			# Net downward Water Flux 			
#	physKeys.append('sofmflup')			# Water flux due to freezing/melting
#	physKeys.append('sosfldow')			# Downward salt flux
	physKeys.append('soicecov')			# Ice fraction
#	physKeys.append('sossheig')                 # Sea surface height
physKeysDict = {i:n for i,n in enumerate(physKeys)}

#####
# Level 1 keys
level1Keys = []
level1Keys.extend(physKeys)
level1Keys.extend(bgcKeys)
level1KeysDict = {i:n for i,n in enumerate(level1Keys)}

#####
# The important keys
keymetricsfirstKeys = [
		'TotalAirSeaFluxCO2',
		'IntPP_OSU',
		'GlobalExportRatio',
                'TotalIceExtent', 
                'NorthernTotalIceExtent',
                'SouthernTotalIceExtent',
		'DrakePassageTransport',
		'AMOC_26N',
		'GlobalMeanTemperature',
		'GlobalMeanSalinity',]
keymetricsfirstDict = {i:n for i,n in enumerate(keymetricsfirstKeys)}




def analysis_timeseries(jobID = "u-ab671",
			clean = 0,
			annual = True,
			strictFileCheck = True,
			analysisSuite = 'all',
			regions = 'all',
			):

	"""
	The role of this code is to produce time series analysis.
	The jobID is the monsoon/UM job id and it looks for files with a specific format

	The clean flag allows you to start the analysis without loading previous data.

	The annual flag means that we look at annual (True) or monthly (False) data.

	The strictFileCheck switch checks that the data/model netcdf files exist.
	It fails if the switch is on and the files no not exist.

	analysisSuite chooses a set of fields to look at.

	regions selects a list of regions, default is 'all', which is the list supplied by Andy Yool.

	:param jobID: the jobID
	:param clean: deletes old images if true
	:param annual: Flag for monthly or annual model data.
	:param strictFileCheck: CStrickt check for model and data files. Asserts if no files are found.
	:param analysisSuite: Which data to analyse, ie level1, physics only, debug, etc
	:param regions:

	"""

	#print "analysis_p2p:",	jobID,clean, annual,strictFileCheck,analysisSuite,regions
	#assert 0

	#####
	# Switches:
	# These are some booleans that allow us to choose which analysis to run.
	# This lets up give a list of keys one at a time, or in parrallel.
	if type(analysisSuite) == type(['Its','A','list!']):
		analysisKeys = analysisSuite

	#####
	# Switches:
	# These are some preset switches to run in series.
	if type(analysisSuite) == type('Its_A_string'):
		analysisKeys = []

                if analysisSuite.lower() in ['keymetricsfirst',]:
			analysisKeys.extend(keymetricsfirstKeys)

                if analysisSuite.lower() in ['level1',]: 
                	analysisKeys.extend(level1Keys)
					
                if analysisSuite.lower() in ['bgc',]:
                	analysisKeys.extend(bgcKeys)
					
                if analysisSuite.lower() in ['physics',]:
                	analysisKeys.extend(physKeys)
                	
		if analysisSuite.lower() in ['level3',]:
                        analysisKeys.append('DMS_ARAN')                 # DMS Aranami Tsunogai


		if analysisSuite.lower() in ['debug',]:
			#analysisKeys.append('AirSeaFlux')		# work in progress
			#analysisKeys.append('TotalAirSeaFluxCO2')	# work in progress
			#analysisKeys.append('TotalOMZVolume')		# work in progress
			#analysisKeys.append('TotalOMZVolume50')	# work in progress
			#analysisKeys.append('OMZMeanDepth')		# work in progress
			#analysisKeys.append('OMZThickness')            # Oxygen Minimum Zone Thickness
			#analysisKeys.append('TotalOMZVolume')		# work in progress
                        #analysisKeys.append('O2')                      # WOA Oxygen
                        #analysisKeys.append('AOU')                      # Apparent Oxygen Usage 
                        #analysisKeys.append('WindStress')               # Wind Stress                        
                        #analysisKeys.append('Dust')                    # Dust
                        #analysisKeys.append('TotalDust')               # Total Dust
                        #analysisKeys.append('TotalDust_nomask')
			#analysisKeys.append('DIC')			# work in progress
			#analysisKeys.append('DrakePassageTransport')	# DrakePassageTransport
			#analysisKeys.append('TotalIceArea')		# work in progress
			#analysisKeys.append('CHN')
			#analysisKeys.append('CHD')
			#analysisKeys.append('CHL')	
			
			#if jobID in ['u-am004','u-am005']:
	                #        analysisKeys.append('DMS_ANDR')                 # DMS Anderson
			#else:   analysisKeys.append('DMS_ARAN')                 # DMS Aranami Tsunogai
	
			#analysisKeys.append('DiaFrac')			# work in progress
			#analysisKeys.append('Iron')			# work in progress
                        #analysisKeys.append('DTC')                 # work in progress

			#analysisKeys.append('Iron')			# work in progress
                        #analysisKeys.append('N')                        # WOA Nitrate
                        #analysisKeys.append('IntPP_OSU')               # OSU Integrated primpary production
                       
                        #####
                        # Physics switches:
                        #analysisKeys.append('T')                       # WOA Temperature
                        #analysisKeys.append('S')                        # WOA Salinity
                        #analysisKeys.append('MLD')                      # MLD
                        #analysisKeys.append('MaxMonthlyMLD')            # MLD                        
                        
                        #analysisKeys.append('NorthernTotalIceArea')    # work in progress
                        #analysisKeys.append('SouthernTotalIceArea')    # work in progress
                        #analysisKeys.append('TotalIceArea')            # work in progress
			#analysisKeys.append('TotalIceExtent')		# work in progress
			#analysisKeys.append('NorthernTotalIceExtent')	# work in progress
			#analysisKeys.append('SouthernTotalIceExtent')	# work in progress
                        #analysisKeys.append('AMOC_32S')                # AMOC 32S
                        analysisKeys.append('AMOC_26N')                # AMOC 26N
                        analysisKeys.append('AMOC_26N_nomexico')
                        #analysisKeys.append('ADRC_26N')                # AMOC 26N                        

                       	#analysisKeys.append('GlobalMeanTemperature')    # Global Mean Temperature
			#analysisKeys.append('GlobalMeanSalinity')    	# Global Mean Salinity                       	
                       	#analysisKeys.append('IcelessMeanSST')    	# Global Mean Surface Temperature with no ice
                       	#analysisKeys.append('quickSST')    		# Area Weighted Mean Surface Temperature

                       	#analysisKeys.append('ZonalCurrent')             # Zonal Veloctity
                       	#analysisKeys.append('MeridionalCurrent')        # Meridional Veloctity
                       	#analysisKeys.append('VerticalCurrent')          # Vertical Veloctity
                       	
			#analysisKeys.append('sowaflup')			# Net Upward Water Flux 
			#analysisKeys.append('sohefldo')			# Net downward Water Flux 			
#			analysisKeys.append('sofmflup')			# Water flux due to freezing/melting
#			analysisKeys.append('sosfldow')			# Downward salt flux
#			analysisKeys.append('soicecov')			# Ice fraction
#                       analysisKeys.append('sossheig')                 # Sea surface height

			#analysisKeys.append('max_soshfldo')		# Max short wave radiation.

                        #####
                        # Physics switches:

	#####
	# Some lists of region.
	# This are pre-made lists of regions that can be investigated.
	# Note that each analysis below can be given its own set of regions.
	if regions == 'all':
  		regionList	= ['Global', 'ignoreInlandSeas',
		  		'SouthernOcean','ArcticOcean',
				'Equator10', 'Remainder',
  				'NorthernSubpolarAtlantic','NorthernSubpolarPacific',
  				]
	if regions == 'short':
		regionList 	= ['Global','SouthernHemisphere','NorthernHemisphere',]

	#if analysisSuite.lower() in ['debug',]:
        #        regionList      = ['Global', 'ArcticOcean',]

	#####
	# The z_component custom command:
	# This flag sets a list of layers and metrics.
	# It's not advised to run all the metrics and all the layers, as it'll slow down the analysis.
	# if z_component in ['SurfaceOnly',]:

	layerList = ['Surface','500m','1000m',]
	metricList = ['mean','median', '10pc','20pc','30pc','40pc','50pc','60pc','70pc','80pc','90pc','min','max']

#	if z_component in ['FullDepth',]:
#		layerList = [0,2,5,10,15,20,25,30,35,40,45,50,55,60,70,]
#		metricList = ['mean','median',]






	#####
	# Location of images directory
	# the imagedir is where the analysis images will be saved.


	#####
	# Location of shelves folder
	# The shelve directory is where the intermediate processing files are saved in python's shelve format.
	# This allows us to put away a python open to be re-opened later.
	# This means that we can interupt the analysis without loosing lots of data and processing time,
	# or we can append new simulation years to the end of the analysis without starting from scratch each time.
	#shelvedir 	= ukp.folder('shelves/timeseries/'+jobID)



	#####
	# Location of data files.
	# The first thing that this function does is to check which machine it is being run.
	# This is we can run the same code on multiple machines withouht having to make many copies of this file.
	# So far, this has been run on the following machines:
	#	PML
	#	JASMIN
	#	Charybdis (Julien's machine at NOCS)
	#
	# Feel free to add other macihines onto this list, if need be.
	machinelocation = ''

	#####
	# PML
	if gethostname().find('pmpc')>-1:
		print "analysis-timeseries.py:\tBeing run at PML on ",gethostname()

		imagedir	 = ukp.folder(paths.imagedir+'/'+jobID+'/timeseries')

		if annual:	WOAFolder = paths.WOAFolder_annual
		else:		WOAFolder = paths.WOAFolder

		#shelvedir 	= ukp.folder(paths.shelvedir+'/'+jobID+'/timeseries/'+jobID)
		shelvedir 	= ukp.folder(paths.shelvedir+"/timeseries/"+jobID)		
	#####
	# JASMIN
	if gethostname().find('ceda.ac.uk')>-1:
		print "analysis-timeseries.py:\tBeing run at CEDA on ",gethostname()
		#machinelocation = 'JASMIN'

		shelvedir 	= ukp.folder("/group_workspaces/jasmin2/ukesm/BGC_data/"+getuser()+"/shelves/timeseries/"+jobID)
		if annual:	WOAFolder = paths.WOAFolder_annual
		else:		WOAFolder = paths.WOAFolder

		imagedir	 = ukp.folder(paths.imagedir+'/'+jobID+'/timeseries')


        if gethostname().find('monsoon')>-1:
        	print "Please set up paths.py"
        	assert 0

                #print "analysis-timeseries.py:\tBeing run at the Met Office on ",gethostname()
                #machinelocation = 'MONSOON'

                #ObsFolder       = "/projects/ukesm/ldmora/BGC-data/"
                #ModelFolder       = "/projects/ukesm/ldmora/UKESM"
                #####
                # Location of model files.
                #MEDUSAFolder_pref       = ukp.folder(ModelFolder)

                #####
                # Location of data files.
                #if annual:      WOAFolder       = ukp.folder(ObsFolder+"WOA/annual")
                #else:           WOAFolder       = ukp.folder(ObsFolder+"WOA/")

                #MAREDATFolder   = ObsFolder+"/MAREDAT/MAREDAT/"
                #GEOTRACESFolder = ObsFolder+"/GEOTRACES/GEOTRACES_PostProccessed/"
                #TakahashiFolder = ObsFolder+"/Takahashi2009_pCO2/"
                #MLDFolder       = ObsFolder+"/IFREMER-MLD/"
                #iMarNetFolder   = ObsFolder+"/LestersReportData/"
                #GlodapDir       = ObsFolder+"/GLODAP/"
                #GLODAPv2Dir     = ObsFolder+"/GLODAPv2/GLODAPv2_Mapped_Climatologies/"
                #OSUDir          = ObsFolder+"OSU/"
                #CCIDir          = ObsFolder+"CCI/"
                #orcaGridfn      = ModelFolder+'/mesh_mask_eORCA1_wrk.nc'



	#####
	# Unable to find location of files/data.
	if not paths.machinelocation:
		print "analysis-timeseries.py:\tFATAL:\tWas unable to determine location of host: ",gethostname()
        	print "Please set up paths.py, based on Paths/paths_template.py"
		assert False



        #####
        # Because we can never be sure someone won't randomly rename the 
        # time dimension without saying anything.
        if jobID in ['u-am515','u-am927','u-am064']:
                #####
                # Because we can never be sure someone won't randomly rename the 
                # time dimension without saying anything.
		ukesmkeys={}
                ukesmkeys['time'] 	= 'time_centered'
		ukesmkeys['temp3d'] 	= 'thetao'
                ukesmkeys['sst'] 	= 'tos'
                ukesmkeys['sal3d']     = 'so'
                ukesmkeys['sss']        = 'sos'
                ukesmkeys['v3d']     = 'vo'
                ukesmkeys['u3d']     = 'uo'
                ukesmkeys['e3u']    = 'thkcello'
                ukesmkeys['w3d']     = 'wo'

        else:
                ukesmkeys={}
                ukesmkeys['time'] = 'time_counter'
                ukesmkeys['temp3d']     = 'votemper'
                ukesmkeys['sst']        = ''
                ukesmkeys['sal3d']     = 'vosaline'
                ukesmkeys['sss']        = ''
                ukesmkeys['v3d']     = 'vomecrty'
                ukesmkeys['u3d']     = 'vozocrtx'
                ukesmkeys['e3u']    = 'e3u'
                ukesmkeys['w3d']     = 'vovecrtz'
	#####
	# Coordinate dictionairy
	# These are python dictionairies, one for each data source and model.
	# This is because each data provider seems to use a different set of standard names for dimensions and time.
	# The 'tdict' field is short for "time-dictionary".
	#	This is a dictionary who's indices are the values on the netcdf time dimension.
	#	The tdict indices point to a month number in python numbering (ie January = 0)
	# 	An example would be, if a netcdf uses the middle day of the month as it's time value:
	#		tdict = {15:0, 45:1 ...}

	timekey		= ukesmkeys['time']
	medusaCoords 	= {'t':timekey, 'z':'deptht', 'lat': 'nav_lat',  'lon': 'nav_lon',   'cal': '360_day',}	# model doesn't need time dict.
	medusaUCoords 	= {'t':timekey, 'z':'depthu', 'lat': 'nav_lat',  'lon': 'nav_lon',   'cal': '360_day',}	# model doesn't need time dict.
	medusaVCoords 	= {'t':timekey, 'z':'depthv', 'lat': 'nav_lat',  'lon': 'nav_lon',   'cal': '360_day',}	# model doesn't need time dict.
	medusaWCoords 	= {'t':timekey, 'z':'depthw', 'lat': 'nav_lat',  'lon': 'nav_lon',   'cal': '360_day',}	# model doesn't need time dict.

	icCoords 	= {'t':timekey, 'z':'nav_lev', 'lat': 'nav_lat',  'lon': 'nav_lon',   'cal': '360_day',}	# model doesn't need time dict.
	maredatCoords 	= {'t':'index_t', 'z':'DEPTH',  'lat': 'LATITUDE', 'lon': 'LONGITUDE', 'cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	takahashiCoords	= {'t':'index_t', 'z':'index_z','lat': 'LAT', 'lon': 'LON', 'cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	woaCoords 	= {'t':'index_t', 'z':'depth',  'lat': 'lat', 	   'lon': 'lon',       'cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	osuCoords	= {'t':'index_t', 'z':'',  	'lat': 'latitude', 'lon': 'longitude', 'cal': 'standard','tdict':[] }
	glodapCoords	= {'t':'index_t', 'z':'depth',  'lat': 'latitude', 'lon': 'longitude', 'cal': 'standard','tdict':[] }	
	glodapv2Coords	= {'t':'time',    'z':'Pressure','lat':'lat',      'lon':'lon',        'cal': '',        'tdict':{0:0,} }
	mldCoords	= {'t':'index_t', 'z':'index_z','lat':'lat',       'lon': 'lon','cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	dmsCoords	= {'t':'time',    'z':'depth',  'lat':'Latitude',  'lon': 'Longitude','cal': 'standard','tdict':ukp.tdicts['ZeroToZero']}
	cciCoords	= {'t':'index_t', 'z':'index_z','lat': 'lat',      'lon': 'lon', 'cal': 'standard','tdict':['ZeroToZero'] }
	godasCoords 	= {'t':'index_t',    'z':'level',  'lat': 'lat',      'lon': 'lon', 'cal': 'standard','tdict':['ZeroToZero'] }


	def listModelDataFiles(jobID, filekey, datafolder, annual):
		print "listing model data files:",jobID, filekey, datafolder, annual
		if annual:
			return sorted(glob(datafolder+jobID+"/"+jobID+"o_1y_*_"+filekey+".nc"))
		else:
			return sorted(glob(datafolder+jobID+"/"+jobID+"o_1m_*_"+filekey+".nc"))


	masknc = dataset(paths.orcaGridfn,'r')
	tlandmask = masknc.variables['tmask'][:]
	masknc.close()

	def applyLandMask(nc,keys):
		#### works like no change, but applies a mask.
		return np.ma.masked_where(tlandmask==0,nc.variables[keys[0]][:].squeeze())
		
        def applySurfaceMask(nc,keys):
                #### works like no change, but applies a mask.
                return np.ma.masked_where(tlandmask[0,:,:]==0, nc.variables[keys[0]][:].squeeze())
                
	def applyLandMask1e3(nc,keys):
		return applyLandMask(nc,keys)*1000.
  	#####
  	# The analysis settings:
  	# Below here is a list of analysis settings.
  	# The settings are passed to timeseriesAnalysis using a nested dictionary (called an autovivification, here).
  	#
  	# These analysis were switched on or off at the start of the function.
  	# Each analysis requires:
  	#	model files
  	#	data files
  	#	model and data coordinate dictionaries, (defines above)
  	#	model and data details (a set of instructions of what to analyse:
  	#		name: 		field name
  	#		vars:		variable names in the netcdf
  	#		convert: 	a function to manipuate the data (ie change units, or add two fields together.
  	#				There are some standard ones in UKESMPython.py, but you can write your own here.
  	#		units: 		the units after the convert function has been applied.
  	#		layers:		which vertical layers to look at (ie, surface, 100m etc...)
  	#		regions:	which regions to look at. Can be speficied here, or use a pre-defined list (from above)
  	#		metrics:	what metric to look at:  mean, median or sum
  	#		model and data source: 	the name of source of the model/data (for plotting)
  	#		model grid: 	the model grid, usually eORCA1
  	#		the model grid file: 	the file path for the model mesh file (contains cell area/volume/masks, etc)
  	#
  	#	Note that the analysis can be run with just the model, it doesn't require a data file.
  	#	If so, just set to data file to an empty string:
  	#		av[name]['dataFile']  = ''

	av = ukp.AutoVivification()
	if 'Chl_pig' in analysisKeys:
		name = 'Chlorophyll_pig'
		av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
		av[name]['dataFile'] 		= paths.MAREDATFolder+"MarEDat20121001Pigments.nc"

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= maredatCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['CHN','CHD'], 'convert': ukp.sums,'units':'mg C/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['Chlorophylla',], 'convert': ukp.div1000,'units':'ug/L'}

		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'MAREDAT'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'CHL' in analysisKeys:
		name = 'Chlorophyll'
		av[name]['modelFiles']  	= listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= maredatCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['CHN','CHD'], 'convert': ukp.sums,'units':'mg C/m^3'}
		av[name]['datadetails']  	= {'name': '', 'units':''}
		
		av[name]['layers'] 		= ['Surface','100m','200m',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3
		

	if 'Chl_CCI' in analysisKeys:
		name = 'Chlorophyll_cci'
		#####
		# Not that this is the 1 degree resolution dataset, but higher resolution data are also available.

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 	= paths.CCIDir+"ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-annual-fv2.0.nc"
			print paths.ModelFolder_pref+"/"+jobID+"o_1y_*_ptrc_T.nc"
		else:	av[name]['dataFile'] 	= paths.CCIDir+'ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-all-fv2.0.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= cciCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['CHN','CHD'], 'convert': ukp.sums,'units':'mg C/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['chlor_a',], 'convert':  ukp.NoChange,'units':'mg C/m^3'}

		av[name]['layers'] 		= ['Surface',] 	# CCI is surface only, it's a satellite product.
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList	#['mean','median', ]

		av[name]['datasource'] 		= 'CCI'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2


	if 'CHD' in analysisKeys or  'CHN' in analysisKeys:
	    for name in ['CHD','CHN',]:
	        if name not in analysisKeys: continue

		av[name]['modelFiles']  	= listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= ''

		av[name]['modeldetails'] 	= {'name': name, 'vars':[name,], 'convert': ukp.NoChange,'units':'mg C/m^3'}
		av[name]['datadetails']  	= {'name': '', 'units':''}

		av[name]['layers'] 		= ['Surface',]#'100m',] 	# CCI is surface only, it's a satellite product.
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList	#['mean','median', ]

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

        if 'DTC' in analysisKeys:
            for name in ['DTC',]:
                if name not in analysisKeys: continue

                av[name]['modelFiles']          = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
                av[name]['dataFile']            = ''

                av[name]['modelcoords']         = medusaCoords
                av[name]['datacoords']          = ''

                av[name]['modeldetails']        = {'name': name, 'vars':[name,], 'convert': ukp.mul1000,'units':'umol-C/m3'}
                av[name]['datadetails']         = {'name': '', 'units':''}

                av[name]['layers']              = ['3000m',]#'100m',]         # CCI is surface only, it's a satellite product.
                av[name]['regions']             = regionList
                av[name]['metrics']             = metricList    #['mean','median', ]

                av[name]['datasource']          = ''
                av[name]['model']               = 'MEDUSA'

                av[name]['modelgrid']           = 'eORCA1'
                av[name]['gridFile']            = paths.orcaGridfn
                av[name]['Dimensions']          = 3


	if 'DiaFrac' in analysisKeys:

		name = 'DiaFrac'
		def caldiafrac(nc,keys):
			chd = applyLandMask(nc,[keys[0],]).squeeze()
                        chn = applyLandMask(nc,[keys[1],]).squeeze()
			return 100.*chd/(chd+chn)

		av[name]['modelFiles']  	= listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= ''

		av[name]['modeldetails'] 	= {'name': name, 'vars':['CHD','CHN',], 'convert': caldiafrac,'units':'%'}
		av[name]['datadetails']  	= {'name': '', 'units':''}

		av[name]['layers'] 		= ['Surface','100m',] 	# CCI is surface only, it's a satellite product.
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList	#['mean','median', ]

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3


	if 'N' in analysisKeys:
		name = 'Nitrate'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		=  WOAFolder+'/woa13_all_n00_01.nc'
		else:
			av[name]['dataFile'] 		=  WOAFolder+'/nitrate_monthly_1deg.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['DIN',], 'convert': ukp.NoChange,'units':'mmol N/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['n_an',], 'convert': ukp.NoChange,'units':'mmol N/m^3'}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList

		#av[name]['layers'] 		= ['Surface','300m',]#'1000m',]#'Surface - 300m',]'100m',
		#av[name]['regions'] 		= regionList#['Global',]#'NorthAtlanticOcean','SouthAtlanticOcean',]#'NorthAtlantic']
		av[name]['metrics']		= metricList #['mean','median', ]

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'Si' in analysisKeys:
		name = 'Silicate'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		= WOAFolder+'woa13_all_i00_01.nc'
		else:
			av[name]['dataFile'] 		= WOAFolder+'wsilicate_monthly_1deg.nc'
		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['SIL',],  'convert': ukp.NoChange,'units':'mmol Si/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['i_an',], 'convert': ukp.NoChange,'units':'mmol Si/m^3'}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'O2' in analysisKeys:
		name = 'Oxygen'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
			av[name]['dataFile'] 		=  WOAFolder+'woa13_all_o00_01.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['OXY',], 'convert': ukp.NoChange,'units':'mmol O2/m^3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['o_an',], 'convert': ukp.oxconvert,'units':'mmol O2/m^3'}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'OMZMeanDepth' in analysisKeys:
		if annual:
			av['OMZMeanDepth']['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
			av['OMZMeanDepth']['dataFile'] 		=  WOAFolder+'woa13_all_o00_01.nc'
		else:
			print "OMZ Thickness not implemented for monthly data"
			assert 0

		nc = dataset(paths.orcaGridfn,'r')
		depths   	= np.abs(nc.variables['gdepw' ][:])
		tmask 		= nc.variables['tmask'][:]
		nc.close()

		omzthreshold = 20.

		def modelMeanOMZdepth(nc,keys):
			o2 = np.ma.array(nc.variables[keys[0]][:].squeeze())
			meandepth = np.ma.masked_where((o2>omzthreshold)+o2.mask + (tmask==0),depths).mean(0)
			if meandepth.max() in [0.,0]: return np.array([0.,])
			return np.ma.masked_where(meandepth==0., meandepth)

		def woaMeanOMZdepth(nc,keys):
			o2 = np.ma.array(nc.variables[keys[0]][:].squeeze() *44.661)
			pdepths = np.zeros_like(o2)
			lons = nc.variables['lon'][:]
			lats = nc.variables['lat'][:]
			wdepths = np.abs(nc.variables['depth'][:])

			for y,lat in enumerate(lats):
			    for x,lon in enumerate(lons):
				pdepths[:,y,x] = wdepths
			wmeanDepth = np.ma.masked_where((o2>omzthreshold)+o2.mask,pdepths).mean(0).data
			print "woaMeanOMZdepth",wmeanDepth.min(),wmeanDepth.mean(),wmeanDepth.max()
			#assert 0

			if wmeanDepth.max() in [0.,0]: return np.array([1000.,])
			return np.ma.masked_where(wmeanDepth==0., wmeanDepth)

		av['OMZMeanDepth']['modelcoords'] 	= medusaCoords
		av['OMZMeanDepth']['datacoords'] 	= woaCoords

		av['OMZMeanDepth']['modeldetails'] 	= {'name': 'OMZMeanDepth', 'vars':['OXY',],  'convert': modelMeanOMZdepth,'units':'m'}
		av['OMZMeanDepth']['datadetails']  	= {'name': 'OMZMeanDepth', 'vars':['o_an',], 'convert': woaMeanOMZdepth,'units':'m'}

		av['OMZMeanDepth']['layers'] 		= ['layerless',]
		av['OMZMeanDepth']['regions'] 		= regionList
		av['OMZMeanDepth']['metrics']		= metricList

		av['OMZMeanDepth']['datasource'] 	= 'WOA'
		av['OMZMeanDepth']['model']		= 'MEDUSA'

		av['OMZMeanDepth']['modelgrid']		= 'eORCA1'
		av['OMZMeanDepth']['gridFile']		= paths.orcaGridfn
		av['OMZMeanDepth']['Dimensions']	= 2





	if 'OMZThickness' in analysisKeys or 'OMZThickness50' in analysisKeys:
		if 'OMZThickness' in analysisKeys and 'OMZThickness50' in analysisKeys:
			print "Only run one of these at a time"
			assert 0


		if annual:
			av['OMZThickness']['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
			av['OMZThickness']['dataFile'] 		=  WOAFolder+'woa13_all_o00_01.nc'
		else:
			print "OMZ Thickness not implemented for monthly data"
			assert 0

		nc = dataset(paths.orcaGridfn,'r')
		thickness   	= nc.variables['e3t' ][:]
		tmask 		= nc.variables['tmask'][:]
		nc.close()

		if 'OMZThickness' in analysisKeys: 	omzthreshold = 20.
		if 'OMZThickness50' in analysisKeys: 	omzthreshold = 50.

		def modelOMZthickness(nc,keys):
			o2 = np.ma.array(nc.variables[keys[0]][:].squeeze())
			totalthick = np.ma.masked_where((o2>omzthreshold)+o2.mask+ (tmask==0),thickness).sum(0).data
			if totalthick.max() in [0.,0]: return np.array([0.,])

			return np.ma.masked_where(totalthick==0., totalthick)
			#return np.ma.masked_where((arr>omzthreshold) + (arr <0.) + arr.mask,thickness).sum(0)


		def woaOMZthickness(nc,keys):
			o2 = nc.variables[keys[0]][:].squeeze() *44.661
			pthick = np.zeros_like(o2)
			lons = nc.variables['lon'][:]
			lats = nc.variables['lat'][:]
			zthick  = np.abs(nc.variables['depth_bnds'][:,0] - nc.variables['depth_bnds'][:,1])

			for y,lat in enumerate(lats):
			    for x,lon in enumerate(lons):
				pthick[:,y,x] = zthick
			totalthick = np.ma.masked_where((o2>omzthreshold)+o2.mask,pthick).sum(0).data

			if totalthick.max() in [0.,0]: return np.array([0.,])
			return np.ma.masked_where(totalthick==0., totalthick)

		av['OMZThickness']['modelcoords'] 	= medusaCoords
		av['OMZThickness']['datacoords'] 		= woaCoords

		av['OMZThickness']['modeldetails'] 	= {'name': 'OMZThickness', 'vars':['OXY',], 'convert': modelOMZthickness,'units':'m'}
		av['OMZThickness']['datadetails']  	= {'name': 'OMZThickness', 'vars':['o_an',], 'convert': woaOMZthickness,'units':'m'}

		av['OMZThickness']['layers'] 		= ['layerless',]
		av['OMZThickness']['regions'] 		= regionList
		av['OMZThickness']['metrics']		= metricList

		av['OMZThickness']['datasource'] 		= 'WOA'
		av['OMZThickness']['model']		= 'MEDUSA'

		av['OMZThickness']['modelgrid']		= 'eORCA1'
		av['OMZThickness']['gridFile']		= paths.orcaGridfn
		av['OMZThickness']['Dimensions']		= 2




	if 'TotalOMZVolume' in analysisKeys or 'TotalOMZVolume50' in analysisKeys:
		if 'TotalOMZVolume' in analysisKeys and 'TotalOMZVolume50' in analysisKeys:
			print "Only run one of these at a time"
			assert 0

		if annual:
			av['TotalOMZVolume']['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
			av['TotalOMZVolume']['dataFile'] 	=  WOAFolder+'woa13_all_o00_01.nc'
		else:
			print "OMZ volume not implemented for monthly data"
			assert 0

		nc = dataset(paths.orcaGridfn,'r')
		try:
			pvol   = nc.variables['pvol' ][:]
			tmask = nc.variables['tmask'][:]
		except:
			tmask = nc.variables['tmask'][:]
			area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
			pvol = nc.variables['e3t'][:] *area
			pvol = np.ma.masked_where(tmask==0,pvol)
		nc.close()

		if 'TotalOMZVolume' in analysisKeys:	omzthreshold = 20.
		if 'TotalOMZVolume50' in analysisKeys:	omzthreshold = 50.

		def modelTotalOMZvol(nc,keys):
			arr = np.ma.array(nc.variables[keys[0]][:].squeeze())
			return np.ma.masked_where((arr>omzthreshold) + pvol.mask + arr.mask,pvol).sum()


		def woaTotalOMZvol(nc,keys):
			arr = np.ma.array(nc.variables[keys[0]][:].squeeze() *44.661)
			#area = np.zeros_like(arr[0])
			pvol = np.zeros_like(arr)
			#np.ma.masked_wjhere(arr.mask + (arr <0.)+(arr >1E10),np.zeros_like(arr))
			lons = nc.variables['lon'][:]
			lats = nc.variables['lat'][:]
			#lonbnds = nc.variables['lon_bnds'][:]
			latbnds = nc.variables['lat_bnds'][:]
			zthick  = np.abs(nc.variables['depth_bnds'][:,0] - nc.variables['depth_bnds'][:,1])

			for y,lat in enumerate(lats):
				area = ukp.Area([latbnds[y,0],0.],[latbnds[y,1],1.])
				for z,thick in enumerate(zthick):
					pvol[z,y,:] = np.ones_like(lons)*area*thick

			return np.ma.masked_where(arr.mask + (arr >omzthreshold)+(arr <0.),pvol).sum()

		av['TotalOMZVolume']['modelcoords'] 	= medusaCoords
		av['TotalOMZVolume']['datacoords'] 	= woaCoords

		av['TotalOMZVolume']['modeldetails'] 	= {'name': 'TotalOMZVolume', 'vars':['OXY',], 'convert': modelTotalOMZvol,'units':'m^3'}
		av['TotalOMZVolume']['datadetails']  	= {'name': 'TotalOMZVolume', 'vars':['o_an',], 'convert': woaTotalOMZvol,'units':'m^3'}

		av['TotalOMZVolume']['layers'] 		= ['layerless',]
		av['TotalOMZVolume']['regions'] 	= ['regionless',]
		av['TotalOMZVolume']['metrics']		= ['metricless', ]

		av['TotalOMZVolume']['datasource'] 		= 'WOA'
		av['TotalOMZVolume']['model']		= 'MEDUSA'

		av['TotalOMZVolume']['modelgrid']		= 'eORCA1'
		av['TotalOMZVolume']['gridFile']		= paths.orcaGridfn
		av['TotalOMZVolume']['Dimensions']		= 1


	if 'AOU' in analysisKeys:
		name = 'AOU'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
			av[name]['dataFile'] 		=  ''#WOAFolder+'woa13_all_o00_01.nc'

		def modelAOU(nc,keys):
			o2 =  nc.variables[keys[0]][:]
			
			ncpath = nc.filename
			print ncpath

			newpath=ncpath.replace('ptrc_T', 'grid_T')
			
			print "modelAOU:",ncpath, newpath
			nc2 = dataset(newpath,'r')
			print "Loaded",newpath
			temp = nc2.variables[ukesmkeys['temp3d']][:]
			sal  = nc2.variables[ukesmkeys['sal3d']][:]			
			return AOU(temp,sal,o2)
			
		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['OXY',ukesmkeys['temp3d'],ukesmkeys['sal3d']], 'convert': modelAOU,'units':'mmol O2/m^3'}
		av[name]['datadetails']  	= {'name':'','units':'',}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3	


	if 'DIC' in analysisKeys:

		def convertkgToM3(nc,keys):
			return nc.variables[keys[0]][:]* 1.027

		name = 'DIC'

		av[name]['modelFiles'] 		= listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 		= paths.GLODAPv2Dir+ 'GLODAPv2.tco2.historic.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= glodapv2Coords

		av[name]['modeldetails'] 	= {'name': 'DIC', 'vars':['DIC',],  'convert': ukp.NoChange,'units':'mmol C/m^3'}
		av[name]['datadetails']  	= {'name': 'DIC', 'vars':['tco2',], 'convert': ukp.convertkgToM3,'units':'mmol C/m^3'}

		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GLODAP'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'Alk' in analysisKeys:
		def convertmeqm3TOumolkg(nc,keys):
			return nc.variables[keys[0]][:]* 1.027

		name = 'Alkalinity'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
			av[name]['dataFile'] 	=  paths.GlodapDir+'Alk.nc'
		else:
			print "Alkalinity data not available for monthly Analysis"
			assert 0

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= glodapCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['ALK',], 'convert': ukp.NoChange,'units':'meq/m^3',}
		av[name]['datadetails']  	= {'name': name, 'vars':['Alk',], 'convert': convertmeqm3TOumolkg,'units':'meq/m^3',}

	#	av[name]['layers'] 		=  ['Surface','100m','300m','1000m',]
	#	av[name]['regions'] 		= regionList
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GLODAP'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3


	if 'AirSeaFlux' in analysisKeys:

		#nc = dataset(paths.orcaGridfn,'r')
		#area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		#nc.close()

		def eOrcaTotal(nc,keys):
			factor =  12./1000.
			arr = nc.variables['CO2FLUX'][:].squeeze()	# mmolC/m2/d
			#if arr.ndim ==3:
			#	for i in np.arange(arr.shape[0]):
			#		arr[i] = arr[i]*area
			#elif arr.ndim ==2: arr = arr*area
			#else: assert 0
			return arr * factor

		def takaTotal(nc,keys):
			arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
			arr = -1.E12* arr / 365.				#g Carbon/day
			factor = -1.E12/(365. ) # convert to #/ 1.E12
			area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
			fluxperarea = arr/area
			#arr = arr*area #* 1.E24 	# converts area into m^2
			#print arr.sum(), arr.sum()*factor
			return fluxperarea
			# area 10^6 km^2
			# flux:  10^15 g Carbon month^-1. (GT)/m2/month


		name = 'AirSeaFluxCO2'

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		=  paths.TakahashiFolder+'takahashi_2009_Anual_sumflux_2006c_noHead.nc'
		else:
			av[name]['dataFile'] 		=  paths.TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'
			print "Air Sea Flux CO2 monthly not implemented"
			assert 0
			#av[name]['dataFile'] 		=  paths.TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= takahashiCoords
		av[name]['modeldetails'] 	= {'name': 'AirSeaFluxCO2', 'vars':['CO2FLUX',], 'convert': eOrcaTotal,'units':'g C/m2/day'}
		av[name]['datadetails']  	= {'name': 'AirSeaFluxCO2', 'vars':['TFLUXSW06','AREA_MKM2'], 'convert': takaTotal,'units':'g C/m2/day'}
		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

	if 'TotalAirSeaFluxCO2' in analysisKeys:
		name = 'TotalAirSeaFluxCO2'
		nc = dataset(paths.orcaGridfn,'r')
		area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		nc.close()

                def uam515_TotalCO2(nc,keys):
                	#####
                	# Hack to deal with the problem in the caspian sea in the spin up job, u-am515.
                	# This is only to dfea
                        factor =  365.25 * 12./1000. / 1.E15
                        times =  tst.getTimes(nc, medusaCoords)
                        if times[0] <2262.:
				arr = nc.variables['CO2FLUX'][:].squeeze()
				arr = np.ma.masked_where(np.ma.abs(arr)>1E10,arr)
                      	  	arr = arr * factor *area    # mmolC/m2/d                        	
                                print "uam515_TotalCO2:\tMasking u-am515", arr.min(),arr.mean(),arr.max()
                        else:
	                        arr = nc.variables['CO2FLUX'][:].squeeze() * factor  *area   # mmolC/m2/d
                        
#                        if arr.ndim ==3:
#                                for i in np.arange(arr.shape[0]):
#                                      uam515_TotalCO2  arr[i] = arr[i]*area
#                        elif arr.ndim ==2: arr = arr*area
#                        else: assert 0
                        return np.ma.sum(arr)

			

		def eOrcaTotal(nc,keys):
			factor =  365.25 * 12./1000. / 1.E15
			arr = nc.variables['CO2FLUX'][:].squeeze() * factor	# mmolC/m2/d
			if arr.ndim ==3:
				for i in np.arange(arr.shape[0]):
					arr[i] = arr[i]*area
			elif arr.ndim ==2: arr = arr*area
			else: assert 0
			return arr.sum()

		def takaTotal(nc,keys):
			arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
			arr = -1.E12* arr /1.E15#/ 365.				#g Carbon/day
			#area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
			#fluxperarea = arr/area
			return arr.sum()
			# area 10^6 km^2
			# flux:  10^15 g Carbon month^-1. (GT)/m2/month




		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		=  paths.TakahashiFolder+'takahashi_2009_Anual_sumflux_2006c_noHead.nc'
		else:
			av[name]['dataFile'] 		=  paths.TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'
			print "Air Sea Flux CO2 monthly not implemented"
			assert 0
			#av[name]['dataFile'] 		=  paths.TakahashiFolder+'takahashi2009_month_flux_pCO2_2006c_noHead.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= takahashiCoords
		if jobID == 'u-am515':	av[name]['modeldetails']        = {'name': 'AirSeaFluxCO2', 'vars':['CO2FLUX',], 'convert': uam515_TotalCO2,'units':'Pg C/yr'}
		else:	                av[name]['modeldetails']        = {'name': 'AirSeaFluxCO2', 'vars':['CO2FLUX',], 'convert': eOrcaTotal,'units':'Pg C/yr'}
		#av[name]['modeldetails'] 	= {'name': 'AirSeaFluxCO2', 'vars':['CO2FLUX',], 'convert': eOrcaTotal,'units':'Pg C/yr'}
		av[name]['datadetails']  	= {'name': 'AirSeaFluxCO2', 'vars':['TFLUXSW06','AREA_MKM2'], 'convert': takaTotal,'units':'Pg C/yr'}
		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

		noTaka = True
		if noTaka:
			av[name]['datadetails'] =  {'name': '',	'units':''}
			av[name]['dataFile']	= ''
			av[name]['datasource']  = ''


	if 'IntPP_iMarNet' in analysisKeys:
		name = 'IntegratedPrimaryProduction_1x1'

		def medusadepthInt(nc,keys):
			return (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:])* 6.625 * 12.011 / 1000.

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)
		#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_diad_T.nc"))
		av[name]['dataFile'] 		= paths.iMarNetFolder+"/PPint_1deg.nc"


		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= maredatCoords

		av[name]['modeldetails'] 	= {'name': 'IntPP', 'vars':['PRN' ,'PRD'], 'convert': medusadepthInt,'units':'mg C/m^3'}
		#av[name]['datadetails']  	= {'name': 'IntPP', 'vars':['Chlorophylla',], 'convert': ukp.div1000,'units':'ug/L'}
		av[name]['datadetails']  	= {'name': 'IntPP', 'vars':['PPint',], 'convert': ukp.div1000,'units':'[ug/L/d'}


		av[name]['layers'] 		= ['Surface',]#'100m','200m','Surface - 1000m','Surface - 300m',]#'depthint']
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'MAREDAT'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

	if 'PP_OSU' in analysisKeys:
		nc = dataset(paths.orcaGridfn,'r')
		area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		nc.close()
		def medusadepthInt(nc,keys):
			#	 mmolN/m2/d        [mg C /m2/d]   [mgC/m2/yr] [gC/m2/yr]     Gt/m2/yr
			factor = 1.		* 6.625 * 12.011 #* 365.	      / 1000.   /     1E15
			arr = (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:]).squeeze()*factor
			#if arr.ndim ==3:
			#	for i in np.arange(arr.shape[0]):
			#		arr[i] = arr[i]*area
			#elif arr.ndim ==2: arr = arr*area
			#else: assert 0
			return arr



		name = 'IntegratedPrimaryProduction_OSU'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)
			av[name]['dataFile'] 		= paths.OSUDir +"/standard_VGPM.SeaWIFS.global.average.nc"
#		else:
#			print ""

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= osuCoords



		nc = dataset(av[name]['dataFile'] ,'r')
		lats = nc.variables['latitude'][:]
		osuareas = np.zeros((1080, 2160))
		osuarea = (111100. / 6.)**2. # area of a pixel at equator. in m2
		for a in np.arange(1080):osuareas[a] = np.ones((2160,))*osuarea*np.cos(np.deg2rad(lats[a]))


		def osuconvert(nc,keys):
			arr = nc.variables[keys[0]][:,:,:]
			#tlen = arr.shape[0]

			#arr  = arr.sum(0)/tlen * 365.	/ 1000. /     1E15
			#if arr.ndim ==3:
			#	for i in np.arange(arr.shape[0]):
			#		arr[i] = arr[i]*osuarea
			#elif arr.ndim ==2: arr = arr*osuarea
			#else: assert 0
			return arr




		av[name]['modeldetails'] 	= {'name': name, 'vars':['PRN' ,'PRD'], 'convert': medusadepthInt,'units':'mgC/m^2/day'}
		av[name]['datadetails']  	= {'name': name, 'vars':['NPP',], 'convert': osuconvert,'units':'mgC/m^2/day'}

		av[name]['layers'] 		= ['Surface',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= 'OSU'
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

	#####
	# Total
	if 'IntPP_OSU' in analysisKeys:
		noOSU = True
		nc = dataset(paths.orcaGridfn,'r')
		area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
		nc.close()
		def medusadepthInt(nc,keys):
			#	 mmolN/m2/d        [mg C /m2/d]   [mgC/m2/yr] [gC/m2/yr]     Gt/m2/yr
			factor = 1.		* 6.625 * 12.011 * 365.	      / 1000.   /     1E15
			arr = (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:]).squeeze()*factor
			if arr.ndim ==3:
				for i in np.arange(arr.shape[0]):
					arr[i] = arr[i]*area
			elif arr.ndim ==2: arr = arr*area
			else: assert 0
			return arr.sum()

		name = 'TotalIntegratedPrimaryProduction'
		if annual:
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)
			if noOSU:	av[name]['dataFile']            = ''
			else:		av[name]['dataFile'] 		= paths.OSUDir +"/standard_VGPM.SeaWIFS.global.average.nc"

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= glodapCoords

                av[name]['modeldetails']        = {'name': 'IntPP_OSU', 'vars':['PRN' ,'PRD'], 'convert': medusadepthInt,'units':'Gt/yr'}
		if noOSU:
	                av[name]['datadetails']         = {'name': '', 'units':''}

		else:
			nc = dataset(av[name]['dataFile'] ,'r')
			lats = nc.variables['latitude'][:]
			osuareas = np.zeros((1080, 2160))
			osuarea = (111100. / 6.)**2. # area of a pixel at equator. in m2
			for a in np.arange(1080):osuareas[a] = np.ones((2160,))*osuarea*np.cos(np.deg2rad(lats[a]))


			def osuconvert(nc,keys):
				arr = nc.variables[keys[0]][:,:,:]
				tlen = arr.shape[0]
				arr  = arr.sum(0)/tlen * 365.	/ 1000. /     1E15
				if arr.ndim ==3:
					for i in np.arange(arr.shape[0]):
						arr[i] = arr[i]*osuarea
				elif arr.ndim ==2: arr = arr*osuarea
				else: assert 0
				return arr.sum()
	               	av[name]['datadetails']         = {'name': 'IntPP_OSU', 'vars':['NPP',], 'convert': osuconvert,'units':'Gt/yr'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]
		if noOSU:	av[name]['datasource']          = ''
		else:		av[name]['datasource'] 		= 'OSU'
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1

	if 'GlobalExportRatio' in analysisKeys:

		def calcExportRatio(nc,keys):
			a = (nc.variables['SDT__100'][:] +nc.variables['FDT__100'][:]).sum()/ (nc.variables['PRD'][:] +nc.variables['PRN'][:] ).sum()
			#a = np.ma.masked_where(a>1.01, a)
			return 	a

		name = 'ExportRatio'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)

		av[name]['dataFile'] 		= ""
		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= maredatCoords
		av[name]['modeldetails'] 	= {'name': name, 'vars':['SDT__100','FDT__100' ,'PRD','PRN',], 'convert': calcExportRatio,'units':''}
		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1

	if  'LocalExportRatio' in analysisKeys:

		def calcExportRatio(nc,keys):
			a = (nc.variables['SDT__100'][:] +nc.variables['FDT__100'][:])/ (nc.variables['PRD'][:] +nc.variables['PRN'][:] )
			a = np.ma.masked_where(a>1.01, a)
			return 	a

		name = 'LocalExportRatio'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)

		av[name]['dataFile'] 		= ""
		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= maredatCoords
		av[name]['modeldetails'] 	= {'name': name, 'vars':['SDT__100','FDT__100' ,'PRD','PRN',], 'convert': calcExportRatio,'units':''}
		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		= ['layerless',]#'100m','200m','Surface - 1000m','Surface - 300m',]#'depthint']
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

	if  'Iron' in analysisKeys:

		name = 'Iron'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)

		av[name]['dataFile'] 		= paths.icFold+"/UKESM_fields_1860_eORCA1_small.nc"
		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= icCoords
		av[name]['modeldetails']	= {'name': name, 'vars':['FER',], 'convert': ukp.mul1000, 'units':'umolFe/m3'}
		av[name]['datadetails']  	= {'name': name, 'vars':['FER',], 'convert': ukp.mul1000, 'units':'umolFe/m3'}
		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= 'InititialCondition'
		av[name]['model']		= 'MEDUSA'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'GlobalMeanTemperature' in analysisKeys:
		name = 'GlobalMeanTemperature'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 	= ''
		#if annual:
		#	av[name]['dataFile'] 		= WOAFolder+'woa13_decav_t00_01v2.nc'
		#else:
		#	av[name]['dataFile'] 		= WOAFolder+'temperature_monthly_1deg.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		nc = dataset(paths.orcaGridfn,'r')
		try:
			pvol   = nc.variables['pvol' ][:]
			gmttmask = nc.variables['tmask'][:]
		except:
			gmttmask = nc.variables['tmask'][:]
			area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
			pvol = nc.variables['e3t'][:] *area
			pvol = np.ma.masked_where(gmttmask==0,pvol)
		nc.close()

		def sumMeanLandMask(nc,keys):
			#### works like no change, but applies a mask.
			temperature = np.ma.masked_where(gmttmask==0,nc.variables[keys[0]][:].squeeze())
			return (temperature*pvol).sum()/(pvol.sum())
		
		
		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['temp3d'],], 'convert': sumMeanLandMask,'units':'degrees C'}
		av[name]['datadetails']  	= {'name': '', 'units':''}
		#av[name]['datadetails']  	= {'name': name, 'vars':['t_an',], 'convert': ukp.NoChange,'units':'degrees C'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1

	if 'GlobalMeanSalinity' in analysisKeys:
		name = 'GlobalMeanSalinity'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 	= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		nc = dataset(paths.orcaGridfn,'r')
		try:
			pvol   = nc.variables['pvol' ][:]
			gmttmask = nc.variables['tmask'][:]
		except:
			gmttmask = nc.variables['tmask'][:]
			area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
			pvol = nc.variables['e3t'][:] *area
			pvol = np.ma.masked_where(gmttmask==0,pvol)
		nc.close()

		def sumMeanLandMask(nc,keys):
			#### works like no change, but applies a mask.
			temperature = np.ma.masked_where(gmttmask==0,nc.variables[keys[0]][:].squeeze())
			return (temperature*pvol).sum()/(pvol.sum())
		
		
		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['sal3d'],], 'convert': sumMeanLandMask,'units':'PSU'}
		av[name]['datadetails']  	= {'name': '', 'units':''}
		#av[name]['datadetails']  	= {'name': name, 'vars':['t_an',], 'convert': ukp.NoChange,'units':'degrees C'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1



	if 'IcelessMeanSST' in analysisKeys:
		name = 'IcelessMeanSST'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 	= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		nc = dataset(paths.orcaGridfn,'r')
		icetmask = nc.variables['tmask'][:]
		area_full = nc.variables['e2t'][:] * nc.variables['e1t'][:]
		nc.close()

		def calcIcelessMeanSST(nc,keys):
			#### works like no change, but applies a mask.
			icecov = nc.variables['soicecov'][:].squeeze()
			sst = np.ma.array(nc.variables[ukesmkeys['temp3d']][:,0,].squeeze())
			sst = np.ma.masked_where((icetmask[0]==0)+(icecov>0.15)+sst.mask,sst)
			area=  np.ma.masked_where(sst.mask,area_full)
			val = (sst*area).sum()/(area.sum())
			print "calcIcelessMeanSST", sst.shape,area.shape, val
			return val


		av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',ukesmkeys['temp3d'],], 'convert': calcIcelessMeanSST,'units':'degrees C'}
		av[name]['datadetails']  	= {'name': '', 'units':''}
		#av[name]['datadetails']  	= {'name': name, 'vars':['t_an',], 'convert': ukp.NoChange,'units':'degrees C'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1


		if 'quickSST' in analysisKeys:
			name = 'quickSST'
			av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)


			nc = dataset(paths.orcaGridfn,'r')
			ssttmask = nc.variables['tmask'][0]
			area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
			area = np.ma.masked_where(ssttmask==0,area)
			nc.close()

			def meanLandMask(nc,keys):
				#### works like no change, but applies a mask.
				#print "meanLandMask:",ssttmask.shape,nc.variables[keys[0]][0,0].shape
				temperature = np.ma.masked_where(ssttmask==0,nc.variables[keys[0]][0,0].squeeze())
				print "meanLandMask:",nc.variables['time_counter'][:],temperature.mean(),(temperature*area).sum()/(area.sum())
				return (temperature*area).sum()/(area.sum())


			if annual:
				#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
				av[name]['dataFile'] 		= ''#WOAFolder+'woa13_decav_t00_01v2.nc'
			else:
				#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1m_*_grid_T.nc"))
				av[name]['dataFile'] 		= ''#WOAFolder+'temperature_monthly_1deg.nc'

			av[name]['modelcoords'] 	= medusaCoords
			av[name]['datacoords'] 		= woaCoords

			av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['temp3d'],], 'convert': meanLandMask,'units':'degrees C'}
			av[name]['datadetails']  	= {'name': '', 'units':''}

			av[name]['layers'] 		= ['layerless',]
			av[name]['regions'] 		= ['regionless',]
			av[name]['metrics']		= ['metricless',]

			av[name]['datasource'] 		= ''
			av[name]['model']		= 'NEMO'

			av[name]['modelgrid']		= 'eORCA1'
			av[name]['gridFile']		= paths.orcaGridfn
			av[name]['Dimensions']		= 1



	if 'T' in analysisKeys:
		name = 'Temperature'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		if annual:
			#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'woa13_decav_t00_01v2.nc'
		else:
			#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1m_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'temperature_monthly_1deg.nc'
		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['temp3d'],], 'convert': applyLandMask,'units':'degrees C'}
		av[name]['datadetails']  	= {'name': name, 'vars':['t_an',], 'convert': ukp.NoChange,'units':'degrees C'}

                tregions =regionList
                #tregions.extend(['NordicSea', 'LabradorSea', 'NorwegianSea'])
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= tregions
		av[name]['metrics']		= metricList
                	
		try:	
			if analysisSuite.lower() in ['debug',]:
		                av[name]['layers']              =  ['Surface',]
        		        av[name]['regions']             =  ['Global',]
		except:pass


		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3

	if 'S' in analysisKeys:
		name = 'Salinity'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		if annual:
			#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'woa13_decav_s00_01v2.nc'
		else:
			#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1m_*_grid_T.nc"))
			av[name]['dataFile'] 		= WOAFolder+'salinity_monthly_1deg.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= woaCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['sal3d'],], 'convert': applyLandMask,'units':'PSU'}
		av[name]['datadetails']  	= {'name': name, 'vars':['s_an',], 'convert': ukp.NoChange,'units':'PSU'}

		salregions =regionList
		#salregions.extend(['NordicSea', 'LabradorSea', 'NorwegianSea'])
		av[name]['layers'] 		=  layerList
		av[name]['regions'] 		= salregions
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'WOA'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 3


	if 'ZonalCurrent' in analysisKeys:
		name = 'ZonalCurrent'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_U', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		= paths.GODASFolder+'ucur.clim.nc'

		av[name]['modelcoords'] 	= medusaUCoords
		av[name]['datacoords'] 		= godasCoords
		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['u3d'],], 'convert': applyLandMask1e3,'units':'mm/s'}
		av[name]['datadetails']  	= {'name': name, 'vars':['ucur',], 'convert': ukp.NoChange,'units':'mm/s'}

		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GODAS'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= './data/eORCA1_gridU_mesh.nc'
		av[name]['Dimensions']		= 3



	if 'MeridionalCurrent' in analysisKeys:
		name = 'MeridionalCurrent'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_V', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		= paths.GODASFolder+'vcur.clim.nc'

		av[name]['modelcoords'] 	= medusaVCoords
		av[name]['datacoords'] 		= godasCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['v3d'],], 'convert': applyLandMask1e3,'units':'mm/s'}
		av[name]['datadetails']  	= {'name': name, 'vars':['vcur',], 'convert': ukp.NoChange,'units':'mm/s'}

		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GODAS'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= './data/eORCA1_gridV_mesh.nc'
		av[name]['Dimensions']		= 3

	if 'VerticalCurrent' in analysisKeys:
		name = 'VerticalCurrent'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_W', paths.ModelFolder_pref, annual)
		if annual:
			av[name]['dataFile'] 		= paths.GODASFolder+'dzdt.clim.nc'



		av[name]['modelcoords'] 	= medusaWCoords
		av[name]['datacoords'] 		= godasCoords

		def applyLandMask1e6(nc,keys):
			return applyLandMask(nc,keys)*1000000.

		av[name]['modeldetails'] 	= {'name': name, 'vars':[ukesmkeys['w3d'],], 'convert': applyLandMask1e6,'units':'um/s'}
		av[name]['datadetails']  	= {'name': name, 'vars':['dzdt',], 'convert': ukp.NoChange,'units':'um/s'}

                vregions =regionList
#                vregions.extend(['NordicSea', 'LabradorSea', 'NorwegianSea'])

		av[name]['layers'] 		= layerList
		av[name]['regions'] 		= vregions
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'GODAS'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= './data/eORCA1_gridW_mesh.nc'
		av[name]['Dimensions']		= 3


	if 'WindStress' in analysisKeys:
		name = 'WindStress'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_U', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 	= ''
		#paths.GODASFolder+'ucur.clim.nc'
			
		def calcwind(nc,keys):
			taux = applySurfaceMask(nc,['sozotaux',])
			
			ncpath = nc.filename
			newpath=ncpath.replace('grid_U', 'grid_V')		

			nc2 = dataset(newpath,'r')
			print "Loaded",newpath
			tauy = applySurfaceMask(nc2,['sometauy',])
						
			return np.ma.sqrt(taux*taux + tauy*tauy)

		av[name]['modelcoords'] 	= medusaUCoords
		av[name]['datacoords'] 		= godasCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['sozotaux','sometauy'], 'convert': calcwind,'units':'N/m2'}
		av[name]['datadetails']  	= {'name': '', 'units':''}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= './data/eORCA1_gridU_mesh.nc'
		av[name]['Dimensions']		= 2

	#####
	# North Atlantic Salinity
        #sowaflup = "Net Upward Water Flux" ;
        #sohefldo = "Net Downward Heat Flux" ;
        #sofmflup = "Water flux due to freezing/melting" ;
        #sosfldow = "Downward salt flux" ;
        	
	naskeys = ['sowaflup','sohefldo','sofmflup','sosfldow','soicecov','sossheig',]
	if len(set(naskeys).intersection(set(analysisKeys))):
	    for name in naskeys:
	    	if name not in analysisKeys:continue

		#nc = dataset(paths.orcaGridfn,'r')
		#area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
		#tmask = nc.variables['tmask'][0,:,:]
		#lat = nc.variables['nav_lat'][:,:]
		#nc.close()

		nas_files = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		nc = dataset(nas_files[0],'r')
		if name not in nc.variables.keys():
			print "analysis_timeseries.py:\tWARNING: ",name ,"is not in the model file."
			continue
		av[name]['modelFiles']  	= nas_files
		av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= medusaCoords		
               
		nasUnits = {	'sowaflup':"kg/m2/s",
				'sohefldo':"W/m2",
				'sofmflup':"kg/m2/s",
				'sosfldow':"PSU/m2/s",
				'soicecov':'',
				'sossheig':'m',
			   }
		
		av[name]['modeldetails'] 	= {'name': name[:], 'vars':[name[:],], 'convert': applySurfaceMask, 'units':nasUnits[name][:]}

		#av[name]['regions'] 		=  ['NordicSea', 'LabradorSea', 'NorwegianSea','Global', ]
                av[name]['regions']             =  ['Global', ]


		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		=  ['layerless',]
		av[name]['metrics']		= metricList
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2
		
	naskeys = ['max_soshfldo',]#'sohefldo','sofmflup','sosfldow','soicecov']
	if len(set(naskeys).intersection(set(analysisKeys))):
	    for name in naskeys:
	    	if name not in analysisKeys:continue

		cutname = name[:].replace('max_','')
		#nc = dataset(paths.orcaGridfn,'r')
		#area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
		#tmask = nc.variables['tmask'][0,:,:]
		#lat = nc.variables['nav_lat'][:,:]
		#nc.close()

		nas_files = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		nc = dataset(nas_files[0],'r')
		if cutname not in nc.variables.keys():
			print "analysis_timeseries.py:\tWARNING: ",cutname ,"is not in the model file."
			continue
		av[name]['modelFiles']  	= nas_files
		av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= medusaCoords		
               
		maxUnits = {	'max_soshfldo':"W/m2",
			   }
		
		def getMax(nc,keys):
			return applySurfaceMask(nc,keys).max()
					
		av[name]['modeldetails'] 	= {'name': name[:], 'vars':[cutname,], 'convert': getMax, 'units':maxUnits[name][:]}

		av[name]['regions'] 		=  ['Global',]# 'LabradorSea', 'NorwegianSea', ]

		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		=  ['layerless',]
		av[name]['metrics']		= ['metricless',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1		
		
		

	if 'MLD' in analysisKeys:

		def mldapplymask(nc,keys):
			mld = np.ma.array(nc.variables[keys[0]][:])
			return np.ma.masked_where((nc.variables[keys[1]][:]==0.)+mld.mask+(mld==1.E9),mld)
                        #eturn np.ma.masked_where((np.tile(nc.variables[keys[1]][:],(12,1,1))==0.)+mld.mask+(mld==1.E9),mld)

		#nc = dataset(paths.orcaGridfn,'r')
		#depth = nc.variables['nav_lev'][:]#
		#nc.close()
		#def calcMLD(nc,keys):
		#	temp = nc.variables[keys[0]][:,:,:,:]
		#	f_out = interp1d(depth[7:9],temp[7:9], axis=1)
		#	tcrit = 0.2
		#	t10m =  f_out(10.)
		#	t10m = np.ma.masked_where(t10m>1E20, t10m) - tcrit
		#	# linear regression to extrapolate below this level to find the first?
		#	f_out = interp1d(temp, depth, axis=1)
		#	#t_out = f_out(newdepth)




		name = 'MLD'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		#av[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_grid_T.nc"))
		av[name]['dataFile'] 		= paths.MLDFolder+"mld_DT02_c1m_reg2.0-annual.nc"	#mld_DT02_c1m_reg2.0.nc"
			#MLD_DT02 = depth where (T = T_10m +/- 0.2 degC)


		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= mldCoords

		av[name]['modeldetails'] 	= {'name': 'mld', 'vars':['somxl010',],   'convert': applySurfaceMask,'units':'m'}
		#av[name]['modeldetails'] 	= {'name': 'mld', 'vars':[ukesmkeys['temp3d'],],   'convert': calcMLD,'units':'m'}
		av[name]['datadetails']  	= {'name': 'mld', 'vars':['mld','mask',], 'convert': mldapplymask,'units':'m'}

		av[name]['layers'] 		= ['layerless',]#'Surface - 1000m','Surface - 300m',]#'depthint']
		mldregions =regionList
		#mldregions.extend(['NordicSea', 'LabradorSea', 'NorwegianSea'])		
		av[name]['regions'] 		= mldregions
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'IFREMER'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

	if 'MaxMonthlyMLD' in analysisKeys:
		
		#/group_workspaces/jasmin2/ukesm/BGC_data/u-ad371/monthlyMLD/MetOffice_data_licence.325210916
		monthlyFiles = glob(paths.ModelFolder_pref+'/'+jobID+'/monthlyMLD/'+jobID+'o_1m_*_grid_T.nc')
		maxmldfiles = mergeMonthlyFiles(monthlyFiles,outfolder='',cal=medusaCoords['cal'])
		
		def mldapplymask(nc,keys):
			mld = np.ma.array(nc.variables[keys[0]][:]).max(0)
			mld = np.ma.masked_where((nc.variables[keys[1]][:]==0.)+mld.mask+(mld==1.E9),mld)
			return mld

		def mldmonthlymask(nc,keys):
			mld = np.ma.array(np.ma.abs(nc.variables[keys[0]][:])).max(0)
			mld = np.ma.masked_where(mld.mask+(mld.data>1.E10),mld)
			return mld
					
                
		name = 'MaxMonthlyMLD'
		av[name]['modelFiles']  	= maxmldfiles #listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 		= paths.MLDFolder+"mld_DT02_c1m_reg2.0.nc"	#mld_DT02_c1m_reg2.0.nc"

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= mldCoords

		av[name]['modeldetails'] 	= {'name': 'mld', 'vars':['somxl010',],   'convert': mldmonthlymask,'units':'m'}
		av[name]['datadetails']  	= {'name': 'mld', 'vars':['mld','mask',], 'convert': mldapplymask,'units':'m'}

		av[name]['layers'] 		= ['layerless',]

		mldregions =regionList
		#mldregions.extend(['NordicSea', 'LabradorSea', 'NorwegianSea'])		
		
		av[name]['regions'] 		= mldregions
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'IFREMER'
		av[name]['model']		= 'NEMO'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2
		
		
		

	icekeys = ['NorthernTotalIceArea','SouthernTotalIceArea','TotalIceArea','NorthernTotalIceExtent','SouthernTotalIceExtent','TotalIceExtent']
	if len(set(icekeys).intersection(set(analysisKeys))):
	    for name in icekeys:
	    	if name not in analysisKeys:continue

		nc = dataset(paths.orcaGridfn,'r')
		area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
		tmask = nc.variables['tmask'][0,:,:]
		lat = nc.variables['nav_lat'][:,:]
		nc.close()

		def calcTotalIceArea(nc,keys):	#Global
			arr = nc.variables[keys[0]][:].squeeze() * area
			return np.ma.masked_where(tmask==0,arr).sum()/1E12

		def calcTotalIceAreaN(nc,keys): # North
			arr = nc.variables[keys[0]][:].squeeze() * area
			return np.ma.masked_where((tmask==0)+(lat<0.),arr).sum()/1E12

		def calcTotalIceAreaS(nc,keys): # South
			arr = nc.variables[keys[0]][:].squeeze() * area
			return np.ma.masked_where((tmask==0)+(lat>0.),arr).sum()/1E12

		def calcTotalIceExtent(nc,keys):	#Global
			return np.ma.masked_where((tmask==0)+(nc.variables[keys[0]][:].squeeze()<0.15),area).sum()/1E12

		def calcTotalIceExtentN(nc,keys): # North
			return np.ma.masked_where((tmask==0)+(nc.variables[keys[0]][:].squeeze()<0.15)+(lat<0.),area).sum()/1E12

		def calcTotalIceExtentS(nc,keys): # South
			return np.ma.masked_where((tmask==0)+(nc.variables[keys[0]][:].squeeze()<0.15)+(lat>0.),area).sum()/1E12

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_T', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= medusaCoords

	    	if name in ['NorthernTotalIceArea',]:
			av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',], 'convert': calcTotalIceAreaN,'units':'1E6 km^2'}
		#	av[name]['regions'] 		=  ['NorthHemisphere',]

	    	if name in ['SouthernTotalIceArea',]:
			av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',], 'convert': calcTotalIceAreaS,'units':'1E6 km^2'}
		#	av[name]['regions'] 		=  ['SouthHemisphere',]

	    	if name in ['TotalIceArea',]:
			av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',], 'convert': calcTotalIceArea,'units':'1E6 km^2'}
		#	av[name]['regions'] 		=  ['Global',]

	    	if name in ['NorthernTotalIceExtent',]:
			av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',], 'convert': calcTotalIceExtentN,'units':'1E6 km^2'}
		#	av[name]['regions'] 		=  ['NorthHemisphere',]

	    	if name in ['SouthernTotalIceExtent',]:
			av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',], 'convert': calcTotalIceExtentS,'units':'1E6 km^2'}
		#	av[name]['regions'] 		=  ['SouthHemisphere',]

	    	if name in ['TotalIceExtent',]:
			av[name]['modeldetails'] 	= {'name': name, 'vars':['soicecov',], 'convert': calcTotalIceExtent,'units':'1E6 km^2'}
		#	av[name]['regions'] 		=  ['Global',]

		av[name]['regions'] 		=  ['regionless',]

		av[name]['datadetails']  	= {'name':'','units':'',}
		#av[name]['layers'] 		=  ['Surface',]
		av[name]['layers'] 		=  ['layerless',]
		av[name]['metrics']		= ['metricless',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'CICE'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1

	if 'DrakePassageTransport' in analysisKeys:
		name = 'DrakePassageTransport'
		####
		# Note that this will only work with the eORCAgrid.

		# coordinates of Drake Passage
		LON=219
		LAT0=79
		LAT1=109

		nc = dataset(paths.orcaGridfn,'r')
		e2u = nc.variables['e2u'][LAT0:LAT1,LON]
		umask = nc.variables['umask'][:,LAT0:LAT1,LON]
		nc.close()

		def drake(nc,keys):
			e3u = nc.variables[ukesmkeys['e3u']][0,:,LAT0:LAT1,LON]
			velo = nc.variables[ukesmkeys['u3d']][0,:,LAT0:LAT1,LON]
			return np.sum(velo*e3u*e2u*umask)*1.e-6

		av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_U', paths.ModelFolder_pref, annual)
		av[name]['dataFile'] 	= ''

		av[name]['modelcoords'] = medusaCoords
		av[name]['datacoords'] 	= medusaCoords

		av[name]['modeldetails']= {'name': name, 'vars':[ukesmkeys['e3u'],ukesmkeys['u3d'],], 'convert': drake,'units':'Sv'}

		av[name]['regions'] 		=  ['regionless',]
		av[name]['datadetails']  	= {'name':'','units':'',}
		av[name]['layers'] 		=  ['layerless',]
		av[name]['metrics']		= ['metricless',]
		av[name]['datasource'] 		= ''
		av[name]['model']		= 'NEMO'
		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1


	if 'AMOC_26N' in analysisKeys or 'AMOC_32S' in analysisKeys or 'ADRC_26N' in analysisKeys or 'AMOC_26N_nomexico' in analysisKeys:
		# Note that this will only work with the eORCAgrid.
		latslice26N = slice(227,228)
                latslice26Nnm = slice(228,229)
		latslice32S = slice(137,138)
		e3v,e1v,tmask,alttmask = {},{},{},{}
	    	for name in ['AMOC_26N','AMOC_32S','ADRC_26N','AMOC_26N_nomexico']:
	    		if name not in analysisKeys:continue

			####
			if name in ['AMOC_26N','ADRC_26N']: 	latslice = latslice26N
			if name == 'AMOC_32S': 	latslice = latslice32S
			if name in ['AMOC_26N_nomexico',]:	latslice = latslice26Nnm
			# Load grid data
			nc = dataset(paths.orcaGridfn,'r')
			e3v[name] = nc.variables['e3v'][:,latslice,:]	# z level height 3D
			e1v[name] = nc.variables['e1v'][latslice,:]	#
			tmask[name] = nc.variables['tmask'][:,latslice,:]
			nc.close()

			# load basin mask
			nc = dataset('data/basinlandmask_eORCA1.nc','r')
			alttmask[name] = nc.variables['tmaskatl'][latslice,:]	# 2D Atlantic mask
                        if name == ['AMOC_26N_nomexico',]:
				alttmask[name][228,180:208]=0.
			nc.close()

		def calc_amoc32S(nc,keys):
			name = 'AMOC_32S'
			zv = np.ma.array(nc.variables[ukesmkeys['v3d']][...,latslice32S,:]) # m/s
			atlmoc = np.array(np.zeros_like(zv[0,:,:,0]))
			e2vshape = e3v[name].shape
			for la in range(e2vshape[1]):		#ji, y
 			  for lo in range(e2vshape[2]):	#jj , x,
 			    if int(alttmask[name][la,lo]) == 0: continue
			    for z in range(e2vshape[0]): 	# jk
 			    	if int(tmask[name][z,la,lo]) == 0: 	   continue
 			    	if np.ma.is_masked(zv[0,z,la,lo]): continue
 			    	atlmoc[z,la] = atlmoc[z,la] - e1v[name][la,lo]*e3v[name][z,la,lo]*zv[0,z,la,lo]/1.E06

 			####
 			# Cumulative sum from the bottom up.
 			for z in range(73,1,-1):
 				atlmoc[z,:] = atlmoc[z+1,:] + atlmoc[z,:]
			return np.ma.max(atlmoc)

		def amoc26N_array(nc,keys,amocname='AMOC_26N'):
			zv = np.ma.array(nc.variables[ukesmkeys['v3d']][...,latslice26N,:]) # m/s
			atlmoc = np.array(np.zeros_like(zv[0,:,:,0]))
			e2vshape = e3v[amocname].shape
			for la in range(e2vshape[1]):		#ji, y
 			  for lo in range(e2vshape[2]):		#jj , x,
 			    if int(alttmask[amocname][la,lo]) == 0: continue
			    for z in range(e2vshape[0]): 	# jk
 			    	if int(tmask[amocname][z,la,lo]) == 0: 	   continue
 			    	if np.ma.is_masked(zv[0,z,la,lo]): continue
 			    	atlmoc[z,la] = atlmoc[z,la] - e1v[amocname][la,lo]*e3v[amocname][z,la,lo]*zv[0,z,la,lo]/1.E06

 			####
 			# Cumulative sum from the bottom up.
 			for z in range(73,1,-1):
 				atlmoc[z,:] = atlmoc[z+1,:] + atlmoc[z,:]
			#return np.ma.max(atlmoc)
			return atlmoc
                def calc_amoc26N(nc,keys):
                        return np.ma.max(amoc26N_array(nc,keys,amocname='AMOC_26N'))

		def calc_amoc26Nnm(nc,keys):
			return np.ma.max(amoc26N_array(nc,keys,amocname='AMOC_26N_nomexico'))
			
		def calc_min_amoc26N(nc,keys):
			return np.ma.min(amoc26N_array(nc,keys,amocname='ADRC_26N'))

			
	    	for name in ['AMOC_26N','AMOC_32S','ADRC_26N','AMOC_26N_nomexico']:
	    		if name not in analysisKeys:continue

			av[name]['modelFiles']  = listModelDataFiles(jobID, 'grid_V', paths.ModelFolder_pref, annual)
			av[name]['dataFile'] 	= ''

			av[name]['modelcoords'] = medusaCoords
			av[name]['datacoords'] 	= medusaCoords

			if name == 'AMOC_26N':	av[name]['modeldetails']= {'name': name, 'vars':[ukesmkeys['v3d'],], 'convert': calc_amoc26N,'units':'Sv'}
                        if name in ['AMOC_26N_nomexico',]:
                                                av[name]['modeldetails']= {'name': name, 'vars':[ukesmkeys['v3d'],], 'convert': calc_amoc26Nnm,'units':'Sv'}
			if name == 'ADRC_26N': 	av[name]['modeldetails']= {'name': name, 'vars':[ukesmkeys['v3d'],], 'convert': calc_min_amoc26N,'units':'Sv'}			
			if name == 'AMOC_32S': 	av[name]['modeldetails']= {'name': name, 'vars':[ukesmkeys['v3d'],], 'convert': calc_amoc32S,'units':'Sv'}

			av[name]['datadetails']  	= {'name':'','units':'',}
			av[name]['layers'] 		=  ['layerless',]
			av[name]['regions'] 		= ['regionless',]
			av[name]['metrics']		= ['metricless',]
			av[name]['datasource'] 		= ''
			av[name]['model']		= 'NEMO'
			av[name]['modelgrid']		= 'eORCA1'
			av[name]['gridFile']		= paths.orcaGridfn
			av[name]['Dimensions']		= 1



	if 'DMS_ARAN' in analysisKeys:
		name = 'DMS'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)[:]
		if annual:
			av[name]['dataFile'] 		= paths.DMSDir+'DMSclim_mean.nc'
		else:
			av[name]['dataFile'] 		= ''

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= dmsCoords

		av[name]['modeldetails'] 	= {'name': name, 'vars':['DMS_ARAN',], 'convert': ukp.NoChange,'units':'nmol/L'}
		av[name]['datadetails']  	= {'name': name, 'vars':['DMS',], 'convert': ukp.NoChange,'units':'umol/m3'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'Lana'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

        if 'DMS_ANDR' in analysisKeys:
                name = 'DMS'
                av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)[:]
                if annual:
                        av[name]['dataFile']            = paths.DMSDir+'DMSclim_mean.nc'
                else:
                        av[name]['dataFile']            = ''

                av[name]['modelcoords']         = medusaCoords
                av[name]['datacoords']          = dmsCoords

                av[name]['modeldetails']        = {'name': name, 'vars':['DMS_ANDR',], 'convert': ukp.NoChange,'units':'nmol/L'}
                av[name]['datadetails']         = {'name': name, 'vars':['DMS',], 'convert': ukp.NoChange,'units':'umol/m3'}

                av[name]['layers']              = ['layerless',]
                av[name]['regions']             = regionList
                av[name]['metrics']             = metricList

                av[name]['datasource']          = 'Lana'
                av[name]['model']               = 'MEDUSA'

                av[name]['modelgrid']           = 'eORCA1'
                av[name]['gridFile']            = paths.orcaGridfn
                av[name]['Dimensions']          = 2



	if 'Dust' in analysisKeys:
		name = 'Dust'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)[:]
		av[name]['dataFile'] 		= paths.Dustdir+'mahowald.orca100_annual.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= medusaCoords
		av[name]['modeldetails'] 	= {'name': name, 'vars':['AEOLIAN',], 'convert': ukp.NoChange,'units':'mmol Fe/m2/d'}

                def mahodatadust(nc,keys):
                        #factors are:
                        # 0.035: iron as a fraction of total dust
                        # 1e6: convert from kmol -> mmol
                        # 0.00532: solubility factor or iron
                        # 55.845: atmoic mass of iron (g>mol conversion)
                        # (24.*60.*60.): per second to per day
                        dust = nc.variables[keys[0]][:]
                        dust[0,0,194:256,295:348] = 0.
                        dust[0,0,194:208,285:295] = 0.
                        dust[0,0,188:216,290:304] = 0.
                        return dust *0.035 * 1.e6 *0.00532*(24.*60.*60.) / 55.845

		av[name]['datadetails']  	= {'name': name, 'vars':['dust_ann',], 'convert': mahodatadust ,'units':'mmol Fe/m2/d'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= regionList
		av[name]['metrics']		= metricList

		av[name]['datasource'] 		= 'Mahowald'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 2

	if 'TotalDust' in analysisKeys:
		name = 'TotalDust'
		av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)[:]
		av[name]['dataFile'] 	= paths.Dustdir+'mahowald.orca100_annual.nc'

		av[name]['modelcoords'] 	= medusaCoords
		av[name]['datacoords'] 		= medusaCoords

		nc = dataset(paths.orcaGridfn,'r')
		masked_area = nc.variables['e2t'][:] * nc.variables['e1t'][:]*nc.variables['tmask'][0]
		nc.close()

		def datadustsum(nc,keys):
			#factors are:
			# 0.035: iron as a fraction of total dust
			# 1e6: convert from kmol -> mmol
			# 1e-12: convert from mol to Gmol
			# 0.00532: solubility factor for iron
			# 55.845: atmoic mass of iron (g>mol conversion)
			# (24.*60.*60.*365.25): per second to per year

			dust = nc.variables[keys[0]][:]
			dust[:,:,234:296,295:348] = 0.
 			dust[:,:,234:248,285:295] = 0.
  			dust[:,:,228:256,290:304] = 0.
			return (masked_area*dust).sum() *0.035 * 1.e6*1.e-12 *0.00532*(24.*60.*60. *365.25)/  55.845

		def modeldustsum(nc,keys):
                        dust = nc.variables[keys[0]][:]
                        dust[:,234:296,295:348] = 0.
                        dust[:,234:248,285:295] = 0.
                        dust[:,228:256,290:304] = 0.
			return (masked_area*dust).sum() *1.E-12 *365.25

		av[name]['modeldetails'] 	= {'name': name, 'vars':['AEOLIAN',], 'convert': modeldustsum,'units':'Gmol Fe/yr'}
		av[name]['datadetails']  	= {'name': name, 'vars':['dust_ann',], 'convert': datadustsum,'units':'Gmol Fe/yr'}

		av[name]['layers'] 		= ['layerless',]
		av[name]['regions'] 		= ['regionless',]
		av[name]['metrics']		= ['metricless',]

		av[name]['datasource'] 		= 'Mahowald'
		av[name]['model']		= 'MEDUSA'

		av[name]['modelgrid']		= 'eORCA1'
		av[name]['gridFile']		= paths.orcaGridfn
		av[name]['Dimensions']		= 1

        if 'TotalDust_nomask' in analysisKeys:
                name = 'TotalDust_nomask'
                av[name]['modelFiles']  = listModelDataFiles(jobID, 'diad_T', paths.ModelFolder_pref, annual)[:]
                av[name]['dataFile']    = paths.Dustdir+'mahowald.orca100_annual.nc'

                av[name]['modelcoords']         = medusaCoords
                av[name]['datacoords']          = medusaCoords

                nc = dataset(paths.orcaGridfn,'r')
                masked_area = nc.variables['e2t'][:] * nc.variables['e1t'][:]*nc.variables['tmask'][0]
                nc.close()

                def datadustsum(nc,keys):
                        #factors are:
                        # 0.035: iron as a fraction of total dust
                        # 1e6: convert from kmol -> mmol
                        # 1e-12: convert from mol to Gmol
                        # 0.00532: solubility factor for iron
                        # 55.845: atmoic mass of iron (g>mol conversion)
                        # (24.*60.*60.*365.25): per second to per year

                        dust = nc.variables[keys[0]][:]
                        #dust[194:256,295:348] = 0.
                        #dust[194:208,285:295] = 0.
                        #dust[188:216,290:304] = 0.
                        return (masked_area*dust).sum() *0.035 * 1.e6*1.e-12 *0.00532*(24.*60.*60. *365.25)/  55.845

                def modeldustsum(nc,keys):
                        dust = nc.variables[keys[0]][:]
                        #dust[:,194:256,295:348] = 0.
                        #dust[:,194:208,285:295] = 0.
                        #dust[:,188:216,290:304] = 0.
                        return (masked_area*dust).sum() *1.E-12 *365.25

                av[name]['modeldetails']        = {'name': name, 'vars':['AEOLIAN',], 'convert': modeldustsum,'units':'Gmol Fe/yr'}
                av[name]['datadetails']         = {'name': name, 'vars':['dust_ann',], 'convert': datadustsum,'units':'Gmol Fe/yr'}

                av[name]['layers']              = ['layerless',]
                av[name]['regions']             = ['regionless',]
                av[name]['metrics']             = ['metricless',]

                av[name]['datasource']          = 'Mahowald'
                av[name]['model']               = 'MEDUSA'

                av[name]['modelgrid']           = 'eORCA1'
                av[name]['gridFile']            = paths.orcaGridfn
                av[name]['Dimensions']          = 1


  	#####
  	# Calling timeseriesAnalysis
	# This is where the above settings is passed to timeseriesAnalysis, for the actual work to begin.
	# We loop over all fiels in the first layer dictionary in the autovificiation, av.
	#
	# Once the timeseriesAnalysis has completed, we save all the output shelves in a dictionairy.
	# At the moment, this dictioary is not used, but we could for instance open the shelve to highlight specific data,
	#	(ie, andy asked to produce a table showing the final year of data.

	shelves = {}
	shelves_insitu={}
	for name in av.keys():
		print "------------------------------------------------------------------"
		print "analysis-Timeseries.py:\tBeginning to call timeseriesAnalysis for ", name

		if len(av[name]['modelFiles']) == 0:
			print "analysis-Timeseries.py:\tWARNING:\tmodel files are not found:",name,av[name]['modelFiles']
			if strictFileCheck: assert 0

		modelfilesexists = [os.path.exists(f) for f in av[name]['modelFiles']]
		if False in modelfilesexists:
			print "analysis-Timeseries.py:\tWARNING:\tnot model files do not all exist:",av[name]['modelFiles']
			for f in av[name]['modelFiles']:
				if os.path.exists(f):continue
				print f, 'does not exist'
			if strictFileCheck: assert 0


		if av[name]['dataFile']!='':
		   if not os.path.exists(av[name]['dataFile']):
			print "analysis-Timeseries.py:\tWARNING:\tdata file is not found:",av[name]['dataFile']
			if strictFileCheck: assert 0

#		profa = profileAnalysis(
#			av[name]['modelFiles'],
#			av[name]['dataFile'],
#			dataType	= name,
 # 			modelcoords 	= av[name]['modelcoords'],
  #			modeldetails 	= av[name]['modeldetails'],
  #			datacoords 	= av[name]['datacoords'],
  #			datadetails 	= av[name]['datadetails'],
#			datasource	= av[name]['datasource'],
#			model 		= av[name]['model'],
#			jobID		= jobID,
#			layers	 	= list(np.arange(102)),	# 102 because that is the number of layers in WOA Oxygen
#			regions	 	= av[name]['regions'],
#			metrics	 	= ['mean',],
#			workingDir	= shelvedir,
#			imageDir	= imagedir,
#			grid		= av[name]['modelgrid'],
#			gridFile	= av[name]['gridFile'],
#			clean 		= clean,
#		)
			#shelves[name] = profa.shelvefn
			#shelves_insitu[name] = profa.shelvefn_insitu

                #####
                # time series and traffic lights.
                tsa = timeseriesAnalysis(
                        av[name]['modelFiles'],
                        av[name]['dataFile'],
                        dataType        = name,
                        modelcoords     = av[name]['modelcoords'],
                        modeldetails    = av[name]['modeldetails'],
                        datacoords      = av[name]['datacoords'],
                        datadetails     = av[name]['datadetails'],
                        datasource      = av[name]['datasource'],
                        model           = av[name]['model'],
                        jobID           = jobID,
                        layers          = av[name]['layers'],
                        regions         = av[name]['regions'],
                        metrics         = av[name]['metrics'],
                        workingDir      = shelvedir,
                        imageDir        = imagedir,
                        grid            = av[name]['modelgrid'],
                        gridFile        = av[name]['gridFile'],
                        clean           = clean,
                )

		#####
		# Profile plots
		if av[name]['Dimensions'] == 3 and name not in ['Iron','Fe']:
			continue
			profa = profileAnalysis(
				av[name]['modelFiles'],
				av[name]['dataFile'],
				dataType	= name,
	  			modelcoords 	= av[name]['modelcoords'],
	  			modeldetails 	= av[name]['modeldetails'],
	  			datacoords 	= av[name]['datacoords'],
	  			datadetails 	= av[name]['datadetails'],
				datasource	= av[name]['datasource'],
				model 		= av[name]['model'],
				jobID		= jobID,
				layers	 	= list(np.arange(102)),		# 102 because that is the number of layers in WOA Oxygen
				regions	 	= av[name]['regions'],
				metrics	 	= ['mean',],
				workingDir	= shelvedir,
				imageDir	= imagedir,
				grid		= av[name]['modelgrid'],
				gridFile	= av[name]['gridFile'],
				clean 		= False,
			)
			#shelves[name] = profa.shelvefn
			#shelves_insitu[name] = profa.shelvefn_insitu

		#shelves[name] = tsa.shelvefn
		#shelves_insitu[name] = tsa.shelvefn_insitu




def singleTimeSeriesProfile(jobID,key):

	FullDepths = ['T','S', 'Chl_pig','N','Si','O2','Alk','DIC','Iron',]
	if key in FullDepths:
		analysis_timeseries(jobID =jobID,analysisSuite=[key,], )

def singleTimeSeries(jobID,key,):
#	try:
		analysis_timeseries(jobID =jobID,analysisSuite=[key,], strictFileCheck=False)#clean=1)
#	except:
#		print "Failed singleTimeSeries",(jobID,key)
#		print "Error: %s" % sys.exc_info()[0]



def main():
	try:	jobID = argv[1]
	except:
		jobID = "u-ab749"

	if 'debug' in argv[1:]:	suite = 'debug'
	#elif 'all' in argv[1:]:	suite = 'all'
	elif 'level1' in argv[1:]:suite='level1'
	elif 'level3' in argv[1:]:suite='level3'
        elif 'physics' in argv[1:]:suite='physics'
        elif 'bgc' in argv[1:]:	suite='bgc'       
	elif 'kmf' in argv[1:] or 'keymetricsfirst' in argv[1:]:
		suite='keymetricsfirst' 
	else:	suite = 'level1'


	analysis_timeseries(jobID =jobID,analysisSuite=suite, )#clean=1)
	#if suite == 'all':
	#analysis_timeseries(jobID =jobID,analysisSuite='FullDepth', z_component = 'FullDepth',)#clean=1)

if __name__=="__main__":
	main()
