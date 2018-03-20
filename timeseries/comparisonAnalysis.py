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
import numpy as np

#####	
# Load specific local code:
from bgcvaltools import bgcvalpython as bvp
from longnames.longnames import getLongName, fancyUnits,titleify 
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

def csvRowify(lst):
	for i,l in enumerate(lst): lst[i] = getLongName(str(l)).replace(';',',')
	return '; '.join(lst)+';\n'
	
def latexify(lst,head=False):
	line = ''
	if head: line+='{'+' '.join(['l' for l in lst])+'}\n'
		
	for i,l in enumerate(lst): lst[i] = getLongName(str(l)).replace('%','\%')
	line+=' & '.join(lst)+'\\\\\n'
	if head: line+='\\hline\n'
	return line
			
def makeCSV(configfile):
	
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
		if akp.makeCSV == False: continue		
 	    	#if not akp.makeTS: continue 
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

	if len(data.keys())==0: return
	
	regions = regions.keys()
	layers = layers.keys()
	metrics	= ['mean' , 'metricless',]#'median',]#'min','max',]

	#yearblocks = [[1850.,1899.99],[1900.,1949.99],[1950.,1999.99],[1990.,1999.99],[2000.,2049.99],[2050.,2099.99],[2100.,2149.99],[2150.,2199.99],[2200.,2249.99],[2250.,2299.99],]

	doIndividual=True
	if doIndividual:
		yearblocks = [[1875.,1899.99],[1975.,1999.99],[2075.,2099.99],]	
		header = ['key', 'model', 'scenario', 'jobID', 'region','layer','metric',]
		header.extend([str(yb) for yb in yearblocks])
		doPercent = True
		if doPercent:	header.append('2075-2100 vs 1975-2000 % diff')
		outstring = csvRowify( header )
	
	
		for (key, scenario,region,layer,metric, model,jobID,) in product(ActiveKeys, scenarios, regions,layers, metrics, models,jobIDs ):
			try:	d = data[(key,model,scenario, jobID)][(region,layer,metric)]
			except : continue

			row = [key, model, scenario, jobID, region,layer,metric,]
		
			for yb in yearblocks:
				trangedata = []
				for t in d.keys():
				#	print t ,min(yb),max(yb), t < min(yb),t >  max(yb)
					if t < min(yb):continue
					if t > max(yb):continue				
					trangedata.append(d[t])
				#print trangedata, len(trangedata),np.ma.array(trangedata).mean()
				#assert 0
				if len(trangedata)==0: row.append('--')
				else:row.append(np.ma.array(trangedata).mean())
		
			if doPercent:
				if '--' in [row[-1],row[-2]]:
					row.append('--')
					continue
			
				percentdiff = 100.*(row[-1]-row[-2])/row[-2]
				row.append(percentdiff)
			
			outstring+=csvRowify( row )
		
  		csvfn = bvp.folder(akp.postproc_csv)+'_'.join([akp.jobID,akp.scenario,])+'.csv'
		print "makeCSV:\tWriting to", csvfn
		print outstring
		csvf = open(csvfn,'w')
		csvf.write(outstring)
		csvf.close()
		print "makeCSV:\tWrote to", csvfn	
	
	dogroups=True	
	if dogroups:
		modelGroups= {}
		yearblocks = [[1975.,1999.99],[2075.,2099.99],'2075-2100 vs 1975-2000 % diff']
		
		####
		# Split data into groups by model
		for (yb,key, scenario,region,layer,metric, model,jobID) in product(yearblocks,ActiveKeys, scenarios, regions,layers, metrics, models,jobIDs ):
			try:	d = data[(key,model,scenario, jobID)][(region,layer,metric)]
			except : continue
			row = [key, scenario, jobID, region,layer,metric,]

			if yb == '2075-2100 vs 1975-2000 % diff':
			
				trangedata1975 = []
				trangedata2075 = []
				for t in d.keys():
					if 1975. < t < 2000. :trangedata1975.append(d[t])
					if 2075. < t < 2100. :trangedata2075.append(d[t])						
					
				if len(trangedata1975)*len(trangedata2075)==0:continue	
				mean = 100.*(np.ma.array(trangedata2075).mean() -np.ma.array(trangedata1975).mean())/np.ma.array(trangedata1975).mean()
				modelgroup = (key,scenario, jobID,region,layer,metric,yb)			
				try:	modelGroups[modelgroup].append(mean)
				except:	modelGroups[modelgroup] = [mean,]
				
			else:
				yb = tuple(yb)
				trangedata = []
				for t in d.keys():
					if t < min(yb):continue
					if t > max(yb):continue				
					trangedata.append(d[t])
			
				if len(trangedata)==0: continue
				mean = np.ma.array(trangedata).mean()
				modelgroup = (key,scenario, jobID,region,layer,metric,yb)				
				try:	modelGroups[modelgroup].append(mean)
				except:	modelGroups[modelgroup] = [mean,]
		header = ['key', 'scenario', 'jobID', 'region','layer','metric','Year Range', ]
		header.append('Number of Models')
		header.append('Mean')
		header.append('Standard Deviation')
		csvoutstring = csvRowify( header )
		
		texheader = ['Field',]
		texheader.append('\#')
		texheader.append('1975-2000')
		texheader.append('2075-2100')
		texheader.append('Mean Diff.')
		#texheader.append('Diff. STD')
		
		texoutstring = latexify( texheader, head=True,)

		####
		# Calculate basic metrics from data in groups by model
		for (yb,key, scenario,jobID, region,layer,metric, ) in product(yearblocks, ActiveKeys, scenarios, jobIDs, regions,layers, metrics,):
			if yb == '2075-2100 vs 1975-2000 % diff':pass
			else:	yb = tuple(yb)		
			modelgroup = (key,scenario, jobID,region,layer,metric,yb)
			try: 	dat = np.ma.array(modelGroups[modelgroup])
			except: continue

			
			row = [key, scenario,jobID, region,layer,metric, yb,]
			row.append(len(dat))
			row.append(dat.mean())			
			row.append(dat.std())
			csvoutstring += csvRowify( row )
			
			#if yb == '2075-2100 vs 1975-2000 % diff':

		for (key, scenario,jobID, region,layer,metric, ) in product( ActiveKeys, scenarios, jobIDs, regions,layers, metrics,):			

			if region not in ['regionless','Global']: continue
			fieldname =  ' '.join([getLongName(str(l)) for l in [region,layer,key]]).replace('%','\%')
			texrow = [fieldname, ]

			
			for yb in yearblocks:
				if yb == '2075-2100 vs 1975-2000 % diff':pass
				else:	yb = tuple(yb)		
				modelgroup = (key,scenario, jobID,region,layer,metric,yb)
				try: 	dat = np.ma.array(modelGroups[modelgroup])
				except: continue			
				
				if key == 'TotalOMZVolume': dat = dat*1E-15 
				
				if yb in [tuple([1975.,1999.99]),]:
					texrow.append(len(dat))
					texrow.append(round(dat.mean(),2))				
				if yb in [tuple([2075.,2099.99]),]:				
					#texrow.append(len(dat))
					texrow.append(round(dat.mean(),2))
					
				if yb == '2075-2100 vs 1975-2000 % diff':
					#texrow.append(len(dat))				
					texrow.append(round(dat.mean(),2))			
					#texrow.append(round(dat.std(),2))
			if len(texrow)==1:continue
			texoutstring += latexify( texrow )
			
			#print texoutstring
		####
		# Write summary file.			
	  	csvfn = bvp.folder(akp.postproc_csv)+'_'.join([akp.jobID,akp.scenario,])+'_summary.csv'	
		print "makeCSV:\tWriting to", csvfn
		print csvoutstring
		csvf = open(csvfn,'w')
		csvf.write(csvoutstring)
		csvf.close()
		print "makeCSV:\tWrote to", csvfn


		####
		# Write latex table.			
	  	csvfn = bvp.folder(akp.postproc_csv)+'_'.join([akp.jobID,akp.scenario,])+'_summarytable.tex'	
		print "makeCSV:\tWriting to", csvfn
		csvf = open(csvfn,'w')
		texoutstring+='\\hline\n'
		csvf.write(texoutstring)
		csvf.close()
		print "makeCSV:\tWrote to", csvfn
					
	
def comparisonAnalysis(configfile, writeCSV=True):

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
                        datarange = [float(t) for t in datarange]

			datatimes = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datatimes
                        datatimes = [float(t) for t in datatimes]

			timerange = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].timerange			
			timerange = [float(t) for t in sorted(timerange)]

                        datasource = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datasource

			for jobID in jobIDs:
			
				try:	
					mdata = data[(key,model,scenario, jobID)][(region,layer,metric)]
				except:					
					continue
					
				times  = []
				for t in sorted(mdata.keys()):
					if t < timerange[0]:continue
					if t > timerange[1]:continue					
					times.append(t) 
				timesD[jobID] 	= times
				arrD[jobID]	= [mdata[t] for t in timesD[jobID]]
			
			if not len(arrD.keys()):continue	
		
			for linestyle in linestyles:
				title = titleify([model, scenario, region, layer, metric, key])	
				filename =  bvp.folder(globalkeys.images_comp)+'_'.join([model, scenario, region, layer, metric, key,linestyle])+'.png'
		
				tsp.multitimeseries(
					timesD, 		# model times (in floats)
					arrD,			# model time series
					data 		= datarange,		# in situ data distribution
					datatimes	= datatimes,		# in situ time range
                                        datasource      = datasource,           # in situ data source
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

                        datarange = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datarange
                        datarange = [float(t) for t in datarange]

                        datatimes = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datatimes
                        datatimes = [float(t) for t in datatimes]

                        timerange = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].timerange
                        timerange = [float(t) for t in sorted(timerange)]

                        datasource = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datasource
	
			for model in models:
			
				try:	mdata = data[(key,model,scenario, jobID)][(region,layer,metric)]
				except:	continue

				times  = []
				for t in sorted(mdata.keys()):
					if t < timerange[0]:continue
					if t > timerange[1]:continue					
					times.append(t)
				timesD[model] 	= times
				arrD[model]	= [mdata[t] for t in timesD[model]]
		
			if not len(arrD.keys()):continue
		
			for linestyle in linestyles:
				title = titleify([scenario,jobID, region, layer, metric, key])
				filename =  bvp.folder(globalkeys.images_comp)+'_'.join([ scenario, jobID, region, layer, metric, key,linestyle])+'.png'
					
				tsp.multitimeseries(
					timesD, 		# model times (in floats)
					arrD,			# model time series
					data 		= datarange,		# in situ data distribution
                                        datatimes       = datatimes,
					datasource	= datasource,
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
                        datarange = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datarange
                        datarange = [float(t) for t in datarange]

                        datatimes = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datatimes
                        datatimes = [float(t) for t in datatimes]

                        timerange = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].timerange
                        timerange = [float(t) for t in sorted(timerange)]

                        datasource = globalkeys.AnalysisKeyParser[(model,jobIDs[0],globalkeys.years[0],scenario,key)].datasource

			#datarange = globalkeys.AnalysisKeyParser[(model,jobID,globalkeys.years[0],scenarios[0],key)].datarange			
                        #datarange = [float(t) for t in sorted(datarange)]
			#timerange = globalkeys.AnalysisKeyParser[(model,jobID,globalkeys.years[0],scenarios[0],key)].timerange			
			#timerange = [float(t) for t in sorted(timerange)]	
			for scenario in scenarios:
			
				try:	mdata = data[(key,model,scenario, jobID)][(region,layer,metric)]
				except:	continue

				times  = []
				for t in sorted(mdata.keys()):
					if t < timerange[0]:continue
					if t > timerange[1]:continue					
					times.append(t)
				timesD[scenario] 	= times
				arrD[scenario]	= [mdata[t] for t in timesD[scenario]]
		
			if not len(arrD.keys()):continue	
			for linestyle in linestyles:			
				title = titleify([model, jobID, region, layer, metric, key])	
				filename =  bvp.folder(globalkeys.images_comp)+'_'.join([model, jobID, region, layer, metric, key,linestyle])+'.png'
		
				tsp.multitimeseries(
					timesD, 		# model times (in floats)
					arrD,			# model time series
					data 		= datarange,		# in situ data distribution
                                        datatimes       = datatimes,		# in situ time range
                                        datasource      = datasource,		# in situ data source
					title 		= title,
					filename	= filename,
					units 		= units,
					plotStyle 	= 'Together',
					lineStyle	= linestyle,
					colours		= colours,
				)
			
			
