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
   :synopsis: This module is a dictionairy used for linking the time stamp in the model with the data field
   	This is needed because the data files are typically climatologies, and don't have "real" time units.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

tdicts = {
		''	   	: '',
		'Annual'	: {0:0,},
		'ZeroToZero'	: {i  :i     for i in xrange(12)},		
		'OneToOne'	: {i+1:i+1   for i in xrange(12)},
		'OneToZero'	: {i+1:i     for i in xrange(12)},
		'ZeroToOne'	: {i  :i+1   for i in xrange(12)},	
	}	
