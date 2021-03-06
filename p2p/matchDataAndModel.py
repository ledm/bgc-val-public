#!/usr/bin/ipython 
#
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
.. module:: matchDataAndModel
   :platform: Unix
   :synopsis: A tool to make matched 1D model-data arrays for point to point analysis.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""


from sys import argv
from os.path import exists,split, getmtime, basename
from glob import glob
from shelve import open as shOpen
from shutil import copy2
from math import radians, cos, sin, asin, sqrt
#from netCDF4 import Dataset
from bgcvaltools.dataset import dataset
from datetime import datetime
import numpy as np

######
# local imports
from bgcvaltools import bgcvalpython as bvp 
from bgcvaltools.extractLayer import extractLayer

#####	
# These are availalble in the module:
#	https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/netcdf_manip
from bgcvaltools.pruneNC import pruneNC
from bgcvaltools.convertToOneDNC import convertToOneDNC
from bgcvaltools.mergeNC import mergeNC
from bgcvaltools.changeNC import changeNC, AutoVivification


#TO DO
#	This still requires the netcdf_manip library, the ORCA1bathy file

class matchDataAndModel:
  """	matchDataAndModel: 
  	This code takes the real data from in situ  measurments in netcdf format and the Model data and created two 1D matched netcdfs. 
	The 1D matched netcdfs are then used to make plots and perform statistical analysis (not in this code).
	The first step is to produce lightweight "pruned" versions of the files, which have the unused fields stripped out.
	Some of the datasets are too large to run this code on desktop machine, so in those cases we request a specific layer, ie "Surface".
	Debug: prints more statements.
  """


  def __init__(self,	DataFile,
  			ModelFile, 
  			dataType = '', 
  			workingDir = '',
  			modelcoords = '',
  			modeldetails = '',
  			datacoords = '',
  			datadetails = '', 
  			datasource = '',
  			model = '', 
  			jobID = '', 
  			scenario='',
  			year = '', 
  			layer = '', 
  			grid = 'ORCA1', 
  			gridFile = '', 
  			debug = True,
  			clean = False,):

	if debug:
		print "matchDataAndModel:\tINFO:\tStarting matchDataAndModel"
		print "matchDataAndModel:\tINFO:\tData file:  \t",DataFile
		print "matchDataAndModel:\tINFO:\tModel file: \t",ModelFile
		print "matchDataAndModel:\tINFO:\tData Type:  \t",dataType
			
	self.DataFile =DataFile
	self.ModelFile = ModelFile 
	
	
	# details about coordinates and what to load.
  	self.modelcoords	= modelcoords
  	self.modeldetails 	= modeldetails
  	self.datacoords 	= datacoords
  	self.datadetails 	= datadetails

	self.DataVars		= self.datadetails['vars']		
	self.ModelVars		= self.modeldetails['vars']	
	
	# meta data:
	self.dataType = dataType
	self.datasource = datasource
	self.model = model 
	self.jobID = jobID 
	self.scenario=scenario
	self.year = year
	self.layer = layer
	self.debug = debug	
	self.clean = clean

	self._meshLoaded_ = False
	
	if not self.datasource:
		raise AssertionError("matchModelToData:\tUnable to determine observational data source:\""+ self.datasource+"\"" + \
				     "\n\t\tYou need to add datasource option to your config.ini file in the ["+self.dataType+"] section")
	
	if debug: print  "matchDataAndModel:\tINFO:\t",self.dataType, '\tModelfile:', self.ModelFile
		
	self.compType= 'MaredatMatched-'+self.model+'-'+self.jobID+'-'+self.year
		
	if workingDir =='':
		self.workingDir = bvp.folder('/data/euryale7/scratch/ledm/ukesm_postProcessed/ukesm/outNetCDF/'+'/'.join([self.compType,self.dataType+self.layer]) )
	else: 	self.workingDir = workingDir	
	self.grid = grid
	if gridFile =='':
		self.gridFile = bvp.getGridFile(grid)
	else:	self.gridFile = gridFile
	print "matchDataAndModel:\tINFO:\tGrid:  \t",grid			
	print "matchDataAndModel:\tINFO:\tGrid File:  \t",gridFile
	
	self.matchedShelve 	= bvp.folder(self.workingDir)+self.model+'-'+self.jobID+'_'+self.year+'_'+self.dataType+'_'+self.layer+'_matched.shelve'
	self.matchesShelve 	= bvp.folder(self.workingDir)+self.model+'-'+self.jobID+'_'+self.year+'_'+self.dataType+'_'+self.layer+'_matches.shelve'
	
	self.workingDirTmp 	= bvp.folder(self.workingDir+'tmp')
	self.DataFilePruned	= self.workingDirTmp+'Data_' +self.dataType+'_'+self.layer+'_'+self.model+'-'+self.jobID+'-'+self.year+'_pruned.nc'
	self.ModelFilePruned	= self.workingDirTmp+'Model_'+self.dataType+'_'+self.layer+'_'+self.model+'-'+self.jobID+'-'+self.year+'_pruned.nc'	
	
	self.DataFile1D  	= self.workingDirTmp + basename(self.DataFilePruned).replace('pruned.nc','1D.nc') 
	self.maskedData1D	= self.workingDir    + basename(self.DataFile1D)
	self.Model1D     	= self.workingDir    + basename(self.ModelFilePruned).replace('pruned.nc','1D.nc')

	self.MatchedModelFile 	= self.Model1D
	self.MatchedDataFile  	= self.maskedData1D
	self.run()


	
  def run(self,):
	"""There are two methods written for manipulating data.
	   One is designed to work with WOA formats, the other with MAREDAT formats.
	   Other data formats are run manually.
	"""
	if not bvp.shouldIMakeFile(self.DataFile,self.MatchedDataFile,debug=False) and not bvp.shouldIMakeFile(self.ModelFile,self.MatchedModelFile,debug=False):
		print "matchDataAndModel:\trun:\talready created:\t",self.maskedData1D, '\n\t\t\tand\t',self.MatchedModelFile
		return
	self._calculateModelYearIndex_()
	self._pruneModelAndData_()	
	self._convertDataTo1D_()	
	self._matchModelToData_()
	self._convertModelToOneD_()
	self._applyMaskToData_()

  def _calculateModelYearIndex_(self,):
   	""" 
   	This function determines which index to use to extract a single time slice from the model file.
  	""" 
  	  	
  	modeltimes = bvp.getTimes(self.ModelFile, self.modelcoords)
  	year = float(self.year)
  	if int(year) == float(year):
 	 	targettime = year+0.5 # mid point of the year
 	else: 	targettime = year
 	modeltimeIndex = bvp.getclosesttime(targettime,modeltimes)
 	if modeltimeIndex == -1: 
 		self.modeltimeIndex = None
 	else: 	self.modeltimeIndex = modeltimeIndex
 	if self.debug:print "calculateModelYearIndex: ",modeltimeIndex, self.modeltimeIndex
  
  def _pruneModelAndData_(self,):
   	""" This routine reduces the full 3d netcdfs by pruning the unwanted fields.
  	""" 
  	
	if bvp.shouldIMakeFile(self.ModelFile,self.ModelFilePruned,debug=False):
		print "matchDataAndModel:\tpruneModelAndData:\tMaking ModelFilePruned:", self.ModelFilePruned
		p = pruneNC(self.ModelFile,self.ModelFilePruned,self.ModelVars, timeindex =self.modeltimeIndex ,  timemean=False, debug = self.debug)
			
	else:	
		print "matchDataAndModel:\tpruneModelAndData:\tModelFilePruned already exists:",self.ModelFilePruned
  	 
	if bvp.shouldIMakeFile(self.DataFile,self.DataFilePruned,debug=False):
		print "matchDataAndModel:\tpruneModelAndData:\tMaking DataFilePruned:", self.DataFilePruned
		p = pruneNC(self.DataFile,self.DataFilePruned,self.DataVars, debug = self.debug) 	
	else:	
		print "matchDataAndModel:\tpruneModelAndData:\tDataFilePruned already exists:",self.DataFilePruned
	 


  def _convertDataTo1D_old(self,):
   	""" 
   		This routine reduces the In Situ data into a 1D array of data with its lat,lon,depth and time components.
  	"""
		
	if not bvp.shouldIMakeFile(self.DataFilePruned,self.DataFile1D,debug=False):
		print "matchDataAndModel:\tconvertDataTo1D:\talready exists: (DataFile1D):\t",self.DataFile1D
		return

	print "matchDataAndModel:\tconvertDataTo1D:\topening DataFilePruned:\t",self.DataFilePruned		

	nc = dataset(self.DataFilePruned,'r')
		
	if self.layer == '':
		print 'matchDataAndModel:\tconvertDataTo1D:\tNo depth level cut or requirement',self.DataFilePruned,'-->',self.DataFile1D
	  	if len(self.DataVars):	convertToOneDNC(self.DataFilePruned, self.DataFile1D, debug=True, variables = self.DataVars)
	  	else:			convertToOneDNC(self.DataFilePruned, self.DataFile1D, debug=True)
	  	nc.close()	  	
	  	return
	  	
	  	
	if self.datacoords['z'] in ['', None,"''"]:
		print 'matchDataAndModel:\tconvertDataTo1D:\tNo data depth level coordinate',self.dataType
		convertToOneDNC(self.DataFilePruned, self.DataFile1D, debug=True, variables = self.DataVars)
		nc.close()
		return
	
	mmask = np.ones(nc.variables[self.DataVars[0]].shape)	  
			
	if self.layer in ['Surface','100m','200m','500m','1000m','2000m',]:	
		print 'matchDataAndModel:\tconvertDataTo1D:\tSlicing along depth direction.'	
		if self.layer == 'Surface':z = 0.
		if self.layer == '100m': 	z = 100.			
		if self.layer == '200m': 	z = 200.
		if self.layer == '500m': 	z = 500.
		if self.layer == '1000m': 	z = 1000.
		if self.layer == '2000m': 	z = 2000.
		
		print self.datacoords['z']
		if nc.variables[self.datacoords['z']].ndim ==1:
			k =  bvp.getORCAdepth(np.abs(z),np.abs(nc.variables[self.datacoords['z']][:]),debug=True)
			mmask[:,k,:,:] = 0
		else:
			####
			# Depth field is the wrong number of dimensions.
			print 'matchDataAndModel:\tconvertDataTo1D:\tDepth field is the wrong shape:', nc.variables[self.datacoords['z']].shape	
			assert 0
			
					
	elif self.layer in ['ATransect','PTransect','SOTransect','Equator','ArcTransect','AntTransect','CanRusTransect']:
		print 'matchDataAndModel:\tconvertDataTo1D:\tSlicing along ',self.layer,' direction.'			
		####
		# Create a lines, then produce a mask along that line.
		lats = nc.variables[self.datacoords['lat']][:]
		lons =  bvp.makeLonSafeArr(nc.variables[self.datacoords['lon']][:])
		
		if (lats.ndim,lons.ndim) ==(1,1):
			lon2d,lat2d = np.meshgrid(lons,lats)
		else:	lon2d,lat2d = lons,lats

		mask2d = np.ones_like(lon2d)

		if self.layer == 'ATransect':
			numpoints = 500
			lon = bvp.makeLonSafe(-28.) # W
			minlat = -89.
			maxlat = 89.99
			transectcoords = [(minlat +i*(maxlat-minlat)/numpoints,lon)  for i in np.arange(numpoints)]# lat,lon
			

		if self.layer == 'PTransect':
			numpoints = 500
			lon = bvp.makeLonSafe(200.) # E
			minlat = -89.
			maxlat = 89.99
			transectcoords = [(minlat +i*(maxlat-minlat)/numpoints,lon)  for i in np.arange(numpoints)]# lat,lon
			
		if self.layer == 'SOTransect':
			numpoints = 5000
			lonmin = -360. # E
			lonmax = +360. # E			
			lat = -60.
			transectcoords = [(lat, minlon +i*(maxlon-minlon)/numpoints)  for i in np.arange(numpoints)]# lat,lon
			
		if self.layer == 'Equator':
			numpoints = 5000
			lonmin = -360. # E
			lonmax = +360. # E			
			lat = -0.
			transectcoords = [(lat, minlon +i*(maxlon-minlon)/numpoints)  for i in np.arange(numpoints)]# lat,lon
			
		if self.layer == 'ArcTransect':
			numpoints = 300
			lon = bvp.makeLonSafe(0.)
			minlat = 50.
			maxlat = 90.
			transectcoords = [(minlat +i*(maxlat-minlat)/numpoints,lon)  for i in np.arange(numpoints)]# lat,lon

			lon = -165.
			minlat = 60.
			maxlat = 90.
			transectcoords.extend([(minlat +i*(maxlat-minlat)/numpoints,lon) for i in np.arange(numpoints)])# lat,lon
			
		if self.layer == 'CanRusTransect':
			numpoints = 300
			lon = bvp.makeLonSafe(83.5)
			minlat = 65.
			maxlat = 90.
			transectcoords = [(minlat +i*(maxlat-minlat)/numpoints,lon)  for i in np.arange(numpoints)]# lat,lon

			lon = bvp.makeLonSafe(-96.)
			minlat = 60.
			maxlat = 90.
			transectcoords.extend([(minlat +i*(maxlat-minlat)/numpoints,lon) for i in np.arange(numpoints)])# lat,lon
		
		if self.layer == 'AntTransect':
			numpoints = 500
			lon = 0.
			minlat = -89.9
			maxlat = -40.
			transectcoords = [(minlat +i*(maxlat-minlat)/numpoints,lon)  for i in np.arange(numpoints)]# lat,lon
	


		
		for (lat,lon) in sorted(transectcoords):
			la,lo = bvp.getOrcaIndexCC(lat, lon, lat2d, lon2d, debug=True,)
			mask2d[la,lo] = 0
		
		if mmask.ndim == 4:
			mshape = mmask.shape 
			mmask = np.tile(mask2d,(mshape[0],mshape[1],1,1))
			
		if mmask.ndim == 3:
			mshape = mmask.shape 
			mmask = np.tile(mask2d,(mshape[0],1,1))	
		
		if mmask.shape != mshape:
			print 'matchDataAndModel:\tERROR:\tconvertDataTo1D:\t',self.layer,'\tMaking mask shape:',mmask.shape
			assert 0 

	if mmask.min()==1:
		print 'matchDataAndModel:\tERROR:\tconvertDataTo1D:\t',self.layer,'\tNo data in here.'
		return 
			  	
	mmask +=nc.variables[self.DataVars[0]][:].mask
	print 'matchDataAndModel:\tconvertDataTo1D:\t',self.layer,'\tMaking mask shape:',mmask.shape		
	print 'matchDataAndModel:\tconvertDataTo1D:\t',self.layer,'\tMaking flat array:',self.DataFilePruned,'-->',self.DataFile1D	
	
	convertToOneDNC(self.DataFilePruned,self.DataFile1D ,newMask=mmask, variables = self.DataVars, debug=True)

  	nc.close()
  	
  		
	
  def _convertDataTo1D_(self,):
   	""" 
   		This routine reduces the In Situ data into a 1D array of data with its lat,lon,depth and time components.
  	"""
		
	if not bvp.shouldIMakeFile(self.DataFilePruned,self.DataFile1D,debug=False):
		print "matchDataAndModel:\tconvertDataTo1D:\talready exists: (DataFile1D):\t",self.DataFile1D
		if not self.clean: return

	print "matchDataAndModel:\tconvertDataTo1D:\topening DataFilePruned:\t",self.DataFilePruned		

	nc = dataset(self.DataFilePruned,'r')
		
	if self.layer == '':
		print 'matchDataAndModel:\tconvertDataTo1D:\tNo depth level cut or requirement',self.DataFilePruned,'-->',self.DataFile1D
	  	if len(self.DataVars):	convertToOneDNC(self.DataFilePruned, self.DataFile1D, debug=True, variables = self.DataVars)
	  	else:			convertToOneDNC(self.DataFilePruned, self.DataFile1D, debug=True)
	  	nc.close()	  	
	  	return
	  	
	  	
	if self.datacoords['z'] in ['', None,"''"]:
		print 'matchDataAndModel:\tconvertDataTo1D:\tNo data depth level coordinate',self.dataType
		convertToOneDNC(self.DataFilePruned, self.DataFile1D, debug=True, variables = self.DataVars)
		nc.close()
		return
	
	mmask =  extractLayer(nc,self.datacoords,self.datadetails,self.layer,data = '',maskWanted=True)	
			  	
	mmask +=nc.variables[self.DataVars[0]][:].mask
	print 'matchDataAndModel:\tconvertDataTo1D:\t',self.layer,'\tMaking mask shape:',mmask.shape		
	print 'matchDataAndModel:\tconvertDataTo1D:\t',self.layer,'\tMaking flat array:',self.DataFilePruned,'-->',self.DataFile1D	
	
	convertToOneDNC(self.DataFilePruned,self.DataFile1D ,newMask=mmask, variables = self.DataVars, debug=True)

  	nc.close()
  	
  		
		
  	
  def _matchModelToData_(self,):
  	print "matchModelToData:\tOpened MAREDAT netcdf:", self.DataFile1D
  	
  	ncIS = dataset(self.DataFile1D,'r')
  	#ncIS = ncdfView(self.DataFile1D,Quiet=True)  	
	is_i	= ncIS.variables['index'][:]
	
	try:
		if self.clean: assert 0
		s = shOpen(self.matchedShelve)
		maxIndex = s['maxIndex']
		self.maremask = s['maremask']
		self.matches = s['matches']
		self.imatches = s['imatches']		
		s.close()		
		print "matchModelToData:\tOpened shelve:", self.matchedShelve
		print "matchModelToData:\tStarting from maxindex:",maxIndex," and ",len(self.matches), " already matched. Mask:",self.maremask.sum()
	except:
		self.matches = {}
		self.imatches = {}
		maxIndex = 0
		self.maremask = np.zeros(is_i.shape) # zero array same length as in situ data.

		print "matchModelToData:\tStarting from maxindex",maxIndex,"\tfinished:",len(self.matches), " already matched. Mask:",self.maremask.sum()
		print "matchModelToData:\tCreating shelve:", self.matchedShelve

	try:
		if self.clean: assert 0	
		s = shOpen(self.matchesShelve)		
		lldict  = s['lldict']
		s.close()
	except:
		lldict={}
	finds = 0	
	
	#####
	# Figure out which type of data this is.
	#self.ytype = []
	#Models = [m.upper() for m in ['Diat-HadOCC', 'ERSEM','HadOCC', 'MEDUSA','PlankTOM6','PlankTOM10','NEMO','IMARNET','CMIP5',]] # skip these to find in situ data types.
	#Models.extend(['IMARNET_' +m.upper() for m in ['Diat-HadOCC', 'ERSEM','HadOCC', 'MEDUSA','PlankTOM6','PlankTOM10','NEMO',]])	
	#Models.extend(['CMIP5_' +m.upper() for m in CMIP5models])		
	#for key in mt.keys():
	#	#key = key.upper()
	#	if key.upper() in Models:continue
	#	try:
	#		if self.dataType in mt[key].keys() and key not in self.ytype:
	#			self.ytype.append(key)
	#	except:pass

	#####
	# Check if there is any data left to match. 
	# This makes it easier to stop and start the longer analyses.
	if maxIndex+1 >=len(is_i):
		ncIS.close()
		print "matchModelToData:\tNo need to do further matches, Finsished with ",maxIndex+1,"\tfinished:",len(self.matches)
		return 		
		
	#if maxIndex+1 <len(is_i):
	zdict={}
	tdict={}
  	is_t		= ncIS.variables[self.datacoords['t']][:]
  	is_index_t	= ncIS.variables['index_t'][:]  	
  	
	if self.datacoords['z']  in ['', None,"''"]:  	pass		# No Depth in data file.
	else:  	is_z 	= ncIS.variables[self.datacoords['z']][:]
  	is_la	= ncIS.variables[self.datacoords['lat']][:]
	is_lo 	= bvp.makeLonSafeArr(ncIS.variables[self.datacoords['lon']][:])

	tdict   = self.datacoords['tdict']
	if is_index_t.min() == is_index_t.max():
		#tdict[is_index_t.min()] = is_t.min()
		print is_t.min() #, tdict[is_t.min()]
		#if np.ma.is_masked(is_t.min()): pass
		#else:
		tdict[is_t.min()]	= is_index_t.min()
		
	#tdict   = {i:i for i in xrange(12)}
	ncIS.close()	     


	print "tdict:", tdict
	#####
	# This list could be removed by adding a check dimensionality of data after it was been pruned.	
	#flatDataOnly =  ['pCO2','seawifs','Seawifs','mld_DT02', 'mld_DR003','mld_DReqDTm02','mld',
	#		  'dms_and','dms_ara','dms_hal','dms_sim',]
	#for d in ['dms_p_and','dms_p_ara','dms_p_hal','dms_p_sim',]:
	#  for i in ['','1','2']:
	#	flatDataOnly.append(d+i)
		
	#if self.dataType in flatDataOnly: 
  	#   	is_z 	= np.ma.zeros(len(is_t))[:]
	#   	zdict = {0:0, 0.:0}  

	if not self._meshLoaded_:self.loadMesh()
	    
	for i,ii in enumerate(is_i[maxIndex:]):
		i+=maxIndex
		wt  = is_t[i]
		wt_index  = is_index_t[i]
		try:	wz  = is_z[i]
		except:	wz = 0
		wla = is_la[i]
		wlo = is_lo[i] 

		#####		
		# Match Latitude and Longitude
		try:
			la,lo = lldict[(wla,wlo)]
		except:
			la,lo = self.getOrcaIndexCC(wla,wlo,i=i,debug=False)
			if la == lo == -1:
				print "STRICT ERROR: Could not find, ",wla,wlo
				continue
			lldict[(wla,wlo)] = la,lo
			finds+=1

			if self.debug and i%10000==0:
			    print "matchModelToData:\t",i,'New match:\tlon:',[wlo,self.loncc[la,lo]],'\tlat:',[wla,self.latcc[la,lo]],[finds,len(lldict)]

			if abs(self.latcc[la,lo] - wla)>90.: 
			    print "Come again? this should never happen:",self.latcc[la,lo],  wla
			    print "matchModelToData:\t",i,'New match:\tlon:',[wlo,self.loncc[la,lo]],'\tlat:',[wla,self.latcc[la,lo]],[finds,len(lldict)]
			    assert False
			    
		#####
		#Match Depth
		try:
			z = zdict[wz]
		except:	 
			z = bvp.getORCAdepth(wz,self.depthcc,debug=True)
			zdict[wz]	= z
			if self.debug: print "matchModelToData:\t",i, 'Found new depth:',wz,'m-->',self.depthcc[z], ['z=',z]

		#####			
		#Match Time	
		try: 
			t = tdict[wt_index]
		except:
			try:
				t = tdict[wt]	
			except:
				print "matchModelToData:\tunable to find time match in longnames, mt[",self.dataType,"]['tdict']", wt
				print "tdict:",tdict
				assert False 
			
				t = getMonthFromSecs(wt)
				tdict[wt] = t
				if self.debug:	print "matchModelToData:\t",i, 'Found new month:', wt, '-->',t

		#####
		# Add match into array
		try:
			tmp = self.matches[(t,z,la,lo)][0]
			self.matches[(t,z,la,lo)].append(i)
			self.imatches[i] = (t,z,la,lo)
			self.maremask[i] = tmp
			#if self.debug: print "matchModelToData:\tWARNING:",i,[wt,wz,wla,wlo], '-->',(t,z,la,lo),'already matched', self.matches[(t,z,la,lo)]
				#for a in self.matches[(t,z,la,lo)]:
					#print '\t',i, a, self.imatches[a]
		except:
			# if this location in the model grid (t,z,la,lo) has not yet been found,
			# self.matches gets a list of all the in situ points that match that location.
			# Conversely, self.maremask's i-th value location of the first time it was found.
			self.matches[(t,z,la,lo)]=[i,]
			self.imatches[i] = (t,z,la,lo)			
			self.maremask[i] = i
			#if self.debug: print "matchModelToData:\tfirst match:",i,[wt,wz,wla,wlo], '-->',(t,z,la,lo)
		
		#####
		# test match up:
		fail=0
		if abs(wz-self.depthcc[z]) >500.:
			print 'depth DOESNT MATCH:',wz,self.depthcc(z)
			fail+=1
		# These tests are already done in getOrcaIndexCC. No need to be done twice.
		#if abs(wla-self.latcc[la,lo]) >2.:
		#	print 'Latitude DOESNT MATCH:',wla, self.latcc[la,lo]
		#	fail+=1		
		#if abs(wlo-self.loncc[la,lo]) >2.:
		#	print 'Longitude DOESNT MATCH:',wlo,self.loncc[la,lo]
		#	fail+=1						
		if fail>0:assert False
		
		
		#####			
		#increment by 1 to save/ end, as it has finished, but i is used as a starting point.
		i+=1
		if i%10000==0:
			if self.debug: print "matchModelToData:\t", i,ii,self.dataType,self.layer,':\t',[wt,wz,wla,wlo] ,'--->',[t,z,la,lo]
			
		if i>1 and i%50000000==0:
			if self.debug: print "matchModelToData:\tSaving Shelve: ", self.matchedShelve
			s = shOpen(self.matchedShelve)
			s['matches']  = self.matches
			s['maxIndex'] = i
			s['maremask'] = self.maremask	
			s['imatches']  = self.imatches
			s.close()
			s = shOpen(self.matchesShelve)		
			s['lldict'] = lldict 
			s.close()				
	maxIndex = i
	#assert False
		
	print "matchDataAndModel:\tSaving Shelve", self.matchedShelve	
	s = shOpen(self.matchedShelve)
	s['matches']  = self.matches
	s['imatches']  = self.imatches	
	s['maxIndex'] = i
	s['maremask'] = self.maremask
	s.close()
	    
	s = shOpen(self.matchesShelve)		
	s['lldict'] = lldict 
	s.close()
	print "matchModelToData:\tFinsished with ",maxIndex+1,"\tfinished:",len(self.matches) #, "Mask:",self.maremask.sum()
	
	
  def _convertModelToOneD_(self,):
	if not bvp.shouldIMakeFile(self.ModelFilePruned,self.Model1D,debug=True):
		print "convertModelToOneD:\tconvertModelToOneD:\talready exists:",self.Model1D
		if not self.clean: return
	
	print "convertModelToOneD:\tconvertModelToOneD:\tMaking 1D Model file:", self.ModelFilePruned,'-->', self.Model1D
  	convertToOneDNC(self.ModelFilePruned, self.Model1D,newMask='',debug=self.debug,dictToKeep=self.matches)




  def _applyMaskToData_(self,):
  	""" This routine applies the mask of the model to the data. 
  	    It is needed because there are some points where two WOA grid cells fall into the same ORCA1 grid, these excess points should be meaned/medianed.
  	    Similarly, some data points fall into a masked grid cell in the model and need to be masked in the data.
  	"""
	
	if not bvp.shouldIMakeFile(self.ModelFilePruned,self.maskedData1D,debug=True):
		print "applyMaskToData:\tapplyMaskToData:\t", "already exists:",self.maskedData1D
		if not self.clean: return
		
	maremask = self.maremask #np.array([int(a) for a in self.maremask] )
		# zero shouldn't happen
		# some number:
			# need to take the median value of for everytime that the same number appears.
			
	maremaskDict={}
	for i,m in enumerate(maremask):
		try:	maremaskDict[m].append(i)
		except:	maremaskDict[m] = [i,]
	def getMedianVal(arr):
		print "applyMaskToData:\tgetMedianVal: 1d:",arr.shape,maremask.shape,'-->',
		out = []
		
		for m in sorted(maremaskDict.keys()):
		    out.append(np.median([arr[i] for i in maremaskDict[m] ]))	
		arr= np.array(out).squeeze()
		print arr.shape
		return arr

	def getMeanVal(arr):
		print "applyMaskToData:\tgetMeanVal: 1d:",arr.shape,maremask.shape,'-->',
		out = []
		
		for m in sorted(maremaskDict.keys()):
		    out.append(np.mean([arr[i] for i in maremaskDict[m] ]))	
		arr= np.array(out).squeeze()
		print arr.shape
		return arr

	def getFirstVal(arr):
		print "\napplyMaskToData:\tgetFirstVal: 1d:",arr.shape,maremask.shape,len(maremaskDict.keys()),'-->',
		out = []
		for m in sorted(maremaskDict.keys()):
		    out.append(arr[maremaskDict[m]][0])	
		    
		arr= np.array(out).squeeze()
		print arr.shape
		return arr
						
	def applyMask(arr):
		print "applyMask: 1d:",arr.shape,maremask.shape,'-->',
		out = []
		for i,m in enumerate(maremask):
			if not m: continue
			out.append(arr[i])	
		arr= np.array(out).squeeze()
		print arr.shape
		return arr
		

  	ncIS = dataset(self.DataFile1D,'r')		
  	#ncIS = ncdfView(self.DataFile1D,Quiet=True)		
	av = AutoVivification()
	for v in ncIS.variables.keys():
		if ncIS.variables[v].ndim != 1: 
			if self.debug: print "matchDataAndModel:\tapplyMaskToData:\tERROR:\tthis is suppoed to be the one D file"
			assert False
		print  "matchDataAndModel:\tapplyMaskToData:AutoViv:", v ,len(ncIS.variables[v][:]), len(self.maremask)
		if len(ncIS.variables[v][:])== len(self.maremask):
			if self.debug: print  "matchDataAndModel:\tapplyMaskToData:AutoViv:", v ,'is getting a mask.'
			av[v]['convert'] = getMedianVal
			#av[v]['convert'] = getMeanVal			
			#av[v]['convert'] = getFirstVal			
						
	ncIS.close()
	
	if self.debug: 
		print "matchDataAndModel:\tapplyMaskToData:\tNEW MASK for 1D Maredat:",maremask.shape, maremask.sum(), maremask.size, maremask.size-maremask.sum()
		print "matchDataAndModel:\tapplyMaskToData:\tMaking 1D Maredat file:", self.DataFile1D,'-->', self.maskedData1D
		
	c = changeNC(self.DataFile1D, self.maskedData1D,av,debug = self.debug)
	

  def loadMesh(self,):
      	# This won't work unless its the 1 degree grid.
      	#f self.ORCA == "ORCA1":
 	print "matchModelToData:\tOpened Model netcdf mesh.", self.grid, '(',self.gridFile,')'
  	ncER = dataset(self.gridFile,'r')
  	
  	#ncER = ncdfView("data/mesh_mask_ORCA1_75.nc",Quiet=True)
  	#if 'nav_lat' in ncER.variables.keys():	self.latcc    = ncER.variables['nav_lat'][:].squeeze()
	#elif 'lat' in ncER.variables.keys():	self.latcc    = ncER.variables['lat'][:].squeeze()
	#else:					
	self.latcc    = ncER.variables[self.modelcoords['lat']][:].squeeze()
	
  	#if 'nav_lon' in ncER.variables.keys():	self.loncc    = bvp.makeLonSafeArr(ncER.variables['nav_lon'][:].squeeze())
	#elif 'lon' in ncER.variables.keys():	self.loncc    = bvp.makeLonSafeArr(ncER.variables['lon'][:].squeeze())
	#else:
	self.loncc    = bvp.makeLonSafeArr(ncER.variables[self.modelcoords['lon']][:].squeeze())

  	#if 'deptht' in ncER.variables.keys():	self.depthcc  = ncER.variables['deptht'][:].squeeze()
	#elif 'gdept_0' in ncER.variables.keys():self.depthcc  = ncER.variables['gdept_0'][:].squeeze()
	#elif 'lev' in ncER.variables.keys():	self.depthcc  = ncER.variables['lev'][:].squeeze()	
	#else:					
	self.depthcc  = ncER.variables[self.modelcoords['z']][:]	
	
	if self.loncc.ndim ==1 and  self.loncc.shape!= self.latcc.shape:
		self.loncc,self.latcc = np.meshgrid(self.loncc,self.latcc)
			
	ncER.close()
 	print "matchModelToData:\tloaded mesh.", self.grid, 'lat:',self.latcc.shape, 'lon:',self.loncc.shape,'depth:',self.depthcc.shape
	self._meshLoaded_ = 1
	
  def getOrcaIndexCC(self,lat,lon,debug=True,slowMethod=False,i=''):#llrange=5.):
	""" takes a lat and long coordinate, an returns the position of the closest coordinate in the NemoERSEM grid.
	    uses the bathymetry file.
	"""
	km = 10.E20
	la_ind, lo_ind = -1,-1
	latrangeCutoff=2.
	lonrangeCutoff=5.
	lat = bvp.makeLatSafe(lat)
	lon = bvp.makeLonSafe(lon)	
	
	if not self._meshLoaded_:self.loadMesh()
	#if abs(lat) <70.:
	c = (self.latcc - lat)**2 + (self.loncc - lon)**2
	#else:   c =  myhaversineArr(lon,lat,self.loncc,self.latcc)
		

	(la_ind,lo_ind) =  np.unravel_index(c.argmin(),c.shape)

	#km2 = abs(haversine((lon, lat), (locc,lacc)))
	if debug: print 'location ', [la_ind,lo_ind],'(',self.latcc[la_ind,lo_ind],self.loncc[la_ind,lo_ind],') is closest to:',[lat,lon]
	"""if abs(self.latcc[la_ind,lo_ind] -lat ) > latrangeCutoff or abs(self.loncc[la_ind,lo_ind] -lon ) > lonrangeCutoff:
		d = myhaversine(self.loncc[la_ind,lo_ind],self.latcc[la_ind,lo_ind],lon,lat)
		print "getOrcaIndexCC:\t",i,"\tERROR:\tDISTANCE IS VERY FAR:",[self.latcc[la_ind,lo_ind],'-->',  lat,], [self.loncc[la_ind,lo_ind], '-->', lon],'distance:',d
		if d>350.:
			print "getOrcaIndexCC:\t",i,"\tdistance too great:",d, 
			#assert False
			return -1,-1
	"""	
	return la_ind,lo_ind
		

#########################################
# Trimming masked values out of 1d files:


	
#########################################
# Coords and Depth:
def myhaversine(lon1, lat1, lon2, lat2):
	"""
	    Calculate the great circle distance between two points 
	    on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2.)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.)**2
	c = 2. * asin(sqrt(a)) 
	km = 6367. * c
	return km 

def myhaversineArr(lon1, lat1, lonarr, latarr):
	"""
	    Calculate the great circle distance between a point and an array 
	    on the earth (specified in decimal degrees)
	"""
	kms = np.zeros(lonarr.shape)+100000. #larger than earths circumference.
	
	for index, lat2 in np.ndenumerate(latarr):
		if abs(lat2-lat1) > 5.: continue	#	 minimi
		lon2 = lonarr[index]
		if abs(makeLonSafe(lon2)-makeLonSafe(lon1)) > 5.:continue
		# convert decimal degrees to radians 
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
		# haversine formula 
		dlon = lon2 - lon1 
		dlat = lat2 - lat1 
		a = sin(dlat/2.)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.)**2
		c = 2. * asin(sqrt(a)) 
		kms[index]= 6367. * c 
		
	return np.ma.array(kms)

def quadraticDistance(lon1, lat1, lon2, lat2):
	"""
	    Calculate the flat quadratic diatance in degrees. Its a rough approximation. But the maps don't include the poles, so it's okay. 
	"""
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	return sqrt(dlon*dlon + dlat*dlat)

	
			
def makeLonSafe(lon):
	while True:
		if -180.<lon<=180.:return lon
		if lon<=-180.:lon+=360.
		if lon> 180.:lon-=360.	
			
def makeLonSafeArr(lon):
	if lon.ndim == 2:
	 for l,lon1 in enumerate(lon):
	  for ll,lon2 in enumerate(lon1):
	   lon[l,ll] = makeLonSafe(lon2)
	 return lon
	if lon.ndim == 1:
	 for l,lon1 in enumerate(lon):
	   lon[l] = makeLonSafe(lon1)
	 return lon
	 	 
	assert False		
	
	  

def getMonthFromSecs(secs):
	if int(secs/30.4) in xrange(0,12):return int(secs/30.4)
	day = int(secs/(24*60*60.))
	#very approximate
	return int(day/30.4) #returns month between 0 and 11 ...
	
	

	




def main():
	assert False
	



	

	

				

			



if __name__=="__main__":
	main() 
	print 'The end.'
