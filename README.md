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



# Requirements

To use this package, the following python packages are required:
* matplotlib
* netCDF4
* numpy 
* scipy
* cartopy 
* https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/netcdf_manip

Most of these packages can be installed with the command:

```bash
pip install --user packagename
```
        
Please note that cartopy can be difficult to install, with many requirements: such as geos, geos-python, geos-devel, proj4, cython etc… (http://scitools.org.uk/cartopy/)



# Installation

Once the required packages have been installed, make a local clone of the trunk of this package with the command:
```bash       
git clone git@gitlab.ecosystem-modelling.pml.ac.uk:ledm/bgc-val-public.git
```

Note that the package name here is subject to change, and that you should check the path at the top of this page.

In the local copy, use the following pip command to make a local installation of this package:

```bash
pip install -e . --user
```



# Running

Once the package has been installed, make a copy of the bgc-val-public/run directory in your working directory.

The run directory will contain:
* run.py: The main script that runs the analysis.
* runconfig.ini: The main configuration script that contains all information, flags, paths and settings needed to produce the analysis.
* localfunctions directory: This directory is where you should put any custom analysis functions that you may want to use to load or manipuate your data.

The command to  run the evaluation is:
```bash
./run.py
```
`run.py` is a simple wrapper which calls the script, [analysis_parser.py](#Analysis_Parser), and passes it the path to the [runconfig.ini](#Run_Config_Initialisation_File) file.

Using default settings, this will produce a workingdir directory, an images directory, and a reports directory. 
These three directories will hold:
* workingdir: Post processed files for each of the analyses.
* images: The .png image files that are produced.
* reports: the html report which can be viewed using a web browser.

## Analysis Parser

`analysis_parser.py` is a script which parsers the runconfig.ini file, and then sends the relevant flags, paths, filenames
and settings to each of the main analyses packages. 
The analysis packages called are:
* Time Series (TS): This looks at a series of consequtive model files and produces various time series analysis.
* Profile Plots: This produces plots showing the time development of the depth-profile of the model.
* Point to point: This produces a point to point comparison analysis of the model versus data for a single year, including statistical analysis, spatial mapping etc.
* Report Maker: This takes all the plots produced and summarises them in an html document.

The location of the model and data files, the description of the files, the regions, times, depth layers under investgation
are all set in the runconfig.ini file. 



## Run configuration initialisation file

The `runconfig.ini` file contains all information, flags, paths and settings needed to produce the analysis.

Note that config files use the following convention:
```ini
[Section]
option : value
; comment
```

When loading the config file into python's module `ConfigParser`, beware that:
* Sections hold capitalisation
* Options all become lowercase
* Values are parsed as strings
* End of line comments require a space or tab before the ';'


The parser expects an [Active Keys](#Active_Keys) section, a section for each key in `[ActiveKeys]`
and a [Global Section])#Global_Section).


The `runconfig.ini` file is parsed by the [bgcvaltools/analysis_parser.py](./bgcvaltools/analysis_parser.py) tool.


### Active Keys

The `[ActiveKeys]` section contains the boolean switches that activate the analysis sections described elsewhere in the `runconfig.ini` file.
The order of the active keys here determines the order that the analysis runs and also the order each field appears in the final html report.
Keys are switched on by being set to `True` and are switched off by being set to `False` or being commented out with a leading ';'.

Each live key in the `[ActiveKeys]` section requires another section with the same name in `runconfig.ini`. ie:
```ini
[ActiveKeys]        
Chlorophyll         : True

[Chlorophyll]
; Chlorophyll analysis details:
...

```



### An exmaple of a active Keys section in runconfig.ini

The following is an example of the options  needed to produce a typical 2D analysis.
In this case, this is a comparison of the surface chlorophyll in MEDUSA against the CCI satellite chlorophyll product.

```ini
[Chl_CCI]
name            : Chl_CCI               ; The name of the analysis.
units           : mg C/m^3              ; The final units, after any transformation function has been applied.
datasource      : CCI                   ; The name of the data source
model           : MEDUSA                ; The name of the model
modelgrid       : eORCA1                ; The name of the model grid
dimensions      : 2                     ; The dimensionaility of the final product.

; -------------------------------
; The filenames                         ; This is a list of paths for the model, model grid and the data file.
modelFiles      : /data/euryale7/scratch/ledm/UKESM/MEDUSA/$JOBID/medusa*_1y_*_ptrc-T.nc
modelFile_p2p   : /data/euryale7/scratch/ledm/UKESM/MEDUSA/$JOBID/medusa*_1y_*$YEAR????_ptrc-T.nc
gridFile        : /data/euryale7/scratch/ledm/UKESM/MEDUSA/mesh_mask_eORCA1_wrk.nc
dataFile        : /data/euryale7/backup/ledm/Observations/CCI/ESACCI-OC-L3S-OC_PRODUCTS-CLIMATOLOGY-16Y_MONTHLY_1degree_GEO_PML_OC4v6_QAA-annual-fv2.0.nc

; -------------------------------
; Model coordinates/dimension names
model_t         : time_centered         ; The time dimension used in the model netcdf.
model_cal       : 360_day               ; The calendar used in the model netcdf.        
model_z         : deptht                ; The depth dimension used in the model netcdf.
model_lat       : nav_lat               ; The latitude dimension used in the model netcdf.
model_lon       : nav_lon               ; The longitude dimension used in the model netcdf.
model_vars      : CHD CHN               ; The names of the fields used in the model netcdf.
model_convert   : sum                   ; The operation applied to the fields in model_vars

; -------------------------------
; Data coordinates names
data_t          : time                  ; The time dimension used in the data netcdf.
data_cal        : standard              ; The calendar used in the data netcdf.
;data_z         : index_z               ; The depth dimension used in the modatadel netcdf. Note that CCI is a surface only product, so no depth field is provided.
data_lat        : lat                   ; The latitude dimension used in the data netcdf.
data_lon        : lon                   ; The longitude dimension used in the data netcdf.
data_vars       : chlor_a               ; The names of the field used in the data netcdf.
data_convert    : NoChange              ; The operation applied to the fields in data_vars.
data_tdict      : ZeroToZero            ; The calendar used in the data netcdf.

layers          : Surface               ; A List of layers or transects to investigate the data.
regions         : Global                ; The regional cuts to make.
```

Note that:
* Many of these fields can be defined in the `[Global]` section, and ommited here, as long as they are the same between all the analyses.
  For instance, the model calendar, defined in `model_cal` is unlikely to differ between analyses. 
  More details below in the [Global Section](#Global_Section_of_the_runconfig.ini) section.
  
* The operations in the `data_convert` and `model_convert` options can be any of the operations in bgc-val-public/functions.py
  or they can be taken from a localfuntion in the localfunction directory. More details below in the [Functions](#Functions) section.

* Layers can be selected from a small list of specific depths, such as `Surface`, `100m`, `500m`, `All` etc... Or from a specific list of 
  Ocean transects, such as `Equator`, more details in the [Layers](#Layers) section, below.

* Regions here is a portmanteau for any selection of data based on it's coordinates, or data values.
  Typically, these are spatial regional cuts, such as `NorthernHemisphere`, but the regional cut is not limited to spatial regions.
  For instance, the "January" "region" removes all data which are not in the first month of the year.
  In addition, it is straightforward to add a custom region if the defaults are not suitable for your analysis.
  More details area availalbe in the [Regions](#Regions) section, below.




### Global Section

The `[Global]` section of the `runconfig.ini` file contains the global flags and the default settings for each field.

For instance, the model calendar, defined in `model_cal` is unlikely to differ between analyses, so it can safely
be set in the `[Global]` section and ommited elsewhere. 

Some values can not be set in the `[Global]`, for instance the `name`, and `model_vars`
and `model_convert` fields are by definition unique for each analysis.

The values used in `[Global]` for `jobID`, `year`, `model` can be put into paths using `$JOBID`, `$YEAR` or `$MODEL`.
Similarly, `$NAME` can be used as a stand in for the name option for of each analysis. 



The following is a typical `[Global]` section:
```ini
[Global]

jobID            : u-am927              ; Unique run/simulation/job identifier
year             : 2055                 ; Year to look at for p2p.
model            : MEDUSA               ; model name

; -------------------------------
; Boolean flags
clean            : False ;              ; Boolean flag to make a run from scratch.
makeTS           : True ;               ; Boolean flag to make the time series plots.
makeProfiles     : True ;               ; Boolean flag to make the 3D profile.
makeP2P          : True ;               ; Boolean flag to make the P2P plots.
makeReport       : True ;               ; Boolean flag to make the report.

; -------------------------------
; Output Images folders
images_ts        : images/$JOBID/timeseries/$NAME
images_pro       : images/$JOBID/profiles/$NAME
images_p2p       : images/$JOBID/p2p/$MODEL-$YEAR/$NAME

; -------------------------------
; Working directories
postproc_ts      : workingdir/$JOBID/timeseries/$NAME
postproc_pro     : workingdir/$JOBID/profiles/$NAME
postproc_p2p     : workingdir/$JOBID/p2p/$MODEL-$NAME-$YEAR

; -------------------------------
; location to put the html report 
reportdir        : reports/$JOBID

; -------------------------------
; These are the default model coordinates
model_t          : time_centered        ; model time dimension
model_cal        : 360_day              ; model calendar
model_z          : deptht               ; model depth dimension
model_lat        : nav_lat              ; model latitude dimension 
model_lon        : nav_lon              ; model latitude dimension 

; -------------------------------
; Default model grid file
modelgrid        : eORCA1                                                                  ; Model grid name
gridFile         : /data/euryale7/scratch/ledm/UKESM/MEDUSA/mesh_mask_eORCA1_wrk.nc        ; Model grid file

; -------------------------------
; The default data details. The default for these is empty, as the time series suite can run without a data file.
data_t           :
data_cal         : 
data_z           : 
data_lat         : 
data_lon         : 
data_tdict       : 
dataFile         : 
```

Please note that by deault, the images and working directory are created in the run directory, unless otherwise specified.


# Functions



# Layers


# Regions


# Longnames

        
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
                        coarsen model precision        to match data
                        use robust statistics instead of standard.

                Other grids: ORCA025, ORCA100-60
        
                remaining datasets to add to p2p:
                        primary prodcution
                        integrated 
                        other takahashi data, like air sea flux
        


                        

