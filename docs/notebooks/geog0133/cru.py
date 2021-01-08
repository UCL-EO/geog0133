from netCDF4 import Dataset
import io
import gzip
import requests
from pathlib import Path
import numpy as np

def get_value(f,var,m,ilon,ilat):
    '''
    Get value of f[var][itime,ilat,ilon]
    
    In case the requested lat/long is masked 
    then take a distance weighted mean
    '''
    this = f[var][m,ilat,ilon]
    if not np.ma.is_masked(this):
        return this
    
    wlon = ((np.arange(np.array(f['lon'][:]).shape[0],dtype=np.int) - ilon)**2).astype(float)
    wlon[wlon==0] = 1e-20
    wlon = 1./wlon

    wlat = ((np.arange(np.array(f['lat'][:]).shape[0],dtype=np.int) - ilat)**2).astype(float)
    wlat[wlat==0] = 1e-20
    wlat = 1./wlat

    wlat = wlat[:,np.newaxis]
    wlon = wlon[np.newaxis,:]
    w = wlon * wlat
    data = f[var][m]
    w[data.mask] = 0.0
    data[data.mask] = 0.0

    return np.sum(data * w)/np.sum(w)

def getCRU(year=2019,month=[0,1,2,3,4,5,6,7,8,9,10,11],longitude=0,latitude=51):
    
    month = list(month)
    dataset = {}
    for var in ['tmx','tmn','cld']:
        if (year >= 2011 and year <= 2019):
            ofile = f'cru_ts4.04.2011.2019.{var}.dat.nc.gz'
            _year = year-2011
        else:
            print("year out of range: use 2011 to 2019")
            return(None)
        
        url=f'https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.04/' +\
                f'cruts.2004151855.v4.04/{var}/{ofile}'
        
        # check if the file exists, else pull it
        if not Path(f"data/{ofile}").exists():
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(f"data/{ofile}", 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
                
        ofilef = Path(f"data/{ofile}".replace('.dat.nc.gz','.dat.nc'))
        if not ofilef.exists():
            with gzip.open(f"data/{ofile}", 'rb') as f:
                file_content = f.read()
                ofilef.write_bytes(file_content)
            
        # read dataset
        tmx = Dataset(ofilef.as_posix(),'r')
        ilon = np.argmin(np.abs(tmx.variables['lon'][:] - longitude))
        ilat = np.argmin(np.abs(tmx.variables['lat'][:] - latitude))
        dataset[var] = []
        # loop over month
        for m in month:
            itime = m + _year*12
            this = tmx[var][itime,ilat,ilon]
            if np.ma.is_masked(this):
                this = get_value(tmx,var,m,ilon,ilat)
            dataset[var].append(this)
        dataset[var] = np.ma.array(dataset[var])
    return dataset

import scipy.ndimage.filters



def splurge(ipar,f=8.0):
    '''
    Spread the quantity ipar forward in time
    using a 1-sided exponential filter of width 
    f * 2.
    
    Arguments:
        ipar: array of 1/2 hourly time step ipar values 
              (length 48)
              
    Keyword:
        f : filter characteristic width. Filter is
            exp(-x/(f*2))
            
    Return:
        ipar_ : normalised, splurged ipar array
    '''
    if f == 0:
        return (ipar-ipar.min())/(ipar.max()-ipar.min())
    # build filter over large extent
    nrf_x_large = np.arange(-100,100)
    # filter function f * 2 as f is in hours
    # but data in 1/2 hour steps
    nrf_large = np.exp(-nrf_x_large/(f*2))    
    # 1-sided filter
    nrf_large[nrf_x_large<0] = 0
    nrf_large /= nrf_large.sum()
    ipar_ = scipy.ndimage.filters.convolve1d(ipar, nrf_large,mode='wrap')
    try:
      return (ipar_-ipar_.min())/(ipar_.max()-ipar_.min())
    except:
      return ipar*0


