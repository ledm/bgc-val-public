# BGC-val-public toolkit


## Introduction

Originally designed as a toolkit for investigating the time development of the marine biogeochemistry component of the UK Earth system model,
BGC-val has since expanded to become a generic tool for comparing model data against historic data. 

The toolkit is python 2.7 based, and is freely available, and distributed with the BSD 3 clause license. 

An up to date version of BGC-val is availalble in PML's in-house gitlab server.

Registration is required, via this link: http://www.pml.ac.uk/Modelling_at_PML/Access_Code

Once registered, the repositoy is available here: https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/bgc-val-public

Please cite this package as:
 ```
 This information will be provided once the paper is published.
 ```

More details about the BGC-val toolkit can be found in the publication:
```
 This information will be provided once the paper is published.
```



## Goal

The goal was to make the evaluation framework as generic as possible:
* Model independent.
* Grid independent.
* Coordinate independent. 
* Dataset independent.
* Field independent.
* Simple to use.
* Front-loading analysis function
* Iterruptable with regular save points + shelve files.
* Version controlled in git 
* Web visible html summary reports.

We outline the decision and design decisions in the GMD paper above. This 
readme should deal with the pragmatic side of using BGC-val.



# Installation

## Requirements

To use this package, the following python packages are required:
* matplotlib
* netCDF4
* numpy 
* scipy
* cartopy 

If they are not available on your linux system, most of these python packages can be 
installed with the command:
```bash
pip install --user packagename
```
The pip install command is able to download and install a standard python package or module.
By using the --user tag, pip will install a user specific local copy in the home directory.
Without the --user tag, pip will attempt to install the package as root user.
Typically, this requires specific permissions.
For more details on pip, see https://pypi.python.org/pypi/pip


Also, please note that cartopy can be difficult to install. Cartopy has a few requirements: 
including geos, geos-python, geos-devel, proj4, cython etc... 
These packages are not python specific, but rather need to be installed on the system level
(ie, not with pip). If you have sudo rights on your machine, geos, geos-python, geos-devel,
proj4, and cython can be installed using your systems installation tool. (apt-get, dnf, yum,
etc...) More details on Cartopy available here: http://scitools.org.uk/cartopy/

Fortunately, cartopy and these other packages are already available on 
several UK computational systems, such as JASMIN or ARCHER.



## Make a local clone

As BGC-val is not a standard python package, the pip install command (as dscribed above) 
can not be used to download BGC-val. A local copy needs to be made, either by downloading
the repository or using the git clone command. We strongly recommend using the git clone
command, as it makes it easier to keep the package up to date and to send new developments 
back to the central repository.

Make a local clone of the trunk of this package with the command:
```bash
git clone git@gitlab.ecosystem-modelling.pml.ac.uk:ledm/bgc-val-public.git
```

Note that the package name here is subject to change, and that you should check the path
at the top of the github/gitlab repository.

According to the git documentation (https://git-scm.com/docs/git-clone), the git clone 
command produces a clone of a repository into a newly created directory, creates 
remote-tracking branches for each branch in the cloned repository (visible using git 
branch -r), and creates and checks out an initial branch that is forked from the cloned
repository’s currently active branch.

To interact with the gitlab server, you will need to set up ssh keys, which speed line
the process of cloning, and pushing/pulling data from the gitlab. The instructions on how
to do this will appear on the gitlab server. 



## pip install

In your local cloned copy, use the following pip command to make a local installation
of this package:

```bash
pip install --editable --user .
```

By using the --user tag, pip will install a user specific local copy in the home directory.
Without the --user tag, pip will attempt to install the package as root user, which 
requires root permission. By using the --editable tag, this means that the repository 
will be editable. 

If the pip software management system is unavailable on your local system, then 
these packages can be added to the $PYTHONPATH in your shell run configuration
file (ie, bashrc, zshrc or cshrc). This command  is shell specific but in bashrc
it will look like:
```bash
export PYTHONPATH=${PYTHONPATH}:/path/to/bgc-val-public
```



## Keeping BGC-val up to date

The gitlab server can be used to keep your local copy of BGC-val up to date.
In order to keep your copy up to date, you need to pull the updates from the
gitlab. However, git will not  you update your local copy if the changes
would overwrite your edits. 

To update your local copy, you will need to "stage" local changes. Effectively,
this means that you tell git about your edits so it doesn't delete them. The 
commands are:
```bash
git add -u
git commit -m 'Description of your local changes'
```
Note that these commands do not push your changes to the git server.

Once the local copy has been staged, the repository can be updated by pulling
the changes from the remote git server (gitlab/github):
```bash
git pull
```
Note that these commands need to be run from in the directory in your repository.

Note that we can not guarantee that the respository stored on the github version,
or in the supplemental data of the GMD paper will be kept up to date.
However, the gitlab server will be keep up to date. 



## Contributing back to BGC-val

The gitlab server can also be used to share edits and push changes to the main repository.
Howeverm you will most likely not have persmission to push changes to the master copy
of the repository. 

Having said that, the gitlab server has a user friendly graphical user interface. If you
spot an issue in the code, something as big as a bug, or as small as a typo, feel free to
flag it as an issue using the issues page: 
https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/bgc-val-public/issues

There is more advanced stuff too, but don't worry about branches, forks or personal 
copies and and pushing changes until you're comfortable with the rest of git.




# Running BGC-val

Once the package has been installed, please look at the file of ini files and locate one
that is most compatible with your goals and computing system. Our example below uses the
[ini/HadGEM2-ES_no3_cmip5_jasmin.ini](./ini/HadGEM2-ES_no3_cmip5_jasmin.ini) 
configuration file, which directs the evaluation of the CMIP5 hadgem2-es models on the 
JASMIN data processing facility. This is the script that was used to produce several
plots shown in the paper.

Before running the suite, please make a copy of your choosen ini file. Make sure that you
go through your copied configuration file, and check that the paths to data, evaluations 
requested reflect your coputational environment, data paths, and goal of your analyses. 

The default [ini/HadGEM2-ES_no3_cmip5_jasmin.ini](./ini/HadGEM2-ES_no3_cmip5_jasmin.ini)
file has two included analyses switched on in the [Active Keys section](#Active_Keys).

Many of the paths in the [Global Section](#Global_Section) will also need to be changes to
reflect your local environment.

The command to run this evaluation is:
```bash
./run.py ini/HadGEM2-ES_no3_cmip5_jasmin.ini
```

`run.py` is a simple wrapper which calls the script, [analysis_parser.py](#Analysis_Parser), 
and passes it the path to the [config ureation .ini file](#Run_Config_Initialisation_File) file.



## Analysis Parser

[analysis_parser.py](./analysis_parser.py) is a script which parsers the configuration file, 
and then sends the relevant flags, paths, filenames and settings to each of the main analyses 
packages. The configuration file is described below and in the paper. 

The [analysis_parser.py](./analysis_parser.py) script:
1. Loads the configuration file using [./bgcvaltools/configparser.py](./bgcvaltools/configparser.py)
2. Sends the configuration information in the configuration file to the [timeseries/timeseriesAnalysis.py](timeseries/timeseriesAnalysis.py) module to produce the time series analysis.
3. Sends the configuration information in the configuration file to the [timeseries/profileAnalysis.py](timeseries/profileAnalysis.py) module to produce the profile analysis.
4. Sends the configuration information in the configuration file to the [p2p/testsuite_p2p.py](p2p/testsuite_p2p.py) module to produce the point to point evaluatuion.
5. Sends the configuration information to the [timeseries/comparisonAnalysis.py](timeseries/comparisonAnalysis.py) module to compare several models/runs/etc.
6. Sends the configuration information to the  [html/makeReportConfig](html/makeReportConfig) to produce an html report.

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
and a [Global Section](#Global_Section).


The `runconfig.ini` file is parsed by the [bgcvaltools/analysis_parser.py](./bgcvaltools/analysis_parser.py) tool.



## Active Keys

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



## An example of a active Keys section in runconfig.ini

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
  
* The operations in the `data_convert` and `model_convert` options can be any of the operations in `bgc-val-public/stdfunctions.py`
  or they can be taken from a localfuntion in the localfunction directory. More details below in the [Functions](#Functions) section.

* Layers can be selected from a specific list of named layers or transects such as `Surface`, `Equator`, etc..
  Arbitrary Layers or Transects can also be defined in the config.ini:
    * Any integer will load that depth layer from the file.
    * Any number followed by 'm', (ie 500m) will load that depth.
    * Any transect along a latitude or longitude can be defines. ie (60S, or 28W)


* Regions here is a portmanteau for any selection of data based on it's coordinates, or data values.
  Typically, these are spatial regional cuts, such as `NorthernHemisphere`, but the regional cut is not limited to spatial regions.
  For instance, the "January" "region" removes all data which are not in the first month of the year.
  In addition, it is straightforward to add a custom region if the defaults are not suitable for your analysis.
  More details area availalbe in the [Regions](#Regions) section, below.
  
* The `gridFile' option allows BGC-val to locate the grid description file.
  The grid description file is a crucial requirement for BGC-val, as it provides important data about the model mask, 
  the grid cell area, the grid cell volume.
  Minimally, the grid file should be a netcdf which contains  the following information about the model grid:
  * the cell centred coordinates for longitude, lattitude and depth,
  * the land mask should be recorded in the netcdf in a field called `tmask',
  * the cell area should be in a field called `area'
  * and the volume should be recorded in a field labelled `pvol'.
  Certain models use more than one grid to describe the ocean; for instance NEMO uses a U grid, a V grid, a W grid, and a T grid.
  In that case, then care needs to be taken to ensure that the grid file provided matches the data.
  BGC-val includes the meshgridmaker module in the  bgcvaltools package 
  and the function `makeGridFile' from that module can be used to produce a grid file.



## Global Section

The `[Global]` section of the `runconfig.ini` file contains the global flags and the default settings for each field.
For instance, the model calendar, defined in `model_cal` is unlikely to differ between analyses, so it can safely
be set as a default value the `[Global]` section and ommited elsewhere. 

The Global options `jobID`, `year`, `model` and  `scenario` can be singular values.
For instance, if the evaluation only needs to run over one model, year, jobID, or scenario.
However, any of these options can be set to multiple fields in by instead using the options: `jobIDs`, `years`, `models` and  `scenarios`.
For instance, if the evaluation needs to compare multiple models, years, jobs or scenarios.

In addition, the values defined in the `[Global]` for `jobID`, `year`, `model` and  `scenario`
can be used to define specific paths at runtime. 
For instance, paths using `$JOBID`, `$YEAR` or `$MODEL`.
Similarly, `$NAME` can be used as a stand in for the name option for of each analysis. 

Some values can not be set in the `[Global]`, for instance the `name`, and `model_vars`
and `model_convert` fields are by definition unique for each analysis.


The following is a typical `[Global]` section:
```ini
[Global]
jobID             : u-am927              ; Unique run/simulation/job identifier
years             : 1980 1990            ; Year to look at for p2p.
model             : MEDUSA               ; model name
scenario	  : historical		 ; scenario


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



## Functions

The `data_convert` and `model_convert` options in the analysis section of the `runconfig.ini` file are used 
to give apply a python function to the data as it is loaded. 

Typically, this is a quick way to convert the model or data so that they use the same units.
With this is mind, most of the standard functions are basic convertions such as 
* multiply by 100.
* Divide by 1000
* Add multple fields together
* Or simply do nothing, just load one field as is.


However, more complex functions can also be applied, for instance:
* Depth integtation
* Global Total sum
* Flux through a certain cross section.



The operations in the `data_convert` and `model_convert` options can be any of the operations in `bgc-val-public/stdfunctions.py`.
They can be also taken from a localfuntion in the localfunction directory. More details below in the [Functions](#Functions) section.

These functions take the netcdf as a dataset object. 
The dataset class defined in bgcvaltools/dataset.py and based on netCDF4.Dataset with added functionaility. 



## Layers

Layers can be selected from a specific list of named layers or transects such as `Surface`, `Equator`, etc..

Any arbitrary depth layer or transects along a constant lattitude or congitude can also be defined in the `runconfig.ini` file:
* Any integer will load that depth layer from the file.
* Any number followed by 'm', (ie `500m`) will calucate the layer of that depth, then extract that layer. 
* Any transect along a latitude or longitude can be defines. ie (60S, or 28W). This works for both 1 and 2 dimensional coordinate systems.



## Regions

The `regions/` directory contains tools that are used to mask out unwanted regions in the data.
For instance, these tools can be used to:
* Remove negative values.
* Remove zero values
* Remove data outside a certain depth range.
* Remove data outside a latituge or longitude range. 

The function produces a mask to hides all points that are not in the requested region.

The list of regions requested is set in the `runconfig.ini` `regions` option, both in the `[Global]` section
and for each field.


The full list of "Standard masks" is defined in the file `regions/makeMask.py`, 
but it is straightforward to add a custom region using the template file, `regions/customMaskTemplate.py`.
Simply make a copy of this file in the regions folder, rename the function to your mask name,
and add whatever cuts you require.

Each regional masking function has access to the following fields:
* name: The name of the data. (useful for debugging)
* region: The name of the regional cut (or slice)
* xt: A one-dimensional array of the dataset times.
* xz: A one-dimensional array of the dataset depths.
* xy: A one-dimensional array of the dataset latitudes.
* xx: A one-dimensional array of the dataset longitudes.
* xd: A one-dimensional array of the data.


It is possible stack masks, simply by adding the masks together. 
For instance, the masking function here excludes all
data outside the equatorial region and below 200m depth.

```python
from regions.makeMask import Shallow, Equator10
def ShallowEquator(name,newSlice, xt,xz,xy,xx,xd,debug=False):
	newmask = np.ma.array(xd).mask
	newmask += Shallow(name,newSlice, xt,xz,xy,xx,xd)
	newmask += Equator10(name,newSlice, xt,xz,xy,xx,xd)	
 	return newmask	
```

However, more complex masking is also possible, for instance in the file `regions/maskOnShelf.py`
which loads a bathymetry file and masks all points in water columns shallower than 500m.


Please note that:
* The name of the function needs to match the region in your `runconfig.ini` file.
* Note that xt,xz,xy,xx,xd should all be the same shape and size. 
* These cuts are applied to both the model and the data files.	
	
		
	
## Longnames

This is a folder which contains dictionaries in .ini format.

These are the pretty public-facing long names for all the python objects, strings and other fields used in the bgc-val.

The index (or key or option) of the .ini file is the name of the field in the code, and the 
value (or item ) in  the dictionairy is the long name, which is used in plots, tables and html. 

For instance:
```ini
[LongNames]
n_mn                                 : Mean Nitrate
sossheig                             : Sea Surface Height
lat                                  : Latitude
```

The dictionaries are loaded at runtime by `longnames/longnames.py`. This script loads all .ini files in the `longnames/` directory.
Users can easilly add their own dictionairies here, without disturbing the main longname.ini dictionairy.

The longname for a specific field is called with:
```python
from longnames.longnames import getLongName
string = 'CHL'
ln = getLongName(string)
```
Note that if a longname is not provided, the string is returned unchanged. 



# The analysis packages

In this section of the `README.md` we look at the programming decisions that were made 
in the design process of the BGC-val suite.


## Time Series (TS)

This looks at a series of consequtive model files and produces various time series analysis.
The files needed to run this are hosted in the `timeseries` directory.
The idea behind the time series tool is to try to understand the model data one time step at 
a time, then produce visualisations that clearly show the time development of the model.

The main time series script is `timeseriesAnalysis.py` in the `timeseries` directory.
The script checks to see whether the model and observatioal data are present. 
Then it loads the observational data (if present) and then the model data.
Both the model and observatioal data are loaded with the DataLoader tool in the 
`timeseriesTools.py` file in the `timeseries` directory.
This process creates a python dictionairy where the processed data is indexed according to :
`(region, layer, metric)`.
The processed model data is stored as another dictionary. 
The second layer dictionairy uses the model's calendar year (converted into a float) as
the index, and the value is the processed model data associated with that time and `(region, layer, metric)`.
This nested dictionary object is called modeldataD in the `timeseriesAnalysis.py`.
Each modeldataD is stored in a shelve file.

This double nested dictionary may seem confusing, but it safer than parrallel 
arrays used elsewhere. For instance, an example of loading this file from shelve would be:
`modeldataD['Global','Surface','Mean'][1955.5]`
would produce the Global surface mean of the year 1955. 

The modeldataD are stored as shelves and are openned by several of the plotting tools, but can also be opened manually in the command line.

The times series produces plots using the `timeseriesPlots.py` file in the `timeseries` directory..
This file contains several python functions which use matplotlib to create visualisations 
of the time series and profile data.
The simple times series, the traffic lights plots, the multitimeseries,
map plots, hovmoeller plots, and profile plots are all produced by functions in this file.
 
The time series directory also includes the `timeseriesTools.py` script.
This toolkit contains several functions used by the other files in the time series folder. 

The time series directory also includes the `extentMaps.py` and `extentProfiles.py` scripts,
which allow users to make maps showing the extent of the data that sits above or below a certain threshold.

The time series directory also includes the `analysis_level0.py` tool which is used to produce an
html summary table of the final years of a simulation. 



## Profile Plots

This produces plots showing the time development of the depth-profile of the model.
The files needed to run this are hosted in the the `timeseries` directory.

The profile tools use many of the same processes and tools as the time series analyses,
however instead of running them over one layer, it runs them over many layers in succession.



## Comparison plots

This tool produces plots showing the time development comparing several models/scenarios/jobs 
of the model. The files needed to run this are hosted in the  `comparisonAnalysis.py` scrinpt in the
`timeseries` directory.



## Point to point
This produces a point to point comparison analysis of the model versus data for a single year, including statistical analysis, spatial mapping etc.
The files needed to run this are hosted in the the `p2p` directory.



## Report Maker

This takes all the plots produced and summarises them in an html document.
The files needed to run this are hosted in the the `html` directory.

The `html` folder contains several templates, some python tools and lots of html assets (css, fonts, js, sass, images).

The html report was based on a template provided by html5up.net under the CCA 3.0 license.

The primary python tool used to produve html reports from a configuration file is the
`makeReportConfig.py` file. 
This includes a function that loads the configuration file, then figures out what was requested,
a pushes this all into a self contained html site.
The html folder can be copied into a web facing server, or opened directly using firefox.

The location of the report on disk is determined by the global flag.



# References:

A description of the point to point methods used here is available in: 
de Mora, L., Butenschön, M., and Allen, J. I.: How should sparse marine in situ measurements be compared to a continuous model: an example, Geosci. Model Dev., 6, 533-548, https://doi.org/10.5194/gmd-6-533-2013, 2013.


                                

                        

