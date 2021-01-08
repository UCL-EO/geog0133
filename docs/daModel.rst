A model and initial comparison with measurements
=================================================

We first recall the canopy model that we developed in a previous exercise, based around the photosynthesis in Jules. This is available via the files: `canopyModel.py <https://raw.githubusercontent.com/UCL-EO/geog0133/main/docs/python/daHard.py>`_, `modellingPractical.py <https://raw.githubusercontent.com/UCL-EO/geog0133/main/docs/python/modellingPractical>`_, and `photJules.py <https://raw.githubusercontent.com/UCL-EO/geog0133/main/docs/python/photJules.py>`_.

One modification here has been to make the proprtion of NPP allocated to leaf C to be equivalent to one minus the fAPAR, but of course other mechanisms could be used.

Drivers and observations
~~~~~~~~~~~~~~~~~~~~~~~~~

It is a good idea to first examine the drivers and observational data to understand a little more about how we expect the model to operate.

.. plot::
    :include-source:

    from phenology import *
    from canopyModel import *

    lat = 57
    lon = 86

    temp= get_temperature ( latitude=lat, longitude=lon )
    [ipar,temp2,mu,julian,dt]  = drivers(ndays=365*11+2,lat=lat,lon=lon)

    retval = fit_phenology_model( lon, lat, [2001],\
                 temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    ndvi = retval[1]

    temp2,ndviFull = fixTemperature(temp,temp2,julian,ndvi,mu)

    plt.clf()
    omega=None
    leaf = leafScale(ipar,temp2,omega=omega,type='Broadleaf tree')
    plt.subplot(3,1,1)
    plt.rcParams['legend.fontsize'] = 9
    plt.legend(loc='best', numpoints=5,fancybox=True, shadow=True )
    plt.grid(True)
    plt.plot(julian,leaf.Al*1e6,label='Al')
    plt.plot(julian,leaf.Al.cumsum()*1000,label='Al cum/1000.')
    plt.plot(julian,ndviFull*20,label='NDVI x 20')
    plt.plot(julian[::12],temp/2,label='T/2')
    plt.plot(julian[::12],ipar[::12]/50,label='ipar / 50')
    plt.legend(loc='best', numpoints=1,fancybox=True, shadow=True )
    plt.xlim(0,365)
    plt.ylim(-5,25)
    plt.subplot(3,1,2)
    plt.ylim(0,25)
    plt.plot(julian,leaf.Wc*1e6,label='Wc')
    plt.plot(julian,leaf.Wl*1e6,label='Wl')
    plt.plot(julian,leaf.We*1e6,label='We')
    plt.plot(julian,leaf.W*1e6,label='W')
    plt.plot(julian,leaf.Rd*1e6,label='Rd')
    plt.plot(julian,leaf.Al*1e6,label='Al')
    plt.xlim(150,160)
    plt.legend(loc='best', numpoints=1,fancybox=True, shadow=True )
    plt.subplot(3,1,3)
    plt.plot(julian,ipar/50.,label='ipar/50')
    plt.plot(julian,temp2,label='T')
    plt.legend(loc='best', numpoints=2,fancybox=True, shadow=True )
    plt.xlim(150,160)
    plt.ylim(0,50)
    plt.xlabel('day of year')


The controlling factor here seems to be :math:`Wc`, the Rubisco limiting rate, which in turn depends on :math:`V_{cmax}`, which in this model is a function of nitrogen availabilty and temperature.

.. math:: V_{cmax} = \frac{Q_{10}^{(0.1(T-25))} V_{cmax25}}{(1+\exp(0.3(T-T_{upp})))(1+\exp(0.3(T_{low}-T)))}

Clearly, the temperature function is what is controlling :math:`V_{cmax}` here, so this is dependent on the upper and lower ranges for temperature for the PFT.

.. plot::
    :include-source:

    from phenology import *
    from canopyModel import *

    lat = 57
    lon = 86

    temp= get_temperature ( latitude=lat, longitude=lon )
    [ipar,temp2,mu,julian,dt]  = drivers(ndays=365*11+2,lat=lat,lon=lon)

    retval = fit_phenology_model( lon, lat, [2001],\
                 temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    ndvi = retval[1]

    temp2,ndviFull = fixTemperature(temp,temp2,julian,ndvi,mu)

    plt.clf()
    omega=None

    plt.rcParams['legend.fontsize'] = 9
    plt.subplot(4,1,1)
    plt.grid(True)
    leaf = leafScale(ipar,temp2,omega=omega,type='C3 grass')
    plt.plot(julian,leaf.Al*1e6,label='Al grass')
    plt.plot(julian,leaf.Vcmax*1e6/2,label='Vcmax grass/2')
    plt.plot(julian,ndviFull*20,label='NDVI x 20')
    plt.plot(julian[::12],temp/2,label='T/2')
    plt.plot(julian[::12],ipar[::12]/50,label='ipar / 50')
    plt.xlim(0,365)
    plt.ylim(-5,25)
    plt.legend(loc='best', fancybox=True, shadow=True )
    plt.subplot(4,1,2)
    plt.grid(True)
    leaf = leafScale(ipar,temp2,omega=omega,type='Broadleaf tree')
    plt.plot(julian,leaf.Al*1e6,label='Al BL tree')
    plt.plot(julian,leaf.Vcmax*1e6/2,label='Vcmax BL tree/2')
    plt.plot(julian,ndviFull*20,label='NDVI x 20')
    plt.plot(julian[::12],temp/2,label='T/2')
    plt.plot(julian[::12],ipar[::12]/50,label='ipar / 50')
    plt.xlim(0,365)
    plt.ylim(-5,25)
    plt.legend(loc='best', fancybox=True, shadow=True )
    plt.subplot(4,1,3)
    plt.grid(True) 
    leaf = leafScale(ipar,temp2,omega=omega,type='Needleleaf tree')
    plt.plot(julian,leaf.Al*1e6,label='Al NL tree')
    plt.plot(julian,leaf.Vcmax*1e6/2,label='Vcmax NL tree/2')
    plt.plot(julian,ndviFull*20,label='NDVI x 20')
    plt.plot(julian[::12],temp/2,label='T/2')
    plt.plot(julian[::12],ipar[::12]/50,label='ipar / 50')
    plt.xlim(0,365)
    plt.ylim(-5,25)
    plt.legend(loc='best', fancybox=True, shadow=True )
    plt.subplot(4,1,4)
    plt.grid(True)
    leaf = leafScale(ipar,temp2,omega=omega,type='Shrub')
    plt.plot(julian,leaf.Al*1e6,label='Al shrub')
    plt.plot(julian,leaf.Vcmax*1e6/2,label='Vcmax shrub/2')
    plt.plot(julian,ndviFull*20,label='NDVI x 20')
    plt.plot(julian[::12],temp/2,label='T/2')
    plt.plot(julian[::12],ipar[::12]/50,label='ipar / 50')
    plt.xlim(0,365)
    plt.ylim(-5,25)
    plt.legend(loc='best', fancybox=True, shadow=True )

For all PFTs then, :math:`V_{cmax}` is controlling leaf assimilation and this directly mimics temperature, with (effectively) different scalings depending on the temperature ranges for each PFT.

The plots of leaf-level assimilation and NDVI are instructive for understanding how people try to use EO data. It is clearly tempting to consider that the signal mapped by NDVI mimics the pattern of leaf-level assimilation. It also however mimics the temperature and IPAR patterns, which of course are the drivers for leaf assimilation here. 

This sort of observation is part of the reason why NDVI has been so widely used in remote sensing, and why it has been used to correlate with so many variables. 

In comparing models with observations however, we should look for physical mechanisms that link the model diagnostics with the observation. This is clearly not straightforward in the case of a vegetation index, but it is probably most reasonable to interpret the NDVI signal as being related to the amount of (green) leaf material in the canopy and probably safest to assume that the NDVI is a surrogate for some linear transformation of fAPAR (assuming other conditions, such as leaf scattering, soil brightness and canopy structural distribution remain constant). There is no direct mechanism by which we could interpret the signal as a *rate* of photosynthesis, but since this has the same broad underlying pattern as NDVI.

According to the Sellers model, and as one of the models in Jules, the scaling between leaf level assimilation and that at the canopy scale is fAPAR times a scaling factor. Whilst this may not be strictly true, it is a useful way of considering the canopy-level photosynthesis, since if fAPAR is proportional to NDVI, and, arguing that :math:`A_l` is broadly proportional to temperature, we would expect the increment in leaf carbon to be proportional to product of NDVI and T (assuming a constant allocation of the proportion of NPP), so the increment in LAI should be proportionate to that too, minus some loss term.

Losses from the leaf pool in these models are generally dealt with in quite a simplistic manner, e.g. by a maximum leaf age mechanism.

.. plot::
    :include-source:

    from canopyModel import *
    plt.clf()
    [ipar,temp,mu,julian,dt]  = drivers(ndays=365*3)
    leaf = leafScale(ipar,temp,omega=None)
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    for leafLoss in [0.25,0.50,0.75,1.00,1.50,2.00]:
        canopyScale(leaf,1.,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='leafLoss=%.2f'%leafLoss)
    plt.legend(loc=4)
    plt.show()
    
The plot above shows modelled fAPAR for a C3 grass at :math:`50^o N` over 3 years. In this plot, we are varying the `leafLoss` parameter, which defines the rate of loss of leaf carbon (when leaf C is added to the pool, its presence in that pool is essentially an exponential function of time, depending on this parameter). This decay also applies to the initial C pool, so we see a transient reponse as the fAPAR settles into a steady state (essentially within 1 year). We notice that there are unstable values of this parameter (e.g. 0.25) which settle to fAPAR=0.

The fAPAR has no dependence on the initial LAI after the transients have decayed.

.. plot::
    :include-source:

    from canopyModel import *
    plt.clf()
    [ipar,temp,mu,julian,dt]  = drivers(ndays=365*3)
    leaf = leafScale(ipar,temp,omega=None)
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    leafLoss = 0.5
    for initialLAI in [0.10,0.50,1.00,2.00,4.00]:
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='iLAI=%.2f'%initialLAI)
    plt.legend(loc=4)
    plt.show()

Neither does it depend strongly on the leaf single scattering albedo, except for extreme values:

.. plot::
    :include-source:

    from canopyModel import *
    plt.clf()
    [ipar,temp,mu,julian,dt]  = drivers(ndays=365*3)
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    leafLoss = 0.5
    initialLAI = 1.00
    for omega in [0.00,0.10,0.50,0.75,0.85,0.99]:
        leaf = leafScale(ipar,temp,omega=omega)
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='omega=%.2f'%omega)
    plt.legend(loc=4)
    plt.show()


The sensitivity to PAR scaling is low:

.. plot::
    :include-source:

    from canopyModel import *
    plt.clf()
    [ipar,temp,mu,julian,dt]  = drivers(ndays=365*3)
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    leafLoss = 0.5    
    initialLAI = 1.00    
    omega = 0.2
    for dScale in [0.50,1.00,2.00,4.00]:
        leaf = leafScale(ipar*dScale,temp,omega=omega)
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='par scale=%.2f'%dScale)
    plt.legend(loc=4)
    plt.show()

But there is quite a strong sensitivity to the scaling of temperature, and we can quite easily move outside of the stable range for this vegetation type:

.. plot::
    :include-source:

    from canopyModel import *
    plt.clf()
    [ipar,temp,mu,julian,dt]  = drivers(ndays=365*3)
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    leafLoss = 0.5
    initialLAI = 1.00
    omega = 0.2
    for dScale in [0.50,0.75,1.00,1.25,1.50]:
        leaf = leafScale(ipar,temp*dScale,omega=omega)
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='T scale=%.2f'%dScale)
    plt.legend(loc=4)
    plt.show()

We can now look at some NDVI data (following a previous practical) (files `phenology.py <python/phenology.py>`_ and `pheno_utils.py <pheno_utils.py>`_):

.. plot::
    :include-source:

    from phenology import *
   
    lat = 57
    lon = 86
    temp= get_temperature ( latitude=lat, longitude=lon )
    retval = fit_phenology_model( lon, lat, [2001,2002,2003,2004],\
                                 temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    agdd = np.array([retval[0]*retval[0],retval[0],retval[0]*0.+1])
    params = retval[-3]
    # fwd model
    fwd = np.dot(agdd.T,params)
    plt.subplot ( 2, 1, 1 )
    plt.plot ( retval[1], '-r', label="MODIS NDVI" )
    plt.plot ( fwd, '-g', label="Predicted" )
    plt.axvline ( 365*4, ymin=-0.1, ymax=1.01, lw=1.5)
    plt.rcParams['legend.fontsize'] = 9 # Otherwise too big
    plt.legend(loc='best', numpoints=1,fancybox=True, shadow=True ) # Legend
    plt.grid ( True )
    plt.ylabel("NDVI")
    plt.subplot ( 2, 1, 2 )
    plt.plot ( retval[0], '-r' )
    plt.axvline ( 365*4, ymin=-0.1, ymax=1.01, lw=1.5)
    plt.xlabel ("Time [DoY since 1/1/2001]")
    plt.ylabel ('AGDD C]')
    print retval[-3] # Print out the fit parameters
    plt.show()

To demonstrate a DA exercise then, we can attempt to run the model:

.. plot::
    :include-source:

    from phenology import *
    from canopyModel import *

    lat = 51
    lon = 10

    temp= get_temperature ( latitude=lat, longitude=lon )
    retval = fit_phenology_model( lon, lat, [2001],\
                   temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    ndvi = retval[1]

    [ipar,temp2,mu,julian,dt]  = drivers(ndays=365*11+2,lat=lat,lon=lon)
    temp2,ndviFull = fixTemperature(temp,temp2,julian,ndvi,mu)

    plt.clf()
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    initialLAI = 2.0
    omega=None
    leaf = leafScale(ipar,temp2,omega=omega,type='Broadleaf tree')
    for leafLoss in [1.00,1.50,2.00,2.50,3.00]:
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='leaf loss=%.2f'%(leafLoss))
    plt.plot(julian,ndviFull,'k',label='NDVI')
    plt.legend(loc=4)
    plt.title('lon %.2f lat %.2f'%(lon,lat))
    plt.show()

.. plot::
    :include-source:

    from phenology import *
    from canopyModel import *

    lat = 57
    lon = 86

    temp= get_temperature ( latitude=lat, longitude=lon )
    retval = fit_phenology_model( lon, lat, [2001],\
                   temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    ndvi = retval[1]

    [ipar,temp2,mu,julian,dt]  = drivers(ndays=365*11+2,lat=lat,lon=lon)
    temp2,ndviFull = fixTemperature(temp,temp2,julian,ndvi,mu)

    plt.clf()
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    initialLAI = 2.0
    omega=None
    leaf = leafScale(ipar,temp2,omega=omega,type='Broadleaf tree')
    for leafLoss in [1.00,1.50,2.00,2.50,3.00]:
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='leaf loss=%.2f'%(leafLoss))
    plt.plot(julian,ndviFull,'k',label='NDVI')
    plt.legend(loc=4)
    plt.title('lon %.2f lat %.2f'%(lon,lat))
    plt.show()

So, there seems to be a slight phase shift between what the model is capable of producing and the NDVI data, and it is not certain that the magnitudes will line up for any value of `leafLoss`, but we can see that we can at least use this model to produce something in the bal;l park of the observations.

.. plot::
    :include-source:

    from phenology import *
    from canopyModel import *

    lat = 57
    lon = 86

    temp= get_temperature ( latitude=lat, longitude=lon )
    retval = fit_phenology_model( lon, lat, [2001],\
                 temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    ndvi = retval[1]

    [ipar,temp2,mu,julian,dt]  = drivers(ndays=365*11+2,lat=lat,lon=lon)
    temp2,ndviFull = fixTemperature(temp,temp2,julian,ndvi,mu)

    plt.clf()
    plt.xlabel('day of year')
    plt.ylabel('fAPAR')
    initialLAI = 2.0
    omega=None
    leaf = leafScale(ipar,temp2,omega=omega,type='C3 grass')
    for leafLoss in [0.80, 1.00,1.50,2.00,2.50,3.00]:
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(julian,leaf.fapar,label='leaf loss=%.2f'%(leafLoss))
    plt.plot(julian,ndviFull,'k',label='NDVI')
    plt.legend(loc=4)
    plt.title('lon %.2f lat %.2f'%(lon,lat))
    plt.show()

In this case, the modelled fapar seems to match the observed NDVI data much better than assuming that the land surface is a broadleaf forest, so apparent error in the PFT selection is something we must pay attention to.


.. plot::
    :include-source:

    from phenology import *
    from canopyModel import *

    lat = 57
    lon = 86

    temp= get_temperature ( latitude=lat, longitude=lon )
    retval = fit_phenology_model( lon, lat, [2001],\
                 temp,tbase=-10.,do_agdd=True, pheno_model="quadratic")
    ndvi = retval[1]

    [ipar,temp2,mu,julian,dt]  = drivers(ndays=365*11+2,lat=lat,lon=lon)
    temp2,ndviFull = fixTemperature(temp,temp2,julian,ndvi,mu)

    plt.clf()
    plt.xlabel('NDVI')
    plt.ylabel('modelled fapar')
    initialLAI = 2.0
    omega=None
    leaf = leafScale(ipar,temp2,omega=omega,type='C3 grass')
    plt.plot(np.array([0.,0.]),np.array([1.,1.]),'k',label='1:1 line')
    for leafLoss in [0.8,0.9,1.0]:
        canopyScale(leaf,initialLAI,mu,julian,dt=dt,leafLoss=leafLoss)
        plt.plot(ndviFull[365*2:],leaf.fapar[365*2:],'.',label='leaf loss=%.2f'%(leafLoss))
    plt.legend(loc=4)
    plt.title('lon %.2f lat %.2f'%(lon,lat))
    plt.show()


The 'circular' or 'hysteresis' pattern we observe on this scatterplot suggests a phase shift between the measured and modelled data that is only slightly altered by changing the leaf loss rate. 

Still, we might suppose :math:`leafLoss = 1.0` to be a reasonable representation of the observations (at least as long as we are willing to bve \lieve an equivalence between NDVI and fAPAR), and this is probably as far as we can get with this model with no explicit phenology model (other than making the leaf partitioning dependent on :math:`1 - fAPAR`).
