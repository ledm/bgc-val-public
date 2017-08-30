#
# Copyright 2017, Plymouth Marine Laboratory
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
.. module:: customFunctionsTemplate
   :platform: Unix
   :synopsis: A template for the functions.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>
"""

import numpy as np
from bgcvaltools.dataset import dataset

def customFunctionTemplate(nc,keys):
	"""
	This function. 
	
	nc: a netcdf openned as a dataset.
	keys: a list of keys to use in this function.
	
	"""
	arr = nc.variables[keys[0]]
	# arr = arr*1000.
	# arr = np.ma.masked_where(arr < 0., arr)
	return arr
	
