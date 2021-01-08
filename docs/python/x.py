from kernels import *
import numpy as np
import pylab as plt
from scipy.optimize import fmin_l_bfgs_b

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

# calculate the kernels
k = Kernels(vza[mask],sza[mask],raa[mask],doIntegrals=False)

# data
red = r[:,0,:,:][mask]
nir = r[:,1,:,:][mask]
doys = doy[mask[:,0,0]]

# select some days before the fire
w = np.where((doys >= 120) * (doys <150))

H = np.matrix([k.Isotropic[w],k.Ross[w],k.Li[w]])
X = np.zeros(3)
Y = red[w]
R = np.eye(len(Y))
R1 = np.matrix(R*R.T).I

def J_obs(X,H,Y,R1):
    '''
    Cost function
    '''
    Y_hat = np.array((X * np.matrix(H)).T).flatten()
    d = np.matrix(Y - Y_hat)
    e = 0.5 * (d * R1 * d.T)[0,0]
    e_prime = -np.matrix(H) * R1 * d.T
    return e,np.array(e_prime)[:,0]


bounds = [(0,1),(0,1),(0,1)]
# solve the minimisation problem
solve = fmin_l_bfgs_b(J_obs,X,args=(H,Y,R1),bounds=bounds)
X_new = solve[0]
RMSE = np.sqrt(solve[1])

print ("red",X_new,'sd',RMSE)

Y_hat = np.array((X_new * np.matrix(H)).T).flatten()
plt.clf()
plt.plot(doys[w],Y,'o',label='obs')
plt.plot(doys[w],Y_hat,'+',label='model')
plt.legend(loc='best')
plt.xlabel('doy')
plt.ylabel('reflectance')
plt.title('red')
plt.savefig('figures/kernel1red.png')

plt.clf()
Y = nir[w]
solve = fmin_l_bfgs_b(J_obs,X,args=(H,Y,R1),bounds=bounds)
X_new = solve[0]
RMSE = np.sqrt(solve[1])

print ("nir",X_new,'sd',RMSE)

Y_hat = np.array((X_new * np.matrix(H)).T).flatten()
plt.plot(doys[w],Y,'o',label='obs')
plt.plot(doys[w],Y_hat,'+',label='model')
plt.legend(loc='best')
plt.xlabel('doy')
plt.ylabel('reflectance')
plt.title('NIR')
plt.savefig('figures/kernel1nir.png')
