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
.. module:: skeleton_parser
   :platform: Unix
   :synopsis: A nearly empty script to produce analysis.

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

#####
# Load Standard Python modules:
from sys import argv,exit
from os.path import exists
from calendar import month_name
from socket import gethostname
from glob import glob
from scipy.interpolate import interp1d
import numpy as np
import os,sys
from getpass import getuser

#####
# Load specific local code:
import UKESMpython as ukp
from timeseries import timeseriesAnalysis
from timeseries import profileAnalysis
from timeseries import timeseriesTools as tst

from p2p.testsuite_p2p import testsuite_p2p_noAV as testsuite_p2p

from functions.standard_functions import functions
from bgcvaltools.dataset import dataset
from bgcvaltools.configparser import AnalysisKeyParser, GlobalSectionParser

from makeReportConfig import html5MakerFromConfig





def analysis_skeleton(
			configfile = 'runconfig.ini',
			):


	globalKeys =  GlobalSectionParser(configfile)
	
	for k, key in globalKeys.ActiveKeys.items():
		akp = AnalysisKeyParser(configfile, key, debug=True)
	

	
		
	
		
		if akp.dimensions in  [2, 3]:
			metricList = ['mean','median', '10pc','20pc','30pc','40pc','50pc','60pc','70pc','80pc','90pc','min','max']
		else:	metricList = ['metricless',]	
		
                tsa = timeseriesAnalysis(
                        akp.modelFiles_ts,
                        akp.dataFile,
                        jobID           = akp.jobID,
                        dataType        = akp.name,
                        workingDir      = akp.postproc_ts,
                        imageDir        = akp.images_ts,
                        metrics         = metricList,
                        modelcoords     = akp.modelcoords,
                        modeldetails    = akp.modeldetails,
                        datacoords      = akp.datacoords,
                        datadetails     = akp.datadetails,
                        datasource      = akp.datasource,
                        model           = akp.model,
                        layers          = akp.layers,
                        regions         = akp.regions,
                        grid            = akp.modelgrid,
                        gridFile        = akp.gridFile,
                        clean           = akp.clean,
                )
               # assert 0

		#####
		# Profile plots
		if akp.dimensions == 3:
			profa = profileAnalysis(
				akp.modelFiles_ts,
				akp.dataFile,
				jobID           = akp.jobID,
				dataType        = akp.name,
				workingDir      = akp.postproc_ts,
				imageDir        = akp.images_ts,
				modelcoords     = akp.modelcoords,
				modeldetails    = akp.modeldetails,
				datacoords      = akp.datacoords,
				datadetails     = akp.datadetails,
				datasource      = akp.datasource,
				model           = akp.model,
				regions         = akp.regions,
				grid            = akp.modelgrid,
				gridFile        = akp.gridFile,
				layers	 	= list(np.arange(102)),		# 102 because that is the number of layers in WOA Oxygen
				metrics	 	= ['mean',],								
				clean 		= akp.clean,
			)

	    	testsuite_p2p(
                        modelFile	= akp.modelFile_p2p,
                        dataFile 	= akp.dataFile,    		
			model 		= akp.model,
			jobID 		= akp.jobID,
			year  		= akp.year,
			modelcoords     = akp.modelcoords,
                        modeldetails    = akp.modeldetails,
                        datacoords      = akp.datacoords,
                        datadetails     = akp.datadetails,
                        datasource      = akp.datasource,
			plottingSlices	= akp.regions,		# set this so that testsuite_p2p reads the slice list from the av.
			workingDir 	= akp.postproc_p2p, 
			imageFolder	= akp.images_p2p,
                        grid            = akp.modelgrid,			
			gridFile	= akp.gridFile,	# enforces custom gridfile.
			noPlots		= False,	# turns off plot making to save space and compute time.
			annual		= True,
			noTargets	= True,
	 	)	

	html5MakerFromConfig(configfile)
	

def main():
	analysis_skeleton()
	
	
if __name__=="__main__":
	main()
