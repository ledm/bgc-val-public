#!/usr/bin/ipython -i

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
# ledm@pml.ac.uk / momm@pml.ac.uk


import numpy as np
import netCDF4
from sys import argv 


#####
# I wish this class wasn't neccesairy.
# We had to do this because netCDF4.Dataset caused a stack trace when trying to load the field "filepath()". 
# This class should work the same way as netCDF4.Dataset, except that this object contains
# a netCDF4.Dataset instead of inheriting from it. As such, there are two layers of datasets.
# This is based on Momme's ncdfView.py class



class dataset:
	
    def __init__(self,filename,readflag='r',Quiet=True):
    	filename 		= filename.replace('//','/')
	
	try: 	self.dataset = netCDF4.Dataset(filename,readflag)
	except:	raise RuntimeError('dataset.py: Unable to open file: '+str(filename))

	self.__filename__ 	= filename
	self.netcdfPath 	= filename
	self.filename 		= filename		

	#####
	# link to various fields, so that the user experience is similar.
	self.variables 		= self.dataset.variables	
	self.dimensions 		= self.dataset.dimensions		
	try:	self.title 		= self.dataset.title	
	except: self.title		= ''
	try:	self.name 		= self.dataset.name	
	except: self.name		= ''
	try:	self.Conventions 	= self.dataset.Conventions	
	except: self.Conventions	= ''		
	try:	self.TimeStamp 		= self.dataset.TimeStamp	
	except: self.TimeStamp		= ''		
	try:	self.description 	= self.dataset.description	
	except: self.description	= ''	
	try:	self.ncattrs 		= self.dataset.ncattrs	
	except: self.ncattrs		= ''
	
	if not Quiet:print self.__unicode__()	
			

  
    def close(self):
    	try:	self.dataset.close()
    	except:	pass
    	
    	
    def __call__(self,varStr,Squeeze=False,Object=False):
	if Object:
	    return self.variables[varStr]
	else:
	    if Squeeze:
		a=self.variables[varStr][:].squeeze()
		return a
	    else:
		a=self.variables[varStr][:]
		return a

    def __unicode__(self):
	infoStr=u'-----------------\n'+\
            u'netCDF Object:\n'+\
            u'-----------------'
	for key in self.ncattrs():
            infoStr+=u'\n\n'+key.encode("utf-8")+u':\t'
            try: infoStr+=unicode(getattr(self,key))
            except:pass
        dimList=self.dimensions.items()
        dimList=[(key,dim,len(dim)) for key,dim in dimList]
        dimList.sort(cmp=lambda x,y: cmp(x[0],y[0]))
        for key,dim,size in dimList:
            infoStr+=u'\n\t'+key
            if dim.isunlimited(): 
                infoStr+=u'\tUNLIMITED => '+unicode(size)
            else:
                infoStr+=u'\t'+unicode(size)
        infoStr+=u'\n\n'+u'Variables:\n'
        varList=self.variables.items()
        varList.sort(cmp=lambda x,y: cmp(x[0],y[0]))
        for key,var in varList:
	    infoStr+='\n\t'+key+':'
            for k in var.ncattrs():
                if k=='long_name':
                   infoStr+=u'\t'+unicode(getattr(var,k))
		elif k=='units':
		   infoStr+=u'\t'+'['+unicode(getattr(var,k)+']')
            infoStr+=u'\n\t\t'+unicode(var.dimensions)+'='+unicode(var.shape)
            infoStr+=u'\t'+unicode(var.dtype)
        return infoStr




if __name__=="__main__":
    	fn=None
    	nc=dataset(argv[1],Quiet=False)
    
    
    	  
