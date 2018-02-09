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
.. module:: longnames
   :platform: Unix
   :synopsis: A list of names used for makeing text on plots pretty.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""

from calendar import month_name
#from itertools import product

import os
from glob import glob

from itertools import product
from bgcvaltools.configparser import checkConfig

package_directory = os.path.dirname(os.path.abspath(__file__))



#####
#	
   
		
def parseLongNames(fn):
	# Creates a longname dictionary from a filename
	print "parseLongNames:\tloading long name dict:",fn
	lnd = {}
	config = checkConfig(fn)
	for section in config.sections():
		options = config.options(section)
		for option in options:lnd[option] = config.get(section, option)
	####
	# Combinatorial stuff
	for field,region  in product(['BGC', 'Physics'],['Times', 'Regions']): # Sections
	    	try:
	    		field_options  = config.options(field)
		    	region_options = config.options(region)	    		    	
		except: continue
	    	for field_option,region_option in product(field_options,region_options):
	    		ln_f = config.get(field,  field_option)
	    		ln_r = config.get(region, region_option)
			lnd[field_option+region_option] = ' '.join([ln_f, ln_r])	    		
			lnd[field_option.lower()+region_option.lower()] = ' '.join([ln_f, ln_r])
			lnd[field_option.title()+region_option.title()] = ' '.join([ln_f, ln_r])			
			lnd[field_option.upper()+region_option.upper()] = ' '.join([ln_f, ln_r])	
			
	for txt in lnd.keys():
		longname	 = lnd[txt]
		lnd[longname]	 = longname
		lnd[txt.lower()] = longname
		lnd[txt.upper()] = longname
		lnd[txt.title()] = longname
		if len(txt)>1:	
			lnd[txt[0].upper()+txt[1:]] = longname			
	return lnd

longNameDict = {}
for longnamedictfn in glob(package_directory+'/*.ini'):
	longNameDict.update(parseLongNames(longnamedictfn))

def getLongName(text,debug=False):

	if debug: print "Getting long name:",text
	
	if type(text) in [type(['a','b',]),type(('a','b',))]:
		return ' '.join([getLongName(t) for t in text])
		#out = ''
		
	try: 	return longNameDict[text]
	except:	
		if debug: print "text not in dict:", text
	try: return longNameDict[text.lower()]
	except: 
		if debug: print "text.lower() not in dict:", text.lower()
	print "text not in dict:", text
		
	return text
	
	

def titleify(ls):
	"""
	Turns a list of strings into a longname.
	"""
       	return ' '.join([ getLongName(i) for i in ls])
	
		
	
	
def fancyUnits(units,debug=False):
	"""	
	Converts ascii units string into latex style formatting.
	"""
	units = units.replace('[','').replace(']','')
		
  	#if units in ['mg C/m^3','mg C/m^2',]:		return 'mg C m'+r'$^{-3}$'
  	if units in ['umol/l, uM, mo/l, ug/l, ',]:	return 'mg m'+r'$^{-3}$' # silly nitrates multi units
  	if units in ['mg C/m^3',]:			return 'mg C m'+r'$^{-3}$'
  	if units in ['mg Chl/m3','ng/L','mgCh/m3',]:		return 'mg Chl m'+r'$^{-3}$'  	
  	if units in ['mg C/m^3/d',]:			return 'mg C m'+r'$^{-3}$/day'
  	if units in ['mg N/m^3',]:			return 'mg N m'+r'$^{-3}$'  
  	if units in ['mg P/m^3',]:			return 'mg P m'+r'$^{-3}$'
  	if units in ['mmol N/m^3', 'mmol-N/m3' ]: 	return 'mmol N m'+r'$^{-3}$'
  	if units in ['mmol P/m^3', ]: 			return 'mmol P m'+r'$^{-3}$'
  	if units in ['mmol C/m^3', ]: 			return 'mmol C m'+r'$^{-3}$'
  	if units in ['umol F/m^3',]:			return r'$\mu$'+'mol m'+r'$^{-3}$'
  	if units in ['umol /m^3','umol / m3',]:		return r'$\mu$'+'mol m'+r'$^{-3}$' 
  	if units in ['mmol S/m^3', ]: 			return 'mmol S m'+r'$^{-3}$'  	
  	if units in ['mmolSi/m3', 'mmol Si/m^3', ]: 	return 'mmol Si m'+r'$^{-3}$'  	  	
  	if units in ['mmolFe/m3',]:			return 'mmol Fe m'+r'$^{-3}$'  	
  	
	if units in ['ug/l','mg/m^3','ug/L',]:  	return 'mg m'+r'$^{-3}$'
	if units in ['10^12 g Carbon year^-1',]:	return r'$10^{12}$'+' g Carbon/year'
	if units in ['mol C/m^',]:			return 'mol C/m'+r'$^{2}$'
  	if units in ['mmmol/m^3', 'mmol/m^3','umol/l','micromoles/l','mmolO2/m3']:
  							return 'mmol m'+r'$^{-3}$'
	if units in ['mmol/m^2']:			return 'mmol m'+r'$^{-2}$' 
	#if units in ['mmol/m^3']:			return 'mmol m'+r'$^{-3}$' 	
	if units in ['degrees Celsius', 'degreesC', 'C', 'degC', 'degrees_celsius',]:
							return r'$\,^{\circ}\mathrm{C}$'
	if units in ['psu','PSU',]:			return 'psu'
	#if units in ['umol/l',]:			return r'$\mu$'+'mol/l'
	if units in ['m','meters','meter',]:		return 'm'	
	if units in ['1/m',]:				return r'$\mathrm{m}^{-1}$'
	if units in ['m/s',]:				return r'$\mathrm{ms}^{-1}$'	
	#if units in ['ug/l']:			#	return 'mg m'+r'$^{-3}$'
	if units in ['W/m^2']:				return 'W m'+r'$^{-2}$'
	if units in ['umol/kg',]:			return r'$\mu$'+'mol kg'+r'$^{-1}$'
	if units in ['nmol/kg',]:			return 'nmol kg'+r'$^{-1}$'
	if units in ['tons C/d',]:			return 'tons C/day'
	if units in ['ug/L/d','ug                  ']:	return 'mg m'+r'$^{-3}$'+'/day'	#yes, there are lots of spaces
	if units.replace(' ','') in ['ug',]:		return r'$\mu$'+'g' #r'$\mu$'+	
	if units in ['1',]:			
		print 'fancyUnits:\tWarning:\tStrange units:',units
		return ''
	if units in ['uatm',]:				return r'$\mu$'+'atm'
	if units in ['ppmv',]:				return 'ppm'	
	if units in ['milliliters_per_liter',]:		return 'ml/l'
	print 'fancyUnits:\tERROR:\t',units,' not found in fancyUnits.'
	if debug:
		assert False
	return units 		
		
	
