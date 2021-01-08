from kernels import *
import numpy as np
import pylab as plt

#load the data, as above
infile = 'data.npz'
data = np.load(infile)
r = data['reflectance']
vza = data['vza']
sza = data['sza']
raa = data['raa']
wavebands = data['wavebands']
mask = data['mask']
doy = data['doy']
lclut = data['landCoverLUT']
lc = data['landcover']
fireday = data['activeFire']
#mask[doy < 110,0,0] = False
# calculate the kernels
k = Kernels(vza[mask],sza[mask],raa[mask],LiType='Dense',RossHS=False,doIntegrals=False)

# data
red = r[:,0,:,:][mask]
nir = r[:,1,:,:][mask]
doys = doy[mask[:,0,0]]

H = np.matrix([k.Isotropic,k.Ross,k.Li])
X = np.zeros(3)
Y = red[0]
R_red = np.eye(1) * 0.005**2
R_nir = np.eye(1) * 0.02**2
# observation uncertainty

# model
M = np.eye(3)
# model uncertainty
Q_red =  np.eye(3) * 0.0006**2
Q_red[1,1] = Q_red[2,2] = 0.00006**2

Q_nir = np.eye(3) * 0.006**2
Q_nir[1,1] = Q_nir[2,2] = 0.0006**2

# initial conditions
x0_red = np.array([0.08996554, 0.0083535, 0.04541085])
x0_nir = np.array([0.44320984, 0.3960118, 0. ])
C_red = np.eye(3) * 0.2**2
C_nir = np.eye(3) * 0.5**2

import kalman

# red
kfr = kalman.Kalman(red,x0_red,C_red,R_red,M,Q_red,H,doys,reverse=True)

# do a kernel set for angular normalisation
vzan = np.zeros_like(kfr.alldoys)
szan = vzan + np.mean(vza[mask])
kernelnorm = Kernels(vzan,szan,vzan,LiType='Dense',RossHS=False,doIntegrals=False)

plt.clf()
kfr.run()
plt.ylim(0,0.15)
plt.errorbar(kfr.alldoys,kfr.x[:,0],yerr=np.sqrt(kfr.C[:,0,0]),fmt='ro',label='fiso')
plt.errorbar(kfr.alldoys,kfr.x[:,1],yerr=np.sqrt(kfr.C[:,1,1]),fmt='bo',label='fvol')
plt.errorbar(kfr.alldoys,kfr.x[:,2],yerr=np.sqrt(kfr.C[:,2,2]),fmt='go',label='fgeo')
plt.legend(loc='best')
plt.savefig('figures/kernelsKFred2.png')

plt.clf()
rednorm = kfr.x[:,0]+kfr.x[:,1]*kernelnorm.Ross+kfr.x[:,2]*kernelnorm.Li
plt.plot(kfr.alldoys,rednorm)
plt.savefig('figures/kernelsKFnormred2.png')

plt.clf()
plt.plot(kfr.sample_doys,kfr.y,'o',label='obs')
plt.plot(kfr.sample_doys,kfr.fwd,'+',label='fwd')
plt.legend(loc='best')
plt.savefig('figures/kernelsKFfwdred2.png')

# nir
plt.clf()
kfn = kalman.Kalman(nir,x0_nir,C_nir,R_nir,M,Q_nir,H,doys,reverse=True)
kfn.run()
kfn1 = kalman.Kalman(nir,x0_nir,C_nir,R_nir,M,Q_nir,H,doys,reverse=False)
kfn1.run()
# we can calculate the Z difference between these distributions
# by (x1-x2)^T (C-1_1 + C^-1_2) (x1 - x2)
#
Z = np.array([(np.matrix(kfn.x[i] - kfn1.x[i]) * \
       (np.matrix(kfn.C[i]).I + np.matrix(kfn1.C[i]).I) *\
       np.matrix(kfn.x[i] - kfn1.x[i]).T)[0,0] \
       for i in range(kfn.x.shape[0])])

# plot the Z score
plt.plot(kfn.alldoys,Z)
plt.axvline(fireday,lw=1.5)
plt.ylabel('Z')
plt.xlabel('doy')
plt.savefig('figures/kernelsZ2.png')


plt.clf()
plt.ylim(0,0.7)
plt.errorbar(kfn.alldoys,kfn.x[:,0],yerr=np.sqrt(kfn.C[:,0,0]),fmt='ro',label='fiso')
plt.errorbar(kfn.alldoys,kfn.x[:,1],yerr=np.sqrt(kfn.C[:,1,1]),fmt='bo',label='fvol')
plt.errorbar(kfn.alldoys,kfn.x[:,2],yerr=np.sqrt(kfn.C[:,2,2]),fmt='go',label='fgeo')
plt.legend(loc='best')
plt.savefig('figures/kernelsKFnir2.png')

plt.clf()
plt.ylim(0,0.25)
nirnorm = kfn.x[:,0]+kfn.x[:,1]*kernelnorm.Ross+kfn.x[:,2]*kernelnorm.Li
nirnorm1 = kfn1.x[:,0]+kfn1.x[:,1]*kernelnorm.Ross+kfn1.x[:,2]*kernelnorm.Li

plt.plot(kfn.alldoys,nirnorm,label='reverse')
plt.plot(kfn1.alldoys,nirnorm1,label='forward')
plt.axvline(fireday,lw=1.5)
plt.legend(loc='best')
plt.savefig('figures/kernelsKFnormnir2.png')

plt.clf()
plt.grid()
plt.ylim(-0.2,0.2)
plt.axvline(fireday,lw=1.5)
plt.plot(kfn.alldoys,nirnorm1-nirnorm)
plt.savefig('figures/kernelsKFnormnir3.png')

plt.clf()
plt.plot(kfn.sample_doys,kfn.y,'o',label='obs')
plt.plot(kfn.sample_doys,kfn.fwd,'+',label='fwd')
plt.legend(loc='best')
plt.savefig('figures/kernelsKFfwdnir2.png')

# ndvi
ndvinorm = (nirnorm-rednorm)/(nirnorm+rednorm)
plt.clf()
plt.ylim(0,1)
plt.plot(kfn.alldoys,ndvinorm)
plt.savefig('figures/kernelsKFnormndvi2.png')



