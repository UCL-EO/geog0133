#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


import json
import numpy as np
import matplotlib.pyplot as plt
from solar import solar_model
import scipy.ndimage.filters
from pathlib import Path
from matplotlib import animation


year=2020
doys = np.arange(1,366)
dts = [datetime(year,1,1) + timedelta(int(doy)-1) for doy in doys]
# solar distance in AU
print()
distance = np.array([solar_model(0.,[0],[12],\
            dt.day,dt.month,dt.year,0,0)[2] for dt in dts]).ravel()
ipar = np.array([solar_model(0.,[0],[12],\
            dt.day,dt.month,dt.year,0,0)[3] for dt in dts]).ravel()

# make into orbit for visualisation
theta = (doys / doys.max()) * 2 * np.pi
# project onto x,y
x,y = distance*np.cos(theta),distance*np.sin(theta)
x0,y0 = np.cos(theta),np.sin(theta)

fig,ax = plt.subplots(1,1,figsize=(5,5))
text = ax.text(0.02, 1.00, '', transform=ax.transAxes)
plt.axis('off')
# plot lines
ax1, = ax.plot(x0,y0,'k--')
ax2, = ax.plot(x,y,'k')
ax3, = ax.plot([0,x[0]],[0,y[0]],'bo--')
ax4, = ax.plot([0],[0],'yo',markersize=0)


def plotfig(i,ax1,ax2,ax3,ax4,text):
    thistext = f' \nIPAR {ipar[i]:4.0f}\nAU {distance[i]:06.4f}\ndoy {doys[i]:03d}'
    ax1.set_data(x0,y0)
    ax2.set_data(x,y)
    ax3.set_data([0,x[i]],[0,y[i]])
    ax4.set_data([0],[0])
    ax4.set_markersize(100 * (ipar[i]/ipar.mean())**4)
    text.set_text(thistext)
    return ax1,ax2,ax3,ax4,text
anim = animation.FuncAnimation(fig, plotfig, len(x), fargs=[ax1,ax2,ax3,ax4,text],
                              interval=25, blit=True)
anim.save('images/earth.gif')
