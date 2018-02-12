#!/usr/bin/ipython
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
.. module:: p2pPlots
   :platform: Unix
   :synopsis: A tool to make plots for point to point analysis.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
	
from netCDF4 import Dataset
from datetime import datetime
from sys import argv
from os.path import exists,split, getmtime, basename
from glob import glob
from shelve import open as shOpen
from matplotlib import pyplot,gridspec, ticker
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import LogNorm
import cartopy

from calendar import month_name
from itertools import product
from scipy.stats import linregress
from scipy.stats.mstats import scoreatpercentile
import numpy as np 

#local imports
import bgcvaltools.unbiasedSymmetricMetrics as usm
from bgcvaltools.StatsDiagram import StatsDiagram
from bgcvaltools.robust import StatsDiagram as robustStatsDiagram
from bgcvaltools import bgcvalpython as bvp 
from regions.makeMask import makeMask,loadMaskMakers
from p2p.slicesDict import populateSlicesList, slicesDict
from longnames.longnames import getLongName, fancyUnits,titleify # getmt
from functions.stdfunctions import extractData

try:	defcmap = pyplot.cm.viridis
except:	
	from bgcvaltools.viridis import viridis
	defcmap = viridis
#from longnames.longnames import MaredatTypes,IFREMERTypes,WOATypes,GEOTRACESTypes

#import seaborn as sb
    

"""	This code makes matched plots, hexbins, scatter plots, and so on.

"""

#BioLogScales 	= ['bac','mesozoo','diatoms','picophyto','microzoo','PP','Seawifs', 'iron'] 
	
noXYLogs 	= [ 'pCO2',
		#'nitrateSurface', 	'nitrateAll',	'nitrateTransect',
		#'phosphateSurface',	'phosphateAll',	'phosphateTransect',
		'silicateSurface',	'silicateAll',	'silicateTransect', 'silicate100m','silicate200m','silicate500m',
		'tempSurface',		'tempAll',	'tempTransect',	'temp100m',	'temp200m','temp1000m',	'temp500m',
		'salSurface', 		'salAll',	'salTransect',	'sal100m',	'sal200m','sal1000m',	'sal500m',]
		
#transectSlices = ['All','Global',]




def robinPlotQuad(lons,
		lats,
		data1, 
                data2, 
                filename, 
                titles=['',''], 
                title='', 
                lon0=0., 
                marble=False, 
                drawCbar=True, 
                cbarlabel='', 
                doLog=False, 
                scatter=True, 
                dpi=100, 
                vmin='', 
                vmax='',
		maptype='Basemap'):#,**kwargs):
	"""
	takes a pair of lat lon, data, and title, and filename and then makes a quad of maps (data 1, data 2, difference and quotient), then saves the figure.
	"""
	fig = pyplot.figure()


	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)
	axs,bms,cbs,ims = [],[],[],[]

	if not vmin: vmin = data1.min()
	if not vmax: vmax = data1.max()
	vmin = min([data1.min(),data2.min(),vmin])
	vmax = max([data1.max(),data2.max(),vmax])			
	
	#doLog, vmin,vmax = determineLimsAndLog(vmin,vmax)
	doLog, vmin,vmax = bvp.determineLimsFromData(data1,data2)
	
	
	doLogs = [doLog,doLog,False,True]
	print "robinPlotQuad:\t",len(lons),len(lats),len(data1),len(data2)
	
	if maptype in ['Basemap','Cartopy']:
		spls = [221,222,223,224]
		fig.set_size_inches(8,5)		
	if maptype=='PlateCarree':		

		mlons = np.ma.masked_where(data1.mask,lons)        
		mlats = np.ma.masked_where(data1.mask,lats)
		
		plotShape = 'Global'	# default
		larange = float(mlats.max()-mlats.min())
		lorange = float(mlons.max()-mlons.min())

		if larange < 40.  and lorange > 180.: 	plotShape = 'longthin'
		if larange > 120. and lorange < 25.: 	plotShape = 'tallthin'		
		print "plot shape:", plotShape
		
	        if plotShape == 'Global': 	
	        	spls = [221,222,223,224]		
			fig.set_size_inches(8,5)			        	
	        if plotShape == 'longthin': 	
	        	spls = [411,412,413,414]			    
			fig.set_size_inches(8,5)			        	
	        if plotShape == 'tallthin': 	
	        	spls = [141,142,143,144]			        
			fig.set_size_inches(8,5)			        	
		
	for i,spl in enumerate(spls):	
		
		if i in [0,1]:
			rbmi = vmin
			rbma = vmax
		if i == 2:	
			rbmi,rbma = bvp.symetricAroundZero(data1,data2)
			#rbma =3*np.ma.std(data1 -data2)
			#print spl,i, rbma, max(data1),max(data2)
			#assert False
			#rbmi = -rbma
		if i == 3:
			rbma = 10. #max(np.ma.abs(data1 -data2))
			rbmi = 0.1		
				
		if doLogs[i] and rbmi*rbma <=0.:
			print "UKESMpython:\trobinPlotQuad: \tMasking",
			data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
			data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
		data = ''
		

		if i in [0,]:	data  = np.ma.clip(data1, 	 rbmi,rbma)
		if i in [1,]:	data  = np.ma.clip(data2, 	 rbmi,rbma)
		if i in [2,]:	data  = np.ma.clip(data1-data2, rbmi,rbma)
		if i in [3,]:	data  = np.ma.clip(data1/data2, rbmi,rbma)
		
		
		if i in [0,1]:
			if rbmi == -rbma:
				 	cmap= pyplot.cm.RdBu_r
			else:		cmap= defcmap
		if i in [2,3]:		cmap= pyplot.cm.RdBu_r
		

		if maptype=='PlateCarree':
                        if doLogs[i]:
                                rbmi = np.int(np.log10(rbmi))
                                rbma = np.log10(rbma)
                                if rbma > np.int(rbma): rbma+=1
                                rbma = np.int(rbma)
					
			axs.append(pyplot.subplot(spl,projection=cartopy.crs.PlateCarree(central_longitude=0.  )))
			ims.append(i)
			#if doLogs[i]: continue
			fig,axs[i],ims[i] = makemapplot(fig,axs[i],lons,lats,data,title, zrange=[rbmi,rbma],lon0=0.,drawCbar=False,cbarlabel='',doLog=False,cmap = cmap)
			print axs[i].get_position()
			assert 0
                        if drawCbar:
                          if i in [0,1,2]:
                                if doLogs[i]:   cbs.append(fig.colorbar(ims[i],ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
                                else:           cbs.append(fig.colorbar(ims[i],))
                          if i in [3,]:
                                cbs.append(fig.colorbar(ims[i],) )#d=0.05,shrink=0.5,))
                                cbs[i].set_ticks ([-1,0,1])
                                cbs[i].set_ticklabels(['0.1','1.','10.'])

#			if drawCbar:
#			  if i in [0,1,2]:
#				if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
#				else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
#			  if i in [3,]:
#				cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
#				cbs[i].set_ticks ([-1,0,1])
#				cbs[i].set_ticklabels(['0.1','1.','10.'])
								
								
			
		if maptype=='Basemap':
			axs.append(fig.add_subplot(spl))		
			bms.append( Basemap(projection='robin',lon_0=lon0,resolution='c') )#lon_0=-106.,
			x1, y1 = bms[i](lons, lats)
			bms[i].drawcoastlines(linewidth=0.5)
			if marble: bms[i].bluemarble()
			else:
				bms[i].drawmapboundary(fill_color='1.')
				bms[i].fillcontinents(color=(255/255.,255/255.,255/255.,1))
			#bms[i].drawparallels(np.arange(-90.,120.,30.))
			#bms[i].drawmeridians(np.arange(0.,420.,60.))
			
			if doLogs[i]:
				rbmi = np.int(np.log10(rbmi))
				rbma = np.log10(rbma)
				if rbma > np.int(rbma): rbma+=1
				rbma = np.int(rbma)
											
			if scatter:
				if doLogs[i]:	
					if len(cbarlabel)>0: 
						cbarlabel='log$_{10}$('+cbarlabel+')'									
					ims.append(bms[i].scatter(x1,y1,c = np.log10(data),cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))# **kwargs))
				else:	ims.append(bms[i].scatter(x1,y1,c = data,	   cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))# **kwargs))
			else:
				xi1,yi1,di1=mapIrregularGrid(bms[i],axs[i],lons,lats,data,lon0,xres=360,yres=180)
				if doLogs[i]: 	ims.append( bms[i].pcolormesh(xi1,yi1,di1,cmap=cmap,norm = LogNorm() ))
				else:	  	ims.append( bms[i].pcolormesh(xi1,yi1,di1,cmap=cmap))
			if drawCbar:
			  	if i in [0,1,2]:
					if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
					else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
			  	if i in [3,]:
					cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					cbs[i].set_ticks ([-1,0,1])
					cbs[i].set_ticklabels(['0.1','1.','10.'])
										  
		  
										  
		if maptype=='Cartopy':
			#axs.append(fig.add_subplot(spl))
			bms.append(pyplot.subplot(spl,projection=ccrs.Robinson()))
			bms[i].set_global()
			

						
			if marble:	bms[i].stock_img()
			else:
				# Because Cartopy is hard wired to download the shapes files from a website that doesn't exist anymore:

				bms[i].add_geometries(list(shapereader.Reader('data/ne_110m_coastline.shp').geometries()),
							ccrs.PlateCarree(), color='k',facecolor = 'none',linewidth=0.5)
			
			if scatter:
				if doLogs[i] and i in [0,1]:
					rbmi = np.int(np.log10(rbmi))
					rbma = np.log10(rbma)
					if rbma > np.int(rbma): rbma+=1
					rbma = np.int(rbma)
							
				if doLogs[i]:
					ims.append(
						bms[i].scatter(lons, lats,c = np.log10(data),
							cmap=cmap,marker="s",alpha=0.9,linewidth='0',
							vmin=rbmi, vmax=rbma,
							transform=ccrs.PlateCarree(),
							)
						)
				else:	
					ims.append(
						bms[i].scatter(lons, lats,c = data,
						        cmap=cmap,marker="s",alpha=0.9,linewidth='0',
						        vmin=rbmi, vmax=rbma,
						        transform=ccrs.PlateCarree(),)
						  )
				if drawCbar:
					  if i in [0,1,2]:
						if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
						else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					  if i in [3,]:
						cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
						cbs[i].set_ticks ([-1,0,1])
						cbs[i].set_ticklabels(['0.1','1.','10.'])
										  
			else:
				crojp2, newData, newLon,newLat = regrid(data.squeeze(),lons, lats)	
				print "cartopy robin quad:",i,spl,newData.shape,newData.min(),newData.max(), rbmi,rbma
				if doLogs[i]:
					ims.append(							
						bms[i].pcolormesh(newLon, newLat,newData,
							transform=ccrs.PlateCarree(),
							cmap=cmap,
							norm=LogNorm(vmin=rbmi,vmax=rbma)
							)
						)
							
				else:
					ims.append(											
						bms[i].pcolormesh(newLon, newLat,newData,
							transform=ccrs.PlateCarree(),
							cmap=cmap,
							vmin=rbmi,vmax=rbma)
						)
				bms[i].coastlines()	#doesn't work.
				#bms[i].fillcontinents(color=(255/255.,255/255.,255/255.,1))
				bms[i].add_feature(cfeature.LAND,  facecolor='1.')	
				if drawCbar:
					  if i in [0,1,2]:
						if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))#ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
						else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
					  if i in [3,]:
						cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
						cbs[i].set_ticks ([0.1,1.,10.])
						cbs[i].set_ticklabels(['0.1','1.','10.'])				

			#else:		ticks = np.linspace( rbmi,rbma,9)
			#print i, spl, ticks, [rbmi,rbma]
			
			#pyplot.colorbar(ims[i],cmap=defcmap,values=[rbmi,rbma])#boundaries=[rbmi,rbma])
		 	#cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5))#,ticks=ticks))
		 	
		 	cbs[i].set_clim(rbmi,rbma)

		    	if len(cbarlabel)>0 and i in [0,1,]: cbs[i].set_label(cbarlabel)
		if i in [0,1]:
			pyplot.title(titles[i])
		if i ==2:	pyplot.title('Difference ('+titles[0]+' - '+titles[1]+')')
		if i ==3:	pyplot.title('Quotient ('  +titles[0]+' / '+titles[1]+')')
	
	if title:
		#fig.text(0.5,0.975,title,horizontalalignment='center',verticalalignment='top')
		fig.suptitle(title)	
	pyplot.tight_layout()		
	print "p2pPlots:\trobinPlotQuad: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()


def makemapplot(fig,ax,lons,lats,data,title, zrange=[-100,100],lon0=0.,drawCbar=True,cbarlabel='',doLog=False,cmap = defcmap):
	"""
	 Wrapper for the map plots.
	Makes a plot according to the options specified in the function call.	
	"""
	if len(lons)==0:return fig,ax
	try:
		if len(lons.compressed())==0:return False, False 
	except:pass
	
	lons = np.array(lons)
	lats = np.array(lats)
	data = np.ma.array(data)	
	
	if doLog and zrange[0]*zrange[1] <=0.:
		print "makemapplot: \tMasking"
		data = np.ma.masked_less_equal(np.ma.array(data), 0.)
	
	print data.min(),lats.min(),lons.min(), data.shape,lats.shape,lons.shape
	
	if data.ndim ==1:
		if doLog:
			im = ax.scatter(lons, lats,c=data, lw=0,marker='s', cmap = cmap, transform=cartopy.crs.PlateCarree(),norm=LogNorm(),vmin=zrange[0],vmax=zrange[1])
		else:	
			im = ax.scatter(lons, lats,c=data, lw=0,marker='s', cmap = cmap, transform=cartopy.crs.PlateCarree(),vmin=zrange[0],vmax=zrange[1])
	else:
		crojp2, data, newLon,newLat = regrid(data,lats,lons)

		if doLog:
			im = ax.pcolormesh(newLon, newLat,data, cmap = cmap, transform=cartopy.crs.PlateCarree(),norm=LogNorm(vmin=zrange[0],vmax=zrange[1]),)
		else:	
			im = ax.pcolormesh(newLon, newLat,data, cmap = cmap, transform=cartopy.crs.PlateCarree(),vmin=zrange[0],vmax=zrange[1])
	
	ax.add_feature(cartopy.feature.LAND,  facecolor='0.85')	

	if drawCbar:
	    c1 = fig.colorbar(im,pad=0.05,shrink=0.75)
	    if len(cbarlabel)>0: c1.set_label(cbarlabel)

	pyplot.title(title)
	print "makemapplot: title:",title	
	ax.set_axis_off()
	pyplot.axis('off')
	ax.axis('off')
		
	return fig, ax, im
	
		
	
def HovPlotQuad(lons,lats, depths, 
		data1,data2,filename,
		titles=['',''],title='',
		lon0=0.,
		marble=False,
		drawCbar=True,
		cbarlabel='',
		doLog=False,
		scatter=True,
		dpi=100,
		vmin='',
		vmax='',
		logy = False,
		maskSurface=True,
		):#,**kwargs):
	"""
	:param lons: Longitude array
	:param lats: Lattitude array	
	:param depths: Depth array	
	:param data1: Data  array
	:param data2: Second data array	
	takes a pair of lat lon, depths, data, and title, and filename and then makes a quad of transect plots
	(data 1, data 2, difference and quotient), then saves the figure.
	"""
	
	fig = pyplot.figure()
	fig.set_size_inches(10,6)
	depths = np.array(depths)
	if depths.max() * depths.min() >0. and depths.max()  >0.: depths = -depths
	
	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)
	if maskSurface:
		data1 = np.ma.masked_where(depths>-10.,data1)
		data2 = np.ma.masked_where(depths>-10.,data2)

		if len(data1.compressed())==0:
			print "No hovmoeller for surface only plots."
			return
	
	doLog, vmin,vmax = bvp.determineLimsFromData(data1,data2)
			
	axs,bms,cbs,ims = [],[],[],[]
	doLogs = [doLog,doLog,False,True]
	print "HovPlotQuad:\t",len(depths),len(lats),len(data1),len(data2)

	#####
	# Plotting coordinate with lowest standard deviation.	
	lon_std = lons.std()
	lat_std = lats.std()	
	if lon_std<lat_std:
		hovXaxis = lats
	else:	hovXaxis = lons
			
	
	for i,spl in enumerate([221,222,223,224]):	
		
		if spl in [221,222]:
			rbmi = vmin
			rbma = vmax
		if spl in [223,]:
			rbmi,rbma = bvp.symetricAroundZero(data1,data2)
			#rbma =3*np.ma.std(data1 -data2)
			#print spl,i, rbma, max(data1),max(data2)
			#rbmi = -rbma
		if spl in [224,]:
			rbma = 10.001 
			rbmi = 0.0999		
				
		if doLogs[i] and rbmi*rbma <=0.:
			print "UKESMpython:\tHovPlotQuad: \tMasking",
			data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
			data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
		data = ''
		
		if spl in [221,]:	data  = np.ma.clip(data1, 	 rbmi,rbma)
		if spl in [222,]:	data  = np.ma.clip(data2, 	 rbmi,rbma)
		if spl in [223,]:	data  = np.ma.clip(data1-data2, rbmi,rbma)
		if spl in [224,]:	data  = np.ma.clip(data1/data2, rbmi,rbma)
		if spl in [221,222,]:	cmap= defcmap
		if spl in [223,224,]:	cmap= pyplot.cm.RdBu_r		
		
		axs.append(fig.add_subplot(spl))
		if scatter:
			if doLogs[i] and spl in [221,222]:
				rbmi = np.int(np.log10(rbmi))
				rbma = np.log10(rbma)
				if rbma > np.int(rbma): rbma+=1
				rbma = np.int(rbma)
					
			if doLogs[i]:	
				ims.append(pyplot.scatter(hovXaxis,depths, c= np.log10(data),cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))
			else:	ims.append(pyplot.scatter(hovXaxis,depths, c=          data ,cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))
			
		else:
			print "hovXaxis:",hovXaxis.min(),hovXaxis.max(),"\tdepths:",depths.min(),depths.max(),"\tdata:",data.min(),data.max()
			newX,newY,newData = arrayify(hovXaxis,depths,data)
			print "newX:",newX.min(),newX.max(),"\tnewY:",newY.min(),newY.max(),"\tnewData:",newData.min(),newData.max() , 'range:', rbmi,rbma			
			if doLogs[i]:	ims.append(pyplot.pcolormesh(newX,newY, newData, cmap=cmap, norm=LogNorm(vmin=rbmi,vmax=rbma),))
			else:		ims.append(pyplot.pcolormesh(newX,newY, newData, cmap=cmap, vmin=rbmi, vmax=rbma,))			
		
		#####
		# All the tools to make a colour bar
		if drawCbar:
			if spl in [221,222,223]:
				if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
				else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
			if spl in [224,]:
				cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
				cbs[i].set_ticks ([0.1,1.,10.])
				cbs[i].set_ticklabels(['0.1','1.','10.'])
	 	
	 		cbs[i].set_clim(rbmi,rbma)
			if doLogs[i] and len(cbarlabel)>0: cbarlabel='log$_{10}$('+cbarlabel+')'	

	    		if len(cbarlabel)>0 and spl in [221,222,]: cbs[i].set_label(cbarlabel)
	    		
	    	#####
	    	# Add the titles.	
		if i in [0,1]:	pyplot.title(titles[i])
		if i ==2:	pyplot.title('Difference ('+titles[0]+' - '+titles[1]+')')
		if i ==3:	pyplot.title('Quotient ('  +titles[0]+' / '+titles[1]+')')
	
		#####
		# Add the log scaliing and limts. 
                if logy: 		axs[i].set_yscale('symlog')	
		if maskSurface:		axs[i].set_ylim([depths.min(),-10.])
		axs[i].set_xlim([hovXaxis.min(),hovXaxis.max()])						
							
		
	#####
	# Add main title
	if title:	fig.text(0.5,0.99,title,horizontalalignment='center',verticalalignment='top')	
	
	#####
	# Print and save
	pyplot.tight_layout()		
	print "UKESMpython:\tHovPlotQuad: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()
	



	
def ArcticTransectPlotQuad(lons,lats, depths, 
		data1,data2,filename,
		titles=['',''],title='',
		lon0=0.,marble=False,drawCbar=True,cbarlabel='',doLog=False,scatter=True,dpi=100,vmin='',vmax='',
		logy = False,
		maskSurface=False,
		transectName  = 'ArcTransect',
		):#,**kwargs):
	"""
	:param lons: Longitude array
	:param lats: Lattitude array	
	:param depths: Depth array	
	:param data1: Data  array
	:param data2: Second data array	
	takes a pair of lat lon, depths, data, and title, and filename and then makes a quad of transect plots
	(data 1, data 2, difference and quotient), then saves the figure.
	This only applies to the Arctic Transect plot
	"""

	depths = np.array(depths)
	if depths.max() * depths.min() >0. and depths.max()  >0.: depths = -depths
	
	lons = np.array(lons)
	lats = np.array(lats)
	data1 = np.ma.array(data1)
	data2 = np.ma.array(data2)

	
	if transectName=='AntTransect':
		####
		# Custom request from Katya for this specific figure.
		data1 = np.ma.array(np.ma.masked_where(depths<-500.,data1).compressed())
		data2 = np.ma.array(np.ma.masked_where(depths<-500.,data2).compressed())
		lats = np.ma.masked_where(depths<-500.,lats).compressed()
		lons = np.ma.masked_where(depths<-500.,lons).compressed()
		depths = np.ma.masked_where(depths<-500.,depths).compressed()
		print lons.shape,lats.shape, depths.shape, data1.shape,data2.shape
		logy = False
		maskSurface = False
		
	if maskSurface:
		data1 = np.ma.masked_where(depths>-10.,data1)
		data2 = np.ma.masked_where(depths>-10.,data2)
		
	if 0 in [len(data1),len(data2)]:
		return
		
	doLog, vmin,vmax = bvp.determineLimsFromData(data1,data2)
	
	fig = pyplot.figure()
	fig.set_size_inches(10,6)			
	axs,bms,cbs,ims = [],[],[],[]
	doLogs = [doLog,doLog,False,True]
	print "ArcticTransectPlotQuad:\t",len(depths),len(lats),len(data1),len(data2)

	#####
	# Artificially build an x axis coordinate list for the Arctic.
	hovXaxis = []
	meanlon = np.mean(lons)
	if transectName in ['ArcTransect','CanRusTransect'] :
		for i,(la,lo) in enumerate(zip(lats,lons)):
			if lo <= meanlon: #lowest lo transect goes first.
				hovXaxis.append(la)
			else:	
				nl = 90.+ abs((90.-la))
				hovXaxis.append(nl)
	else:
		hovXaxis = lats
		
	hovXaxis = np.array(hovXaxis)				

	for i,spl in enumerate([221,222,223,224]):	
		
		if spl in [221,222]:
			rbmi = vmin
			rbma = vmax
		if spl in [223,]:
			rbmi,rbma = bvp.symetricAroundZero(data1,data2)
			#			rbma =3.*np.ma.std(data1 -data2)
			#print spl,i, rbma, max(data1),max(data2)
			#rbmi = -rbma
		if spl in [224,]:
			rbma = 10.001 
			rbmi = 0.0999		
				
		if doLogs[i] and rbmi*rbma <=0.:
			print "UKESMpython:\tArcticTransectPlotQuad: \tMasking",
			data1 = np.ma.masked_less_equal(ma.array(data1), 0.)
			data2 = np.ma.masked_less_equal(ma.array(data2), 0.)
		data = ''
		
		if spl in [221,]:	data  = np.ma.clip(data1, 	 rbmi,rbma)
		if spl in [222,]:	data  = np.ma.clip(data2, 	 rbmi,rbma)
		if spl in [223,]:	data  = np.ma.clip(data1-data2, rbmi,rbma)
		if spl in [224,]:	data  = np.ma.clip(data1/data2, rbmi,rbma)
		if spl in [221,222,]:	cmap= defcmap
		if spl in [223,224,]:	cmap= pyplot.cm.RdBu_r		
		
		axs.append(fig.add_subplot(spl))
		if scatter:
			if doLogs[i] and spl in [221,222]:
				rbmi = np.int(np.log10(rbmi))
				rbma = np.log10(rbma)
				if rbma > np.int(rbma): rbma+=1
				rbma = np.int(rbma)
					
			if doLogs[i]:	
				ims.append(pyplot.scatter(hovXaxis,depths, c= np.log10(data),cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))
			else:	ims.append(pyplot.scatter(hovXaxis,depths, c=          data ,cmap=cmap, marker="s",alpha=0.9,linewidth='0',vmin=rbmi, vmax=rbma,))
			
		else:
			print "ArcticTransectPlotQuad: hovXaxis:",hovXaxis.min(),hovXaxis.max(),"\tdepths:",depths.min(),depths.max(),"\tdata:",data.min(),data.max()
			newX,newY,newData = arrayify(hovXaxis,depths,data)
			print "ArcticTransectPlotQuad: newX:",newX.min(),newX.max(),"\tnewY:",newY.min(),newY.max(),"\tnewData:",newData.min(),newData.max() , 'range:', rbmi,rbma			
			if doLogs[i]:	ims.append(pyplot.pcolormesh(newX,newY, newData, cmap=cmap, norm=LogNorm(vmin=rbmi,vmax=rbma),))
			else:		ims.append(pyplot.pcolormesh(newX,newY, newData, cmap=cmap, vmin=rbmi, vmax=rbma,))			

		if transectName == 'ArcTransect':		
			xticks 		= [ 60.,	    75.,  90.,         105., 120.]
			xtickslabs 	= ['Bering Strait','75N','North Pole','75N','Shetland']
			pyplot.xticks(xticks,xtickslabs)#,labelsize=8)
			pyplot.tick_params(axis='x', which='both', labelsize=9)

		if transectName == 'CanRusTransect':		
			xticks 		= [ 75.,     80.,  85.,  90.,      95., 100.,  105.]
			xtickslabs 	= ['Canada','80N','85N','N. Pole','85N','80N','Siberia']
			pyplot.xticks(xticks,xtickslabs)#,labelsize=8)
			pyplot.tick_params(axis='x', which='both', labelsize=9)
		if transectName == 'AntTransect':
			pyplot.xlabel('Latitude')
	
								
		#####
		# All the tools to make a colour bar
		if drawCbar:
			if spl in [221,222,223]:
				if doLogs[i]:	cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,ticks = np.linspace(rbmi,rbma,rbma-rbmi+1)))
				else:		cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
			if spl in [224,]:
				cbs.append(fig.colorbar(ims[i],pad=0.05,shrink=0.5,))
				cbs[i].set_ticks ([0.1,1.,10.])
				cbs[i].set_ticklabels(['0.1','1.','10.'])
	 	
	 		cbs[i].set_clim(rbmi,rbma)
			if doLogs[i] and len(cbarlabel)>0: cbarlabel='log$_{10}$('+cbarlabel+')'	

	    		if len(cbarlabel)>0 and spl in [221,222,]: cbs[i].set_label(cbarlabel)
	    		
	    	#####
	    	# Add the titles.	
		if i in [0,1]:	pyplot.title(titles[i])
		if i ==2:	pyplot.title('Difference ('+titles[0]+' - '+titles[1]+')')
		if i ==3:	pyplot.title('Quotient ('  +titles[0]+' / '+titles[1]+')')
	
		#####
		# Add the log scaliing and limts. 
                if logy: 		axs[i].set_yscale('symlog')	
		if maskSurface:		axs[i].set_ylim([depths.min(),-10.])
		axs[i].set_xlim([hovXaxis.min(),hovXaxis.max()])						
							
		
	#####
	# Add main title
	if title:	fig.text(0.5,0.99,title,horizontalalignment='center',verticalalignment='top')	
	
	#####
	# Print and save
	pyplot.tight_layout()		
	print "p2pPlots.py:\tArcticTransectPlotQuad: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()



def histPlot(datax, datay,  filename, Title='', labelx='',labely='',xaxislabel='', logx=False,logy=False,nbins=50,dpi=100,minNumPoints = 6, legendDict= ['mean','mode','std','median','mad']):
#	try:import seaborn as sb
#	except:pass
	"""
	Produces a histogram pair.
	"""

	fig = pyplot.figure()
        fig.set_size_inches(6,6)
		
        if len(legendDict)>0:
	       	gs = gridspec.GridSpec(2, 1, height_ratios=[5,2], wspace=0.005, hspace=0.0)
		ax = pyplot.subplot(gs[0])
	else:	ax = pyplot.subplot(111)


	xmin =  np.ma.min([np.ma.min(datax),np.ma.min(datay)])#*0.9
	xmax =  np.ma.max([np.ma.max(datax),np.ma.max(datay)])#*1.1

		
	logx, xmin,xmax = bvp.determineLimsAndLog(xmin,xmax)
	
		
	if datax.size < minNumPoints and datay.size < minNumPoints:
		print "UKESMpython:\thistPlot:\tThere aren't enough points for a sensible dataplot: ", datax.size
		return		

	print "UKESMpython:\thistplot:\t preparing", Title, datax.size, datay.size, (xmin, '-->',xmax)#, datax,datay
		
	if logx:
		n, bins, patchesx = pyplot.hist(datax,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
		n, bins, patchesy = pyplot.hist(datay,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
	else: 
		n, bins, patchesx = pyplot.hist(datax,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax] )
		n, bins, patchesy = pyplot.hist(datay,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax])

	ax.set_xlim([xmin,xmax])			
	pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
	pyplot.setp(patchesy, 'facecolor', 'b', 'alpha', 0.5)

        #if logx:
        #       bins = range(xmin, xmax)
        #       pyplot.xticks(bins, ["2^%s" % i for i in bins])
        #       plt.hist(numpy.log2(data), log=True, bins=bins)

        if logx:
                ax.set_xscale('log')

        if logy: ax.set_yscale('log')
        pyplot.title(Title)
        pyplot.xlabel(xaxislabel)


        leg = pyplot.legend([labelx,labely],loc='best')
        leg.draw_frame(False)
        leg.get_frame().set_alpha(0.)

	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0 + box.height * 0.1,
        #         box.width, box.height * 0.9])
	# Put a legend below current axis
	leg2 = pyplot.legend([labelx,labely], ncol=2,
		loc='upper center', bbox_to_anchor=(0.5, -0.1),)
	leg2.draw_frame(False)
        leg2.get_frame().set_alpha(0.)


	if len(legendDict)>0:
                ax2 = pyplot.subplot(gs[1])
		ax2.axis('off')
		
		if logx: 
			mod = bvp.scimode(np.ma.round(np.ma.log10(datax),2))[0][0]#	
			mod = 10.**mod
		else:	mod = bvp.scimode(np.ma.round(datax,2))[0][0]#		
		med = np.ma.median(datax)
		mea = np.ma.mean(datax)
		std = np.ma.std(datax)
		mad = bvp.MAD(datax)

		txt ='' 
		if 'mean' in legendDict: 	txt += 'Mean:      '+str(round(mea,2)) +'\n'
		if 'median' in legendDict: 	txt += 'Median:   '+str(round(med,2))+'\n'
		if 'mode' in legendDict: 	txt += 'Mode:      '+str(round(mod,2))+'\n'
		if 'std' in legendDict: 	txt += r'$\sigma$'+':             '+str(round(std,2))+'\n'
		if 'mad' in legendDict: 	txt += 'MAD:       '+str(round(mad,2))+'\n'
                ax2.text(0.14,-0.34,txt,horizontalalignment='left',verticalalignment='bottom')
				
		if logx: 
			mody = bvp.scimode(np.ma.round(np.ma.log10(datay),2))[0][0]#
			mody= 10.**mody
		else:	mody= bvp.scimode(np.ma.round(datay,2))[0][0]#	
		
		medy = np.ma.median(datay)
		meay = np.ma.mean(datay)
		stdy = np.ma.std(datay)
		mady = bvp.MAD(datay)
							
		txt ='' 
		if 'mean' in legendDict: 	txt += 'Mean:      '+str(round(meay,2))+'\n'
		if 'median' in legendDict: 	txt += 'Median:   '+str(round(medy,2))+'\n'
		if 'mode' in legendDict: 	txt += 'Mode:      '+str(round(mody,2))+'\n'
		if 'std' in legendDict: 	txt += r'$\sigma$'+':             '+str(round(stdy,2))+'\n'
		if 'mad' in legendDict: 	txt += 'MAD:       '+str(round(mady,2))	+'\n'
		ax2.text(0.63,-0.34,txt,horizontalalignment='left',verticalalignment='bottom')
		
	
	print "UKESMpython:\thistPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)
	pyplot.close()	


def histsPlot(datax, datay,  filename, Title='', labelx='',labely='',xaxislabel='', logx=False,logy=False,nbins=50,dpi=100,minNumPoints = 6):

	"""
	Produces a single histogram.
	"""
	
	fig = pyplot.figure()		

	fig.set_size_inches(10,10)	
	xmin =  np.ma.min([np.ma.min(datax),np.ma.min(datay)])
	xmax =  np.ma.max([np.ma.max(datax),np.ma.max(datay)])
	
	logx, xmin,xmax = bvp.determineLimsAndLog(xmin,xmax)
		
	
	
	if datax.size < minNumPoints and datay.size < minNumPoints:
		print "UKESMpython:\thistsPlot:\tThere aren't enough points for a sensible dataplot: ", datax.size
		return		

	ax = pyplot.subplot(221)	
	if logx:
		n, bins, patchesx = pyplot.hist(datax,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
	else: 
		n, bins, patchesx = pyplot.hist(datax,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax] )
			
	pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
	
	if logx: ax.set_xscale('log')
	if logy: ax.set_yscale('log')
	pyplot.legend([labelx,labely],loc='upper left')
	
	pyplot.title(labelx +' '+Title)	

	ax = pyplot.subplot(222)	
	if logx:
		n, bins, patchesy = pyplot.hist(datay,  histtype='stepfilled', bins=10.**np.linspace(np.log10(xmin), np.log10(xmax), nbins),range=[xmin,xmax])
	else: 
		n, bins, patchesy = pyplot.hist(datay,  bins=np.linspace(xmin, xmax, nbins), histtype='stepfilled',range=[xmin,xmax])
			
	pyplot.setp(patchesy, 'facecolor', 'b', 'alpha', 0.5)
	
	if logx: ax.set_xscale('log')
	if logy: ax.set_yscale('log')
	pyplot.legend([labelx,labely],loc='upper left')
	
	pyplot.title(labely +' '+Title)
	
	

	ax = pyplot.subplot(223)
	pyplot.title('Difference: '+labelx+' - '+labely )	
	d = datax-datay
	maxd = np.max(np.abs(d))
	n, bins, patchesx = pyplot.hist(d,  bins=np.linspace(-maxd, maxd, nbins), histtype='stepfilled',range=[-maxd,maxd] )
	pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5,)		
	y = pyplot.axvline(x=0., c = 'k',ls='--',lw=2,)
	y = pyplot.axvline(x=np.ma.mean(d), c = 'k',ls='-',label= 'Mean Bias: '+str(round(np.ma.mean(d),2)))	
	y = pyplot.axvline(x=np.ma.median(d), c = 'k',ls='--',label= 'Median Bias: '+str(round(np.ma.median(d),2)))		
	pyplot.legend(loc='upper left')
	
	ax = pyplot.subplot(224)
	pyplot.title('Quotient: '+labelx+' / '+labely)	
	d = datax/np.ma.masked_where(datay==0.,datay)

	if logx:		
		maxd = np.ma.power(10.,np.int(np.ma.max(np.ma.abs(np.ma.log10(d)))+1))
		print maxd, 1/maxd
		n, bins, patchesx = pyplot.hist(d,  histtype='stepfilled', bins=10**np.linspace(np.log10(1./maxd), np.log10(maxd), nbins),range=[xmin,xmax])	
		pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
		ax.set_xscale('log')
	else:
		n, bins, patchesx = pyplot.hist(d,  histtype='stepfilled', range=[d.min(),d.max()])	
		pyplot.setp(patchesx, 'facecolor', 'g', 'alpha', 0.5)	
				
	y = pyplot.axvline(x=1., c = 'k',ls='--',lw=2,)
	y = pyplot.axvline(x=np.ma.mean(d), c = 'k',ls='-',label= 'Mean Slope: '+str(round(np.ma.mean(d),2)))	
	y = pyplot.axvline(x=np.ma.median(d), c = 'k',ls='--',label= 'Median Slope: '+str(round(np.ma.median(d),2)))	
	pyplot.legend(loc='upper left')		
	
	print "UKESMpython:\thistPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)
	pyplot.close()	
	
	


	
def scatterPlot(datax, datay,  filename, Title='', labelx='',labely='', logx=False,logy=False, hexPlot = True, bestfitLine=True,addOneToOne=True,gridsize=50,set_equal=True,percentileRange = [0,100],dpi=100):
	"""
	Produces a scatter plot and saves it.
	"""
	statsOutsidePicture = True
	fig = pyplot.figure()	
	if statsOutsidePicture:
                #fig.set_size_inches(5,5.5)
	       	#gs = gridspec.GridSpec(2,1, height_ratios=[5,2], )# wspace=0.005, hspace=0.0)
                fig.set_size_inches(6,5)
                gs = gridspec.GridSpec(1,2, width_ratios=[5,2], )# wspace=0.005, hspace=0.0)

		ax = pyplot.subplot(gs[0])		
		showtext = False	
	else:
		ax = pyplot.subplot(111)
        	fig.set_size_inches(6,5)
		showtext = True

	if percentileRange == [0,100]:
		xmin = datax.min()
		xmax = datax.max()
		ymin = datay.min()
		ymax = datay.max()
	else:
		xmin = scoreatpercentile(datax.compressed(),percentileRange[0])
		xmax = scoreatpercentile(datax.compressed(),percentileRange[1])
		ymin = scoreatpercentile(datay.compressed(),percentileRange[0])
		ymax = scoreatpercentile(datay.compressed(),percentileRange[1])
	
	if set_equal:
		ax.set_aspect("equal")
		#xmin = ymin= np.ma.min([xmin,ymin])
		#xmax = ymax= np.ma.max([xmax,ymax])
                xmin = np.ma.min([xmin,ymin])
                xmax = np.ma.max([xmax,ymax])

	
	dolog, xmin,xmax = bvp.determineLimsAndLog(xmin,xmax)
	logx=dolog
	logy=dolog	
	
	plotrange = [xmin, xmax, xmin, xmax]			
	print "UKESMpython:\tscatterPlot:\trange:",plotrange
	
	if logx: ax.set_xscale('log')
	if logy: ax.set_yscale('log')
		
	#gridsize = 50
	if hexPlot:
		colours = 'Blues' #'gist_yarg' # 'Greens'
		
		#if logx:bins = 10**linspace(np.log10(xmin), np.log10(xmax))
		#else: 
		bins = 'log'

		if logx and logy:
			
			h = pyplot.hexbin(datax, datay,xscale='log', yscale='log',  bins='log', extent=np.log10(plotrange), gridsize = gridsize, cmap=pyplot.get_cmap(colours),mincnt=0)
		else:
			h = pyplot.hexbin(datax, datay, bins='log',gridsize = gridsize, extent=plotrange,cmap=pyplot.get_cmap(colours),mincnt=0)	

		#divider = make_axes_locatable(ax)
		#cax = divider.append_axes('right', size='5%', pad=0.05)
	        #cb = pyplot.colorbar(h, cax=cax, ticks=[0, 1, 2, 3, 4, 5, 6, ],)#fraction=1.)
		cb = pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, ],fraction=0.041, pad=0.04)#fraction=1.)
	
		cb.set_ticklabels([r'$10^0$',r'$10^1$',r'$10^2$',r'$10^3$',r'$10^4$',r'$10^5$',r'$10^6$',])
		#cb.set_label('np.log10(N)')
					
	else:
		pyplot.scatter(datax, datay, marker ='o')	

	if bestfitLine:
		bvp.addStraightLineFit(ax, datax, datay, showtext =False, extent=plotrange)

        if addOneToOne:
		pyplot.plot([xmin,xmax],[xmin,xmax], 'k--')
			
	pyplot.axis(plotrange)	
		
	#pyplot.title(Title)	
	pyplot.xlabel(labelx)
	pyplot.ylabel(labely)


        if statsOutsidePicture:
                b1, b0, rValue, pValue, stdErr = bvp.getLinRegText(ax, datax, datay, showtext =False)
                pyplot.title(Title,loc='left')

                ax2 = pyplot.subplot(gs[1])
		ax2.axis('off')
        	txt =   'Slope      = '+bvp.strRound(b1)             
               	txt+= '\nIntersect = '+bvp.strRound(b0)        
                txt+= '\nP value   = '+bvp.strRound(pValue)
	        txt+= '\nR             = '+ bvp.strRound(rValue)            
                txt+= '\nN             = '+str(int(len(datax)))

                #ax2.text(0.45,-0.14,txt,horizontalalignment='left',verticalalignment='bottom')
                ax2.text(0.,0.5,txt,horizontalalignment='left',verticalalignment='bottom')
	else:
	        pyplot.title(Title)


	print "UKESMpython:\tscatterPlot:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)
	pyplot.close()	
	
		




class makePlots:
  def __init__(self,matchedDataFile,
  		matchedModelFile, 
  		name, 
  		datasource = '',
  		model = '',
  		scenario = '', 
  		jobID='',
  		year='',
  		layer='', 
		modelcoords = '',
		modeldetails = '',
		datacoords = '',
		datadetails = '', 
		shelveDir='',
  		imageDir='',
  		newSlices =['All','Standard'], 
  		compareCoords	= True,  		
  		noPlots		= False,
		clean		= False,  		
  		dpi = 100): #xfilename,yfilename,saveShelve=True,

	""" This is the class that loads all the information and sends it to the plotting tools, above."""
  
  	self.xfn =matchedModelFile
  	self.yfn =matchedDataFile  	
    	self.name = name
    	self.newSlices = newSlices
    	self.layer = layer
  	
  	self.xtype = model  	
  	self.ytype = datasource	
  	  	
  	self.model = model  	
  	self.jobID = jobID
  	self.scenario=scenario
  	self.year = year
  	self.shelveDir = shelveDir
  	self.compareCoords = compareCoords
	self.months 	= {month_name[i+1]:i for i in xrange(0,12) }
	self.noPlots 	= noPlots  
	self.clean 	= clean  
		
	# details about coordinates and what to load.
  	self.modelcoords	= modelcoords
  	self.modeldetails 	= modeldetails
  	self.datacoords 	= datacoords
  	self.datadetails 	= datadetails
  	self.dpi 		= dpi
  	
  	self.newSlices, self.maskingfunctions	= loadMaskMakers(regions = self.newSlices)

		
	

  	if self.shelveDir == '':self.shelveDir = bvp.folder(['shelves',self.xtype,self.year,self.ytype, 'Slices',self.name+self.layer])
  	else:			self.shelveDir = bvp.folder(self.shelveDir)		

	if imageDir=='':	
		self.imageDir = bvp.folder(['images',self.xtype,'P2P_plots',self.year,self.name+self.layer])
		print "Using default image folder:",self.imageDir
	else: 			self.imageDir = bvp.folder(imageDir)

	self.run()
	
	
	
	
  def run(self,):

  	self.xnc = Dataset(self.xfn,'r')
  	self.ync = Dataset(self.yfn,'r')

	if self.compareCoords: self.CompareCoords()
	#self.defineSlices(self.plotallcuts)
	
	
	self.plotWithSlices()

  	self.xnc.close()
  	self.ync.close()  	


  def plotWithSlices(self):#,newSlice,):  
	print "plotWithSlices:\txtype:",self.xtype,"\tytype:",self.ytype,"\tname:",self.name,self.layer
  	
	#####
	# Test if any of the plots exist.
	  	
	xkeys = []
	ykeys = []

	
	#nx = self.mt[self.xtype][self.name]
	
	#if type(nx) == type(['a',]):	xkeys = self.mt[self.xtype][self.name]
	#else:				xkeys.append(self.mt[self.xtype][self.name]['name'])
	#ny = self.mt[self.ytype][self.name]
	#if type(ny) == type(['a',]):	ykeys = self.mt[self.ytype][self.name]
	#else:				ykeys.append(self.mt[self.ytype][self.name]['name'])	
	xkeys = [self.modeldetails['name'],]
	ykeys = [self.datadetails['name'],]	

	print "plotWithSlices:\txkeys:", xkeys,'\tykeys:', ykeys
	if [{}] in [xkeys, ykeys]:
		print "plotWithSlices:\tERROR\t This data type  is not defined in longnames.py"
		print "plotWithSlices:\tx:\t['"+self.xtype+"'\t]['"+self.name+"'] = ",  xkeys
		print "plotWithSlices:\ty:\t['"+self.ytype+"'\t]['"+self.name+"'] = ",  ykeys	
		assert False
	
	#####
	# This section of code is a bit of a time saver.
	# It checks to see if the image and the output shelve exist.
	# If they both exist and and are older than the input netcdfs, the rest of this function is skipped.
	# If one is missing, or the input files are newer than the old image, the function runs as normal.
	# Caveat: if some image can not be made, ie the data makes the mask cover 100% of the data, then the code will run as normal (no skipping).  
	self.shelvesAV = []#AutoVivification()
	
	plotsToMake=0
	for newSlice in self.newSlices:	
	    for xk,yk in product(xkeys,ykeys):
	  	print 'plotWithSlices:\t',newSlice,'\tlisting plotpairs:\tX', xk,': [',self.xtype,'][',self.name,']'
	  	print 'plotWithSlices:\t',newSlice,'\tlisting plotpairs:\tY', yk,': [',self.ytype,'][',self.name,']'	 
		print xk,yk,self.xtype,self.ytype,self.name

		if type(newSlice) in [type(['a','b',]),type(('a','b',))]:	
			ns = ''.join(newSlice)
		else: 	ns = newSlice	
				
		try:fn = ns+'_'+xk+'vs'+yk
	  	except:
	  		print "ERROR:\tcan\'t add ",newSlice,ns,xk,yk, 'together as strings. the problem is probably in your mt dictionary in longnames.'
			assert False
		
		#####
		# Don't make Plots for transects with two spacial cuts.
		#if self.layer.lower().find('transect') >-1 and newSlice not in transectSlices: continue
			
		#####
		# Does the image exist?	
		#filename = self.getFileName(newSlice,xk,yk)
		filename = self.plotname([newSlice,])
		if bvp.shouldIMakeFile([self.xfn,self.yfn],filename,debug=False):
			plotsToMake+=1
		else:
			print "No need to make: ",filename
			
		#####
		#Does the shelve file exist?		
		shelveName = self.shelveDir +self.name+'_'+ns+'_'+xk+'vs'+yk+'.shelve'
		if bvp.shouldIMakeFile([self.xfn,self.yfn],shelveName,debug=False):
			plotsToMake+=1
		else:
			print "No need to make: ",shelveName			
		#####
		# Make a list of shelve meta data, to aid post processing.
		she = bvp.shelveMetadata(model=self.model,
					name=self.name,
					year=self.year,
					layer=self.layer,
					newSlice=newSlice,
					xkey=xk,
					ykey=yk,
					shelve = shelveName)
		self.shelvesAV.append(she)#shelveName						
		#self.shelvesAV[newSlice][xk][yk] = shelveName				
		try:	self.shelves.append(shelveName)
		except:	self.shelves = [shelveName,]

		
	if plotsToMake == 0 and self.clean==False: 
	  	print 'plotWithSlices:\tAll plots and shelve files already made',self.name, newSlice, xkeys,ykeys
		return
	

	#####
	# Load Coordinates
	#time and depth
	self.xt = np.ma.array(self.xnc.variables[self.modelcoords['t']][:])
	self.yt = np.ma.array(self.ync.variables[self.datacoords['t']][:])
	self.xz = np.ma.array(self.xnc.variables[self.modelcoords['z']][:])
	try: 	self.yz = np.ma.array(self.ync.variables[self.datacoords['z']][:])
	except: self.yz = np.zeros_like(self.xt)

	#lat and lon
	self.xy = np.ma.array(self.xnc.variables[self.modelcoords['lat']][:])
	self.yy = np.ma.array(self.ync.variables[self.datacoords['lat']][:])
	self.xx = bvp.makeLonSafeArr(np.ma.array(self.xnc.variables[self.modelcoords['lon']][:]))
	self.yx = bvp.makeLonSafeArr(np.ma.array(self.ync.variables[self.datacoords['lon']][:]))
	
	for newSlice in self.newSlices:	

	    #####
	    # Don't make Plots for transects with two spacial cuts.
	    #if self.layer.lower().find('transect') >-1 and newSlice not in transectSlices: continue	
	    
	    for xkey,ykey in product(xkeys,ykeys):
	    	print "plotWithSlices:\t", newSlice, xkey,ykey
		self.plotsFromKeys(newSlice,xkey,ykey)



  def plotsFromKeys(self,newSlice,xkey,ykey):	     

	#####
	# check that the plot and shelve should be made 
	if type(newSlice) in [type(['a','b',]),type(('a','b',))]:	
		ns = ''.join(newSlice)
	else: ns = newSlice
	self.shelveName = self.shelveDir +self.name+'_'+ns+'_'+xkey+'vs'+ykey+'.shelve'		
 	#filename = self.getFileName(newSlice,xkey,ykey)
 	filename = self.plotname([newSlice,])
	print "plotWithSlices:\tINFO:\tinvestigating:",(newSlice), filename
	if not bvp.shouldIMakeFile([self.xfn,self.yfn],self.shelveName,debug=False) \
		and not bvp.shouldIMakeFile([self.xfn,self.yfn],filename,debug=False): return
	
	
	#####
	# Extract remaining data (already know lat,lon,time,depth)
	xd = extractData(self.xnc,self.modeldetails,) 
	yd = extractData(self.ync,self.datadetails, ) 
 
	
	#####
	# Build mask
	fullmask = xd.mask.astype(int) + yd.mask.astype(int) + np.ma.masked_invalid(xd).mask.astype(int) + np.ma.masked_invalid(yd).mask.astype(int)
	
	if type(newSlice) in [type(['a',]),type(('a',))]:    	# newSlice is actaully a list of multiple slices.
	   	for n in newSlice:
	  		fullmask += makeMask(self.maskingfunctions,self.name,n,self.xt,self.xz,self.xy,self.xx,xd).astype(int)	  
		  	fullmask += makeMask(self.maskingfunctions,self.name,n,self.yt,self.yz,self.yy,self.yx,yd).astype(int)	  
		  	
	elif newSlice == 'Standard':				# Standard is a shorthand for my favourite cuts.
	  	for stanSlice in slicesDict['StandardCuts']: 
			if self.name in ['tempSurface','tempTransect', 'tempAll'] and stanSlice in ['aboveZero',]:continue 
				    						
	  		fullmask += makeMask(self.maskingfunctions,self.name,stanSlice,self.xt,self.xz,self.xy,self.xx,xd).astype(int)
	  	 	fullmask += makeMask(self.maskingfunctions,self.name,stanSlice,self.yt,self.yz,self.yy,self.yx,yd).astype(int)	
	  	 	
	else:  	# newSlice is a simple slice.
	  	fullmask += makeMask(self.maskingfunctions,self.name,newSlice,self.xt,self.xz,self.xy,self.xx,xd).astype(int)
	  	fullmask += makeMask(self.maskingfunctions, self.name,newSlice,self.yt,self.yz,self.yy,self.yx,yd).astype(int)
	  	print 'plotWithSlices:\t',fullmask.sum()

	  
        if self.name in ['mld','mld_DT02','mld_DR003','mld_DReqDTm02']:
        	mldMask = self.ync.variables['mask'][:]
        	fullmask += np.ma.masked_where(mldMask==0.,mldMask).mask        
	  
	
	N = len(self.xt)			

	maskcoverpc = 100.*np.clip(fullmask,0,1).sum()/float(N)
	if maskcoverpc==100.:
		print "plotWithSlices:\tNew Mask,",newSlice,", covers entire dataset.",maskcoverpc,'%', N
		try:	self.shelves[newSlice][xk][yk] = ''
		except:	pass			
		return
	print "plotWithSlices:\tNew Mask,",newSlice,", covers ",maskcoverpc,'% of ', N, 'data'
		
	#####
	# Apply mask to all data.	
	nmxx 	= np.ma.masked_where(fullmask, self.xx).compressed()
	nmxy 	= np.ma.masked_where(fullmask, self.xy).compressed()
	nmxz 	= np.ma.masked_where(fullmask, self.xz).compressed()
	nmxt 	= np.ma.masked_where(fullmask, self.xt).compressed()	
	nmyx 	= np.ma.masked_where(fullmask, self.yx).compressed()
	nmyy 	= np.ma.masked_where(fullmask, self.yy).compressed()
	nmyz 	= np.ma.masked_where(fullmask, self.yz).compressed()
	nmyt 	= np.ma.masked_where(fullmask, self.yt).compressed()
	datax 	= np.ma.masked_where(fullmask, xd).compressed()
	datay 	= np.ma.masked_where(fullmask, yd).compressed()
	
	
	print "plotWithSlices:\tlenghts",  [len(datax),len(datay)],'x:\t',[len(nmxx),len(nmxy)],'y:\t',[len(nmxz),len(nmyx)],'z:\t',[len(nmyy),len(nmyz)]
	if 0 in [len(datax),len(datay),len(nmxx),len(nmxy),len(nmxz),len(nmyx),len(nmyy),len(nmyz)]:
		print 'plotWithSlices:\tWARNING:\tslice:',newSlice,'There is a zero in one of the fields.' 
		#try:	self.shelvesAV[newSlice][xk][yk] = ''			
		#except:	pass			
		return	
						
	dmin = min([datax.min(),datay.min()])
	dmax = max([datax.max(),datay.max()])
	if dmin == dmax: 
		print "plotWithSlices:\tWARNING:\tminimum == maximum,\t (",dmin,' == ',dmax,')'
		#try:	self.shelvesAV[newSlice][xk][yk] = ''
		#except:	pass			
		return
			

	#####
	# Prepare units, axis labels and titles.
	if 'units' in self.modeldetails.keys():
		 xunits = fancyUnits(self.modeldetails['units'])
	else:
		try:    xunits = fancyUnits(self.xnc.variables[self.modeldetails['vars'][0]].units,debug=True)
		except: 
			print "plotWithSlices:\tWARNING:\tno units provided for model ",self.modeldetails['name'],'in details dictionairy'
			xunits = ''

	if 'units' in self.datadetails.keys():
		 yunits = fancyUnits(self.datadetails['units'])	
	else:
		try:   yunits = fancyUnits(self.ync.variables[self.datadetails['vars'][0]].units,debug=True)	
		except:
			print "plotWithSlices:\tWARNING:\tno units provided for data ",self.datadetails['name'],'in details dictionairy'
			yunits = ''
			
	
	labelx = getLongName(self.xtype)+' '+getLongName(self.name)+', '+ xunits
	labely = getLongName(self.ytype)+' '+getLongName(self.name)+', '+ yunits	
	
	title = titleify([newSlice,self.layer,self.name,self.year])	
	#try: title = getLongName(newSlice)+' '+getLongName(self.name+self.layer)#+getLongName(self.name)
	#except:title = newSlice+' '+xkey+' vs '+ykey
			
	scatterfn  	= filename.replace('.png','_scatter.png')
	robfnxy  	= filename.replace('.png','_xyrobin.png')
	robfnquad  	= filename.replace('.png','_robinquad.png')	
	platecquad  	= filename.replace('.png','_PlateCarreeQuad.png')		
	robfncartopy	= filename.replace('.png','_robinquad-cartopy.png')		
	transectquadfn	= filename.replace('.png','_transect.png')			
	histfnxy 	= filename.replace('.png','_hist.png')
	#histsfnxy 	= filename.replace('.png','_hists.png')				
	
	#####
	# Can turn off plots to run analysis faster.
	if self.noPlots:
		print "plotWithSlices:\tSkipping plots ..."
	else:
		#####
		# Robinson projection plots - Basemap
		mptbasemap = True	# Don't need both.			
		if mptbasemap:
		  if bvp.shouldIMakeFile([self.xfn,self.yfn],robfnquad,debug=False):
			ti1 = getLongName(self.xtype)
			ti2 =  getLongName(self.ytype)
			cbarlabel=xunits
			if self.name in noXYLogs or dmin*dmax <=0.:
				doLog=False
			else:	
				doLog=True
			print "plotWithSlices:\tROBIN QUAD:",[ti1,ti2],False,dmin,dmax
			robinPlotQuad(nmxx, nmxy, 
					datax,
					datay,
					robfnquad,
					titles=[ti1,ti2],
					title  = title, #' '.join([getLongName(newSlice),getLongName(self.name),getLongName(self.layer),self.year]),
					cbarlabel=cbarlabel, 
					doLog=doLog,
					vmin=dmin,vmax=dmax,
					maptype='Basemap',
					)
		  if bvp.shouldIMakeFile([self.xfn,self.yfn],platecquad,debug=False):
			ti1 = getLongName(self.xtype)
			ti2 =  getLongName(self.ytype)
			cbarlabel=xunits
			if self.name in noXYLogs or dmin*dmax <=0.:
				doLog=False
			else:	
				doLog=True
                        print "plotWithSlices:\tPlate Carre quad:",[ti1,ti2],False,dmin,dmax
			robinPlotQuad(nmxx, nmxy, 
					datax,
					datay,
					platecquad,
					titles=[ti1,ti2],
					title  = title, #' '.join([getLongName(newSlice),getLongName(self.name),getLongName(self.layer),self.year]),
					cbarlabel=cbarlabel, 
					doLog=doLog,
					vmin=dmin,vmax=dmax,
					maptype='PlateCarree',
					)
					
		# Robinson projection plots - Cartopy
		# Global plot only, and interpollation is switched on.
		#makeCartopy = True	# Don't need both.	
		if newSlice=='Global' and self.layer in ['Surface','100m','200m','500m','1000m',] :
		   # ####
		   # Global, as we have interpollation turned on here.
		   if bvp.shouldIMakeFile([self.xfn,self.yfn],robfncartopy,debug=False):
			ti1 = getLongName(self.xtype)
			ti2 =  getLongName(self.ytype)
			cbarlabel=xunits
			if self.name in noXYLogs or dmin*dmax <=0.:
				doLog=False
			else:	
				doLog=True
			print "plotWithSlices:\tROBIN QUAD:",[ti1,ti2],False,dmin,dmax
			try:
				robinPlotQuad(nmxx, nmxy, 
					datax,
					datay,
					robfncartopy,
					titles=[ti1,ti2],
					title  = title, #' '.join([getLongName(self.name),getLongName(self.layer),self.year]),
					cbarlabel=cbarlabel, 
					doLog=doLog,
					vmin=dmin,vmax=dmax,
					maptype = 'Cartopy',
					scatter=False)
			except:
				print "Cartopy is broken again, can't make: ",robfncartopy

		#####
		# Hovmoeller plots for transects
		if self.layer not in ['Surface','100m','200m','500m','1000m',]:# No point in making these.
		  if bvp.shouldIMakeFile([self.xfn,self.yfn],transectquadfn,debug=False):
			ti1 = getLongName(self.xtype)
			ti2 =  getLongName(self.ytype)
			cbarlabel=xunits			
			if self.name in noXYLogs or dmin*dmax <=0.:
				doLog=False
			else:	
				doLog=True
			print "plotWithSlices:\ttransect quad:",[ti1,ti2],False,dmin,dmax
			if self.layer in ['ArcTransect','AntTransect','CanRusTransect',]:
				ArcticTransectPlotQuad(nmxx,nmxy, nmxz, 
					datax,
					datay,
					transectquadfn,
					titles=[ti1,ti2],
					title  = title , #' '.join([getLongName(self.name),getLongName(self.layer),self.year]),
					cbarlabel=cbarlabel, 
					doLog=doLog,
					vmin=dmin,
					vmax=dmax,
					scatter 	= False,
					logy		= True,
					transectName  	= self.layer,
					)			
			else:
				HovPlotQuad(nmxx,nmxy, nmxz, 
					datax,
					datay,
					transectquadfn,
					titles=[ti1,ti2],
					title  = title, #' '.join([getLongName(self.name),getLongName(self.layer),self.year]),
					cbarlabel=cbarlabel, 
					doLog=doLog,
					vmin=dmin,
					vmax=dmax,
					scatter = False,
					logy=True,
					)		
		
		#####
		# Simultaneous histograms plot	- single
		if bvp.shouldIMakeFile([self.xfn,self.yfn],histfnxy,debug=False):
			xaxislabel= getLongName(self.name)+', '+ xunits
			labelx = self.xtype
			labely = self.ytype
			histtitle = title
			histxaxis = xaxislabel
			if self.ytype in ['LANA', 'LANA_p']:
				labelx = getLongName(self.name)
				labely = getLongName(self.ytype)
				histtitle = getLongName(newSlice) +' DMS: '+labelx +' vs '+ labely
				histxaxis = 'DMS, '+ xunits
				
			if self.name in noXYLogs or dmin*dmax <=0.:				
				histPlot(datax, datay,  histfnxy, Title=histtitle, labelx=labelx,labely=labely,dpi=self.dpi,xaxislabel =histxaxis)	
			else:	histPlot(datax, datay,  histfnxy, Title=histtitle, labelx=labelx,labely=labely,dpi=self.dpi,xaxislabel =histxaxis, logx = True, )

		# Simultaneous histograms plot	- triple
		#if bvp.shouldIMakeFile([self.xfn,self.yfn],histsfnxy,debug=False):
		#	xaxislabel= getLongName(self.name)+', '+ xunits
		#	if self.name in noXYLogs or dmin*dmax <=0.:				
		#		bvp.histsPlot(datax, datay,  histsfnxy, Title=title, labelx=self.xtype,labely=self.ytype,xaxislabel =xaxislabel)	
		#	else:	bvp.histsPlot(datax, datay,  histsfnxy, Title=title, labelx=self.xtype,labely=self.ytype,xaxislabel =xaxislabel, logx = True, )
							
			
		#####
		# Scatter  (hexbin) plot
		if bvp.shouldIMakeFile([self.xfn,self.yfn],scatterfn,debug=False):		
			gs = 50	
			scattitle = title
			slabelx = labelx
			slabely = labely	
			if self.ytype in ['LANA', 'LANA_p']:
				slabelx = getLongName(self.name)+' DMS, '+ xunits
				slabely = getLongName(self.ytype)+' DMS, '+ xunits		
				scattitle = getLongName(newSlice) +' DMS: '+getLongName(self.name) +' vs '+ getLongName(self.ytype)		
				
				pass
			
			if self.name in noXYLogs or dmin*dmax <=0.:
				scatterPlot(datax, datay,  scatterfn, Title=scattitle, labelx=slabelx,labely=slabely,dpi=self.dpi, bestfitLine=True,gridsize=gs)
			else:	scatterPlot(datax, datay,  scatterfn, Title=scattitle, labelx=slabelx,labely=slabely,dpi=self.dpi, bestfitLine=True,gridsize=gs,logx = True, logy=True,)

	#####
	# Save fit in a shelve file.		
	s = shOpen(self.shelveName)
	print "plotWithSlices:\tSaving ",self.shelveName	
	b1, b0, rValue, pValue, stdErr = linregress(datax, datay)
	print "plotWithSlices:\tlinear regression: \n\tb1:",b1, "\n\tb0:", b0, "\n\trValue:",rValue, "\n\tpValue:",pValue, "\n\tstdErr:",stdErr
	s['b1'] 	=  b1
	s['b0'] 	=  b0
	s['rValue'] 	=  rValue
	s['pValue'] 	=  pValue
	s['stdErr'] 	=  stdErr						
	s['N'] 	    	=  len(datax)
					
  	mtaylor = StatsDiagram(datax,datay)
	s['Taylor.E0'] 	= mtaylor.E0
	s['Taylor.E']	= mtaylor.E
	s['Taylor.R']	= mtaylor.R
	s['Taylor.p']	= mtaylor.p							
	s['Taylor.gamma']=mtaylor.gamma


	s['MNAFE'] = usm.MNAFE(datax,datay)
	s['MNFB' ] = usm.MNFB( datax,datay)
	s['NMAEF'] = usm.NMAEF(datax,datay)
	s['NMBF' ] = usm.NMBF( datax,datay)	
			
				
	mrobust = robustStatsDiagram(datax,datay,0.01)
	print "makePlots.py:\tWARNING: robustStatsDiagram CALCULATED WITH DEFAULT PRECISION (0.01)"
	s['robust.E0'] 	= mrobust.E0
	s['robust.E']	= mrobust.E
	s['robust.R']	= mrobust.R
	s['robust.p']	= mrobust.p							
	s['robust.gamma']=mrobust.gamma	
		
	s['datax'] = datax
	s['datay'] = datay

	s['x_lon'] = nmxx
	s['x_lat'] = nmxy
	s['x_depth'] = nmxz
	s['x_time'] = nmxt			
	s['y_lon'] = nmyx
	s['y_lat'] = nmyy
	s['y_depth'] = nmyz
	s['y_time'] = nmyt					
			
	s['title'] = 	title
	s['labelx'] = 	labelx
	s['labely'] = 	labely
	s['name'] =   	self.name
	s['layer'] =   self.layer	
	s['region'] =   self.layer		
	s['year'] =   	self.year 
	s['xtype'] =  	self.xtype
	s['ytype'] =  	self.ytype
	s['xfn'] =  	self.xfn
	s['yfn'] =  	self.yfn
	s['slice']= 	newSlice
	s['newSlice'] = ns
	s['xkey'] = 	xkey			
	s['ykey'] = 	ykey
	s.close()

 
  	

  def CompareCoords(self,):
	"""	This routine plots the coordinates of the data against the coordinates of the model.
		This should produce a straight line plot, ensuring that the matching has been performed correctly.
	"""
	#import seaborn as sb
	#sb.set(style="ticks")
	xcoords = [self.modelcoords[k] for k in ['t','lat','lon','z','lon',]]
	ycoords = [self.datacoords[k]  for k in ['t','lat','lon','z','lat',]]
	  	 	  	
  	for xkey,ykey in zip(xcoords,ycoords):
	    	if xkey not in self.xnc.variables.keys():continue  	    
	    	if ykey not in self.ync.variables.keys():continue
		filename = bvp.folder(self.imageDir+'CompareCoords')+'CompareCoords'+self.name+self.layer+xkey+'vs'+ykey+'.png'	    	
		if not bvp.shouldIMakeFile([self.xfn,self.yfn],filename,debug=False):continue
		print "CompareCoords:\tx:",xkey, "\ty:",ykey
		if xkey not in self.xnc.variables.keys():
			print xkey, "not in xnc"
			assert False
		if ykey not in self.ync.variables.keys():
			print ykey, "not in ync"
			assert False		
		

		mask = np.ma.array(self.xnc.variables[xkey][:]).mask + np.ma.array(self.ync.variables[ykey][:]).mask
		dx = np.ma.masked_where(mask, np.ma.array(self.xnc.variables[xkey][:])).compressed()
		dy = np.ma.masked_where(mask, np.ma.array(self.ync.variables[ykey][:])).compressed()
				
		print "CompareCoords:\t",xkey,':', len(dx)
		print "CompareCoords:\t",ykey,':', len(dy)
		print [dx.min(),dx.max()], [dy.min(), dy.max()]
	
		fig = pyplot.figure()
		fig.set_size_inches(8, 12)		
		ax = pyplot.subplot(411)

		rects1 = pyplot.hist((dx,dy),label=[xkey,ykey],histtype='bar',bins=72/2)#,alpha=0.2)
		pyplot.legend()
		ax.set_yscale('log')

		ax.set_title(xkey + ' and '+ykey)		
		ax = pyplot.subplot(412)		
		rects3 = pyplot.hist(dx - dy,bins=72,label=[xkey + ' - '+ykey])
		pyplot.legend()
		ax.set_yscale('log')

		ax = pyplot.subplot(212)
		pyplot.hexbin(dx, dy, bins='log',gridsize = 72, cmap=pyplot.get_cmap('gist_yarg'),mincnt=0)#extent=plotrange,
		cb = pyplot.colorbar()				
		mmax = max(dx.max(),dy.max())
		mmin = min(dx.min(),dy.min())
			
		fx = np.arange(mmin, mmax, (mmax-mmin)/20.)
		pyplot.plot(fx,fx, 'k--')
		ax.set_aspect("equal")

		pyplot.xlabel(self.xtype+' '+xkey)
		pyplot.ylabel(self.ytype+' '+ykey)

		print "\tSaving: " + filename
		pyplot.savefig(filename,dpi=self.dpi,)
		pyplot.close()	  	


	
 		
  def getFileName(self,newSlice,xkey,ykey):
  	#####
  	# This needs some work.
	#for dictkey,dictlist in slicesDict.items():
	#	if dictkey=='AllSlices':continue
	#	if newSlice not in dictlist: continue
	#	if type(newSlice) in [type(['a','b',]),type(('a','b',))]: 
	#		newSlice = list(newSlice)
	#		for i,n in enumerate(newSlice):
	#		   if n in slicesDict['Months']:
	#		   	newSlice[i] = bvp.mnStr(self.months[n]+1)+n
	#		newSlice = ''.join(newSlice)			
	#	if newSlice in slicesDict['Months']:
	#		 newSlice = bvp.mnStr(self.months[newSlice]+1)+newSlice	
	#	if dictkey == 'Default': dictkey=''
	
	return bvp.folder(self.imageDir)+'_'.join([self.model,self.jobID,self.name,self.layer,newSlice,xkey,ykey,self.xtype,self.year])+'.png'

  def plotname(self,ls):
	pn = bvp.folder(self.imageDir)
	listt = [self.model, self.scenario, self.jobID,	self.name,self.layer,self.year]
	listt.extend(ls)
	pn += '_'.join(listt)+'.png'
	return pn



		
if __name__=="__main__":
	print "makePlots isn't written to be run as a __main__"
	print "Look at testsuite_p2p.py for examples on how to run this."
	print 'The end.'
	
