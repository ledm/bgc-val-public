#!/usr/bin/ipython
#
# Copyright 2014, Plymouth Marine Laboratory
#
# This file is part of the ukesm-validation library.
#
# ukesm-validation is free software: you can redistribute it and/or modify it
# under the terms of the Revised Berkeley Software Distribution (BSD) 3-clause license. 

# ukesm-validation is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the revised BSD license for more details.
# You should have received a copy of the revised BSD license along with ukesm-validation.
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


from glob import glob
from os.path import basename,exists
from sys import argv
import numpy as np
import UKESMpython as ukp 
#from UKESMpython import folder
#from UKESMpython import getFileList,shouldIMakeFile#,getCalendar
from netCDF4 import Dataset
from changeNC import changeNC,AutoVivification
from mergeNC import mergeNC
from pruneNC import pruneNC
"""	The goal of this code is to have a simple way to make climatology code.
"""


def run(jobID,key,runType,foldIn):

	try:		    
		float(key)
		yearKey=True	
		print "Key is a specific year:", key
		years = [key,]
	except:	
		assert false
		#yearKey=False
		#years = [str(y) for y in np.arange(1997,2008)]
	
	baseline = ['deptht','nav_lat','nav_lon','time_counter',]

	if runType == 'CHL':
		keys = ['CHD','CHN',]
		finalKeys = ['CHL',]	
		L = '_ptrc_T'

	if runType == 'DIN':
		keys = ['DIN',]
		finalKeys = ['DIN',]	
		L = '_ptrc_T'

	if runType == 'OXY':
		keys = ['OXY',]
		finalKeys = ['OXY',]	
		L = '_ptrc_T'

	if runType == 'SAL':
		keys = ['vosaline',]
		finalKeys = ['vosaline',]	
		L = 'T'

	if runType == 'TEMP':
		keys = ['votemper',]
		finalKeys = ['votemper',]	
		L = 'T'
		
	if runType == 'MLD':
		keys = ['somxl010',]
		finalKeys = ['somxl010',]	
		L = 'T'		

	if runType == 'U':
		finalKeys = ['vozocrtx',]
		keys = finalKeys		
		L = 'U'
		
	if runType == 'V':
		finalKeys = ['vomecrty',]
		keys = finalKeys
		L = 'V'

	if runType == 'W':
		finalKeys = ['vovecrtz',]
		keys = finalKeys		
		L = 'W'		
		 								
	#months = sorted(['0121', '0821','0321','0921', '0421','1021', '0521','1121', '0621','1221', '0721','1221'])
	cal = '365_day'		

	#if jobID[:4]=='xjez' and key in ['2001', ]:
	#	print jobID, key
	#	months = sorted([ '20010301', '20010501', '20010701', '20010901', '20011101', '20010130', '20010330', '20010530', '20010730', '20010930', '20011130','20020101',])	
	#	cal = '360_day'
		
	mergedFiles = []
	
	#fns = foldIn+'/'+jobID+'*_1m_'+key+'*'+L+'*.nc'
	fns = foldIn+'/'+jobID+'*_'+key+'*'+L+'.nc'	
	filesIn = sorted(glob(fns))
		
	print "filesIn:", fns, filesIn
		
	for fn in filesIn:
	
		prunedfn = ukp.folder('/tmp/outNetCDF/tmp-Clims')+basename(fn)[:-3]+'_'+key+'_'+runType+'.nc'
		print fn, '--->', prunedfn
		

		if not exists(prunedfn):
			m = pruneNC( fn, prunedfn, keys, debug=True)#,calendar=cal)
		if runType == 'CHL':
			nc = Dataset(prunedfn,'r')
			
			fileOut = prunedfn.replace('.nc','_CHL.nc')
			if not exists(fileOut):
				av = AutoVivification()
				av['CHN']['name']='False'
				av['CHD']['name']	='CHL'
				av['CHD']['units']	='[mg Chl/m3]'
				av['CHD']['long_name']	='Total Chlorophyll'
				av['CHD']['newDims']	=(u'time_counter', u'deptht', u'y', u'x') 
				av['CHD']['newData'] = nc.variables['CHD'][:] + nc.variables['CHN'][:]
				nc.close()
				c = changeNC(prunedfn,fileOut,av,debug=True)
			print fileOut
			#print prunedfn
		else:fileOut = prunedfn
		
		mergedFiles.append(fileOut)		
		#del m
		

	
	filenameOut = ukp.folder('/data/euryale7/scratch/ledm/UKESM/MEDUSA/'+jobID+'_postProc/'+key)+jobID+'_'+key+'_'+runType+'.nc'
	
	if  ukp.shouldIMakeFile(mergedFiles,filenameOut): 
		m = mergeNC( mergedFiles, filenameOut, finalKeys, timeAverage=False,debug=True,calendar=cal)
	
	filenameOut = ukp.folder('/data/euryale7/scratch/ledm/UKESM/MEDUSA/'+jobID+'_postProc/'+key+'-annual')+jobID+'_'+key+'-annual'+'_'+runType+'.nc'
	
	if  ukp.shouldIMakeFile(mergedFiles,filenameOut): 
		m = mergeNC( mergedFiles, filenameOut, finalKeys, timeAverage=True,debug=True,calendar=cal)
		

def main():
	runTypes= ['W','U','V','SAL','TEMP','MLD',]#'OXY','DIN','CHL',]
	#'ERSEMNuts','ERSEMphytoBm','ERSEMphytoChl','ERSEMzoo', 'ERSEMMisc','ERSEMbac']
	#'SalTempWind','ERSEMFull','ERSEMphyto','Detritus', ]#'SalTempWind', ]# ]#]#]
	

			
	try: 	
		jobID = argv[1]
		key   = argv[2]
		print "Using command line arguments:", jobID,key
	except:
		jobID = 'xjwki'
		key = '1979'
		print "Not using command line arguments"
		jobs = ['xjwki', ]
		for j in jobs:
		  for r in runTypes:
			#foldIn = '/data/euryale7/scratch/ledm/iMarNet/'+j+'/MEANS/'		  
			foldIn = '/data/euryale7/scratch/ledm/UKESM/MEDUSA-ORCA025/'+j		  			
		  	run(j,key,r,foldIn)
		return
		


	
	for r in runTypes: 
		#foldIn = '/data/euryale7/scratch/ledm/iMarNet/'+jobID+'/MEANS/'	
		foldIn = '/data/euryale7/scratch/ledm/UKESM/MEDUSA/'+jobID		  					
		run(jobID,key,r,foldIn)
main()	
