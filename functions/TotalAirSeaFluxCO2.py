
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
.. module:: TotalAirSeaFluxCO2
   :platform: Unix
   :synopsis: This function calculated the total Air Sea FLux for the MEDUSA model in the eORCA grid.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

import numpy as np

from bgcvaltools.dataset import dataset


nc = dataset("/data/euryale7/scratch/ledm/UKESM/MEDUSA/mesh_mask_eORCA1_wrk.nc",'r')
try:	
	model_area = nc.variables['area'][:]
except:
	model_area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
nc.close()


def TotalAirSeaFluxCO2(nc,keys):
	"""
	This function calculated the total Air Sea FLux for the MEDUSA model in the eORCA grid.
	"""
	factor =  365.25 * 12./1000. / 1.E15
	arr = nc.variables['CO2FLUX'][:].squeeze() * factor	# mmolC/m2/d
#	if arr.ndim ==3:
#		for i in np.arange(arr.shape[0]):
#			arr[i] = arr[i]*area
	if arr.ndim ==2: arr = arr*model_area
	else: assert 0
	return arr.sum()

#def takaTotal(nc,keys):
#	arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
#	arr = -1.E12* arr /1.E15#/ 365.				#g Carbon/day
#	#area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
#	#fluxperarea = arr/area
#	return arr.sum()
#	# area 10^6 km^2
#	# flux:  10^15 g Carbon month^-1. (GT)/m2/month




