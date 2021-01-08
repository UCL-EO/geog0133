import numpy as np
import pylab as plt


class Kalman():
    def __init__(self,y,x0,C0,R,M,Q,sample_H,sample_doys,\
                                 reverse=False,outlier=None):
        self.R = R
        self.Q = Q
        self.M = np.matrix(M)
        self.outlier = outlier 
        self.reverse = reverse
        self.sample_H = sample_H
        self.sample_doys = sample_doys
        self.bad = np.zeros_like(sample_doys).astype(bool)
        self.y = y

        self.alldoys = np.arange(sample_doys.min(),sample_doys.max()+1)
        self.x = np.zeros([len(self.alldoys),3]) 
        self.residual_sd = np.zeros([len(self.alldoys)])
        self.x[0,:] = x0
        self.C = np.zeros([len(self.alldoys),3,3])
        self.C[0,:,:] = C0
        self.I = np.eye(3)
        self.rk = np.zeros([len(self.alldoys)])    
        self.Kk = np.zeros([len(self.alldoys),3]) 
        self.fwd = np.zeros([len(self.y)])

    def predict_k(self,k,bp=1.0):
        xk = self.x[k,:] * self.M 
        Pk = self.M.T * self.C[k,:,:] * self.M + self.Q * bp
        return xk,Pk

    def update_k(self,k,xk,Pk,sign=1):
        if np.in1d(self.alldoys[k],self.sample_doys)[0]:
            sample = np.where(self.sample_doys == self.alldoys[k])[0]
            H = self.sample_H[:,sample]
            rk = self.y[sample] - xk * H
            Sk = H.T * Pk * H + self.R
            self.residual_sd[k] = np.sqrt((rk.T * Sk.I * rk)/np.sqrt(2*np.pi*Sk))[0,0]
            if self.outlier:
                if  self.residual_sd[k] > self.outlier:
                    self.bad[sample] = True
            if self.bad[sample] == False:
                Kk = Pk * H * Sk.I
                self.x[k+sign,:] = xk + np.array(Kk * rk)[:,0]
                self.x[(self.x < 0)] = 0.
                self.C[k+sign,:,:] = (self.I - Kk* H.T)*Pk
                self.Kk[k,:] = np.array(Kk).flatten()
            else:
                self.x[k+sign,:] = xk
                self.C[k+sign,:,:] = Pk
            self.fwd[sample] = (np.array(self.x[k+sign,:] * H).flatten())[0]
            self.rk[k] = rk
        else:
            self.x[k+sign,:] = xk 
            self.C[k+sign,:,:] = Pk

    def run(self,bp=None):
        #import pdb
        #pdb.set_trace()
        if self.reverse:
            self.x[-1,:] = self.x[0,:]
            self.C[-1,:,:] = self.C[0,:,:]
            for i in np.arange(len(self.alldoys)-1,0,-1):
                bpscale = 1.0
                if bp:
                    if np.abs(self.alldoys[i] - bp) <= 5.0:
                        bpscale = 10000
                xk,Pk = self.predict_k(i,bp=bpscale)
                self.update_k(i,xk,Pk,sign=-1)
        else:
            for i in range(len(self.alldoys)-1):
                bpscale = 1.0
                if bp:
                    if np.abs(self.alldoys[i] - bp) <= 5.0:
                        bpscale = 10000
                xk,Pk = self.predict_k(i,bp=bpscale)
                self.update_k(i,xk,Pk)


