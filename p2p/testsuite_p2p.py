# Copyright 2014, Plymouth Marine Laboratory
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
.. module:: testsuite_p2p
   :platform: Unix
   :synopsis: The tool that does the legwork for the point to point analysis.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
#Standard Python modules:
from sys import argv,exit
import os
from os.path import exists
from calendar import month_name

#Specific local code:
from bgcvaltools import bgcvalpython as bvp
from bgcvaltools.dataset import dataset
from p2p import matchDataAndModel,makePlots,makeTargets, makePatternStatsPlots
from p2p.slicesDict import populateSlicesList, slicesDict
#from 
###	Potential problems?
###		Reliance on ORCA1 grid


																			
def testsuite_p2p(	
                        modelFile	= '',
                        dataFile	= '',
			model		= '',
			scenario	= '',			
			year		= '',
			jobID		= '',
			dataType	= '',
			modelcoords 	= '',
			modeldetails 	= '',
			datacoords 	= '',
			datadetails 	= '',	
			datasource	= '',
			plottingSlices 	= [],
			layers		= [],
			workingDir  	= '',
			imageFolder 	= '',
			grid		= '',			
			gridFile	= '',
			annual 		= '',
			noPlots 	= False,
			noTargets 	= False,
			clean 		= False,
			):

	"""
	This analysis package performs the point to point analysis for a single model, for one year, for one job ID.
	
	Arguments:
	    model: Model name
	    
	    year: year (4 digit string), doesn't need to be exact. For climatologies, we typically use 2525 or something absurd.
	    
	    jobID: 5 letter jobID as used on monsoon. 
	    
	    av:
		The AutoVivification (av) is crucial. It controls the analysis. It locates the files. It identifies the field names in the netcdf.
	
		The av has a few very specific requiments in terms of structure and key words.
		Here is an example, of ERSEM chlorophyll:
			av['chl']['Data']['File'] 	= Observation_Filename_path_.netcdf	
			av['chl']['Data']['Vars'] 	= ['Chlorophylla',]		
			av['chl']['ERSEM']['File'] 	= Model_Filename_path_.netcdf
			av['chl']['ERSEM']['Vars'] 	= ['chl',]
			av['chl']['ERSEM']['grid']	= 'ORCA1'				
			av['chl']['layers'] 	= ['',]
		where: 
			'File' is the file path
			'Vars' is the variable as it is call in the netcdf.
			'grid' is the model grid name. These grids are linked to a grid mesh file for calculating cell volume, surface area and land masks.
			'layers' a list of depth levels. This is needed because some WOA files are huges and desktop computers may run the p2p analysis of that data.
				layers options are ['', 'Surface','100m','200m','500m',]
				layers = ['',] indicates look at no depth slicing. (Not recommended for big (>500,000 points) datasets! Don't say I didn't warn you.)

	    plottingSlices:
		plottingSlices is a list of regional, temporal, or statistical slices to be given to the analysis for plotting.
		ie:	plottingSlices = ['All', 				# plots everything,
					  'NorthAtlantic', 			# plots North Atlantic
					  'February',				# plots February
					  ('NorthAtlantic', 'February'),	# plots North Atlantic in February
					  ]
			plottingSlices can be made automatically with UKESMpthon.populateSlicesList()
			plottingSlices can also be added to the av:
				av[name]['plottingSlices'] = a list of slices
	    workingDir: 
	    	workingDir is a location for the working files that are produced during the analysis. 
	    	if no working directory is provided, the default is: ~/WorkingFiles/model-jobID-yyear
	    		
	    imageFolder: 
	    	imageFolder is a location for all the images  that are produced during the analysis. 
	    	if no working directory is provided, the default is: ~/images/model-jobID  	

	    noPlots:
	    	noPlots is a boolean value to turn off the production of images.
	    	This can streamline the analysis routine, if plots are not needed.
	    	
	Returns:
		shelvesAV:
		another AutoVivification with the following structure:
		shelvesAV[model][name][layer][newSlice][xkey] = shelvePath
	
	testsuite_p2p is not the place for intercomparisons of models, years, or jobID. 
	This can be done after calling testsuite_p2p.py, and by using the 

	"""

	print "#############################"
	print "testsuite_p2p:  "
	print "models:        ",model
	print "year:          ",year
	print "scenario:      ",scenario	
	print "jobID:         ",jobID
	#print "av keys:	      ",sorted(av.keys())
	print "#############################"	
		
	#if len( av.keys())==0:
	#	print "No autovivification nested dictionary given. - See testsuite_p2p documentation or a working example."
	#	exit(0)
	

	# Location of processing files
	if len( workingDir) == 0:
		workingDir = bvp.folder("WorkingFiles/"+model+'-'+jobID+'-'+year)
		print "No working directory provided, creating default:",workingDir
		
	# Location of image Output files
	if noPlots is False:
	    if len(imageFolder)==0:
		imageFolder 	= bvp.folder('images/'+jobID)
		print "No image directory provided, creating default:",imageFolder

	# Location of image Output files
	if type(modelFile) == type('A_String'):
	        print "testsuite_p2p.py:\tINFO:\tfound p2p file (it's a string):",modelFile
	elif type(modelFile) == type(['a','list']):
		modelFiles = modelFile[:]
		found = 0
		if len(modelFile) ==1:
			#####
			# ModelFile is a list of one 
			modelFile = modelFile[0]
			found+=1
			print "testsuite_p2p.py:\tINFO:\tfound p2p file: (it's a list)",modelFile
		else:
                    #####
                    # ModelFile is a list of many files.

		    yr = float(year)
		    if float(year) == int(year): yr = yr + 0.55
		    
		    for fn in modelFiles:
		    
			nc = dataset(fn,'r')
			ts = bvp.getTimes(nc,modelcoords)
			# assert False	#i don't think that this is correct #please think about it some more.
			if ts.max()+1 < yr:
				print "p2p:\t File outside time range",yr,':',[int(ts.min()),'->',int(ts.max())]
				nc.close()
				continue
			if ts.min()-1 > yr:
				print "p2p:\t File outside time range",yr,':',[int(ts.min()),'->',int(ts.max())]		
				nc.close()
				continue
                        print "p2p:\t File  inside time range",yr,':',[int(ts.min()),'->',int(ts.max())], "Found it!"
			print "Found p2p file:",fn
			modelFile = fn
			found+=1
		if found == 0 : 
			print "Did not find p2p file for year", yr
			assert 0					
	else:
        	assert("testsuite_p2p.py:\tError:\tp2p file is not a string or a list:",modelFile)
		

	#####
	# Start analysis here:
	shelvesAV = []#AutoVivification()
	for name in [	dataType, ]:
		#####
		# Start with some tests of the av.
		
		#####
		# Testing av for presence of model keyword
	    	print "testsuite_p2p.py: \tINFO:\t",model,jobID, year, name #, av[name][model]
			

		#####
		# Testing av for presence of data/obs files.
		if not os.path.exists(modelFile):
			print "testsuite_p2p.py:\tWARNING:\tModel File does not exist", modelFile
			continue			    	
		if not os.path.exists(dataFile):
			print "testsuite_p2p.py:\tWARNING:\tData File does not exist", dataFile
			continue
		if not os.path.exists(gridFile):
			print "testsuite_p2p.py:\tWARNING:\tGrid File does not exist", gridFile
			continue
						
	    	#####					
		# Testing av for presence of layers	
		if len(layers) ==0:
			raise AssertionError("testsuite_p2p: \tERROR: no layers provided.")
			
		#####
		# Made it though the initial tests. Time to start the analysis.
		print "testsuite_p2p.py:\tINFO:\tMade it though initial tests."
		for layer in layers:
			layer = str(layer)
			print "testsuite_p2p.py:\tINFO:\tRunning:",model,jobID, year, name, layer
			#####
			# matchDataAndModel:
			# Match observations and model. 
			# Does not produce and plots.
			b = matchDataAndModel(			dataFile, 
								modelFile,
								dataType	= name,
					  			modelcoords 	= modelcoords,
					  			modeldetails 	= modeldetails,
					  			datacoords 	= datacoords,
					  			datadetails 	= datadetails,								
								datasource	= datasource,
								model 		= model,
								scenario	= scenario,
								jobID		= jobID,
								year		= year,
								workingDir 	= bvp.folder(workingDir),
								layer 		= layer,
								grid		= grid,
								gridFile	= gridFile,
								clean		= clean,
						)

			#####
			# makePlots:
			# Make some plots of the point to point datasets.
			# MakePlot runs a series of analysis, comparing every pair in DataVars and ModelVars
			#	 under a range of different masks. For instance, only data from Antarctic Ocean, or only data from January.
			# The makePlot produces a shelve file in workingDir containing all results of the analysis.
			if len( plottingSlices) ==0:
				nplottingSlices = populateSlicesList()
				print "No plotting slices provided, using defaults",nplottingSlices
			else:	
				nplottingSlices = plottingSlices
				print "Plotting slices provided, using ",nplottingSlices					

					
			#imageDir	= bvp.folder(imageFolder +'/P2Pplots/'+year+'/'+name+layer)	
			m = makePlots(	b.MatchedDataFile, 
					b.MatchedModelFile, 
					name, 
					newSlices 	= nplottingSlices,
					datasource	= datasource,
					model 		= model,
					scenario	= scenario,					
					jobID		= jobID,
					layer 		= layer,
					year 		= year, 
		  			modelcoords 	= modelcoords,
		  			modeldetails 	= modeldetails,
		  			datacoords 	= datacoords,
		  			datadetails 	= datadetails,
					shelveDir 	= bvp.folder(workingDir),
					imageDir	= bvp.folder(imageFolder),
					compareCoords	= True,
					noPlots		= noPlots,
					clean		= clean,
				     )

			#shelvesAV[model][name][layer] = m.shelvesAV
			shelvesAV.extend(m.shelvesAV)
			
			#####
			# no plots doesn't produce any plots, but does produce the list of shelves which can be used in Taylor/Target/Pattern diagrams.			
			if noPlots: continue

			if noTargets: continue
			#csvFile = bvp.folder(workingDir+'/CSV')+'summary_file.csv'
			#print "attempting csvFromShelves:",m.shelves, csvFile
			#c = csvFromShelves.csvFromShelves(m.shelves, csvFile ,['check',])

			
			#####
			# makeTargets:
			# Make a target diagram of all matches for this particular dataset. 
			#filename = bvp.folder(imageFolder+'/Targets/'+year+'/AllSlices')+model+'-'+jobID+'_'+year+'_'+name+layer+'.png'
			#t = makeTargets(	m.shelves, 
			#			filename,
			#			#name=name,
			#			legendKeys = ['newSlice','ykey',],
			#			debug=True)
			#			#imageDir='', 
			
			#####
			# Produce a set of pattern and a target plots for each of the groups here.
			if annual:	groups = {'Oceans':[],'depthRanges':[], 'BGCVal':[],}
			else:		groups = {'Oceans':[],'Months':[],'Seasons':[],'NorthHemisphereMonths':[],'SouthHemisphereMonths':[],'depthRanges':[],'BGCVal':[],}
			for g in groups:
			    	groups[g] = bvp.reducesShelves(shelvesAV,  models =[model,],layers = [layer,], names = [name,], sliceslist =slicesDict[g])
				print g, groups[g]
				
				if len(groups[g])==0:continue 
				 
				#####
				# makeTargets:
				# Make a target diagram of the shelves of this group. 
			  	filename = bvp.folder(imageFolder+'/Targets/'+year+'/'+name+layer+'/'+g)+model+'_'+jobID+'_'+year+'_'+name+layer+'_'+g+'.png'
				makeTargets(	groups[g], 
						filename,
						legendKeys = ['newSlice',],					
						)
				#####
				# makePattern plots:
				# Make a pattern  diagram of all matches for this particular dataset. 
				xkeys=''
				for o in ['Oceans','Months','depthRanges','BGCVal']:
					if g.find(o)>=0:  xkeys=o
				if xkeys=='':
					print "Could no find x axis keys!",g,'in',['Oceans','Months','BGCVal']
					
			  	filenamebase = bvp.folder(imageFolder+'/Patterns/'+year+'/'+name+layer+'/'+g)+'Months_'+model+'_'+jobID+'_'+year+'_'+name+layer
				makePatternStatsPlots(	{name :groups[g],}, # {legend, shelves}
							name+' '+g,	#xkeysname
							slicesDict[xkeys],		#xkeysLabels=
							filenamebase,	# filename base	
							grid		= grid,	
							gridFile	= gridFile				
							)
			if not annual:
				#####
				# After finding all the shelves, we can plot them on the same axis.				
			  	filenamebase = bvp.folder(imageFolder+'/Patterns/'+year+'/'+name+layer+'/ANSH')+'ANSH-Months_'+model+'_'+jobID+'_'+year+'_'+name+layer
			  	
				makePatternStatsPlots(	{'North Hemisphere' :groups['NorthHemisphereMonths'],
							 'South Hemisphere' :groups['SouthHemisphereMonths'],
							 'Global' :	     groups['Months'], }, # {legend, shelves}
							name+' Months',	#xkeysname
							slicesDict['Months'],#xkeysLabels=
							filenamebase,	# filename base	
							grid	= grid,	
							gridFile= gridFile												
							)

		if noPlots: 	continue
		if noTargets: 	continue		
		#####
		# And now by depth levels:
		if annual:	groups = ['Oceans','depthRanges','BGCVal',]
		else:		groups = ['Oceans','Months','Seasons','depthRanges','BGCVal',]	#'NorthHemisphereMonths':[],'SouthHemisphereMonths':[]}		
		for g in groups:
			if len(layers)<=1: continue	
			outShelves = {}
			for dl in layers:
				outShelves[dl] = bvp.reducesShelves(shelvesAV,  models =[model,],layers = [dl,], names = [name,], sliceslist =slicesDict[g])	
		  	filenamebase = bvp.folder(imageFolder+'/Patterns/'+year+'/'+name+'AllDepths/')+'AllDepths_'+g+'_'+model+'_'+jobID+'_'+year+'_'+name
			makePatternStatsPlots(	outShelves, 
						name+' '+g,
						slicesDict[g],		
						filenamebase,
						grid	= grid,
						gridFile= gridFile			
						)


	
	


	return shelvesAV
				


	
	
	
if __name__=="__main__":
	print 'The end.'
	



















	
