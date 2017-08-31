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

#Standard Python modules:
from sys import argv,exit
from os.path import exists
from calendar import month_name

#Specific local code:
from UKESMpython import populateSlicesList, AutoVivification, folder, reducesShelves,listShelvesContents,mnStr
from testsuite_p2p import testsuite_p2p
from p2p import makePatternStatsPlots
from p2p.patternAnalyses import InterAnnualPatterns,BGCvsPhysics
from longnames.longnames import months

#####
# code plan:
#	This is a the script that calls testsuite_p2p now.
#	Now all code is run though that testsuite.
#	the idea being that each analysis produces a new one of these analysis tools.
#	

# 	from 
def analysis():
	# DMS model:
	#model= 'MEDUSA'
	#jobID = 'xkrum'
	#year = 'clim'		
	#modelGrid = 'ORCA1'
	#MEDUSAFolder	= "/data/euryale7/scratch/ledm/UKESM_postProcessed/MEDUSA/outNetCDF/"+jobID+'-' + year+'/'

	# ORCA1:
	models= ['MEDUSA','NEMO']
	jobID = 'xkrus'
	years = ['2077-annual'] #'2075','2076',
	modelGrid = 'ORCA1'
	MEDUSAFolder_pref= "/data/euryale7/scratch/ledm/UKESM/MEDUSA/xkrus_postProc/"
	NEMOFolder_pref= "/data/euryale7/scratch/ledm/UKESM/MEDUSA/xkrus_postProc/"
	annual = True
	
	# ORCA025:
	#model= 'MEDUSA'
	#jobID = 'xjwki'
	#year = '1979'		
	#modelGrid = 'ORCA025'	
	#MEDUSAFolder	= "/data/euryale7/scratch/ledm/UKESM/MEDUSA-ORCA025/"+jobID+"_postProc/"+year+"/"
	
		
	#####
	# Which analysis to run
	doCHL 		= 0#True
	doMAREDAT 	= 0#True
	doN		= 0#True
	doSi		= 0#True	
	doFe		= 0#True		
	doPCO2		= 0#True
	doIntPP		= 0#True
	doO2		= True	
	
	doSal		= 0#True
	doTemp		= 0#True
	doMLD		= 0#True
	
	
	#####
	# What depth level to investigate, in the case of big 3D files (T,Sal, N,P,Si, etc)	
	if annual:	depthLevels 	= ['',]
	else:		depthLevels 	= ['Transect','Surface','100m','200m','500m',]

	#####
	# Location of data files.
	MAREDATFolder 	= "/data/perseus2/scratch/ledm/MAREDAT/MAREDAT/"
	if annual:	WOAFolder 	= "/data/euryale7/scratch/ledm/WOA/annual/"
	else:		WOAFolder 	= "/data/euryale7/scratch/ledm/WOA/"	
	GEOTRACESFolder = "/data/euryale7/scratch/ledm/GEOTRACES/GEOTRACES_PostProccessed/"
	TakahashiFolder = "/data/euryale7/scratch/ledm/Takahashi2009_pCO2/"
	LesterFolder 	= "/data/euryale7/scratch/ledm/LestersReportData/"			
	
	shelvesAV = []
	
	for year in years:		
		#####
		# Location of model files.
		MEDUSAFolder 	= MEDUSAFolder_pref+year+'/'
		NEMOFolder  	= NEMOFolder_pref+year+'/'			

		#####
		# AutoVivification is a form of nested dictionary.
		# We use AutoVivification here to determine which files to analyse and which fields in those files.
		# depthLevel is added, because some WOA files are huges and my desktop can not run the p2p analysis of that data.
		av = AutoVivification()
		if doCHL:
			av['chl']['Data']['File'] 		= MAREDATFolder+"MarEDat20121001Pigments.nc"	
			if modelGrid == 'ORCA1':	
				av['chl']['MEDUSA']['File'] 	= MEDUSAFolder+jobID+'_' + year+"_MEDUSA_bio.nc"
				av['chl']['MEDUSA']['Vars'] 	= ['CHD','CHN']				
			if modelGrid == 'ORCA025':
				av['chl']['MEDUSA']['File']	= MEDUSAFolder+"xjwki_1979_CH.nc"
				av['chl']['MEDUSA']['Vars'] 	= ['CHL',]			
			av['chl']['Data']['Vars'] 		= ['Chlorophylla',]

			av['chl']['depthLevels'] 		= ['',]
			av['chl']['MEDUSA']['grid']		= modelGrid		
						
		if doMAREDAT:
			av['diatoms']['Data']['File'] 		= MAREDATFolder+"MarEDat20120716Diatoms.nc"	
			av['diatoms']['MEDUSA']['File'] 	= MEDUSAFolder+"medusa_bio_"+year+".nc"	
			av['diatoms']['Data']['Vars'] 		= ['BIOMASS',]
			av['diatoms']['MEDUSA']['Vars'] 	= ['PHD',]	
			av['diatoms']['depthLevels'] 		= ['',]	
			av['diatoms']['MEDUSA']['grid']		= modelGrid						
		
			av['microzoo']['Data']['File'] 		= MAREDATFolder+"MarEDat20120424Microzooplankton.nc"	
			av['microzoo']['Data']['Vars'] 		= ['BIOMASS',]
			av['microzoo']['MEDUSA']['File'] 	= MEDUSAFolder+"medusa_bio_"+year+".nc"	
			av['microzoo']['MEDUSA']['Vars'] 	= ['ZMI',]	
			av['microzoo']['MEDUSA']['grid']	= modelGrid		
			av['microzoo']['depthLevels'] 		= ['',]	
	
			av['mesozoo']['Data']['File'] 		= MAREDATFolder+"MarEDat20120705Mesozooplankton.nc"	
			av['mesozoo']['Data']['Vars'] 		= ['BIOMASS',]
			av['mesozoo']['MEDUSA']['File'] 	= MEDUSAFolder+"medusa_bio_"+year+".nc"	
			av['mesozoo']['MEDUSA']['Vars'] 	= ['ZME',]	
			av['mesozoo']['MEDUSA']['grid']		= modelGrid		
			av['mesozoo']['depthLevels'] 		= ['',]

		if doN:
			av['nitrate']['Data']['File'] 		= WOAFolder+'nitrate_monthly_1deg.nc'	
			av['nitrate']['Data']['Vars'] 		= ['n_an',] 		#l+'_mn',
			if modelGrid == 'ORCA1':			
				av['nitrate']['MEDUSA']['File'] = MEDUSAFolder+jobID+'_'+ year+"_MEDUSA_bio.nc"		
			if modelGrid == 'ORCA025':
				av['nitrate']['MEDUSA']['File'] = MEDUSAFolder+jobID+'_'+ year+"_DIN.nc"							
			av['nitrate']['MEDUSA']['Vars'] 	= ['DIN',]									
			av['nitrate']['MEDUSA']['grid']		= modelGrid		
			av['nitrate']['depthLevels'] 		= depthLevels
			
		if doSi:
			av['silicate']['Data']['File'] 		= WOAFolder+'silicate_monthly_1deg.nc'	
			av['silicate']['Data']['Vars'] 		= ['i_an',] 		#l+'_mn',
			av['silicate']['MEDUSA']['Vars'] 	= ['SIL',]									
			av['silicate']['MEDUSA']['File'] 	= MEDUSAFolder+"medusa_bio_"+year+".nc"
			av['silicate']['MEDUSA']['grid']	= modelGrid		
			av['silicate']['depthLevels'] 		= depthLevels
						
		if doFe:							
			av['iron']['Data']['File'] 		= GEOTRACESFolder+"Iron_GEOTRACES_IDP2014_Discrete_Sample_Data_ascii.nc"
			av['iron']['MEDUSA']['File'] 		= MEDUSAFolder+"medusa_bio_"+year+".nc"	
			av['iron']['Data']['Vars'] 		= ['Fe_D_CONC_BOTTLE',]
			av['iron']['MEDUSA']['Vars'] 		= ['FER',]	
			av['iron']['depthLevels'] 		= ['',]
			av['iron']['MEDUSA']['grid']		= modelGrid		

		if doO2:
			if annual:	av['oxygen']['Data']['File'] 	=  WOAFolder+'woa13_all_o00_01.nc'
			else:		av['oxygen']['Data']['File'] 	=  WOAFolder+'oxygen-woa13.nc'
			av['oxygen']['Data']['Vars'] 	= ['o_an',] 
			av['oxygen']['MEDUSA']['Vars'] 	= ['OXY',]
			av['oxygen']['MEDUSA']['File']	= MEDUSAFolder+jobID+"_"+year+"_OXY.nc"
			av['oxygen']['MEDUSA']['grid']	= modelGrid
			av['oxygen']['depthLevels'] 	= depthLevels
		
		if doPCO2:
			av['pCO2']['Data']['File'] 	= TakahashiFolder + "takahashi2009_month_flux_pCO2_2006c_noHead.nc"	
			av['pCO2']['MEDUSA']['File'] 	= MEDUSAFolder+"medusa_bio_"+year+".nc"
			av['pCO2']['Data']['Vars'] 	= ['PCO2_SW',] 		#l+'_mn',
			av['pCO2']['MEDUSA']['Vars'] 	= ['OCN_PCO2',]	
			av['pCO2']['depthLevels'] 	= ['',]
			av['pCO2']['MEDUSA']['grid']	= modelGrid				


	#	if doIntPP:
	#		av['intpp']['Data']['File'] 	=  LesterFolder+'PPint_1deg.nc'
	#		av['intpp']['Data']['Vars'] 	= ['PPint',]
	#		#av['intpp']['ERSEM']['Vars'] 	= ['netPP',] This field is net, not integrated.
	#		#av['intpp']['ERSEM']['File']	= ERSEMFolder+'_ERSEMMisc.nc' This file will need to be remade.
	#		av['intpp']['ERSEM']['grid']	= modelGrid
	#		av['intpp']['depthLevels'] 		= ['',]
		
		
		if doSal:
			if annual:	av['salinity']['Data']['File'] 		= WOAFolder+'woa13_decav_s00_01v2.nc'	
			else:		av['salinity']['Data']['File'] 		= WOAFolder+'salinity_monthly_1deg.nc'	
			av['salinity']['Data']['Vars'] 		= ['s_an',]
			av['salinity']['NEMO']['File'] 		= NEMOFolder+jobID+"_"+year+'_SAL.nc'	
			av['salinity']['NEMO']['Vars'] 		= ['vosaline',]
			av['salinity']['NEMO']['grid'] 		= modelGrid
			av['salinity']['depthLevels'] 		= depthLevels	 

		
		if doTemp:
			if annual:	av['temperature']['Data']['File'] 	= WOAFolder+'woa13_decav_t00_01v2.nc'	
			else:		av['temperature']['Data']['File'] 	= WOAFolder+'temperature_monthly_1deg.nc'	
			av['temperature']['Data']['Vars'] 	= ['t_an',]	
			av['temperature']['NEMO']['File'] 	= NEMOFolder+jobID+"_"+year+'_TEMP.nc'	
			av['temperature']['NEMO']['Vars'] 	= ['votemper',]
			av['temperature']['NEMO']['grid'] 	= modelGrid	
			av['temperature']['depthLevels'] 	= depthLevels	

						   
		if doMLD:	
			#if annual:	
			if annual:	av['mld']['Data']['File'] 		= "/data/euryale7/scratch/ledm/IFREMER-MLD/mld_DT02_c1m_reg2.0-annual.nc"
			else:		av['mld']['Data']['File'] 		= "/data/euryale7/scratch/ledm/IFREMER-MLD/mld_DT02_c1m_reg2.0.nc"
			av['mld']['Data']['Vars'] 		= ['mld','mask',]
			av['mld']['NEMO']['File'] 		= NEMOFolder+jobID+"_"+year+'_MLD.nc'			
			av['mld']['NEMO']['Vars'] 		= ['somxl010',]	
			av['mld']['NEMO']['grid'] 		= modelGrid
			av['mld']['depthLevels'] 		= ['',]

		
				
		#####
		# Set which spatial and temporal limitations to plot.
		if annual:
			plottingSlices = populateSlicesList(
				 plotDefaults		=True,	
				 plotMonths		=0,#True,
				 plotdepthRanges	=True,
				 plotpercentiles	=0,#True	
				 plotLatRegions		=0,# True
				 plotQualityCuts	=0,#True	
				 plotSeas		=0,#True		 
				 plotOceans		=True,
				 plotHemispheres	=True,
				 plotSeasons		=0,# True
				 plotOceanSeasons	=0,# True		 		 
				 plotOceanMonths   	=0,#True	
				 plotHemispheresMonths  =0,#True,
			)
				
		else:
			plottingSlices = populateSlicesList(
				 plotDefaults		=True,	
				 plotMonths		=True,
				 plotdepthRanges	=0,
				 plotpercentiles	=0,#True	
				 plotLatRegions		=0,# True
				 plotQualityCuts	=0,#True	
				 plotSeas		=0,#True		 
				 plotOceans		=True,
				 plotHemispheres	=0,# True
				 plotSeasons		=0,# True
				 plotOceanSeasons	=0,# True		 		 
				 plotOceanMonths   	=0,#True	
				 plotHemispheresMonths  =True,
			)

		for model in models:
			workingDir = folder("/data/euryale7/scratch/ledm/ukesm_postProcessed/"+model+'-'+jobID+'-'+year)
			imageFolder 	= folder('images/'+model+'-'+jobID)

	
			shelvesAV.extend(
		    		testsuite_p2p(
					model = model,
					jobID = jobID,
					year  = year,
					av = av,
					plottingSlices= plottingSlices,
					workingDir = workingDir,
					imageFolder= imageFolder
			 	)
			)

	BGCvsPhysics(shelvesAV, jobID, modelGrid )
		
	if len(years)>1: InterAnnualPatterns(shelvesAV, jobID, years,modelGrid)	# plots interannual comparison and time series.
	
		
if __name__=="__main__":
	analysis()	
	
	
			

