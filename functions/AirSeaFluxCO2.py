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
from bgcvaltools.configparser import GlobalSectionParser




model_area 	= {}

def loadDataArea(gridfn):
	global model_area
	nc = dataset(gridfn,'r')
	try:	mo = nc.variables['area'][:]		
	except:	mo = nc.variables['e1t'][:]*nc.variables['e2t'][:]
	model_area[gridfn] = mo.squeeze()
	nc.close()
	

def TotalAirSeaFluxCO2(nc,keys,**kwargs):
	"""
	This function calculated the total Air Sea FLux for the MEDUSA model in the eORCA grid.
	"""
	factor =  365.25 * 12./1000. / 1.E15
	
	try:	arr = nc.variables[keys[0]][:].squeeze() * factor	# mmolC/m2/d
	except: 
		raise AssertionError("TotalAirSeaFluxCO2:\tNot able to load "+str(keys[0])+" from netcdf "+str(nc.filename))		


	if 'gridfn' not in kwargs.keys():
		raise AssertionError("TotalAirSeaFluxCO2:\t Needs an `gridfn` kwarg to run calculation.")	
	gridfn = kwargs['gridfn']
	
	try:	area = model_area[gridfn]
	except:
		loadDataArea(gridfn)
		area = model_area[gridfn]
		
	
	if arr.ndim ==2: arr = arr*area
	else: 
		raise AssertionError("TotalAirSeaFluxCO2:\t"+str(keys[0])+" from netcdf "+str(nc.filename) +" has an unexpected number of dimensions: "+str(arr.ndim))
	return arr.sum()

def TotalAirSeaFluxCO2kgm2s(nc,keys,**kwargs):
	"""
	This function calculated the total Air Sea FLux for the CMIP5 models. in kg m-2 s-1
	"""
	factor =  365.25 *24.*60.*60. / 1.E12
	
	try:	arr = nc.variables[keys[0]][:].squeeze() * factor	# mmolC/m2/d
	except: 
		raise AssertionError("TotalAirSeaFluxCO2kgm2s:\tNot able to load "+str(keys[0])+" from netcdf "+str(nc.filename))		


	if 'gridfile' not in kwargs.keys():
		raise AssertionError("TotalAirSeaFluxCO2kgm2s:\t Needs an `gridfile` kwarg to run calculation.")	
	gridfn = kwargs['gridfile']
	
	try:	area = model_area[gridfn]
	except:
		loadDataArea(gridfn)
		area = model_area[gridfn]
		
	
	if arr.ndim ==2: 
		arr = arr*area
		return arr.sum()
	elif arr.ndim ==3: 
		out =[]
		for t in np.arange(arr.shape[0]):
			out.append((arr[t]*area).sum())
		return out
	raise AssertionError("TotalAirSeaFluxCO2kgm2s:\t"+str(keys[0])+" from netcdf "+str(nc.filename) +" has an unexpected number of dimensions: "+str(arr.ndim))

	
#def takaTotal(nc,keys):
#	arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
#	arr = -1.E12* arr /1.E15#/ 365.				#g Carbon/day
#	#area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
#	#fluxperarea = arr/area
#	return arr.sum()
#	# area 10^6 km^2
#	# flux:  10^15 g Carbon month^-1. (GT)/m2/month




