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
.. module:: maskOnShelf
   :platform: Unix
   :synopsis: A example of a compelx regional mask..
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

from bgcvaltools.dataset import dataset
import numpy as np
import os
import UKESMpython as ukp

package_directory = os.path.dirname(os.path.abspath(__file__))

bathync = dataset(package_directory+"/../data/ORCA1bathy.nc")
bathy = np.ma.abs(bathync.variables["bathymetry"][:])
latcc, loncc =  bathync.variables["lat"][:], bathync.variables["lon"][:]	
bathync.close()
		
def maskOnShelf(name,newSlice, xt,xz,xy,xx,xd,debug=False): 	
	shelfDepth=500.
	shelveFn = ukp.folder("shelves/MatchingMasks/")+"shelfmask.shelve"
	try:
		s = shOpen(shelveFn)		
		lldict  = s['lldict']
		s.close()
	except:	lldict={}
	nmask = np.zeros_like(xd)
	
	count = 0
	for i,z in enumerate(xz):
			try:
				la,lo = lldict[(xy[i],xx[i])]
			except:
				la,lo = ukp.getOrcaIndexCC(xy[i],xx[i],latcc,loncc,debug=False)
				lldict[(xy[i],xx[i])] = la,lo
			
			if la==lo==-1:
				print "Corner case:", la,lo,bathy[la,lo] 
				nmask[i]=1
				
			if  bathy[la,lo] <= shelfDepth: nmask[i]=1	
			count+=1
			if count%100000==0:# or i==(len(xz)+1):
			    try:
				s = shOpen(shelveFn)		
				s['lldict'] = lldict 
				s.close()
				count=0
			    except:
			    	print "makeMask:\tWARNING:\tUnable to save lldict at this time"
	try:
		s = shOpen(shelveFn)		
		s['lldict'] = lldict 
		s.close()
   	except:
   	 	print "makeMask:\tWARNING:\tUnable to save lldict at this time"
   	 	
	print "maskOnShelf:", newSlice, nmask.sum(), 'of', len(nmask)
	return nmask	
