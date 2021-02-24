import numpy as np
import matplotlib.pyplot as plt
from geog0133.photJules import photosynthesis

def plotme(x,photo,plotter):
    '''
    plotter utility
    x     :  array to be used for x-axis 
    photo :  photosynthesis data
           
    plotter = {
        n_subplots : 1,       # number of sub-plots
        subplot    : 0,       # index of this sub-plot
        title      : 'title', # subplot title
        name       : 'name',  # plot file name 
        xlabel     : 'x label'# x label             
        log        : False   # use log y scale?
        ymax       : None    # max value for y
    }
    '''
    
    if not plotter:
        return plotter   
    # defaults
    if 'n_subplots' not in plotter:
        plotter['n_subplots'] = 1
    if 'subplot' not in plotter:
        plotter['subplot'] = 0
    if 'ymax' not in plotter:
        plotter['ymax'] = None
    if 'title' not in plotter:
        plotter['title'] = None
    if 'xlabel' not in plotter:
        plotter['xlabel'] = None
    if 'name' not in plotter:
        plotter['name'] = None
    if 'log' not in plotter:
        plotter['log'] = False
    
    if (plotter['subplot'] == 0) \
        or ('fig' not in plotter) \
        or ('axs' not in plotter):
            fig,axs = plt.subplots(plotter['n_subplots'],1,\
                                   figsize=(10,5*plotter['n_subplots']))
            if plotter['n_subplots'] == 1:
                axs = [axs]
            else:
                axs = axs.flatten()
    else:
        axs = plotter['axs']
        fig = plotter['fig']
              
    i = plotter['subplot']
    
    if plotter['log']:
      axs[i].set_yscale('log')

    if plotter['ymax']:
      axs[i].set_ylim(None,plotter['ymax'])
    axs[i].plot( x, photo.Wc * 1e6,label='Wc')
    axs[i].plot( x, photo.Ws * 1e6,label='Ws')
    axs[i].plot( x, photo.We * 1e6,label='We')
    axs[i].plot( x, photo.W * 1e6,label='W')
    axs[i].plot( x, photo.Al* 1e6,label='Al')
    axs[i].plot( x, photo.Rd* 1e6,label='Rd')

    axs[i].set_ylabel('Assimilation rate $(\mu mol\, CO_2 m^{-2} s^{-1})$', fontsize=10)
    if plotter['xlabel'] is None:
        axs[i].set_xlabel('Temperature (C)', fontsize=10)
    else:
        axs[i].set_xlabel(xlabel, fontsize=10)
    if plotter['title']:
        axs[i].set_title(title, fontsize=10)
    else:
        axs[i].set_title(photo.pft[0], fontsize=10)
    axs[i].legend(loc='best', fontsize=10)
    
    # save to file
    if i == plotter['n_subplots'] - 1:
        plotter['filename'] = f"photter_{plotter['name']}.png"
        fig.savefig(plotter['filename'])
        print(f">>> Saved result in {plotter['filename']}")
    else:
        plotter['filename'] = None
        
    plotter['axs'] = axs
    plotter['fig'] = fig
    plotter['subplot'] += 1
    return plotter

def day_plot(params,info='',title=None):
    '''
    Plot assimilation over the day

    Inputs:
    params : a list of (jd,ipar,Tc,p,doy) with
    
    jd:   day of year (including fraction of day)
    ipar: incident PAR (u mol(photons) / (m^2 s))
    Tc:   surface Temperature
    p:     photosynthesis object
    doy:   integer doy

    Keywords:
    title: plot super title
    '''
    n = len(params)
    fig,axs = plt.subplots( 1+n, 2, figsize=(11,2.5*(1+n)))
    fig.suptitle(title)
    colours = ['r','g','b','c','m','y','k']
    
    # ipar
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        axs[0,1].plot(jd,ipar, f'{colours[i]}-',label=str(doy))
    axs[0,1].set_ylabel('iPAR $\mu mol\, photons/ (m^2 s))$')
    axs[0,1].set_xlim(jd[0],jd[-1])
    axs[0,1].legend(loc='best')

    # TC
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        axs[0,0].plot(jd, Tc, f'{colours[i]}-',label=str(doy))

    axs[0,0].set_ylabel("$T_c$ (C)")
    axs[0,0].set_xlim(jd[0],jd[-1])
    axs[0,0].legend(loc='best')
    
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        # now plot Al  over the day
        axs[i+1,0].plot(jd,(p.W)*1.e6, '-',label=f"W {doy}")
        axs[i+1,0].plot(jd,(p.Al)*1.e6, '-',label=f"Al {doy}")
        axs[i+1,0].plot(jd,(p.Rd)*1.e6, '-',label=f"Rd {doy}")
        axs[i+1,0].set_xlim(jd[0],jd[-1])
        
        if i == n-2:
            axs[i+1,0].set_ylabel('Assim/Respiration rate $[\mu mol\, m^{-2} s^{-1}]$')
        if i == n-1:
            axs[i+1,0].set_xlabel("Fraction of day")
        
        axs[i+1,0].legend(loc='upper right')
        
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        # now plot W terms over the day
        axs[i+1,1].plot( jd, p.Wc * 1e6,label=f'Wc {info}')
        axs[i+1,1].plot( jd, p.Ws * 1e6,label=f'Ws {info}')
        axs[i+1,1].plot( jd, p.We * 1e6,label=f'We {info}')
        axs[i+1,1].plot( jd, p.W * 1e6,label=f'W {info}')
        axs[i+1,1].plot( jd, p.Al* 1e6,label=f'Al {info}')
        axs[i+1,1].plot( jd, p.Rd* 1e6,label=f'Rd {info}')
        if i == n-2:
            axs[i+1,1].set_ylabel('Assim/Respiration rate $[\mu mol\, m^{-2} s^{-1}]$')
        if i == n-1:
            axs[i+1,1].set_xlabel("Fraction of day")
        axs[i+1,1].set_xlim(jd[0],jd[-1])
        axs[i+1,1].legend(loc='upper right')
    return 




def day_plot2(jd,ipar,Tc,p,info='',title=None,fig=None,axs=None,final=False):
    '''
    Plot assimilation over the day
    
    Inputs:
    jd:   day of year (including fraction of day)
    ipar: incident PAR (u mol(photons) / (m^2 s))
    Tc:   surface Temperature
    p:     photosynthesis object
    
    Keywords:
    title: plot super title
    fig : fig from matplotlib (or None)
    axs : array of plt from matplotlib subplots (or None)
    info : info string to add to legends
    final : True if final plot
    '''
    if (fig is None):
      fig,axs = plt.subplots( 2, 2, figsize=(12,10))
      fig.suptitle(title)
 
    axs[0,1].plot(jd,ipar, '-',label=info)
    if final:
      axs[0,1].set_ylabel('$PAR_{inc}\,\sim$ $\mu mol\, photons/ (m^2 s))$')
      axs[0,1].set_xlabel("Fraction of day")
      axs[0,1].set_xlim(jd[0],jd[-1])
    
    axs[0,0].plot(jd, Tc, '-',label=info)
    if final:
      axs[0,0].set_ylabel("$T_c$ (C)")
      axs[0,0].set_xlabel("Fraction of day")
      axs[0,0].set_xlim(jd[0],jd[-1])
    
    # now plot Al  over the day
    axs[1,0].plot(jd,(p.W)*1.e6, '-',label=f"W {info}")
    axs[1,0].plot(jd,(p.Al)*1.e6, '-',label=f"Al {info}")
    axs[1,0].plot(jd,(p.Rd)*1.e6, '-',label=f"Rd {info}")
    if final:
      axs[1,0].set_ylabel('Assim/Respiration rate $[\mu mol\, m^{-2} s^{-1}]$')
      axs[1,0].set_xlabel("Fraction of day")
      axs[1,0].set_xlim(jd[0],jd[-1])
      axs[1,0].legend(loc='upper right')

    # now plot W terms over the day
    axs[1,1].plot( jd, p.Wc * 1e6,label=f'Wc {info}')
    axs[1,1].plot( jd, p.Ws * 1e6,label=f'Ws {info}')
    axs[1,1].plot( jd, p.We * 1e6,label=f'We {info}')
    axs[1,1].plot( jd, p.W * 1e6,label=f'W {info}')
    axs[1,1].plot( jd, p.Al* 1e6,label=f'Al {info}')
    axs[1,1].plot( jd, p.Rd* 1e6,label=f'Rd {info}')
    if final:
      axs[1,1].set_ylabel('Assim rate factors $[\mu mol\, m^{-2} s^{-1}]$')
      axs[1,1].set_xlabel("Fraction of day")
      axs[1,1].set_xlim(jd[0],jd[-1])
      axs[1,1].legend(loc='upper right')
    return fig,axs


def gpp_plot(params,info='',title=None):
    '''
    Plot assimilation over the day

    Inputs:
    params : a list of (jd,ipar,Tc,p,doy) with

    jd:   day of year (including fraction of day)
    ipar: incident PAR (u mol(photons) / (m^2 s))
    Tc:   surface Temperature
    p:     photosynthesis object
    doy:   integer doy

    Keywords:
    title: plot super title
    '''
    n = len(params)
    fig,axs = plt.subplots( 1+n, 2, figsize=(11,2.5*(1+n)))
    fig.suptitle(title)
    colours = ['r','g','b','c','m','y','k']

    # ipar
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        axs[0,1].plot(jd,ipar, f'{colours[i]}-',label=str(doy))
    axs[0,1].set_ylabel('iPAR $\mu mol\, photons/ (m^2 s))$')
    axs[0,1].set_xlim(jd[0],jd[-1])
    axs[0,1].legend(loc='best')

    # TC
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        axs[0,0].plot(jd, Tc, f'{colours[i]}-',label=str(doy))

    axs[0,0].set_ylabel("$T_c$ (C)")
    axs[0,0].set_xlim(jd[0],jd[-1])
    axs[0,0].legend(loc='best')

    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        # now plot Al  over the day
        axs[i+1,0].plot(jd,(p.W)*1.e6, '-',label=f"W {doy}")
        axs[i+1,0].plot(jd,(p.Al)*1.e6, '-',label=f"Al {doy}")
        axs[i+1,0].plot(jd,(p.Rd)*1.e6, '-',label=f"Rd {doy}")
        axs[i+1,0].set_xlim(jd[0],jd[-1])

        if i == n-2:
            axs[i+1,0].set_ylabel('Leaf level Assim/Respiration rate $[\mu mol\, m^{-2} s^{-1}]$')
        if i == n-1:
            axs[i+1,0].set_xlabel("Fraction of day")

        axs[i+1,0].legend(loc='upper right')
        
    for i in range(n):
        jd,ipar,Tc,p,doy = params[i]
        # now plot Al  over the day
        axs[i+1,1].plot(jd,(p.PiG)*1.e6, '-',label='GPP')
        axs[i+1,1].set_xlim(jd[0],jd[-1])
        try:
          if p.Pi.sum() > 0:
            axs[i+1,1].plot(jd,(p.Pi)*1.e6, '-',label='NPP')
        except:
          pass

        if i == n-2:
            axs[i+1,1].set_ylabel('NPP/GPP $[mg\,C m^{-2}s^{-1}]$')
        if i == n-1:
            axs[i+1,1].set_xlabel("Fraction of day")

        axs[i+1,1].legend(loc='upper right')

    return

    
