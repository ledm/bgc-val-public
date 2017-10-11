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
.. module:: omz 
   :platform: Unix
   :synopsis: This function calculates the Oxygen minimum zone fields (volume, extent, etc ) for the MEDUSA model in the eORCA grid.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

import numpy as np
from bgcvaltools.dataset import dataset
from bgcvaltools.bgcvalpython import Area

omzdetails = {}

def loadDataMask(gridfn):
	global omzdetails
	nc = dataset(gridfn,'r')		
	try:
		pvol   = nc.variables['pvol' ][:]
		tmask = nc.variables['tmask'][:]
	except:
		tmask = nc.variables['tmask'][:]
		area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
		pvol = nc.variables['e3t'][:] *area
	pvol = np.ma.masked_where(tmask==1,pvol)
	nc.close()
	omzdetails[(gridfn,'pvol')] = pvol
	omzdetails[(gridfn,'tmask')] = tmask	
	
	

	

def modelTotalOMZvol(nc,keys, **kwargs):
	if 'gridfile' not in kwargs.keys():
		raise AssertionError("OMZ:\t Needs an `gridfile` kwarg to calculate Total OMZ")	
	gridfn = kwargs['gridfile']
	
	try: 	omzthreshold = float(kwargs['omzthreshold'])
	except:	raise AssertionError("OMZ:\t Needs an `omzthreshold` kwarg to calculate OMZ")

	try:
		pvol = omzdetails[(gridfn,'pvol')]
	except:
		loadDataMask(gridfn)		
		pvol = omzdetails[(gridfn,'pvol')]
				
	if np.ma.sum(pvol) == 0:
		raise AssertionError("omz.py:\t Model volume not loaded correctly")

		
	ox = np.ma.array(nc.variables[keys[0]][:].squeeze())
	if ox.ndim==3:
		return np.ma.masked_where((ox>omzthreshold) + pvol.mask + ox.mask,pvol).sum()	
		
	if ox.ndim==4:
		tlen  = ox.shape[0]
		ox = np.ma.masked_where(ox>omzthreshold, ox)
		omz = []
		for t in range(tlen):
			omz.append(np.ma.masked_where(pvol.mask + ox.mask[t],pvol).sum() )
			#print "OMZ:",t, omz[t], ':',[ox[t].min(),ox[t].mean(),ox[t].max()], ('omzthreshold:',omzthreshold)			
			#from matplotlib import pyplot
			#pyplot.figure()
			#ax1 = pyplot.subplot(221)
			#pyplot.pcolormesh(ox[t].min(0))
			#pyplot.colorbar()
			#ax2 = pyplot.subplot(222)
			#pyplot.pcolormesh(pvol.sum(0))
			#pyplot.colorbar()
			#ax3 = pyplot.subplot(223)
			#pyplot.pcolormesh(ox.mask[t].sum(0))
			#pyplot.colorbar()
			#ax4 = pyplot.subplot(224)
			#pyplot.pcolormesh(pvol.mask.sum(0))
			#pyplot.colorbar()
			#pyplot.show()
			#assert 0
			#print "OMZ:",t, omz[t], ':',[ox[t].min(),ox[t].mean(),ox[t].max()], ('omzthreshold:',omzthreshold)
		return np.ma.array(omz)
	raise AssertionError("OMZ:\t Unexpected Dimensions:"+str(ox.shape))

def woaTotalOMZvol(nc, keys, **kwargs):
	if 'omzthreshold' not in kwargs.keys():
		raise AssertionError("OMZ:\t Needs an `omzthreshold` kwarg to calculate OMZ")	
	omzthreshold = float(kwargs['omzthreshold'])
	
	arr = np.ma.array(nc.variables[keys[0]][:].squeeze() *44.661)
	#area = np.zeros_like(arr[0])
	wpvol = np.zeros_like(arr)
	#np.ma.masked_wjhere(arr.mask + (arr <0.)+(arr >1E10),np.zeros_like(arr))
	lons = nc.variables['lon'][:]
	lats = nc.variables['lat'][:]
	#lonbnds = nc.variables['lon_bnds'][:]
	latbnds = nc.variables['lat_bnds'][:]
	zthick  = np.abs(nc.variables['depth_bnds'][:,0] - nc.variables['depth_bnds'][:,1])

	for y,lat in enumerate(lats):
		area = Area([latbnds[y,0],0.],[latbnds[y,1],1.])
		for z,thick in enumerate(zthick):
			wpvol[z,y,:] = np.ones_like(lons)*area*thick

	return np.ma.masked_where(arr.mask + (arr >omzthreshold)+(arr <0.),wpvol).sum()
				
