#
# Copyright 2014, Plymouth Marine Laboratory
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
.. module:: BGC-val python
   :platform: Unix
   :synopsis: A swiss army knife of tools for BGCval.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
from sys import argv
from string import join
from os.path  import exists,getmtime
from os import mkdir, makedirs
import os
import math
from glob import glob
from itertools import product,izip
import numpy as np

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

from matplotlib import pyplot,gridspec
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import LogNorm

from netCDF4 import num2date
from datetime import datetime
from bgcvaltools.dataset import dataset
try:
	import cartopy.crs as ccrs
	import cartopy.io.shapereader as shapereader
	from cartopy import img_transform, feature as cfeature	
except:
	print "Unable to load Cartopy"
from scipy.stats.mstats import scoreatpercentile
from scipy.stats import linregress,mode as scimode
from calendar import month_name
from shelve import open as shOpen
import socket

from  bgcvaltools.RobustStatistics import MAD
try:import yaml 
except: pass

"""	BGC-val python is a catch all toolkit for the python methods and shorthands used in this code.
"""

try:	defcmap = pyplot.cm.viridis
except:	
	from bgcvaltools.viridis import viridis
	defcmap = viridis

def folder(name):
	""" This snippet takes a string, makes the folder and the string.
	    It also accepts lists of strings.
	"""
	if type(name) == type(['a','b','c']):
		name=join(name,'/')
	if name[-1] != '/':
		name = name+'/'
	if exists(name) is False:
		makedirs(name)
		print 'makedirs ', name
	return name

def rebaseSymlinks(fn,dryrun=True):
	""" 
	:param fn: A full path to a filename. It should be a symbolic link.
	:param dryrun: A boolean switch to do a trial run of this function.

	This function reduces a chain of symbolic links down to one. It takes a full path, 
	checks whether it is a sym link, then checks whether the real path is the  target of the link.
	If not, it replaces the target with the real path.
	
	"""
	#####
	# fn is a link file
	#if not os.path.exists(fn):
	#	print "rebaseSymlinks:\tfile does not exist.",fn
	#	return
	if not os.path.islink(fn):
		print "rebaseSymlinks:\tfile is not a symlink.",fn
		return
	#####
	# Real path and first target:
	realpath = os.path.realpath(fn)		# The final end of the link chin
	linkpath = os.readlink(fn)		# The first target in the symlink chain
	
	if realpath == linkpath: return
	
	print "rebaseSymlinks:\tdeleting and re-linking ",fn,'-->', realpath
	if dryrun:	return
	os.remove(fn)
	os.symlink(realpath,fn)
	


def mnStr(month):
	""" 
	:param month: An int between 1 and 100.
	
	Returns a 2 digit number string with a leading zero, if needed.
	
	"""
	mn = '%02d' %  month
	return mn
	
#def getCommandJobIDandTime():
#	jobID = argv[1]	
#	timestamp = argv[2]
#	return jobID,timestamp
	
def getFileList(fin):
	if type(fin)==type('abc') and fin.find('*')<0 and fin.find('?')<0: # fin is a string file:
		return [fin,]
	if type(fin)==type('abc') and (fin.find('*')>-1 or fin.find('?')>-1 or fin.find('[')>-1): # fin is a string file:
		return glob(fin)
	if type(fin) == type(['a','b','c',]): # fin is many files:
		filesout = []
		for f in fin:
			filesout.extend(glob(f))
		return filesout

def listFiles(a, want=100, listType = 'even' ,first = 30,last = 30):
	"""
	:param a: A list, usually made of paths to a filename. 
	:param want: An estimate of the number of filesout
	:param listType: Three options available:
			'even': evenly distribute data. 
			'frontloaded': Log scale with most of the data at the front.
			'backloaded': Log scale with most of the data at the end.	
	:param first: All the "first" number of items from the front of the list.
	:param last: All the "last" number of items from the end of the list.	
	"""
	
	l = len(a)
	a = sorted(a)
	want = int(want)

	#####
	# Look at them evenly.
	if len(a) > want:
		if listType=='even': 
			newlist = list(a[::int(l/float(want))])
		if listType=='frontloaded':
			newlist = [a[int(f)] for f in np.logspace(0,np.log10(l-1),want,)]
		if listType=='backloaded':
			
			newlist = [a[l-int(f)] for f in np.logspace(0,np.log10(l),want,)]		
	else:
		newlist = a	

	#####
	# Add the last 30 files
	if last and len(a)>last: 
		newlist.extend(a[-last:])
	else:
		newlist.append(a[-1])		
	#####
	# Add the first 30 files
	if first and len(a)>first: 
		newlist.extend(a[:first])
	else:
		newlist.append(a[0])
		
	#####
	# remove duplicates and sort
	newlist =sorted({n:True for n in newlist}.keys())
	return newlist



	
def getDates(nc, coords):
	"""
	Loads the times from the netcdf.
	"""
	if type(nc) == type('filename'):
		nc = dataset(nc,'r')

	units = nc.variables[coords['t']].units
	#if cal.lower() in ['auto','guess']:
		
	try: 	cal = nc.variables[coords['t']].calendar
	except:	
		cal  = coords['cal']		
		print "getDates was unable to load Calendar, using config calendar:",cal
	
	dtimes = num2date(nc.variables[coords['t']][:], units,calendar=cal)[:]
	return dtimes
	
def DOYarr(dates,debug=False):
	"""
	Converts datetime objects into an array of floats in units of years.
	"""
	try:
		ts = np.array([float(dt.year) + dt.dayofyr/365. for dt in dates])
		if debug: print "DOYarr time array (dt.dayofyr method):",ts
		return ts
	except: pass
	
	ts = []
	for d in dates:
		tdelta = d - datetime(d.year,1,1,0,0,0)
		ts.append(float(d.year) + float(tdelta.days)/365. + float(tdelta.seconds)/(365.*60.*60.))
	if debug: print "DOYarr time array (timedelta method):",ts
	return np.array(ts)
		
def getTimes(nc, coords):
	"""
	Loads the times as a string of floats from the netcdf.
	"""
	dtimes = getDates(nc, coords)	
	ts = DOYarr(dtimes)
	return ts
	
	

def makeThisSafe(arr,debug = True, key='',noSqueeze=False):
	"""
	:param arr: The numpy array.
	:param key: a key, used in debuging.
	:param noSqueeze: A boolean flag for squeezing the array.
	
	This tool takes a numpy array and masks	it where it is a very high value, nan or inf.
	
	"""
	
	if noSqueeze:pass
	else: arr=np.ma.array(arr).squeeze()
	
	ma,mi = arr.max(), arr.min()
	
	if ma > 9.E36:	
		if debug: 	print "makeThisSafe: \tMasked values greater than 9.E36",key
		arr = np.ma.masked_greater(arr, 9.E36)
	
	if np.isinf(ma ) or np.isnan(ma ):
		if debug: print "makeThisSafe: \tMasking infs and Nans",key	
		arr = np.ma.array(arr)
		arr = np.ma.masked_where(np.isnan(arr)+arr.mask +np.isinf(arr) , arr)	
		
	return arr



def intersection(a, b):
    return list(set(a) & set(b))

def maenumerate(marr):
	"""	Masked array enumerate command based on numpy.ndenumerate, which iterates a list of (index, value) for n-dimensional arrays.
		This version ignores masked values.
	"""
	
    	mask = ~marr.mask.ravel()
    	for i, m in izip(np.ndenumerate(marr), mask):
        	if m: yield i
        
def altSpellingDict(dict1):
	"""	Takes a dictionary, and returns the same dict, but with all keys duplicated with alternative spellings.
	"""
	for key in dict1.keys():
		val	 = dict1[key]
		dict1[key.lower()] = val
		dict1[key.upper()] = val
		dict1[key.title()] = val	
		if len(key)>1:
			dict1[key[0].upper()+key[1:]] = val	
	return dict1
	        

class AutoVivification(dict):
    """Implementation of perl's autovivification feature.
    	This class allows you to automate the creating of layered dictionaries.
    	from https://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python
    """
    def __getitem__(self, item):
        try: return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def AutoVivToYaml(av,yamlFile):
	"""
	Saves Nested dictionary or AutoVivification as a yaml readable file.
	
	"""
	space = 4*' '
	s = ''	
	def recursivePrint(d,depth,s):
	    for key in sorted(d.keys()):
	        if depth==0:s+='\n'	# empty line separator.
	        if isinstance(d[key], dict):
	            s += depth * space + str(key) + ': \n'
	            s = recursivePrint(d[key], depth+1, s)
	        else:
	            s += depth * space + str(key) + ': ' + str(d[key]) + '\n'	      
	    return s

	s = recursivePrint(av,0,s)
	
	#print 'AutoVivToYaml:\tFinal string:\n',s
	
	print 'AutoVivToYaml:\tSaving:',yamlFile
	fn = open(yamlFile,'w')
	fn.write(s)
	fn.close()

def YamlToDict(yamlFile):
	"""
	Opens a yaml file and outputs it as a dictionary.
	"""
	print 'YamlToDict:\tLoading:',yamlFile	
	with open(yamlFile, 'r') as f:
		d = yaml.load(f)
	return d


#def machineName():
#	name = str(socket.gethostname())
#	if name.find('npm')>-1:	return 'PML'
#	if name.find('pmpc')>-1: return 'PML'
#	if name.find('esmval')>-1: return 'esmval'
#	if name.find('ceda')>-1: return 'ceda'
#	return False
	
class NestedDict(dict):
    """                                                                       
    Nested dictionary of arbitrary depth with autovivification.               

    Allows data access via extended slice notation.                           
    
    from https://stackoverflow.com/questions/15077973/how-can-i-access-a-deeply-nested-dictionary-using-tuples
    """
    def __getitem__(self, keys):
        # Let's assume *keys* is a list or tuple.                             
        if not isinstance(keys, basestring):
            try:
                node = self
                for key in keys:
                    node = dict.__getitem__(node, key)
                return node
            except TypeError:
            # *keys* is not a list or tuple.                              
                pass
        try:
            return dict.__getitem__(self, keys)
        except KeyError:
            raise KeyError(keys)
    def __setitem__(self, keys, value):
        # Let's assume *keys* is a list or tuple.                             
        if not isinstance(keys, basestring):
            try:
                node = self
                for key in keys[:-1]:
                    try:
                        node = dict.__getitem__(node, key)
                    except KeyError:
                        node[key] = type(self)()
                        node = node[key]
                return dict.__setitem__(node, keys[-1], value)
            except TypeError:
                # *keys* is not a list or tuple.                              
                pass
        dict.__setitem__(self, keys, value)
        
        
def getGridFile(grid):
	"""
	Deprecated. 
	"""
	assert 0
	if grid.upper() in ['ORCA1',]:
		#grid = 'ORCA1'
		gridFile    = "data/mesh_mask_ORCA1_75.nc"		
	if grid in ['Flat1deg',]:	
		gridFile = 'data/Flat1deg.nc' 
				
	if grid.upper() in ['ORCA025',]:	
		#####
		# Please add files to link to 
		for orcafn in [ "/data/euryale7/scratch/ledm/UKESM/MEDUSA-ORCA025/mesh_mask_ORCA025_75.nc",	# PML
				"/group_workspaces/jasmin/esmeval/example_data/bgc/mesh_mask_ORCA025_75.nc",]:	# JASMIN
			if exists(orcafn):	gridFile  = orcafn
		try: 
			if exists(gridFile):pass
		except: 
			print "bgcvalpython:\tgetGridFile:\tERROR:\tIt's not possible to load the ORCA025 grid on this machine."+ \
			      "\n\t\t\tPlease add the ORCA025 file to the orcafn getGridFile() list to BGC-val python.py"
			assert False
        return gridFile
	


def shouldIMakeFile(fin,fout,debug = True):
	""" 
	:param fin: Files in
	:param fout: Files out. 
	
	
	Answers the question should I Make this File?
	returns: True: make the file, or  False: Don't make the file.
	
	It looks at the age of the files in and the file out.
	If the output file doesn't exist. The answer is yes.
	If the output file exists, but is older than the input files: the answer is yes.
		 
	"""
	if not exists(fout): 
		if debug: print 'shouldIMakeFile: out file doesn\'t exit and should be made.'
		return True	

	if type(fin)==type('abc') and fin.find('*')<0: # fin is a string file:
		if not exists(fin): 
			if debug: print 'Warning: ',fin ,'does not exist'
			return False 
	
		if getmtime(fin) > getmtime(fout):
			if debug: print 'shouldIMakeFile: out-file is younger than in-file, you should make it.'
			return True #
		if debug: print 'shouldIMakeFile: out-file is older than in-file, you shouldn\'t make it.'		 
		return False
	if type(fin)==type('abc') and fin.find('*')>0:
		if debug: print 'shouldIMakeFile: in-file contains *, assuming it is a wildcard: ',fin
		fin = glob(fin)
		if debug: print 'shouldIMakeFile: files : ', fin
		
	if type(fin) == type(['a','b','c',]): # fin is many files:
		for f in fin:
			if not exists(f): 
				if debug: print 'Warning: ',f ,'does not exist'
				return False 
			if getmtime(f) > getmtime(fout):
				if debug: print	'shouldIMakeFile: ',f,' is younger than an ',fout,', you should make it'
				return True
		if debug: print 'shouldIMakeFile: no new files in the list. Don\'t make it.'
		return False
	if debug:
		print	'shouldIMakeFile: got to the end somehow:'
		print type(fin), fin, fout
	return False



def getAxesAspectRatio(ax):
	"""
	"""
	axes = ax.get_position()
	width  = axes.x1 - axes.x0
	height = axes.y1 - axes.y0	
	return width/height
	
	
def makemapplot(fig,ax,lons,lats,data,title, zrange=[-100,100],lon0=0.,drawCbar=True,cbarlabel='',doLog=False,drawLand=True,cmap='default'):
	"""
	takes a pyplot figre and axes, lat lon, data, and title and then makes a single map. 
	"""
	lons = np.array(lons)
	lats = np.array(lats)
	data = np.ma.array(data)	
	if doLog and zrange[0]*zrange[1] <=0.:
		print "makemapplot: \tMasking"
		data = np.ma.masked_less_equal(np.ma.array(data), 0.)
	print data.min(),lats.min(),lons.min(), data.shape,lats.shape,lons.shape
	crojp2, data, newLon,newLat = regrid(data,lats,lons)
	if type(cmap) == type('str'):
	    if cmap=='default':
		try:	cmap = pyplot.cm.viridis
		except: cmap = pyplot.cm.jet
	    else:
	    	cmap = pyplot.cm.get_cmap(cmap)
		
	if doLog:
		im = ax.pcolormesh(newLon, newLat,data, cmap=cmap, transform=ccrs.PlateCarree(),norm=LogNorm(vmin=zrange[0],vmax=zrange[1]),)
	else:	
		im = ax.pcolormesh(newLon, newLat,data, cmap=cmap, transform=ccrs.PlateCarree(),vmin=zrange[0],vmax=zrange[1])
	
	if drawLand: ax.add_feature(cfeature.LAND,  facecolor='0.85')	


	if drawCbar:
	    c1 = fig.colorbar(im,pad=0.05,shrink=0.75)
	    if len(cbarlabel)>0: c1.set_label(cbarlabel)
	pyplot.title(title)
	ax.set_axis_off()
	pyplot.axis('off')
	ax.axis('off')
		
	return fig, ax,im

def makePolarmapplot(fig,ax,lons,lats,data,title, zrange=[-100,100],lon0=0.,drawCbar=True,cbarlabel='',doLog=False,drawLand=True,cmap='default'):
	"""
	takes a pyplot figre and axes, lat lon, data, and title and then makes a single polar map. 
	"""
	lons = np.array(lons)
	lats = np.array(lats)
	data = np.ma.array(data)	
	if doLog and zrange[0]*zrange[1] <=0.:
		print "makemapplot: \tMasking"
		data = np.ma.masked_less_equal(np.ma.array(data), 0.)
	print data.min(),lats.min(),lons.min(), data.shape,lats.shape,lons.shape
	
	crojp2, data, newLon,newLat = regrid(data,lats,lons)
	
	if type(cmap) == type('str'):
	    if cmap=='default':
		try:	cmap = pyplot.cm.viridis
		except: cmap = pyplot.cm.jet
	    else:
	    	cmap = pyplot.cm.get_cmap(cmap)
		
	if doLog:
		im = ax.pcolormesh(newLon, newLat,data, cmap=cmap, transform=ccrs.NorthPolarStereo(),norm=LogNorm(vmin=zrange[0],vmax=zrange[1]),)
	else:	
		im = ax.pcolormesh(newLon, newLat,data, cmap=cmap, transform=ccrs.NorthPolarStereo(),vmin=zrange[0],vmax=zrange[1])
	
	if drawLand: ax.add_feature(cfeature.LAND,  facecolor='0.85')	


	if drawCbar:
	    c1 = fig.colorbar(im,pad=0.05,shrink=0.75)
	    if len(cbarlabel)>0: c1.set_label(cbarlabel)
	pyplot.title(title)
	ax.set_axis_off()
	pyplot.axis('off')
	ax.axis('off')
		
	return fig, ax,im



def robinPlotSingle(lons,lats,data,filename,title, zrange=[-100,100],drawCbar=True,cbarlabel='',doLog=False,dpi=100,):
	"""
	takes a pyplot lat lon, data, and title, and filename and then makes a single map, then saves it.
	"""	
	fig = pyplot.figure()
	fig.set_size_inches(10,6)

	lons = np.array(lons)
	lats = np.array(lats)
	data = np.ma.array(data)
	
	rbmi = min([data.min(),])
	rbma = max([data.max(),])
	
	if rbmi * rbma >0. and rbma/rbmi > 100.: doLog=True

	print lons.shape,lats.shape,data.shape
	lon0 = lons.mean()
	ax = pyplot.subplot(111,projection=ccrs.PlateCarree(central_longitude=lon0, ))
		
	fig,ax,im = makemapplot(fig,ax,lons,lats,data,title, zrange=[rbmi,rbma],lon0=lon0,drawCbar=drawCbar,cbarlabel=cbarlabel,doLog=doLog,)

	print "robinPlotSingle.py:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()


	
def robinPlotPair(lons, lats, data1,data2,filename,titles=['',''],lon0=0.,marble=False,drawCbar=True,cbarlabel='',doLog=False,scatter=True,dpi=100,):#**kwargs):
	"""
	takes a pair of lat lon, data, and title, and filename and then makes a pair of maps, then saves the figure.
	"""	
	fig = pyplot.figure()

	fig.set_size_inches(10,10)

	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)
		
	ax1 = fig.add_subplot(211)		
	m1 = Basemap(projection='robin',lon_0=lon0,resolution='c') #lon_0=-106.,
	x1, y1 = m1(lons, lats)
	m1.drawcoastlines(linewidth=0.5)

	rbmi = min([data1.min(),data2.min()])
	rbma = max([data1.max(),data2.max()])	
	if marble: m1.bluemarble()
	else:
		m1.drawmapboundary(fill_color='1.')
		m1.fillcontinents(color=(255/255.,255/255.,255/255.,1))
	m1.drawparallels(np.arange(-90.,120.,30.))
	m1.drawmeridians(np.arange(0.,420.,60.))

	if doLog and rbmi*rbma <=0.:
		print "bgcvalpython:\trobinPlotPair: \tMasking",
		data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
		data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
	if scatter:
		if doLog:	
			if len(cbarlabel)>0: 
				cbarlabel='log$_{10}$('+cbarlabel+')'				
			im1 =m1.scatter(x1,y1,c=np.log10(data1),marker="s",alpha=0.9,linewidth='0', **kwargs) 
		else:	im1 =m1.scatter(x1,y1,c=data1,marker="s",alpha=0.9,linewidth='0',**kwargs)

	else:
		xi1,yi1,di1=mapIrregularGrid(m1,ax1,lons,lats,data1,lon0,xres=360,yres=180)
	
		if doLog: im1 = m1.pcolormesh(xi1,yi1,di1,cmap=defcmap,norm = LogNorm() )
		else:	  im1 = m1.pcolormesh(xi1,yi1,di1,cmap=pyplot.cm.jet)

	
	if drawCbar:
	    c1 = fig.colorbar(im1,pad=0.05,shrink=0.75)

	    if len(cbarlabel)>0: c1.set_label(cbarlabel)

	pyplot.title(titles[0])
	
	
	#lower plot:
	ax2 = fig.add_subplot(212)					
	m2 = Basemap(projection='robin',lon_0=lon0,resolution='c') #lon_0=-106.,
	x2, y2 = m2(lons, lats)
	m2.drawcoastlines(linewidth=0.5)
	if marble: m2.bluemarble()
	else:
		m2.drawmapboundary(fill_color='1.')
		m2.fillcontinents(color=(255/255.,255/255.,255/255.,1))
	
	m2.drawparallels(np.arange(-90.,120.,30.))
	m2.drawmeridians(np.arange(0.,420.,60.))

	if scatter:
		if doLog:	im2 =m2.scatter(x2,y2,c=np.log10(data2),marker="s",alpha=0.9,linewidth='0',**kwargs) #vmin=vmin,vmax=vmax)
		else:		im2 =m2.scatter(x2,y2,c=data2,marker="s",alpha=0.9,linewidth='0',**kwargs) #vmin=vmin,vmax=vmax)		
	else:
		xi2,yi2,di2=mapIrregularGrid(m2,ax2,lons,lats,data2,lon0,xres=360,yres=180)
	
		if doLog: im2 = m2.pcolormesh(xi2,yi2,di2,cmap=defcmap,norm = LogNorm() )
		else:	  im2 = m2.pcolormesh(xi2,yi2,di2,cmap=defcmap) #shading='flat',
	
	if drawCbar:
	    c2 = fig.colorbar(im2,pad=0.05,shrink=0.75)	
	    if len(cbarlabel)>0: c2.set_label(cbarlabel)

	pyplot.title(titles[1])			
		
	print "bgcvalpython:\trobinPlotPair: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()



	


	
		
def arrayify(oldX,oldY,data,fillGaps = True,minimumGap = 3., debug = False):
	"""
	Takes three arrays and converts it into mesh grid style coordinates and a 2D array of the data.
	fillGaps adds x pixels the data has a gap larger than the minimumGap (default is 3) degrees. 
	This means that land mask data, which has been stripped by np.array.compressed(), can be re-added in a crude way.
	"""
	
	#####
	# test for size restrictions.	
	if len(oldX) == len(oldY) == len(data): pass
	else:
		print "arrayify:\tArrays are the wrong size!"
		assert 0
	#####
	# Create 1 D arrays for X and Y
	newXd,newYd,newDatad = {},{},{}		
	for x, y, d in zip(oldX,oldY,data):
		newXd[x] = 1
		newYd[y] = 1		
		newDatad[(x,y)] = d
	newX = np.array(sorted(newXd.keys()))
	newY = np.array(sorted(newYd.keys()))

	#####
	# Extend the newX grid to include land. 
	if fillGaps:
		####
		# Iterate over 	
		for i,(x0,x1) in enumerate(zip(newX[:-1], newX[1:])):
			diff = abs(x1-x0)
			if diff <minimumGap:continue
			
			adding = int(diff) -1
			interval = diff/adding
			
			for a in np.arange(adding):
				####
				# Append the new point to the end. (it'll be sorted later)
				newpoint = x0 + a*interval
				newX = np.append(newX,newpoint)
				
		newX = np.array(sorted(list(newX)))
	
	indexX = {x:i for i,x in enumerate(newX)}
	indexY = {y:i for i,y in enumerate(newY)}
	
	newData = np.ma.zeros((len(newY),len(newX))) - 999.
	
	for (x,y),d in newDatad.items():
		i = indexX[x]
		j = indexY[y]
		newData[j,i] = d

	newData = np.ma.masked_where(newData==-999.,newData)
	return newX,newY,newData


def mameanaxis(a, axis=None):
    """
    	implements a version of np.mean(array, axis=tuple), which is not implemented by default in numpy.
    	Taken from:
    	https://stackoverflow.com/questions/30209624/numpy-mean-used-with-a-tuple-as-axis-argument-not-working-with-a-masked-arr
    	Thanks user2357112!
    """
    if a.mask is np.ma.nomask:
        return super(np.ma.MaskedArray, a).mean(axis=axis)
    counts = np.logical_not(a.mask).sum(axis=axis)
    if counts.shape:
        sums = a.filled(0).sum(axis=axis)
        mask = (counts == 0)
        return np.ma.MaskedArray(data=sums * 1. / counts, mask=mask, copy=False)
    elif counts:
        # Return scalar, not array
        return a.filled(0).sum(axis=axis) * 1. / counts
    else:
        # Masked scalar
        return np.ma.masked
        
        
def determineLimsAndLog(mi,ma):
	"""
	Takes the minimum, the maximum value and retuns wherether it should be a log, and the new axis range.
	"""
	log = True
	
	if 0. in [mi,ma]:
		log=False		
	elif ma/mi < 500.:
		log=False
		
	if log:
		#####
		# log
		diff = np.log10(ma) - np.log10(mi)
		xmin = 10.**(np.log10(mi)-diff/20.) 
		ma = 10.**(np.log10(ma)+diff/20.) 	
	else:	#####
		# not log
		diff = abs(ma - mi)
		mi =mi-diff/20.
		ma = ma+diff/20.	
	return log, mi ,ma		

def determineLimsFromData(data1,data2):
	"""
	Takes the two data sets, and retuns wherether it should be a log, and the new axis range.
	"""
	log = True
	
	data = np.append(data1.compressed(),data2.compressed(),)
	
	mi = np.percentile(data, 5.)
	ma = np.percentile(data,95.)	
	
	if 0. in [mi,ma]:
		log=False		
	elif ma/mi < 500.:
		log=False
	
	if -2.<ma/mi <-0.5:
		m = np.max([np.abs(mi),np.abs(ma)])
		return log, -m,m
	return log, mi ,ma

def symetricAroundZero(data1,data2):
	# rbmi,rbma = symetricAroundZero(data1,data2)
	rbma =3.*np.ma.std(data1 -data2)
	rbmi = -rbma
	return rbmi,rbma					



def makeOneDPlot(dates, data, title, filename, minmax=[0.,0.],dpi=100):
	"""
	Produces a single time series plot.
	"""
	
	print "makeOneDPlot: ", filename
	fig = pyplot.figure()
	ax = fig.add_subplot(111)
	fig.set_size_inches(16, 6)
	
	if len(dates) != len(data):
		print "makeOneDPlot:\tTHere is a size Mismatch between time and data", len(dates) ,len(data)
		assert False
		
	ma,mi = np.ma.max(data), np.ma.min(data)
	if np.isinf(ma ) or np.isnan(ma ) :
		print title,"has an inf/NaN:",ma,mi, np.isinf(ma ) , np.isnan(ma)	
		data = np.ma.array(data)
		data = np.ma.masked_invalid(data)
		ma = np.ma.max(data)
		mi = np.ma.min(data)
		
	if ma is np.ma.masked: 
		print 'makeOneDPlot:\tNo values in the masked array'
		return
	try: print ma+mi
	except: 
		print 'makeOneDPlot:\tmaximum isn\'t a number. exiting.'	
		return
				
	if minmax!= [0.,0.]:
		mi,ma = minmax[0],minmax[1]
		
	pyplot.plot(dates, data)
		
	if ma/100. > mi and ma * mi > 0. and ma > 0.: ax.set_yscale('log')
	
	pyplot.title(title) 
		
	print "makeOneDPlot:\tSaving: " + filename
	pyplot.savefig(filename,dpi=dpi)#, bbox_inches='tight')
	pyplot.close()	
	
		
		
def strRound(val,i=4): return str(round_sig(val,3))


def round_sig(x, sig=2):
	"""
	:param x: a float
	:param sig: number of significant figures
	
	rounds a value to a specific number of significant figures.
	"""
	if np.isnan(x): return "NaN"
	if np.isinf(x): return "Inf"	
	if x == 0. :	return 0.
	if x <  0. :	return -1.* round(abs(x), sig-int(math.floor(math.log10(abs(x))))-1)	
	if x >  0. :	return      round(x, sig-int(math.floor(math.log10(x)))-1)


def getLinRegText(ax, x, y, showtext=True):
        x = [a for a in x if (a is np.ma.masked)==False]
        y = [a for a in y if (a is np.ma.masked)==False]
        beta1, beta0, rValue, pValue, stdErr = linregress(x, y)
        thetext = r'$\^\beta_0$ = '+strRound(beta0)             \
                + '\n'+r'$\^\beta_1$ = '+strRound(beta1)        \
                + '\nR = '+ strRound(rValue)            \
                + '\nP = '+strRound(pValue)             \
                + '\nN = '+str(int(len(x)))
                #+ '\n'+r'$\epsilon$ = ' + strRound(stdErr)     \
        if showtext: pyplot.text(0.04, 0.96,thetext ,
                        horizontalalignment='left',
                        verticalalignment='top',
                        transform = ax.transAxes)
        return beta1, beta0, rValue, pValue, stdErr


def addStraightLineFit(ax, x,y,showtext=True, addOneToOne=False,extent = [0,0,0,0]):
	"""
	Adds a straight line fit to an axis.
	"""
	if 0 in [len(x), len(y)]: return
	
	b1, b0, rValue, pValue, stdErr = getLinRegText(ax, x, y, showtext =showtext)
	if extent == [0,0,0,0]:
		fx = arange(x.min(), x.max(), (x.max()-x.min())/20.)
		fy =[b0 + b1*a for a in fx]
	else:
		minv = min(extent)
		maxv = max(extent)
		fx = np.arange(minv, maxv, (maxv-minv)/1000.)
		fy = np.array([b0 + b1*a for a in fx])
		
		fx = np.ma.masked_where((fx<minv) + (fy < minv) + (fx>maxv) + (fy > maxv), fx)
		fy = np.ma.masked_where((fx<minv) + (fy < minv) + (fx>maxv) + (fy > maxv), fy)
		
	pyplot.plot(fx,fy, 'k')
	#if addOneToOne: pyplot.plot([minv,minv],[maxv,maxv], 'k--')
	#xstep = (x.max()-x.min())/40.
	#ystep = (y.max()-y.min())/40.
	#pyplot.axis([x.min()-xstep, x.max()+xstep, y.min()-ystep, y.max()+ystep])
	

	
		
			
def getOrcaIndexCC(lat,lon, latcc, loncc, debug=True,):	#slowMethod=False,llrange=5.):
	""" 
	Takes a lat and long coordinate, an returns the position of the closest coordinate in the grid.
	"""
	km = 10.E20
	la_ind, lo_ind = -1,-1
	loncc = makeLonSafeArr(loncc)
	lat = makeLatSafe(lat)
	lon = makeLonSafe(lon)	
	
	c = (latcc - lat)**2 + (loncc - lon)**2

	(la_ind,lo_ind) =  np.unravel_index(c.argmin(),c.shape)

	if debug: print 'location ', [la_ind,lo_ind],'(',latcc[la_ind,lo_ind],loncc[la_ind,lo_ind],') is closest to:',[lat,lon]	
	return la_ind,lo_ind


def getORCAdepth(z,depth_arr,debug=True):
	""" 
	:param z: Depth
	:param depth_arr: depth array.
	
	Calculate the closest depth to z in the array, and returns the index.
	"""
	d = 1000.
	best = -1
	depth_arr = np.array(depth_arr)	
	print "getORCAdepth:",z, depth_arr
	if len(depth_arr) ==1:return 0

	for i,zz in enumerate(depth_arr.squeeze()):
		d2 = abs(abs(z)-abs(zz))
		if d2<d:
		   d=d2
		   best = i
		   if debug: print 'bgcvalython.getORCAdepth:',i,z,zz,depth_arr.shape, 'best:',best
	if debug: print 'bgcvalython.getORCAdepth:\tdepth: in situ:', z,'index:', best, 'distance:',d,', closest model:',depth_arr.shape, depth_arr[best]
	return best

def getclosestlon(x,lons,debug=True):
	"""	
	Locate the closets longitude coordinate for transects. 
	Only works for 1D longitude arrays
	Returns an index
	"""
	d = 1000.
	best = -1
	lons = np.array(lons)
	if lons.ndim >1: 
		print "getclosestlon:\tFATAL:\tThis code only works for 1D longitude arrays"
		assert False
	x = makeLonSafe(x)
	lons = makeLonSafeArr(lons)
	
	for i,xx in enumerate(lons.squeeze()):
		d2 = abs(x-xx)
		if d2<d:
		   d=d2
		   best = i
		   print 'getORCAdepth:',i,x,xx,lons.shape, 'best:',best
	if debug: print 'lons: in situ:', x,'index:', best, 'distance:',d,', closest model:',lons.shape, lons[best]
	return best
	
def getclosestlat(x,lats,debug=True):
	"""	
	Locate the closets latitute coordinate for transects. Only works for 1D latitute arrays.
	Returns an index
	"""
	d = 1000.
	best = -1
	if lats.ndim >1: 
		print "getclosestlon:\tFATAL:\tThis code only works for 1D latitute arrays"
		assert False
	
	for i,xx in enumerate(lats.squeeze()):
		d2 = abs(x-xx)
		if d2<d:
		   d=d2
		   best = i
		   print 'getORCAdepth:',i,x,xx,lats.shape, 'best:',best
	if debug: print 'lats: in situ:', x,'index:', best, 'distance:',d,', closest model:',lats.shape, lats[best]
	return best
	
	
def getclosesttime(t,times,debug=True):
	"""	
	Locate the closest time point compared to an array. 
	Returns an index
	"""
	d = 1e20
	best = -1
	if times.ndim >1: 
		print "getclosesttime:\tFATAL:\tThis code only works for 1D latitute arrays"
		assert False
	
	for i,xx in enumerate(times.squeeze()):
		d2 = abs(t-xx)
		if d2<d:
		   d=d2
		   best = i
		  # print 'getclosesttime:',i,t,xx,times.shape, 'best:',best
	if debug: print 'getclosesttime: target', t,'index:', best, 'distance:',d,', closest model:', times[best]
	return best	
	
def makeLonSafe(lon):
	"""
	Makes sure that the value is between -180 and 180.
	"""
	while True:
		if -180.<lon<=180.:	return lon
		if lon<=-180.:		lon+=360.
		if lon> 180.:		lon-=360.		
	
def makeLatSafe(lat):
	"""
	Makes sure that the value is between -90 and 90.
	"""
	
	#while True:
	if -90.<=lat<=90.:return lat
	#print 'You can\'t have a latitude > 90 or <-90',lat
	if lat is np.ma.masked: return lat
	print "makeLatSafe:\tERROR:\tYou can\'t have a latitude > 90 or <-90", lat
	assert False
	#return np.ma.clip(lat,-90.,90.)
	#assert False		
	#return False
	#if lon<=-90:lat+=360.
	#if lon> 90:lat-=360.		
	   
def makeLonSafeArr(lon):
	"""
	Makes sure that the entire array is between -180 and 180.
	"""
	
	if lon.ndim == 3:
	 for (l,ll,lll,) , lo in np.ndenumerate(lon):
		lon[l,ll,lll] = makeLonSafe(lo)
	 return lon	 	  
	if lon.ndim == 2:
	 for l,lon1 in enumerate(lon):
	  for ll,lon2 in enumerate(lon1):
	   lon[l,ll] = makeLonSafe(lon2)
	 return lon
	if lon.ndim == 1:
	 for l,lon1 in enumerate(lon):
	   lon[l] = makeLonSafe(lon1)
	 return lon	 	 
	assert False

def sensibleLonBox(lons):
	""" Takes a small list of longitude coordinates, and makes sure that they're all together.
	Ie. a box of (179, 181,) would become 179,-179 when makeLonSafe, so we're undoing that.
	"""
	lons = np.array(lons)
	# all positiv or all negative: fine
	
	if lons.min() * lons.max() >= 0.:
		return lons
	
	boundary =10.
	if lons.min()<-180.+boundary and lons.max() > 180. -boundary:
		# move all below zero values to around 180.

		for l,lo in enumerate(lons):
			if lo <0.:
				#print "move all below zero values to around 180.", l, lo
				lons[l] = lo+360.
	#####
	# Note that this will need tweaking if we start looking at pacific transects.	

	return lons	
	

def Area(p1,p2):#lat,lon
	"""
	Calculates the area in m^2 between two coordinates points.
	points are [lat,lon]
	"""
	
	R=6378000. #m
	lat1,lon1=p1[0],p1[1]
	lat2,lon2=p2[0],p2[1]
	A = (np.pi/180.)*R*R* abs(np.sin(lat1*np.pi/180.)-np.sin(lat2*np.pi/180.))*abs(lon1-lon2)
	print 'Area:',lat1,'N->',lat2,'N\t',lon1,'E->',lon2,'E,\tA=',A

	return A
			
			

def regrid(data,lon,lat):
	"""
	Uses cartopy to transform the data into a new grid.
	"""
	
    	nX = np.arange(-179.5,180.5,1.)
    	nY = np.arange( -89.5, 90.5,1.)
    	
    	if lat.ndim ==2:
    		   oldLon, oldLat = lon,lat		
    	else:
    		if data.ndim >1:
 	   		oldLon, oldLat = np.meshgrid(lon,lat)
 	   	else:
 	   		oldLon, oldLat,data = lon,lat,data

    	newLon, newLat = np.meshgrid(nX,nY)
    	
    	crojp1 = ccrs.PlateCarree(central_longitude=180.0, )#central_latitude=300.0)
    	crojp2 = ccrs.PlateCarree(central_longitude=180.0, )#central_latitude=300.0)

    	a = img_transform.regrid(data,
    			     source_x_coords=oldLon,
                             source_y_coords=oldLat,
                             source_cs=crojp1,
                             target_proj=crojp2,
                             target_x_points=newLon,
                             target_y_points=newLat
                             )
       # print 'newregid shape:',a.shape                     
	return crojp2, a, newLon,newLat
	
	

def weighted_percentiles(values, percentiles, weights=None, values_sorted=False, old_style=False):
    """ Very close to np.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: np.array with data
    :param percentiles: array-like with many percentiles needed
    :param weights: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of initial array
    :param old_style: if True, will correct output to be consistent with np.percentile.
    :return: np.array with computed quantiles.
    from https://stackoverflow.com/questions/21844024/weighted-percentile-using-numpy
    """
    values = np.array(values)
    quantiles = np.array(percentiles)/100.
    
    if weights is None:
        weights = np.ones(len(values))
    weights = np.array(weights)
    assert np.all(quantiles >= 0) and np.all(quantiles <= 1), 'percentiles should be in [0, 100]'

    if not values_sorted:
        sorter = np.argsort(values)
        values = values[sorter]
        weights = weights[sorter]

    weighted_quantiles = np.cumsum(weights) - 0.5 * weights
    if old_style:
        # To be convenient with np.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= np.sum(weights)
    return np.interp(quantiles, weighted_quantiles, values)
    
    
    
    
    
			

class shelveMetadata:
   """
   A tool to load the metadata of a shelve.
   """
   def __init__(self,model='',name='',year='',layer='',newSlice='',xkey='',ykey='',shelve = ''):
   	self.model 	= model
   	self.name 	= name
   	self.year 	= year   	
   	self.layer	= layer
   	self.newSlice 	= newSlice
   	self.xkey 	= xkey   	   	   	
   	self.ykey 	= ykey   	   	   	   	
   	self.shelve 	= shelve   	      	
   def __repr__(self):
	string = ''   
   	for a in [ self.model,self.name,self.year,self.layer,self.newSlice,self.xkey,self.ykey]:
   		string+=', '+a
   	string+='\nshelve:'+self.shelve
        return string
   def __str__(self):
	string = ''   
   	for a in [ self.model,self.name,self.year,self.layer,self.newSlice,self.xkey,self.ykey]:
   		if len(a) ==0:continue
   		string+='-'+a
        return string   
       
        
        
def reducesShelves(AllShelves,models=[],names=[],years=[],layers=[],sliceslist=[],):
	"""
	This routine takes the AllShelves dictionary of shelveMetadata then returns a list of shelves.
	This is useful for producing a target diagram, or a patterns plot.
	requirements is a list of models, slices, layers that are required.
	"""
	emptySMDtype = type(shelveMetadata())
	outArray = []
	for shelveMD in AllShelves:
		if type(shelveMD) != emptySMDtype:
			print "somewhere, this is not a shelveMD:",shelveMD
			assert False
		
		if len(models) 		and shelveMD.model 	not in models:	continue
		if len(names) 		and shelveMD.name 	not in names:	continue
		if len(years) 		and shelveMD.year 	not in years:	continue
		if len(layers) 	and shelveMD.layer not in layers:continue
		if len(sliceslist) 	and shelveMD.newSlice 	not in sliceslist:continue
		outArray.append(shelveMD.shelve)
	return outArray		
	
class listShelvesContents:
   def __init__(self,AllShelves):
	"""
	This routine takes the AllShelves dictionary of shelveMetadata then produces lists of all components.
	"""
	models={}
	names={}
	years={}
	layers={}
	sliceslist = {}
	emptySMDtype = type(shelveMetadata())
	for shelveMD in AllShelves:
		if type(shelveMD) != emptySMDtype:
			print "somewhere, this is not a shelveMD:",shelveMD
			assert False
		
		models[shelveMD.model] 		= True
		names[shelveMD.name] 		= True
		years[shelveMD.year] 		= True
		layers[shelveMD.layer]= True				
		sliceslist[shelveMD.newSlice] 	= True						

	self.models = models.keys()
	self.names = names.keys()
	self.years = years.keys()
	self.layers = layers.keys()
	self.sliceslist = sliceslist.keys()
   def __repr__(self):
	string = ''   
   	for a in [ self.models,self.names,self.years,self.layers,self.sliceslist]:
   		string+=', '+' '.join(a)
   	string+='\nshelve contents:'+self.shelve
        return string
   def __str__(self):
	string = ''   
   	for a in [ self.models,self.names,self.years,self.layers,self.sliceslist]:
   		if len(a) ==0:continue
   		string+='-'+' '.join(a)
        return string   
	

		      	
		
	      		
####
# The following functions for maniulating and loading data are now in stdfunctions.py
def NoChange(nc,keys):	
	""" 
	Loads keys[0] from the netcdf, but applies no change.
	"""
	return nc.variables[keys[0]][:]
def N2Biomass(nc,keys):	
	""" 
	Loads keys[0] from the netcdf, but multiplies by 79.572 (to convert Nitrogen into biomass).
	"""
	return nc.variables[keys[0]][:]* 79.573

def KtoC(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, and converts from Kelvin to Celcius.
	"""
	return nc.variables[keys[0]][:] - 273.15


def mul1000(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but multiplies by 1000.
	"""
	return nc.variables[keys[0]][:]* 1000.

def mul1000000(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but multiplies by 1000000.
	"""
	return nc.variables[keys[0]][:]* 1000000.
		
def div1000(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, then divides by 1000.
	"""
	return nc.variables[keys[0]][:]/ 1000.	
def div1e6(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but divides by 1.e6.
	"""
	return nc.variables[keys[0]][:]/ 1.e6	

def applymask(nc,keys):		
	""" 
	Loads keys[0] from the netcdf, but applies a mask.
	"""
	return np.ma.masked_where(nc.variables[keys[1]][:]==0.,nc.variables[keys[0]][:])

def sums(nc,keys):	
	""" 
	Loads Key[0] from the netcdf, then sums the other keys.
	"""
		
	a = nc.variables[keys[0]][:]
	for k in keys[1:]:a += nc.variables[k][:]
	return a 
	
def oxconvert(nc,keys): 	
	""" 
	Loads keys[0] from the netcdf, but multiplies by 44.771 (to convert oxygen units ).
	"""
	return nc.variables[keys[0]][:] *44.661
	
def convertkgToM3(nc,keys): 	
	""" 
	Loads keys[0] from the netcdf, but multiplies by 1.027 (to convert from density kg to volume).
	"""
	return nc.variables[keys[0]][:]* 1.027

# 1 ml/l = 103/22.391 = 44.661 umol/l
# http://ocean.ices.dk/Tools/UnitConversion.aspx
	
tdicts = {	'ZeroToZero': {i  :i     for i in xrange(12)},		
		'OneToOne':   {i+1:i+1   for i in xrange(12)},
		'OneToZero':  {i+1:i     for i in xrange(12)},
		'ZeroToOne':  {i  :i+1   for i in xrange(12)},			
	}		      		

def extractData_old(nc, details,key = ['',],debug=False):
  	""" 	
  	This loads the data based on the instructions from details dictionairy.
  	If you want to do something funking to the data before plotting it, just create a new convert function in getMT().
  	details dict usually contains: {'name': 'Chlorophylla', 'vars':['Chlorophylla',], 'convert': bvp.div1000,'units':'ug/L'}
  	"""
  	
	if isinstance(details,dict): 
  		keys = details.keys()
  		if debug: print "extractData: details is a dict", details.keys()
  		
  	elif len(key) and key in nc.variables.keys():
  		if debug: print "extractData: details Not a dict:", details,'but, the key is valid:',key
  		return np.ma.array(nc.variables[key][:])  	
 		
	if 'convert' in keys and 'vars' in keys:	
		xd = np.ma.array(details['convert'](nc,details['vars']))
		return xd
  	
  	print "extractData:\t you may have a problem in your details dictionairy:", details, key
  	assert False
  	
  	
  	
  	
		      		
		      		

