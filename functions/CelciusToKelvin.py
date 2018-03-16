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
.. module:: CelciusToKelvin 
   :platform: Unix
   :synopsis: This basic example loads temperature then converts Celcius into Kelvin.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

from bgcvaltools.dataset import dataset


def CelciusToKelvin(nc,keys, **kwargs):
	# Assuming that zero-th item in keys list is temperature in Celcius
	
	return nc.variables[keys[0]][:] + 273.15 
	

def KelvinToCelcius(nc,keys, **kwargs):
	# Assuming that zero-th item in keys list is temperature in Kelvin
	
	return nc.variables[keys[0]][:] - 273.15 	
