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
.. module:: makeMaskNC 
   :platform: Unix
   :synopsis: Tool to make a mask netcdf for the regions.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
import os	
#from netCDF4 import Dataset
from bgcvaltools import bgcvalpython as bvp
import numpy as np
from changeNC import changeNC, AutoVivification
#import paths
from regions.makeMask import makeMask,loadMaskMakers
from bgcvaltools.dataset import dataset


""" 	This code makes a mask netcdf for the regions written below.
	this code is needed for profileAnalysis.py
"""

def makeMaskNC(outFile, regions, grid,coords, gridfn=''):

	#if grid in ['eORCA1',]:
	#	orcaGridfn 	= '/data/euryale7/scratch/ledm/UKESM/MEDUSA/mesh_mask_eORCA1_wrk.nc'	
	#	orcaGridfn	= paths.orcaGridfn
	#####
	# load mask and coordinates.
	ncmesh = dataset(gridfn,)#'r')
	landmask = ncmesh.variables['tmask'][:]
	maskdims = ncmesh.variables['tmask'].dimensions
	lats 	 = ncmesh.variables[coords['lat']][:]
	lons 	 = ncmesh.variables[coords['lon']][:]
	depths 	 = ncmesh.variables[coords['z']][:]
	floattype = ncmesh.variables[coords['lat']][:].dtype
	inttype = np.int16
	ncmesh.close()
	
	#### 
	# What about upside down grids?
	if landmask.ndim ==4:	masked_value  	= landmask[0,0,0,0]
	elif landmask.ndim ==3:	masked_value  	= landmask[0,0,0]
	elif landmask.ndim ==2:	masked_value  	= landmask[0,0]
	else:	raise AssertionError("land mask has strange dimensions:"+str( landmask.ndim))
								
	landmask = np.ma.masked_where(landmask==masked_value,landmask)
	
	#####
	# Create Temporary Output Arrays.
	arr 	= []
	arr_lat = []
	arr_lon = []
	arr_t 	= []  	  		
	arr_z 	= []  
	arr_y 	= []  
	arr_x 	= []  

	######
	# Make 1D arrays of coordinates
	print 'Make 1D arrays of coordinates from ', landmask.shape, 'landmask'
	print 'landmask', landmask.min(), landmask.mean(),landmask.max()
	for index,v in bvp.maenumerate(landmask):
		if v == masked_value:	continue	
		if np.isnan(v): 	continue
		if np.isinf(v): 	continue		
		
		if len(index) == 3: (z,y,x) 	= index 
		if len(index) == 2: (y,x) 	= index 		
		t = 0

		if lats.ndim ==2:
			la = lats[y,x]
			lo = lons[y,x]
		if lats.ndim ==1:
			la = lats[y]
			lo = lons[x]

		arr.append(v)
		arr_t.append(t)
		arr_z.append(z)
		arr_y.append(y)
		arr_x.append(x)	
		arr_lat.append(la)
		arr_lon.append(lo)

	arr_t 	= np.array(arr_t)
	arr_z	= np.array(arr_z)
	arr_lat	= np.array(arr_lat)
	arr_lon = np.array(arr_lon)
	arr 	= np.array(arr)
	ones    = np.ones_like(arr)
	
	######
	# Calculate 1D mask
	oneDmasks = {}	
	regions, maskingfunctions = loadMaskMakers(regions = regions)
	for r in regions:
		print 'Calculate 1D mask',r, len(arr)
		mask = makeMask(
				maskingfunctions,
				'mask name', 
				r, 
  				arr_t,
  				arr_z,
  				arr_lat,
  				arr_lon,
  				arr)

  		oneDmasks[r] = np.ma.masked_where( mask, ones )
	
	for r in oneDmasks.keys():
		print r, oneDmasks[r].mean(), oneDmasks[r].min(),oneDmasks[r].max(), 'sum:',np.sum(oneDmasks[r]), '%cover',np.sum(oneDmasks[r])/float(len(oneDmasks[r]))
		
	######
	# Convert 1D mask to 3D
	threeDmasks={}
	for r in regions:
		print 'Convert 1D mask to 3D',r, len(oneDmasks[r]), sum(oneDmasks[r])
		mask = np.zeros_like(np.array(landmask),dtype=inttype)
		for i,m in enumerate(oneDmasks[r]):
			#print r, i, m, arr_z[i],arr_y[i],arr_x[i]
			if m == 0: continue
			if np.ma.is_masked(m):continue
			if   landmask.ndim ==3:	mask[arr_z[i],arr_y[i],arr_x[i]] = 1
			elif landmask.ndim ==2:	mask[arr_y[i],arr_x[i]] 	 = 1		
			else:	assert 0
		threeDmasks[r] = mask
		if mask.sum() == 0: 
			raise AssertionError("Mask is 100%"+region)
			
	plotting = 1
	if plotting:
		from matplotlib import pyplot
		for r in regions:
			pyplot.pcolormesh(threeDmasks[r].sum(0),cmap='jet')
			pyplot.colorbar()
			pyplot.title(r + ' '+ os.path.basename(gridfn))
			filename = bvp.folder('images/makeMaskNC/')+os.path.basename(gridfn).replace('.nc', '') + '_'+r+'.png'
			try:
				pyplot.savefig(filename )
				print "Saved", r, 'map image', filename
			except: pass
			pyplot.close()
		     	
		pyplot.pcolormesh(landmask.sum(0),cmap='jet')
		pyplot.colorbar()
		pyplot.title('landmask '+ os.path.basename(gridfn))
		filename = bvp.folder('images/makeMaskNC/')+os.path.basename(gridfn).replace('.nc', '') + '_landmask.png'
		try:
			pyplot.savefig(filename )
			print "Saved", r, 'map image', filename
		except: pass
		pyplot.close()		
	
	av = AutoVivification()
	for r in regions:
		av['newVar'][r]['name']		= r
		av['newVar'][r]['long_name']	= r+ ' mask'
		av['newVar'][r]['units']	= ''
		av['newVar'][r]['newDims']	= maskdims
		av['newVar'][r]['dtype']	= inttype
		av['newVar'][r]['newData']	= threeDmasks[r][:]#.mask	

	removes = [u'e1f', u'e1t', u'e1u', u'e1v', u'e2f', u'e2t', u'e2u', u'e2v', u'ff', u'fmask', u'fmaskutil', u'gdepu', u'gdepv', u'glamf', u'glamt', u'glamu', u'glamv', u'gphif', u'gphit', u'gphiu', u'gphiv', u'isfdraft',  u'misf',   u'tmaskutil',u'umaskutil',  u'vmaskutil', u'e3t', u'e3u', u'e3v', u'e3w', u'e3t_0', u'e3w_0', u'gdept,', u'gdepw', u'gdept_0', u'gdepw_0']
	for rem in removes:
		av[rem]['name']='False'
	print "makeMaskNC:\tmaking new mask file", outFile
	
	c = changeNC(gridfn, outFile, av)

	
	
def main():
	regions	= ['Global', 
		'ignoreInlandSeas',
	  	'SouthernOcean','ArcticOcean',
		'Equator10', 'Remainder',
		'NorthernSubpolarAtlantic','NorthernSubpolarPacific',
		]
	fn = 	'data/eORCA1_masks.nc'
	grid = 'eORCA'
	makeMaskNC(fn, regions, grid)
	
if __name__=="__main__":
	main()


