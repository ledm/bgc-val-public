
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
.. module:: tdicts
   :platform: Unix
   :synopsis: This module is a dictionairy of functions that can be applied to the data.
   	The expectation is that users will either add to this list.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""


#####
# These are the default evaluation functions.

functions = {}

####
# Some functions for maniulating data:
def NoChange(nc,keys):	
	""" 
	Loads keys[0] from the netcdf, but applies no change.
	"""
	return nc.variables[keys[0]][:]

def N2Biomass(nc,keys):	
	""" 
	Loads keys[0] from the netcdf, but multiplies by 79.572 (to convert Nitrogen into biomass).
	"""
	return nc.variables[keys[0]][:]* 79.573

def KtoC(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, and converts from Kelvin to Celcius.
	"""
	return nc.variables[keys[0]][:] - 273.15

def mul1000(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but multiplies by 1000.
	"""
	return nc.variables[keys[0]][:]* 1000.

def mul1000000(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but multiplies by 1000000.
	"""
	return nc.variables[keys[0]][:]* 1000000.
	
def div1000(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, then divides by 1000.
	"""
	return nc.variables[keys[0]][:]/ 1000.	

def div1e6(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but divides by 1.e6.
	"""
	return nc.variables[keys[0]][:]/ 1.e6	

def applymask(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but applies a mask.
	"""
	return np.ma.masked_where(nc.variables[keys[1]][:]==0.,nc.variables[keys[0]][:])
	
def sums(nc,keys):	
	""" 
	Loads Key[0] from the netcdf, then sums the other keys.
	"""
		
	a = nc.variables[keys[0]][:]
	for k in keys[1:]:a += nc.variables[k][:]
	return a 

def oxconvert(nc,keys): 	
	""" 
	Loads keys[0] from the netcdf, but multiplies by 44.771 (to convert oxygen units ).
	"""
	return nc.variables[keys[0]][:] *44.661
def convertkgToM3(nc,keys): 	
	""" 
	Loads keys[0] from the netcdf, but multiplies by 1.027 (to convert from density kg to volume).
	"""
	return nc.variables[keys[0]][:]* 1.027
	
	


functions['NoChange'] 		= NoChange	
functions['N2Biomass'] 		= N2Biomass	
functions['KtoC'] 		= KtoC
functions['mul1000'] 		= mul1000
functions['mul1000000'] 	= mul1000000		
functions['div1000'] 		= div1000	
functions['div1e6'] 		= div1e6
functions['applymask'] 		= applymask
functions['sums'] 		= sums
functions['sum'] 		= sums
functions['oxconvert'] 		= oxconvert
functions['convertkgToM3'] 	= convertkgToM3






