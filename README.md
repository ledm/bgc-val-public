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

Please cite this package as: 

# Requirements

To use this package, the following python packages are required:
* matplotlib
* netCDF4
* numpy 
* scipy
* cartopy 
* https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/netcdf_manip

Access to this packages can be requested via the web form: http://www.pml.ac.uk/Modelling_at_PML/Access_Code

 
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

Using default settings, this will produce a workingdir directory, an images directory, and a reports directory. 

These three directories will hold:
* workingdir: Post processed files for each of the analyses.
* images: The .png image files that are produced.
* reports: the html report which can be viewed using a web browser.

`run.py` is a simple wrapper which calls the script, [analysis_parser.py](#Analysis_Parser), and passes it the path to the [runconfig.ini](#Run_Config_Initialisation_File) file.

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




### Global Section

The `[Global]` section of the `runconfig.ini` file contains the global flags and the default settings for each field.

For instance, the model calendar, defined in `model_cal` is unlikely to differ between analyses, so it can safely
be set in the `[Global]` section and ommited elsewhere. 

Some values can not be set in the `[Global]`, for instance the `name`, and `model_vars`
and `model_convert` fields are by definition unique for each analysis.

The values used in `[Global]` for `jobIDs`, `years`, `models` and  `scenarios` can be put into paths using `$JOBID`, `$YEAR` or `$MODEL`.
Similarly, `$NAME` can be used as a stand in for the name option for of each analysis. 

In addition, multiple analyses can be compared by using a list of jobIDs. 



The following is a typical `[Global]` section:
```ini
[Global]

jobIDs            : u-am927              ; Unique run/simulation/job identifier
years             : 2055                 ; Year to look at for p2p.
models            : MEDUSA               ; model name
scenarios	  : historical		 ; scenario

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




# Functions

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



# Layers

Layers can be selected from a specific list of named layers or transects such as `Surface`, `Equator`, etc..

Any arbitrary depth layer or transects along a constant lattitude or congitude can also be defined in the `runconfig.ini` file:
* Any integer will load that depth layer from the file.
* Any number followed by 'm', (ie `500m`) will calucate the layer of that depth, then extract that layer. 
* Any transect along a latitude or longitude can be defines. ie (60S, or 28W). This works for both 1 and 2 dimensional coordinate systems.










# Regions

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
	
	
	
	
	
	
# Longnames

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


# References:

A description of the point to point methods used here is available in: 
de Mora, L., Butenschön, M., and Allen, J. I.: How should sparse marine in situ measurements be compared to a continuous model: an example, Geosci. Model Dev., 6, 533-548, https://doi.org/10.5194/gmd-6-533-2013, 2013.


                                

                        

