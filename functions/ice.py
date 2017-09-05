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
.. module:: applyLandMask
   :platform: Unix
   :synopsis: This function applied a land mask

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

import numpy as np
from bgcvaltools.dataset import dataset
#from bgcvaltools.bgcvalpython import Area

tmask 	= 0
area	= 0
lat	= 0
loadedArea = False

def loadDataMask(gridfn,maskname,):
	global loadedArea
	global tmask
	global area
	global lat		
	nc = dataset(gridfn,'r')		
	tmask = nc.variables[maskname][0]
	area = nc.variables['e2t'][:] * nc.variables['e1t'][:]
	lat = nc.variables['nav_lat'][:,:]
	nc.close()
	loadedArea = True

def calcTotalIceArea(nc,keys, **kwargs):	#Global
	if 'areafile' not in kwargs.keys():
		raise AssertionError("calcTotalIceArea:\t Needs an `areafile` kwarg to run calculation.")	

	try:	maskname = kwargs['maskname']
	except:	maskname = 'tmask'
			
	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)
	
	arr = nc.variables[keys[0]][:].squeeze() * area
	return np.ma.masked_where(tmask==0,arr).sum()/1E12


def calcTotalIceAreaN(nc,keys, **kwargs): # North
	if 'areafile' not in kwargs.keys():
		raise AssertionError("calcTotalIceAreaN:\t Needs an `areafile` kwarg to run calculation.")	
	try:	maskname = kwargs['maskname']
	except:	maskname = 'tmask'
			
	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)
	
	arr = nc.variables[keys[0]][:].squeeze() * area
	return np.ma.masked_where((tmask==0)+(lat<0.),arr).sum()/1E12


def calcTotalIceAreaS(nc,keys, **kwargs): # South
	if 'areafile' not in kwargs.keys():
		raise AssertionError("calcTotalIceAreaS:\t Needs an `areafile` kwarg to run calculation.")	
	try:	maskname = kwargs['maskname']
	except:	maskname = 'tmask'		
	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)
	
	arr = nc.variables[keys[0]][:].squeeze() * area
	return np.ma.masked_where((tmask==0)+(lat>0.),arr).sum()/1E12


def calcTotalIceExtent(nc,keys, **kwargs):	#Global
	if 'areafile' not in kwargs.keys():
		raise AssertionError("calcTotalIceExtent:\t Needs an `areafile` kwarg to run calculation.")	
	try:	maskname = kwargs['maskname']
	except:	maskname = 'tmask'
	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)

	try:	minIce = float(kwargs['minIce'])
	except:	minIce = 0.15

	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)
	
	return np.ma.masked_where((tmask==0)+(nc.variables[keys[0]][:].squeeze()<minIce),area).sum()/1E12



def calcTotalIceExtentN(nc,keys, **kwargs): # North
	if 'areafile' not in kwargs.keys():
		raise AssertionError("calcTotalIceExtentN:\t Needs an `areafile` kwarg to run calculation.")	
	try:	maskname = kwargs['maskname']
	except:	maskname = 'tmask'		
	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)
	
	try:	minIce = float(kwargs['minIce'])
	except:	minIce = 0.15
	
	return np.ma.masked_where((tmask==0)+(nc.variables[keys[0]][:].squeeze()<minIce)+(lat<0.),area).sum()/1E12

def calcTotalIceExtentS(nc,keys, **kwargs): # South

	if 'areafile' not in kwargs.keys():
		raise AssertionError("calcTotalIceExtentS:\t Needs an `areafile` kwarg to run calculation.")	
	try:	maskname = kwargs['maskname']
	except:	maskname = 'tmask'		
	if not loadedArea: loadDataMask(kwargs['areafile'],maskname)
	
	try:	minIce = float(kwargs['minIce'])
	except:	minIce = 0.15
	
	return np.ma.masked_where((tmask==0)+(nc.variables[keys[0]][:].squeeze()<minIce)+(lat>0.),area).sum()/1E12
	
	
	
	

