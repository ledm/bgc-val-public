#!/usr/bin/ipython 
#
# Copyright 2018, Plymouth Marine Laboratory
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
# -------------------------------------------------------------------------



# jasmin_cmip5_linking.py
#
# This is a tool which can be used to link
# a CMIP5 RCP scenario dataset
# with the historical run.
# Such that they can be analysed together.



from string import join
from os.path  import exists
import os 
from glob import glob

def folder(name):
	""" This snippet takes a string, makes the folder and the string.
        	It also accepts lists of strings.
   	 """
	if type(name) == type(['a','b','c']):
		name=join(name,'/')
	if name[-1] != '/': name = name+'/'
	if exists(name) is False:
		os.makedirs(name)
		print 'makedirs ', name
	return name





def link_hist2Sceanrio(model,field,scenario = 'rcp85',	times = "yr", jobID = "r1i1p1",region = "ocnBgchem"):
	

	testFiles = "/badc/cmip5/data/cmip5/output1/*/"+model+"/"+scenario+"/"+times+"/"+region+"/O"+times+"/"+jobID+"/latest/"+field+"/*.nc"
	filesin = glob(testFiles)

	extended = "/badc/cmip5/data/cmip5/output1/*/"+model+"/historical/"+times+"/"+region+"/O"+times+"/"+jobID+"/latest/"+field+"/*.nc"
        filesin.extend(glob(extended))
	#print testFiles, extended

	outFold = folder(os.path.expanduser("~")+"/cmip5links/"+model+"/"+scenario+'/'+field)
	
	for fn in filesin:
		#print "Testing",fn		
		basename = os.path.basename(fn)
		basename = outFold+ basename.replace('historical', scenario)
	
                if os.path.exists(basename):continue
	
		print "ln -s",fn,basename
		os.symlink(fn, basename)



models = ["HadGEM2-ES","HadGEM2-CC","NorESM1-ME","GFDL-ESM2G","GFDL-ESM2M","CESM1-BGC","MPI-ESM-MR","MPI-ESM-LR","IPSL-CM5A-MR","IPSL-CM5B-LR","CMCC-CESM", "GISS-E2-R-CC","GISS-E2-H-CC",]
	#";","MIROC-ESM","MIROC-ESM-CHEM","CanESM2"

#annualbgcfields = ['chl',]	
#for field in annualbgcfields:
#  for model in models:
#	link_hist2Sceanrio(model,field,scenario = 'rcp85', times = "yr", jobID = "r1i1p1",region = "ocnBgchem")

monthlybgcfields = ['intpp','fgco2',]
for field in monthlybgcfields:
  for model in models:
	print field,model
        link_hist2Sceanrio(model,field,scenario = 'rcp85', times = "mon", jobID = "r1i1p1",region = "ocnBgchem")

monthlyPhysFields = ['uo','vo','tos','sos']
for field in monthlyPhysFields:
  for model in models:
        print field,model
        link_hist2Sceanrio(model,field,scenario = 'rcp85', times = "mon", jobID = "r1i1p1",region = "ocean")



