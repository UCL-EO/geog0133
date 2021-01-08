
from photJules import *
import pylab as plt

self = photosynthesis()

def test1(self,n=100,name='a',ipar=200.,Tc=None,x=None,xlabel=None,\
          omega=None,co2_ppmv=390,C3=True,type='C3 grass',plot=True):
    '''
    low light level, span a temperature range, normal CO2
    '''
  
    self.data = np.zeros(n)

    # set plant type to C3
    self.C3 = np.zeros([n]).astype(bool) + C3

    self.Lcarbon = np.ones([n]) * 1
    self.Rcarbon = np.ones([n]) * 1
    self.Scarbon = np.ones([n]) * 1

    # set pft type
    # options are:
    # 'C3 grass', 'C4 grass', 'Needleleaf tree', 'Shrub'
    # 'Broadleaf tree'
    # Note that if C4 used, you must set the array
    # self.C3 to False

    self.pft = np.array([type]*n)

    # set up Ipar, incident PAR in (mol m-2 s-1)
    self.Ipar = np.ones_like(self.data) * ipar * 1e-6
    
    # set co2 (ppmv)
    self.co2_ppmv = co2_ppmv*np.ones_like(self.data)
    
    # set up a temperature range (C)
    try:
        if Tc == None:
            self.Tc = Tc or np.arange(n)/(1.*n) * 100. - 30.
        else:
            self.Tc = Tc
    except:
        self.Tc = Tc
    # initialise
    self.initialise()
    # reset defaults
    self.defaults()

    # omega
    if omega != None:
        self.omega = self.omega*0 + omega
    # calculate leaf and canopy photosynthesis
    self.photosynthesis()

    if plot == True:
        # plot
        plt.clf()
        if x == None:
            x = self.Tc
        plt.plot(x,self.Wc * 1e6,label='Wc')
        plt.plot(x,self.Wl * 1e6,label='Wl')
        plt.plot(x,self.We * 1e6,label='We')
        plt.plot(x,self.W * 1e6,label='W')
        plt.plot(x,self.Al* 1e6,label='Al')
        plt.plot(x,self.Rd* 1e6,label='Rd')

        plt.ylabel('assimilation rate (umol CO2 m-2 s-1)')
        if xlabel == None:
            plt.xlabel('temperature (C))')
        else:
            plt.xlabel(xlabel)
        plt.legend(loc='upper right')
        plt.savefig('figures/test1%s.png'%name)

# make sure can access pyephem
import sys
sys.path.append ("/home/ucfajlg/Data/python_libs/pyephem-3.7.5.1-py2.7-linux-x86_64.egg/" )
 
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
        import ephem
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
        for lon in np.nditer(lons):
            self.gatech.lon = str(lon)
            for lat in np.nditer(lats):
                self.gatech.lat = str(lat)
                for year in np.nditer(years):
                    for month in np.nditer(months):
                        for day in np.nditer(days):
                            for hour in np.nditer(hours):
                                for min in np.nditer(mins):
                                    for sec in np.nditer(secs):
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

