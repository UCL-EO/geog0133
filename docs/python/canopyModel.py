
import numpy as np
import scipy.optimize

from modellingPractical import *


# Follow the setup from the vegetation modelling practical

def drivers(year=2001,lat=50.,lon=0.0,ndays=365\
            ,tau=0.2,parScale=0.5,tempScale=35.):
    # get sun information
    s = sunInfo(julianOffset='%4d/1/1'%year)

    # loop over day and month at latitude 50.0
    # NB we use the dates 1-366 of January here to avoid month issues
    # be careful here ... only use the minutes field if hours set to every hour
    # else dt isnt constant
    s.sun(0.,np.array([0.]),np.arange(24/2)*2.,np.arange(ndays)+1,1.,year,lat,lon)

    # Asssume PAR is 50% (parScale) of downwelling radiation
    # and atmospheric optical thickness of PAR is 0.2 (tau)
    # we multiply by cos(solar zenith) here to project
    # onto a flat surface (a 'big leaf')
    mu = np.cos((s.sza*np.pi/180.))
    ipar = s.solarRad_mol *parScale * np.exp(-tau/mu) * mu  # u mol(photons) / (m^2 s)
    temp = tempScale * mu
    dt = (s.julian[1]-s.julian[0]) * 24 * 60 * 60 #  in seconds  
    # temperature estimated from SW down
    return [ipar,temp,mu,s.julian,dt]


def leafScale(ipar,temp,co2_ppmv=390.,omega=None,\
              type='C3 grass',C3=True,plotName='leaf1'):
    leaf = photosynthesis()
    # run the leaf level model
    test1(leaf,n=len(ipar),Tc=temp,C3=C3,type=type,omega=omega,\
	name=plotName,ipar=ipar,co2_ppmv=co2_ppmv,plot=None)
    return leaf

def canopyScale(self,LAIinit,mu,julian,leafLoss=1./100.,\
                dt=1800.,leafNPPProportion=0.3,delay=0):
    self.Lcarbon[:] = LAIinit * self.sigmal # kg C m-2
    self.leafLoss = leafLoss
    #self.sigmal = 0.025 # kg C m-2 per unit LAI for C3 grass
    # for Needleleaf tree: 0.10
    # for Broadleaf tree: 0.0375
    # for others: 0.05
    self.LAI = 0.*self.Lcarbon/self.sigmal
    self.LAI[0] = LAIinit
    self.leafNPPProportion = leafNPPProportion
    # leaf single scattering albedo
    # NPP/GPP scalar
    self.rg = 0.25

    self.G = 0.5
    self.mubar = np.mean(mu)
    self.kbar = (self.G/self.mubar)*np.sqrt(1-self.omega)
    self.fapar = 1 - np.exp(-self.kbar * self.LAI)
    # the underscore indicates a need to scale by fapar
    # 0.012: kg C m-2 s-1: conversion factor from Clark et al. 2011
    self.Rpm_ = 0.036 * self.Rd / self.kbar
    self.PiG_ = 0.012*(self.Al - self.beta * self.Rd) / self.kbar
    self.Rpg_ = self.rg * (self.PiG_ - self.Rpm_)
    self.Rp_ = self.Rpm_ + self.Rpg_
    self.Rp_[self.Rp_<0] = 0.
    # NPP: self.Pi
    self.Pi_ = self.PiG_ - self.Rp_

    self.Rpm = np.zeros_like(self.fapar)
    self.Rpg = np.zeros_like(self.fapar)
    self.Rp = np.zeros_like(self.fapar)
    self.PiG = np.zeros_like(self.fapar)
    self.Pi = np.zeros_like(self.fapar)

    # leaf loss is per year
    # so if leafLoss is 1, we lose leaf over 1 year, if 0.5 over half a year
    decay = np.exp(-(julian-julian[0])/(70.*leafLoss))
    #w = np.where((julian-julian[0]) <= leafLoss*365)
    #decay = np.zeros_like(self.fapar)
    #decay[w] = 1.0
    # integral = 1
    decay = decay/decay.sum()
    delay = leafLoss*365
    ddelay = np.where(np.abs(julian-delay) == (np.abs(julian-delay)).min())[0][0]
    # put a decay on the original LAI
    origPlusDLcarbon = self.LAI[0] * self.sigmal[0]
    self.leafLoss = decay * origPlusDLcarbon
    self.leafGain = np.zeros_like(self.leafLoss)
    #self.leafGain[0] = origPlusDLcarbon
    # all below here is dynamic
    # so we run in a loop
    #sigma = delay/3.5
    #Z = (julian-delay)/sigma
    #decay[:] = np.exp(-0.5*Z**2)
    #decay[:ddelay] = 1
    #decay = decay / decay.sum()
    for i in range(len(self.LAI)-1):
        self.fapar[i] = 1 - np.exp(-self.kbar[i] * self.LAI[i])
        # NPP: self.Pi: integral over the time period
        self.Pi[i] = self.Pi_[i] * self.fapar[i]
        # allocate portion of GPP to leaf
        # NB NPP is in kg C m-2 per time step now
        #PlusDLcarbon = np.max([0,self.Pi[i] * dt * self.leafNPPProportion])
        #PlusDLcarbon = self.Pi[i] * dt * self.leafNPPProportion
        PlusDLcarbon = self.Pi[i] * dt * (1. - self.fapar[i])
        # if NPP is negative, we assume (for now) that this comes from other pools
        # but we dont in any case, increment the leaf pool
        # now we decay that over the required time period
        n = len(self.leafLoss[i+ddelay:])
        if True or PlusDLcarbon > 0:
            self.leafGain[i+1] = PlusDLcarbon
            self.leafLoss[i+ddelay:] += decay[:n] * PlusDLcarbon 
        self.LAI[i+1] = self.LAI[i] + ( self.leafGain[i+1] - self.leafLoss[i])/self.sigmal[i]
        self.Lcarbon[i+1] = self.LAI[i] * self.sigmal[i]

    self.fapar = 1 - np.exp(-self.kbar * self.LAI)
    self.Rpm = self.Rpm_ * self.fapar
    self.PiG = self.PiG_ * self.fapar
    self.Rpg = self.Rpg_ * self.fapar
    self.Rp = self.Rp_ * self.fapar

def fixTemperature(temp,temp2,julian,ndvi,mu):
    ndviFull = np.zeros_like(temp2)
    temp3 = temp2*0.
    # scale the temperatures to the observed
    for i in np.arange(len(temp)):
        try:
            w = np.where((julian>=i) * (julian<(i+1)))
            ndviFull[w] = ndvi[i]
            if temp[i] > 0:
                integral = (temp2[w] * mu[w]).sum()/mu[w].sum()
                temp3[w] = temp[i]*temp2[w]/integral
            else:
                temp3[w] = temp[i]
        except:
            temp3[w] = temp[i]
    return temp3,ndviFull
#omega = None
#[ipar,temp,mu,julian,dt]  = drivers(ndays=365*3)
#leaf = leafScale(ipar,temp,omega=omega)
#canopyScale(leaf,1.,mu,julian,dt=dt,leafLoss=1.)

