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
   :synopsis: A script to produce an html5 document summarising a jobs performance.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

#####	
# Load Standard Python modules:
from glob import glob
from sys import argv
import os 
import shutil

#####	
# Load specific local code:
from UKESMpython import folder, shouldIMakeFile,round_sig
from html5 import html5Tools, htmltables
from bgcvaltools.pftnames import getLongName

from bgcvaltools.configparser import AnalysisKeyParser, GlobalSectionParser

package_directory = os.path.dirname(os.path.abspath(__file__))

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
		if shouldIMakeFile(fn, newfn,):
			if debug: print "removing old file",fn
			os.remove(newfn)
			shutil.copy2(fn, newfn)			
			if debug: print "cp",fn, newfn
	return relfn

            

def addSections(
		configfn,
		indexhtmlfn,
		imagesfold,
		reportdir,
		key):

	akp = AnalysisKeyParser(configfn, key, debug=True)	
	
	#####
	# href is the name used for the html 

	SectionTitle= getLongName(key)
	hrefs 	= []
	Titles	= {}
	SidebarTitles = {}
	Descriptions= {}
	FileLists	= {}

	for region in akp.regions:
		href = 	key+'-'+region
		hrefs.append(href)
		
		#####
		# Title is the main header, SidebarTitles is the side bar title.
		Titles[href] = 	getLongName(region)
		SidebarTitles[href] = getLongName(region)	
							
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
	
		vfiles.extend(glob(akp.images_ts+'/*'+region+'*.png'))
		vfiles.extend(glob(akp.images_p2p+'/*/*'+region+'*.png'))
		
		#####
		# Create plot headers for each file.
		for fn in vfiles:
			#####
			# Copy image to image folder and return relative path.
			relfn = addImageToHtml(fn, imagesfold, reportdir)
		
			#####
			# Create custom title by removing extra bits.
			#title = filenameToTitle(relfn)

			FileLists[href][relfn] = html5Tools.fnToTitle(relfn) 
			print "Adding ",relfn,"to script"
						
	html5Tools.AddSubSections(indexhtmlfn,
			hrefs,
			SectionTitle,
			SidebarTitles=SidebarTitles,#
			Titles=Titles, 
			Descriptions=Descriptions,
			FileLists=FileLists)
				

def html5MakerFromConfig(
		configfn,
		doZip = False
	):


	globalkeys = GlobalSectionParser(configfn)

	

	
	if globalkeys.clean:
		#####
		# Delete old files
		print "Removing old files from:",globalkeys.reportdir
		try:shutil.rmtree(globalkeys.reportdir)
		except: pass

	reportdir = folder(globalkeys.reportdir)
	
	####
	# Copy all necceasiry objects and templates to the report location:
	print "Copying html and js assets to", reportdir
	copytree(package_directory+'/html5Assets', reportdir)
	indexhtmlfn 	= reportdir+"index.html"
	try:os.rename(reportdir+'index-template.html', indexhtmlfn)
	except: pass

	imagesfold 	= folder(reportdir+'images/')
	def newImageLocation(fn):
		return imagesfold+os.path.basename(fn)
	
	#####
	#
	descriptionText = 'Validation of the job: '+globalkeys.jobID
	if globalkeys.year != '*':	descriptionText+=', in the year: ' +globalkeys.year
	
	html5Tools.writeDescription(
				indexhtmlfn,
				descriptionText,
				)

	for key in globalkeys.ActiveKeys:
		addSections(
			configfn,
			indexhtmlfn,
			imagesfold,
			reportdir,
			key)
			


        tar = "tar cfvz  report-"+globalkeys.jobID+".tar.gz "+reportdir

	print "-------------\nSuccess\ntest with:\nfirefox",indexhtmlfn
	print "To zip it up:\n",tar
	if doZip:
		import subprocess
		subprocess.Popen(tar.split())	


				
	
def main():
	html5MakerFromConfig('runconfig.ini')			
	
	
if __name__=="__main__":	
	main()




