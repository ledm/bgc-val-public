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
.. module:: timeseriesPlots
   :platform: Unix
   :synopsis: A swiss army knife set of plotting tools for the time series analysis.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>
"""

from matplotlib import pyplot, gridspec

from matplotlib.colors import LogNorm
import matplotlib.patches as mpatches
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable

import cartopy
import numpy as np
from numpy import hanning,hamming,bartlett,blackman 
from scipy import interpolate 
#from statsmodels.nonparametric.smoothers_lowess import lowess


import timeseriesTools as tst
from bgcvaltools.viridis import viridis,discrete_viridis
from bgcvaltools import bgcvalpython as bvp

defcmap = viridis
defcmapstr = 'viridis'

#try:	
#	defcmap = pyplot.cm.jet
#	defcmapstr = 'jet'
#except:	
#	defcmap = viridis
#	defcmapstr = 'viridis'	

cmipcolours = 	['goldenrod',
		 'navy',
		 'royalblue',
		 'lightskyblue',		 
		 'lightseagreen',
		 'seagreen',		 		 
		 'green',
		 'olive',
		 'burlywood',
		 'sienna',
		 'salmon',		 
		 'red',
		 'purple',
		 'plum',
		 'violet',
		 'dodgerblue',
		 'black',
		 'grey',		 
		 'gold',
		 'blue',
		 'lime',
		 'firebrick',
		 'chocolate',
		 'orange']


def trafficlights(ax,xlims, bands,labels=[],drawlegend=True):
	if len(bands) != 6: print "wrong number of bands to traffic light."

	ax.fill_between(xlims,bands[0], bands[1] ,color='r', 		alpha = 0.2)		
	ax.fill_between(xlims,bands[1] ,bands[2] ,color='DarkOrange', 	alpha = 0.2)				
	ax.fill_between(xlims,bands[2] ,bands[3] ,color='g', 		alpha = 0.2)
	ax.fill_between(xlims,bands[3] ,bands[4] ,color='DarkOrange', 	alpha = 0.2)
	ax.fill_between(xlims,bands[4] ,bands[5] ,color='r', 		alpha = 0.2)	
	
	if len(labels)==5:
		patch4 = mpatches.Patch(color='r', 		alpha = 0.2,label=labels[4])
		patch3 = mpatches.Patch(color='DarkOrange', 	alpha = 0.2,label=labels[3])
		patch2 = mpatches.Patch(color='g', 		alpha = 0.2,label=labels[2])
		patch1 = mpatches.Patch(color='DarkOrange', 	alpha = 0.2,label=labels[1])
		patch0 = mpatches.Patch(color='r', 		alpha = 0.2,label=labels[0])		
		handles = [patch4,patch3,patch2,patch1,patch0,]
		if drawlegend: pyplot.legend(handles=handles)
	return ax

def drawgreyband(ax,xaxis, bands,labels=[], **kwargs):
	ax.fill_between(xaxis,bands[0], bands[1] ,color='k', 	alpha = 0.05, **kwargs)
	return ax


def drawLegendAlongside(ax,numberoflines,space=0.1):
	#####
	# Add legend outisde axes
	legendSize = numberoflines+1
	ncols = int(legendSize/25)+1
	box = ax.get_position()
	ax.set_position([box.x0,
			  box.y0 ,
			  box.width*(1.- space*ncols), 
			  box.height ])
										
	legd = ax.legend(loc='center left', ncol=ncols,prop={'size':10},bbox_to_anchor=(1., 0.5))
	legd.draw_frame(False) 
	legd.get_frame().set_alpha(0.)	
	return ax
		 
		 


def percentilesPlot(
		timesDict,		# model times dict
		modeldataDict,		# model data dictionairy
		dataslice,		# in situ data distribution
		dataweights = [],	# in situ data weights (approx cell area)
		title 	='',
		filename='',
		units = '',		
		greyband= 'MinMax',	# MinMax, 10-90pc or none
		dolog=True
	):
	
	metrics = sorted(timesDict.keys())

	#####
	# Determine the x axis limts.	
	mint = np.ma.min(timesDict[metrics[0]])
	maxt = np.ma.max(timesDict[metrics[0]])
	xlims= [mint,maxt]	
	
	if greyband == 'MinMax':
		miny = np.ma.min(modeldataDict['min'])
		maxy = np.ma.max(modeldataDict['max'])
	elif greyband == '10-90pc':	
		miny = np.ma.min(modeldataDict['10pc'])
		maxy = np.ma.max(modeldataDict['90pc'])	
	else:
		miny = np.ma.min(modeldataDict['20pc'])
		maxy = np.ma.max(modeldataDict['80pc'])		
		
	if miny in [np.ma.masked, np.nan,np.inf]:
		print "percentilesPlot:\tIt is not possible to make this plot,(",title,"), as the min values are no plottable:",miny
		return
		
		
	
			
	#####
	# Make, resize and divide the figure into an uneven grid/
	fig = pyplot.figure()
	#fig.set_size_inches(10,6)	
        fig.set_size_inches(8,4)
	gs = gridspec.GridSpec(1, 2, width_ratios=[12,1], wspace=0.0, hspace=0.0) 		
	
	#####
	# Data plot to the r.
	axd = pyplot.subplot(gs[1])	

	if len(dataslice):
		if not len(dataweights): dataweights = np.ma.ones_like(dataslice)	
		
		#dataslice   = np.ma.masked_where(dataslice.mask + dataweights.mask,dataslice)
		#dataweights = np.ma.masked_where(dataslice.mask + dataweights.mask,dataweights)		
		pcs = [10.,20.,30.,40.,50.,60.,70.,80.,90.]
		out_pc = bvp.weighted_percentiles(dataslice, pcs, weights = dataweights)
		datapcs = {p:o for p,o in zip(pcs,out_pc)}
		
		pc1 = np.array([datapcs[20.] for i in xlims])
		pc2 = np.array([datapcs[30.] for i in xlims])
		pc3 = np.array([datapcs[40.] for i in xlims])
		pc4 = np.array([datapcs[60.] for i in xlims])
		pc5 = np.array([datapcs[70.] for i in xlims])
		pc6 = np.array([datapcs[80.] for i in xlims])
		labels = ['20-30 pc','30-40 pc','40-60 pc','60-70 pc','70-80 pc',]
		axd = trafficlights(axd,xlims, [pc1,pc2,pc3,pc4,pc5,pc6],labels=labels,drawlegend=False)

		axd.axhline(y=np.ma.average(dataslice,weights=dataweights),  c='k',ls='--',lw=1.5,)#label='mean')
		axd.axhline(y=datapcs[50.],c='k',ls='-', lw=1.5,)#label='median')
				
		if greyband == 'MinMax':
			pcmin 	= np.array([dataslice.min() for i in xlims])
			pcmax 	= np.array([dataslice.max() for i in xlims])
			axd  	= drawgreyband(axd,xlims, [pcmin,pc1],)
			axd  	= drawgreyband(axd,xlims, [pc6,pcmax],)
			miny_dat = np.ma.min(dataslice)
			maxy_dat = np.ma.max(dataslice)
		elif greyband == '10-90pc':
			pcmin 	= np.array([datapcs[10.] for i in xlims])
			pcmax 	= np.array([datapcs[90.] for i in xlims])
			axd  	= drawgreyband(axd,xlims, [pcmin,pc1],)
			axd  	= drawgreyband(axd,xlims, [pc6,pcmax],)	
			miny_dat = datapcs[10.]
			maxy_dat = datapcs[90.]					
		else:
			 miny_dat = datapcs[20.]
			 maxy_dat = datapcs[80.]
		if miny_dat < miny: miny = miny_dat
		if maxy_dat > maxy: maxy = maxy_dat		
	ylims= [miny,maxy]

	#####
	# Widen the ylims.
	if np.ma.max(ylims)/np.ma.min(ylims)>20.:	
		#####
		# log
		ylims[0] = ylims[0]*0.6
		ylims[1] = ylims[1]*1.4	
	else:	#####
		# not log
		diff = abs(ylims[1] - ylims[0])
		ylims[0] = ylims[0]-diff/20.
		ylims[1] = ylims[1]+diff/20.
		
	
	# Add a legend
	box = axd.get_position()
	axd.set_position([box.x0,
			  box.y0 ,
			  box.width*0.8, 
			  box.height ])
		

	labels = ['10-20','20-30','30-40','40-60','60-70','70-80','80-90',]
	a1 = pyplot.fill_between([],[],[],alpha = 0.,	color='w',		label='%ile')				
	b1 = pyplot.fill_between([],[],[],alpha = 0.05,	color='k',		label=labels[6])			
	c1 = pyplot.fill_between([],[],[],alpha = 0.2,	color='r',		label=labels[5])
	d1 = pyplot.fill_between([],[],[],alpha = 0.2,	color='DarkOrange',	label=labels[4])			
	e1 = pyplot.fill_between([],[],[],alpha = 0.2,	color='g',		label=labels[3])
	f1 = pyplot.fill_between([],[],[],alpha = 0.2,	color='DarkOrange',	label=labels[2])			
	g1 = pyplot.fill_between([],[],[],alpha = 0.2,	color='r',		label=labels[1])									
	h1 = pyplot.fill_between([],[],[],alpha = 0.05,	color='k',		label=labels[0])
	i1 = pyplot.fill_between([],[],[],alpha = 0.,	color='w',label=' ')				
	#j1 = pyplot.plot([],[], 'k--', lw=1.5, label='mean')
	#k1 = pyplot.plot([],[], 'k-',  lw=1.5, label='median')
	j1 = pyplot.Line2D([],[], color='k', ls='--', lw=1.5, label='mean 2')
	k1 = pyplot.Line2D([],[], color='k', ls='-',  lw=1.5, label='median 2')	
	
	legendOrder = [a1,b1,c1,d1,e1,f1,g1,h1,i1,j1,k1,]
	legendTxt   = ['%ile', labels[6],labels[5],labels[4],labels[3],labels[2],labels[1],labels[0], ' ','mean', 'median']
	#handles, labels = axd.get_legend_handles_labels()
	# reverse the order
	#ax.legend(legendOrder, legendTxt)
	#print handles, labels
	#assert 0
												
	legd = axd.legend(handles = legendOrder,labels = legendTxt, loc='center left', ncol=1,prop={'size':9},bbox_to_anchor=(0.9, 0.5))
	legd.draw_frame(False) 
	legd.get_frame().set_alpha(0.)	

	#lege = axd.legend( loc='center left', ncol=1,prop={'size':9},bbox_to_anchor=(0.9, 0.5)) #[j1,k1,],['mean', 'median',]
	#lege.draw_frame(False) 
	#lege.get_frame().set_alpha(0.)	
	
	axd.text(0.5,0.985,'Data',
		va='top',ha='center',
		transform=axd.transAxes)



	#####
	# Model plot to the left.	
	axm = pyplot.subplot(gs[0])	

	axm.text(1.,0.985,'Model  ',
		va='top',ha='right',
		transform=axm.transAxes)


	pyplot.plot(timesDict['mean'],  modeldataDict['mean']  ,'k--',lw=1,)#label='mean')
	pyplot.plot(timesDict['median'],modeldataDict['median'],'k-', lw=1,)#label='median')	
			
	#legend = pyplot.legend(loc='lower center',  numpoints = 1, ncol=2, prop={'size':12}) 
	#legend.draw_frame(False) 
	#legend.get_frame().set_alpha(0.)
		
	
	labels = ['20-30 pc','30-40 pc','40-60 pc','60-70 pc','70-80 pc',]	
	trafficarray = [modeldataDict[m] for m in ['20pc','30pc','40pc','60pc','70pc','80pc']]
	axm = trafficlights(axm,timesDict['min'], trafficarray,labels=labels,drawlegend=False)		

	if greyband == 'MinMax':
		axm  	= drawgreyband(axm,timesDict['min'], [modeldataDict[m] for m in ['min','20pc']],)
		axm  	= drawgreyband(axm,timesDict['min'], [modeldataDict[m] for m in ['80pc','max']],)				

	if greyband == '10-90pc':
		axm  	= drawgreyband(axm,timesDict['min'], [modeldataDict[m] for m in ['10pc','20pc']],)
		axm  	= drawgreyband(axm,timesDict['min'], [modeldataDict[m] for m in ['80pc','90pc']],)				


	#yticks = list(axm.get_xticks())
	#ytickLabels = list(axm.get_yticklabels())

	
	axm.set_xlim(xlims)	
	axm.set_title(title)	


					
	axm.set_ylim(ylims)	
	axd.set_ylim(ylims)

	#if np.ma.max(ylims)/np.ma.min(ylims)>500.:
	#	axm.set_yscale('log')	
	#	axd.set_yscale('log')

	modelleft = 0#True
	if modelleft:
		axm.get_yaxis().set_ticklabels([])			
		axd.get_xaxis().set_ticks([])	
	
		if greyband == 'MinMax':
			ytickLabels	= ['min',  '20pc','30pc','40pc','60pc','70pc','80pc','max']
		elif greyband == '10-90pc':	
			ytickLabels	= ['10pc', '20pc','30pc','40pc','60pc','70pc','80pc','90pc']
		else:
			ytickLabels	= [        '20pc','30pc','40pc','60pc','70pc','80pc',]			

		yticks = [ modeldataDict[m][-1]	for m in ytickLabels]
		axm.set_yticks(yticks)
		axm.set_yticklabels(ytickLabels,fontsize=10)
		axm.yaxis.tick_right()		
	else:
		#axm.get_yaxis().set_ticklabels([])			
		axd.get_xaxis().set_ticks([])	
		axm.set_ylabel(units)



				
					
		#if greyband == 'MinMax':
	#	#	ytickLabels	= ['min',  '20pc','30pc','40pc','60pc','70pc','80pc','max']
		#elif greyband == '10-90pc':	
		#	ytickLabels	= ['10pc', '20pc','30pc','40pc','60pc','70pc','80pc','90pc']
		#else:
		#	ytickLabels	= [        '20pc','30pc','40pc','60pc','70pc','80pc',]			

		#yticks = [ modeldataDict[m][-1]	for m in ytickLabels]
		#axm.set_yticks(yticks)
		#axm.set_yticklabels(ytickLabels,fontsize=10)
		#axm.yaxis.tick_right()	
		
	
	print "timeseriesPlots:\tpercentilesPlot:\tSaving:" , filename
	try:pyplot.savefig(filename )
	except:	print "WARNING: THIS PLOT FAILED:",filename , '(probably beaucse of all masks/ infs./nans)'
	pyplot.close()	

def getSmallestAboveZero(arr):
	arr = np.array(arr)
	return np.ma.masked_where(arr<=0.,arr).min()
	




def simpletimeseries(
		times, 		# model times (in floats)
		arr,		# model time series
		data,		# in situ data distribution
		title 	='',
		filename='',
		units = '',
		greyband = False		
	):
	#####
	# This is exclusively used for sums now.
	
	if len(times) ==0 or len(arr) == 0:
		print "trafficlightsPlot:\tWARNING:\tdata or time arrays are empty.",len(times),len(arr),title
		return
	if np.ma.is_masked(arr):
		print "trafficlightsPlot:\tWARNING:\tdata arrays is masked",len(times),len(arr),title
		return
				
	xlims= [times[0],times[-1]]
	
	fig = pyplot.figure()
	ax = fig.add_subplot(111)	
        fig.set_size_inches(6,5)

	
        arr_new = movingaverage_DT(arr,times, window_len=5.,window_units='years')	# 5 year average.
	pyplot.plot(times,arr,    c='b',ls='-',lw=0.2, label = 'Model')	
	pyplot.plot(times,arr_new,c='b',ls='-',lw=2. , label='Model 5yr moving average')
		
	pyplot.xlim(xlims)	
	pyplot.title(title)	
	pyplot.ylabel(units)

        if data not in [np.ma.masked,np.ma.array([0.,0.],mask=True)[0],-999,-999.,] and np.isnan(data)==False and np.isinf(data) == False:
		pyplot.axhline(y=data,c='k',ls='-',lw=1,label = 'Data')
		
#	legend = pyplot.legend(loc='lower center',  numpoints = 1, ncol=2, prop={'size':16}) 
#	legend.draw_frame(False) 
#	legend.get_frame().set_alpha(0.)
		
	print "timeseriesPlots:\tsimpletimeseries:\tSaving:" , filename
	pyplot.savefig(filename )
	pyplot.close()	


def movingaverage(interval, window_size):
	window = np.ones(int(window_size))/float(window_size)
	counts = np.arange(len(interval))
	arr = np.convolve(interval, window, 'same')
	return np.ma.masked_where((counts<window/2.) + (counts>len(arr)-window/2.) ,arr)    


def movingaverage2(x,window_len=11,window='flat',extrapolate='axially'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """
    x = np.array(x)
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            , 'robust']:
        raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

 # extrapolation by reflection of dat at end point
    wlp1=window_len+1
 # get stopping index for backward iteration in extrapolation
    if wlp1>x.size:
        mwlp1=None
    else:
        mwlp1=-wlp1
    if extrapolate=='axially':
        s=np.r_[x[window_len-1:0:-1],x,x[-2:mwlp1:-1]]
 # extrapolation by circular wrapping
    elif extrapolate=='periodically':
        s=np.r_[x[-window_len+1:],x,x[:window_len-1]]
 # extrapolation by rotation of data at end point
    elif extrapolate=='rotation':
        s=np.r_[2*x[0]-x[window_len-1:0:-1],x,2*x[-1]-x[-2:mwlp1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    elif window=='robust':
        pass
#    elif window =='hanning':
 #      w=eval(np.hanning(
    else:
        w=eval(window+'(window_len)')

    if window=='robust':
        y=s.copy()
        for n in xrange(window_len-1,len(y)-window_len):
                y[n]=median(s[n-window_len/2:n+window_len/2+1])
    else:
        y=np.convolve(w/w.sum(),s,mode='same')
    returning = y[window_len-1:-window_len+1]
    if len(x) != len(returning):
	print "output array is not the same size as input:\tin:",len(x),'\tout:', len(returning)
	assert 0
    counts = np.arange(len(x))
    return np.ma.masked_where((counts<window_len/2.) + (counts>len(x)-window_len/2.) ,returning)




def movingaverage_DT(data,times, window_len=5.,window_units='years'):
	######
	#
	window_units = window_units.lower()
	if window_units not in ['days','months','years']:
     	   	raise ValueError("movingaverage_DT: window_units not recognised"+str(window_units))
	if len(data) !=len(times):
     	   	raise ValueError("movingaverage_DT: Data and times are different lengths.")
	data = np.ma.array(data)
	
	#####
	# Assuming time 
	if window_units in ['years',]:	window = float(window_len)/2.
	if window_units in ['months',]:	window = float(window_len)/(2.*12.)
	if window_units in ['days',]:	window = float(window_len)/(2.*365.25)
	output = np.ma.zeros(data.shape)
	for i,o in enumerate(output):
		t = times[i]
		av = np.ma.masked_where(((times < (t-window) ) + (times > (t+window) )), data).mean()
		output[i] = av
	return output
	
	

      
        
    
def multitimeseries(
		timesD, 		# model times (in floats)
		arrD,			# model time series
                datatimes = -999,       # in situ data times
		data = -999,		# in situ data
		datasource = '', 
		title 	='',
		filename='',
		units = '',
		colours = cmipcolours, #['red','orange','green','purple','blue','pink','yellow','lime',],
		plotStyle = 'Together',	
		lineStyle = '',
		dpi = 200,	
	):

        if 0 in [len(timesD) , len(timesD.keys())]:return

	if len(colours) < len(arrD.keys()):
		print colours, arrD.keys()
		raise ValueError("Not enough colours in "+str(colours)+'\n\t\tplease add '+str(len(arrD.keys())-len(colours))+' new colours')
        #####
        # is empty?
        emptydat=True
        for i,jobID in enumerate(sorted(timesD.keys())):
                if len(arrD[jobID]):emptydat=False
        if emptydat:
                print "No data for this figure:", plotStyle,timesD.keys(), title,filename
                return


        	
	fig = pyplot.figure()
	#fig.set_size_inches(10,6)
        #ig.set_size_inches(5,5)
        fig.set_size_inches(8,5)
		
	if plotStyle == 'Together':
		ax = fig.add_subplot(111)
	elif plotStyle == 'Separate':
		axs = []
		
	xlims = [1e20,-1e20]
	ylims = [1e20,-1e20]
	if type(colours) == type({'a':'dict',}):pass
	elif type(colours) == type(['a','list',]):
		#####
		# convert colour into a dict.
		tmpdict = {jobID, c in zip(sorted(timesD.keys()),colours )}
		colours = tmpdict
	else:	print "colours isn't working."


		
	for i,jobID in enumerate(sorted(timesD.keys())):
		times = timesD[jobID]
		arr = arrD[jobID]
		
		if plotStyle == 'Separate':
			if len(timesD.keys()) <= 4:	axs.append(fig.add_subplot(2,2,i+1))
			elif len(timesD.keys()) <= 6:	axs.append(fig.add_subplot(2,3,i+1))
			elif len(timesD.keys()) <= 9:	axs.append(fig.add_subplot(3,3,i+1))
			elif len(timesD.keys()) <= 12:	axs.append(fig.add_subplot(3,4,i+1))			
			else:
				print "Something is wrong here",i,plotStyle,len(timesD.keys()), jobID
			print "Separate plots",i,jobID, len(timesD.keys()), len(axs)
			axs[i].set_title(jobID)	
			
		
		if len(times) ==0 or len(arr) == 0:
			print "multitimeseries:\tWARNING:\tdata or time arrays are empty.",len(times),len(arr),title
			continue
		if np.ma.is_masked(arr):
			print "multitimeseries:\tWARNING:\tdata arrays is masked",len(times),len(arr),title
			continue
		if times[0]  < xlims[0]: 	xlims[0] = times[0]
		if times[-1] > xlims[1]: 	xlims[1] = times[-1]

		if np.min(arr) < ylims[0]: 	ylims[0] = np.min(arr)
		if np.max(arr) > ylims[1]: 	ylims[1] = np.max(arr)
		
					
		
		if lineStyle.lower() in ['spline','all']:
			tnew = np.linspace(times[0],times[-1],60)
			arr_smooth = interpolate.spline(times,arr,tnew)
			pyplot.plot(tnew,arr_smooth,c=colours[jobID],ls='-',label=jobID+' spline',)

		#if lineStyle.lower() in ['movingaverage','both','all']:
		#	if len(times)>100.: window = 30
		#	elif len(times)>30.: window = 15
		#	elif len(times)>10.: window = 4			
		#	else: window = 1
                #        arr_new = movingaverage2(arr, window_len=window,window='flat',extrapolate='periodically')
		#	pyplot.plot(times,arr_new,c=colours[jobID],ls='-',label=jobID,)#label=jobID+' smooth',)

		#if lineStyle.lower() in ['movingaverage5',]:
		#	window = 5
                #        arr_new = movingaverage2(arr,times, window_len=window,window='flat',extrapolate='periodically')
		#	pyplot.plot(times,arr_new,c=colours[jobID],ls='-',label=jobID,)#label=jobID+' smooth',)




		if lineStyle.lower() in ['movingav1year',]:
                        arr_new = movingaverage_DT(arr,times, window_len=1.,window_units='years')
			pyplot.plot(times,arr_new,c=colours[jobID],ls='-',label=jobID,)
		if lineStyle.lower() in ['movingav5years',]:
                        arr_new = movingaverage_DT(arr,times, window_len=5.,window_units='years')
			pyplot.plot(times,arr_new,c=colours[jobID],ls='-',label=jobID,)



		#if lineStyle.lower() in ['movingaverage12',]:
		#	window = 12
		#	if len(arr)>12:
 	        #        	arr_new = movingaverage2(arr, window_len=window,window='flat',extrapolate='periodically')
		#		pyplot.plot(times,arr_new,c=colours[jobID],ls='-',lw=2.,label=jobID,)#label=jobID+' smooth',)
				
		#if lineStyle.lower() in ['movingaverage60',]:
		#	window = 60
		#	if len(arr)>60:
 	         #       	arr_new = movingaverage2(arr, window_len=window,window='flat',extrapolate='periodically')
		#		pyplot.plot(times,arr_new,c=colours[jobID],ls='-',lw=2.,label=jobID,)#label=jobID+' smooth',)
													
		#if lineStyle.lower() in ['lowess','all','both',]:
		#	filtered = lowess(arr, times, is_sorted=True, frac=0.025, it=0)			
		#	pyplot.plot(filtered[:,0], filtered[:,1], colour[i],ls='-',label=jobID+' lowess',)
			
		if lineStyle.lower() in ['','both','all',]:
			pyplot.plot(times,arr,c=colours[jobID],ls='-',lw=0.25)#label=jobID,)

                if lineStyle.lower() in ['dataonly']:
                        pyplot.plot(times,arr,c=colours[jobID],ls='-',lw=0.75,label=jobID,)


	
	if data != -999:
		
		if datatimes in [-999, -999.]: # Data has no time comonent
	  	    try:
			data = [float(d) for d in data]
			if len(data) == 4:
			
				ax = drawgreyband(ax,xlims, [data[0],data[3]],label=datasource)
				ax = drawgreyband(ax,xlims, [data[1],data[2]],label=datasource)							
			if len(data) == 2:
				ax = drawgreyband(ax,xlims, data,label=datasource)				
			if len(data) == 1:
				pyplot.axhline(y=data[0],c='k',ls='-',lw=1,label = datasource)	
		    except TypeError:
			pyplot.axhline(y=data,c='k',ls='-',lw=1,label = datasource)
		else:	# Data have a time component
                        if len(data) == 2 and len(datatimes)==2:
			        ax.fill_between(datatimes,data[0], data[1],facecolor=(0.,0.,0.,0.05),edgecolor=(0.,0.,0.,1.), lw=1, label=datasource,zorder=100)
#                               ax = drawgreyband(ax,datatimes, data,label=datasource, edgecolor=(0.,0.,0.,1.), linewidth=1.,)
#				pyplot.show()
			else:
	                        data = np.array([float(d) for d in data])
                                datatimes = np.array([float(d) for d in datatimes])

				if len(data) > 5*12. :
			                if lineStyle.lower() in ['movingav1year',]:
        			                data_new = movingaverage_DT(data,datatimes, window_len=1.,window_units='years')
			                elif lineStyle.lower() in ['movingav5years',]:
                        			data_new = movingaverage_DT(data,datatimes, window_len=5.,window_units='years')
						print datatimes
						print data_new
						print len(datatimes),len(data_new)
#						assert 0
					else:	data_new = data

                                        pyplot.plot(datatimes,data_new,lw=1.5,c='k',label=datasource,zorder=100)
				else:	pyplot.plot(datatimes,data,lw=1,c='k',label=datasource)
					



	if plotStyle == 'Together':
		pyplot.title(title)
                pyplot.xlabel('Year')
		pyplot.ylabel(units)		
		pyplot.xlim(xlims)
		if len(timesD.keys()) < 5:
								
			try:	
				legend = pyplot.legend(loc='best',  numpoints = 1, ncol=len(timesD.keys())/2, prop={'size':12}) 
				legend.draw_frame(False) 
				legend.get_frame().set_alpha(0.)
			except:pass
		else:
			ax= drawLegendAlongside(ax, len(timesD.keys()),space=0.15)
		
	elif plotStyle == 'Separate':
		for ax in axs:
			ax.set_ylabel(units)
			ax.set_xlim(xlims)	
			ax.set_ylim(ylims)
		pyplot.suptitle(title)				

		
	print "multitimeseries:\tsimpletimeseries:\tSaving:" , filename
	pyplot.savefig(filename, dpi=dpi )
	pyplot.close()	
	


def regrid(data,lat,lon):
    	nX = np.arange(-179.5,180.5,0.25)
    	nY = np.arange( -89.5, 90.5,0.25)
    	if lat.ndim ==1:
    		oldLon, oldLat = np.meshgrid(lon,lat) 
    	else:
    		   oldLon, oldLat = lon,lat		
    	newLon, newLat = np.meshgrid(nX,nY)
    	
    	crojp1 = cartopy.crs.PlateCarree(central_longitude=0.0, ) #central_latitude=300.0)
    	crojp2 = cartopy.crs.PlateCarree(central_longitude=0.0, ) #central_latitude=300.0)

    	a = cartopy.img_transform.regrid(data,
    			     source_x_coords=oldLon,
                             source_y_coords=oldLat,
                             source_cs=crojp1,
                             target_proj=crojp2,
                             target_x_points=newLon,
                             target_y_points=newLat
                             )
       # print 'newregid shape:',a.shape                     
	return crojp2, a, newLon,newLat
	
	
	
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
		data = np.ma.masked_less_equal(ma.array(data), 0.)
	
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
	
def mapPlotSingle(lons1, lats1, data1,filename,titles=['',],lon0=0.,drawCbar=True,cbarlabel='',doLog=False,dpi=100,cmap = defcmap):#**kwargs):
	"""
	Makes a single pane map plot (ie, when there is no observartional data)
	"""
	fig = pyplot.figure()
	fig.set_size_inches(10,6)
	
	lons1 = np.array(lons1)
	lats1 = np.array(lats1)
	data1 = np.ma.array(data1)
	
	rbmi = data1.min()
	rbma = data1.max()
	
	if rbmi * rbma >0. and rbma/rbmi > 100.: doLog=True
	ax1 = pyplot.subplot(111,projection=cartopy.crs.PlateCarree(central_longitude=0.0, ))
		
	fig,ax1,im = makemapplot(fig,ax1,lons1,lats1,data1,titles[0], zrange=[rbmi,rbma],lon0=0.,drawCbar=True,cbarlabel='',doLog=doLog,cmap = cmap)
	ax1.set_extent([-180.,180.,-90.,90.])
	print "mapPlotSingle.py:\tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()
	

def mapPlotPair(lons1, lats1, data1,lons2,lats2,data2,filename,titles=['',''],lon0=0.,drawCbar=True,cbarlabel='',doLog=False,dpi=100,cmap = defcmap):#**kwargs):
	"""
	Makes a pair of plots - model top, observational data below.	
	If no obs data remain, it sends it to singlePlot tool
	"""

	lons1 = np.array(lons1)
	lats1 = np.array(lats1)
	data1 = np.ma.array(data1)
		
	lons2 = np.array(lons2)
	lats2 = np.array(lats2)
	data2 = np.ma.array(data2)
	
	rbmi = min([data1.min(),data2.min()])
	rbma = max([data1.max(),data2.max()])		
	
			
	bins = 15
	if defcmapstr =='viridis':
		cmap1 = discrete_viridis(bins)
	else:	cmap1 = pyplot.cm.get_cmap(defcmap, bins)    
	
	if rbmi * rbma >0. and rbma/rbmi > 100.: doLog=True
	if 0 in [len(data2.compressed()),len(np.ma.array(lons2).compressed()),len(np.ma.array(lats2).compressed()), ]:
 		try:    mapPlotSingle(lons1, lats1, data1,filename,titles=titles,lon0=lon0,drawCbar=drawCbar,cbarlabel=cbarlabel,doLog=doLog,dpi=dpi,cmap = cmap1)
 		except:pass
 		return

	if 0 in [len(data1.compressed()),len(data2.compressed()),len(np.ma.array(lons1).compressed()),len(np.ma.array(lats1).compressed()),]:
		return


        mask1 = data1.mask
	mlons1 = np.ma.masked_where(data1.mask,lons1)        
	mlats1 = np.ma.masked_where(data1.mask,lats1)

        mask2 = data2.mask
	mlons2 = np.ma.masked_where(data2.mask,lons2)        
	mlats2 = np.ma.masked_where(data2.mask,lats2)

        lami = min([mlats1.min(),mlats2.min()])
        lama = max([mlats1.max(),mlats2.max()])
        lomi = min([mlons1.min(),mlons2.min()])
        loma = max([mlons1.max(),mlons2.max()])
	


	plotShape = 'Global'	# default
	larange = float(lama-lami)
        lorange = float(loma-lomi)
	print "Lat range:",lami,lama,(larange)
        print "Lon range:",lomi,loma,(lorange)

	if larange < 40.  and lorange > 180.: 
		plotShape = 'longthin'
		
	if larange >120. and lorange < 25.: 
		plotShape = 'tallthin'		
        print "plot shape:", plotShape
	
        fig = pyplot.figure()
	sharedCbar = True
	if sharedCbar: 
	        if plotShape == 'Global':
	                fig.set_size_inches(8,8)
        	        width_ratio = [15, 1]
	                gs = gridspec.GridSpec(2, 2,  width_ratios=[15,1] )
			gs_ax1 = gs[0]
                        gs_ax2 = gs[2]
                        gs_cb  = gs[:,1]
                        cb_Orientation='vertical'

	        if plotShape == 'longthin':
	                fig.set_size_inches(8,5)
			gs = gridspec.GridSpec(3, 1, height_ratios=[10,10, 1], )
                        gs_ax1 = gs[0]
                        gs_ax2 = gs[1]
                        gs_cb  = gs[2]
			cb_Orientation='horizontal'

	        if plotShape == 'tallthin':
        	        fig.set_size_inches(5,8)
                        gs = gridspec.GridSpec(1, 3, width_ratios=[10,10, 1], )
                        gs_ax1 = gs[0]
                        gs_ax2 = gs[1]
                        gs_cb  = gs[2]
                        cb_Orientation='vertical'
			ytitles = titles[:]	# put titles on y axis instead of above
			titles = ['','']

		drawCbar = False
		ax1 = pyplot.subplot(gs_ax1,projection=cartopy.crs.PlateCarree(central_longitude=0.0, ))
	else:
		ax1 = pyplot.subplot(211,projection=cartopy.crs.PlateCarree(central_longitude=0.0, ))
		ax2 = pyplot.subplot(212,projection=cartopy.crs.PlateCarree(central_longitude=0.0, ))	
	#try:
		#####
		# Draw second plot first, as ax1 can be made by itself if this fails.
	#	fig,ax2,im2 = makemapplot(fig,ax2,lons2,lats2,data2,titles[1], zrange=[rbmi,rbma],lon0=0.,drawCbar=drawCbar,cbarlabel='',doLog=doLog,cmap = cmap1)
	#	if False in [fig, ax2]: assert False
	#	ax2.set_extent([-180.,180.,-90.,90.])		
	#except: 
	#	try:mapPlotSingle(lons1, lats1, data1,filename,titles=titles,lon0=lon0,drawCbar=True,cbarlabel=cbarlabel,doLog=doLog,dpi=dpi,cmap = cmap1)
	#	except:pass
	#	return
	
	fig,ax1,im1 = makemapplot(fig,ax1,lons1,lats1,data1,titles[0], zrange=[rbmi,rbma],lon0=0.,drawCbar=drawCbar,cbarlabel='',doLog=doLog,cmap = cmap1)
        if plotShape == 'tallthin':  
		#ax1.set_ylabel(ytitles[0])
		ax1.set_title(ytitles[0],x=-1.5,y=0.5,
			rotation='vertical',
			horizontalalignment='left',
			verticalalignment='center',)
		#ax1.update()
#	ax1.set_extent([-180.,180.,-90.,90.])	

        if sharedCbar: 
		ax2 = pyplot.subplot(gs_ax2, projection=cartopy.crs.PlateCarree(central_longitude=0.0, ))
        fig,ax2,im2 = makemapplot(fig,ax2,lons2,lats2,data2,titles[1], zrange=[rbmi,rbma],lon0=0.,drawCbar=drawCbar,cbarlabel='',doLog=doLog,cmap = cmap1)
#        ax2.set_extent([-180.,180.,-90.,90.])

        if plotShape == 'tallthin':
                #x2.set_ylabel(ytitles[1])
                ax2.set_title(ytitles[1],x=-1.5,y=0.5,
			rotation='vertical', 
			horizontalalignment='left',
			verticalalignment='center',)

		#ax2.update()
	if sharedCbar:
	        axcb = pyplot.subplot(gs_cb)
		cb = pyplot.colorbar(im1,cax=axcb,orientation=cb_Orientation)
		cb.set_label(cbarlabel)		
		
	print "mapPlotPair: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()	


#def calculateExtent(lat1,lat2,lon1,lon2):
#        latmin = -90. 
#	latmax =  90.
#        lonmin = -180.
#	lonmax =  180.
#	
#	latmin = min([lat1.min(), lat2.min()])
#        latmax = max([lat1.max(), lat2.max()])
#	
#	latboard = (latmax - latmin)/10.
	


	
	
	
def hovmoellerAxis(fig,ax,title,xaxis,yaxis,data,vmin='',vmax='',cmap = defcmap ,debug = False):
	yaxis = np.array(yaxis)
	if yaxis.min()*yaxis.max() <=0.:
		if yaxis.mean()<0:yaxis = np.clip(yaxis,-10000.,-0.001)
	
	if debug:	print "hovmoellerAxis:\txaxis:",title, xaxis,"\tyaxis:",yaxis,"\tdata:",data
	if debug:	print "hovmoellerAxis:\txaxis:",title, xaxis.shape,"\tyaxis:",yaxis.shape,"\tdata:",data.shape
	
	
	if vmin==vmax=='':	p=pyplot.pcolormesh(xaxis,yaxis,data,cmap = cmap)
	else:			p=pyplot.pcolormesh(xaxis,yaxis,data,vmin=vmin,vmax=vmax,cmap = cmap)
	pyplot.title(title)
	#ax.set_yscale("log", nonposy='clip')
	ax.set_yscale('symlog')
	
def zaxisfromCC(arr):
	"""
		This function creates a 1D array for the depth axis.
		It assumes that the z axis given is cell centered (cc) depth, it adds a zero to the start
		and takes the mid point between the cc depths.
		It then converts the array into negative values.
	"""
	arr = np.array(arr)
	zarr = list((arr[1:]+arr[:-1])/2.)
	zarr.insert(0,0.)
	zarr.append(arr[-1])	
	#print arr,zarr
	return -1.*np.abs(np.array(zarr))
		
def taxisfromCC(arr):
	"""
		This function creates a 1D array for the time axis.
		It assumes that the x axis given is cell centered (cc), 
		it adds a starting time to the start and takes the mid point between the cc depths.
		It then converts the array into negative values.
	"""
	arr = np.array(arr)
	diff = np.mean(np.abs(arr[1:]-arr[:-1]))/2.
	zarr = list((arr[1:]+arr[:-1])/2.)
	zarr.insert(0,arr[0]-diff)
	zarr.append(arr[-1]+diff)	
	#print arr,zarr
	return np.array(zarr)
	

def hovmoellerPlot(modeldata,dataslice,filename, modelZcoords = {}, dataZcoords= {}, title = '',zaxislabel = '',dpi=100,diff=True):	
	#####
	# creating model data dictionairies
	md = []
	times_cc = []
	yaxis_cc = []
	
	for l in sorted(modelZcoords.keys()):
		if l not in modeldata.keys():continue
		yaxis_cc.append(modelZcoords[l])

		times_cc = sorted(modeldata[l].keys())
		try:	md.append(np.array([modeldata[l][t][0] for t in times_cc]))
		except:	md.append(np.array([modeldata[l][t] for t in times_cc]))
		
	md = np.ma.array(md)#
	md = md.squeeze()
	md = np.ma.masked_where(np.ma.masked_invalid(md).mask + md.mask, md)
	times = taxisfromCC(np.array(times_cc))
	yaxis = zaxisfromCC(yaxis_cc)
	print "hovmoellerPlot model:", title, md.shape,md.mean(),times.shape,yaxis.shape #, times, yaxis
	if len(md.shape)==1 or 1 in md.shape:
		print "Not enough model data dimensions:",md.shape
		return
		
	#####
	# creating data data dictionairies
	dd = []
	dxaxis= []
	dyaxis_cc = []
	
	for l in sorted(dataZcoords.keys()):
		if l not in dataslice.keys():continue
		dyaxis_cc.append(dataZcoords[l])
		#print 'hovmoellerPlot:\tpreparing data for hov:',l,dataZcoords[l], dataslice[l]
		dd.append(dataslice[l])
	if len(dd):
		dd = np.ma.array(dd)#.squeeze()
		print "hovmoellerPlot data: (pre-mask)", title, '\t',dd.shape,dd.min(),dd.mean(),dd.max()
		dd = np.ma.masked_where(np.ma.masked_invalid(dd).mask + dd.mask, dd)	
		print "hovmoellerPlot data: (post-mask)", title, '\t',dd.shape,dd.min(),dd.mean(),dd.max()
		dyaxis_cc = np.array(dyaxis_cc)
	else:
		dd = np.ma.array([-999,],mask=True)
		dyaxis_cc = np.ma.array([-999,],mask=True)	
		
	#####
	# A hack to defuse an unusal bug that occurs when all layers of the data set are masked.
	while len(dd.shape)> 2:
		if dd.shape[-1] == 1:
			dd = dd[:,:,0]
		if len(dd.shape) >2 and dd.shape[-1] !=1: 
			print "Something very strange is happenning with this array:", dd
			assert False

	dxaxis = np.array([0,1,])
	dyaxis = zaxisfromCC(dyaxis_cc)
	print "hovmoellerPlot: - data:", title, dd.shape,dd.mean(),dxaxis.shape,dyaxis.shape
	
 	if len(dd.squeeze().compressed())==0 and diff: 
		print "hovmoellerPlot:\tWARNNG: Data entire masked, can not take difference of entirely masked data."
		return
	
	
	######
	# Locate min/max colours
	rbmi = min([md.min(),dd.min(),])
	rbma = max([md.max(),dd.max(),])
	
	######
	# Locate min/max depths
	zmi = min([dyaxis.min(),yaxis.min(),])
	zma = max([dyaxis.max(),yaxis.max(),])	
	
	
	bins = 15
	if defcmapstr =='viridis':
		cmapax1 = discrete_viridis(bins)
	else:	cmapax1 = pyplot.cm.get_cmap(defcmap, bins)    

	if diff:
		#####
		# diff:
		# If the diff key is true, this subtracts the data from the model, it also changes the colour scheme.
		
		if len(dd.squeeze().compressed())==0:
			print "hovmoellerPlot:\tWARNNG: Data entire masked, can not take difference of entirely masked data."
			return
		# First step is to perform the interpollartion.		
		f = interpolate.interp1d(dyaxis_cc, dd.squeeze(), kind='linear')
		newData = f(np.ma.clip(yaxis_cc,dyaxis_cc.min(),dyaxis_cc.max()))	

		###
		# subtract data from model:		
		for i,t in enumerate(times_cc):
			
			md[:,i] = md[:,i] -  newData
	
		####
		# change plot ranges, title, colorscale
		ax2max = max([abs(md.max()),abs(md.min()),])
		ax2min = - ax2max
		#cmapax2 = pyplot.cm.bwr
		cmapax2 = pyplot.cm.get_cmap('RdBu_r', bins)    
		#pyplot.cm.RdBu_r	
		title = 'Model - Data: '+title		
	else:
		ax2max	= rbma
		ax2min	= rbmi
		if defcmapstr =='viridis':
			cmapax2 = discrete_viridis(bins)
		else:	cmapax2 = pyplot.cm.get_cmap(defcmap, bins) 
		title = title
	#####
	# Start drawing
	# Grid spec allows you to make un-even shaped subplots.
	# here we want the in situ data to be much narrower.
	fig = pyplot.figure()	
	#fig.set_size_inches(10,6)
	fig.set_size_inches(8,4)
	if diff:
		#####
		# model - data plot
		ax2 = pyplot.subplot(111)
		hovmoellerAxis(fig,ax2,title,times,yaxis,md,vmin=ax2min,vmax=ax2max,cmap = cmapax2)
		pyplot.xlim([times.min(),times.max()])
		pyplot.ylim([zmi,zma])	
		ax2.set_yscale('symlog')	
		#pyplot.xlabel('Year')			
		pyplot.ylabel('Depth, m')
		
		divider = make_axes_locatable(ax2)
		cax = divider.append_axes("right", size="5%", pad=0.15)	
		cb = pyplot.colorbar(cax=cax)
		cb.set_label(zaxislabel)
		


	else:
		#gs = gridspec.GridSpec(1, 2, width_ratios=[12, 1]) 
#                gs = gridspec.GridSpec(1, 2, width_ratios=[10,1], wspace=0.01, hspace=0.)
        	gs = gridspec.GridSpec(1, 2, width_ratios=[9,1], wspace=0.005, hspace=0.0)

		#####
		# model subplot
		ax1 = pyplot.subplot(gs[0])
		hovmoellerAxis(fig,ax1,title,times,yaxis,md,vmin=ax2min,vmax=ax2max,cmap = cmapax2)
		pyplot.xlim([times.min(),times.max()])
		pyplot.ylim([zmi,zma])	

		ax1.set_yscale('symlog')	
		#ax1.yaxis.set_ticklabels([])
		#pyplot.xlabel('Year')
		pyplot.ylabel('Depth, m') 	 	
		pyplot.ylim([zmi,zma])
		
		#####
		# Data  subplot
		ax2 = pyplot.subplot(gs[1])
		if len(dd.squeeze().compressed())!=0:
			try:	hovmoellerAxis(fig,ax2,'',dxaxis,dyaxis,dd,vmin=rbmi,vmax=rbma , cmap = cmapax1)
			except:	
				hovmoellerAxis(fig,ax2,'',dxaxis,dyaxis,np.tile(dd,[2,1]).transpose(),vmin=rbmi,vmax=rbma,cmap = cmapax1)
		pyplot.ylim([zmi,zma])	
		ax2.set_yscale('symlog')	
		ax2.get_xaxis().set_ticks([])
		ax2.get_yaxis().set_ticks([])
		
		divider = make_axes_locatable(ax2)
		cax = divider.append_axes("right", size="50%", pad=0.15)								
		cb = pyplot.colorbar(cax=cax)
		cb.set_label(zaxislabel)	
	
		ax2.text(0.7,1.0450,'Data',
			va='top',ha='center',
			transform=ax2.transAxes)

		ax1.text(1.,1.050,'Model  ',
			va='top',ha='right',
			transform=ax1.transAxes)
		
	#pyplot.tight_layout()			
	print "hovmoellerPlot.py: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()	
	




def profilePlot(modeldata,dataslice,filename, modelZcoords = {}, dataZcoords= {}, title = '',xaxislabel = '',dpi=100,):	
	#####
	# creating model data dictionairies
	md = []
	times_cc = []
	yaxis_cc = []
	
	for l in sorted(modelZcoords.keys()):
		if l not in modeldata.keys():continue
		yaxis_cc.append(modelZcoords[l])

		times_cc = sorted(modeldata[l].keys())
		try:	md.append(np.array([modeldata[l][t][0] for t in times_cc]))
		except:	md.append(np.array([modeldata[l][t] for t in times_cc]))
		
	md = np.ma.array(md)#
	md = md.squeeze()
	md = np.ma.masked_where(np.ma.masked_invalid(md).mask + md.mask, md)
	yaxis_cc = np.abs(np.array(yaxis_cc))*-1.
	#times = taxisfromCC(np.array(times_cc))
	#yaxis = zaxisfromCC(yaxis_cc)
	#print "profilePlot model:", title, md.shape,md.mean(),times.shape,yaxis.shape #, times, yaxis
	if len(md.shape)==1 or 1 in md.shape:
		print "Not enough model data dimensions:",md.shape
		return
		
	#####
	# creating data data dictionairies
	dd = []
	#dxaxis= []
	dyaxis_cc = []
	
	for l in sorted(dataZcoords.keys()):
		if l not in dataslice.keys():continue
		dyaxis_cc.append(dataZcoords[l])
		#print 'preparing data for hov:',l,dataZcoords[l], dataslice[l]
		dd.append(dataslice[l])
	
	if len(dd):
		dd = np.ma.array(dd)#.squeeze()
		print "profilePlot data: (pre-mask)", title, '\t',dd.shape,dd.min(),dd.mean(),dd.max()
		dd = np.ma.masked_where(np.ma.masked_invalid(dd).mask + dd.mask, dd)	
		print "profilePlot data: (post-mask)", title, '\t',dd.shape,dd.min(),dd.mean(),dd.max()
		dyaxis_cc = np.abs(np.array(dyaxis_cc))*-1.
	else:
		dd = np.ma.array([-999,],mask=[True,])
		dyaxis_cc = np.ma.array([-999,],mask=[True,])	

	######
	# Locate min/max colours
	rbmi = np.ma.min([md.min(),dd.min(),])
	rbma = np.max([md.max(),dd.max(),])
	
	######
	# Locate min/max depths
	zmi = np.ma.min([dyaxis_cc.min(),yaxis_cc.min(),])
	zma = np.ma.max([dyaxis_cc.max(),yaxis_cc.max(),])	
	zma = np.ma.min([-9.,zma]) 	# set shallowest depth to 9m
	

	#####
	# Start drawing
	# Grid spec allows you to make un-even shaped subplots.
	# here we want the in situ data to be much narrower.
	fig = pyplot.figure()	
	#fig.set_size_inches(8,6)
        fig.set_size_inches(6,5)


	#####
	# Data  subplot
	
	ax1 = pyplot.subplot(111)

	#####
	# Choose which years tp plot:	
	profileTimes = {}
	firstyr = sorted(times_cc)[0]
	lastyr = len(times_cc) -1
	if   lastyr<10:	plotEvery = 1
	elif lastyr<25:	plotEvery = 2
	elif lastyr<50:	plotEvery = 5	
	elif lastyr<100:plotEvery = 10		
	elif lastyr<500:plotEvery = 20			
	else:		plotEvery = 50
	
	for i,t in enumerate(times_cc):
		if i == 0: 		profileTimes[i] = t	# First year
		if i == lastyr: 	profileTimes[i] = t	# Last year		
		if int(t)%plotEvery==0:  	profileTimes[i] = t	# Every 50 years
		
	####
	# Add model data
	plotDetails = {}
	jetmap = pyplot.cm.jet
	for i in sorted(profileTimes.keys()):
		print 'profilePlot',i,profileTimes[i], md[:,i].shape,yaxis_cc.shape
		lw =1
		if i == lastyr: 	lw =2
		color = jetmap((float(profileTimes[i])-times_cc[0])/(float(times_cc[-1]-times_cc[0])))
		label = str(int(profileTimes[i]))
		plotDetails[i] = {'c': color, 'label':label, 'lw':lw,}
		pyplot.plot(md[:,i], yaxis_cc, c=color, lw = lw, )#label=label)

	pyplot.xlabel(xaxislabel)
	pyplot.ylabel('Depth')
	pyplot.title(title)
	print 'x',rbmi,'->',rbma, 'z:',zmi,'->',zma

	#ax1.set_yscale('log')	# Doesn't like negative values

	
	#####
	ticks = []
	for i in [10,100,1000,]: ticks.extend(np.arange(1,10)*i)
	ticks = np.array(ticks)*-1.
	ticks = ticks[ticks>zmi]
	ticks = ticks[ticks<zma]
	ax1.set_yscale('symlog',linthreshy=np.abs(ticks.max()))
	pyplot.ylim([zmi,zma])	
	ax1.set_yticks(ticks)

	#####
	# Add data:
	if len(dd.squeeze().compressed())!=0:
		print "Adding data profile."	
		pyplot.plot(dd, dyaxis_cc, 'k', lw=2, )#label='Data')

	#####
	# Add legend:
	legendSize = len(plotDetails.keys())+1
	ncols = int(legendSize/25)+1
	box = ax1.get_position()
	ax1.set_position([box.x0,
			  box.y0 ,
			  box.width*(1.-0.1*ncols), 
			  box.height ])
	
	if len(dd.squeeze().compressed())!=0 :
		
		pyplot.plot([], [], 'k', lw=2, label='Data')

	for i in sorted(plotDetails.keys()):
		pyplot.plot([], [], c=plotDetails[i]['c'], lw = plotDetails[i]['lw'], label=plotDetails[i]['label'])
	
												
	legd = ax1.legend(loc='center left', ncol=ncols,prop={'size':10},bbox_to_anchor=(1., 0.5))
	legd.draw_frame(False) 
	legd.get_frame().set_alpha(0.)	
		
	#legend = pyplot.legend(loc='best',  numpoints = 1, ncol=2, prop={'size':10}) 
	#legend.draw_frame(False) 
	#legend.get_frame().set_alpha(0.)
					
	
	#pyplot.tight_layout()			
	print "profilePlot.py: \tSaving:" , filename
	pyplot.savefig(filename ,dpi=dpi)		
	pyplot.close()	
	
		
			

