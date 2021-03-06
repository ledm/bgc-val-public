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
.. module:: analysis_parser
   :platform: Unix
   :synopsis: A simple script that parses the config file and runs  the analysis.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

#####
# Load Standard Python modules:
from sys import argv,exit
import numpy as np
import os,sys
from itertools import product

#####
# Load specific local code:
from bgcvaltools import bgcvalpython as bvp
from timeseries import timeseriesAnalysis
from timeseries import profileAnalysis
from timeseries import timeseriesTools as tst
from timeseries import comparisonAnalysis, makeCSV
from p2p.testsuite_p2p import testsuite_p2p

from bgcvaltools.dataset import dataset
from bgcvaltools.configparser import AnalysisKeyParser, GlobalSectionParser

from html.makeReportConfig import htmlMakerFromConfig

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')


parrallel = False
if parrallel:
	try:	from multiprocessing import Pool
	except: parrallel = False


def evaluateFromConfig( akp,
			model	= '',
			jobID	= '',
			year	= '',
			scenario= '',
			key	= ''):

	if akp.dimensions in  [1,]:			
		metricList = ['metricless',]
	if akp.dimensions in  [2, 3]:
		metricList = ['mean','median', '10pc','20pc','30pc','40pc','50pc','60pc','70pc','80pc','90pc','min','max']
	#####
	# Time series plots		
	if akp.makeTS: 
	        tsa = timeseriesAnalysis(
	                modelFiles	= akp.modelFiles_ts,
	                dataFile 	= akp.dataFile,
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
			scenario        = akp.scenario,						                
			timerange       = akp.timerange,
	                layers          = akp.layers,
	                regions         = akp.regions,
	                grid            = akp.modelgrid,
	                gridFile        = akp.gridFile,
	                clean           = akp.clean,
	        )


    	
	#####
	# Profile plots (only works for 3 Dimensional data.)
	if akp.makeProfiles and akp.dimensions == 3:
		profa = profileAnalysis(
			modelFiles 	= akp.modelFiles_ts,
			dataFile	= akp.dataFile,
			jobID           = akp.jobID,
			dataType        = akp.name,
			workingDir      = akp.postproc_pro,
			imageDir        = akp.images_pro,
			modelcoords     = akp.modelcoords,
			modeldetails    = akp.modeldetails,
			datacoords      = akp.datacoords,
			datadetails     = akp.datadetails,
			datasource      = akp.datasource,
			model           = akp.model,
			scenario        = akp.scenario,	
			timerange       = akp.timerange,						
			regions         = akp.regions,
			grid            = akp.modelgrid,
			gridFile        = akp.gridFile,
			layers	 	= list(np.arange(102)),		# 102 because that is the number of layers in WOA Oxygen
			metrics	 	= ['mean',],								
			clean 		= akp.clean,
		)
		
	#####
	# Point to point plots
	print 'p2p:',akp.modelFile_p2p
	print 'ts :',akp.modelFiles_ts	
	if akp.makeP2P and  akp.dimensions not in [1,]:
	    	testsuite_p2p(
	                modelFile	= akp.modelFile_p2p,
	                dataFile 	= akp.dataFile,    		
			model 		= akp.model,
			scenario        = akp.scenario,								
			jobID 		= akp.jobID,
	    		dataType        = akp.name,						
			year  		= akp.year,
			modelcoords     = akp.modelcoords,
	                modeldetails    = akp.modeldetails,
	                datacoords      = akp.datacoords,
	                datadetails     = akp.datadetails,
	                datasource      = akp.datasource,
			plottingSlices	= akp.regions,		# set this so that testsuite_p2p reads the slice list from the av.
			layers		= akp.layers,
			workingDir 	= akp.postproc_p2p, 
			imageFolder	= akp.images_p2p,
	                grid            = akp.modelgrid,			
			gridFile	= akp.gridFile,	# enforces custom gridfile.
			noPlots		= False,	# turns off plot making to save space and compute time.
			annual		= True,
			noTargets	= True,
	                clean           = akp.clean,				
	 	)
		 	
jobsDict = {}
def parrallelEval(index):
	"""
	Parralllelise the evaluation of a specific job.
	"""
	[(model,jobID,year,scenario,key),akp] = jobsDict[index]
	print "parrallelEval:",model,jobID,year,scenario,key
	evaluateFromConfig( akp,
		model	= model,
		jobID	= jobID,
		year	= year,
		scenario= scenario,
		key	= key)	
				
def analysis_parser(
			configfile = 'runconfig.ini',
			):
	
	#####
	# Load global level keys from the config file.
	gk =  GlobalSectionParser(configfile)
	#print gk
	#assert 0

	#####
	# Run the evaluation for each True boolean key in the config file section [ActiveKeys].	
	if parrallel:
		global jobsDict
		
		i = 0
		for (model,jobID,year,scenario,key),akp in gk.AnalysisKeyParser.items():
			jobsDict[i] = [(model,jobID,year,scenario,key),akp]
			i+=1
		
		nproc = 6
		pool = Pool(processes=nproc)              	# start nproc worker processes
		pool.map(parrallelEval, sorted(jobsDict.keys()))# Map processes onto jobDict 
		pool.close()					# end
	else:
		for (model,jobID,year,scenario,key),akp in gk.AnalysisKeyParser.items():
			evaluateFromConfig( akp,
				model	= model,
				jobID	= jobID,
				year	= year,
				scenario= scenario,
				key	= key)
		
	#####
	# Comparison Plots.
	if gk.makeComp:	
	    	comparisonAnalysis(configfile)

	#####
	# Make CSV's	    	
	if gk.makeCSV:
	    	makeCSV(configfile)			 	

	#####
	# Make HTML Report
	if gk.makeReport:
		htmlMakerFromConfig(configfile)
	else:
		print "analysis_parser:\tReport maker  is switched Off. To turn it on, use the makeReport boolean flag in "

def main():
        try: 	configfn = argv[1]
	except:
		configfn = 'runconfig.ini'
		print "run.py:\tNo config file provided, using default: ", configfn

	analysis_parser(
		configfile= configfn,
		)
		
	
if __name__=="__main__":
	main()
