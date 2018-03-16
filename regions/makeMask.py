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
.. module:: makeMask
   :platform: Unix
   :synopsis: A function that produces a mask after a region.
.. moduleauthor:: Lee de Mora <ledm@pml.ac.uk>

"""
import numpy as np
import os, inspect
from calendar import month_name
from glob import glob

from bgcvaltools import bgcvalpython as bvp
from bgcvaltools.dataset import dataset
from bgcvaltools.configparser import AnalysisKeyParser, GlobalSectionParser

package_directory = os.path.dirname(os.path.abspath(__file__))

####


#####
# Global function, returns everything that is unmasked.
def Global(name,region, xt,xz,xy,xx,xd,debug=False): 	
 	m = np.ma.array(xd).mask
 	for a in [xt,xz,xy,xx]:
 		try: m += a.mask
 		except:pass	
	return np.ma.masked_where(m ,xd).mask

#####
# Useful zeros
def nonZero(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( xd == 0.,xd).mask 			
def aboveZero(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( xd <= 0.,xd).mask
def belowZero(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( xd >= 0.,xd).mask

#####
# Simple Regional masks
def NorthHemisphere(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( xy < 0.,xd).mask
def SouthHemisphere(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( xy > 0.,xd).mask
def Tropics(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( np.ma.abs(xy) >23.,xd).mask 
def Equatorial(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( np.ma.abs(xy) >7.,xd).mask 
def Temperate(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xy) <23.)+(np.ma.abs(xy) >60.),xd).mask 
def NorthTropics(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (xy >23.)+(xy < 7.),xd).mask 
def SouthTropics(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (xy <-23.)+(xy > -7.),xd).mask 
def NorthTemperate(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (xy <23.)+(xy >60.),xd).mask 
def SouthTemperate(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (xy >-23.)+(xy <-60.),xd).mask 
def AtlanticTransect(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( (xx > -26.)+(xx<-30.),xd).mask
def PacificTransect(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( (xx > -139.)+(xx<-143.),xd).mask
def tenN(name,region, xt,xz,xy,xx,xd,debug=False): 			return np.ma.masked_where( (xy >  12.)+(xy<  8.),xd).mask
def tenS(name,region, xt,xz,xy,xx,xd,debug=False): 			return np.ma.masked_where( (xy >  -8.)+(xy<-12.),xd).mask
def SouthernTransect(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( (xy > -55.)+(xy<-59.),xd).mask
def Arctic(name,region, xt,xz,xy,xx,xd,debug=False): 			return np.ma.masked_where( np.ma.abs(xy) < 60.,xd).mask
def Antarctic(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( xy > -60.,xd).mask 
def NorthArctic(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( xy < 60.,xd).mask 
def SouthernOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where(  xy >-40.,xd).mask 
def AntarcticOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where(  xy >-50.,xd).mask 
def ignoreArtics(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_outside(xy,-70., 70.).mask
def ignoreMidArtics(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_outside(xy,-65., 65.).mask
def ignoreMoreArtics(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_outside(xy,-60., 60.).mask
def ignoreExtraArtics(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_outside(xy,-50., 50.).mask 
def NorthAtlanticOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_outside(bvp.makeLonSafeArr(xx), -80.,0.).mask + np.ma.masked_outside(xy, 10.,60.).mask
def SouthAtlanticOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_outside(bvp.makeLonSafeArr(xx), -65.,20.).mask + np.ma.masked_outside(xy, -50.,-10.).mask
def EquatorialAtlanticOcean(name,region, xt,xz,xy,xx,xd,debug=False): return np.ma.masked_outside(bvp.makeLonSafeArr(xx), -65.,20.).mask + np.ma.masked_outside(xy, -15.,15.).mask

#####
# Complex Regional masks
def ArcticOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	 	
	mx = np.ma.masked_where(  xy < 60.,xd).mask 
	mx+= np.ma.masked_inside(xx, -45., 15.).mask * np.ma.masked_inside(xy, 50.,80.).mask
	return np.ma.masked_where( mx,xd).mask 

def NorthernSubpolarAtlantic(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_outside(xx,-74., -3. ).mask + np.ma.masked_outside(xy,40., 60. ).mask
	mx *= np.ma.masked_outside(xx, -45., 15.).mask + np.ma.masked_outside(xy, 60.,80.).mask
	return mx	

def NordicSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_outside(xx,-44., -5. ).mask 
	mx += np.ma.masked_outside(xy, 53., 65.).mask 
	return mx
	
def LabradorSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx  = np.ma.masked_outside(xx,-69., -45.).mask
	mx += np.ma.masked_outside(xy,  53., 67.).mask
	return mx

def NorwegianSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx  = np.ma.masked_outside(xx,-15., 10.).mask
	mx += np.ma.masked_outside(xy, 67., 76.).mask
	return mx

def YevgenyNordicSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_outside(xx,-44., -5. ).mask 
	mx += np.ma.masked_outside(xy, 53., 65.).mask 
	return mx
	
def YevgenyLabradorSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx  = np.ma.masked_outside(xx,-69., -45.).mask
	mx += np.ma.masked_outside(xy,  53., 67.).mask
	return mx

def YevgenyNorwegianSea(name,region, xt,xz,xy,xx,xd,debug=False): 	 
	mx  = np.ma.masked_outside(xx,-15., 10.).mask
	mx += np.ma.masked_outside(xy, 67., 76.).mask
	return mx

def NorthernSubpolarPacific(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx,-100., 120. ).mask
	mx += np.ma.masked_inside(xx,260., 365. ).mask		
	mx += np.ma.masked_outside(xy,40., 60. ).mask
	return np.ma.masked_where( mx,xd).mask 		

def Remainder(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = ignoreInlandSeas(name,region, xt,xz,xy,xx,xd,debug=debug)
	mx += np.ma.masked_inside(xy,-10., 10. ).mask
	mx += np.ma.masked_outside(abs(xy),-40., 40. ).mask		
	return np.ma.masked_where( mx,xd).mask 		

def Equator10(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = ignoreInlandSeas(name,region, xt,xz,xy,xx,xd,debug=debug)
        mx += np.ma.masked_outside(xy,-10., 10. ).mask
        return mx 

def NorthPacificOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx,-100., 120. ).mask
	mx += np.ma.masked_inside(xx,260., 365. ).mask		
	mx += np.ma.masked_outside(xy,10., 60. ).mask
	return mx

def EquatorialPacificOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx,-83., 120. ).mask
	mx += np.ma.masked_inside(xx,260., 365. ).mask		
	mx += np.ma.masked_outside(xy,-15., 15. ).mask
	return mx
	

def SouthPacificOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	 	
	mx = np.ma.masked_inside(xx,-70., 140. ).mask
	mx += np.ma.masked_inside(xx,290., 365. ).mask		
	my = np.ma.masked_outside(xy,-10., -50. ).mask
	return np.ma.masked_where( mx+my,xd).mask 
	
	
def HighLatWinter(name,region, xt,xz,xy,xx,xd,debug=False): 	 
	NHwinter = np.ma.masked_where( ~((xt == months['January'])+(xt == months['February']) +(xt == months['March'])    ) ,xd).mask
	SHwinter = np.ma.masked_where( ~((xt == months['July'])   +(xt == months['August'])   +(xt == months['September'])) ,xd).mask
	mnhw = np.ma.masked_where( (xy <  45.) + NHwinter ,xd).mask
	mshw = np.ma.masked_where( (xy > -45.) + SHwinter ,xd).mask 
	return   np.ma.masked_where( mnhw*mshw,xd).mask 

def CCI_JJA(name,region, xt,xz,xy,xx,xd,debug=False): 	
        mx = np.ma.masked_where(  xy < -53.,xd).mask
        mx += np.ma.masked_where(  xy > 80.,xd).mask
        return np.ma.masked_where( mx,xd).mask

def CCI_DJF(name,region, xt,xz,xy,xx,xd,debug=False): 	
        mx = np.ma.masked_where(  xy > 53.,xd).mask
        mx += np.ma.masked_where(  xy > 80.,xd).mask
        return np.ma.masked_where( mx,xd).mask
	
def BlackSea(name,region, xt,xz,xy,xx,xd,debug=False): 	 	
	mx = np.ma.masked_outside(xx, 25.9,41.7).mask
	my = np.ma.masked_outside(xy, 39.8,48.1).mask				
	return np.ma.masked_where( mx+my,xd).mask 
	
def ignoreBlackSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx, 25.9,41.7).mask
	my = np.ma.masked_inside(xy, 39.8,48.1).mask				
	return np.ma.masked_where( mx*my,xd).mask 	
	
def BalticSea(name,region, xt,xz,xy,xx,xd,debug=False): 	 	
	mx = np.ma.masked_outside(xx, 12.5,30.7).mask
	my = np.ma.masked_outside(xy, 53.0,66.4).mask				
	return np.ma.masked_where( mx+my,xd).mask 
	
def ignoreBalticSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx, 12.5,30.7).mask
	my = np.ma.masked_inside(xy, 53.0,66.4).mask				
	return np.ma.masked_where( mx*my,xd).mask 	

def RedSea(name,region, xt,xz,xy,xx,xd,debug=False): 	 	
	mx = np.ma.masked_outside(xx, 30.0,43.0).mask
	my = np.ma.masked_outside(xy, 12.4,30.4).mask				
	return np.ma.masked_where( mx+my,xd).mask 
	
def ignoreRedSea(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx, 30.0,43.0).mask
	my = np.ma.masked_inside(xy, 12.4,30.4).mask				
	return np.ma.masked_where( mx*my,xd).mask 	
	
def PersianGulf(name,region, xt,xz,xy,xx,xd,debug=False): 	 	
	mx = np.ma.masked_outside(xx, 47.5, 56.8).mask
	my = np.ma.masked_outside(xy, 22.3, 32.1).mask				
	return np.ma.masked_where( mx+my,xd).mask 
	
def ignorePersianGulf(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx, 47.5, 56.8).mask
	my = np.ma.masked_inside(xy, 22.3, 32.1).mask				
	return np.ma.masked_where( mx*my,xd).mask 										
	
def ignoreCaspian(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx = np.ma.masked_inside(xx,45.0,  55.0).mask * np.ma.masked_inside(xy, 35., 48.).mask 	# caspian
	return np.ma.masked_where( mx,xd).mask 
	
def ignoreMediteranean(name,region, xt,xz,xy,xx,xd,debug=False): 	
	mx  = np.ma.masked_inside(xx, -5.8, 42.5).mask #E
	my  = np.ma.masked_inside(xy, 30., 43.).mask	#N			
	mx2 = np.ma.masked_inside(xx, 0., 20.).mask #E
	my2 = np.ma.masked_inside(xy, 32., 47.).mask #N
	m = mx*my+ mx2*my2
	return np.ma.masked_where( m,xd).mask 		

def ignoreInlandSeas(name,region, xt,xz,xy,xx,xd,debug=False): 	 
	mx = np.ma.masked_inside(xx, 47.5,  56.8).mask * np.ma.masked_inside(xy, 22.3, 32.1).mask	
	mx += np.ma.masked_inside(xx, 30.0, 43.0).mask * np.ma.masked_inside(xy, 12.4,30.4).mask	
	mx += np.ma.masked_inside(xx, 12.5, 30.7).mask * np.ma.masked_inside(xy, 53.0,66.4).mask
	mx += np.ma.masked_inside(xx, 25.9, 41.7).mask * np.ma.masked_inside(xy, 39.8,48.1).mask		
	mx += np.ma.masked_inside(xx, -5.8, 42.5).mask * np.ma.masked_inside(xy, 30., 43.).mask
	mx += np.ma.masked_inside(xx, 0.0,  20.0).mask * np.ma.masked_inside(xy, 32., 47.).mask 
	mx += np.ma.masked_inside(xx,45.0,  55.0).mask * np.ma.masked_inside(xy, 35., 52.).mask 	# caspian
	return np.ma.masked_where( mx,xd).mask 		
	
def IndianOcean(name,region, xt,xz,xy,xx,xd,debug=False): 	 
	mx = np.ma.masked_inside(xx, 47.5,  56.8).mask * np.ma.masked_inside(xy, 22.3, 32.1).mask	
	mx += np.ma.masked_inside(xx, 30.0, 43.0).mask * np.ma.masked_inside(xy, 12.4,30.4).mask	
	mx += np.ma.masked_inside(xx, 12.5, 30.7).mask * np.ma.masked_inside(xy, 53.0,66.4).mask
	mx += np.ma.masked_inside(xx, 25.9, 41.7).mask * np.ma.masked_inside(xy, 39.8,48.1).mask		
	mx += np.ma.masked_inside(xx, -5.8, 42.5).mask * np.ma.masked_inside(xy, 30., 43.).mask
	mx += np.ma.masked_inside(xx, 0.0,  20.0).mask * np.ma.masked_inside(xy, 32., 47.).mask 
	mx += np.ma.masked_inside(xx,45.0,  55.0).mask * np.ma.masked_inside(xy, 35., 52.).mask 	# caspian
	mx += np.ma.masked_outside(xx, 25.,100.).mask
	my = np.ma.masked_outside(xy, -50.,30.).mask
	return np.ma.masked_where( mx+my,xd).mask 
	
	
	

#####
# Depths masks
def Depth_0_10m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( np.ma.abs(xz) > 10.,xd).mask 
def Depth_0_100m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( np.ma.abs(xz) > 100.,xd).mask 
def Depth_10_20m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xz) < 10.)+(np.ma.abs(xz) > 20.),xd).mask 
def Depth_20_50m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xz) > 20.)+(np.ma.abs(xz) > 50.),xd).mask 
def Depth_50_100m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xz) < 50.)+(np.ma.abs(xz) > 100.),xd).mask
def Depth_100_500m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xz) < 100.)+(np.ma.abs(xz) > 500.),xd).mask
def Depth_500m(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where(  np.ma.abs(xz) < 500.,xd).mask
def Depth_0_50m(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where( np.ma.abs(xz) > 50.,xd).mask
def Depth_50_100m(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where( (np.ma.abs(xz) < 50.)+(np.ma.abs(xz) > 100.),xd).mask
def Depth_100_200m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xz) < 100.)+(np.ma.abs(xz) > 200.),xd).mask
def Depth_200_500m(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( (np.ma.abs(xz) < 200.)+(np.ma.abs(xz) > 500.),xd).mask
def Depth_500_1000m(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( (np.ma.abs(xz) < 500.)+(np.ma.abs(xz) > 1000.),xd).mask
def Depth_1000_2000m(name,region, xt,xz,xy,xx,xd,debug=False): 	return np.ma.masked_where( (np.ma.abs(xz) < 1000.)+(np.ma.abs(xz) > 2000.),xd).mask
def Depth_1000m(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where(  np.ma.abs(xz) < 1000.,xd).mask
def Depth_2000m(name,region, xt,xz,xy,xx,xd,debug=False): 	 	return np.ma.masked_where(  np.ma.abs(xz) < 2000.,xd).mask
def Shallow(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( xz > 200.,xd).mask
def Deep(name,region, xt,xz,xy,xx,xd,debug=False): 			return np.ma.masked_where( xz < 200.,xd).mask


#####
# Time masks
# These only work if the time array is in months, starting from zero.
months = {month_name[i+1]:i for i in xrange(0,12) }
def January(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( ~(xt == months['January']),xd).mask
def February(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( ~(xt == months['February']),xd).mask
def March(name,region, xt,xz,xy,xx,xd,debug=False):		return np.ma.masked_where( ~(xt == months['March']),xd).mask
def April(name,region, xt,xz,xy,xx,xd,debug=False):		return np.ma.masked_where( ~(xt == months['April']),xd).mask
def May(name,region, xt,xz,xy,xx,xd,debug=False):		return np.ma.masked_where( ~(xt == months['May']),xd).mask
def June(name,region, xt,xz,xy,xx,xd,debug=False):		return np.ma.masked_where( ~(xt == months['June']),xd).mask
def July(name,region, xt,xz,xy,xx,xd,debug=False):		return np.ma.masked_where( ~(xt == months['July']),xd).mask
def August(name,region, xt,xz,xy,xx,xd,debug=False):		return np.ma.masked_where( ~(xt == months['August']),xd).mask
def September(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( ~(xt == months['September']),xd).mask
def October(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( ~(xt == months['October']),xd).mask
def November(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( ~(xt == months['November']),xd).mask
def December(name,region, xt,xz,xy,xx,xd,debug=False):	return np.ma.masked_where( ~(xt == months['December']),xd).mask
	
def JFM(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where( ~(xt== months['January'])+(xt== months['February'])+(xt== months['March']),xd).mask 
def AMJ(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where(~(xt==months['April'])+(xt==months['May'])+(xt==months['June']),xd).mask 
def JAS(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where(~(xt==months['July'])+(xt==months['August'])+(xt==months['September']),xd).mask 
def OND(name,region, xt,xz,xy,xx,xd,debug=False): 		return np.ma.masked_where(~(xt==months['October'])+(xt==months['November'])+(xt==months['December']),xd).mask 




#####
# The std_maskerslist was made with the following script:
#lines = open('makeMasks.py','r')
#
#for l in lines:
#	if len(l)<6:continue
#	if l[0] in ['#','\t','\\', ' ',]:continue
#	start = 4
#	end = l.find('(')
#	s = l[start:end]
#	if s[0] in ['+', '=']:continue
#	if l.find('std_maskers')==0:continue
#	print "std_maskers['"+s+"'] \t= "+s
#
std_maskers = {}
std_maskers['Global'] 		= Global
std_maskers['All'] 		= Global
std_maskers['regionless'] 	= Global
std_maskers['layerless'] 	= Global
std_maskers['nonZero'] 		= nonZero
std_maskers['aboveZero'] 	= aboveZero
std_maskers['belowZero'] 	= belowZero

# Regions
std_maskers['NorthHemisphere'] 	= NorthHemisphere
std_maskers['SouthHemisphere'] 	= SouthHemisphere
std_maskers['Tropics'] 		= Tropics
std_maskers['Equatorial'] 	= Equatorial
std_maskers['Temperate'] 	= Temperate
std_maskers['NorthTropics'] 	= NorthTropics
std_maskers['SouthTropics'] 	= SouthTropics
std_maskers['NorthTemperate'] 	= NorthTemperate
std_maskers['SouthTemperate'] 	= SouthTemperate
std_maskers['AtlanticTransect'] = AtlanticTransect
std_maskers['PacificTransect'] 	= PacificTransect
std_maskers['tenN'] 		= tenN
std_maskers['tenS'] 		= tenS
std_maskers['SouthernTransect'] = SouthernTransect
std_maskers['Arctic'] 		= Arctic
std_maskers['Antarctic'] 	= Antarctic
std_maskers['NorthArctic'] 	= NorthArctic
std_maskers['SouthernOcean'] 	= SouthernOcean
std_maskers['AntarcticOcean'] 	= AntarcticOcean
std_maskers['ignoreArtics'] 	= ignoreArtics
std_maskers['ignoreMidArtics'] 	= ignoreMidArtics
std_maskers['ignoreMoreArtics'] 	= ignoreMoreArtics
std_maskers['ignoreExtraArtics'] 	= ignoreExtraArtics
std_maskers['NorthAtlanticOcean'] 	= NorthAtlanticOcean
std_maskers['SouthAtlanticOcean'] 	= SouthAtlanticOcean
std_maskers['EquatorialAtlanticOcean'] 	= EquatorialAtlanticOcean
std_maskers['ArcticOcean'] 		= ArcticOcean
std_maskers['NorthernSubpolarAtlantic'] = NorthernSubpolarAtlantic
std_maskers['NordicSea'] 		= NordicSea
std_maskers['LabradorSea'] 		= LabradorSea
std_maskers['NorwegianSea'] 		= NorwegianSea
std_maskers['YevgenyNordicSea'] 	= YevgenyNordicSea
std_maskers['YevgenyLabradorSea'] 	= YevgenyLabradorSea
std_maskers['YevgenyNorwegianSea'] 	= YevgenyNorwegianSea
std_maskers['NorthernSubpolarPacific'] 	= NorthernSubpolarPacific
std_maskers['Remainder'] 		= Remainder
std_maskers['Equator10'] 		= Equator10
std_maskers['NorthPacificOcean'] 	= NorthPacificOcean
std_maskers['EquatorialPacificOcean'] 	= EquatorialPacificOcean
std_maskers['SouthPacificOcean'] 	= SouthPacificOcean
std_maskers['HighLatWinter'] 		= HighLatWinter
std_maskers['CCI_JJA'] 			= CCI_JJA
std_maskers['CCI_DJF'] 			= CCI_DJF
std_maskers['BlackSea'] 		= BlackSea
std_maskers['ignoreBlackSea'] 		= ignoreBlackSea
std_maskers['BalticSea'] 		= BalticSea
std_maskers['ignoreBalticSea'] 		= ignoreBalticSea
std_maskers['RedSea'] 			= RedSea
std_maskers['ignoreRedSea'] 		= ignoreRedSea
std_maskers['PersianGulf'] 		= PersianGulf
std_maskers['ignorePersianGulf'] 	= ignorePersianGulf
std_maskers['ignoreCaspian'] 		= ignoreCaspian
std_maskers['ignoreMediteranean'] 	= ignoreMediteranean
std_maskers['ignoreInlandSeas'] 	= ignoreInlandSeas
std_maskers['IndianOcean'] 		= IndianOcean

# Depths
std_maskers['Depth_0_10m'] 	= Depth_0_10m
std_maskers['Depth_0_100m'] 	= Depth_0_100m
std_maskers['Depth_10_20m'] 	= Depth_10_20m
std_maskers['Depth_20_50m'] 	= Depth_20_50m
std_maskers['Depth_50_100m'] 	= Depth_50_100m
std_maskers['Depth_100_500m'] 	= Depth_100_500m
std_maskers['Depth_500m'] 	= Depth_500m
std_maskers['Depth_0_50m'] 	= Depth_0_50m
std_maskers['Depth_50_100m'] 	= Depth_50_100m
std_maskers['Depth_100_200m'] 	= Depth_100_200m
std_maskers['Depth_200_500m'] 	= Depth_200_500m
std_maskers['Depth_500_1000m'] 	= Depth_500_1000m
std_maskers['Depth_1000_2000m'] = Depth_1000_2000m
std_maskers['Depth_1000m'] 	= Depth_1000m
std_maskers['Depth_2000m'] 	= Depth_2000m
std_maskers['Shallow'] 		= Shallow
std_maskers['Deep'] 		= Deep

# Times
std_maskers['January'] 		= January
std_maskers['February'] 	= February
std_maskers['March'] 		= March
std_maskers['April'] 		= April
std_maskers['May'] 		= May
std_maskers['June'] 		= June
std_maskers['July'] 		= July
std_maskers['August'] 		= August
std_maskers['September']	= September
std_maskers['October'] 		= October
std_maskers['November'] 	= November
std_maskers['December'] 	= December
std_maskers['JFM'] 		= JFM
std_maskers['AMJ'] 		= AMJ
std_maskers['JAS'] 		= JAS
std_maskers['OND'] 		= OND

#####
# Add lower case, upper, Title, etc...
std_maskers = bvp.altSpellingDict(std_maskers)


def loadCustomMasks(debug=False):
	"""
	This function loads all the custom modules in the regions folder, and adds them to the std_maskers dict.
	This means that users can add custom regional definitions to their runconfig.ini file, 
	as long as the function name.
	"""
	outDict = {}
	modules = {}
	all_modules = {}
	for functionFileName in glob(package_directory+'/*.py'):
		#####
		# Skip this file (don't load twice!) and skip __init__.py
		if functionFileName == os.path.realpath(__file__):	continue
		if functionFileName.find('__init__.py')>-1: 		continue

		#####
		# Determine the filename			
		functionFileName = 'regions.'+os.path.basename(functionFileName)
		lst = functionFileName.replace('.py','').replace('/', '.').split('.')		
		modulename =  '.'.join(lst)
		
		#####
		# Load the file as a module
		if debug: print "\nmakeMask.py:\timporting ",modulename
		modules[modulename] = __import__(modulename)

		#####
		# Look at the contents of the file
		all_modules[modulename] = inspect.getmembers(modules[modulename], inspect.ismodule)
		for (modname,mod) in all_modules[modulename]:
			all_functions = inspect.getmembers(mod, inspect.isfunction)			
			for (funcname,func) in all_functions:
				if debug: print "Module:",modname," has the functions:", funcname
				if funcname in std_maskers.keys(): 	print "loadCustomMasks:\tWARNING:\tOverwriting previous mask:",funcname
				outDict[funcname] = func
	if debug: print "Successfully added keys:",outDict.keys()
	outDict = bvp.altSpellingDict(outDict)	
	return outDict			

std_maskers.update(loadCustomMasks())







def loadMaskMakersConfig(configfile = ''):
	#####
	# First, make a list of all possible regions requested.
	maskingfunctions = []
	globalKeys =  GlobalSectionParser(configfile)
	for key in globalKeys.ActiveKeys:
		akp = AnalysisKeyParser(configfile, key, debug=True)
		maskingfunctions.extend(akp.regions)
	
	#####
	# Cast to dictionary to remove duplicates.
	maskingfunctions = {region:'' for region in maskingfunctions}

	outRegions = []	
	#####
	# Create a dictionairy of the masking functions.
	for region in maskingfunctions.keys():
		#####
		# The region requestion is one of the standard regions, defined above,
		# or in another file in this folder.
		if region in std_maskers.keys():
			maskingfunctions[region] = std_maskers[region]
			outRegions.append(region)
			#continue
		else:
			raise AssertionError("loadMaskMakersConfig:\tNot able to find this region name: "+str(region)+\
					"\nIs the region function in the bgcval/region folder?"+\
					"\nIs the filename the same as the function?")

	return outRegions, maskingfunctions		

def loadMaskMakersList(regions = []):
	#####
	# Create a dictionairy of the masking functions.
	maskingfunctions = {}
	outRegions = []
	
	for region in regions:
		#####
		# The region requestion is one of the standard regions, defined above,
		# or in another file in this folder.
		if region in std_maskers.keys():
			maskingfunctions[region] = std_maskers[region]
			outRegions.append(region)
		else:
			raise AssertionError("loadMaskMakersConfig:\tNot able to find this region name: "+str(region)+\
				"\n\t\tIs the region function in the bgcval/region folder?"+\
				"\n\t\tIs the filename the same as the function name?")
					
	return outRegions, maskingfunctions	



	
def loadMaskMakers(configfile = '', regions = []):
	#####
	# Create a dictionairy of the masking functions, either from a list of a config file.
	print "loadMaskMakers:\tconfigfile", configfile,"\tregions:",regions, len(regions)
	if len(regions) == 0:
		return loadMaskMakersConfig(configfile = configfile)
	else:	return loadMaskMakersList(  regions    = regions)
		
	 	
def makeMask(maskingfunctions, name,region, xt,xz,xy,xx,xd,debug=False):
	"""
	:param name: The name of the data. (useful for debugging)
	:param region: The name of the regional cut (or slice)
	:param xt: A one-dimensional array of the dataset times.
	:param xz: A one-dimensional array of the dataset depths.
	:param xy: A one-dimensional array of the dataset latitudes.
	:param xx: A one-dimensional array of the dataset longitudes.
	:param xd: A one-dimensional array of the data.

	Wrapper so that it behaves as it did before.
		
	This function produces a mask to hides all points that are not in the requested region.
	
	Note that xt,xz,xy,xx,xd should all be the same shape and size. 
	
	This functional can call itself, if two regional masks are needed.
	
	Please add your own regions, at the bottom of the list, if needed.
	"""	
	if debug:print "makeMask:\tmakeMask:\tinitialise:\t",name, '\t',"\""+region+"\""
	return maskingfunctions[region](name,region, xt,xz,xy,xx,xd,debug=debug)
  	






	
