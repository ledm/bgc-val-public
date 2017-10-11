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
.. module:: TotalIntPP
   :platform: Unix
   :synopsis: This function calculated the total primary production for the MEDUSA model in the eORCA grid.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

import numpy as np

from bgcvaltools.dataset import dataset
from bgcvaltools.configparser import GlobalSectionParser





model_area = 0
loadedArea = False

def loadDataMask(gridfn):
	global loadedArea
	global model_area	
	nc = dataset(gridfn,'r')
	try:	model_area = nc.variables['area'][:]
	except: model_area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
	nc.close()
		
	loadedArea = True
	

def TotalIntPP(nc,keys,**kwargs):
	"""
	This function calculated the total primary production for the MEDUSA model in the eORCA grid.
	"""
	if 'areafile' not in kwargs.keys():
		raise AssertionError("TotalIntPP:\t Needs an `areafile` kwarg to calculate Total Int PP")	
	

	if loadedArea == False: loadDataMask(kwargs['areafile'])
	
	if np.ma.sum(model_area) == 0.:
		raise AssertionError("TotalIntPP:\t Model area not loaded correctly")
	
	#	 mmolN/m2/d        [mg C /m2/d]   [mgC/m2/yr] [gC/m2/yr]     Gt/m2/yr
	factor = 1.		* 6.625 * 12.011 * 365.	      / 1000.   /     1E15
	arr = (nc.variables[keys[0]][:]+ nc.variables[keys[1]][:]).squeeze()*factor
	if arr.ndim ==3:
		for i in np.arange(arr.shape[0]):
			arr[i] = arr[i]*model_area
	elif arr.ndim ==2: arr = arr*model_area
	else: assert 0
	return arr.sum()

		
ppdetails = {}

def loadArea(gridfn):
	global ppdetails
	nc = dataset(gridfn,'r')		
	tmask = nc.variables['tmask'][:]
	try:
		area   = nc.variables['area' ][:]
	except:
		area = nc.variables['e2t'][:] * nc.variables['e1t'][:]

		
	nc.close()
	ppdetails[(gridfn,'area')] = area
	
def TotalIntPPcmip(nc,keys,**kwargs):
	"""
	This function calculated the total primary production for the MEDUSA model in the eORCA grid.
	"""
	if 'areafile' not in kwargs.keys():
		raise AssertionError("TotalIntPP:\t Needs an `areafile` kwarg to calculate Total Int PP")	
	gridfn = kwargs['areafile']
	try:
		area = ppdetails[(gridfn,'area')]
	except:
		loadArea(gridfn)		
		area = ppdetails[(gridfn,'area')]
			

	if np.ma.sum(area) == 0.:
		raise AssertionError("TotalIntPP:\t Model area not loaded correctly")
	
	#	 [g C /m2/s]   [mgC/m2/yr] [gC/m2/yr]     Gt/m2/yr
	factor = 12.011 * (365.*24.*60.*60.) *	1E-15
	arr = nc.variables[keys[0]][:] * factor 
	#+ nc.variables[keys[1]][:]).squeeze()*factor
	
	if arr.ndim ==3:
		out = []
		for i in np.arange(arr.shape[0]):
			out.append((arr[i]*area).sum())
			print 'intpp',i, out[i]
		return np.ma.array(out)
	elif arr.ndim ==2: 
		arr = arr*area
		return arr.sum()
	else: assert 0





	
