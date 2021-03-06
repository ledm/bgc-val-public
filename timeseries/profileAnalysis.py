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
"""
.. module:: profileAnalysis
   :platform: Unix
   :synopsis: A tool for running a depth-profile time series analysis.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>
"""


import numpy as np
from shelve import open as shOpen
#from netCDF4 import num2date
import os
import shutil

#Specific local code:
from bgcvaltools import bgcvalpython as bvp
import timeseriesTools as tst 
import timeseriesPlots as tsp 
from bgcvaltools.makeMaskNC import makeMaskNC
from bgcvaltools.dataset import dataset
from longnames.longnames import getLongName
from functions.stdfunctions import extractData

class profileAnalysis:
  def __init__(self,
  		modelFiles	= '', 
		dataFile	= '',
		dataType	= '',
		modelcoords 	= '',
		modeldetails 	= '',
		datacoords 	= '',
		datadetails 	= '',								
		datasource	= '',
		model 		= '',
		scenario	= '',
		timerange	= '',		
		jobID		= '',
		layers	 	= '',
		regions	 	= '',			
		metrics	 	= '',
		workingDir	= '',
		imageDir	= '',						
		grid		= '',
		gridFile	= '',
		clean		= True,
		debug		= True,
		strictFileCheck = False,
		):
		
	#####
	#	This is the class that does most of the legwork.
	#	First we save all the initialisation settings as class attributes.
		
	
	if debug: print "profileAnalysis:\t init."	
	self.modelFiles 	= modelFiles 		
	self.dataFile		= dataFile
	self.dataType		= dataType
	self.modelcoords 	= modelcoords		
	self.modeldetails 	= modeldetails
	self.datacoords 	= datacoords
	self.datadetails 	= datadetails						
	self.datasource		= datasource
	self.model 		= model
	self.scenario		= scenario
	self.jobID		= jobID
	self.layers	 	= layers
	self.regions	 	= regions			
	self.metrics	 	= metrics						
	self.grid		= grid
	self.gridFile		= gridFile
	self.workingDir		= workingDir
  	self.imageDir 		= imageDir
	self.debug		= debug
	self.clean		= clean

	self.timerange		= np.array([float(t) for t in sorted(timerange)]) 	
	
	####
	# 	Do some tests on whether the files are present/absent	
	if len(modelFiles) == 0:
		print "analysis-profiles.py:\tWARNING:\tmodel files are not provided:",modelFiles
		return
		if strictFileCheck: assert 0
		
		
  	self.gridmaskshelve 	= bvp.folder(self.workingDir)+'_'.join([self.grid,])+'_masks.shelve'		
  	self.shelvefn 		= bvp.folder(self.workingDir)+'_'.join(['profile',self.jobID,self.dataType,])+'.shelve'
	self.shelvefn_insitu	= bvp.folder(self.workingDir)+'_'.join(['profile',self.jobID,self.dataType,])+'_insitu.shelve'

	self._masksLoaded_ 	= False
	self.doHov		= True
	#####
	# Load Data file
        self.__madeDataArea__ = False		
 	self.loadData()
	#assert 0
	
	#####
	# Load Model File
  	self.loadModel()  	

	#####
	# Make the plots:
  	self.makePlots()
  	
        if self.debug:print "profileAnalysis:\tsafely finished ",self.dataType, (self.modeldetails['name'])
  		

  def setmlayers(self):
  	"""	From the first model netcdf,
  		determine the number of depth layers.
  	""" 	
	if self.layers not in ['All','Every2','Every5','Every10',]:
		self.mlayers = self.layers
		return
	mlayers = self.calclayers(self.modelFiles[0],self.modelcoords['z'])
	if self.layers =='All':		self.mlayers = mlayers
	if self.layers =='Every2':	self.mlayers = mlayers[::2]
	if self.layers =='Every5':	self.mlayers = mlayers[::5]		
	if self.layers =='Every10':	self.mlayers = mlayers[::10]
	print self.mlayers		
				
  def setdlayers(self):
  	"""	From the data netcdf,
  		determine the number of depth layers.
  	""" 	
	if self.layers not in ['All','Every2','Every5','Every10',]:
		self.dlayers = self.layers
		return
	dlayers = self.calclayers(self.dataFile,self.datacoords['z'])
	if self.layers =='All':		self.dlayers = dlayers
	if self.layers =='Every2':	self.dlayers = dlayers[::2]
	if self.layers =='Every5':	self.dlayers = dlayers[::5]		
	if self.layers =='Every10':	self.dlayers = dlayers[::10]
				
		
  def calclayers(self,fn,depthkey):
  	
	nc = dataset(fn,'r')
	depth = nc.variables[depthkey]  	
	if depth.ndim == 1:
		layers = np.arange(len(depth))
	if depth.ndim == 3:
		layers = np.arange(len(depth[:,0,0]))
	nc.close()
	return list(layers)
	
		
  def loadModel(self):
	if self.debug: print "profileAnalysis:\tloadModel."
	####
	# load and calculate the model info
        self.setmlayers()
	
	try:
		if self.clean: 
			print "profileAnalysis:\tloadModel:\tUser requested clean run. Wiping old data."
			assert 0		
		sh = shOpen(self.shelvefn)
		readFiles 	= sh['readFiles']
		modeldataD 	= sh['modeldata']
		sh.close()

		print "OprofileAnalysis:\tloadModel:\tpened shelve:", self.shelvefn, '\tread', len(readFiles)
	except:
		readFiles = []
		modeldataD = {}
#		self.setmlayers()
		for r in self.regions:
		 for l in self.mlayers:
		  for m in self.metrics:
		   	modeldataD[(r,l,m)] = {}
		   	
		print "profileAnalysis:\tloadModel:\tCould not open shelve:", self.shelvefn, '\tread', len(readFiles)

	###############
	# Check whethere there has been a change in what was requested:
	for r in self.regions:
	  for l in self.mlayers:
	    for m in self.metrics:
	    	if self.debug:print "profileAnalysis:\tloadModel:\tChecking: ",[r,l,m,],'\t',
	    	try:
	    		if self.debug: print 'has ', len(modeldataD[(r,l,m)].keys()), 'keys'
	    	except: 
	    		readFiles = []
	    		modeldataD[(r,l,m)] = {}
	    		if self.debug: print 'has no keys'
	    	try:	
	    	    	if len(modeldataD[(r,l,m)].keys()) == 0: 
	    	    		print "profileAnalysis:\tloadModel:\tmodeldataD[",(r,l,m),"] has no keys"
	    	    		readFiles = []
	    	    		assert 0
	    	    		
	    	except: pass

	#####
	# Summarise checks
	if self.debug:	
		print "profileAnalysis:\tloadModel:\tloadModel:post checks:"
		#print "modeldataD:",modeldataD
		print "profileAnalysis:\tloadModel:\tshelveFn:",self.shelvefn
		print "profileAnalysis:\tloadModel:\treadFiles:",
		try:	print readFiles[-1]
		except: print '...'

	###############
	# Load files, and calculate fields.
	openedFiles = 0					
	for fn in self.modelFiles:
		if fn in readFiles:continue
		
		if not self._masksLoaded_: 
			self.loadMasks()		
		
		print "profileAnalysis:\tloadModel:\tloading new file:",self.dataType,fn,
		nc = dataset(fn,'r')
		ts = bvp.getTimes(nc,self.modelcoords)
		dates = bvp.getDates(nc,self.modelcoords) 		
		meantimes = np.mean(ts)
		print "\ttime:",meantimes
		if ts.max() < self.timerange[0]:
			print "profileAnalysis:\t File outside time range",(self.timerange),':',ts.max()
			nc.close()
			continue
		if ts.min() > self.timerange[1]:
			print "profileAnalysis:\t File outside time range",(self.timerange),':',ts.min()		
			nc.close()
			continue
		
		#DL = tst.DataLoader(fn,nc,self.modelcoords,self.modeldetails, regions = self.regions, layers = self.layers,)
		nc = dataset(fn,'r')
		dataAll = extractData(nc,self.modeldetails).squeeze()
		
		for r in self.regions:
		  for m in self.metrics:
		    	if m =='mean':		  
		  	    if len(ts) == 1:
				#####
				# One time step per file.
				
				data = bvp.mameanaxis(np.ma.masked_where((self.modelMasks[r] != 1) + dataAll.mask,dataAll), axis=(1,2))
				
				if self.debug: print "profileAnalysis:\tloadModel.",r,m,self.dataType,'\tyear:',int(meantimes), 'mean:',data.mean(),data.shape
				#if self.debug:print "profileAnalysis:\tloadModel.",self.dataType, data.shape, data.min(),data.max(), dataAll.shape ,self.modelMasks[r].shape, dataAll.min(),dataAll.max()
				alllayers = []
				for l,d in enumerate(data):
					#print "Saving model data profile",r,m,l,d
					modeldataD[(r,l,m)][meantimes] = d
					alllayers.append(l)
					
				#####
				# Add a masked value in layers where there is no data.
				for l in self.mlayers:
					if l in alllayers:continue
					modeldataD[(r,l,m)][meantimes] = np.ma.masked
					
		  	    else:
				#####
				# multiple time steps per file.
				for t, meantime in enumerate(ts):
					dataAllt  = dataAll[t]
					data = bvp.mameanaxis(np.ma.masked_where((self.modelMasks[r] != 1) + dataAllt.mask,dataAllt), axis=(1,2))
				
					if self.debug: print "profileAnalysis:\tloadModel.",r,m,self.dataType,'\tyear:',int(meantime), 'mean:',data.mean(),data.shape
					alllayers = []
					for l,d in enumerate(data):
						#print "Saving model data profile",r,m,l,d,t,meantime
						modeldataD[(r,l,m)][meantime] = d
						alllayers.append(l)
					
					#####
					# Add a masked value in layers where there is no data.
					for l in self.mlayers:
						if l in alllayers:continue
						modeldataD[(r,l,m)][meantime] = np.ma.masked					
			else:
				print 'ERROR:',m, "not implemented in profile"
				assert 0
								
		readFiles.append(fn)
		openedFiles+=1			

		nc.close()
		if openedFiles:
			print "Saving shelve:",self.dataType, self.shelvefn, '\tread', len(readFiles)				
			sh = shOpen(self.shelvefn)
			sh['readFiles']		= readFiles
			sh['modeldata'] 	= modeldataD
			sh.close()
			openedFiles=0	
	if openedFiles:
		print "Saving shelve:",self.dataType, self.shelvefn, '\tread', len(readFiles)				
		sh = shOpen(self.shelvefn)
		sh['readFiles']		= readFiles
		sh['modeldata'] 	= modeldataD
		sh.close()
	
	self.modeldataD = modeldataD
	if self.debug: print "profileAnalysis:\tloadModel.\t Model loaded:",	self.modeldataD.keys()[:3], '...', len(self.modeldataD.keys())	

  def loadMasks(self):
  	#####
	# Here we load the masks file.
	self.maskfn = bvp.folder(self.workingDir+'/masks')+self.grid+'_masks.nc'
	
	if not os.path.exists(self.maskfn):
		print "Making mask file",self.maskfn, 'from',self.gridFile

		makeMaskNC(self.maskfn, self.regions, self.grid,self.modelcoords,gridfn= self.gridFile)
	else:
		print "Mask file exists:",self.maskfn
	self.modelMasks= {}
	
	ncmasks = dataset(self.maskfn,'r')
	
	for r in self.regions:
		if r in ncmasks.variables.keys():
			print "Loading mask",r
			self.modelMasks[r] = ncmasks.variables[r][:]
			
		else:
			newmask = bvp.folder(self.workingDir+'/masks')+self.grid+'_masks_'+r+'.nc'

			if not os.path.exists(newmask):
				makeMaskNC(newmask, [r,], self.grid,self.modelcoords,gridfn= self.gridFile)
			nc = dataset(newmask,'r')
			self.modelMasks[r] = nc.variables[r][:]
			nc.close()			
			
	print "Loaded masks",self.modelMasks.keys()

	ncmasks.close()
	self._masksLoaded_ = True



	
  def loadData(self):
  	
	if self.debug: print "profileAnalysis:\t loadData.",self.dataFile		
	
  	if not self.dataFile: 
 		if self.debug: print "profileAnalysis:\t No data File provided:",self.dataFile		 		
		self.dataD = {}
		return

  	if not os.path.exists(self.dataFile): 
 		if self.debug: print "profileAnalysis:\tWARNING:\t No such data File:",self.dataFile		 
		self.dataD = {}
		return
				
	###############
	# load and calculate the real data info
	try:
		if self.clean: 
			print "profileAnalysis:\t loadData\tUser requested clean run. Wiping old data."
			assert 0		
		sh = shOpen(self.shelvefn_insitu)
		dataD 	= sh['dataD']
		sh.close()
		print "profileAnalysis:\t loadData\tOpened shelve:", self.shelvefn_insitu
		self.dataD = dataD
	except:
		dataD = {}
		print "profileAnalysis:\t loadData\tCould not open shelve:", self.shelvefn_insitu


	###############
	# Test to find out if we need to load the netcdf, or if we can just return the dict as a self.object.
	needtoLoad = False
	self.setdlayers()
	for r in self.regions:
	     if needtoLoad:continue
	     for l in sorted(self.dlayers)[:]:	    
 	      for m in sorted(self.metrics)[:]:
		#if needtoLoad:continue
	    	try:	
	    		dat = self.dataD[(r,l,m)]
	    		print "profileAnalysis:\t loadData\t",(r,l,m)#,dat
	    	except: 
			needtoLoad=True
			print "profileAnalysis:\t loadData\tUnable to load",(r,l,m)

	if needtoLoad: pass	
	else:
		self.dataD = dataD	
		return
		
	###############
	# Loading data for each region.
	print "profileAnalysis:\t loadData,\tloading ",self.dataFile
	nc = dataset(self.dataFile,'r')
	data = tst.loadData(nc, self.datadetails)

	if not self.__madeDataArea__: self.AddDataArea()	
	
	###############
	# Loading data for each region.
	dl = tst.DataLoader(self.dataFile,'',self.datacoords,self.datadetails, regions = self.regions, layers = self.dlayers[:],)
	
									    	
	maskedValue = np.ma.masked # -999.# np.ma.array([-999.,],mask=[True,])
	#maskedValue = np.ma.array([-999.,],mask=[True,])
	#maskedValue  = -999 #np.ma.array([-999.,],mask=[True,])	
	count =0
    	for l in sorted(self.dlayers)[:]:
	    for r in self.regions:
	    	dataDarray = dl.load[(r,l,)]	
	    	try:   	
	    		meandatad = dataDarray.mean()
	    		datadmask = (~np.ma.array(dataDarray).mask).sum()
	    	except: 
	    		meandatad = False
	    		datadmask = False
	    		
		if np.isnan(meandatad) or np.isinf(meandatad) or dataDarray.mask.all() or np.ma.is_masked(meandatad):
	    		meandatad = False
	    		datadmask = False			

	    		

		if False in [meandatad, datadmask]: 
			for m in self.metrics:		
				dataD[(r,l,m)] = maskedValue
			continue
    			print "profileAnalysis:\t loadData\tproblem with ",(r,l)
    			
				
	    	dataDlat = dl.load[(r,l,'lat')]		    	
	    	dataDlon = dl.load[(r,l,'lon')]		
	    	dataDarea = self.loadDataAreas(dataDlat,dataDlon)
		    	
    		print "profileAnalysis:\t loadData,\tloading ",(r,l), '\tmean (pre weighting):\t',meandatad

		if 'mean' in self.metrics:
			dataD[(r,l,'mean')] = np.average(dataDarray, weights = dataDarea)
		
		if 'median' in self.metrics:
			out_pc = bvp.weighted_percentiles(dataDarray, [50.,], weights = dataDarea)
			
			for pc,dat in zip(percentiles, out_pc):
				if pc==50.: dataD[(r,l,'median')][meantime] = dat
				
		if 'min' in self.metrics:
			dataD[(r,l,'min')] = np.ma.min(dataslice)
			
		if 'max' in self.metrics:
			dataD[(r,l,'max')] = np.ma.max(dataslice)
			
				
				
				

    	    count+=1
    	    if count%20==0 and count >0:	
		    print "profileAnalysis:\t loadData.\tSaving shelve: (layer",l,")", self.shelvefn_insitu			
		    sh = shOpen(self.shelvefn_insitu)
		    sh['dataD'] 	= dataD
		    sh.close()
		    count=0

    		
	###############
	# Savng shelve		
	print "profileAnalysis:\t loadData.\tSaving shelve:", self.shelvefn_insitu
	if count>0:			
		try:
			sh = shOpen(self.shelvefn_insitu)
			sh['dataD'] 	= dataD
			sh.close()

			print "profileAnalysis:\t loadData.\tSaved shelve:", self.shelvefn_insitu
		
		except:
			print "profileAnalysis:\t WARNING.\tSaving shelve failed, trying again.:", self.shelvefn_insitu			
			print "Data is", dataD.keys()
		
			for key in sorted(dataD.keys()): 

			
				print key, ':\t', dataD[key]
				sh = shOpen(bvp.folder('./tmpshelves')+'tmshelve.shelve')
				sh['dataD'] 	= dataD[key]
				sh.close()
				print "saved fine:\t./tmpshelves/tmshelve.shelve"
		
			shutil.move(self.shelvefn_insitu, self.shelvefn_insitu+'.broken')

	#		try:
			sh = shOpen(self.shelvefn_insitu)
			sh['dataD'] 	= dataD
			sh.close()
	#		except:
	#			print "profileAnalysis:\t WARNING.\tUnable to Save in situ shelve.\tYou'll have to input it each time.",self.shelvefn_insitu	
		 	
	self.dataD = dataD

  def AddDataArea(self,):
  	"""
  	Adding Area dictionany
  	"""
  	if not self.dataFile:
  		self.dataAreaDict = {}
  		return
  	area = tst.makeArea(self.dataFile,self.datacoords)
	nc = dataset(self.dataFile,'r')
	lats = nc.variables[self.datacoords['lat']][:]	
	lons = nc.variables[self.datacoords['lon']][:]	
	nc.close()
	print "timeseriesAnalysis:\tAddDataArea:\t",area.shape,lats.shape,lons.shape
	self.dataAreaDict = {}
	if lats.ndim ==2:
		for (i,j), a in np.ndenumerate(area):
			#if np.ma.is_masked(a):continue
			self.dataAreaDict[(lats[i,j],lons[i,j])] = a
	if lats.ndim ==1:
		for (i,j), a in np.ndenumerate(area):
			#if np.ma.is_masked(a):continue
			self.dataAreaDict[(lats[i],lons[j])] = a
	self.__madeDataArea__ = True
	
  def loadDataAreas(self,lats,lons):
  	"""
  	Adding Area for each region.
  	"""
	areas =   []
	for la,lo in zip(lats,lons):
		try:	areas.append(self.dataAreaDict[(la,lo)] )
		except: areas.append(0.)
	return 	np.ma.array(areas)			
 	


	
  def makePlots(self):
	if self.debug: print "profileAnalysis:\t makePlots."	  


	#####
	# create a dictionary of model and data depths and layers.
  	mnc = dataset(self.modelFiles[-1],'r')		
	modelZcoords = {i:z for i,z in enumerate(mnc.variables[self.modelcoords['z']][:])}
  	mnc.close()  

	if self.dataFile:
	  	dnc = dataset(self.dataFile,'r')
                if self.debug: print "profileAnalysis:\t makePlots\tOpening", self.dataFile	
	  	dataZcoords = {i:z for i,z in enumerate(dnc.variables[self.datacoords['z']][:])}
                if self.debug: print "profileAnalysis:\t makePlots\tOpened", self.dataFile

                if self.debug: print "profileAnalysis:\t makePlots\tloaded", dataZcoords
	  	dnc.close()  	
	else: 	dataZcoords = {}

	#####
	# Hovmoeller plots
	for r in self.regions:
	    for m in self.metrics: 
	    	if m not in ['mean','median','min','max',]:continue
		if self.debug: print "profileAnalysis:\t makePlots\t",r,m
	   	#####
	   	# Load data layers:
		data = {}
		if self.dataFile:		
	  	    for l in self.dlayers:
	  		#print "Hovmoeller plots:",r,m,l
	  		
	  		if type(l) == type('str'):continue	# no strings, only numbered layers.
	  		if l > max(dataZcoords.keys()): continue
	  		
			data[l] = self.dataD[(r,l,m)]	
			
		
				

	   	#####
	   	# Load model layers:
		modeldata = {}	   	
	  	for l in self.mlayers:
	  		if type(l) == type('str'):continue	# no strings, only numbered layers.
	  		if l > max(modelZcoords.keys()): continue
			modeldata[l] = {}
			for t in sorted(self.modeldataD[(r,l,m)]):
		    		if t < self.timerange.min():continue
		    		if t > self.timerange.max():continue	
				modeldata[l][t] = self.modeldataD[(r,l,m)][t]

			
                if self.debug: print "profileAnalysis:\tmakePlots:\tHovmoeller plots:",r,m,'\tloaded model data'
	
			
		
		#####
		# check that multiple layers were requested.
		#if len(data.keys())<1: continue
		if len(modeldata.keys())<1: continue
	


		title = ' '.join([getLongName(t) for t in [r,m,self.dataType]])	
		
		profilefn =  self.plotname([r,m,'profile'])
		#bvp.folder(self.imageDir)+'_'.join([self.model, self.scenario, self.jobID,r, m, self.dataType,'profile'])+'.png'		
	    	#profilefn = bvp.folder(self.imageDir)+'_'.join([,self.jobID,self.dataType,r,m,])+'.png'
	    	axislabel = getLongName(self.modeldetails['name'])+', '+getLongName(self.modeldetails['units'])
		if  bvp.shouldIMakeFile([self.shelvefn, self.shelvefn_insitu],profilefn,debug=False):					    	
			tsp.profilePlot(modeldata,data,profilefn, modelZcoords = modelZcoords, dataZcoords= dataZcoords, xaxislabel = axislabel,title = title,)			
			
		if self.doHov:	
			hovfilename =  self.plotname([r,m,'profilehov'])		
			#hovfilename =  bvp.folder(self.imageDir)+'_'.join([self.model, self.scenario, self.jobID,r, m, self.dataType,'profilehov'])+'.png'				
		    	#hovfilename = bvp.folder(self.imageDir)+'_'.join(['profilehov',self.jobID,self.dataType,r,m,])+'.png'
			if  bvp.shouldIMakeFile([self.shelvefn, self.shelvefn_insitu],hovfilename,debug=False):				
				tsp.hovmoellerPlot(modeldata,data,hovfilename, modelZcoords = modelZcoords, dataZcoords= dataZcoords, title = title,zaxislabel =axislabel, diff=False)		
	
		    	#hovfilename_diff = bvp.folder(self.imageDir)+'_'.join(['profileDiff',self.jobID,self.dataType,r,m,])+'.png'
			hovfilename_diff =  self.plotname([r,m,'profileDiff'])				    	
			#hovfilename_diff =  bvp.folder(self.imageDir)+'_'.join([self.model, self.scenario, self.jobID, r, m, self.dataType,'profileDiff'])+'.png'
			if  bvp.shouldIMakeFile([self.shelvefn, self.shelvefn_insitu],hovfilename_diff,debug=False):					    	
				tsp.hovmoellerPlot(modeldata,data,hovfilename_diff, modelZcoords = modelZcoords, dataZcoords= dataZcoords, title = title,zaxislabel =axislabel,diff=True)		
	


  def plotname(self,ls):
	pn = bvp.folder(self.imageDir)
	listt = [self.model, self.scenario, self.jobID,	self.dataType,]
	listt.extend(ls)
	pn += '_'.join(listt)+'.png'
	return pn
			
			
			
