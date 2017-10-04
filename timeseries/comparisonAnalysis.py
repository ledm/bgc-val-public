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
.. module:: analysis_compare
   :platform: Unix
   :synopsis: A script to produce an intercomparison of multiple runs the time series analyses.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

#####	
# Load Standard Python modules:
from shelve import open as shopen
from itertools import product
import os

#####	
# Load specific local code:
from bgcvaltools import bgcvalpython as bvp
from longnames.longnames import getLongName
from timeseries import timeseriesPlots as tsp 
from bgcvaltools.configparser import GlobalSectionParser


#colourList = ['green','blue','red','orange','purple','black',]


def guessLeadMetric(
		globalkeys,
		):
	if len(globalkeys.models)>1: 	return 'model'
	if len(globalkeys.jobIDs)>1: 	return 'jobID'	
	if len(globalkeys.scenarios)>1: return 'scenario'
	#default:
	return 'jobID'		
	
	
def comparisonAnalysis(configfile):

	#####
	# open config file.	
	globalkeys =  GlobalSectionParser(configfile)	
	
	#####
	# This looping forces the report to match the order.
	ActiveKeys 	= globalkeys.ActiveKeys
	models 		= globalkeys.models
	scenarios 	= globalkeys.scenarios
	jobIDs	 	= globalkeys.jobIDs

	
	#####
	times 	= {}
	data 	= {}
	regions = {}
	layers 	= {}	

	leadmetric = guessLeadMetric(globalkeys)


	#####
	# Load model data	
	for key in ActiveKeys: 
	 for model in models:	
  	  for scenario in scenarios:
 	    for jobID in jobIDs:	
		akp = globalkeys.AnalysisKeyParser[(model,jobID,globalkeys.years[0],scenario,key)]
		
 	    	if not akp.makeTS: continue 
	  	shelvefn 		= bvp.folder(akp.postproc_ts)+'_'.join([akp.jobID,akp.name,])+'.shelve'

		regions.update({r:True for r in akp.regions})
		layers.update({r:True for r in akp.layers})
		print "comparisonAnalysis:\topening: ",shelvefn
		sh = shopen(shelvefn)
		print sh.keys()
		try:
			modeldataD = sh['modeldata']
			sh.close()			
		except:	
			sh.close()
			continue
		data[(key,model,scenario, jobID)] = modeldataD
		print "Loaded", (key,model,scenario, jobID)		

		#shelvefn_insitu	= bvp.folder(akp.postproc_ts)+'_'.join([akp.jobID,akp.name,])+'_insitu.shelve'		
		#sh = shopen(shelvefn)
		#modeldataD = sh['modeldataD']
		#sh.close()

	regions = regions.keys()
	layers = layers.keys()
	metrics	= ['mean' , 'metricless','median',]
	linestyles = ['DataOnly','movingav1year','movingav5years',]
	
	colourList = tsp.cmipcolours
	#####
	# Make the plots, comparing differnet jobIDs
	if leadmetric=='jobID' and len(jobIDs)>1:
		colours		= {j:c for j,c in zip(jobIDs,colourList)}			
   	    	for (key, model, scenario,region,layer,metric) in product(ActiveKeys, models, scenarios,regions, layers,metrics):
			timesD = {}
			arrD   = {}
	
			units = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].units
			datarange = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datarange
			for jobID in jobIDs:
			
				try:	mdata = data[(key,model,scenario, jobID)][(region,layer,metric)]
				except:	continue

				timesD[jobID] 	= sorted(mdata.keys())
				arrD[jobID]	= [mdata[t] for t in timesD[jobID]]
		
			if not len(arrD.keys()):continue	
		
			for linestyle in linestyles:
				title = ' '.join([getLongName(i) for i in [model, scenario, region, layer, metric, key]])	
				filename =  bvp.folder(globalkeys.images_comp)+'_'.join([model, scenario, region, layer, metric, key,linestyle])+'.png'
		
				tsp.multitimeseries(
					timesD, 		# model times (in floats)
					arrD,			# model time series
					data 		= datarange,		# in situ data distribution
					title 		= title,
					filename	= filename,
					units 		= units,
					plotStyle 	= 'Together',
					lineStyle	= linestyle,
					colours		= colours,
				)
			
	#####
	# Make the plots, comparing differnet models
	if leadmetric=='model' and len(models)>1:	
		colours		= {j:c for j,c in zip(models,colourList)}				
   	    	for (key, jobID, scenario,region,layer,metric) in product(ActiveKeys, jobIDs, scenarios,regions, layers,metrics):
			timesD = {}
			arrD   = {}
	
			units = globalkeys.AnalysisKeyParser[(models[0],jobID,globalkeys.years[0],scenario,key)].units
			datarange = globalkeys.AnalysisKeyParser[(models[0],jobID,globalkeys.years[0],scenario,key)].datarange		
			for model in models:
			
				try:	mdata = data[(key,model,scenario, jobID)][(region,layer,metric)]
				except:	continue

				timesD[model] 	= sorted(mdata.keys())
				arrD[model]	= [mdata[t] for t in timesD[model]]
		
			if not len(arrD.keys()):continue	
		
			for linestyle in linestyles:		
				title = ' '.join([getLongName(i) for i in [scenario,jobID, region, layer, metric, key]])	
				filename =  bvp.folder(globalkeys.images_comp)+'_'.join([ scenario, jobID, region, layer, metric, key,linestyle])+'.png'
		
				tsp.multitimeseries(
					timesD, 		# model times (in floats)
					arrD,			# model time series
					data 		= datarange,		# in situ data distribution
					title 		= title,
					filename	= filename,
					units 		= units,
					plotStyle 	= 'Together',
					lineStyle	= linestyle,
					colours		= colours,
				)			

	#####
	# Make the plots, comparing differnet scenarios
	if leadmetric=='scenario' and len(scenarios)>1:	
		colours		= {j:c for j,c in zip(scenarios,colourList)}					
   	    	for (key, model, jobID,region,layer,metric) in product(ActiveKeys, models, jobIDs,regions, layers,metrics):
			timesD = {}
			arrD   = {}
	
			units = globalkeys.AnalysisKeyParser[(model,jobID,globalkeys.years[0],scenarios[0],key)].units
			datarange = globalkeys.AnalysisKeyParser[(model,jobID,globalkeys.years[0],scenarios[0],key)].datarange				
			for scenario in scenarios:
			
				try:	mdata = data[(key,model,scenario, jobID)][(region,layer,metric)]
				except:	continue

				timesD[scenario] 	= sorted(mdata.keys())
				arrD[scenario]	= [mdata[t] for t in timesD[scenario]]
		
			if not len(arrD.keys()):continue	
			for linestyle in linestyles:			
				title = ' '.join([getLongName(i) for i in [model, jobID, region, layer, metric, key]])	
				filename =  bvp.folder(globalkeys.images_comp)+'_'.join([model, jobID, region, layer, metric, key,linestyle])+'.png'
		
				tsp.multitimeseries(
					timesD, 		# model times (in floats)
					arrD,			# model time series
					data 		= datarange,		# in situ data distribution
					title 		= title,
					filename	= filename,
					units 		= units,
					plotStyle 	= 'Together',
					lineStyle	= linestyle,
					colours		= colours,
				)
			
			
