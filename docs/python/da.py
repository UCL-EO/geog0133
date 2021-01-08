
import numpy as np

sd_0 = 0.3
sd_1 = 0.2
rho = -0.5
# Form B
B = np.matrix([[sd_0**2,rho*sd_0*sd_1],[rho*sd_0*sd_1,sd_1**2]])
# inverse
BI = B.I
# check:
print ('B x B-1 = I')
print (B,'x')
print (BI,'=')
print (BI * B)


import numpy as np

mean_0 = 0.2
mean_1 = 0.5
sd_0 = 0.3
sd_1 = 0.2
# case 1: with correlation
rho = -0.5

test = [0.,0.]
dx0 = test[0] - mean_0
dx1 = test[1] - mean_1
B00 = sd_0**2
B11 = sd_1**2
B01 = sd_0 * sd_1 * rho
Z2 = (dx0*B00+dx1*B01)*dx0 + (dx0*B01+dx1*B11)*dx1
detB = B00*B11 - B01**2
scale = (2.*np.pi) * np.sqrt(detB)
p0 = (1./scale) * np.exp(-0.5 * Z2)
print ('p0: rho = -0.5: p(0,0) =',p0)

# case 1: without correlation
rho = -0.0

test = [0.,0.]
dx0 = test[0] - mean_0
dx1 = test[1] - mean_1
B00 = sd_0**2
B11 = sd_1**2
B01 = sd_0 * sd_1 * rho
Z2 = (dx0*B00+dx1*B01)*dx0 + (dx0*B01+dx1*B11)*dx1
detB = B00*B11 - B01**2
scale = (2.*np.pi) * np.sqrt(detB)
p1 = (1./scale) * np.exp(-0.5 * Z2)
print ('p1: rho =  0.0: p(0,0) =',p1)
print ('p1/p0 =',p1/p0)



import numpy as np
import scipy.optimize

# prior 
xb = np.array([0.1,0.5])
B  = np.matrix([[0.2**2,0.5*0.2*0.3],[0.5*0.2*0.3,0.3**2]])

# a direct observation: sd = 0.1
xr = np.array([0.15,0.4])
R  = np.matrix([[0.1**2,0.0],[0.0,0.1**2]])

BI = B.I
RI = R.I

# starting guess
x = np.array([0.,0.])

def cost(x,xb,BI,xr,RI):
    '''
    Return J and J' at x
    '''
    Jb = np.dot(np.array(0.5*(xb-x) * BI),(xb-x))[0]
    Jr = np.dot(np.array(0.5*(xr-x) * RI),(xr-x))[0]
    JbPrime = -(xb-x)*BI 
    JrPrime = -(xr-x)*RI
    return Jr+Jb,np.array(JrPrime+JbPrime)[0]

def uncertainty(x,xb,BI,xr,RI):
    # inverse of Hessian
    return (BI + RI).I

retval = scipy.optimize.fmin_l_bfgs_b(cost,x,args=(xb,BI,xr,RI))

# x new
x = retval[0]
# uncertainty
Cpost = uncertainty(x,xb,BI,xr,RI)

# print prior
psigma0 = np.sqrt(B[0,0])
psigma1 = np.sqrt(B[1,1])
prho12  = B[0,1]/(psigma0*psigma1)
print ('prior:     x0,x1      :',xb[0],xb[1])
print ('prior:     sd0,sd1,rho:',psigma0,psigma1,prho12)

# print observation
rsigma0 = np.sqrt(R[0,0])
rsigma1 = np.sqrt(R[1,1])
rrho12  = R[0,1]/(rsigma0*rsigma1)
print ('observation: x0,x1      :',xr[0],xr[1])
print ('observation: sd0,sd1,rho:',rsigma0,rsigma1,rrho12)

sigma0 = np.sqrt(Cpost[0,0])
sigma1 = np.sqrt(Cpost[1,1])
rho12  = Cpost[0,1]/(sigma0*sigma1)
print ('posterior: x0,x1      :',x[0],x[1])
print ('posterior: sd0,sd1,rho:',sigma0,sigma1,rho12)



from plotGauss import *
plotGauss(xb[0],xb[1],psigma0,psigma1,prho12,\
          title='prior',file='figures/Tprior.png')


plotGauss(xr[0],xr[1],rsigma0,rsigma1,rrho12,\
          title='observation',file='figures/Tobs.png')


plotGauss(x[0],x[1],sigma0,sigma1,rho12,\
          title='posterior',file='figures/Tpost.png')


import os
files = 'figures/Tprior.png figures/Tobs.png figures/Tpost.png'
os.system('convert -delay 50 -loop 0 %s figures/Tanim.gif'%files)


# just remind ourselves of the values above
Cprior = np.matrix(B)
Cpost = np.matrix(Cpost)
xpre = xb
xpost = x

D = 0.5*(np.log(np.linalg.det(Cprior)/np.linalg.det(Cpost)) + \
                            (Cpost * Cprior.I).trace()[0,0] - Cpost.shape[0])
print ('Dispersion =',D)

S = 0.5*np.dot((xpost-xpre).T * Cprior.I,xpost-xpre)[0,0]
print ('Signal =',S)

print ('relative entropy =',(D+S)/np.log(2.), 'bits')
