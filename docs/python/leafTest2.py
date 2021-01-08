class sunInfo():
    '''
    A utility to work out some solar information
    '''
    def __init__(self,julianOffset=None):
        '''
        Initialise class

        options:
            julianOffset: set to report Julian day with an offset subtracted
                          Format, 'YYYY/M/D' e.g. '2012/1/1'
        '''
        # use the python library ephem
        try:
          import ephem
        except:
          import pyephem as ephem
        self.gatech = ephem.Observer()
        if julianOffset != None:
            self.julianOffset = ephem.julian_date(julianOffset)
        else:
            self.julianOffset  = 0.

        # http://acrim.com/TSI%20Monitoring.htm
        self.solar = 1361 #W/m2

        # PPFD is measured in micromoles/m2/sec
        # (Photosynthetic Photon Flux Density)

        # astronomical unit
        # http://neo.jpl.nasa.gov/glossary/au.html
        # we dont need this, but its interesting to know
        self.AU = 149597870.691 * 1e3 # m

        # energy content of PAR quanta
        self.EPAR = 220.e-3 # MJmol-1

    def sun(self,secs,mins,hours,days,months,years,lats,lons):
        '''
        Utility to set days, months, years, lats, lons
        and calculate max_solar_flux
        '''
        import ephem
        self.julian = []
        self.sza = []
        self.earth_distance = []

        import pdb;pdb.set_trace()
        for lon in np.atleast_1d(lons):
            self.gatech.lon = str(lon)
            for lat in np.atleast_1d(lats):
                self.gatech.lat = str(lat)
                for year in np.atleast_1d(years):
                    for month in np.atleast_1d(months):
                        for day in np.atleast_1d(days):
                            for hour in np.atleast_1d(hours):
                                for min in np.atleast_1d(mins):
                                    for sec in np.atleast_1d(secs):
                                        self.gatech.date = '%4d/%d/%d %d:%d:%d'%\
                                            (year,month,day,hour,min,int(sec))
                                        v = ephem.Sun(self.gatech)
                                        alt = np.max([0,v.alt * 180./np.pi])
                                        self.sza.append(90. - alt)
                                        jd = ephem.julian_date('%4d/%d/%d'%(year,month,day)) \
                                                 - self.julianOffset
                                        jd += hour/24. + min/60./24. + sec/60./60./24.
                                        self.julian.append(jd)
                                        self.earth_distance.append(v.earth_distance)
        self.julian = np.array(self.julian)
        self.sza = np.array(self.sza)
        self.earth_distance = np.array(self.earth_distance)
        self.solarRad = self.solar/(self.earth_distance*self.earth_distance)
        # Express radiation in mol(photons) / (m^2 s)
        self.solarRad_mol = self.solarRad/self.EPAR

    def plot(self,x,y,xname,yname,plotname='sunplot.png'):
        '''
        Plot utility
        '''
        plt.clf()
        plt.xlabel(xname)
        plt.ylabel(yname)
        plt.plot(x,y)
        plt.savefig('figures/' + plotname)

# get sun information
s = sunInfo(julianOffset='2012/1/1')
# loop over day (1 Jan 2012) at latitude 52.0
s.sun(0.,np.array([0.,30.]),np.arange(25),1,1,2012,52.0,0)
s.plot(s.julian,np.cos((s.sza*np.pi/180.)),'Fraction of day',\
       'Cosine of Solar Zenith angle (degrees)',plotname='sunplot.png')

# assume PAR is 50% of downwelling radiation
# and atmospheric optical thickness of PAR is 0.2
# we multiply by cos(solar zenith) here to project
# onto a flat surface (a 'big leaf')

tau = 0.2
mu = np.cos((s.sza*np.pi/180.))
ipar = s.solarRad_mol * 0.5 * np.exp(-tau/mu) * mu  # u mol(photons) / (m^2 s)

s.plot(s.julian,ipar,'Fraction of day','Indicent PAR radiation (approx. in units u mol(photons) / (m^2 s))',\
       plotname='ipar.png')

test1(self,n=len(ipar),Tc=25.0,name='c',ipar=ipar,co2_ppmv=390,x=ipar,xlabel='incident PAR (umol m-2 s-1)')

# now plot Al + Rd over the day
s.plot(s.julian,(self.Al+self.Rd)*1.e6,'Fraction of day','assimilation rate (u mol CO2 m-2 s-1)',plotname='Al.png')


