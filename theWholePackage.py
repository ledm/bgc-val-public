#!/usr/bin/ipython 
#####
#

"""
	In this code, we run the whole package analysis suite.
	
"""
from sys import argv,exit
from multiprocessing import Pool

from downloadFromMass import  downloadMass, findLastFinishedYear
from analysis_timeseries import analysis_timeseries, singleTimeSeries, singleTimeSeriesProfile
from analysis_timeseries import level1KeysDict, timeseriesDict
from analysis_p2p import analysis_p2p, p2pDict_annual, single_p2p
from makeReport import html5Maker
from UKESMpython import folder


def timeseriesParrallel(index):
	print "timeseriesParrallel",index, jobID, 'START'
	key = timeseriesDict[index]
	singleTimeSeries(jobID, key,)
	print "timeseriesParrallel",index, jobID, 'SUCESS'	
	
def timeseriesParrallelL1(index):
	print "timeseriesParrallel",index, jobID, 'START'
	key = level1KeysDict[index]
	singleTimeSeries(jobID, key,)
	print "timeseriesParrallel",index, jobID, 'SUCESS'	

def p2pParrallel(index):
	print "p2pParrallel",index, jobID, 'START'
	key = p2pDict_annual[index]
	single_p2p(jobID, key, year)
	print "p2pParrallel",index, jobID, 'SUCESS'
	



def theWholePackage(jobID):
	print "########\nThe Whole Package:\tStarting job", jobID , year
#	downloadMass(jobID)

	parrallel = True
	cores = 8
	#suite = 'all'
	suite = 'level1'
			  

	print "########\nThe Whole Package:\tStarting Time series (surface only)", jobID 	
	if parrallel:
		if suite =='all':	remaining = sorted(timeseriesDict.keys())[:]
		if suite =='level1':	remaining = sorted(level1KeysDict.keys())[:]
			
	   	p = Pool(cores)
	    	if suite =='all':	p.map(timeseriesParrallel,  remaining)
	    	if suite =='level1':	p.map(timeseriesParrallelL1,remaining)
	else:	
		analysis_timeseries(jobID =jobID,analysisSuite='level1', )#z_component = 'SurfaceOnly',)
		
		
	print "########\nThe Whole Package:\tRunning point to point analysis of", jobID,"on", year
	if parrallel:
		remaining = sorted(p2pDict_annual.keys())[:]
	   	p1 = Pool(cores)
	    	p1.map(p2pParrallel,remaining)	

		#####
		# And once over to make the summary target diagrams.
		analysis_p2p(models	= ['NEMO','MEDUSA',],
			jobID 	= jobID,
			years 	= [year,], #'2075','2076',
			modelGrid = 'eORCA1',
			annual 	= True,
			noPlots = True,
			analysisSuite='annual',)  
				    	
	else:	
		analysis_p2p(models	= ['NEMO','MEDUSA',],
			jobID 	= jobID,
			years 	= [year,], #'2075','2076',
			modelGrid = 'eORCA1',
			annual 	= True,
			noPlots = False,
			analysisSuite='annual',)        


	


	print "########\nThe Whole Package:\tmaking Summary report"	
	html5Maker(jobID =jobID,
		   reportdir=folder('reports/'+jobID),
		   year = year,
		   clean=True,
		   )





if __name__=="__main__":	

	try:	jobID = argv[1]
	except:	
		print "Please provide a job ID"
		exit()
        year = findLastFinishedYear(jobID)		
	theWholePackage(jobID)
		