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
.. module:: calcExportRatio 
   :platform: Unix
   :synopsis: This function calculates the export ratio for the MEDUSA model in the eORCA grid.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

import numpy as np
from bgcvaltools.dataset import dataset



def calcExportRatio(nc,keys):
	a = (nc.variables['SDT__100'][:] +nc.variables['FDT__100'][:]).sum()/ (nc.variables['PRD'][:] +nc.variables['PRN'][:] ).sum()
	#a = np.ma.masked_where(a>1.01, a)
	return 	a	

		
	
