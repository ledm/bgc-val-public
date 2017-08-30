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
.. module:: customMaskTemplate
   :platform: Unix
   :synopsis: A template that produces a mask.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
import numpy as np


def customMaskTemplate(name,newSlice, xt,xz,xy,xx,xd,debug=False):
	"""
	name: The name of the field being analysed.
	newSlice: The name of the regional mask applied here.
	The following fiels are identically sized one dimensional arrays:
	xt : time array
	xz : depth array
	xy : lattitude array
	xx : longigute array
	xd : data array
	"""
	if debug: print "customMaskTemplate:",name
	newmask = np.ma.array(xd).mask
	#####
	# Add some thing to newmask ie:
	# newmask += np.ma.masked_where( xy < 0.,xd).mask	# Mask negative latitudes
	# newmask += np.ma.masked_where( xd < 0.,xd).mask	# Mask negative data	
	#
	## alternativelty, you can combine masks in makeMask:
	## from regions.makeMask import ignoreMediteranean
	# newmask += ignoreMediteranean(name,newSlice, xt,xz,xy,xx,xd,debug=False)
 	return newmask			

