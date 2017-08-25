
print "importing TotalAirSeaFluxCO2"


def TotalAirSeaFluxCO2(nc,keys):
	akp = AnalysisKeyParser(configfile, key, debug=True)

	nc = dataset(paths.orcaGridfn,'r')
	area = nc.variables['e1t'][:]*nc.variables['e2t'][:]
	nc.close()

	

	def eOrcaTotal(nc,keys):
		factor =  365.25 * 12./1000. / 1.E15
		arr = nc.variables['CO2FLUX'][:].squeeze() * factor	# mmolC/m2/d
		if arr.ndim ==3:
			for i in np.arange(arr.shape[0]):
				arr[i] = arr[i]*area
		elif arr.ndim ==2: arr = arr*area
		else: assert 0
		return arr.sum()

	def takaTotal(nc,keys):
		arr = nc.variables['TFLUXSW06'][:].squeeze()	# 10^12 g Carbon year^-1
		arr = -1.E12* arr /1.E15#/ 365.				#g Carbon/day
		#area = nc.variables['AREA_MKM2'][:].squeeze() *1E12	# 10^6 km^2
		#fluxperarea = arr/area
		return arr.sum()
		# area 10^6 km^2
		# flux:  10^15 g Carbon month^-1. (GT)/m2/month




