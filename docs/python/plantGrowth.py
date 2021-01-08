import numpy as np
import pylab as plt

def getfiles(files=['usa.dat','prc.dat'],server='cdiac.ornl.gov',dir='pub/trends/emissions'):
    '''
    Retrieve some files (list) from the directory dir on the ftp server
    '''
    from ftplib import FTP

    # get some files from the server
    ftp = FTP(server)
    ftp.login()
    ftp.cwd(dir)

    for file in files:
        ftp.retrbinary('RETR '+file,open(file, 'wb').write)
    ftp.quit()


class leaf():
    '''
    '''
    def  __init__(self):
        '''
        '''
        self.constants()
        self.parameters()


    def state(self):
        # Tstar (K) is the leaf surface temperature
        self.Tstar = 0.
        # leaf surface partial pressure (Pa)
        self.cc =  0.
        # internal CO2 partial pressure (Pa)
        self.ci = 0.
        # net leaf photosynthesis, A (mol CO2 m-2 s-1)
        self.A = 0.
        # stomatal conductance to water vapour, gs (m s-1)
        self.g = 0.

    def parameters(self,pft='broadleaf'):
        '''
        '''
        #critical and wilting soil moisture concentrations
        self.ThetaC = 0.
        self.ThetaW = 0.
        self.setPftDefaultParameters(pft)         

    def pftDefaultParameters(self)
        #  PFT specific parameters
        self.Pawl['broadleaf'] = 0.650
        self.PgammaNu['broadleaf'] = 0.004
        self.PgammaW['broadleaf'] = 0.010
        self.Pgamma0['broadleaf'] = 0.250
        self.PLmax['broadleaf'] = 9.
        self.PLmin['broadleaf'] = 3.
        # top-leaf nitrogen concentration
        self.Pnl0['broadleaf'] = 0.040 # (Kg N) (Kg C)-1
        self.Psigmal['broadleaf'] = 0.0375 # kg C m-2 LAI-1
        self.PF0['broadleaf'] = 0.875
        self.PDc['broadleaf'] = 0.090 # kg (kg)-1
        self.PTlow['broadleaf'] = 0.0 # C
        self.PTlupp['broadleaf'] = 36.0 # C



    def setPftDefaultParameters(self,pft):
        # 
        self.awl = self.Pawl[pft]
        #  large-scale disturbance rate
        self.gammaNu = self.PgammaNu[pft]
        # stemwood turnover rate
        self.gammaW = self.PgammaW[pft]
        # minimum leaf turnover rate
        self.gamma0 = self.Pgamma0[pft]
        self.Lmax = self.PLmax[pft]
        self.Lmin = self.PLmin[pft]
        # 
        # top-leaf nitrogen concentration
        self.nl0 = self.Pnl0[pft]
        self.sigmal = self.Psigmal[pft]
        self.F0 = self.PF0[pft]
        self.Dc = self.PDc[pft]
        self.Tlow = self.PTlow[pft] 
        self.Tlupp = self.PTlupp[pft]

    def constants():
        '''
        '''
        self.R = 8.314462175

    def moistureStressFactor(Theta):
        '''
        '''
        # initialise output to zero
        out = Theta*0.
        # consider the case ThetaC = ThetaW
        # what then? return 0.5
        if self.ThetaC == self.ThetaW:
            self.error = 'self.ThetaC == self.ThetaW'
            return out+0.5
        elif Theta <= self.ThetaW:
            return out
        elif Theta > self.ThetaC:
            return out+1.
        else:
             return (Theta-self.ThetaW)/(self.ThetaC-self.ThetaW)

    def  netLeafPhotosynthesis():
        '''
        '''
        # net leaf photosynthesis, A (mol CO2 m-2 s-1), 
        # and stomatal conductance to water vapour, gs (m s-1), are linked through
        # The factor of 1.6 accounts for the different molecular diffusivities of water and carbon dioxide.
        self.A = self.g * (self.cc - self.ci) / (1.6 * self.R* self.Tstar)

        # direct soil moisture dependence
        A = A * beta


class triffid():
    '''
    '''
    def  __init__():
        '''
        '''
        # R is the perfect gas constant (J / (mol K))
        self.R = 8.314462175
        self.leaf = leafState()
        
    def  netLeafPhotosynthesis():
        '''
        '''
        # net leaf photosynthesis, A (mol CO2 m-2 s-1), 
        # and stomatal conductance to water vapour, gs (m s-1), are linked through
        # The factor of 1.6 accounts for the different molecular diffusivities of water and carbon dioxide.
        self.leaf.A = g * (self.cc - self.ci) / (1.6 * R* self.Tstar)

        # direct soil moisture dependence
        A = A * beta

def cropGrowth()
