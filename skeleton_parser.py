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
.. module:: skeleton_parser
   :platform: Unix
   :synopsis: A nearly empty script to produce analysis.

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

from p2p.testsuite_p2p import testsuite_p2p_noAV as testsuite_p2p

from bgcvaltools.dataset import dataset
from bgcvaltools.configparser import AnalysisKeyParser, linkActiveKeys, parseFilepath





def analysis_skeleton(
#			pathsfn = 'paths.ini',	
			configfile = 'runconfig.ini',
			#model = 'MEDUSA',
			#clean = False,
			#strictFileCheck = True,
			):
	#paths = FullyParseConfig(configfile,debug=True)['paths']
	
	#####
	# Location of images directory
	# the imagedir is where the analysis images will be saved.

	#imagedir = parseFilepath(configfile, 'Global', 'imagedir')
	#image2 = parseFilepath(configfile, 'Defaults', 'imagedir')
	#image3 = parseFilepath(configfile, 'Chl_CCI', 'imagedir')	
	#imagedir_ts 	= ukp.folder(imagedir +'/'+jobID+'/timeseries')
	#print imagedir , type(imagedir)	
	#print image2 , type(image2)	
	#print image3 , type(image3)			
	#assert 0
	
	#imagedir_p2p	= ukp.folder(paths['imagedir']'/'+jobID+'/p2p/')
	
	#####
	# Location of shelves folder
	# The shelve directory is where the intermediate processing files are saved in python's shelve format.
	# This allows us to put away a python open to be re-opened later.
	# This means that we can interupt the analysis without loosing lots of data and processing time,
	# or we can append new simulation years to the end of the analysis without starting from scratch each time.
	#workingdir_ts 	= ukp.folder(parseFilepath(configfile, 'Global', 'shelvedir') +'/'+jobID+'/timeseries')
#	workingdir_ts 	= ukp.folder(paths.shelvedir+"/timeseries/"+jobID)
	
	#workingdir_p2p	= ukp.folder(paths.p2p_ppDir+'/'+model+'-'+jobID+'-'+year)

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
  	#		av_ts[name]['dataFile']  = ''



                        
	#av_ts = ukp.AutoVivification()
	#av_p2p = ukp.AutoVivification()	

	"""	
	if 'Chl_CCI' in timeseriesKeys:
		name = 'Chlorophyll_cci'
		#####
		# Not that this is the 1 degree resolution dataset, but higher resolution data are also av_tsailable.
		#av_ts[name]['modelFiles']  = listModelDataFiles(jobID, 'ptrc_T', paths.ModelFolder_pref, annual)
		av_ts[name]['modelFiles']  	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1y_*_ptrc_T.nc"))
		av_ts[name]['dataFile'] 	= paths.CCIDir+"ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-annual-fv2.0.nc"

		av_ts[name]['modelcoords'] 	= {'t':'time_counter', 'z':'deptht', 'lat': 'nav_ts_lat',  'lon': 'nav_lon',   'cal': '360_day',}
		av_ts[name]['datacoords'] 	= {'t':'index_t', 'z':'index_z','lat': 'lat',      'lon': 'lon', 'cal': 'standard','tdict':['ZeroToZero'] }

		av_ts[name]['modeldetails'] 	= {'name': name, 'vars':['CHL',], 'convert': ukp.NoChange,'units':'mg C/m^3'}
		av_ts[name]['datadetails']  	= {'name': name, 'vars':['chlor_a',], 'convert':  ukp.NoChange,'units':'mg C/m^3'}

		av_ts[name]['layers'] 		= ['Surface',] 	# CCI is surface only, it's a satellite product.
		av_ts[name]['regions'] 		= ['Global', 'ignoreInlandSeas', 'SouthernOcean','ArcticOcean','Equator10', 'Remainder','NorthernSubpolarAtlantic','NorthernSubpolarPacific',]
		#av_ts[name]['metrics']		= metricList	#['mean','median', ]

		av_ts[name]['datasource'] 	= 'CCI'
		av_ts[name]['model']		= 'MEDUSA'

		av_ts[name]['modelgrid']	= 'eORCA1'
		av_ts[name]['gridFile']		= paths.orcaGridfn
		av_ts[name]['Dimensions']	= 2


	if 'Chl_CCI' in p2pKeys:						
		name = 'Chlorophyll_cci'
		av_p2p[name]['Data']['File'] 	= paths.CCIDir+"ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-annual-fv2.0.nc"	
		av_p2p[name]['MEDUSA']['File'] 	= sorted(glob(paths.ModelFolder_pref+jobID+"/"+jobID+"o_1m_*"+year+"????_ptrc_T.nc"))[-1]
		
		av_p2p[name]['MEDUSA']['grid']	= 'eORCA1'		
		av_p2p[name]['depthLevels'] 	= ['',]
		av_p2p[name]['plottingSlices'] 	= ['Global', 'ignoreInlandSeas', 'SouthernOcean','ArcticOcean','Equator10', 'Remainder','NorthernSubpolarAtlantic','NorthernSubpolarPacific',]
		
		av_p2p[name]['Data']['coords'] 	= {'t':'index_t', 'z':'index_z','lat': 'lat',      'lon': 'lon', 'cal': 'standard','tdict':['ZeroToZero'] }
		av_p2p[name]['MEDUSA']['coords']= {'t':'time_counter', 'z':'deptht', 'lat': 'nav_ts_lat',  'lon': 'nav_lon',   'cal': '360_day',}
		
		av_p2p[name]['Data']['source'] 	= 'CCI'
		av_p2p[name]['MEDUSA']['source']= 'MEDUSA'			

		av_p2p[name]['MEDUSA']['details']=  {'name': name, 'vars':['CHL',], 'convert': ukp.NoChange,'units':'mg C/m^3'}
		av_p2p[name]['Data']['details']	= {'name': name, 'vars':['chlor_a',], 'convert':  ukp.NoChange,'units':'mg C/m^3'}	

	"""

  	#####
  	# Calling timeseriesAnalysis
	# This is where the above settings is passed to timeseriesAnalysis, for the actual work to begin.
	# We loop over all fiels in the first layer dictionary in the autovificiation, av.
	#
	# Once the timeseriesAnalysis has completed, we save all the output shelves in a dictionairy.
	# At the moment, this dictioary is not used, but we could for instance open the shelve to highlight specific data,
	#	(ie, andy asked to produce a table showing the final year of data.
	analysiskeys =  linkActiveKeys(configfile)
	print analysiskeys
	
	for k, key in analysiskeys.items():
		akp = AnalysisKeyParser(configfile, key, debug=True)
	

	
		
	
		
		if akp.dimensions in  [2, 3]:
			metricList = ['mean','median', '10pc','20pc','30pc','40pc','50pc','60pc','70pc','80pc','90pc','min','max']
		else:	metricList = ['metricless',]	
		
                tsa = timeseriesAnalysis(
                        akp.modelFiles,
                        akp.dataFile,
                        jobID           = akp.jobID,
                        dataType        = akp.name,
                        workingDir      = akp.postproc_ts,
                        imageDir        = akp.images_ts,
                        metrics         = metricList,
                        modelcoords     = akp.modelcoords,
                        modeldetails    = akp.modeldetails,
                        datacoords      = akp.datacoords,
                        datadetails     = akp.datadetails,
                        datasource      = akp.datasource,
                        model           = akp.model,
                        layers          = akp.layers,
                        regions         = akp.regions,
                        grid            = akp.modelgrid,
                        gridFile        = akp.gridFile,
                        clean           = True,
                )
               # assert 0

		#####
		# Profile plots
		if akp.dimensions == 3:
			profa = profileAnalysis(
				akp.modelFiles,
				akp.dataFile,
				jobID           = akp.jobID,
				dataType        = akp.name,
				workingDir      = shelvedir,
				imageDir        = imagedir_ts,
				modelcoords     = akp.modelcoords,
				modeldetails    = akp.modeldetails,
				datacoords      = akp.datacoords,
				datadetails     = akp.datadetails,
				datasource      = akp.datasource,
				model           = akp.model,
				regions         = akp.regions,
				grid            = akp.modelgrid,
				gridFile        = akp.gridFile,
				layers	 	= list(np.arange(102)),		# 102 because that is the number of layers in WOA Oxygen
				metrics	 	= ['mean',],								
				clean 		= False,
			)

	    	testsuite_p2p(
                        modelFile	= akp.modelFile_p2p,
                        dataFile 	= akp.dataFile,    		
			model 		= akp.model,
			jobID 		= akp.jobID,
			year  		= akp.year,
			modelcoords     = akp.modelcoords,
                        modeldetails    = akp.modeldetails,
                        datacoords      = akp.datacoords,
                        datadetails     = akp.datadetails,
                        datasource      = akp.datasource,
			plottingSlices	= akp.regions,		# set this so that testsuite_p2p reads the slice list from the av.
			workingDir 	= akp.postproc_p2p, 
			imageFolder	= akp.images_p2p,
                        grid            = akp.modelgrid,			
			gridFile	= akp.gridFile,	# enforces custom gridfile.
			noPlots		= False,	# turns off plot making to save space and compute time.
			annual		= True,
			noTargets	= True,
	 	)	



def main():
	analysis_skeleton()
	#jobID='u-ad371')
	assert 0
	
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

	analysis_timeseries(jobID =jobID,analysisSuite=suite, )
	
if __name__=="__main__":
	main()
