#!/usr/bin/ipython 

#
# Copyright 2017, Plymouth Marine Laboratory
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
.. module:: meshgridmaker
   :platform: Unix
   :synopsis: This is a tool to make a mesh grid file. 
   		This tool takes an input netcdf file, and calculates the area, volume, 
   		and cross sectionional area of several transects.   

.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

import numpy as np
import os

from math import pi, cos, radians,sin, asin, sqrt
from matplotlib import pyplot
from matplotlib.colors import LogNorm

from bgcvaltools.dataset import dataset

from shapely.geometry import shape,LineString, Polygon
from shapely.geometry.polygon import orient as geoorient
from pyproj import Proj,transform as projTransform

import bgcvalpython as bvp	
from changeNC import changeNC, AutoVivification


# Significant lines.
# (lat,lon), (lat,lon) , (N, E)
AMOCCoords =  [(26.001, -80.8), (26.001, -10.)]	
DrakeCoords = [(-75.01, -68.501), (-54.01, -68.501)]
WestAusCoords = [(-75.01, 118.501), (-26.01, 118.501)]
SouthAfrCoords = [(-75.01, 21.501), (-26.01, 21.501)]
NorthPacCoords = [(19.001, -155.001), (62.001, -155.001)]
NorthEastPacCoords = [(19.001, -155.001), (19.001, -102.001)]
WestIndianCoords   = [(-30.501, 26.001), (-30.501, 77.001)]
NorthIndianCoords  = [(-30.501, 77.001), ( 25.501, 77.001)]
EastIndianCoords   = [(-30.501, 77.001), (-30.501, 121.001)]
SEAcoords	   = [(-24.501, 117.001), ( 28.501, 117.001)]

CrossSections = {
		'AMOC':		AMOCCoords,
		'Drake':	DrakeCoords,
		'WestAus':	WestAusCoords,
		'SouthAfr':	SouthAfrCoords,
		'NorthPac':	NorthPacCoords,
		'NorthEastPac':	NorthEastPacCoords,				
		'WestIndian':	WestIndianCoords,				
		'NorthIndian':	NorthIndianCoords,						
		'EastIndian':	EastIndianCoords,						
		'SouthEastAsia':SEAcoords,								
		}
		
CrossSectionsLongnames = {
		'AMOC':		'Atlantic Transect at 26N - cross sectional area',
		'Drake':	'Drake passage cross sectional area',
		'WestAus':	'Southern Ocean Transect at 118E - cross sectional area',
		'SouthAfr':	'Southern Ocean Transect at 21E - cross sectional area',
		'NorthPac':	'North Pacific Ocean Transect at 155W - cross sectional area',
		'NorthEastPac':	'North Pacific Ocean Transect at 19N - cross sectional area',
		'WestIndian':	'West Indian Ocean Transect at 30W - cross sectional area',			
		'NorthIndian':	'North Indian Ocean Transect at 77E - cross sectional area',						
		'EastIndian':	'East Indian Ocean Transect at 30W - cross sectional area',
		'SouthEastAsia':'South East Asian transect at 117E - cross sectional area',
		}

		
				

	
def haversine(p1,p2):	#lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1 = p1[0]
    lon1 = p1[1]
    lat2 = p2[0]
    lon2 = p2[1]
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2.)**2. + cos(lat1) * cos(lat2) * sin(dlon/2.)**2.	# Wikipeida order
    #  a = sin(dlon/2.)**2. + cos(lon1) * cos(lon2) * sin(dlat/2.)**2.    
    c = 2. * asin(sqrt(a)) 
    meters = 6378137. * abs(c)
    return meters
    


def GetArea(points,projection='leae',printAll=False):
	poly = {"type": "Polygon", "coordinates": [   points, ]}
	     
	lon, lat = zip(*poly['coordinates'][0])	
		
	if printAll:
		EPSG4326  = Proj(init="EPSG:4326")  # LatLon with WGS84 datum used by GPS units and Google Earth
		epsg3410  = Proj(init="EPSG:3410")  # Cylindrical Equal-Area
		epsg3408  = Proj(init="EPSG:3408")  # Lambert Azimuthal Equal-Area
		EPSG3995  = Proj(init="EPSG:3995")  #"Arctic Polar Stereographic",

		epsglongnames = {
			'EPSG4326':	"LatLon with WGS84 datum used by GPS units and Google Earth",
			'epsg3410':	"Cylindrical Equal-Area projection",
			'epsg3408': 	"Lambert Azimuthal Equal-Area",
			'EPSG3995':	"Arctic Polar Stereographic",
			}
		projs = {
			'EPSG4326':	EPSG4326,	#  LatLon with WGS84 datum used by GPS units and Google Earth
			'epsg3410':	epsg3410,	# Cylindrical Equal-Area projection
			'epsg3408': 	epsg3408,	# Lambert Azimuthal Equal-Area
			'EPSG3995':	EPSG3995,	# "Arctic Polar Stereographic",
			}
				
		for name, pa in projs.items():
			x, y = pa(lon, lat)
			cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
			#lat,lon
			projArea = shape(cop).area
			print name,epsglongnames[name], '\tarea:',projArea
	###
	# projection
	if projection=='leae':
		epsg3408  = Proj(init="EPSG:3408")
		x, y = epsg3408(lon, lat)
		cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
		lat,lon
		return shape(cop).area
		
def makeBnds(arr):
	"""
	make a 2D array of boundaries from a 1D field
	"""
	arr = np.array(arr)
	if arr.ndim !=1: assert 0
	mids = (arr[1:] + arr[:-1])/2.
	distances = (arr[1:] - arr[:-1])
	meandistance = distances.mean()
	#print 'makeBnds:',arr[0], meandistance,mids[0], arr.shape
	bnds = [[arr[0] -meandistance/2., mids[0]],]
	#print bnds
	for i,a in enumerate(arr[:-1]):# skip last noe, add afterwards
		if i ==0:continue
		#print i,a,[mids[i-1],mids[i]]
		bnds.append([mids[i-1],mids[i]])
	bnds.append([mids[-1],arr[-1]+meandistance/2.])
	return np.array(bnds)
		

def makeArea(nc,coordsdict):
	lats = nc.variables[coordsdict['lat']][:]	
	lons = bvp.makeLonSafeArr(nc.variables[coordsdict['lon']][:])
	
	key_latbnd = ''
	key_lonbnd = ''
	if 'lat_bnds' in nc.variables.keys():
		key_latbnd = 'lat_bnds'
		key_lonbnd = 'lon_bnds'		

	elif 'lat_vertices' in nc.variables.keys():
		key_latbnd = 'lat_vertices'
		key_lonbnd = 'lon_vertices'
	
	if key_latbnd and key_lonbnd:
		print "makeArea:\t",key_latbnd,key_lonbnd
		lat_bnds = nc.variables[key_latbnd][:]
		lon_bnds = bvp.makeLonSafeArr(nc.variables[key_lonbnd][:])
	else:
		print "makeArea:\tBoundaries fields not found. "
		#### key_lonbnd and key_latbnd not found.#
		lat_bnds = makeBnds(lats)
		lon_bnds = bvp.makeLonSafeArr(makeBnds(lons))

		
	
	if lats.ndim ==1 and lat_bnds.ndim==2:
		area = np.zeros((len(lats),len(lons)))
		for (i,j), a in np.ndenumerate(area):
			points = [
				  (lon_bnds[j,0],lat_bnds[i,0]),
				  (lon_bnds[j,0],lat_bnds[i,1]),
				  (lon_bnds[j,1],lat_bnds[i,1]),
				  (lon_bnds[j,1],lat_bnds[i,0]),
				  (lon_bnds[j,0],lat_bnds[i,0]),
				  ]
			#area[i,j] = area_of_polygon(points)
			area[i,j] = GetArea(points)			
			#print i, j, area[i,j]	
		return area		
			
	if lats.ndim ==2 and lat_bnds.ndim==3:
		area = np.zeros(lats.shape)
		print area		
		for (i,j), a in np.ndenumerate(area):
			latcorners = lat_bnds[i,j,:]
			loncorners = lon_bnds[i,j,:]
			points = [(lo,la) for la,lo in zip(latcorners,loncorners)]
			points.append((loncorners[0],latcorners[0]))	# to close the shape
			#points = [(la,lo) for la,lo in zip(latcorners,loncorners)]
			#points.append((latcorners[0],loncorners[0]))	# to close the shape			
			#area[i,j] = area_of_polygon(points)
			area[i,j] = GetArea(points)			
			#print i, j, area[i,j]				
		return area		

	print "timeseriesTools.py:\tNot implemeted makeArea for this grid. ",lats.ndim, coordsdict, lat_bnds
	assert 0 , 'timeseriesTools.py:\tNot implemeted makeArea for this grid. '+str(lats.ndim)

def makeVolume(nc,coordsdict,area):
	if 'depth_bnds' in nc.variables.keys():
		depth_bnds = nc.variables['depth_bnds'][:]			
	elif 'lev_bnds' in nc.variables.keys():
		depth_bnds = nc.variables['lev_bnds'][:]
	else:
		depth_bnds = makeBnds(nc.variables[coordsdict['z']])
				
				
	if depth_bnds.ndim == 2:
		pvol = np.zeros((depth_bnds.shape[0],area.shape[0],area.shape[1])) 
		thickness = np.abs(depth_bnds[:,1]-depth_bnds[:,0])

		print "makeVolume:",pvol.shape, pvol.min(),pvol.max()
						
		for (z,i,j), p in np.ndenumerate(pvol):
			pvol[z,i,j] = area[i,j] * thickness[z]

		print "makeVolume:",pvol.shape, pvol.min(),pvol.max()
		return pvol
	assert "Depth boundaries not know"


	
	
def drawLine(	fn,
		model,
		points 		= [(-75., -68.5), (-54., -68.5)],
		linename 	= 'DrakePassage',
		returnMask	= False):
	try:coordsdict = CoordDict[model]
	except: return
	#fn = getGridFile(model)
	
	if len(points) !=2:assert "Only want two points:"+str(points)
	
	#####
	# Load nc
	nc = dataset(fn,'r',Quiet=True)
	lats = nc.variables[coordsdict['lat']][:]	
	lons = bvp.makeLonSafeArr(nc.variables[coordsdict['lon']][:])
	#if 'o2' not in nc.variables.keys(): assert 0
	ox = nc('o2')[0,0]
	# Make a map
	tmask = makeMask(nc,'o2')[:]
	data = np.zeros_like(ox)	
	#data  = makeMask(nc,'o2')[0]
	nc.close()
	

	openValue = 4.

	points = np.array(points)
	pointnum = 500.
	latline = np.linspace(points[0,0],points[1,0],num=pointnum)
	lonline = np.linspace(points[0,1],points[1,1],num=pointnum)

	#for (j,k), d in np.ndenumerate(data):
	#	data[j,k] = float(tmask[0,j,k]	)

	for lat,lon in zip(latline,lonline):
		
		if lats.ndim==2:	
			la,lo =  bvp.getOrcaIndexCC(lat,lon, lats, lons,debug=False)
		else:
			lo = bvp.getclosestlon(lon, lons,debug=False)
			la = bvp.getclosestlat(lat, lats,debug=False)			
		if la==-1 or la==-1:	continue
		data[la,lo] = openValue
		
	filename = bvp.folder('images/drawLine/'+linename)+model+'-drawLine.png'
	title = model	
	meshPlot(data, title ,filename)
	
	#####
	# making a mask for the netcdf;
	newmask = np.ones_like(tmask)
	
	for (j,k), d in np.ndenumerate(data):
		if d == openValue: 
			newmask[:,j,k] = tmask[:,j,k]
		
#	for (i,j,k), a in np.ndenumerate(newmask):
#		if a in [1,1.]: continue
#		if data[j,k] == openValue:
#			print 'line!',i,j,k,a
#			newmask[i,j,k] = 0.	# line 
#		else:	newmask[i,j,k] = 1.	# mask everything else
	newmask = np.clip(newmask,0.,1.)
	filename = bvp.folder('images/drawLine/'+linename)+model+'-mask.png'
	meshPlot(newmask.sum(0), title ,filename)
		
	if returnMask: return newmask

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
	
	
	
	
def lengthOfLineInPolygon(linepoints,corners,orient=True,debug=True):
	"""
	This tool calculates the length in m of a straight line inside a Polygon.
	"""
	
	# Create a polygon from the corners
	# orient makes sure that the corners of the pixel are in anti-clockwise, but is very slow
	
	if orient:
		pixel = geoorient(Polygon(corners))	
	else:	pixel = Polygon(corners)
	
	#####
	# Create a line along the points given
	line1 = LineString(bvp.makeLonSafeArr(np.array(linepoints)))

	try:	line2 = pixel.intersection(line1)
	except: 
		if not pixel.is_valid:
			pixel = pixel.buffer(0)	
		line2 = pixel.intersection(line1)				
	#####
	# ignore points that don't meet the line
	if line2.is_empty:  
		if debug: print "Didn't meet:", line1,pixel
		return 0.	
	

	if len(line2.coords[:]) != 2 :	
		print "The line has the wrong number of points!:", line2.coords[:]
		assert 0
	intersect1 = (line2.xy[0][0],line2.xy[1][0])	#	 note that line.xy[0] is list of x- coordinates!
	intersect2 = (line2.xy[0][1],line2.xy[1][1])	
	dist = haversine(intersect1, intersect2)
		
	if debug:	
		print "lengthOfLineInPolygon:\tintersection of points: ",intersect1, intersect2
		print "lengthOfLineInPolygon:\tDistance:", dist	
	return dist
	

def crossectionalAreaAlongLine(
		fn,
		model,
		coordsdict,
		field = 'o2',
		points 		= [(-75., -68.5), (-54., -68.5)],	#lat, lon
		linename 	= 'DrakePassage',
		):
		
	print "crossectionalAreaAlongLine:",model

	#####
	# Load nc
	print "crossectionalAreaAlongLine: opening:", fn
	nc = dataset(fn,'r',Quiet=True)

	tmask = makeMask(nc,field)[:]
	ox = nc(field)[0,:]	# 3d
	surface = np.zeros_like(ox[0])	
	crossection = np.zeros(np.ma.array(ox).shape)	
			
	#####
	# load lat,lon, z, boundaries
	lats = nc.variables[coordsdict['lat']][:]	
	lons = bvp.makeLonSafeArr(nc.variables[coordsdict['lon']][:])	
	key_latbnd = ''
	key_lonbnd = ''	
	if 'lat_bnds' in nc.variables.keys():
		key_latbnd = 'lat_bnds'
		key_lonbnd = 'lon_bnds'		
	if 'lat_vertices' in nc.variables.keys():
		key_latbnd = 'lat_vertices'
		key_lonbnd = 'lon_vertices'
		
	if key_latbnd and key_lonbnd:
		lat_bnds = nc.variables[key_latbnd][:]
		lon_bnds = bvp.makeLonSafeArr(nc.variables[key_lonbnd][:])
	#else:
	#	#### key_lonbnd and key_latbnd not found.
	#	lat_bnds = makeBnds(lats)
	#	lon_bnds = bvp.makeLonSafeArr(makeBnds(lons))
				

	print lon_bnds.max()
	if lon_bnds.max() > 180.:assert 0

	if 'depth_bnds' in nc.variables.keys():
		lev_bnds = nc.variables['depth_bnds'][:]			
	elif 'lev_bnds' in nc.variables.keys():
		lev_bnds = nc.variables['lev_bnds'][:]
	else:
		lev_bnds = makeBnds(nc.variables[coordsdict['z']])

	
	if lev_bnds.ndim == 2:
		thickness = np.ma.abs(lev_bnds[:,0] - lev_bnds[:,1])
	else:
		print "What?"
		assert 0
	nc.close()

	if tmask.ndim==4:	
		assert 0
		surfmask = tmask[0,0]
		
	if tmask.ndim==3:	surfmask = tmask[0]
	if tmask.ndim==2:	surfmask = tmask	

	#pyplot.pcolormesh(surfmask)
	#pyplot.colorbar()
	#pyplot.show()
	#assert 0
	
	intersection = False
	
	for (i,j), d in np.ndenumerate(surface):
		#if d == 1.: continue	# ignore land points
		if surfmask[i,j] in [1.,1]:continue
		if lat_bnds.ndim == 2:
			lon_bnds[j] = sensibleLonBox(lon_bnds[j])
			corners = [
				  (lat_bnds[i,0],lon_bnds[j,0],),
				  (lat_bnds[i,1],lon_bnds[j,0],),
				  (lat_bnds[i,1],lon_bnds[j,1],),
				  (lat_bnds[i,0],lon_bnds[j,1],),
				  (lat_bnds[i,0],lon_bnds[j,0],),
				  ]		
		elif lat_bnds.ndim == 3:
			lon_bnds[i,j] = sensibleLonBox(lon_bnds[i,j])		
			corners = [[la,lo] for la, lo in zip(lat_bnds[i,j,:],lon_bnds[i,j,:])]
			corners.append([lat_bnds[i,j,0],lon_bnds[i,j,0]])
		else:
			print "What?"			
			assert 0
		
		dist = lengthOfLineInPolygon(points,corners,debug=False)
		
		if dist < 0.:
			print "Distance is below 0!", dist, (i,j)
			assert 0 
		
		xsec = thickness * dist
		if xsec.min()<0.:
			print 'ERROR: crossection below 0!', i,j, dist
			for z,cs in enumerate(crossection[:,i,j]): print [z,i,j],' : ',cs , d
			assert 0 
		crossection[:,i,j] =  xsec
		

			
		if not dist:continue
		intersection = True
	
	crossection = np.ma.masked_where(tmask==1., crossection)
		
	#next stage is to calculate the distance using pyproj, then multiply that by the thickness of the pixel.
	filename = bvp.folder('images/drawLine/'+linename)+model+'-'+linename+'-crossection.png'
	title = model + ' - cross sectional area'
	try:	meshPlot(crossection.sum(0), title ,filename)			
	except: pass
	
	#####
	# Hiow can you have a negative cross section?
	if crossection.min()<0.:
		filename = bvp.folder('images/drawLine/'+linename)+model+'-'+linename+'-crossection-NEGATIVE.png'	
		meshPlot(crossection.min(0), title ,filename)	
		assert 0					
	#####
	# Basically, this part prints a bunch of stuff then asserts.
	if not intersection:
		print "Didn't find any points!",model, title, crossection.sum()
		
		points = np.array(points)
		latline = np.linspace(points[0,0],points[1,0],num=1000)
		lonline = np.linspace(points[0,1],points[1,1],num=1000)

		founds = {}
		lonline = bvp.makeLonSafeArr(lonline)		
		for lat,lon in zip(latline,lonline):
		
			if lats.ndim==2:	
				la,lo =  bvp.getOrcaIndexCC(lat,lon, lats, lons,debug=False)
			else:
				lo = bvp.getclosestlon(lon, lons,debug=False)
				la = bvp.getclosestlat(lat, lats,debug=False)	
						
			if la==-1 or la==-1:	continue
			try:	
				fns = founds[(i,j)]
				continue
			except: pass
					
			if lat_bnds.ndim == 2:
				corners = [
					  (lat_bnds[i,0],lon_bnds[j,0],),
					  (lat_bnds[i,1],lon_bnds[j,0],),
					  (lat_bnds[i,1],lon_bnds[j,1],),
					  (lat_bnds[i,0],lon_bnds[j,1],),
					  (lat_bnds[i,0],lon_bnds[j,0],),
					  ]		
					  
			if lat_bnds.ndim == 3:
				corners = [[la,lo] for la, lo in zip(lat_bnds[i,j,:],lon_bnds[i,j,:])]
				corners.append([lat_bnds[i,j,0],lon_bnds[i,j,0]])
			founds[(i,j)] = True
			print lat,lon, i,j, corners
		assert 0
	else:
		return 	crossection
	




def makeMask(nc,field):
	if type(nc) == type('str'):
		nc = dataset(nc,'r',Quiet=True)
	try:	
		tmask = nc.variables[field][0].mask
		return tmask		
	except: pass

	if nc.variables[field].ndim==4:
		tmask = np.ma.masked_where(nc.variables[field][0,:] == nc.variables[field][0,0,0,0],nc.variables[field][0,:]).mask
	if nc.variables[field].ndim==3:
		tmask = np.ma.masked_where(nc.variables[field][0,:] == nc.variables[field][0,0,0],nc.variables[field][0,:]).mask
	return tmask	

				
				
				
#####
# Plotting tools:
def meshPlot(arr, title,filename):
	if arr.min()*arr.max()>0.:
		pyplot.pcolormesh(arr,norm=LogNorm())
	else:	pyplot.pcolormesh(arr)
	print "mesh-plot:", title, filename, arr.min(), arr.max(),arr.shape, arr,type(arr)
	print arr.mask
	pyplot.colorbar()
	pyplot.title(title)
	pyplot.axis('tight')
	print "Saving", filename
	pyplot.savefig(filename)
	pyplot.close()	
	

def ncdfToPlots(fn,model):
	print "Making plots from:\t",fn
	nc = dataset(fn,'r',Quiet=True)

	area = nc('area')[:]
	tmask = nc('tmask')[:]	
	if tmask.ndim == 3: 
		volume = nc('pvol')[:]
		maarea = np.ma.masked_where(tmask[0],area)		
		mavol  = np.ma.masked_where(tmask,volume).sum(0)			
	else:
		maarea = np.ma.masked_where(tmask,area)
	lons = nc('lon')[:]
	lats = nc('lat')[:]	
	nc.close()

	
	
	areafn = bvp.folder('images/areas/')+model+'.png'
	meshPlot(maarea, model,areafn )		
	if tmask.ndim == 3: 
		volfn = bvp.folder('images/Volume/')+model+'.png'
		meshPlot(np.ma.masked_where(tmask,np.abs(volume)).sum(0), model, volfn)

	robinfn = bvp.folder('images/Robinson-areas/')+model+'.png'
	if maarea.min()*maarea.max()>0.: doLog = True
	else:	doLog = False
	bvp.robinPlotSingle(lats,lons,maarea,robinfn,model, drawCbar=True,doLog=doLog,)

	if tmask.ndim == 3: 
		robinfn = bvp.folder('images/Robinson-vol/')+model+'.png'

		if mavol.min()*mavol.max()>0.: doLog = True
		else:	doLog = False
		bvp.robinPlotSingle(lats,lons,mavol,robinfn,model, drawCbar=True,doLog=doLog,)
			
#####
# Make the grid file:
def makeGridFile(fn,fnout,field,coordsdict,model ='',threeD=True):
	
	#####
	# copy explicitly all coordintaes, and boundaries.
	# add area and volume and mask.
	print "makeGridFile:\tLoading", fn
	nc = dataset(fn,'r',Quiet=True)

	print "makeGridFile:\tmaking ", fnout,field,model
	dims = list(nc.variables[field].dimensions)
	
#	vartype =  nc.variables[field][:].dtype
#	print vartype, numpy.float32
#	if vartype not in 
	doubletype =  np.float32
	
#	assert 0
	if len(dims)==4:
		##### reduce dimensionality to 3
		zyxdims = dims[1:]
		yxdims = dims[2:]
		
	if len(dims)==3:
		##### reduce dimensionality by one
		yxdims = dims[1:]
		
	area = makeArea(nc,coordsdict)
	tmask = makeMask(nc,field)

	if len(dims)==4:		
		volume= makeVolume(nc,coordsdict,area)
		xsect = {}
		for k in CrossSections.keys():
			xsect[k] = crossectionalAreaAlongLine(fn,model,coordsdict,field=field, points = CrossSections[k], linename = k)
			print xsect[k]
			if xsect[k].min() <0. : 
				print "FAILED:",k	
				assert 0
	#else:
		
	#	assert 0
	nc.close()	


	av = bvp.AutoVivification()
		
	r = 'area'
	av['newVar'][r]['name']		= r
	av['newVar'][r]['long_name']	= r.title()
	av['newVar'][r]['units']	= 'm^2'
	av['newVar'][r]['newDims']	= tuple(yxdims)
	av['newVar'][r]['dtype']	= doubletype
	av['newVar'][r]['newData']	= area	

	if threeD:
		r = 'pvol'
		av['newVar'][r]['name']		= r
		av['newVar'][r]['long_name']	= 'Volume'.title()
		av['newVar'][r]['units']	= 'm^3'
		av['newVar'][r]['newDims']	= tuple(zyxdims)
		av['newVar'][r]['dtype']	= doubletype
		av['newVar'][r]['newData']	= volume	

	if len(dims)==4:
		r = 'tmask'	
		av['newVar'][r]['name']		= r
		av['newVar'][r]['long_name']	= 'Land mask'
		av['newVar'][r]['units']	= ''
		av['newVar'][r]['newDims']	= tuple(zyxdims)
		av['newVar'][r]['dtype']	= doubletype
		av['newVar'][r]['newData']	= tmask	
		
	if len(dims)==3:
		r = 'tmask'	
		av['newVar'][r]['name']		= r
		av['newVar'][r]['long_name']	= 'Land mask'
		av['newVar'][r]['units']	= ''
		av['newVar'][r]['newDims']	= tuple(yxdims)
		av['newVar'][r]['dtype']	= doubletype
		av['newVar'][r]['newData']	= tmask	
	#r = 'DrakePassageMask'	
	#av['newVar'][r]['name']		= r
	#av['newVar'][r]['long_name']	= 'Drake passage'
	#av['newVar'][r]['units']	= '0 is water, 1 is mask'
	#av['newVar'][r]['newDims']	= tuple(zyxdims)
	#av['newVar'][r]['dtype']	= doubletype
	#av['newVar'][r]['newData']	= drakeMask	

	#r = 'Atlantic26N_Mask'	
	#av['newVar'][r]['name']		= r
	#av['newVar'][r]['long_name']	= 'Atlantic Transect at 26N'
	#av['newVar'][r]['units']	= '0 is water, 1 is mask'
	#av['newVar'][r]['newDims']	= tuple(zyxdims)
	#av['newVar'][r]['dtype']	= doubletype
	#av['newVar'][r]['newData']	= Atlantic26N	
	
	for xsec in CrossSections.keys():
		if not threeD:continue
		av['newVar'][xsec]['name']	= xsec
		av['newVar'][xsec]['long_name']	= CrossSectionsLongnames[xsec]
		av['newVar'][xsec]['units']	= 'm^2'
		av['newVar'][xsec]['newDims']	= tuple(zyxdims)
		av['newVar'][xsec]['dtype']	= doubletype
		av['newVar'][xsec]['newData']	= xsect[xsec]	
	
#	if doAMOC:
#		r = 'AMOC_26N_A'	
#		av['newVar'][r]['name']		= r
#		av['newVar'][r]['long_name']	= 'Atlantic Transect at 26N - cross sectional area'
#		av['newVar'][r]['units']	= 'm^2'
#		av['newVar'][r]['newDims']	= tuple(zyxdims)
#		av['newVar'][r]['dtype']	= doubletype
#		av['newVar'][r]['newData']	= amoc	
		
			
#	if doDrake:
#		r = 'Drake_A'
#		av['newVar'][r]['name']		= r
#		av['newVar'][r]['long_name']	= 'Drake passage cross sectional area'
#		av['newVar'][r]['units']	= 'm^2'
#		av['newVar'][r]['newDims']	= tuple(zyxdims)
#		av['newVar'][r]['dtype']	= doubletype
#		av['newVar'][r]['newData']	= drake	
#	
#	if doAMOC:
#		r = 'AMOC_26N_A'	
#		av['newVar'][r]['name']		= r
#		av['newVar'][r]['long_name']	= 'Atlantic Transect at 26N - cross sectional area'
#		av['newVar'][r]['units']	= 'm^2'
#		av['newVar'][r]['newDims']	= tuple(zyxdims)
#		av['newVar'][r]['dtype']	= doubletype
#		av['newVar'][r]['newData']	= amoc	
				
	#### remove unneeded fields	
	av[field]['name' ] 		= 'False'
	av[coordsdict['t']]['name' ] 	= 'False'	
	av['time_bnds']['name' ] 	= 'False'		
	av['average_DT']['name' ] 	= 'False'		
	av['average_T1']['name' ] 	= 'False'		
	av['average_T2']['name' ] 	= 'False'					
	
	c = changeNC(fn, fnout, av,debug=False)
	#ncdfToPlots(fnout,model)	
	print "Finished", fnout



	
#####
# test Area calculation:	
def testArea():

	#import mpl_toolkits.basemap.pyproj.Proj as Proj
	
	# Corners of colorado
	colorado = {"type": "Polygon", "coordinates": [
	    [(-102.05, 41.0),
	     (-102.05, 37.0),
	     (-109.05, 37.0),
	     (-109.05, 41.0),
	     (-102.05, 41.0),]]}
	coloradoArea = 268952044107.43506
	
	area = GetArea(colorado)
	print "Area of colorado should be",coloradoArea,'\tand is:',area, ((100.*area/coloradoArea),'%')
	

		
def main():
	#####
	# Test this alorithm with the 2D ERSST sst file:
	# http://journals.ametsoc.org/doi/10.1175/JCLI-D-14-00006.1
	# ftp://ftp.cdc.noaa.gov/Datasets/noaa.ersst/sst.mnmean.v4.nc
	
	fn = "/data/euryale7/backup/ledm/Observations/ERSST.v4/sst.mnmean.v4.nc"
	fnout = bvp.folder('GridFiles/')+'ERSST_sst.nc'
	field = 'sst'
	coordsdict = {'lat':'lat','lon':'lon','t':'time'}
	model = 'ERSST'
	makeGridFile(fn,fnout,field,coordsdict,model=model,threeD=False)

	#####
	# Test this alorithm with the 3D WOA temperautre  file:
		
	fn = "/data/euryale7/backup/ledm/Observations/WOA/temperature_monthly_1deg.nc"
	fnout = bvp.folder('GridFiles/')+'WOA_temp_grid.nc'
	field = 't_an'
	coordsdict = {'lat':'lat','lon':'lon','t':'time', 'z':'depth'}
	model = 'WOA'
	makeGridFile(fn,fnout,field,coordsdict,model=model,threeD=True)
		
	
if __name__=="__main__":
	
	main()	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
