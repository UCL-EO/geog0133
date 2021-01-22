def GPP(p,verbose=False):
    # now we want the canopy level response
    p.LAI = p.Lcarbon/p.sigmal

    # leaf single scattering albedo
    p.omega = 0.2
    p.G = 0.5
    p.mubar = np.mean(p.mu_)
    p.kbar = (p.G/p.mubar)*np.sqrt(1-p.omega)
    p.fapar = 1 - np.exp(-p.kbar * p.LAI)
    if verbose:
        print (f'doy {doy:03d} - mubar = {p.mubar:.2f}')
        print (f'doy {doy:03d} - kbar = {p.kbar:.2f}')
        print (f'doy {doy:03d} - fapar = {p.fapar.mean():.2f}')

    # kg C m-2 s-1: conversion factor from Clark et al. 2011
    p.PiG = 0.012 * (p.Al + p.Rd)* p.fapar / p.kbar
    return(p)


def NPP(p):
    p = GPP(p,verbose=False)
    # NPP calculation
    p.rg = 0.25
    # scale Rd (respiration in the light) up to canopy here
    p.Rpm = 0.036 * p.Rd * p.fapar / p.kbar
    # Gpp from above, introducing beta
    p.PiG = 0.012*( p.Al - p.beta * p.Rd) * p.fapar / p.kbar
    # Grow respiration is a fraction of (GPP - maint resp)
    p.Rpg = p.rg * (p.PiG - p.Rpm)
    # ensure Rpg is non negative
    p.Rpg[p.Rpg < 0] = 0.
    # total respiration
    p.Rp = p.Rpm + p.Rpg
    # NPP: calculated as the difference
    p.Pi = p.PiG - p.Rp
    return p


def daily_PP(pft="C3 grass",Lcarbon=0.07,\
             latitude=51.,longitude=0.,year=2019):
    '''
    Daily GPP and NPP
    
    Returns numpy arrays of:
        doys
        gpp
        npp
    
    Keywords:
        pft       : PFT name
                    default "C3 grass"
        Lcarbon   : leaf carbon (kg C m-2)
                    default 0.07
        latitude  : latitude (degrees)
                    default 51.0
        longitude : longitude (degrees)
                    default 0.0
        year      : year, default 2019
                    (2011-2019 allowed)
    
    '''
    doys = np.arange(1,366,dtype=np.int)
    gpp = np.zeros_like(doys).astype(np.float)
    npp = np.zeros_like(doys).astype(np.float)
    for i,doy in enumerate(doys):
        jd,ipar,Tc,mu = radiation(latitude,longitude,\
                                  int(doy),domu=True,year=year)
        # run the leaf level model
        p = do_photosynthesis(n=len(ipar), pft_type=pft,Tc=Tc,\
                              ipar=ipar,co2_ppmv=390,\
                              x=ipar,plotter=None)[0]
        # now we want the canopy level response
        p.mu_ =  mu
        p.Lcarbon = Lcarbon # kg C m-2
        p = NPP(p)
        nsec_in_day = 60 * 60 * 24
        gpp[i] = p.PiG.mean() * nsec_in_day
        npp[i] = p.Pi.mean() * nsec_in_day
    return doys,gpp,npp

def annual_npp(pft="C3 grass",Lcarbon=0.07,\
             latitude=51.,longitude=0.,year=2019):
    '''
    Annual GPP and NPP
    
    Returns values of:
        gpp
        npp
    
    Keywords:
        pft       : PFT name
                    default "C3 grass"
        Lcarbon   : leaf carbon (kg C m-2)
                    default 0.07
        latitude  : latitude (degrees)
                    default 51.0
        longitude : longitude (degrees)
                    default 0.0
        year      : year, default 2019
                    (2011-2019 allowed)
    
    '''
    doys,gpp,npp = daily_PP(pft=pft,year=year,\
                        latitude=latitude,longitude=longitude)
    integral_npp = np.sum(npp) * 1e3 * 0.01 # t C/ha/yr
    integral_gpp = np.sum(gpp) * 1e3 * 0.01 # t C/ha/yr
    return integral_npp,integral_gpp

