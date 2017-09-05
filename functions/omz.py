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

tmask 	= 0
pvol 	= 0
loadedArea = False

def loadDataMask(gridfn):
	global loadedArea
	global tmask
	global pvol
	nc = dataset(gridfn,'r')		
	try:
		pvol   = nc.variables['pvol' ][:]
		tmask = nc.variables['tmask'][:]
	except:
		tmask = nc.variables['tmask'][:]
		area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
		pvol = nc.variables['e3t'][:] *area
		pvol = np.ma.masked_where(tmask==0,pvol)
	nc.close()
	loadedArea = True
	

def modelTotalOMZvol(nc,keys, **kwargs):
	if 'areafile' not in kwargs.keys():
		raise AssertionError("OMZ:\t Needs an `areafile` kwarg to calculate Total OMZ")	

	try: 	omzthreshold = float(kwargs['omzthreshold'])
	except:	raise AssertionError("OMZ:\t Needs an `omzthreshold` kwarg to calculate OMZ")

	if not loadedArea: loadDataMask(kwargs['areafile'])
	if np.ma.sum(pvol) == 0:
		raise AssertionError("omz.py:\t Model volume not loaded correctly")

		
	arr = np.ma.array(nc.variables[keys[0]][:].squeeze())
	return np.ma.masked_where((arr>omzthreshold) + pvol.mask + arr.mask,pvol).sum()


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
				
