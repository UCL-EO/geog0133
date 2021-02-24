import ephem
import itertools
import numpy as np

import scipy.constants
from datetime import datetime
from datetime import timedelta
from geog0133.cru import getCRU,splurge

def solar_model(secs, mins, hours, days, months, years, lats, longs, 
                julian_offset='2000/1/1'):
    """A function that calculates the solar zenith angle (sza, in
    degrees), the Earth-Sun distance (in AU), and the instantaneous 
    downwelling solar radiation in mol(photons) per square meter per
    second for a set of time(s) and geographical locations. """
    solar_constant = 1361. #W/m2
    # energy content of PAR quanta
    energy_par = 220.e-3 # MJmol-1
    # Define the observer
    observer = ephem.Observer()
    # Additionally, add a julian date offset
    if julian_offset != 0:
        julian_offset = ephem.julian_date(julian_offset)
    # Ensure we can easily iterate over all inputs
    # Even if they're scalars
    secs = np.atleast_1d(secs)
    mins = np.atleast_1d(mins)
    hours = np.atleast_1d(hours)
    months = np.atleast_1d(months)
    days = np.atleast_1d(days)
    years = np.atleast_1d(years)
    lats = np.atleast_1d(lats)
    longs = np.atleast_1d(longs)

    # What we return
    julian_day = []
    sza = []
    earth_sun_distance = []
    
    for second, minute, hour, day, month, year, lati, longi in \
        itertools.product(
            secs,mins,hours,days,months,years,lats,longs):
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        observer.date = \
            f'{year:04d}/{month:d}/{day:d} {hour:d}:{minute:d}:{second:d}'
        
        observer.lon = f'{longi:f}'
        observer.lat = f'{lati:f}'
        solar_position = ephem.Sun(observer)
        solar_altitude = max([0, solar_position.alt * 180./np.pi])
        this_sza = 90. - solar_altitude
        this_distance_earth_sun = solar_position.earth_distance
        jd = ephem.julian_date(f'{year:04d}/{month:d}/{day:d}') - julian_offset
        jd += hour/24. + minute/60./24. + second/(3600*24) + 1
        julian_day.append(jd)
        sza.append(this_sza)
        earth_sun_distance.append(this_distance_earth_sun)
    
    julian_day = np.array(julian_day)
    sza = np.array(sza)
    earth_sun_distance = np.array(earth_sun_distance)
    iloc = np.argsort(julian_day)
    julian_day = julian_day[iloc]
    sza = sza[iloc]
    earth_sun_distance = earth_sun_distance[iloc]
    solar_radiation = solar_constant/(earth_sun_distance**2)
    # Express radiation in mol(photons) / (m^2 s)
    solar_radiation = solar_radiation/energy_par
    return julian_day, sza, earth_sun_distance, solar_radiation



import numpy as np
from datetime import datetime
from datetime import timedelta

def radiation(latitude,longitude,doy,
              tau=0.2,parprop=0.5,year=2019,domu=False,
              Tmin=5.0,Tmax=30.0,f=8.0):
    '''
    Simple model of solar radiation making call 
    to solar_model(), calculating modelled
    ipar 
    
    Arguments:
    latitude : latitude (degrees)
    longitude: longitude (degrees)
    doy:  day of year (integer)
    
    Keywords:
    
    tau:     optical thickness (0.2 default)
    parprop: proportion of solar radiation in PAR
    Tmin:    min temperature (C) 20.0 default
    Tmax:    max temperature (C) 30.0 default
    year:    int 2020 default
    f:       Temperature smearing function characteristic
             length (hours)
    domu:    Return mu at end of list
    '''
    # Calculate solar position over a day, every 30 mins
    # for somewhere like London (latitude 51N, Longitude=0)
    dt = datetime(year,1,1) + timedelta(doy-1)

    jd, sza, distance, solar_radiation = solar_model(
        0.,np.array([0.,30.]),np.arange(24),dt.day,dt.month,dt.year,
        latitude, 0 ,julian_offset=f'{year}/1/1')
    mu = np.cos(np.deg2rad(sza))
    
    n = mu.shape[0]

    ipar = solar_radiation* parprop * np.exp(-tau/mu) * mu  # u mol(photons) / (m^2 s)
    fd = getCRU(year,longitude=longitude,latitude=latitude)
    Tmax = fd['tmx'][dt.month-1]
    Tmin = fd['tmn'][dt.month-1]
    cld = fd['cld'][dt.month-1]
    scale = (1-cld/300.)
    #print(f'Tmin {Tmin:.2f} Tmax {Tmax:.2f} Cloud {cld:.2f} Scale {scale:.2f}')
    # reduce irradiance by 1/3 on cloudy day
    ipar = ipar * scale
    # smear ipar
    ipar_ = splurge(ipar,f=f)
    # normalise
    Tc = ipar_*(Tmax-Tmin)+Tmin
    #Tc = (Tc-Tc.min())
    #Tc = Tc/Tc.max()
    #Tc = (Tc*(Tmax-Tmin) + (Tmin))
    if domu:
      return jd-jd[0],ipar,Tc,mu
    else:
      return jd-jd[0],ipar,Tc

