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
.. module:: extractLayer
   :platform: Unix
   :synopsis: A tool to extract a specific layer from a model
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""


from sys import argv
from os.path import exists,split, getmtime, basename
from glob import glob
from shelve import open as shOpen
from shutil import copy2
from math import radians, cos, sin, asin, sqrt
from netCDF4 import num2date,Dataset
from datetime import datetime
import numpy as np

######
# local imports
from bgcvaltools import bgcvalpython as bvp 
from alwaysInclude import depthNames
from functions.stdfunctions import extractData

	
def ApplyDepthSlice(nc,coords,details,z,data,maskWanted=False):
	"""
	This function extracted depth layer z from 
	
	"""
	zdim = determineZ(nc,coords,details)
	
	if maskWanted:
		mmask = np.ma.ones(data.shape)	  	
		if zdim == 0:	mmask[z,...] = 0
		if zdim == 1:	mmask[:,z,...] = 0
		if zdim == 2:	mmask[:,:,z,...] = 0
		if zdim == 3:	mmask[:,:,:,z,...] = 0
		return mmask
	if not maskWanted:	
		if zdim == 0:	return data[z,...]
		if zdim == 1:	return data[:,z,...]
		if zdim == 2:	return data[:,:,z,...]
		if zdim == 3:	return data[:,:,:,z,...]
	
	raise AssertionError("extractLayer:\tERROR:\tunusual layer 'type'provided: "+str(layer)+', type: '+str(type(layer)))
	

def determineZ(nc,coords,details):
	"""
	The goal of this code is to determine which dimension is depth.
	"""
	dims = nc.variables[details['vars'][0]].dimensions	
	for d,dim in enumerate(dims):
		if dim in depthNames: return d
	raise AssertionError("determineZ:\tERROR:\tNot able to find the depth in the dimensions:"+str(dims)+"\n\t\tPlease add your depth to alwaysInclude.py:depthsNames")

def drawLine(lat1,lat2,lon1,lon2,numpoints=5000):
	"""
	draw a list of points in a coordinately straight line between two points.

	"""	
	latstep = (lat2-lat1)/numpoints
	lonstep	= (lon2-lon1)/numpoints
	
	return [(lat1 + (i*latstep),lon1 + (i*lonstep))  for i in np.arange(numpoints)]
	
	
def extractLayer(nc,coords,details,layer,data = '',maskWanted=False):
	"""
	The goal of this code is to extract a dataset from the netcdf.
	It can return the extracted layer data, or as a mask.
	"""
	
	if type(nc) == type('filename'):
		nc = dataset(nc,'r')
		
	if type(data) ==type(''): 
		data = extractData(nc,details)

	dims = nc.variables[details['vars'][0]].dimensions
	if len(dims) != data.ndim:
		raise AssertionError("extractLayer:\tERROR:\tunusual layer 'type'provided: "+str(layer)+', type: '+str(type(layer))) 	
	
	#####
	# This is when a numbered specific layer is requested
	if type(layer) in [type(0),np.int64,np.int,]:
		try:	z = nc.variables[coords['z']][layer]
		except:	return []
		print "getHorizontalSlice:\tSpecific depth level requested",details['name'], z, data.shape	
		return ApplyDepthSlice(nc,coords,details,layer,data,maskWanted=maskWanted)

	#####
	# Assuming that layer is a string from now on	
	if type(layer) == type('string'):	pass
	else:	raise AssertionError("extractLayer:\tERROR:\tunusual layer 'type'provided: "+str(layer)+', type: '+str(type(layer)))

	
	#####
	# Basic fields:
	# If no layer requested.	
	if layer.lower() in ['layerless','all']:
		return data	

	#####	
	# Data is 1D or 2D
	if data.ndim == 2: return data	
	if data.ndim == 1: return data	

	
	#####
	# First checks:
	# No Depth in coordinate dictionary
	if coords['z'] == '' :
		raise AssertionError("extractLayer:\tERROR:\tno depth layer provided: "+str(coords))

	#####
	# Coordinate depth isn't in the netcdf.
	if coords['z'] not in nc.variables.keys():
		raise AssertionError("extractLayer:\tERROR:\tcoordinate "+str(coords['z'])+" not in file:"+str(nc.filename))

	#####
	# The depth netcdf has only one layer:
	if nc.variables[coords['z']][:].shape ==(1,):
		data =  data.squeeze()
		if data.ndim == 2: return data
		if data.ndim == 1: return data
		#raise AssertionError("extractLayer:\tERROR:\tcoordinate "+str(coords['z'])+" not in file:"+str(nc.filename))

	#####
	# This is when there is only one dimension in the data/model file.
	if len(nc.dimensions.keys()) == 1:
		if layer in ['Surface',]:	return np.ma.masked_where(np.abs(nc.variables[coords['z']][:])<5.,data)	# top 5 m
		if layer in ['layerless',]:	return data
		raise AssertionError("extractLayer:\tERROR:\tcoordinate "+str(coords['z'])+" not in file:"+str(nc.filename))	

	#####
	# Check if it's a custom layer request (ie 100m, 28W, etc.)
	customLayerValue = None
	customLayerType	 = None
	for z in ['m','N','E','S','W']:
		try:	customLayerValue = float(layer.replace(z, ''))
		except:	continue
		if z == 'm':	customLayerType	= 'z'
		if z == 'N':	customLayerType	= 'lat'
		if z == 'E':	customLayerType	= 'lon'
		if z == 'S':	
			customLayerType	= 'lat'
			customLayerValue *= -1.
		if z == 'W':	
			customLayerType	= 'lon'
			customLayerValue *= -1.


	if layer == 'Surface':
		customLayerType	 = 'z'
		customLayerValue = 0.

	if layer == 'Transect':
		customLayerType	 = 'lat'
		customLayerValue = -28.				
	if layer == 'PTransect':
		customLayerType	 = 'lat'
		customLayerValue = 200.		
		
	if layer == 'Equator':
		customLayerType	 = 'lon'
		customLayerValue = 0.	
	if layer == 'SOTransect':
		customLayerType	 = 'lon'
		customLayerValue = -60.			
	
	#####
	# Looking to make sure that the depth is 1D.
	if nc.variables[coords['z']][:].ndim > 1:
		raise AssertionError("extractLayer:\tERROR:\tNot ready for sigma coordinate, but add the code here!")
	
	#####
	# extract data at a specific depth:
	if customLayerType == 'z':
		k =  bvp.getORCAdepth(customLayerValue,nc.variables[coords['z']][:],debug=False)
		print "extractLayer:\tSpecific depth field requested",details['name'], layer,[k],nc.variables[coords['z']][k], data.shape
		return ApplyDepthSlice(nc,coords,details,k,data,maskWanted=maskWanted)		

	####
	# extract data along a specific longitude (ie North South transect)
	if customLayerType == 'lon': 
		transectcoords	= drawLine(-89.,89.99,customLayerValue,customLayerValue,)
	####
	# extract data along a specific latitude (ie East West transect)
	if customLayerType == 'lat':	
		transectcoords	= drawLine(customLayerValue,customLayerValue,-360.,360.,)			
	####
	#Some special transects.
	if layer == 'ArcTransect':
		lon = 0.
		minlat = 50.
		maxlat = 90.
		transectcoords	= drawLine(minlat,maxlat,lon,lon,)

		lon = -165.
		minlat = 60.
		maxlat = 90.
		transectcoords.extend(drawLine(minlat,maxlat,lon,lon,))
		
	if layer == 'CanRusTransect':
		lon = 83.5
		minlat = 65.
		maxlat = 90.
		transectcoords.extend(drawLine(minlat,maxlat,lon,lon,))
		lon = -96.
		minlat = 60.
		maxlat = 90.
		transectcoords.extend([(minlat +i*(maxlat-minlat)/numpoints,lon) for i in np.arange(numpoints)])# lat,lon
		transectcoords.extend(drawLine(minlat,maxlat,lon,lon,))
	
	if layer == 'AntTransect':
		lon = 0.
		minlat = -89.9
		maxlat = -40.
		transectcoords.extend(drawLine(minlat,maxlat,lon,lon,))			
		
	lats = nc.variables[coords['lat']][:]
	lons = nc.variables[coords['lon']][:]
	if (lats.ndim,lons.ndim) ==(1,1):
		lon2d,lat2d = np.meshgrid(lons,lats)
	else:	lon2d,lat2d = lons,lats

	mmask = np.ones_like(data)
	mask2d = np.ones_like(lon2d)	
	try : 	transectcoords
	except:	raise NameError('extractLayer:\tERROR:\tUnable to define the transect coordinates.\t layer:'+str(layer))

	for (lat,lon) in sorted(transectcoords):
		la,lo = bvp.getOrcaIndexCC(lat, lon, lat2d, lon2d, debug=True,)
		mask2d[la,lo] = 0	


	if mmask.ndim == 3:
		mshape = mmask.shape 
		mmask = np.tile(mask2d,(mshape[0],1,1))	
			
	if mmask.ndim == 4:
		mshape = mmask.shape 
		mmask = np.tile(mask2d,(mshape[0],mshape[1],1,1))
			

	if mmask.shape != mshape:
		raise AssertionError('extractLayer:\tERROR:\tconvertDataTo1D:\t'+str(layer)+'\tMaking mask shape: '+str(mmask.shape))
		assert 0 

	#####
	# Return data.
	if maskWanted:	return mmask
	else:		return np.ma.masked_where(data.mask + mmask==1, data)	
		
		
		
		

	
			

def getHorizontalSlice(nc,coords,details,layer,data = ''):
	if type(nc) == type('filename'):
		nc = dataset(nc,'r')
	
	
	#####
	# In the case that there is no depth field provided, or the depth field is not the netcdf.
	# We just attempt to extract the data. 
	# This is useful
	if coords['z'] == '' or coords['z'] not in nc.variables.keys():
		print "getHorizontalSlice:\tNo depth field in",details['name']
		if type(data) ==type(''): 	data = extractData(nc,details)
		return data
				
	####
	#
	if len(nc.variables[coords['z']][:]) ==1 and layer in ['Surface',]:
		print "getHorizontalSlice:\tNo depth field only 1 value",details['name']	
		if data =='': 	data = extractData(nc,details)
		return ApplyDepthSlice(data, 0)
	if layer in ['layerless',]:
		print "getHorizontalSlice:\tNo layer data requested", layer
		if type(data) == type(''): 	data = extractData(nc,details)
		return data

	#####
	# This is when there is only one dimension in the data/model file.
	if len(nc.dimensions.keys()) == 1 and layer in ['Surface','layerless']:
		print "getHorizontalSlice:\tOne D file",details['name']	
		if data =='': 	data = extractData(nc,details)
		data = np.ma.masked_where(nc.variables[coords['z']][:]>0,data)
		return data
		#return ApplyDepthSlice(data, 0)
		
	
	if layer in ['Surface','100m','200m','300m','500m','1000m','2000m','3000m',]:
		if layer == 'Surface':	z = 0.
		if layer == '100m': 	z = 100.			
		if layer == '200m': 	z = 200.
		if layer == '300m': 	z = 300.		
		if layer == '500m': 	z = 500.
		if layer == '1000m': 	z = 1000.
		if layer == '2000m': 	z = 2000.
                if layer == '3000m':    z = 3000.
		k =  bvp.getORCAdepth(z,nc.variables[coords['z']][:],debug=False)
		if type(data) == type(''):
		 	data = extractData(nc,details)
		print "getHorizontalSlice:\tSpecific depth field requested",details['name'], layer,[k],nc.variables[coords['z']][k], data.shape
		return ApplyDepthSlice(data, k)
			

	if type(layer) in [type(0),np.int64,np.int,]:
		k = layer
		try:	z = nc.variables[coords['z']][k]
		except:	return []
		if data =='': 	data = extractData(nc,details)				
		print "getHorizontalSlice:\tSpecific depth level requested",details['name'], layer,nc.variables[coords['z']][k], data.shape	
		return ApplyDepthSlice(data, k)
			
	if layer in nc.variables[coords['z']][:]:
		z = layer
		k =  bvp.getORCAdepth(z,nc.variables[coords['z']][:],debug=False)
		if data =='': 	data = extractData(nc,details)		
		print "getHorizontalSlice:\tSpecific depth requested",details['name'], layer,nc.variables[coords['z']][k], data.shape	
		return ApplyDepthSlice(data, k)
			
	raise AssertionError("getHorizontalSlice:\tERROR:\tunrecoginised layer instructions: \n\t\tlayer:"+str(layer)+"\n\t\tcoords: "+str(coords))




