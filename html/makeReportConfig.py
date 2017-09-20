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
"""
.. module:: makeReport
   :platform: Unix
   :synopsis: A script to produce an html document summarising a jobs performance.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

#####	
# Load Standard Python modules:
from glob import glob
from sys import argv
import os 
import shutil
from itertools import product

#####	
# Load specific local code:
from bgcvaltools import bgcvalpython as bvp
from html import htmlTools, htmltables
from longnames.longnames import getLongName

from bgcvaltools.configparser import AnalysisKeyParser, GlobalSectionParser

package_directory = os.path.dirname(os.path.abspath(__file__))

#####
# Quick tools to make a list into a string
def titleify(ls):	return ' '.join([ getLongName(i) for i in ls]) 
def hrefify(ls):	return '-'.join(ls) 
def wildcardify(ls):	return '*'.join(ls) 



def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            try:shutil.copytree(s, d, symlinks, ignore)
            except:pass
        else:
            try:shutil.copy2(s, d)
            except: pass
            
def addImageToHtml(fn,imagesfold,reportdir,debug=True):
	#####
	# Note that we use three paths here.
	# fn: The original file path relative to here
	# newfn: The location of the new copy of the file relative to here
	# relfn: The location of the new copy relative to the index.html
	
	newfn = imagesfold+os.path.basename(fn)
	relfn = newfn.replace(reportdir,'./')	
		
	if not os.path.exists(newfn):
		if debug: print "cp",fn, newfn
		shutil.copy2(fn, newfn)
	else:
		####
		# Check if the newer file is the same one from images.
		if os.path.getmtime(fn) == os.path.getmtime(newfn): return relfn
		####
		# Check if file is newer than the one in images.		
		if bvp.shouldIMakeFile(fn, newfn,):
			if debug: print "removing old file",fn
			os.remove(newfn)
			shutil.copy2(fn, newfn)			
			if debug: print "cp",fn, newfn
	return relfn

def isSingle(ls): 
	if len(ls)==1: return True
	return False            

def removeDuplicates(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]
	
def fnToTitle(fn,ignores= []):
	"""	This script takes a filename and returned a usable description of the plot title.
	"""
	titlelist=  os.path.basename(fn).replace('.png', '').replace('_',' ').split(' ')
	
	titlelist = removeDuplicates(titlelist)
	
	IgnoreList = ['percentiles', 'BGCVal', '','10-90pc','5-95pc','sum','Sum',]
	
	title = []
	for i,t in enumerate(titlelist):
		# remove redundent versus field
		if t.find('vs')>-1:	continue
		if t in IgnoreList:	continue
		if t in ignores:	continue
		ln = getLongName(t)
		if ln in IgnoreList:continue
		title.append(ln)
	return 	titleify(title)
		
		

def addSections(
		akp,
		indexhtmlfn,
		imagesfold,
		reportdir,
		key):
	
	raise  AssertionError("addSections:\tthis function is deprecated.") 
	
	#####
	# href is the name used for the html 
	SectionTitle= ' '.join([ getLongName(key), akp.model, akp.jobID, akp.scenario,akp.year,]) #getLongName(key)
	hrefs 	= []
	Titles	= {}
	SidebarTitles = {}
	Descriptions= {}
	FileLists	= {}

	for region in akp.regions:
	    for layer in akp.layers:
		href = 	key+'-'+region+'-'+layer
		hrefs.append(href)
		
		#####
		# Title is the main header, SidebarTitles is the side bar title.
		Titles[href] 		= ' '.join([akp.model, akp.jobID, akp.scenario, akp.year, getLongName(region), getLongName(layer), getLongName(key)])
		SidebarTitles[href] 	= ' '.join([akp.jobID, getLongName(region), getLongName(layer)])
							
		#####
		# Descriptions is a small sub-header
		desc = ''
		Descriptions[href] = desc
		
		#####
		# A list of files to put in this group.
		FileLists[href] = {}
		#####
		# Determine the list of files:
		vfiles = []
		
		if akp.makeTS:	
			files = {}
			#for layer in akp.layers:		
			files.update({f:1 for f in glob(akp.images_ts +'/*'+region+'*'+layer+'*.png')})
			files.update({f:1 for f in glob(akp.images_ts +'/*'+layer+'*'+region+'*.png')})
			vfiles.extend(sorted(files.keys()))

		if akp.makeProfiles:	
			files = {}
			files.update({f:1 for f in glob(akp.images_pro +'/*'+region+'*.png')})
			vfiles.extend(sorted(files.keys()))
						
		if akp.makeP2P:
			files = {}
			#for layer in akp.layers:		
			files.update({f:1 for f in glob(akp.images_p2p +'/*'+region+'*'+layer+'*.png')})
			files.update({f:1 for f in glob(akp.images_p2p +'/*'+layer+'*'+region+'*.png')})
			vfiles.extend(sorted(files.keys()))
					
		#####
		# Create plot headers for each file.
		for fn in vfiles:
			#####
			# Copy image to image folder and return relative path.
			relfn = addImageToHtml(fn, imagesfold, reportdir)
		
			#####
			# Create custom title by removing extra bits.
			FileLists[href][relfn] = fnToTitle(relfn) 
			print "Adding ",relfn,"to script"
						
	htmlTools.AddSubSections(indexhtmlfn,
			hrefs,
			SectionTitle,
			SidebarTitles=SidebarTitles,#
			Titles=Titles, 
			Descriptions=Descriptions,
			FileLists=FileLists)

	
#####
# Assumes multiple jobIDs and only one model and scenario.
def addComparisonSection(
		globalkeys,
		indexhtmlfn,
		imagesfold,
		reportdir,
		model='',
		scenario='',
		):

	jobIDs = globalkeys.jobIDs
	#####
	# href is the name used for the html 
	SectionTitle= titleify([model, scenario]) 
	hrefs 		= []
	Titles		= {}
	SidebarTitles 	= {}
	Descriptions	= {}
	FileLists	= {}
	filecount	= 0
	for key in globalkeys.ActiveKeys:
	
		href = 	hrefify(['Comparison', key, model, scenario])
		hrefs.append(href)
	
		#####
		# Title is the main header, SidebarTitles is the side bar title.
		Titles[href] 		= titleify([ key, ])
		SidebarTitles[href] 	= titleify([ key, ])
						
		#####
		# Descriptions is a small sub-header
		desc = ''
		Descriptions[href] = titleify(['Comparison of the time developement of the', model,
					'models', key, 
					'in the scenario',scenario, 
					'for the jobs: ',' '.join(jobIDs)])


		#####
		# A list of files to put in this group.
		FileLists[href] = {}
	
		#####
		# Determine the list of files:
		vfiles = []	
		

		filecheck = globalkeys.images_comp +'/' +wildcardify([model, scenario, key])+'*.png'
		files = {f:1 for f in glob(filecheck)}
		vfiles.extend(sorted(files.keys()))

			
		#####
		# Create plot headers for each file.
		ignoreList = [model,scenario,]		
		for fn in vfiles:
			#####
			# Copy image to image folder and return relative path.
			relfn = addImageToHtml(fn, imagesfold, reportdir)
	
			FileLists[href][relfn] = fnToTitle(relfn,ignores=ignoreList) 
			print "Adding ",relfn,"to script"
		filecount+=len(vfiles)			
	if filecount==0:return			
				
	htmlTools.AddSubSections(indexhtmlfn,
			hrefs,
			SectionTitle,
			SidebarTitles=SidebarTitles,#
			Titles=Titles, 
			Descriptions=Descriptions,
			FileLists=FileLists)
			

def addTimeSeriesSection(
		akp,
		indexhtmlfn,
		imagesfold,
		reportdir,
		debug=False
		):
	if not akp.makeTS: return
	
	key 	= akp.key
	model 	= akp.model
	scenario = akp.scenario
	jobID 	= akp.jobID
	
	#####
	# href is the name used for the html 
	SectionTitle	= titleify([jobID,key ,'time series',]) 		
	hrefs 		= []
	Titles		= {}
	SidebarTitles 	= {}
	Descriptions	= {}
	FileLists	= {}
	filecount	= 0
	
	for region in akp.regions:
	    for layer in akp.layers:
		href = 	hrefify([key, region,layer, 'ts',model,scenario,jobID])
		hrefs.append(href)
		
		#####
		# Title is the main header, SidebarTitles is the side bar title.
		Titles[href] 		= titleify(['Time series of ', key,'in',jobID])
		SidebarTitles[href] 	= titleify([region, layer])
							
		#####
		# Descriptions is a small sub-header

		desc = ['Timeseries of the', model, 'model\'s',key, ]
		if len(akp.datasource):	desc += ['against',akp.datasource,'data',]
		desc += ['for the job', jobID, 
			'under the',scenario,'scenario', 
			'in the', region, 'region',
			'at',  layer+'.']
		Descriptions[href] =  titleify(desc)
			
		#####
		# A list of files to put in this group.
		FileLists[href] = {}
		
		#####
		# Determine the list of files:
		vfiles = []
		files = {}
		filecheck = akp.images_ts +'/' +wildcardify([model, scenario,jobID, key,region,layer,])+'*.png'		
		#files.update({f:1 for f in glob(akp.images_ts +'/*'+region+'*'+layer+'*.png')})
		#files.update({f:1 for f in glob(akp.images_ts +'/*'+layer+'*'+region+'*.png')})
		files = {f:1 for f in glob(filecheck)}
		vfiles.extend(sorted(files.keys()))
					
		#####
		# Create plot headers for each file.
		ignoreList = [model,scenario,jobID,]		
		for fn in vfiles:
			#####
			# Copy image to image folder and return relative path.
			relfn = addImageToHtml(fn, imagesfold, reportdir)
		
			#####
			# Create custom title by removing extra bits.
			FileLists[href][relfn] = fnToTitle(relfn,ignores=ignoreList) 
			
			if debug:print "Adding ",relfn,"to script"
		filecount+=len(vfiles)			
	if filecount==0:return
							
	htmlTools.AddSubSections(indexhtmlfn,
			hrefs,
			SectionTitle,
			SidebarTitles=SidebarTitles,
			Titles=Titles, 
			Descriptions=Descriptions,
			FileLists=FileLists)


			
def addProfilesSection(
		akp,
		indexhtmlfn,
		imagesfold,
		reportdir,
		debug=False
		):
		
	if not akp.makeProfiles: return
		
	key = akp.key
	model = akp.model
	scenario = akp.scenario
	jobID = akp.jobID
	
	#####
	# href is the name used for the html 
	SectionTitle	= titleify([jobID,key ,'profiles',]) 	
	hrefs 		= []
	Titles		= {}
	SidebarTitles 	= {}
	Descriptions	= {}
	FileLists	= {}
	filecount = 0
	
	for region in akp.regions:
		href = 	hrefify([key, region, 'profile',model,scenario,jobID])
		hrefs.append(href)
		
		#####
		# Title is the main header, SidebarTitles is the side bar title.
		Titles[href] 		= titleify(['Profiles of', key,'in',jobID])	
		SidebarTitles[href] 	= titleify([region, ])
							
		#####
		# Descriptions is a small sub-header
		desc = ['Depth profile of the', model, 'model\'s',key, ]
		if len(akp.datasource):	desc += ['against',akp.datasource,'data',]
		desc += ['for the job', jobID, 
			'under the',scenario,'scenario', 
			'in the', region, 'region.']
								
		Descriptions[href] =  titleify(desc)
		#####
		# A list of files to put in this group.
		FileLists[href] = {}
		
		#####
		# Determine the list of files:
		vfiles = []
	

		files = {}
		filecheck = akp.images_pro +'/' +wildcardify([model, scenario,jobID, key,region,])+'*.png'		
		files = {f:1 for f in glob(filecheck)}
		vfiles.extend(sorted(files.keys()))
						
				
		#####
		# Create plot headers for each file.
		ignoreList = [model,scenario,jobID,]		
		for fn in vfiles:
			#####
			# Copy image to image folder and return relative path.
			relfn = addImageToHtml(fn, imagesfold, reportdir)
		
			#####
			# Create custom title by removing extra bits.
			FileLists[href][relfn] = fnToTitle(relfn,ignores=ignoreList) 
			
			if debug:print "Adding ",relfn,"to script"
		filecount+=len(vfiles)			
	if filecount==0:return
							
	htmlTools.AddSubSections(indexhtmlfn,
			hrefs,
			SectionTitle,
			SidebarTitles=SidebarTitles,#
			Titles=Titles, 
			Descriptions=Descriptions,
			FileLists=FileLists)	
			
						
def addP2PSection(
		akp,
		indexhtmlfn,
		imagesfold,
		reportdir,
		):
	if not akp.makeP2P: return
	
	key = akp.key
	model = akp.model
	scenario = akp.scenario
	jobID = akp.jobID
	year = akp.year	
	#####
	# href is the name used for the html 
	SectionTitle	= titleify([jobID,key ,'p2p in',year]) 				
		
	#SectionTitle= ' '.join([ getLongName(key), model, jobID, scenario,year,]) #getLongName(key)
	hrefs 		= []
	Titles		= {}
	SidebarTitles 	= {}
	Descriptions	= {}
	FileLists	= {}
	filecount	= 0
	
	for region in akp.regions:
	    for layer in akp.layers:
		href = 	hrefify([key, region,layer, 'p2p',year,model,scenario,jobID])
		hrefs.append(href)
		
		#####
		# Title is the main header, SidebarTitles is the side bar title.
		Titles[href] 		= titleify([ key,'point to point plots for',jobID,'in',region, layer])
		SidebarTitles[href] 	= titleify([ region, layer])
		
		#####
		# Descriptions is a small sub-header
		Descriptions[href] =  titleify(['Point to point comparison plots',
						'of the ', model, 'model\'s',key, 
						'against',akp.datasource,'data',
						'for the job', jobID, 
						'under the',scenario,'scenario', 
						'in the', region, 'region',
						'at', layer+'.'])

		#####
		# A list of files to put in this group.
		FileLists[href] = {}
		
		#####
		# Determine the list of files:
		vfiles = []
	
		files = {}
		filecheck = akp.images_p2p +'/' +wildcardify([model, scenario,jobID, key,region,layer,year,])+'*.png'				
	#	filecheck = akp.images_p2p +'/' +wildcardify([model, key,layer,region, year])+'*.png'
		files = {f:1 for f in glob(filecheck)}		
		#files.update({f:1 for f in glob(akp.images_p2p +'/*'+region+'*'+layer+'*.png')})
		#files.update({f:1 for f in glob(akp.images_p2p +'/*'+layer+'*'+region+'*.png')})
		vfiles.extend(sorted(files.keys()))
		filecount+=len(vfiles)
		#####
		# Create plot headers for each file.
		ignoreList = [model,scenario,jobID,]
		for fn in vfiles:
			#####
			# Copy image to image folder and return relative path.
			relfn = addImageToHtml(fn, imagesfold, reportdir)
		
			#####
			# Create custom title by removing extra bits.
			FileLists[href][relfn] = fnToTitle(relfn,ignores=ignoreList) 
			print "Adding ",relfn,"to script"

	if filecount==0:return
						
	htmlTools.AddSubSections(indexhtmlfn,
			hrefs,
			SectionTitle,
			SidebarTitles=SidebarTitles,#
			Titles=Titles, 
			Descriptions=Descriptions,
			FileLists=FileLists)			


def htmlMakerFromConfig(
		configfn,
		doZip = False
	):

	globalkeys = GlobalSectionParser(configfn)

	#####
	# Delete old files, if needed
	for (model,jobID,year,scenario,key),akp in globalkeys.AnalysisKeyParser.items():
		if not akp.clean: continue
		print "Removing old files from:",globalkeys.reportdir
		try:shutil.rmtree(globalkeys.reportdir)
		except: pass		
		

	reportdir = bvp.folder(globalkeys.reportdir)
	
	####
	# Copy all necceasiry objects and templates to the report location:
	print "Copying html and js assets to", reportdir
	copytree(package_directory+'/htmlAssets', reportdir)
	indexhtmlfn 	= reportdir+"index.html"
	try:	os.rename(reportdir+'index-template.html', indexhtmlfn)
	except: pass

	imagesfold 	= bvp.folder(reportdir+'images/')
	def newImageLocation(fn):
		return imagesfold+os.path.basename(fn)
	
	#####
	#
	def lst(ls):	return ', '.join(ls)
	descriptionText = '<p></p>'
	descriptionText += '<p>Evaluation of the '+lst(globalkeys.models)+' model '
	if globalkeys.jobIDs not in ['', ]:	descriptionText+=', with job ID: ' +lst(globalkeys.jobIDs) 
	if globalkeys.scenarios not in [ '', ]:	descriptionText+=', under scenario: ' +lst(globalkeys.scenarios) 
	if globalkeys.years not in [ '*', '']:	descriptionText+=', in the year: ' +lst(globalkeys.years) 	
	descriptionText += '</p>'
	
	htmlTools.writeDescription(
				indexhtmlfn,
				descriptionText,
				)
				
	if globalkeys.makeComp:
		addComparisonSection(
			globalkeys,
			indexhtmlfn,
			imagesfold,
			reportdir,
			model=model,
			scenario=scenario,
			)
				
	#####
	# This looping forces the report to match the order.
	for key,model,scenario in product(globalkeys.ActiveKeys, globalkeys.models,globalkeys.scenarios):
			
		
 	    	for jobID in globalkeys.jobIDs:	

			akp = globalkeys.AnalysisKeyParser[(model,jobID,globalkeys.years[0],scenario,key)]
			
			addTimeSeriesSection(
				akp,
				indexhtmlfn,
				imagesfold,
				reportdir,
				)
				
			addProfilesSection(
				akp,
				indexhtmlfn,
				imagesfold,
				reportdir,
				)
								
	  	    	for year in globalkeys.years:
				akp = globalkeys.AnalysisKeyParser[(model,jobID,year,scenario,key)]	
				addP2PSection(
					akp,
					indexhtmlfn,
					imagesfold,
					reportdir,
					)


        tar = "tar cfvz  report-"+hrefify(globalkeys.jobIDs)+".tar.gz "+reportdir

	print "-------------\nSuccess\ntest with:\nfirefox",indexhtmlfn
	print "To zip it up:\n",tar
	if doZip:
		import subprocess
		subprocess.Popen(tar.split())	


				
	
def main():
	htmlMakerFromConfig('runconfig.ini')			
	
	
if __name__=="__main__":	
	main()




