# BGC-val-public toolkit

## Introduction

Originally designed as a toolkit for investigating the time development of the marine biogeochemistry component of the UK Earth system model,
BGC-val has since expanded to become a generic tool for comparing model data against historic data. 

The toolkit is 100% python, and is freely available, and distributed with the BSD 3 clause license, via our in-house gitlab server. Registration is required, via this link.


The goal was to make the evaluation framework as generic as possible:
* Model independent.
* Grid independent.
* Coordinate independent. 
* Dataset independent.
* Field independent.


This package utilises:
* python parallelization. 
* Front-loading analysis function
* Regular save points + shelve files.
* Versioning in git (using gitlab)
* Web visible html summary reports.



## Requirements

To use this code, the following python packages are required:
* Matplotlib
* netCDF4
* numpy 
* scipy
* Cartopy 
* https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/netcdf_manip

Most of these packages can be installed with the command :

 	pip install --user packagename
 	
Please note that cartopy can be difficult to install, with many requirements: such as geos, geos-python, geos-devel, proj4, cython etc… (http://scitools.org.uk/cartopy/)

## Installation

Once the previously mentionned packages have been installed, make a local copy of the trunk of this package with something like:
	
	git clone git@gitlab.ecosystem-modelling.pml.ac.uk:ledm/bgc-val-public.git

Note that the package name here is subject to change, and that you should check the path at the top of this page.

In the local copy, use the following pip command to make a local installation of this package:

	pip install -e . --user


## Running

Once the package has been installed, make a copy of the bgc-val-public/run directory in your working directory.

The run directory will contain:
* run.py: The main script that runs the analysis.
* runconfig.ini: The main configuration script that contains all information, flags, paths and settings needed to produce the analysis.
* localfunctions directory: This directory is where you should put any custom analysis functions that you may want to use to load or manipuate your data.


###  runconfig.ini

The run config file contains all information, flags, paths and settings needed to produce the analysis.

Note that config files use the following convention:
```ini
	[Section]
	option 	: value
	; comment
```

;
; When loading the config file into ConfigParser.py:
; Beware that:
; 	Sections hold capitalisation
; 	Options all become lowercase
; 	Values are parsed as strings
;	; denotes a comment, but if you place it at the end of a line, it requires a space before. 
;
; The parser expects an [ActiveKeys] section, a [Global] section,
; and a section for each key in [ActiveKeys]
;
; The values used in [Global] for jobID, year, model can be put into paths using $JOBID,$YEAR or $MODEL.
; Similarly, $NAME can be used as a stand in for the name option for of each analysis. 
; 




	
## Package contents

	pftnames.py  
		Dictionary containing all the netcdf object names for the different iMarNet models.
		
	testsuite_p2p.py  
		Code to run all tests in the p2p toolkit.
		
	UKESMpython.py
		Toolkit containing many useful functions.


	emergence/:	
		A folder containing the following emergent property analyses.
		
		cchl.py  
			Carbon to Chlorophyll ratio
		
		cchlvsIrradiance.py  
			Carbon:Chl ratio against Irradiance
		
		communityfit.py  
			Community Strcutre plotting
			
		primaryproduction.py
			Calculate annual and monthly primary production.
	
	
	p2p/: 
		A folder containing the Point to point analsyes scritps.

		prepareERSEMyear.py:
			this merges 12 monthly netcdfs into one annual file. 

		matchDataAndModel.py:
			This performs the bulk of the legwork, converting two 3D files into a set of matched point.
							
		makePlots.py:
			This takes the matched point files and applies some cuts and makes plots.

		makeTargets.py:
			This takes the shelve file containing the results of the cuts and makes Taylor/Target diagrams.
		
		csvFromShelves.py:
			This takes a shelve file(s) and produces a csv file of the Target metrics.
			
	
	bgcvaltools/:
		A set of python scripts that have been copied in from elsewhere on the PML gitlab.
		
		C2Chl.py:
			Carbon to Chlorophyll ratio, from Sathyrendranath 2009. Written by Momme.
		
		communitystructure.py and comstrucFit.py:
			Comminity structure code and fit, ie Brewin 2014. Written by Lee.
		
		StatsDiagram.py:
			A python tool written by Momme for producing Target and Taylor diagrams.

	timeseries/:
		Contains all the tools needed to do the time series analysis.
		timeseriesAnalysis.py  
		timeseriesPlots.py  
		timeseriesTools.py
		
		Launched by analysis-timeseries.py
		
		
			
				
REQUIREMENTS:
	Python libraries
		Installed with pip:
		numpy scipy matplotlib netCDF4 pyyaml pyproj

		
		Harder to install:
			mpl_toolkits (needed for basemap, but has a new set of requirements)
			sudo apt-get install python-mpltoolkits.basemap
			sudo yum install python-mpltoolkits.basemap		
			or from source.
							
			It may be possible to switch Basemap out for cartopy.
			Cartopy is equally difficult to install.
	
	Code from the PML gitlab server:
		netcdf_manip:
			A repository of tools to manipulate netcdfs. 
			Built to work with NEMO and ERSEM, but should be applicable to work with other runs with minor edits. Questions: ledm@pml.ac.uk
			
			Includes:
				changeNC, mergeNC, pruneNC, convertToOneDNC
				from: https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/netcdf_manip
			
	You may also need the maps for cartopy:
		You can copy them to your local directory (on JASMIN) from the ESMVAL machine:
			rsync -avP /usr/local/cartopy/shapefiles/*  ~/.local/cartopy/shapefiles/.
		or from mydirectory:
			rsync -avP ~ledm/.local/cartopy/shapefiles/* ~/.local/cartopy/shapefiles/.	
TO DO:
	
	
	Needs Improvement.
		Valnote output metrics need to be improved, but are okay right now.

		Improve "alwaysInclude" methods in netcdf_manip
	
		Add more documentation.
	
		Sort out longnames - but ValNote doesn't care, as it only looks at a single metric.
			Replace pftnames.getlongname with something better.
			how about moving long_names into testsuite_p2p? - not really an option.
	
		
		getMT, testsuite_p2p aren't great:
			There has got to be a better way.
			Move extraction function into getMT?
			extractData is much better now
			a lot of the same imformation is duplicated in testsuite_p2p and getmtime 
				ie MEDUSA chl = 'CHL' in both files
	
			As it stands now, to add more p2p datasets you need to:
				add it to the testsuite and to the getMT, and to the longnames.
			
			Move the NameTypes (ie GEOTRACESTypes) into the getmt?	
		
		jobID is explicitly defined in a few places.
		This needs to be set by Valnote/AutoAssess
			(add consistent jobID naming in MEDUSA)
		
		Different types of output data times.
			Currently only works with annual files containing 12 months.
			Can we run with 12 monthly files
			or annual means 
			possibly to be moved around when we slice.
			
			
	Slicing issues:
		 newSlice:
		 	Implement a better slicing method.
		 	For instance: Three different slicing names, one for time, one for depth, one of lat/lon.
	
		Move target diagram faff out of testsuite (related to newSlice)
			made target diagrams out of a series of shelve files
			move shelve File into its own routine?
	
		Make the p2p region cut more generic. 
			Currently only works for WOA depth fields.
		
				
	New things to add and test:
		Investigate a 1D point to point validation at HOTS/BATS.


		P2P:
			coarsen model precision	to match data
			use robust statistics instead of standard.

		Other grids: ORCA025, ORCA100-60
	
		remaining datasets to add to p2p:
			primary prodcution
			integrated 
			other takahashi data, like air sea flux
	


			

