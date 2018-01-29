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
.. module:: globalVolMean 
   :platform: Unix
   :synopsis: This function calculates the volume weighted mean of a field.

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

def globalVolumeMean(nc,keys, **kwargs):

	try: 	areafile = kwargs['areafile']
	except:	raise AssertionError("globalVolumeMean:\t Needs an `areafile` kwarg to calculate Global Volume Mean")

	try: 	addvalue = kwargs['addvalue']	# In case you want to add a constant value to the data (usually Kelvin to Celcius)
	except:	addvalue = 0.

	try: 	multiplyBy = kwargs['multiplyBy']	# In case you want to multiply the data by a factor
	except:	multiplyBy = 1.		

		
	if not loadedArea: loadDataMask(areafile)
			
        temp = np.ma.array(nc.variables[keys[0]][:].squeeze())
        temp = np.ma.masked_where((tmask==0) + (temp.mask),temp)

	temp = temp *multiplyBy + addvalue
	
	if temp.shape == pvol.shape:
	        vol = np.ma.masked_where(temp.mask, pvol)
        	return (temp*vol).sum()/(vol.sum())

        if temp.shape[1:] == pvol.shape:
		# the temperature has a time dimension.
		outvol = []
		vol = np.ma.masked_where(temp[0].mask, pvol)
		volsum = vol.sum()
		for t in range(temp.shape[0]):
			outvol.append((temp[t]*vol).sum()/volsum)
                return outvol 
	
	assert ("It looks like your data have a strange shape:"+str(temp.shape)+" and the mask shape is "+str(pvol.shape))                        	

