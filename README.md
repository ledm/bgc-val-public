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

The [analysis_parser.py](./analysis_parser.py) is the central script which parsers the configuration
file, and then sends the relevant flags, paths, filenames and settings to each of the main analyses 
packages. The configuration file is described below and in the paper. 

The [analysis_parser.py](./analysis_parser.py) script performs the following actions:

1. Loads the configuration information from the configuration file using 
   the [./bgcvaltools/configparser.py](./bgcvaltools/configparser.py) module.

2. Sends the configuration information in the configuration file to the 
   [timeseries/timeseriesAnalysis.py](timeseries/timeseriesAnalysis.py) module 
   to produce the time series analysis.
   
3. Sends the configuration information to the 
   [timeseries/profileAnalysis.py](timeseries/profileAnalysis.py)
   module to produce the profile analysis.
   
4. Sends the configuration information to the [p2p/testsuite_p2p.py](p2p/testsuite_p2p.py)
   module to produce the point to point evaluatuion.
   
5. Sends the configuration information to the [timeseries/comparisonAnalysis.py](timeseries/comparisonAnalysis.py)
   module to compare several models/runs/scenarios etc.
   
6. Sends the configuration information to the  [html/makeReportConfig](html/makeReportConfig.py)
   to produce an html report based on the outputs of stages 2-5. 
   
These individual modules are all internally documented, and each function should have a (albeit) short
description. 




# Configuration file

The configuration file is central to the running of BGC-val 
and contains all the details needed to evaluate a simulation.
This includes the file path of the input model files,
the users choice of analysis regions, layers and functions,
the names of the dimensions in the model and observational files,
the final output paths, and many other settings. All settings 
and configuration choices are recorded in an single file, 
using the `.ini` format. Several example configuration files can 
also be found in the `ini` directory. Each BGC-val configuration
file is composed of three parts: an Active keys section, a list
of evaluation sections, and a Global section. Each of these 
parts are described below.

The tools that parse the configuration file is in the 
`configparser.py` module in the `bgcvaltools` package.
These tools interpret the configuration file and
use them to direct the evaluation.
Please note that we use the standard `.ini` format
nomenclature while describing configuration files.
In this, `[Sections]` are denoted with square brackets,
each option is separated from its value by a colon, ``:'',
and the semi-colon ``;'' is the comment syntax in  `.ini` format:
```ini
[Section]
option : value
; comment
```


## Active keys section

The active keys section should be the first section of any BGC-val configuration file.
This section consists solely of a list of Boolean switches,
one Boolean for each field that the user wants to evaluate:

```ini
[ActiveKeys]
Chlorophyll     : True
A               : False
; B             : True
```

To reiterate the `ini` nomenclature, in this example
`ActiveKeys` is the section name,
and `Chlorophyll`, `A`, and `B` are options.
The values associated with these options are the Boolean's, 
`True`, `False`, and `True`. 
The option `B` is commented out and will be ignored by BGC-val.

In the `[ActiveKeys]` section, only options whose values are set to `True` are active.
False Boolean's values and commented lines are not evaluated by BGC-val.
In this example, the `Chlorophyll` evaluation is active,
but both options `A` and `B` are switched off.


## Individual evaluation sections

Each `True` Boolean options in the `[ActiveKeys]` section
needs an associated `[Section]` with the same name
as the option in `[ActiveKeys]` section.
The following is an example of an evaluation 
section for chlorophyll in the HadGEM2-ES model.


```ini
[Chlorophyll]
name             : Chlorophyll
units            : mg C/m^3

; The model name and paths
model            : HadGEM2-ES
modelFiles       : /Path/*.nc
modelgrid        : CMIP5-HadGEM2-ES
gridFile         : /Path/grid_file.nc


; Model coordinates/dimension names
model_t          : time
model_cal        : auto
model_z          : lev
model_lat        : lat
model_lon        : lon

; Data and conversion
model_vars       : chl
model_convert    : multiplyBy
model_convert_factor : 1e6
dimensions       : 3


; Layers and Regions
layers           : Surface 100m
regions          : Global SouthernOcean
```


The `name` and `units` options are descriptive only;
they are shown on the figures and in the html report, but do not influence the calculations.
This is set up so that the name associated with the analysis may be different to the
name of the fields being loaded.
Similarly, while NetCDF files often have units associated with each field, 
they may not match the units after the user has applied an evaluation function. 
For this reason, the final units after any transformation must be supplied by the user.
In the example showed here, HadGEM2-ES correctly used the CMIP5 standard units
for chlorophyll concentration, kg m$^{-3`$.
However, we prefer to view Chlorophyll in units of mg m^-3 .

The `model` option is typically set in the `Global` section, described below
but it can be set here as well.
The `modelFiles` option is the path that BGC-val should use to locate the model data files on local storage.
The `modelFiles` option can point directly at a single NetCDF file,
or can point to many files using wild-cards (`*`, `?`).
The file finder uses the standard python package, `glob`, 
so wild-cards must be compatible with that package.
Additional nuances can be added to the file path parser using the
placeholders `$MODEL`, `$SCENARIO`, `$JOBID`,
`$NAME` and `$USERNAME`.
These placeholders are replaced with the appropriate 
global setting they are read by the `configparser` package.
The global settings are described below 
For instance, if the configuration file is set to iterate over several models,
then the `$MODEL` placeholder will be replaced by 
the model name currently being evaluated.

The `gridFile` option allows BGC-val to locate the grid description file.
The grid description file is a crucial requirement for BGC-val, 
as it provides important data about the model mask, 
the grid cell area, the grid cell volume.
Minimally, the grid file should be a NetCDF which contains 
the following information about the model grid:
the cell centred coordinates for longitude, latitude and depth,
and these fields should use the same coordinate system as the field currently being evaluated.
In addition, the land mask should be recorded in the grid description NetCDF in a field called `tmask`,
the cell area should be in a field called `area`
and the cell volume should be recorded in a field labelled `pvol`.
BGC-val includes the `meshgridmaker` module in the  `bgcvaltools` package
and the function `makeGridFile` from that module can be used to produce a grid file.
The `meshgridmaker` module can also be used to calculate 
the cross sectional area of an ocean transect, which is used in several 
flux metrics such as the Drake passage current or the Atlantic Meridianal Overturning circulation.

Certain models use more than one grid to describe the ocean; 
for instance NEMO uses a U grid, a V grid, a W grid, and a T grid.
In that case, care needs to be taken to ensure that the grid file provided matches the data.
The name of the grid can be set with the `modelgrid` option.

The names of the coordinate fields in the NetCDF need to be provided here.
They are `model_t` for the time, `model_cal` for the model calendar.
Any NetCDF calendar option (360_day, 365_day, standard, Gregorian, etc ...)
is also available using the `model_cal` option, however, the code will
preferentially use the calendar included in standard NetCDF files.
For more details, see the `num2date` function of the
`netCDF4` python package, https://unidata.github.io/netcdf4-python/.
The depth, latitude and longitude field names are passed to BGC-val 
via the `model_z`, `model_lat` and `model_lon` options.

The `model_vars` option tells BGC-val the names of the model fields that we are interested in.
In this example, the CMIP5 HadGEM2-ES chlorophyll field
is stored in the NetCDF under the field name `chl`.
As mentioned already, HadGEM2-ES used the CMIP5 standard units
for chlorophyll concentration, kg m$^-3 , 
but we prefer to view Chlorophyll in units of mg m^-3 .
As such, we load the chlorophyll field using the conversion function,
`multiplyBy` and give it the argument 1e6
with the `model_convert_factor` option.
More details are available below.

BGC-val uses the coordinates provided here to extract 
the layers requested in the `layers` option
from the data loaded by the function in the `model_convert` option.
In this example that would be the surface and the 100~m depth layer.
For the time timeseries and profile analyses, 
the layer slicing is applied in the 
`DataLoader` class in the 
`timeseriesTools` module of 
the `timeseries` package.
For the point to point analyses, 
the layer slicing is applied in the 
`matchDataAndModel` class in the `matchDataAndModel` module of 
the `p2p` package.

Once the 2D field has has been extracted, 
BGC-val masks the data outside the regions requested in the `regions` option.
In this example, that is the `Global` and the `SouthernOcean` regions.
These two regions are defined in the `regions` package in the `makeMask` module.
This process is described below.


The `dimensions` option tells BGC-val what the dimensionality
of the variable will be after it is loaded, but before it is masked or sliced.
The dimensionality of the loaded variable affects how the final results are plotted.
For instance, one dimensional variables 
such as the global total primary production
or the total northern hemisphere ice extent can not be
plotted with a depth profile, or with a spatial component.
Similarly, two dimensional variables such 
as the air sea flux of CO_2 or the mixed layer depth 
shouldn't be plotted as a depth profile, 
but can be plotted with percentiles distribution.
Three dimensional variables such as the
temperature and salinity fields, the nutrient concentrations,
and  the biogeochemical advected tracers 
are plotted with time series, 
depth profile, and percentile distributions.
If any specific types of plots are possible but not wanted, 
they can be switched off using one of the following options:
```ini
makeTS          : True
makeProfiles    : False
makeP2P         : True
```
The `makeTS` options controls the time series plots,
the `makeProfiles` options controls the profile plots,
and the `makeP2P` options controls the point to point evaluation plots.
These options can be set for each Active Keys section, 
or they can be set in the global section, described below.

In the case the HadGEM2-ES's chlorophyll section, shown in this example,
the absence of an observational data file means that some evaluation figures
will have blank areas, and others figures will not be made at all.
For instance, it's impossible to produce a 
point to point comparison plot without both model
and observational data files.
The evaluation of `[Chlorophyll]` could be expanded by mirroring the model's coordinate and convert fields
with a similar set of data coordinates and convert functions for an observational dataset.



## Global section

The `[Global]` section of the configuration file
can be used to set default behaviour which is common to many evaluation sections.
This is because the evaluation sections of the configuration file
often use the same option and values in several sections.
As an example, the names that a model uses for
its coordinates are typically the same between fields;
i.e. a Chlorophyll data file will use the same name for
the latitude coordinate as the Nitrate data file from the same model.
Setting default analysis settings 
in the `[Global]` section ensures that
they don't have to be repeated in each evaluation section.
As an example, the following is a small part of a global settings section:
```ini
[Global]
model           : ModelName
model_lat       : Latitude
```
These values are now the defaults,
and individual evaluation sections of this configuration file
no longer require the `model` or `model_lat` options.
However, note that local settings override the global settings.
Note that certain options such as `name` or `units`
can not be set to a default value. 

The global section also includes some options
that are not present in the individual field sections.
For instance, each configuration file can 
only produce a single output report,
so all the configuration details regarding the
html report are kept in the global section:
```ini
[Global]
makeComp        : True
makeReport      : True
reportdir       : reports/HadGEM2-ES_chl
```
where the `makeComp` is a Boolean flag to turn on the comparison of multiple jobs, models or scenarios.
The `makeReport` is a Boolean flag which turns on the global report making
and `reportdir` is the path for the html report.

The global options `jobID`, `year`,
`model` and `scenario` can be set to a single value, or
can be set to multiple values (separated by a space character),
by swapping them with the options: `jobIDs`, `years`,
`models` or `scenarios`.
For instance, if multiple models were requested, then swap:
```ini
[Global]
model           : ModelName1
```

with the following:
```ini
[Global]
models          : ModelName1 ModelName2
```

For the sake of the clarity of the final report, we recommend only setting
one of these options with multiple values at one time.
The comparison reports are clearest when
grouped according to a single setting
ie, please don't try to compare too many different models, scenarios, and jobIDs at the same time.

The `[Global]` section also holds the paths to the location on disk 
where the processed data files and the output images are to be saved.
The images are saved to the paths set with the following global options:
`images_ts`, `images_pro`, `images_p2p`, `images_comp`
for the timeseries, profiles, point to point and comparisons figures, respectively.
Similarly, the post processed data files are saved to the paths set with the following global options:
`postproc_ts`, `postproc_pro`, `postproc_p2p`
for the timeseries, profiles, and point to point processed data files respectively.


As described above, the global fields `jobID`, `year`,
`model` and `scenario`
can be used as placeholders in file paths.
Following the bash shell grammar, 
the placeholders are marked as all capitals with a leading $ sign.
For instance, the output directory for the time series images could be set to:
```ini
[Global]
images_ts : images/$MODEL/$NAME
```
where `$MODEL` and `$NAME` are placeholders for the
model name string and the name of the field being evaluated.
In the example in sect.~ref{sec:confevalsections` above,
the `images_ts` path would become:
`images/HadGEM2-ES/Chlorophyll`.
Similarly, the `basedir_model` and `basedir_obs` global options
can be used as fill the placeholders `$BASEDIR_MODEL` and `$BASEDIR_OBS`
such that the base directory for models or observational data don't need to be repeated
in every section.

A full list of the contents of a global section can be found in the `README.md` file.
Also, several example configuration files are available in the `ini`.



* Many of these fields can be defined in the `[Global]` section, and ommited here, as long as they are the same between all the analyses.
  For instance, the model calendar, defined in `model_cal` is unlikely to differ between analyses. 
  More details below in the [Global Section](#Global_Section_of_the_configuration file) section.











## A note on grid files:

The `gridFile' option allows BGC-val to locate the grid description file.
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



# User configurable python packages


## Functions

The `data_convert` and `model_convert` options in the analysis section of the configuration 
file are used to give apply a python function to the data as it is loaded. 

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

Any arbitrary depth layer or transects along a constant lattitude or congitude can also be defined in the configuration file:
* Any integer will load that depth layer from the file.
* Any number followed by 'm', (ie `500m`) will calucate the layer of that depth, then extract that layer. 
* Any transect along a latitude or longitude can be defines. ie (60S, or 28W). This works for both 1 and 2 dimensional coordinate systems.

* Layers can be selected from a specific list of named layers or transects such as `Surface`, `Equator`, etc..
  Arbitrary Layers or Transects can also be defined in the config.ini:
    * Any integer will load that depth layer from the file.
    * Any number followed by 'm', (ie 500m) will load that depth.
    * Any transect along a latitude or longitude can be defines. ie (60S, or 28W)


## Regions

The `regions/` directory contains tools that are used to mask out unwanted regions in the data.
For instance, these tools can be used to:
* Remove negative values.
* Remove zero values
* Remove data outside a certain depth range.
* Remove data outside a latituge or longitude range. 

The function produces a mask to hides all points that are not in the requested region.

The list of regions requested is set in the configuration file `regions` option, both in the `[Global]` section
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
* The name of the function needs to match the region in your configuration file.
* Note that xt,xz,xy,xx,xd should all be the same shape and size. 
* These cuts are applied to both the model and the data files.	
	

* Regions here is a portmanteau for any selection of data based on it's coordinates, or data values.
  Typically, these are spatial regional cuts, such as `NorthernHemisphere`, but the regional cut is not limited to spatial regions.
  For instance, the "January" "region" removes all data which are not in the first month of the year.
  In addition, it is straightforward to add a custom region if the defaults are not suitable for your analysis.
  More details area availalbe in the [Regions](#Regions) section, below.

		
	
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


# Primary python packages


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


                                

                        

