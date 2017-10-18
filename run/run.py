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
.. module:: run
   :platform: Unix
   :synopsis: A nearly empty script that launches the BGC-val analysis parser.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
from sys import argv

from analysis_parser import analysis_parser

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

if __name__=="__main__":
	try: 	configfn = argv[1]
	except: 
		configfn = 'runconfig.ini'
		print "run.py:\tNo config file provided, using default: ", configfn

	analysis_parser( 
		configfile= configfn,
		)
